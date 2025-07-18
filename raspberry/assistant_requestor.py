import os
import pandas as pd
import requests
import json
from generate_box_image import boxDrawer

class assistantRequestor:
    def __init__(self, device_id, server_url, text_color, resize):
        self.device_id = device_id
        self.server_url = server_url
        self.text_color = text_color
        self.resize = resize

    def request_assistant(self):
        box_drawer = boxDrawer(self.device_id, self.server_url, self.text_color, self.resize)
        while True:
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            response = requests.get(f''+self.server_url+'/assistent?device_id='+self.device_id, headers=headers)
            
            try:
                data = response.json()     
                df = pd.DataFrame(data)   
                df.to_csv(f"boxed.csv", index=False)
                print("csv received")    
                boxDrawer.run('boxed.csv')
                
            except requests.exceptions.RequestException:
                    print(response.text)
