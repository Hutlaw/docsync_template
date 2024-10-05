import os
import json
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from base64 import b64decode

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

def element_to_html(text_run):
    """ Convert a textRun element from Google Docs to styled HTML text """
    content_text = text_run['content']
    text_style = text_run.get('textStyle', {})
    html_text = content_text

    # Handle bold, italic, underline, strikethrough
    if text_style.get('bold'):
        html_text = f"<b>{html_text}</b>"
    if text_style.get('italic'):
        html_text = f"<i>{html_text}</i>"
    if text_style.get('underline'):
        html_text = f"<u>{html_text}</u>"
    if text_style.get('strikethrough'):
        html_text = f"<strike>{html_text}</strike>"

    # Handle text color
    if 'foregroundColor' in text_style:
        color = text_style['foregroundColor'].get('color', {}).get('rgbColor', {})
        if color:
            red = int(color.get('red', 0) * 255)
            green = int(color.get('green', 0) * 255)
            blue = int(color.get('blue', 0) * 255)
            html_text = f'<span style="color: rgb({red}, {green}, {blue});">{html_text}</span>'

    # Handle font size
    if 'fontSize' in text_style:
        size = text_style['fontSize'].get('magnitude', 12)  # Default font size 12
        html_text = f'<span style="font-size:{size}px;">{html_text}</span>'

    return html_text

def save_doc_as_html(content):
    try:
        if not os.path.exists("synced_docs"):
            os.mkdir("synced_docs")
            logging.info("Created directory: synced_docs")
        
        file_path = 'synced_docs/document.html'
        
        with open(file_path, 'w') as file:
            # Write the basic HTML structure
            file.write('<html><body>\n')
            
            for element in content['body']['content']:
                # Paragraphs and Headers
                if 'paragraph' in element:
                    paragraph = element['paragraph']
                    para_style = paragraph.get('paragraphStyle', {})
                    heading = para_style.get('heading')
                    
                    # Handle headings (h1-h6)
                    if heading:
                        level = heading.replace('HEADING_', '')
                        file.write(f'<h{level}>')
                        for elem in paragraph['elements']:
                            if 'textRun' in elem:
                                file.write(element_to_html(elem['textRun']))
                        file.write(f'</h{level}>\n')
                    else:
                        file.write('<p>')
                        for elem in paragraph['elements']:
                            if 'textRun' in elem:
                                file.write(element_to_html(elem['textRun']))
                        file.write('</p>\n')

                    # Handle indentation, alignment, and spacing
                    if 'indentStart' in para_style:
                        indent = para_style['indentStart'].get('magnitude', 0)
                        file.write(f'<div style="margin-left:{indent}px;">\n')

                # Handle Images
                if 'inlineObjectElement' in element:
                    inline_object_id = element['inlineObjectElement']['inlineObjectId']
                    inline_object = content['inlineObjects'][inline_object_id]
                    embedded_object = inline_object['inlineObjectProperties']['embeddedObject']

                    # Check if there's an image
                    if 'imageProperties' in embedded_object:
                        image_source = embedded_object['imageProperties']['contentUri']
                        file.write(f'<img src="{image_source}" alt="Image">\n')

                # Handle Tables
                if 'table' in element:
                    table = element['table']
                    rows = table['tableRows']
                    file.write('<table border="1">\n')

                    for row in rows:
                        file.write('<tr>\n')
                        cells = row['tableCells']
                        for cell in cells:
                            file.write('<td>')
                            for content in cell['content']:
                                if 'paragraph' in content:
                                    for elem in content['paragraph']['elements']:
                                        if 'textRun' in elem:
                                            file.write(element_to_html(elem['textRun']))
                            file.write('</td>\n')
                        file.write('</tr>\n')
                    file.write('</table>\n')

            file.write('</body></html>\n')
            
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
