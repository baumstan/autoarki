from email import header
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from wsgiref.simple_server import WSGIRequestHandler
import detect
import boto3
import os
import shutil
import io
from PIL import Image
#import pandas as pd


HOST = ""
PORT = 8003

#recent_messages = pandas.read_csv('recent_messages.csv', header=True)

recent_messages = [] # need to export to file and read in each time

# get files from bucket
def get_files(key1,key2):
    print('entering get_files')
    ACCESS_KEY= os.getenv('ACCESS_KEY')
    ACCESS_SECRET= os.getenv('ACCESS_SECRET')
    bucket = 'autoarki-preprocessed-images'
    client = boto3.client('s3',region_name='us-east-1', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=ACCESS_SECRET)
    #response = client.list_objects_v2(Bucket=bucket)
    s3 = boto3.resource('s3',region_name='us-east-1', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=ACCESS_SECRET)
    bucket = s3.Bucket(bucket)
    #for i in range(0,len(response['Contents'])):
    file_path = f'{key1} {key2}'
    print(file_path)
    object = bucket.Object(file_path)
    file_stream = io.BytesIO()
    object.download_fileobj(file_stream)
    img = Image.open(file_stream)
    img_name = f'{key1}{key2[1:]}'
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
def send_to_bucket(key1, key2, key):
    print('entering send_to_bucket')
    ACCESS_KEY= os.getenv('ACCESS_KEY')#'AKIATPBXJR6PWVHPLENC' # os.getenv('ACCESS_KEY')
    ACCESS_SECRET= os.getenv('ACCESS_SECRET')#'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' # os.getenv('ACCESS_SECRET')
    img_lst = []
    dire = os.listdir('runs/detect/')[-1]
    file_path = f'runs/detect/{dire}/{key1}{key2[1:]}'
    #for file in os.listdir('runs/detect/' + dire):
    s3_client = boto3.client('s3', region_name='us-east-1', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=ACCESS_SECRET)
    bucket = 'autoarki-processed-images'
    s3_client.upload_file(file_path, bucket, key)
    # img = Image.open(file_path)
    # img = img.convert('RGB')
    # img_lst.append(img)
    # img_lst[0].save(f'runs/detect/{dire}/set.pdf', save_all=True, append_images=img_lst[1:])
    # s3_client.upload_file(f'runs/detect/{dire}/set.pdf', bucket, 'test/set.pdf')

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
        if msg_id in recent_messages:
            return True
        else:
            return False
        
    def do_GET(self):
        print('handled get request')
        api_url = "https://jsonplaceholder.typicode.com/todos/1"
        response = requests.get(api_url)
        response.json()

    def do_POST(self):
        global recent_messages
        msg_type = str(self.headers.get('x-amz-sns-message-type'))
        content_len = int(self.headers.get('Content-Length'))
        if msg_type == "SubscriptionConfirmation":
            post_body = self.rfile.read(content_len)
            print(post_body)
        elif msg_type == "Notification":
            # read data
            if content_len == 981:
                post_body = json.loads(self.rfile.read(content_len))
                # check if we have processed this message yet
                msg_id = post_body["MessageId"]
                if self.in_recents(msg_id):
                    pass
                else:
                    recent_messages.append(msg_id)
                    if "Message" in list(post_body.keys()):
                        message = json.loads(post_body['Message'])
                        if "key_name" in message.keys():
                            key1, key2 = str(message['key_name']).split('+')
                            key = f'{key1} {key2}'
                            get_files(key1,key2)
                            run_detection()
                            send_to_bucket(key1,key2,key)
                            
                    


server = HTTPServer((HOST, PORT), ModelHandler)
print('Server now running...')


server.serve_forever()
server.server_close()
# write out msg id cache to file
print('Server stopped!')
