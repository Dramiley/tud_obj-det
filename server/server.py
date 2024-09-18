import io
import json                    
import base64                  
import logging             
import numpy as np
from PIL import Image

from flask import Flask, request, jsonify, abort

app = Flask(__name__)         
app.logger.setLevel(logging.DEBUG)
  
  
@app.route("/objectdetection", methods=['POST'])
def safe_image():         
    # print(request.json)      
    if not request.json or 'image' not in request.json: 
        abort(400)
             
    # get the base64 encoded string
    im_b64 = request.json['image']

    # convert it into bytes  
    img_bytes = base64.b64decode(im_b64.encode('utf-8'))

    # convert bytes data to PIL Image object
    img = Image.open(io.BytesIO(img_bytes))

    # save the image
    img.save('input/image.jpg')    

    result_dict = {'result': 'success'}
    return result_dict
 
def run_server_api():
    app.run(host='0.0.0.0', port=8080)
  
  
if __name__ == "__main__":     
    run_server_api()