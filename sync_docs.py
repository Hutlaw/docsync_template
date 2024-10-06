import subprocess
import os
import shutil
from google.oauth2 import service_account
from googleapiclient.discovery import build

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}")
        print(f"Error output: {e.stderr}")
        raise

def export_google_doc_to_html(document_id, file_path):
    creds = service_account.Credentials.from_service_account_file(os.getenv("SERVICE_ACCOUNT_KEY"))
    docs_service = build('docs', 'v1', credentials=creds)
    doc = docs_service.documents().get(documentId=document_id).execute()
    content = doc.get('body').get('content')
    
    html_content = "<html><body>"
    for element in content:
        if 'paragraph' in element:
            for text_run in element['paragraph']['elements']:
                if 'textRun' in text_run:
                    html_content += text_run['textRun']['content'].replace('\n', '<br>') + '<br>'
    html_content += "</body></html>"

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(html_content)

def sync_docs_to_github():
    try:
        run_command('git config --global user.email "github-actions@github.com"')
        run_command('git config --global user.name "GitHub Actions"')

        document_path = 'synced_docs/document.html'

        export_google_doc_to_html(os.getenv("DOCUMENT_ID"), document_path)

        if os.path.exists(document_path):
            shutil.move(document_path, document_path + ".bak")

        run_command('git pull origin main')

        if os.path.exists(document_path + ".bak"):
            shutil.move(document_path + ".bak", document_path)

        changes = run_command('git status --porcelain')

        if changes:
            run_command(f'git add {document_path}')
            run_command('git commit -m "Updated synced Google Doc"')
            run_command('git push --force origin main')

            print("Changes successfully pushed to GitHub."
        else:
            print("No changes to commit.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during sync: {e}")
        print(f"Error output: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    sync_docs_to_github()
