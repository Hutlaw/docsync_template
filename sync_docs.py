import os
import json
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
SERVICE_ACCOUNT_INFO = os.getenv("SERVICE_ACCOUNT_KEY")
DOC_ID = os.getenv("DOCUMENT_ID")

def authenticate():
    if not SERVICE_ACCOUNT_INFO:
        logging.error("Service Account key missing from environment variables.")
        raise EnvironmentError("Missing Service Account credentials.")

    try:
        service_account_info = json.loads(SERVICE_ACCOUNT_INFO)
        creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
        logging.info("Successfully authenticated using Service Account.")
        return creds
    except Exception as e:
        logging.error(f"Failed to authenticate using Service Account: {e}")
        raise

def fetch_google_doc(service):
    try:
        doc = service.documents().get(documentId=DOC_ID).execute()
        logging.info(f"Successfully fetched Google Doc with ID: {DOC_ID}")
        return doc
    except Exception as e:
        logging.error(f"Failed to fetch Google Doc: {e}")
        raise

def save_doc_as_html(content):
    try:
        if not os.path.exists("synced_docs"):
            os.mkdir("synced_docs")
            logging.info("Created directory: synced_docs")
        
        file_path = 'synced_docs/document.html'
        with open(file_path, 'w') as file:
            for element in content['body']['content']:
                file.write(json.dumps(element))
        logging.info(f"Document saved as HTML to {file_path}")
        return file_path
    except Exception as e:
        logging.error(f"Failed to save document as HTML: {e}")
        raise

def sync_docs_to_github():
    creds = authenticate()
    service = build('docs', 'v1', credentials=creds)
    doc = fetch_google_doc(service)
    file_path = save_doc_as_html(doc)

if __name__ == '__main__':
    try:
        sync_docs_to_github()
    except Exception as e:
        logging.error(f"Script failed: {e}")
        exit(1)
