import base64
import email
from httplib2 import Http
from bs4 import BeautifulSoup
import csv
from time import strftime, gmtime
import sys
from apiclient import errors


class gmail_func:
    def __init__(self, service, user_id):
        self.service = service
        self.user_id = user_id
    

    def get_email(self, msg_id):
        email_dict = { }

        try:

            message = self.service.users().messages().get(userId = self.user_id, id = msg_id).execute() # fetch the message using API
            payld = message['payload'] # get payload of the message
            headr = payld['headers'] # get header of the payload
            part_data = ''
            data = ''
            for info in headr: # getting the Subject
                if info['name'] == 'Subject':
                    msg_subject = info['value']
                    email_dict['Subject'] = msg_subject
                else:
                    pass
                if info['name'] == 'Date':
                    msg_date = info['value']
                    email_dict['DateTime'] = msg_date
                else:
                    pass
                if info['name'] == 'From':
                    msg_from = info['value']
                    email_dict['MsgFrom'] = msg_from
                else:
                    pass

            # Fetching message body
            def get_body(obj, data):
                
                if obj["mimeType"] == "multipart/mixed" or obj["mimeType"] == "multipart/alternative" or obj["mimeType"] == "multipart/related":
                    for i in obj['parts']:
                        if i["mimeType"] == "multipart/mixed" or i["mimeType"] == "multipart/alternative" or i["mimeType"] == "multipart/related":
                            for x in i['parts']:
                                data += get_body(x, data) or ''
                        elif i["mimeType"] in ("text/plain", "text/html") and i["filename"] == "":
                            try:
                                data += i['body']['data'] or ''
                            except:
                                print('Error msg id:', msg_id)
                elif obj["mimeType"] in ("text/plain", "text/html") and obj["filename"] == "":
                    try:
                        data += obj['body']['data'] or ''
                    except:
                        print('Error msg id:', msg_id)
                else:
                    print(msg_id)
                    return
                return data
                

            part_data = get_body(payld, data)
            clean_one = part_data.replace("-","+") # decoding from Base64 to UTF-8
            clean_one = clean_one.replace("_","/") # decoding from Base64 to UTF-8
            clean_two = base64.urlsafe_b64decode(bytes(clean_one, 'UTF-8')) # decoding from Base64 to UTF-8
            soup = BeautifulSoup(clean_two , 'lxml' )
            message_body = soup.text.strip()
            email_dict['Message_body'] = message_body

        except Exception as e:
            print(e)
            email_dict = None
            pass

        finally:
            return email_dict

    def get_msgids_with_labels(self, label_ids=[]):
        try:
            response = self.service.users().messages().list(userId = self.user_id, labelIds = label_ids).execute()
            
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']

                response = self.service.users().messages().list(userId=self.user_id, labelIds=label_ids, pageToken=page_token).execute()

                messages.extend(response['messages'])
                
                print('... total %d emails on next page [page token: %s], %d listed so far' % (len(response['messages']), page_token, len(messages)))
                sys.stdout.flush()

            return messages

        except errors.HttpError as error:
            print('An error occurred: %s' % error)

    def export_csv(self, msg_id_list):
        #exporting the values as .csv
        rows = 0
        file = 'emails_%s.csv' % (strftime("%Y_%m_%d_%H%M%S", gmtime()))
        with open(file, 'w', encoding='utf-8', newline = '') as csvfile:
            fieldnames = ['MsgFrom','Subject','DateTime','Message_body']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter = ',')
            writer.writeheader()

            for id in msg_id_list:
                email_dict = self.get_email(id)
                if email_dict is not None:
                    writer.writerow(email_dict)
                    rows += 1
                    print(rows)

                if rows > 0 and (rows%50) == 0:
                    print('... total %d read so far' % (rows))
                    sys.stdout.flush()

        print('... emails exported into %s' % (file))
        print("\n... total %d message retrived" % (rows))
        sys.stdout.flush()


        print('... all Done!')