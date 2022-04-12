from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from re import L
import re
import detect
import boto3
import os
import shutil
import io
from PIL import Image


HOST = ""
PORT = 8003

#recent_messages = pandas.read_csv('recent_messages.csv', header=True)

recent_messages = {} # todo: need to export to file and read in each time
recent_message_keys = {}
sent = []

# get files from bucket
def get_files(recent_message_keys):
    print('entering get_files')
    ACCESS_KEY= os.getenv('ACCESS_KEY')
    ACCESS_SECRET= os.getenv('ACCESS_SECRET')
    bucket = 'autoarki-preprocessed-images'
    #client = boto3.client('s3',region_name='us-east-1', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=ACCESS_SECRET)
    s3 = boto3.resource('s3',region_name='us-east-1', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=ACCESS_SECRET)
    bucket = s3.Bucket(bucket)
    #for i in range(0,len(response['Contents'])):
    directory = list(recent_message_keys.keys())[0]
    for file_name in list(recent_message_keys.values())[0]:
        file_path = f'{directory} /{file_name}'
        print(file_path)
        object = bucket.Object(file_path)
        file_stream = io.BytesIO()
        object.download_fileobj(file_stream)
        img = Image.open(file_stream)
        img_name = f'{directory}{file_name}'
        img.save('autoarki_raw_imgs/' + img_name)

# run detection
def run_detection():
    print('entering get_detect')
    weights = 'best.pt' # path to best.pt file
    source = 'autoarki_raw_imgs/' # path to source files
    conf_thres = 0.5 # confidence threshold
    device = 0 # cuda device
    line_thickness = 3 # pixel width of bounding boxes
    hide_labels = False # toggle for label names display
    hide_conf = False # toggle for confidence display
    detect.run(weights=weights,
               source=source,
               conf_thres=conf_thres,
               device = device,
               line_thickness=line_thickness,
               hide_labels=hide_labels,
               hide_conf=hide_conf)

# send to bucket
def send_to_bucket(recent_message_keys):
    print('entering send_to_bucket')
    ACCESS_KEY= os.getenv('ACCESS_KEY')#'AKIATPBXJR6PWVHPLENC' # os.getenv('ACCESS_KEY')
    ACCESS_SECRET= os.getenv('ACCESS_SECRET')#'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' # os.getenv('ACCESS_SECRET')
    img_lst = []
    dire = os.listdir('runs/detect/')[-1]
    key1 = list(recent_message_keys.keys())[0]
    img_lst = []
    for key2 in list(recent_message_keys.values())[0]:
        file_path = f'runs/detect/{dire}/{key1}{key2}'
        print(f'file path: {file_path}')
        key = f'{key1}/ {key2}'
        print(f'key: {key}')
        #for file in os.listdir('runs/detect/' + dire):
        s3_client = boto3.client('s3', region_name='us-east-1', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=ACCESS_SECRET)
        bucket = 'autoarki-processed-images'
        s3_client.upload_file(file_path, bucket, key)
        img = Image.open(file_path)
        img = img.convert('RGB')
        img_lst.append(img)
    img_lst[0].save(f'runs/detect/{dire}/{key1}.pdf', save_all=True, append_images=img_lst[1:])
    s3_client.upload_file(f'runs/detect/{dire}/{key1}.pdf', bucket, f'{key1}/ {key1}.pdf')

def generate_pdf(recent_message_keys):
    pass

def done_yet(recent_messages):
    # determines if all pages have been ingested yet
    print(list(recent_messages.values()))
    if min(list(recent_messages.values())) == 1:
        return False
    else:
        return True 


def remove_files(recent_message_keys):
    directory = list(recent_message_keys.keys())[0]
    for file in list(recent_message_keys.values())[0]:
        raw_path = f'autoarki_raw_imgs/{directory}{file}'
        os.remove(raw_path)
    for subdir in os.listdir('runs/detect'):
        shutil.rmtree(f'runs/detect/{subdir}')

class ModelHandler(BaseHTTPRequestHandler):

    def crop_recents(self):
        # only keep a cache of the most recent 100 messages
        global recent_messages
        if len(recent_messages) > 100:
            recent_messages = recent_messages[-100:]
        else:
            pass

    def in_recents(self, msg_id):
        # checks if we have processed this message already (each msg is deliverd 3 times)
        global recent_messages
        if msg_id in list(recent_messages.keys()):
            return True
        else:
            return False
        
    def do_GET(self):
        print('handled get request')

    def do_POST(self):
        global recent_messages
        global recent_message_keys
        global sent
        msg_type = str(self.headers.get('x-amz-sns-message-type'))
        content_len = int(self.headers.get('Content-Length'))
        if msg_type == "SubscriptionConfirmation":
            # if this is a subscription confirmation
            # print the entire body
            post_body = self.rfile.read(content_len)
            print(post_body)
        elif msg_type == "Notification":
            # If this is a notification message of the correct format, read thee data
            if content_len == 981:
                post_body = json.loads(self.rfile.read(content_len))
                # check if we have processed this message yet
                msg_id = post_body["MessageId"]
                if msg_id in sent:
                    # if we have already sent this message, then we stop execution
                    return
                if self.in_recents(msg_id):
                    # check if we have processed this message yet
                    # if we have, increment the count by 1
                    recent_messages[msg_id] += 1
                else:
                    # if theis is a new message enter this block
                    recent_messages[msg_id] = 1  # message count = 1
                    if "Message" in list(post_body.keys()):
                        # check if there is a message portion to the keys
                        message = json.loads(post_body['Message'])
                        if "key_name" in message.keys():
                            key1, key2 = str(message['key_name']).split('+')
                            if key1 in list(recent_message_keys.keys()):
                                recent_message_keys[key1].append(key2[1:])
                            else:
                                recent_message_keys[key1] = [key2[1:]]
                if done_yet(recent_messages):
                    for message in list(recent_messages.keys()):
                        sent.append(message)
                    print('got all pages!')
                    get_files(recent_message_keys)
                    run_detection()
                    generate_pdf(recent_message_keys)
                    send_to_bucket(recent_message_keys)
                    remove_files(recent_message_keys)
                    recent_message_keys = {}
                else:
                    pass


server = HTTPServer((HOST, PORT), ModelHandler)
print('Server now running...')


server.serve_forever()
server.server_close()
# write out msg id cache to file
print('Server stopped!')
