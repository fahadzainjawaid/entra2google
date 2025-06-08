# Using "Application Default Credentials" 
This means it will not require any special configuration of service accounts etc. Just uses the `gcloud auth application-default login` credentials for Google and uses the `az login` 

## If no Azure Subscriptions
- If there are no Azure Subscriptions, then login like so: `az login --allow-no-subscriptions`
- Sometimes, az login would give the url to login in a weird way and add an extra '.' or ':' or 'prompt" error. So pay attention to the url it prompts. Might need manually copy paste the url portion into the browser.
