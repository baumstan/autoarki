import detect
import boto3
import os
import shutil
import io
from PIL import Image

# get files from bucket
def get_files():
    ACCESS_KEY= os.getenv('ACCESS_KEY')
    ACCESS_SECRET= os.getenv('ACCESS_SECRET')
    bucket = 'autoarki-preprocessed-images'
    client = boto3.client('s3',region_name='us-east-1', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=ACCESS_SECRET)
    response = client.list_objects_v2(Bucket=bucket)
    s3 = boto3.resource('s3',region_name='us-east-1', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=ACCESS_SECRET)
    bucket = s3.Bucket(bucket)
    for i in range(0,len(response['Contents'])):
        file_path = response['Contents'][i]['Key']
        object = bucket.Object(file_path)
        file_stream = io.BytesIO()
        object.download_fileobj(file_stream)
        img = Image.open(file_stream)
        img_name = file_path.split('/')[-1]
        img.save('autoarki_raw_imgs/' + img_name)

# run detection
def run_detection():
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
def send_to_bucket():
    ACCESS_KEY= os.getenv('ACCESS_KEY')
    ACCESS_SECRET= os.getenv('ACCESS_SECRET')
    img_lst = []
    dire = os.listdir('runs/detect/')[-1]
    for file in os.listdir('runs/detect/' + dire):
        s3_client = boto3.client('s3', region_name='us-east-1', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=ACCESS_SECRET)
        bucket = 'autoarki-processed-images'
        key = f'test/{file}'
        s3_client.upload_file(f'runs/detect/{dire}/{file}', bucket, key)
        img = Image.open(f'runs/detect/{dire}/{file}')
        img = img.convert('RGB')
        img_lst.append(img)
    img_lst[0].save(f'runs/detect/{dire}/set.pdf', save_all=True, append_images=img_lst[1:])
    s3_client.upload_file(f'runs/detect/{dire}/set.pdf', bucket, 'test/set.pdf')

# run it
get_files()
run_detection()
send_to_bucket()
