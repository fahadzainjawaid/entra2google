import json
from google.auth import default
from googleapiclient.discovery import build
from google.auth.exceptions import DefaultCredentialsError

#import config from config.py which is located in parent directory/config directory
from config import config

#print("Using config file: ", config)
#print("Project ID: ", config.PROJECT_ID)
#print(f"Service Account Name: {config.SERVICE_ACCOUNT_NAME}")
#print(f"Delegated Admin Email: {config.DELEGATED_ADMIN_EMAIL}")
#print(f"OAuth Scopes: {config.OAUTH_SCOPES}")
#print(f"Initial Password: {config.INITIAL_PASSWORD}")



def set_quota_project():
    """
    Set the quota project for the Google API client.
    This is necessary to ensure that the API calls are billed to the correct project.
    """
    command = f"gcloud auth application-default set-quota-project {config.PROJECT_ID}"
    import subprocess
    try:
        subprocess.run(command, shell=True, check=True)
        #print(f"Quota project set to {config.PROJECT_ID}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to set quota project: {e}")
        raise

def get_all_users():
    # get credentails for a project by fetch project id from the config file

    # and then use the default credentials to access the Google Admin SDK
    # This assumes that the environment is set up with the necessary permissions

    credentials, _ = default(scopes=['https://www.googleapis.com/auth/admin.directory.user.readonly'])
    service = build('admin', 'directory_v1', credentials=credentials)

    all_users = []
    page_token = None

    while True:
        response = service.users().list(
            customer='my_customer',
            maxResults=100,
            orderBy='email',
            pageToken=page_token
        ).execute()

        users = response.get('users', [])
        all_users.extend(users)

        page_token = response.get('nextPageToken')
        if not page_token:
            break

    return all_users

def main():
    try:
        set_quota_project()  # Set the quota project for the API client
        users = get_all_users()
        print(json.dumps(users, indent=2))  # output to stdout
    except DefaultCredentialsError:
        print("ERROR: Unable to load ADC credentials. Run `gcloud auth application-default login`.")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    main()