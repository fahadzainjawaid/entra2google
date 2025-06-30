import subprocess
from config import config  # Importing the configuration from config.py
import json
import tempfile
import os



print(f"Using config file: {config}")
print(f"Project ID: {config.PROJECT_ID}")
print(f"Service Account Name: {config.SERVICE_ACCOUNT_NAME}")
print(f"Delegated Admin Email: {config.DELEGATED_ADMIN_EMAIL}")
print(f"OAuth Scopes: {config.OAUTH_SCOPES}")
print(f"Initial Password: {config.INITIAL_PASSWORD}")
print(f"Key File Name: {config.KEY_FILE_NAME}")


skipOrgPolicy = True



def run_command(command):
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr.strip()}")
    else:
        print(f"✅ Success: {result.stdout.strip()}")
    return result

# === 1. Backup org policy

if not skipOrgPolicy:
  print("\n🔁 Backing up current org policy...")
  backup_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json").name
  run_command([
      "gcloud", "org-policies", "describe",
      "constraints/iam.disableServiceAccountKeyCreation",
      "--project", config.PROJECT_ID,
      "--format=json"
  ])

  # === 2. Disable org policy
  print("\n🔓 Disabling org policy to allow key creation...")
  run_command([
      "gcloud", "org-policies", "disable-enforce",
      "constraints/iam.disableServiceAccountKeyCreation",
      "--project", config.PROJECT_ID
  ])

# === 3. Create Service Account
print("\n⚙️ Creating service account...")
run_command([
    "gcloud", "iam", "service-accounts", "create", config.SERVICE_ACCOUNT_NAME,
    "--display-name", config.DISPLAY_NAME,
    "--project", config.PROJECT_ID
])

# === 4. Assign IAM roles
print("\n🔐 Assigning IAM roles...")
for role in config.IAM_ROLES:
    run_command([
        "gcloud", "projects", "add-iam-policy-binding", config.PROJECT_ID,
        "--member", f"serviceAccount:{config.SERVICE_ACCOUNT_NAME}@{config.PROJECT_ID}.iam.gserviceaccount.com",
        "--role", role
    ])

# === 5. Create key
print("\n🔑 Creating service account key...")
run_command([
    "gcloud", "iam", "service-accounts", "keys", "create", config.KEY_FILE_NAME,
    "--iam-account", f"{config.SERVICE_ACCOUNT_NAME}@{config.PROJECT_ID}.iam.gserviceaccount.com"
])

# === 6. Restore original policy
if not skipOrgPolicy:
  print("\n🔒 Re-enabling org policy to restore original enforcement...")
  run_command([
    "gcloud", "org-policies", "enable-enforce",
    "constraints/iam.disableServiceAccountKeyCreation",
    "--project", config.PROJECT_ID
  ])

# === 7. Output instructions
print("\n⚠️  Final Step: Set up Domain-Wide Delegation manually:")
print("--------------------------------------------------------")
print("1. Go to: https://admin.google.com/ac/owl/domainwidedelegation")
print("2. Click 'Add New' and enter:")
print(f"   - Client ID: (from {config.KEY_FILE_NAME})")
print(f"   - OAuth Scopes: {config.OAUTH_SCOPES}")
print(f"3. Delegate on behalf of: {config.DELEGATED_ADMIN_EMAIL} (must be a Super Admin)")
print("--------------------------------------------------------")
