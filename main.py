from __future__ import print_function
import pickle
from typing import List, Tuple
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors
import re
from database import DatabaseService
import sys
from tqdm import tqdm
from dateutil.parser import parse 


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']
TAG_RE = re.compile(r'<[^>]+>')
toolbar_width = 40

# setup toolbar
sys.stdout.write("[%s]" % (" " * toolbar_width))
sys.stdout.flush()
sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['


class GmailService:
   
  def __init__(self) -> None:
    pass

  def list_messages_with_labels(self, service: object, user_id:int, label_ids: List = None) -> List[int]:
    """List all Messages of the user's mailbox with label_ids applied.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      label_ids: Only return Messages with these labelIds applied.

    Returns:
      List of Messages that have all required Labels applied. Note that the
      returned list contains Message IDs, you must use get with the
      appropriate id to get the details of a Message.
    """

    if label_ids is None:
      label_ids = []
    try:
      response = service.users().messages().list(userId=user_id,labelIds=label_ids).execute()
      messages = []
      if 'messages' in response:
        messages.extend(response['messages'])

      while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(userId=user_id,labelIds=label_ids,pageToken=page_token).execute()
        messages.extend(response['messages'])

      return [i["id"] for i in messages]
    except errors.HttpError as error:
      print ('An error occurred: ' , error)


  def initialize_gmail_credentials(self) -> Tuple[object,int,List[str],bool]:
      """
      Shows basic usage of the Gmail API.
      Lists the user's Gmail labels.
      """
      status=True
      creds = None
      # The file token.pickle stores the user's access and refresh tokens, and is
      # created automatically when the authorization flow completes for the first
      # time.
      if os.path.exists('token.pickle'):
          with open('token.pickle', 'rb') as token:
              creds = pickle.load(token)
      # If there are no (valid) credentials available, let the user log in.
      if not creds or not creds.valid:
          if creds and creds.expired and creds.refresh_token:
              creds.refresh(Request())
          else:
              flow = InstalledAppFlow.from_client_secrets_file(
                  'credentials.json', SCOPES)
              creds = flow.run_local_server(port=0)
          # Save the credentials for the next run
          with open('token.pickle', 'wb') as token:
              pickle.dump(creds, token)

      service = build('gmail', 'v1', credentials=creds)
      print(service)
      # Call the Gmail API
      results = service.users().labels().list(userId='me').execute()
      labels = results.get('labels', [])
      print(labels)
      if not labels:
          print('No labels found.')
          status=False

      user_id='me'
      label_ids =["INBOX"]
      
      return service,user_id,label_ids,status


  def fetch_messege_and_save_in_db(self, service:object, user_id:int, msg_id:int, count:int) -> dict:
    """Get a Message with given ID.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      msg_id: The ID of the Message required.

    Returns:
      A Message.
    """
    label_tags=['From','Date','Subject','To']
    try:
      message = service.users().messages().get(userId=user_id, id=msg_id).execute()
      row_info=[]

      for i in message['payload']['headers']:
            
            if i["name"] in label_tags:
              if i["name"] == "Date":
                    Date = parse(i["value"])
              elif i["name"] == "From":
                  From = i["value"]
              elif i["name"] == "Subject":
                  Subject = i["value"]
              elif i["name"] == "To":
                  To = i["value"]

      row_info.extend((From, Date, Subject, To, msg_id,count))

      DatabaseService().insert_data(tuple(row_info))
      return message

    except errors.HttpError as error:
      print ('An error occurred: %s' % error)


  def modify_email(self, service: object, user_id: int, msg_id: int, msg_labels: List) -> dict:
    """Modify the Labels on the given Message.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      msg_id: The id of the message required.
      msg_labels: The change in labels.

    Returns:
      Modified message, containing updated labelIds, id and threadId.
    """
    try:
      message = service.users().messages().modify(userId=user_id, id=msg_id,body={"addLabelIds": msg_labels}).execute()

      label_ids = message['labelIds']

      print(f'Message ID: {msg_id} - With Label IDs {label_ids}')
      return message
    except errors.HttpError as error:
      print(f'An error occurred: {error}')

  def main(self) -> None:

    service,user_id,label_ids,status=self.initialize_gmail_credentials()
    if status:
        all_email_ids= self.list_messages_with_labels(service,user_id,label_ids)
        DatabaseService().drop_table()
        DatabaseService().create_table()

        print("Building the email Databse")
        print("")
        print("-"*98)
        for count in tqdm(range(20)):
          self.fetch_messege_and_save_in_db(service=service, user_id=user_id, msg_id=all_email_ids[count],count=count)

        print("-"*98)
        print("")
        print("Latest 20 emails has been feteched from GMAIL !!!!!")



if __name__ == '__main__':
    GmailService().main()