import subprocess
import json
import argparse, random
import sys
from sync.utils import generate_random_string  # Importing the utility function to generate random strings

from google.auth import default
from googleapiclient.discovery import build

#define constants
from config import config  # Importing the configuration from config.py

#generate a random password for INITIAL_PASSWORD

config.INITIAL_PASSWORD = generate_random_string() 

print("Using config file: ", config)
print("Project ID: ", config.PROJECT_ID)
print(f"Service Account Name: {config.SERVICE_ACCOUNT_NAME}")
print(f"Delegated Admin Email: {config.DELEGATED_ADMIN_EMAIL}")
print(f"OAuth Scopes: {config.OAUTH_SCOPES}")
print(f"Initial Password: {config.INITIAL_PASSWORD}")



credentials, _ = default(scopes=["https://www.googleapis.com/auth/admin.directory.user"])
admin_service = build('admin', 'directory_v1', credentials=credentials)

from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = config.KEY_FILE_NAME  # Path to your service account key file
SCOPES = ["https://www.googleapis.com/auth/admin.directory.user"]
DELEGATED_ADMIN = config.DELEGATED_ADMIN_EMAIL  # Email of the super admin for delegation
ALLOWABLE_DOMAINS = config.ALLOWABLE_DOMAINS  # List of allowed domains
SKIP_USERS = config.SKIP_USERS  # List of users to skip


ENTRA_USERS = {}
GCP_USERS = {}


credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

delegated_credentials = credentials.with_subject(DELEGATED_ADMIN)

admin_service = build("admin", "directory_v1", credentials=delegated_credentials)


def fetch_azure_users():
    try:
        result = subprocess.run(
            ['az', 'ad', 'user', 'list'],
            capture_output=True, text=True, check=True
        )
        ENTRA_USERS = json.loads(result.stdout)
        return ENTRA_USERS
    except subprocess.CalledProcessError as e:
        print("Failed to fetch Azure users:", e.stderr, file=sys.stderr)
        sys.exit(1)

def fetch_gcloud_users():
    try:
        result = subprocess.run(
            ['python3', '-m' 'sync.export_gcloud_users'],
            capture_output=True, text=True, check=True
        )

        
        try:
            dict = json.loads(result.stdout)
            GCP_USERS = dict
            #print (dict)
        except json.JSONDecodeError:
            print("Error decoding JSON from export_gcloud_users.py output.")
            sys.exit(1)


        if not result.stdout.strip():
            print("No users found in Google Cloud Identity.")
            return []
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Failed to fetch Google users:", e.stderr, file=sys.stderr)
        sys.exit(1)
def fetch_blocked_users_from_azure():

    command = r'az rest --method GET --url "https://graph.microsoft.com/v1.0/users?\$filter=accountEnabled eq false&\$select=displayName,userPrincipalName"   --headers "ConsistencyLevel=eventual"'
    

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        blocked_users = json.loads(result.stdout).get("value", [])
        return {user["userPrincipalName"].lower() for user in blocked_users}
    except subprocess.CalledProcessError as e:
        print("Failed to fetch blocked users from Azure:", e.stderr, file=sys.stderr)
        sys.exit(0)
    

  

def sync_users(azure_users, gcloud_users, dry_run=False):
    gcloud_emails = {user["primaryEmail"].lower() for user in gcloud_users}
    new_users = []

    for user in azure_users:
        email = user["userPrincipalName"].lower()

        # Skip external users
        if "ext" in email:
            continue

        # Check if email domain is in the allowable domains list
        domain = email.split("@")[-1]
        if domain not in ALLOWABLE_DOMAINS:
            print (f"Skipping User: {email} because domain: {domain}")
            continue

        if email in SKIP_USERS:
            continue

        # Add user if they don't exist in Google Cloud
        if email not in gcloud_emails:
            new_users.append(user)

    print(f"\nUsers to be synced ({len(new_users)}):\n")

    for user in new_users:
        email = user["userPrincipalName"]
        name = user.get("displayName", "")
        print(f"- {email} ({name})")
        if not dry_run:
            # Example: Sync user to GCP
            # You may want to use Directory API or gcloud identity commands here
            print(f"Attempting to sync: {email}...")
            create_google_user(user, admin_service)
            # Implement user creation logic here if not dry_run
        else:
            print(f"Simulating sync: {email}")

    if not new_users:
        print("✅ All Azure users already exist in Google Cloud.")

def remove_gcp_users_not_in_azure(azure_users, gcloud_users, dry_run=False):
    gcloud_emails = {user["primaryEmail"].lower() for user in gcloud_users}
    azure_emails = {user["userPrincipalName"].lower() for user in azure_users}

    # Find users in GCP that are not in Azure
    users_to_remove = gcloud_emails - azure_emails

    remove_list = []
    for user in gcloud_users:        
        email = user["primaryEmail"].lower()
        #print(f"Checking user: {email}")
        if email not in azure_emails:
            print(f"---User needs to be removed: {email}")
            remove_list.append(email)

    if not remove_list:
        print("✅ All Google Cloud users are present in Azure.")
        return

    print(f"\nUsers to be removed from Google Cloud ({len(remove_list)}):\n")
    
    for email in remove_list:
        if (email in SKIP_USERS):
            print(f"Skipping removal of user: {email} as it is in the skip list.")
            continue
        print(f"- {email}")
        if not dry_run:
            try:
                admin_service.users().delete(userKey=email).execute()
                print(f"✅ Removed user: {email}")
            except Exception as e:
                print(f"❌ Failed to remove user {email}: {e}")
        else:
            print(f"Simulating removal of: {email}")

def create_google_user(user, admin_service):
    email = user["userPrincipalName"]
    display_name = user.get("displayName", "")

    # Simple name parsing
    name_parts = display_name.split()
    given_name = name_parts[0] if name_parts else "First"
    family_name = name_parts[-1] if len(name_parts) > 1 else "Last"

    g_user = {
        "primaryEmail": email,
        "name": {
            "givenName": given_name,
            "familyName": family_name
        },
        "password": config.INITIAL_PASSWORD,  # You can replace this with generated or config-based value
        "changePasswordAtNextLogin": True
    }

   

    try:
        admin_service.users().insert(body=g_user).execute()
        print(f"✅ Created user: {email}")
    except Exception as e:
        print(f"❌ Failed to create user {email}: {e}")

def create_cloud_identity_user(email, given_name, family_name, password):
    # Get access token using gcloud
    try:
        access_token = subprocess.check_output(
            ["gcloud", "auth", "print-access-token"],
            text=True
        ).strip()
    except subprocess.CalledProcessError as e:
        print("❌ Failed to get access token from gcloud.")
        print(e.output)
        return

    # Define user payload
    user_data = {
        "name": {
            "givenName": given_name,
            "familyName": family_name
        },
        "password": password,
        "primaryEmail": email
    }

    # Call Admin SDK API using curl
    curl_command = [
        "curl", "-s", "-X", "POST", "https://admin.googleapis.com/admin/directory/v1/users",
        "-H", f"Authorization: Bearer {access_token}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(user_data)
    ]

    print(f"📤 Creating user: {email}")
    try:
        response = subprocess.check_output(curl_command, text=True)
        response_json = json.loads(response)
        if 'error' in response_json:
            print("❌ Error creating user:", json.dumps(response_json, indent=2))
        else:
            print("✅ User created successfully:", json.dumps(response_json, indent=2))
    except subprocess.CalledProcessError as e:
        print("❌ Curl command failed:", e.output)


def deactivate_gcp_users_if_deactivated_in_azure(azure_users, gcloud_users, dry_run=False):
    gcloud_emails = {user["primaryEmail"].lower() for user in gcloud_users}
    azure_emails = {user["userPrincipalName"].lower() for user in azure_users}

    # Find users in GCP that are deactivated in Azure
    emails_to_deactivate = fetch_blocked_users_from_azure()
    users_to_deactivate = gcloud_emails - azure_emails
    for user in azure_users:
        email = user["userPrincipalName"].lower()
        if email in emails_to_deactivate:
           users_to_deactivate.add(email)

    if not users_to_deactivate:
        print("✅ All Google Cloud users are active in Azure.")
        return

    print(f"\nUsers to be deactivated in Google Cloud ({len(users_to_deactivate)}):\n")
    
    for email in users_to_deactivate:
        if (email in SKIP_USERS):
            print(f"Skipping deactivation of user: {email} as it is in the skip list.")
            continue
        print(f"- {email}")
        if not dry_run:
            try:
                user = admin_service.users().get(userKey=email).execute()
                user['suspended'] = True
                admin_service.users().update(userKey=email, body=user).execute()
                print(f"✅ Deactivated user: {email}")
            except Exception as e:
                print(f"❌ Failed to deactivate user {email}: {e}")
        else:
            print(f"Simulating deactivation of: {email}")



def main():
    parser = argparse.ArgumentParser(description="Sync users from Microsoft Entra to Google Cloud Identity.")
    parser.add_argument('--dry-run', action='store_true', help='Preview users to be synced without making changes.')

    args = parser.parse_args()

    print("🔄 Fetching Azure AD users...")
    azure_users = fetch_azure_users()

    print("🔄 Fetching Google Cloud Identity users via export_gcloud_users.py...")
    gcloud_users = fetch_gcloud_users()

    sync_users(azure_users, gcloud_users, dry_run=args.dry_run)
    remove_gcp_users_not_in_azure(azure_users, gcloud_users, dry_run=args.dry_run)
    deactivate_gcp_users_if_deactivated_in_azure(azure_users, gcloud_users, dry_run=args.dry_run)

if __name__ == "__main__":
    main()