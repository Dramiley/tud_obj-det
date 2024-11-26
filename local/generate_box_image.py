import numpy as np
import argparse
import os
import PIL
from PIL import Image # Pillow
import glob
import time
import pandas as pd
import matplotlib.pyplot as plt

import PIL.Image as Image
import PIL.ImageColor as ImageColor
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont


# modified function from object_detection.utils.visualization_utils
def draw_bounding_box_with_text(image, xmin, xmax, ymin, ymax, box_color, text_color, thickness, display_str_list):
    box=[xmin, xmax, ymin, ymax]
    draw = ImageDraw.Draw(image)
    im_width, im_height = image.size
    (left, right, top, bottom) = (xmin, xmax, ymin, ymax)
    draw.line([(left, top), (left, bottom), (right, bottom),
             (right, top), (left, top)], width=thickness, fill=box_color)
    try:
        font = ImageFont.truetype('arial.ttf', 18)
    except IOError:
        font = ImageFont.load_default()

    text_bottom = top
    # Reverse list and print from bottom to top.
    for display_str in display_str_list[::-1]:
        #text_width, text_height = font.getsize(display_str)
        (temp1,temp2, text_width,text_height) = font.getbbox(display_str)
        margin = np.ceil(0.05 * text_height)
        #draw.rectangle(
        #    [(left, text_bottom - text_height - 2 * margin), (left + text_width,
        #                                                  text_bottom)],
        #    fill=color)
        draw.text(
            (left + margin, text_bottom - text_height - margin),
            display_str,
            fill=text_color,
            font=font)
        text_bottom -= text_height - 2 * margin

if __name__ == '__main__':
    # get all csv files from input folder
    csv_files = glob.glob('input/*.csv')
    
    for csv in csv_files:
        df = pd.read_csv(csv)
        df.columns = ['numbers','detection_scores','class', 'x min', 'y min', 'x max', 'y max']
        
        classes = df['class']
        det_scores = df['detection_scores']
        x_min = df['x min']
        y_min = df['y min']
        x_max = df['x max']
        y_max = df['y max']
        
        image = Image.new('RGB', (512, 512), (0, 0, 0))
        file_name = os.path.basename(csv).removesuffix('.csv')
        
        for i in range(len(classes)):
            name = classes[i]
            
            draw_bounding_box_with_text(image, x_min[i], x_max[i], y_min[i], y_max[i],'red','blue', 4, (name,''))
        
        image.save(f'input/{file_name}_out.png')
        
    
