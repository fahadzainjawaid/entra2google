# Using "Application Default Credentials" 
This means it will not require any special configuration of service accounts etc. Just uses the `gcloud auth application-default login` credentials for Google and uses the `az login` 

## If no Azure Subscriptions
- If there are no Azure Subscriptions, then login like so: `az login --allow-no-subscriptions`
- Sometimes, az login would give the url to login in a weird way and add an extra '.' or ':' or 'prompt" error. So pay attention to the url it prompts. Might need manually copy paste the url portion into the browser.

## Usage 
- From inside "ADC" directory
- `gcloud auth application-default login`
- `az login --allow-no-subscriptions`
- `python3 entra2gcp.py`

### Usage `Dry Run Mode`
- - `python3 entra2gcp.py --dry-run`
 
### Test Usage: Just list Google Cloud Identity Users
- `python3 export_gcloud_users.py`

### Test Usage: Just list Azure Entra Users
- `az ad user list`
- OR: `az ad user list --query '[].{userPrincipalName:userPrincipalName, displayName:displayName}' -o json`
 
  
# Setup
We need to create a service account in a GCP project where we want to house the identity sync. To do this, simply use the python script in the `setup/` folder.
`python3 sa-setup.py`

## Setup/config.py
We need to have all the configuration in the setup/config.py for the Setup. The sample is provided as `config.py.sample`. Simply, rename or copy it to `config.py` and add your values. `config.py` will not commit with the code base, it is added in .gitignore - since it may contain secrets or non-public information.

## Sync/config.py
We also need some of the similar values from `setup/config.py` to the sync service. A sample is provded as `sample.config.py`. Simply, rename or copy it to `config.py` and add your values. `config.py` will not commit with the code base, it is added in .gitignore - since it may contain secrets or non-public information.

## Serivce Account Keys
We need to create service account keys to authenticate using the org-wide service account. The `setup/sa-setup.py` will attempt to create the keys. However, it might fail if your org has policies preventing Service Account keys. If so, you'll need to enable it by following these steps:

Steps in the Google Cloud Console
1. Go to the Organization Policies page https://console.cloud.google.com/iam-admin/orgpolicies
2. In the "Select a project" dropdown (top bar), choose your target project.
3. Use the search bar or scroll to find: `Disable Service Account Key Creation` (Constraint: constraints/iam.disableServiceAccountKeyCreation)
4. Click on the policy name to open the settings.
5. Click "Edit" (pencil icon in the top right).
6. Under "Policy enforcement", uncheck the box labeled:
`✅ Enforce (disabling this allows key creation)`
7. Click "Save".