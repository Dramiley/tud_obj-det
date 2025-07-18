# <img width="830" height="100" alt="🖥_Server" src="https://github.com/Dramiley/tud_obj-det/blob/main/server_banner.png" />

## Usage
### Running the server:
1. run the object-detection docker-container with:
```console
server:~$ docker pull ghcr.io/dramiley/object_detection:latest
server:~$ docker run -ti -v <path of inputfolder>:/input ghcr.io/dramiley/object_detection:latest
```
2. run the add_box_instructions.py script
3. run the server.py script

### API description:
#### /objectdetection (POST)
Request-Data: request.json including:
- image as base64 encoded string
- device_id
- can include warnings

Server answers with corresponding csv-file containing the detections 

#### /assistant<device_id> (GET)
- device_id gets passed over the url
- e.g. /assistant?device_id=73er8dasndeu31

Server answers with visualisation instructions inside a csv-file

#### /error (POST)
Request-Data: request.json including:
- error as string
- device_id

Server answers with a confirmation

#### /started<device_id> (GET)
- device_id gets passed over the url
- e.g. /started?device_id=73er8dasndeu31

Server answers with the chosen mode (1 for object-detection, 2 for camera position calibration)
