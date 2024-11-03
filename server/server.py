import io
import json                    
import base64                  
import logging             
import numpy as np
from PIL import Image
from time import sleep
import pandas
import os


from flask import Flask, request, jsonify, abort

app = Flask(__name__)         
app.logger.setLevel(logging.DEBUG)
  
  
@app.route("/objectdetection", methods=['POST'])
def safe_image():         
    # print(request.json)      
    if not request.json or 'image' not in request.json or 'device_id' not in request.json: 
        abort(400)
             
    # get the base64 encoded string
    im_b64 = request.json['image']
    
    # get the device id
    device_id = request.json['device_id']

    # convert it into bytes  
    img_bytes = base64.b64decode(im_b64.encode('utf-8'))

    # convert bytes data to PIL Image object
    img = Image.open(io.BytesIO(img_bytes))

    # save the image
    img.save(f'input/{device_id}.jpg')    

    result_dict = {'result': 'success'}
    
    while not f'{device_id}.jpg.csv' in os.listdir('input') or (os.path.getmtime(f"input/{device_id}.jpg") > os.path.getmtime(f"input/{device_id}.jpg.csv")):
        sleep(1)
    csvFile = pandas.read_csv(f'input/{device_id}.jpg.csv') 
    
    return csvFile.to_json(orient='records')
 
@app.route("/error", methods=['POST'])
def print_error():
    if not request.json or 'error' not in request.json or 'device_id' not in request.json: 
        abort(400)
    error = request.json['error']
    device_id = request.json['device_id']
    
    print(f"Error: {error} for device {device_id}")
    return "Error received"
    
     
def run_server_api():
    app.run(host='0.0.0.0', port=8080)
  
  
if __name__ == "__main__":     
    run_server_api()