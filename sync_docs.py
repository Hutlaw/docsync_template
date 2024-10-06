import subprocess

def run_command(command):
    result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    return result.stdout.strip()

def sync_docs_to_github():
    try:
        run_command('git config --global user.email "github-actions@github.com"')
        run_command('git config --global user.name "GitHub Actions"')
        run_command('git pull origin main')
        run_command('git add .')
        run_command('git commit -m "Updated synced Google Doc"')
        run_command('git push origin main')
        print("Changes successfully pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e.stderr}")
        return

if __name__ == "__main__":
    sync_docs_to_github()
