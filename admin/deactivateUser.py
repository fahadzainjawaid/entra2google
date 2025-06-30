import argparse
import subprocess
from config import config

DOMAIN = config.DOMAIN
SKIP_USERS = config.SKIP_USERS

GREEN = config.GREEN
RED = config.RED
RESET = config.RESET

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

def deactivate_user(email, dry_run=False):
    command = f"az ad user update --id {email} --account-enabled false"
    run_command(command, dry_run=dry_run)

def delete_user(email, dry_run=False):
    command = f"az ad user delete --id {email}"
    run_command(command, dry_run=dry_run)

def main():
    parser = argparse.ArgumentParser(description="Deactivate or delete a Microsoft Entra user")
    parser.add_argument("--userEmail", required=True, help="Email of the user to manage")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without executing")
    parser.add_argument("--delete", action="store_true", help="Delete the user after deactivation")
    args = parser.parse_args()

    user_email = args.userEmail.lower()

    if user_email in [u.lower() for u in SKIP_USERS]:
        print(f"{RED}Skipping user {user_email} as it's in SKIP_USERS.{RESET}")
        return

    print(f"{GREEN}Processing user: {user_email}{RESET}")
    deactivate_user(user_email, dry_run=args.dry_run)

    if args.delete:
        delete_user(user_email, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
