# <img width="700" height="100" alt="🖥_Server" src="https://github.com/user-attachments/assets/400da72f-0939-45d6-a185-54d1e1e45069" />

## Usage
### API description:
#### /objectdetection (POST)
Request-Data: request.json including:
- image as base64 encoded string
- device_id
- can include warnings

Server answers with corresponding csv-file containing the detections 

#### /assistant<device_id> (GET)
- device_id gets passed over the url\
- e.g. /assistant?device_id=73er8dasndeu31

Server answers with visualisation instructions inside a csv-file

#### /error (POST)
Request-Data: request.json including:
- error as string
- device_id

Server answers with a confirmation

#### /started (POST)
Request-Data: request.json including:
- device_id

Server answers with the chosen mode
