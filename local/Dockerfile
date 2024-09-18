FROM python:3.9

COPY . .

RUN cd /models/research && python -m pip install .
RUN pip install numpy
RUN pip install requests
CMD [ "python", "csv_from_image.py", "-m", "./inference_graph/saved_model",  "-l", "label_map.pbtxt", "-i", "./input"]