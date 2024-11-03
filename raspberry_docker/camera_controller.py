import requests
import configparser
import base64
import json
from picamera2 import Picamera2
from time import sleep
import uuid
import os
import pandas as pd
from PIL import Image


def read_config():
    # Create a ConfigParser object
    config = configparser.ConfigParser()
 
    # Read the configuration file
    try:
        config.read('volume/config.ini')
    except Exception as e:
        print("Error reading config file: ", e)
        print("You need to add a config.ini file in the volume")
        exit()
 
    # Access values from the configuration file
    sleep_time = config.getint('General','sleep_time')
    server_url = config.get('General','server_url')
    
    # Return a dictionary with the retrieved values
    config_values = {
        'sleep_time': sleep_time,
        'server_url': server_url
    }
 
    return config_values
    
def get_uuid():
    device_id = str(uuid.uuid1())
    if not os.path.isfile("volume/uuid.txt"):
        with open("volume/uuid.txt", "w") as file:
            file.write(device_id)
            file.close()
    else:
        with open("volume/uuid.txt", "r") as file:
            device_id = file.read()
            file.close()
    return device_id


if __name__ == '__main__':
    print("Starting script")
    
    # Parse arguments
    print("Reading configuration")
    config_data = read_config()
    sleep_time = config_data['sleep_time']
    server_url = config_data['server_url']
    print("Configuration read")
    
    device_id = get_uuid()
    print("Generated device id: ", device_id)
   
   
    print("Press Ctrl+C to stop the script")
    
    # Configure camera
    picam2 = Picamera2()
    picam2.start()
    # Main loop
    try:
        while True:
            # Take photo
            picam2.capture_file("/volume/image.jpg")
            
            #TODO in testing
            image = Image.open('/volume/image.jpg')
            new_image = image.resize((512, 512))
            new_image.save('/volume/image.jpg')
            
            
            # Send image to server
            with open("/volume/image.jpg", "rb") as f:
                im_bytes = f.read()        
            im_b64 = base64.b64encode(im_bytes).decode("utf8")
            
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
  
            payload = json.dumps({"image": im_b64, "device_id": device_id})
            response = requests.post(f''+server_url+'/objectdetection', data=payload, headers=headers)
            try:
                data = response.json()     
                df = pd.DataFrame(data)   
                df.to_csv(f"/volume/image.csv", index=False)
                print("csv received")                  
            except requests.exceptions.RequestException:
                print(response.text)
            
            sleep(sleep_time)
           
    except KeyboardInterrupt:
        # Stop script
        print("Script stopped by user")
        pass
    
    except Exception as e:
        print("An error occurred: ", e)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        errormessage = requests.post(f''+server_url+'/error', data=json.dumps({"device_id": device_id, "error": str(e)}), headers=headers)
        pass
    