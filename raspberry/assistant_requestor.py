import os
import pandas as pd
import requests
import json

class assistantRequestor:
    def __init__(self, device_id, server_url):
        self.device_id = device_id
        self.server_url = server_url


    def request_assistant(self):
        while True:
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            response = requests.get(f''+self.server_url+'/assistent', headers=headers)
            
            try:
                data = response.json()     
                df = pd.DataFrame(data)   
                df.to_csv(f"boxed.csv", index=False)
                print("csv received")    
                
            except requests.exceptions.RequestException:
                    print(response.text)
