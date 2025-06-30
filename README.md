# Using "Application Default Credentials" 
This means it will not require any special configuration of service accounts etc. Just uses the `gcloud auth application-default login` credentials for Google and uses the `az login` 

## If no Azure Subscriptions
- If there are no Azure Subscriptions, then login like so: `az login --allow-no-subscriptions`
- Sometimes, az login would give the url to login in a weird way and add an extra '.' or ':' or 'prompt" error. So pay attention to the url it prompts. Might need manually copy paste the url portion into the browser.

# Usage 
## To Sync a User
- From root of the directory
- `gcloud auth application-default login`
- `az login --allow-no-subscriptions`
    - Or, just `az login` and then select a subscription
- `python3 -m sync.entra2gcp`

## To Create a new user
- This will create a a user, and then you can run sync to move them to Google.
- `python3 -m create.addUser --firstname=FIRSTNAME --lastname=LASTNAME`


### Usage `Dry Run Mode`
- - `python3 -m sync.entra2gcp --dry-run`
 
### Test Usage: Just list Google Cloud Identity Users
- `python3 -m sync.export_gcloud_users`

### Test Usage: Just list Azure Entra Users
- `az ad user list`
- OR: `az ad user list --query '[].{userPrincipalName:userPrincipalName, displayName:displayName}' -o json`
 
  
# Setup
We need to create a service account in a GCP project where we want to house the identity sync. To do this, simply use the python script in the `setup/` folder.
`python3 -m setup.sa-setup`

## Config/config.py
We need to have all the configuration in the `config/config.py` for the Setup and Sync. The sample is provided as `config/config.py.sample`. Simply, rename or copy it to `config.py` and add your values. `config.py` will not commit with the code base, it is added in .gitignore - since it may contain secrets or non-public information. If you operate with multiple organizations or directories, you can use the an environment variable to set different config values. This is also provided in the sample, but commented out.

## Serivce Account Keys
We need to create service account keys to authenticate using the org-wide service account. The `setup/sa-setup.py` will attempt to create the keys. However, it might fail if your org has policies preventing Service Account keys. If so, you'll need to enable it by following these steps:

Steps in the Google Cloud Console
1. Go to the Organization Policies page https://console.cloud.google.com/iam-admin/orgpolicies
2. In the "Select a project" dropdown (top bar), choose your target project.
3. Use the search bar or scroll to find: `Disable Service Account Key Creation` (Constraint: constraints/iam.disableServiceAccountKeyCreation)
    a. You will need `Organization Policy Administrator` role to do this.
    b. Go to your IAM at Organization level, and add the Organization Policy Admin role
4. Click on the policy name to open the settings.
5. Click "Edit" (pencil icon in the top right).
6. Under "Policy enforcement", uncheck the box labeled:
`✅ Enforce (disabling this allows key creation)`
7. Click "Save".
