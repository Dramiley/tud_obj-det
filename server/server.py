import io
import json                    
import base64                  
import logging             
import numpy as np
from PIL import Image
from time import sleep
import pandas
import os
import time


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
    
    # get warnings
    warnings = request.json['warnings']

    # convert it into bytes  
    img_bytes = base64.b64decode(im_b64.encode('utf-8'))

    # convert bytes data to PIL Image object
    img = Image.open(io.BytesIO(img_bytes))

    # save the image
    img.save(f'input/{device_id}.jpg')  
    
    # print the warnings
    if warnings != "":
        print(f"Warning: {warnings} for device {device_id}") 
    
    while not f'{device_id}.jpg.csv' in os.listdir('input') or (os.path.getmtime(f"input/{device_id}.jpg") > os.path.getmtime(f"input/{device_id}.jpg.csv")):
        sleep(1)
    csvFile = pandas.read_csv(f'input/{device_id}.jpg.csv') 
    
    return csvFile.to_json(orient='records')
 
 
@app.route("/assistent/<device_id>", methods=['GET'])
def assistent(device_id):
    connected_time = time.time()
    # run LLM-assistent
    while not f'{device_id}.boxes.csv' in os.listdir('input') or (connected_time >= os.path.getmtime(f"input/{device_id}.boxes.csv")):
        sleep(1)
            
    csvFile = pandas.read_csv(f"input/{device_id}.boxes.csv")
        
    return csvFile.to_json(orient='records')
@app.route("/error", methods=['POST'])
def print_error():
    if not request.json or 'error' not in request.json or 'device_id' not in request.json: 
        abort(400)
    error = request.json['error']
    device_id = request.json['device_id']
    
    print(f"Error: {error} for device {device_id}")
    return "Error received"
   
@app.route("/started", methods=['POST'])
def started():
    if not request.json or 'device_id' not in request.json: 
        abort(400)
    device_id = request.json['device_id']
    
    print(f"Device {device_id} started")
    print("Enter which script you want to run")
    print("1: Camera Controller")
    print("2: Camera Adjuster")
    
    choice = input("Enter the number of your choice: ")
    valid = False
    while not valid:
        if choice == '1':
            print("Starting Camera Controller...")
            valid = True
        elif choice == '2':
            print("Starting Camera Adjuster...")
            valid = True    
        else:
            print("Invalid choice, please try again.")
        
        
    return choice
     
def run_server_api():
    app.run(host='0.0.0.0', port=8081)
  
  
if __name__ == "__main__":     
    run_server_api()
    