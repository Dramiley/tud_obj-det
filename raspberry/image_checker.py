import numpy as np
from PIL import Image
import argparse
import cv2

class ImageChecker:
    def __init__(self, min_brightness, max_brightness, blurry_threshold):
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness
        self.blurry_threshold = blurry_threshold

    def checkBrightness(self, img):
        # Convert image to numpy array
        img_array = np.array(img)
        # Calculate brightness
        brightness = np.mean(img_array)
        # Check if the brightness is in the range
        if brightness < self.min_brightness or brightness > self.max_brightness:
            return False, brightness
        return True, brightness
    
    def checkBlurry(self, img):
        image = np.array(img)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        fm = cv2.Laplacian(gray, cv2.CV_64F).var()
        if fm < self.blurry_threshold:
            return False
        return True
