## define the domains in the array below, and then rename this file to 'config.py'
## git will not include this config.py in the git repo

ALLOWABLE_DOMAINS = [
    "example.com"
]


SKIP_USERS = [
    "skip.me@domain.com",
    "skip.me.too@example.com",
]


KEY_FILE_NAME = "gcloud-ad-sync-sa-key.json"  # Name of the service account key file
PROJECT_ID = "Your-gcp-project-id"  # Your GCP project ID
SERVICE_ACCOUNT_NAME = "gcloud-ad-sync-sa"  # Name of the service account
DELEGATED_ADMIN_EMAIL = "super.admin@domina.com"  # must be a super admin
OAUTH_SCOPES = ["https://www.googleapis.com/auth/admin.directory.user"]  # OAuth scopes for the service account

INITIAL_PASSWORD = "tempPass123!"  # Initial password for new users