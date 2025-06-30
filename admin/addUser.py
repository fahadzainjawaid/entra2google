import argparse
import subprocess
import json
import uuid

from config import   config 

DOMAIN = config.DOMAIN
GROUP_IDS = config.GROUP_IDS
APP_IDS = config.APP_IDS


GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def run_command(command, dry_run=False):
    print(f"{GREEN}Running: {command}{RESET}")
    if dry_run:
        print(f"{GREEN}[Dry Run] Command not executed.{RESET}")
        return None
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"{RED}Error: {result.stderr.strip()}{RESET}")
    else:
        print(f"{GREEN}Success: {result.stdout.strip()}{RESET}")
    return result

def list_verified_domains():
    print(f"{GREEN}Fetching verified domain names...{RESET}")
    command = r'az rest --method GET --uri "https://graph.microsoft.com/v1.0/domains?$filter=isVerified eq true&$select=id"'
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        data = json.loads(result.stdout)
        domains = [d['id'] for d in data.get('value', [])]
        print(f"{GREEN}Verified Domains:{RESET}")
        for d in domains:
            print(f"  - {d}")
    else:
        print(f"{RED}Failed to retrieve domains:{RESET} {result.stderr.strip()}")

def create_user(firstname, lastname, dry_run=False):
    email = f"{firstname.lower()}.{lastname.lower()}@{DOMAIN}"
    user_principal_name = email
    display_name = f"{firstname} {lastname}"
    password = str(uuid.uuid4())[:12] + "!aA"

    user_payload = {
        "accountEnabled": True,
        "displayName": display_name,
        "mailNickname": f"{firstname.lower()}.{lastname.lower()}",
        "userPrincipalName": user_principal_name,
        "givenName": firstname,
        "surname": lastname,
        "passwordProfile": {
            "forceChangePasswordNextSignIn": True,
            "password": password
        }
    }

    print(f"{GREEN}User payload being submitted:{RESET}")
    print(f"{GREEN}{json.dumps(user_payload, indent=2)}{RESET}")

    command = f"az rest --method POST --uri https://graph.microsoft.com/v1.0/users --body '{json.dumps(user_payload)}'"
    result = run_command(command)

    if result.returncode != 0 and "The domain portion of the userPrincipalName property is invalid" in result.stderr:
        list_verified_domains()
        return None

    if result.returncode == 0:
        print(f"{GREEN}User {user_principal_name} created successfully with password: {password}{RESET}")
        return user_principal_name
    return None

def get_user_id(upn, dry_run=False):
    command = f"az ad user show --id {upn} --query id -o tsv"
    result = run_command(command)
    return result.stdout.strip() if result.returncode == 0 else None

def add_user_to_groups(user_id, dry_run=False):
    for group_id in GROUP_IDS:


        pcommand= 'az rest --method POST --uri "https://graph.microsoft.com/v1.0/groups/$GROUP_ID/members/\$ref" --body "{\\"@odata.id\\": \\"https://graph.microsoft.com/v1.0/directoryObjects/$USER_ID\\"}"'
        pcommand = pcommand.replace("$GROUP_ID", group_id).replace("$USER_ID", user_id)

        command = pcommand
        #body_payload = {"@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{user_id}"}
        #command = f'az rest --method POST --uri "https://graph.microsoft.com/v1.0/groups/{group_id}/members/$ref" --body \'{json.dumps(body_payload)}\''

        print(f"{GREEN}Adding user to group: {group_id}{RESET}")
        print(f"{GREEN}User ID: {user_id}{RESET}")

        run_command(command)

def assign_user_to_apps(user_id, dry_run=False):
    for app_id in APP_IDS:

        pcommand = 'az rest --method POST --url "https://graph.microsoft.com/v1.0/servicePrincipals/$APP_ID/appRoleAssignedTo" --body "{\\"principalId\\":\\"$USER_ID\\",\\"resourceId\\":\\"$APP_ID\\",\\"appRoleId\\":\\"$ROLE_ID\\"}"'
        pcommand = pcommand.replace("$APP_ID", app_id).replace("$USER_ID", user_id).replace("$ROLE_ID", config.DEFAULT_USER_APP_ROLE_ID)
#        command = f"az rest --method POST --uri https://graph.microsoft.com/v1.0/servicePrincipals/{app_id}/appRoleAssignments --body '{{\"principalId\": \"{user_id}\", \"resourceId\": \"{app_id}\", \"appRoleId\": \"00000000-0000-0000-0000-000000000000\"}}'"
        command = pcommand
        print (f"{GREEN}Assigning user to app: {app_id}{RESET}")
        run_command(command)

def main():
    parser = argparse.ArgumentParser(description="Create and assign a Microsoft Entra user")
    parser.add_argument("--firstname", required=True, help="User's first name")
    parser.add_argument("--lastname", required=True, help="User's last name")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without executing")

    args = parser.parse_args()

    upn = create_user(args.firstname, args.lastname, dry_run=args.dry_run)
    if not upn:
        return

    user_id = get_user_id(upn, dry_run=args.dry_run)
    if not user_id:
        return

    add_user_to_groups(user_id, dry_run=args.dry_run)
    assign_user_to_apps(user_id, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
