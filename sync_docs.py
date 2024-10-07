import subprocess
import os
import shutil
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}")
        print(f"Error output: {e.stderr}")
        raise

def export_google_doc_to_html(document_id):
    service_account_info = json.loads(os.getenv("SERVICE_ACCOUNT_KEY"))
    creds = service_account.Credentials.from_service_account_info(service_account_info)
    drive_service = build('drive', 'v3', credentials=creds)

    request = drive_service.files().export_media(fileId=document_id, mimeType='text/html')
    return request.execute()

def modify_html(html_content, config):
    soup = BeautifulSoup(html_content, 'html.parser')

    if soup.title:
        soup.title.string = config['tab_title']
    else:
        new_title = soup.new_tag('title')
        new_title.string = config['tab_title']
        soup.head.append(new_title)

    favicon = soup.new_tag('link', rel='icon', href=config['favicon_url'])
    soup.head.append(favicon)

    alignment = config['html_alignment']
    body_style = soup.body.get('style', '')
    if alignment == 'center':
        body_style += ' text-align: center;'
    elif alignment == 'right':
        body_style += ' text-align: right;'
    else:
        body_style += ' text-align: left;'
    soup.body['style'] = body_style

    return str(soup)

def sync_docs_to_github():
    try:
        with open('config.json') as f:
            config = json.load(f)

        raw_html = export_google_doc_to_html(os.getenv("DOCUMENT_ID"))

        modified_html = modify_html(raw_html, config)

        github_html_path = config['github_html_path']
        os.makedirs(os.path.dirname(github_html_path), exist_ok=True)
        with open(github_html_path, 'w', encoding='utf-8') as f:
            f.write(modified_html)

        run_command('git config --global user.email "github-actions@github.com"')
        run_command('git config --global user.name "GitHub Actions"')

        run_command('git pull origin main')

        changes = run_command('git status --porcelain')
        if changes:
            run_command(f'git add {github_html_path}')
            run_command('git commit -m "Updated synced Google Doc"')
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
