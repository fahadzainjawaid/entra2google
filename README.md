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
 
  
