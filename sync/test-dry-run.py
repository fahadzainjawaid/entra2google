

command = "python3 entra2gcp.py --dry-run"
import subprocess
try:
    result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
    print("Dry run output:")
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print("Error during dry run:")
    print(e.stderr)
    print(f"Command failed with return code: {e.returncode}")
    exit(1)
    print("Dry run completed successfully.")
except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")
    exit(1) 