import os
import json
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
SERVICE_ACCOUNT_INFO = os.getenv("SERVICE_ACCOUNT_KEY")
DOC_ID = os.getenv("DOCUMENT_ID")

def convert_to_html(content):
    html = ""
    
    for element in content['body']['content']:
        if 'paragraph' in element:
            paragraph = element['paragraph']
            if 'paragraphStyle' in paragraph:
                if paragraph['paragraphStyle'].get('namedStyleType') == 'HEADING_1':
                    html += '<h1>'
                    html += get_paragraph_text(paragraph)
                    html += '</h1>'
                elif paragraph['paragraphStyle'].get('namedStyleType') == 'HEADING_2':
                    html += '<h2>'
                    html += get_paragraph_text(paragraph)
                    html += '</h2>'
                elif paragraph['paragraphStyle'].get('namedStyleType') == 'HEADING_3':
                    html += '<h3>'
                    html += get_paragraph_text(paragraph)
                    html += '</h3>'
                else:
                    html += '<p>'
                    html += get_paragraph_text(paragraph)
                    html += '</p>'
            else:
                html += '<p>'
                html += get_paragraph_text(paragraph)
                html += '</p>'

        elif 'table' in element:
            table = element['table']
            html += '<table border="1">'
            for row in table['tableRows']:
                html += '<tr>'
                for cell in row['tableCells']:
                    html += '<td>'
                    for content in cell['content']:
                        html += convert_to_html({'body': {'content': [content]}})
                    html += '</td>'
                html += '</tr>'
            html += '</table>'

        elif 'inlineObjectElement' in element:
            inline_object_id = element['inlineObjectElement']['inlineObjectId']
            html += handle_inline_image(content, inline_object_id)

    return html

def get_paragraph_text(paragraph):
    text = ""
    for elem in paragraph['elements']:
        if 'textRun' in elem:
            text_run = elem['textRun']
            style = text_run.get('textStyle', {})
            content = text_run['content']

            if style.get('bold'):
                content = f"<b>{content}</b>"
            if style.get('italic'):
                content = f"<i>{content}</i>"
            if style.get('underline'):
                content = f"<u>{content}</u>"

            text += content
    return text

def handle_inline_image(content, inline_object_id):
    try:
        inline_object = content['inlineObjects'][inline_object_id]
        embedded_object = inline_object['inlineObjectProperties']['embeddedObject']
        if 'imageProperties' in embedded_object:
            source = embedded_object['imageProperties']['contentUri']
            width = embedded_object['size']['width']['magnitude']
            height = embedded_object['size']['height']['magnitude']
            return f'<img src="{source}" width="{width}" height="{height}"/>'
        return ""
    except Exception as e:
        logging.error(f"Failed to process inline image: {e}")
        return ""

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
        html_content = convert_to_html(content)
        with open(file_path, 'w') as file:
            file.write(f"<html><body>{html_content}</body></html>")
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
