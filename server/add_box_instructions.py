import numpy as np
import argparse
import os
import PIL
from PIL import Image # Pillow
import glob
import time
import pandas as pd
import matplotlib.pyplot as plt
import random

import PIL.Image as Image
import PIL.ImageColor as ImageColor
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont
import math

# This script generates instructions for the visualization of bounding boxes on images.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add box instructions to images.')
    parser.add_argument('-i','--input_dir', type=str, required=True, help='Directory containing input')
            
    args = parser.parse_args()
            
    input = args.input_dir
    last_modified = 0
    
    if not os.path.exists(input):
        print(f"Input directory {input} does not exist.")
        exit(1)
    try:
        while True:
            for file in os.listdir(input):
                if file.endswith('.jpg') or file.endswith('.png'):
                    continue
                if file.endswith('.csv') and not file.endswith('.boxes.csv'):
                    if os.path.getmtime(os.path.join(input, file)) > last_modified:
                        df = pd.read_csv(os.path.join(input, file))
                        box_color = []
                        blinking = []
                        box_edge = []
                        outline_color = []
                        for class_name in df["class"]:
                            
                            # insert random values,
                            # TODO: implement logic, LLM to generate these values
                            box_color.append(random.choice(["red", "green", "blue", "purple", "orange"]))
                            blinking.append(random.choice([True, False]))
                            box_edge.append(random.choice(["none", "dashed", "dotted", "solid"]))
                            outline_color.append(random.choice(["red", "green", "blue", "purple", "orange"]))
                        
                        df["box color"] = box_color
                        df["blinking"] = blinking
                        df["box edge"] = box_edge
                        df["outline color"] = outline_color
                        df.to_csv(os.path.join(input, file.replace('.csv', '.boxes.csv')), index=False)
                        last_modified = os.path.getmtime(os.path.join(input, file))
                        
            time.sleep(1)
                    
            
            
    except KeyboardInterrupt:
        print("Exiting...")