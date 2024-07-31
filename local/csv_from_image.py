import numpy as np
import argparse
import os
import tensorflow as tf
from PIL import Image # Pillow
from io import BytesIO
import glob
import matplotlib.pyplot as plt
import time
import requests

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

import pandas as pd

# patch tf1 into `utils.ops`
utils_ops.tf = tf.compat.v1

# Patch the location of gfile
tf.gfile = tf.io.gfile


def load_model(model_path):
    model = tf.saved_model.load(model_path)
    return model


def load_image_into_numpy_array(path):
    """Load an image from file into a numpy array.

    Puts image into numpy array to feed into tensorflow graph.
    Note that by convention we put it into a numpy array with shape
    (height, width, channels), where channels=3 for RGB.

    Args:
      path: a file path (this can be local or on colossus)

    Returns:
      uint8 numpy array with shape (img_height, img_width, 3)
    """
    img_data = tf.io.gfile.GFile(path, 'rb').read()
    image = Image.open(BytesIO(img_data))
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)


def run_inference_for_single_image(model, image, path):
    # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
    input_tensor = tf.convert_to_tensor(image)
    input_tensor = input_tensor[tf.newaxis, ...]

    # Run inference
    output_dict = model(input_tensor)

    # All outputs are batches tensors.
    # Convert to numpy arrays, and take index [0] to remove the batch dimension.
    # We're only interested in the first num_detections.
    num_detections = int(output_dict.pop('num_detections'))
    output_dict = {key: value[0, :num_detections].numpy()
                   for key, value in output_dict.items()}
    output_dict['num_detections'] = num_detections

    # detection_classes should be ints.
    output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)

    # Handle models with masks:
    if 'detection_masks' in output_dict:
        # Reframe the the bbox mask to the image size.
        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
            output_dict['detection_masks'], output_dict['detection_boxes'],
            image.shape[0], image.shape[1])
        detection_masks_reframed = tf.cast(detection_masks_reframed > 0.5, tf.uint8)
        output_dict['detection_masks_reframed'] = detection_masks_reframed.numpy()

    # Save sorted output to csv
    df = output_to_csv(output_dict)
    df.to_csv(f'{path}.csv')
    print(f"Saved {path}.csv")
    
    # Send csv to server if needed
    if server_needed:
        files = {'file': open(f'{path}.csv', 'rb')}
        x = requests.post(url, files=files)
        print(x.status_code)
        print(x.text)

    return df


def output_to_csv(od):
    
    # Set minimum detection score
    min_score = 0.5
    # Remove unnecessary keys
    remove_keys = ['raw_detection_scores', 'raw_detection_boxes', 'detection_multiclass_scores', 'detection_anchor_indices', 'num_detections']
    for key in remove_keys:
        od.pop(key)
    above_min = 0
    # Count number of detections above min_score
    for score in od['detection_scores']:
        if score >= min_score:
            above_min+=1
        else:
            break
    
    # Remove low score detections, add class names and convert to pixel coordinates
    i = above_min  
    classes, x_min, y_min, x_max, y_max = [], [], [], [], []
    for box in od['detection_boxes']:
        if i == 0:
            break
        # remove * 512 and round for relative coordinates
        # y cords are from top to bottom
        y_min.append(round(box[0] * 512))
        x_min.append(round(box[1] * 512))
        y_max.append(round(box[2] * 512))
        x_max.append(round(box[3] * 512))
        i -= 1
    i = above_min
    for nr in od['detection_classes']:
        if i == 0:
            break
        classes.append(category_index[nr]['name'])
        i-=1
    
    od.pop('detection_boxes')
    od.pop('detection_classes')
    # Create DataFrame for csv
    df = pd.DataFrame(od).head(len(y_max))
    df['class'] = classes
    df['x min'] = x_min
    df['y min'] = y_min
    df['x max'] = x_max
    df['y max '] = y_max
    
    return df
def run_inference(model, category_index, image_path):
    
    # Load images
    if os.path.isdir(image_path):
        image_paths = []
        for file_extension in ('*.png', '*jpg'):
            image_paths.extend(glob.glob(os.path.join(image_path, file_extension)))
        
        if image_paths == []:
            print("No images found")

        """add iterator here"""
        i = 0
        for i_path in image_paths:
            image_np = load_image_into_numpy_array(i_path)
            # Actual detection
            output_dict = run_inference_for_single_image(model, image_np, i_path)


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='Detect objects inside webcam videostream')
    parser.add_argument('-m', '--model', type=str, required=True, help='Model Path')
    parser.add_argument('-l', '--labelmap', type=str, required=True, help='Path to Labelmap')
    parser.add_argument('-i', '--image_path', type=str, required=True, help='Path to image (or folder)')
    args = parser.parse_args()
    
    # Load environment variables
    sleep_time_raw = os.getenv("Sleep_Time")
    server_needed = True
    url = os.getenv("URL")
    
    # Verify if server is needed
    if url is None or url == "":
        server_needed = False
        print("No server URL provided")
    else: print("loaded Server URL: ", url)
    
    # Verify sleep time
    try:
        sleep_time = int(sleep_time_raw)
    except ValueError:
        sleep_time = 5
    print(f"Sleep time set to {sleep_time} ")

    # Load model
    print("loading model")
    detection_model = load_model(args.model)
    
    # Load labelmap
    print("loading labelmap")
    category_index = label_map_util.create_category_index_from_labelmap(args.labelmap, use_display_name=True)
    
    print("running inference")
    print("Press Ctrl+C to stop the script")
    
    # Main loop
    try:
        while True:
            
            # Run inference
            run_inference(detection_model, category_index, args.image_path)
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        # Stop script
        print("Script stopped by user")
        pass
    

# Command to start script
#  python csv_from_image.py -m .\saved_model -l .\label_map.pbtxt -i .\test_images