import os
import json
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
DOC_ID = os.getenv("DOCUMENT_ID")

def authenticate():
    if CLIENT_ID is None or CLIENT_SECRET is None:
        logging.error("Google Client ID and Secret are missing from environment variables.")
        raise EnvironmentError("Missing Google API credentials.")

    creds = None
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            logging.error(f"Error reading token.json: {e}")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logging.info("Token refreshed successfully.")
            except Exception as e:
                logging.error(f"Error refreshing token: {e}")
                raise
        else:
            try:
                flow = InstalledAppFlow.from_client_config({
                    "installed": {
                        "client_id": CLIENT_ID,
                        "client_secret": CLIENT_SECRET,
                        "redirect_uris": ["http://localhost"],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://accounts.google.com/o/oauth2/token"
                    }
                }, SCOPES)
                creds = flow.run_local_server(port=0)
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
                logging.info("New token created and saved to token.json.")
            except Exception as e:
                logging.error(f"Error during OAuth flow: {e}")
                raise
    return creds

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
