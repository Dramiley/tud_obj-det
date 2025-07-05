from picamera2 import Picamera2, Preview
from PIL import Image
from time import sleep
from fullscreen_image import imageFullscreen

class CameraAdjuster:
    def __init__(self, resize):
        self.status = True
        self.resize = resize
    def adjust_camera(self):
        # Configure camera
        #picam2 = Picamera2()
        #camera_config = picam2.create_preview_configuration({"size": (3280, 2464)})
        #picam2.configure(camera_config)
        #picam2.start_preview(Preview.QTGL, x=0, y=0, width=1920, height=1080)
        #picam2.start()
        image_Fullscreen = imageFullscreen()
        picam2 = Picamera2()
        camera_config = picam2.create_still_configuration({"size": (3280, 2464)})
        picam2.configure(camera_config)
        picam2.start()
        
        while self.status:
            try:
                picam2.capture_file("image.jpg")
                image = Image.open('image.jpg')
                if self.resize:
                    image = image.resize((1640, 1232))
                else:
                    image = image.resize((512, 512))
                image_Fullscreen.updateImage(image)
            except KeyboardInterrupt:
                self.status = False
                image_Fullscreen.close()
                print("Camera Adjuster stopped by user")
                exit()
            
        #picam2.stop_preview()
        #picam2.stop()
        