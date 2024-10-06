import subprocess
import os

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}")
        print(f"Error output: {e.stderr}")
        raise

def create_document_if_missing(file_path):
    """Create the file if it doesn't exist."""
    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w') as f:
            f.write("<html><body><h1>Synced Google Doc</h1></body></html>")
        print(f"File created: {file_path}")
    else:
        print(f"File already exists: {file_path}")

def sync_docs_to_github():
    try:
        run_command('git config --global user.email "github-actions@github.com"')
        run_command('git config --global user.name "GitHub Actions"')
        document_path = 'synced_docs/document.html'
        create_document_if_missing(document_path)
        run_command('git pull origin main')
        changes = run_command('git status --porcelain')

        if changes:
            run_command(f'git add {document_path}')
            run_command('git commit -m "Updated synced Google Doc"')
            run_command('git push origin main')

            print("Changes successfully pushed to GitHub.")
        else:
            print("No changes to commit.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during sync: {e}")
        print(f"Error output: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    sync_docs_to_github()
