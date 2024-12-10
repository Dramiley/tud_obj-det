import numpy as np
import argparse
import os
import tensorflow as tf
from PIL import Image # Pillow
from io import BytesIO
import glob
import time
import requests
import pandas as pd
import matplotlib.pyplot as plt

#os.chdir( 'D:\\projects\\data core\\helmet detection\\models\\research\\object_detection' )

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util



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
    # The model expects a batch of images, so add an axis with `tf.newaxis`.
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
    
    # Safe image to server
    vis_util.visualize_boxes_and_labels_on_image_array(
                image,
                output_dict['detection_boxes'],
                output_dict['detection_classes'],
                output_dict['detection_scores'],
                category_index,
                instance_masks=output_dict.get('detection_masks_reframed', None),
                use_normalized_coordinates=True,
                line_thickness=8)
    """The existing plt lines do not work on local pc as they are not setup for GUI
    Use plt.savefig() to save the results instead and view them in a folder"""
    plt.imshow(image)
    plt.savefig(f"{path}_boxes.png") 
    print(f"Saved {path}_boxes.png")

    # Save sorted output to csv
    df = output_to_csv(output_dict)
    df.to_csv(f'{path}.csv')
    print(f"Saved {path}.csv")
    
    # Generate blank image with boxes
    os.system("python generate_box_image.py -tc blue -bc red -r True")
    

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
        csv_paths = []
        for file_extension in ('*.png','*.jpg'):
            image_paths.extend(glob.glob(os.path.join(image_path, file_extension)))
        # Load existing csv files
        for file_extension in ('*.csv'):
            csv_paths.extend(glob.glob(os.path.join(image_path, file_extension)))
        
        if image_paths == []:
            print("No images found")
        
        else:
            for i_path in image_paths: 
                # Check if csv file exists or image has been modified since last detection AND is not a detection image
                if (not '_boxes.png' in i_path) and (not '_out.png' in i_path) and ((not f"{i_path}.csv" in csv_paths) or (os.path.getmtime(i_path) > os.path.getmtime(f"{i_path}.csv"))):
                    image_np = load_image_into_numpy_array(i_path)
                    # Actual detection
                    output_dict = run_inference_for_single_image(model, image_np, i_path)


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='Detect objects inside image')
    parser.add_argument('-m', '--model', type=str, required=True, help='Model Path')
    parser.add_argument('-l', '--labelmap', type=str, required=True, help='Path to Labelmap')
    parser.add_argument('-i', '--image_path', type=str, required=True, help='Path to image (or folder)')
    args = parser.parse_args()
    
    # Load environment variables
    sleep_time_raw = os.getenv("Sleep_Time")
    
    # Verify sleep time
    if sleep_time_raw is None or sleep_time_raw == "":
        sleep_time = 1
    else:
        try:
            sleep_time = int(sleep_time_raw)
        except ValueError:
            sleep_time = 1
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