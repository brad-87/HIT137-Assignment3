import cv2, os, time, sys, random
import tkinter as tk
from PIL import Image, ImageTk


db = 1 # debug info

def to_tk_image(cv_img):
    rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)
    return ImageTk.PhotoImage(pil_img)


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
    
        # List of diference objects
        self.differences = []

        # Generate a list of 5 regions to apply visual effects to
        while len(self.differences) < 5:
        # Generate a difference region
            new_diff = Difference(self.width, self.height)

            # Check if the new region overlaps any other stored region, and disregard if operlapping
            if self.overlaps_with_existing(new_diff):
                continue
            
            # Non overlapping regions are added to the differences list.
            self.differences.append(new_diff)
        
        for diff in self.differences:
            self.modified[
            diff.y : diff.y + diff.h,
            diff.x : diff.x + diff.w
            ]  = (0, 0, 0)

    
    # Comapre newly generated candidate region for any overlapping with existing regions
    def overlaps_with_existing(self, candidate):
        
        # Load the saved valid regions one by one to check against the candidate region
        for diff in self.differences:
                
                if not (
                    # If an overlap doesn't exist then return True, else return False
                    diff.x + diff.w <= candidate.x or  candidate.x + candidate.w <= diff.x or
                    diff.y + diff.h <= candidate.y or  candidate.y + candidate.h <= diff.y
                    ):
                        return True
        return False
    
# Represent a hidden difference region, and detects if it's been clicked.
class Difference:

    def __init__(self, image_w, image_h):
        # Create variables for difference regions
        self.x = None
        self.y = None
        self.w = None
        self.h = None
        self.found = False
        self.image_w = image_w
        self.image_h = image_h
        self.randomise()

        if db:
            print(f"Difference created: {self.__dict__}")

    # Create region within specified parameters
    def randomise(self):
        # Using the smaller dimension of the image, 
        # scale min and max sizes to use in randint to be relative to image size
        min_size = int(0.05 * min(self.image_w, self.image_h))
        max_size = int(0.10 * min(self.image_w, self.image_h))

        # Generate random width and height for region
        min_size = max(5, min_size)
        max_size = max(min_size + 1, max_size)
        self.w = random.randint(min_size, max_size)
        self.h = random.randint(min_size, max_size)
        
        # Generate region x and y coordinate
        self.x = random.randint(0, self.image_w - self.w)
        self.y = random.randint(0, self.image_h - self.h)
    
# Controls game state, user interaction, scoring, etc.
class Game:
    pass


if __name__ == "__main__":
    image = GameImage()
    image.load_image("test.png")

    # Create window
    root = tk.Tk()
    root.title("Spot the Difference")

    # Convert images
    img1 = to_tk_image(image.image)
    img2 = to_tk_image(image.modified)

    # Create labels
    label1 = tk.Label(root, image=img1)
    label1.pack(side="left", padx=10, pady=10)

    label2 = tk.Label(root, image=img2)
    label2.pack(side="right", padx=10, pady=10)

    # IMPORTANT: keep references
    label1.image = img1
    label2.image = img2

    root.mainloop()