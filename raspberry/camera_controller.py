import requests
import configparser
import base64
import json
from picamera2 import Picamera2
from time import sleep
import uuid
import os
import pandas as pd
import sys
if sys.version_info[0] == 2:  # the tkinter library changed it's name from Python 2 to 3.
    import Tkinter
    tkinter = Tkinter #I decided to use a library reference to avoid potential naming conflicts with people's programs.
else:
    import tkinter
from PIL import Image, ImageTk
from fullscreen_image import imageFullscreen
from generate_box_image import boxDrawer

def read_config():
    # Create a ConfigParser object
    config = configparser.ConfigParser()
 
    # Read the configuration file
    try:
        config.read('config.ini')
    except Exception as e:
        print("Error reading config file: ", e)
        print("You need to add a config.ini file in the volume")
        exit()
 
    # Access values from the configuration file
    sleep_time = config.getint('General','sleep_time')
    server_url = config.get('General','server_url')
    box_color = config.get('General','box_color')
    text_color = config.get('General','text_color')
    resize = config.getboolean('General','resize')
    
    # Return a dictionary with the retrieved values
    config_values = {
        'sleep_time': sleep_time,
        'server_url': server_url,
        'box_color': box_color,
        'text_color': text_color,
        'resize': resize
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
    box_color = config_data['box_color']
    text_color = config_data['text_color']
    resize = config_data['resize']
    print("Configuration read")
    
    device_id = get_uuid()
    print("Generated device id: ", device_id)
   
   
    print("Press Ctrl+C to stop the script")
    
    # Configure camera
    picam2 = Picamera2()
    pic_config = picam2.create_still_configuration({"size": (3280, 2464)})
    picam2.configure(pic_config)
    picam2.start()
    # Create box_drawer object
    box_drawer = boxDrawer(device_id, server_url, box_color, text_color, resize)
    # Set last csv time
    box_drawer.check_new_csv()
    
    # Create fullscreen image object
    image_Fullscreen = imageFullscreen()
    
    try:
        while True:
            # Take photo
            picam2.capture_file("image.jpg")
            
            #TODO in testing
            image = Image.open('image.jpg')
            new_image = image.resize((512, 512))
            new_image.save('image.jpg')
            
            
            # Send image to server
            with open("image.jpg", "rb") as f:
                im_bytes = f.read()        
            im_b64 = base64.b64encode(im_bytes).decode("utf8")
            
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
  
            payload = json.dumps({"image": im_b64, "device_id": device_id})
            
            # recieve respond and csv
            response = requests.post(f''+server_url+'/objectdetection', data=payload, headers=headers)
            try:
                data = response.json()     
                df = pd.DataFrame(data)   
                df.to_csv(f"image.csv", index=False)
                print("csv received")                  
            except requests.exceptions.RequestException:
                print(response.text)
            
            if box_drawer.check_new_csv():
                box_drawer.run('image.csv')
                image_Fullscreen.updateImage(Image.open('image.csv_out.png'))
            
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
    