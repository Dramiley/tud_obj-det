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

class DashedImageDraw(ImageDraw.ImageDraw):

    def thick_line(self, xy, direction, fill=None, width=0):
        #xy – Sequence of 2-tuples like [(x, y), (x, y), ...]
        #direction – Sequence of 2-tuples like [(x, y), (x, y), ...]
        if xy[0] != xy[1]:
            self.line(xy, fill = fill, width = width)
        else:
            x1, y1 = xy[0]            
            dx1, dy1 = direction[0]
            dx2, dy2 = direction[1]
            if dy2 - dy1 < 0:
                x1 -= 1
            if dx2 - dx1 < 0:
                y1 -= 1
            if dy2 - dy1 != 0:
                if dx2 - dx1 != 0:
                    k = - (dx2 - dx1)/(dy2 - dy1)
                    a = 1/math.sqrt(1 + k**2)
                    b = (width*a - 1) /2
                else:
                    k = 0
                    b = (width - 1)/2
                x3 = x1 - math.floor(b)
                y3 = y1 - int(k*b)
                x4 = x1 + math.ceil(b)
                y4 = y1 + int(k*b)
            else:
                x3 = x1
                y3 = y1 - math.floor((width - 1)/2)
                x4 = x1
                y4 = y1 + math.ceil((width - 1)/2)
            self.line([(x3, y3), (x4, y4)], fill = fill, width = 1)
        return   
        
    def dashed_line(self, xy, dash=(2,2), fill=None, width=0):
        #xy – Sequence of 2-tuples like [(x, y), (x, y), ...]
        for i in range(len(xy) - 1):
            x1, y1 = xy[i]
            x2, y2 = xy[i + 1]
            x_length = x2 - x1
            y_length = y2 - y1
            length = math.sqrt(x_length**2 + y_length**2)
            dash_enabled = True
            postion = 0
            while postion <= length:
                for dash_step in dash:
                    if postion > length:
                        break
                    if dash_enabled:
                        start = postion/length
                        end = min((postion + dash_step - 1) / length, 1)
                        self.thick_line([(round(x1 + start*x_length),
                                          round(y1 + start*y_length)),
                                         (round(x1 + end*x_length),
                                          round(y1 + end*y_length))],
                                        xy, fill, width)
                    dash_enabled = not dash_enabled
                    postion += dash_step
        return

    def dashed_rectangle(self, xy, dash=(2,2), outline=None, width=0):
        #xy - Sequence of [(x1, y1), (x2, y2)] where (x1, y1) is top left corner and (x2, y2) is bottom right corner
        x1, y1 = xy[0]
        x2, y2 = xy[1]
        halfwidth1 = math.floor((width - 1)/2)
        halfwidth2 = math.ceil((width - 1)/2)
        min_dash_gap = min(dash[1::2])
        end_change1 = halfwidth1 + min_dash_gap + 1
        end_change2 = halfwidth2 + min_dash_gap + 1
        odd_width_change = (width - 1)%2        
        self.dashed_line([(x1 - halfwidth1, y1), (x2 - end_change1, y1)],
                         dash, outline, width)       
        self.dashed_line([(x2, y1 - halfwidth1), (x2, y2 - end_change1)],
                         dash, outline, width)
        self.dashed_line([(x2 + halfwidth2, y2 + odd_width_change),
                          (x1 + end_change2, y2 + odd_width_change)],
                         dash, outline, width)
        self.dashed_line([(x1 + odd_width_change, y2 + halfwidth2),
                          (x1 + odd_width_change, y1 + end_change2)],
                         dash, outline, width)
        return
        


class boxDrawer:
    def __init__(self, device_id, server_url,box_color, text_color, resize):
        self.device_id = device_id
        self.server_url = server_url
        self.box_color = box_color
        self.text_color = text_color
        self.resize = resize
        self.last_csv = 0
        
# modified function from object_detection.utils.visualization_utils
    def draw_bounding_box(self,image, xmin, xmax, ymin, ymax, thickness, display_str_list):
        box_color = random.choice(["red", "green", "blue", "purple", "orange"])
        box=[xmin, ymin, xmax, ymax]
        draw = ImageDraw.Draw(image)
        im_width, im_height = image.size
        (left, right, top, bottom) = (xmin, xmax, ymin, ymax)
        #draw.line([(left, top), (left, bottom), (right, bottom),
        #(right, top), (left, top)], width=thickness, fill=self.box_color)
        draw.rectangle(box, outline=box_color, width=thickness, fill=box_color)
           
        
    def add_text(self,image, xmin, xmax, ymin, ymax, thickness, display_str_list):
        (left, right, top, bottom) = (xmin, xmax, ymin, ymax)
        try:
            font = ImageFont.truetype('arial.ttf', 18)
        except IOError:
            font = ImageFont.load_default()
        draw = ImageDraw.Draw(image)
        text_bottom = top
        # Reverse list and print from bottom to top.
        for display_str in display_str_list[::-1]:
            #text_width, text_height = font.getsize(display_str)
            (temp1,temp2, text_width,text_height) = font.getbbox(display_str)
            margin = np.ceil(0.05 * text_height)
            check = False
            while check == False:
                (x0,y0,x1,y1) = draw.textbbox([left + margin, (top + bottom) / 2],
                display_str,
                font=font)
                if x0 >= left and x1 + margin <= right:
                    check = True
                else:
                    font = ImageFont.truetype('arial.ttf', font.size - 1)
                    
            draw.text([left + margin, (top + bottom) / 2],
                display_str,
                fill=self.text_color,
                font=font)
            #draw.text(
            #    (left + margin, text_bottom - text_height - margin),
            #    display_str,
            #    fill=self.text_color,
            #    font=font)
            text_bottom -= text_height - 2 * margin
            
            avg_x = (xmin + xmax) / 2
            avg_y = (ymin + ymax) / 2
            size = 2
            
    def add_outlines(self,image, xmin, xmax, ymin, ymax, thickness, display_str_list):
        (left, right, top, bottom) = (xmin, xmax, ymin, ymax)
        box_edge = random.choice(["none", "dashed", "dotted", "solid"])
        outline_color = random.choice(["red", "green", "blue", "purple", "orange"])
        print(f"Box edge style: {box_edge}")   
        if box_edge == "none":
            pass
        else:
            d = DashedImageDraw(image)
            if box_edge == "dashed":
                d.dashed_rectangle([(left, top), (right, bottom)], dash = (5, 3), outline  = outline_color, width = 4)
            elif box_edge == "dotted":
                d.dashed_rectangle([(left, top), (right, bottom)], dash = (1, 1), outline  = outline_color, width = 4)
            elif box_edge == "solid":
                draw = ImageDraw.Draw(image)
                draw.rectangle([(left, top), (right, bottom)], outline= outline_color, width=4, fill=None)
                
    def add_blinking_box(self, image, xmin, xmax, ymin, ymax, thickness, display_str_list):
        (left, right, top, bottom) = (xmin, xmax, ymin, ymax)
        draw = ImageDraw.Draw(image)
        threshold = 0.6  # Adjust this threshold as needed
        if random.uniform(0, 1) >= threshold:
            # Draw a blinking box
            draw.rectangle([(left, top), (right, bottom)], outline=None, width=thickness, fill= "black")
        
            
        
    def check_new_csv(self):
        if os.path.isfile("image.csv"):
            if os.path.getmtime("image.csv") > self.last_csv:
                self.last_csv = os.path.getmtime("image.csv")
                return True
        return False

    def run(self, csv_path):
        image = Image.new('RGB', (512, 512), (0, 0, 0))
        try:
            df = pd.read_csv(csv_path)
            df.columns = ['numbers','detection_scores','class', 'x min', 'y min', 'x max', 'y max']

            classes = df['class']
            det_scores = df['detection_scores']
            x_min = df['x min']
            y_min = df['y min']
            x_max = df['x max']
            y_max = df['y max']

            sizes = []
            for i in range(len(classes)):
                sizes.append((x_max[i] - x_min[i]) * (y_max[i] - y_min[i]))
            
            df['sizes'] = sizes
            
            df = df.sort_values(by='sizes', ascending=False)
            
            for i in range(len(classes)):
                name = classes[i]
            
                self.draw_bounding_box(image, x_min[i], x_max[i], y_min[i], y_max[i], 4, (name,''))
                self.add_outlines(image, x_min[i], x_max[i], y_min[i], y_max[i], 4, (name,''))
            
            for i in range(len(classes)):
                name = classes[i]
                
                self.add_text(image, x_min[i], x_max[i], y_min[i], y_max[i], 4, (name,''))
                
            
               
        except pd.errors.EmptyDataError:
            pass
        
        if self.resize:
            new_image = image.resize((1640, 1232))
            
        new_image.save(f'{csv_path}_out.png')
        
        for i in range(len(classes)):
            self.add_blinking_box(image, x_min[i], x_max[i], y_min[i], y_max[i], 4, (classes[i], ''))
        
        if self.resize:
            new_image = image.resize((1640, 1232))
        
        new_image.save(f'{csv_path}2_out.png')
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate box image from csv file')
    parser.add_argument('--text_color', type=str, default='white', help='Color of the text')
    
    args = parser.parse_args()
    
    drawer = boxDrawer("Test", None, None, args.text_color, True)
    drawer.run('image.csv')