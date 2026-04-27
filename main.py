import cv2, os, time, sys
import tkinter as tk

db = 1 # debug info

# Handle loading and storing the image and the modified image.
class GameImage:

    def __init__(self):
        self.image = None
        self.modified = None
        self.height = None
        self.width = None

    def load_image(self, filename):
        try:
            # Build the full file path and read and store the image
            path = os.path.join(os.path.dirname(__file__), filename)
            self.image = cv2.imread(path)
            
            # Make sure something was read into image variable
            if self.image is None:
                print("Error: Failed to load image")
                sys.exit()

            # Get image metrics, and create an image copy we can modify
            self.height, self.width, _ = self.image.shape
            self.modified = self.image.copy()

            if db:
                print(f"File '{path}' loaded. width:{self.width} height:{self.height}")

        except Exception as errormsg:
            print("Error:", errormsg)

        

# Represent a hidden difference region, and detects if it's been clicked.
class Difference:
    pass

# Controls game state, user interaction, scoring, etc.
class Game:
    pass


if __name__ == "__main__":
    image = GameImage()
    image.load_image("test.png")