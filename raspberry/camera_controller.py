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
from image_checker import ImageChecker
from camera_adjuster import CameraAdjuster
from assistant_requestor import assistantRequestor

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
    check_brightness = config.getboolean('General','check_brightness')
    check_blur = config.getboolean('General','check_blur')
    
    # Return a dictionary with the retrieved values
    config_values = {
        'sleep_time': sleep_time,
        'server_url': server_url,
        'box_color': box_color,
        'text_color': text_color,
        'resize': resize,
        'check_brightness': check_brightness,
        'check_blur': check_blur
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
    text_color = config_data['text_color']
    resize = config_data['resize']
    check_brightness = config_data['check_brightness']
    check_blur = config_data['check_blur']
    print("Configuration read")
    
    device_id = get_uuid()
    print("Generated device id: ", device_id)
   
   
    print("Press Ctrl+C to stop the script")
                    
    print("Waiting for server to start...")
    # recieve respond choice (camera controller or camera adjuster)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    payload = json.dumps({"started": True, "device_id": device_id})
    response = requests.post(f''+server_url+'/started', data=payload, headers=headers)
    choice = response.text
    
    if choice == '1':
        print("Starting Camera Controller...")
        
    elif choice == '2':
        try:
            print("Starting Camera Adjuster...")
            camera_adjuster = CameraAdjuster(resize)
            camera_adjuster.adjust_camera()
            try: 
                while camera_adjuster.status:
                    sleep(10)
            except KeyboardInterrupt:
                camera_adjuster.status = False
                exit()
        except Exception as e:
            print("An error occurred while starting the Camera Adjuster: ", e)
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            errormessage = requests.post(f''+server_url+'/error', data=json.dumps({"device_id": device_id, "error": str(e)}), headers=headers)
            sleep(100)
            
    else:
        print("Invalid choice, starting Camera Controller on default...")
    
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
    
    # Create image checker object, with min and max brightness, may need to be adjusted
    image_checker = ImageChecker(50, 200, 70)
    
    image_Fullscreen.run_loop()
    
    # listen for assistant requests
    assistant_requestor = assistantRequestor(device_id, server_url, text_color, resize)
    assistant_requestor.request_assistant()
    
    
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
                   
            warning = ""
            
            # Nested if statements to only check brightness and blur if the config is set to true
            if check_brightness:
                # Check brightness of image
                cb = image_checker.checkBrightness(new_image)
                if not cb[0]:
                    if cb[1] < 150: 
                        warning = "Image is too dark, reposition the camera! "
                    else:
                        warning = "Image is too bright, reposition the camera! "
            if check_blur:
                if not image_checker.checkBlurry(new_image):
                    warning += "Image is too blurry, don't move the camera!"
        
            payload = json.dumps({"image": im_b64, "device_id": device_id, "warnings": warning})
                    
            # recieve respond and csv
            response = requests.post(f''+server_url+'/objectdetection', data=payload, headers=headers)
            try:
                data = response.json()     
                df = pd.DataFrame(data)   
                df.to_csv(f"image.csv", index=False)
                print("csv received")                  
            except requests.exceptions.RequestException:
                print(response.text)
                    
            # Check if new csv is available, if so, draw the boxes and display the image
            if box_drawer.check_new_csv():
                box_drawer.run('image.csv')
                image_Fullscreen.updateImage(Image.open('image.csv_out.png'))
                #image_Fullscreen.updateImage(Image.open('image.csv_out.png'))
                
            # Sleep after each iteration
            sleep(sleep_time)
           
    except KeyboardInterrupt:
        # Stop script
        print("Script stopped by user")
        image_Fullscreen.close()
        exit()
    
    except Exception as e:
        print("An error occurred: ", e)
        image_Fullscreen.close()
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        errormessage = requests.post(f''+server_url+'/error', data=json.dumps({"device_id": device_id, "error": str(e)}), headers=headers)
        sleep(100)
        exit()
    