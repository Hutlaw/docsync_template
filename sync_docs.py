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
    header_added = False
    footer_added = False
    
    for element in content['body']['content']:
        if 'paragraph' in element:
            paragraph = element['paragraph']
            if 'paragraphStyle' in paragraph:
                if paragraph['paragraphStyle'].get('namedStyleType') == 'HEADING_1' and not header_added:
                    html += '<header><h1 style="color:#333;text-align:center;">'
                    html += get_paragraph_text(paragraph)
                    html += '</h1></header>'
                    header_added = True
                elif paragraph['paragraphStyle'].get('namedStyleType') == 'NORMAL_TEXT':
                    html += format_paragraph(paragraph)
            else:
                html += format_paragraph(paragraph)

        elif 'table' in element:
            html += format_table(element['table'])

        elif 'inlineObjectElement' in element:
            inline_object_id = element['inlineObjectElement']['inlineObjectId']
            html += handle_inline_image(content, inline_object_id)

        if element.get('endIndex') == content['endIndex'] and not footer_added:
            footer_added = True
            html += '<footer style="text-align:center;color:#555;font-size:12px;">Generated Footer</footer>'

    return html

def format_paragraph(paragraph):
    style = paragraph.get('paragraphStyle', {})
    indent = style.get('indentStart', {}).get('magnitude', 0)
    align = style.get('alignment', 'LEFT').lower()
    spacing = style.get('lineSpacing', 1.15)
    
    html = f'<p style="text-align:{align}; margin-left:{indent}pt; line-height:{spacing};">'
    html += get_paragraph_text(paragraph)
    html += '</p>'
    
    return html

def format_table(table):
    html = '<table style="border-collapse: collapse; width:100%;">'
    for row in table['tableRows']:
        html += '<tr>'
        for cell in row['tableCells']:
            html += '<td style="border: 1px solid #ddd; padding: 8px;">'
            for content in cell['content']:
                html += convert_to_html({'body': {'content': [content]}})
            html += '</td>'
        html += '</tr>'
    html += '</table>'
    return html

def get_paragraph_text(paragraph):
    text = ""
    for elem in paragraph['elements']:
        if 'textRun' in elem:
            text_run = elem['textRun']
            style = text_run.get('textStyle', {})
            content = text_run['content']

            # Text formatting options
            if style.get('bold'):
                content = f"<b>{content}</b>"
            if style.get('italic'):
                content = f"<i>{content}</i>"
            if style.get('underline'):
                content = f"<u>{content}</u>"
            if style.get('strikethrough'):
                content = f"<s>{content}</s>"
            if style.get('subscript'):
                content = f"<sub>{content}</sub>"
            if style.get('superscript'):
                content = f"<sup>{content}</sup>"
            if style.get('highlightColor'):
                highlight_color = get_rgb(style['highlightColor']['color']['rgbColor'])
                content = f'<span style="background-color:rgb({highlight_color});">{content}</span>'
            if 'fontSize' in style:
                size = style['fontSize']['magnitude']
                content = f'<span style="font-size:{size}pt;">{content}</span>'
            if 'foregroundColor' in style:
                color = style['foregroundColor']['color']['rgbColor']
                rgb = get_rgb(color)
                content = f'<span style="color:rgb({rgb});">{content}</span>'
            if style.get('fontFamily'):
                font_family = style['fontFamily']
                content = f'<span style="font-family:{font_family};">{content}</span>'

            text += content
    return text

def get_rgb(color_dict):
    r = int(color_dict.get('red', 0) * 255)
    g = int(color_dict.get('green', 0) * 255)
    b = int(color_dict.get('blue', 0) * 255)
    return f"{r},{g},{b}"

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
        return creds
    except Exception as e:
        raise

def fetch_google_doc(service):
    try:
        doc = service.documents().get(documentId=DOC_ID).execute()
        return doc
    except Exception as e:
        raise

def save_doc_as_html(content):
    try:
        if not os.path.exists("synced_docs"):
            os.mkdir("synced_docs")
        
        file_path = 'synced_docs/document.html'
        html_content = convert_to_html(content)
        page_style = '<style>body{background-color:#f0f0f0;margin:20px;padding:20px;font-family:Arial;}</style>'
        with open(file_path, 'w') as file:
            file.write(f"<html>{page_style}<body>{html_content}</body></html>")
        return file_path
    except Exception as e:
        raise

def sync_docs_to_github():
    creds = authenticate()
    service = build('docs', 'v1', credentials=creds)
    doc = fetch_google_doc(service)
    file_path = save_doc_as_html(doc)

if __name__ == '__main__':
    sync_docs_to_github()
