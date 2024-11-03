import requests
import configparser
import base64
import json
from time import sleep
import uuid
import os
import pandas as pd

def read_config():
    # Create a ConfigParser object
    config = configparser.ConfigParser()
 
    # Read the configuration file
    config.read('config.ini')
 
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
    if not os.path.isfile("uuid.txt"):
        with open("uuid.txt", "w") as file:
            file.write(device_id)
            file.close()
    else:
        with open("uuid.txt", "r") as file:
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
    
    # Main loop
    try:
        while True:
            # Send image to server
            with open("image.jpg", "rb") as f:
                im_bytes = f.read()        
            im_b64 = base64.b64encode(im_bytes).decode("utf8")
            
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
  
            payload = json.dumps({"image": im_b64, "device_id": device_id})
            response = requests.post(f''+server_url+'/objectdetection', data=payload, headers=headers)
            try:
                data = response.json()     
                df = pd.DataFrame(data)   
                df.to_csv(f"image.csv", index=False)
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
        errormessage = requests.post(f''+server_url+'/error', data=json.dumps({"device_id": device_id, "error": str(e)}), headers=headers)
        pass