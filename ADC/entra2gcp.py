import subprocess
import json
import argparse
import sys


#define constants
from config import ALLOWABLE_DOMAINS, SKIP_USERS

def fetch_azure_users():
    try:
        result = subprocess.run(
            ['az', 'ad', 'user', 'list'],
            capture_output=True, text=True, check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Failed to fetch Azure users:", e.stderr, file=sys.stderr)
        sys.exit(1)

def fetch_gcloud_users():
    try:
        result = subprocess.run(
            ['python3', 'export_gcloud_users.py'],
            capture_output=True, text=True, check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Failed to fetch Google users:", e.stderr, file=sys.stderr)
        sys.exit(1)

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
            print(f"Would sync: {email} ... [SIMULATED]" if dry_run else f"Syncing: {email}")
            # Implement user creation logic here if not dry_run

    if not new_users:
        print("✅ All Azure users already exist in Google Cloud.")

def main():
    parser = argparse.ArgumentParser(description="Sync users from Microsoft Entra to Google Cloud Identity.")
    parser.add_argument('--dry-run', action='store_true', help='Preview users to be synced without making changes.')

    args = parser.parse_args()

    print("🔄 Fetching Azure AD users...")
    azure_users = fetch_azure_users()

    print("🔄 Fetching Google Cloud Identity users via export_gcloud_users.py...")
    gcloud_users = fetch_gcloud_users()

    sync_users(azure_users, gcloud_users, dry_run=args.dry_run)

if __name__ == "__main__":
    main()