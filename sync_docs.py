import subprocess
import os
import shutil

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
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Create an empty file or add default content
        with open(file_path, 'w') as f:
            f.write("<html><body><h1>Synced Google Doc</h1></body></html>")
        print(f"File created: {file_path}")
    else:
        print(f"File already exists: {file_path}")

def sync_docs_to_github():
    try:
        # Set up git user details
        run_command('git config --global user.email "github-actions@github.com"')
        run_command('git config --global user.name "GitHub Actions"')

        # Path to document
        document_path = 'synced_docs/document.html'

        # Remove the document to avoid conflict during pull
        if os.path.exists(document_path):
            print(f"Temporarily removing {document_path} to avoid pull conflicts")
            shutil.move(document_path, document_path + ".bak")

        # Pull the latest changes from the main branch
        run_command('git pull origin main')

        # Restore the document after pull
        if os.path.exists(document_path + ".bak"):
            print(f"Restoring {document_path}")
            shutil.move(document_path + ".bak", document_path)

        # Ensure the document exists
        create_document_if_missing(document_path)

        # Check if there are changes to commit
        changes = run_command('git status --porcelain')

        if changes:
            # Stage all changes
            run_command(f'git add {document_path}')

            # Commit the changes
            run_command('git commit -m "Updated synced Google Doc"')

            # Force push the changes to the remote branch
            run_command('git push --force origin main')

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
