from __future__ import print_function
import pickle
import requests
import os.path
import base64
import email
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors
import re
import database
import time
import sys
from tqdm import tqdm
from dateutil.parser import parse 



# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
TAG_RE = re.compile(r'<[^>]+>')
toolbar_width = 40

# setup toolbar
sys.stdout.write("[%s]" % (" " * toolbar_width))
sys.stdout.flush()
sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['



def RemoveTags(text):
    return TAG_RE.sub('', text)

def ListMessagesWithLabels(service, user_id, label_ids=[]):
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
  try:
    response = service.users().messages().list(userId=user_id,
                                               labelIds=label_ids).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id,
                                                 labelIds=label_ids,
                                                 pageToken=page_token).execute()
      messages.extend(response['messages'])

    return [i["id"] for i in messages]
  except errors.HttpError as error:
    print ('An error occurred: ' , error)




def GmailCredential():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    message=""
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

"""Get Message with given ID.
"""

# import base64
# import email
# from apiclient import errors

def GetMessage(service, user_id, msg_id,count):
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
                # print(i["name"]," ",i["value"])
                
                if i["name"] == "Date":
                      row_info.append(parse(i["value"]))
                else:
                      row_info.append(i["value"])
    # row_info[1]=parse(row_info[1])  
    # print(row_info[1])
    # message = service.users().messages().get(userId=user_id, id=msg_id,
    #                                          format='raw').execute()

    # msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

    # html_body = email.message_from_string(msg_str.decode('utf-8'))
    # text = RemoveTags(str(html_body))
    # # print(text)
    # row_info.extend((text,count))

    row_info.extend((msg_id,count))

    database.insert_data(tuple(row_info))
    # print(message)
    return message

  except errors.HttpError as error:
    print ('An error occurred: %s' % error)





def ModifyMessage(service, user_id, msg_id, msg_labels):
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
    message = service.users().messages().modify(userId=user_id, id=msg_id,
                                                body=msg_labels).execute()
    
    label_ids = message['labelIds']

    print ('Message ID: %s - With Label IDs %s' % (msg_id, label_ids))
    return message
  except errors.HttpError as error:
    print ('An error occurred: %s' % error)


def CreateMsgLabels():
  """Create object to update labels.

  Returns:
    A label update object.
  """
  return {'removeLabelIds': [], 'addLabelIds': ['UNREAD', 'INBOX', 'Label_2']}











def main():
    service,user_id,label_ids,status=GmailCredential()
    if status:
        all_email_ids=ListMessagesWithLabels(service,user_id,label_ids)
        msg_id=all_email_ids[0]
        database.drop_table()
        database.create_table()

        print("Building the email Databse")
        print("")
        print("-"*98)
        for count in tqdm(range(500)):
          GetMessage(service, user_id, all_email_ids[count],count)
          # time.sleep(1)
        #   sys.stdout.write("-")
        #   sys.stdout.flush()
        # sys.stdout.write("]\n") # this ends the progress ba

        print("-"*98)
        print("")
        print("Latest 100 emails has been feteched from GMAIL !!!!!")



if __name__ == '__main__':
    main()