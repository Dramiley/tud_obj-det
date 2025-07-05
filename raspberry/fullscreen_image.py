import sys
import os
if sys.version_info[0] == 2:  # the tkinter library changed it's name from Python 2 to 3.
    import Tkinter
    tkinter = Tkinter #I decided to use a library reference to avoid potential naming conflicts with people's programs.
else:
    import tkinter
from PIL import Image, ImageTk
import requests
import json
import pygame
import time

        
class imageFullscreen:
    def __init__(self):
        pygame.display.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen.fill((0, 0, 0))
        
    def updateImage(self, pilImage):
        image = pygame.image.fromstring(pilImage.tobytes(), pilImage.size, pilImage.mode).convert()
        self.screen.blit(image, (0, 0))
        pygame.display.update()

    def close(self):
        pygame.display.quit()
        pygame.quit()
        sys.exit()