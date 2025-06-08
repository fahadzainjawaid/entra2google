import json
from google.auth import default
from googleapiclient.discovery import build
from google.auth.exceptions import DefaultCredentialsError

def get_all_users():
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
        users = get_all_users()
        print(json.dumps(users, indent=2))  # output to stdout
    except DefaultCredentialsError:
        print("ERROR: Unable to load ADC credentials. Run `gcloud auth application-default login`.")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    main()