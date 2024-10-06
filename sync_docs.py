import os
import json
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_INFO = os.getenv("SERVICE_ACCOUNT_KEY")
DOC_ID = os.getenv("DOCUMENT_ID")

def authenticate():
    if not SERVICE_ACCOUNT_INFO:
        logging.error("Service Account key missing from environment variables.")
        raise EnvironmentError("Missing Service Account credentials.")

    try:
        service_account_info = json.loads(SERVICE_ACCOUNT_INFO)
        creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
        return creds
    except Exception as e:
        raise

def export_google_doc_as_html(service, doc_id):
    try:
        request = service.files().export(fileId=doc_id, mimeType='text/html')
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
            logging.info(f"Download {int(status.progress() * 100)}%.")
        
        file_content.seek(0)
        return file_content
    except Exception as e:
        logging.error(f"Failed to export Google Doc as HTML: {e}")
        raise

def save_html_file(file_content, filename='document.html'):
    try:
        if not os.path.exists("synced_docs"):
            os.mkdir("synced_docs")
        file_path = os.path.join("synced_docs", filename)
        with open(file_path, 'wb') as f:
            f.write(file_content.read())
        return file_path
    except Exception as e:
        logging.error(f"Failed to save HTML file: {e}")
        raise

def sync_docs_to_github():
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    file_content = export_google_doc_as_html(service, DOC_ID)
    file_path = save_html_file(file_content)
    logging.info(f"HTML file saved at: {file_path}")

if __name__ == '__main__':
    sync_docs_to_github()
