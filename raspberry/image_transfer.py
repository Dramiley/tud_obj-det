import requests
import configparser
import base64
import json
from time import sleep

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
    

if __name__ == '__main__':
    print("Starting script")
    
    # Parse arguments
    print("Reading configuration")
    config_data = read_config()
    sleep_time = config_data['sleep_time']
    server_url = config_data['server_url']
    print("Configuration read")
   
    print("Press Ctrl+C to stop the script")
    
    # Main loop
    try:
        while True:
            # Send image to server
            with open("image.jpg", "rb") as f:
                im_bytes = f.read()        
            im_b64 = base64.b64encode(im_bytes).decode("utf8")
            
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
  
            payload = json.dumps({"image": im_b64})
            response = requests.post(server_url, data=payload, headers=headers)
            try:
                data = response.json()     
                print(data)                
            except requests.exceptions.RequestException:
                print(response.text)
            
            sleep(sleep_time)
           
    except KeyboardInterrupt:
        # Stop script
        print("Script stopped by user")
        pass
    