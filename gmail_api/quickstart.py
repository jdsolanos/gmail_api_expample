import base64
import time
import os
from typing import List 
from google_apis import create_service

user_id_cons = "fundasuvicolstore4@gmail.com"
#user_id_cons = "parkourunal@gmail.com"
class GmailException(Exception):
    """gmail base exception"""

class NoEmailFound(GmailException):
    """no email found"""


def search_emails(query_string:str, label_ids: List=None):
    #el userId es el correo del usuario a consultar. 'me' corre con el usuario logeado
    #en mi caso, no entinedo porque me reconoce el de parkour y no el de la unal
    try:
        message_list_response = service.users().messages().list(
            userId= user_id_cons,
            labelIds= label_ids, 
            q = query_string
        ).execute()

        message_items = message_list_response.get('messages')
        next_page_token = message_list_response.get('nextPageToken')

        while next_page_token:
            message_list_response = service.users().messages().list(
                userId= user_id_cons,
                labelIds= label_ids, 
                q = query_string,
                pageToken = next_page_token
            ).execute()
            message_items.extend(message_list_response.get('messages'))
            next_page_token = message_list_response.get('nextPageToken')
        
        return message_items
    except Exception as e:
        raise NoEmailFound("No Email Returned")
    

def get_message_detail(message_id, msg_format='metadata', metadata_headers: List = None):
    message_detail = service.users().messages().get(
            userId=user_id_cons,
            id = message_id,
            format = msg_format,
            metadataHeaders = metadata_headers
        ).execute()
    return message_detail
    
def get_file_data(message_id, attachment_id,file_name, save_location):
    response = service.users().messages().attachments().get(
            userId=user_id_cons,
            messageId= message_id, 
            id = attachment_id
        ).execute()
    
    file_data = base64.urlsafe_b64decode(response.get('data').encode('UTF-8'))
    return file_data

if __name__ == '__main__':
    CLIENT_FILE = "credentials.json"
    API_NAME = 'gmail'
    API_VERSION = 'v1'
    SCOPES = ['https://mail.google.com/']
    service = create_service(CLIENT_FILE,API_NAME,API_VERSION,SCOPES)
    query_string ='has:attachment from:andreacarolinahd1@gmail.com after:2022/11/01 before:2022/12/31'
    # before:2022/12/31
    save_location = os.getcwd()
    email_messages = search_emails(query_string)

    for email_message in email_messages:
        message_detail = get_message_detail(email_message['id'],msg_format='full',metadata_headers=['parts'])
        message_detail_payload = message_detail.get('payload')
        message_date = message_detail.get('internalDate')
        if 'parts' in message_detail_payload:
            for msg_payload in message_detail_payload['parts']:
                file_name:str = msg_payload['filename']
                ending_file_name = "_fecha_"+message_date+".pdf"
                file_name = file_name.replace(".pdf",ending_file_name)
                body = msg_payload['body']
                if 'attachmentId' in body:
                    attachment_id = body['attachmentId']
                    attachment_content = get_file_data(email_message['id'], attachment_id, file_name, save_location)

                    with open(os.path.join(save_location,'adjuntos',file_name),'wb') as _f:
                        _f.write(attachment_content)
                        print(f"file {file_name} is saved at {save_location}")
        time.sleep(0.5)