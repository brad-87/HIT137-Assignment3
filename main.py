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
            
            # Make sure something was read into the image variable
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
    
    

        # List of different objects
        self.differences = []

        # Generate a list of 5 regions to apply visual effects to
        while len(self.differences) < 5:
            # Generate a difference region
            new_diff = Difference(self.width, self.height)

            # Check if the new region overlaps any other stored region, and disregard if overlapping
            if self.overlaps_with_existing(new_diff):
                continue
            
            # Non-overlapping regions are added to the differences list.
            self.differences.append(new_diff)
        
        # Make the image modifications
        for diff in self.differences:

            # Extract the selected region from the modified image
            # ROI = Region Of Interest
            roi = self.modified[
                diff.y : diff.y + diff.h,
                diff.x : diff.x + diff.w
            ]

            # Randomly choose one of three visual effects
            choice = random.choice(["colour", "blur", "brightness"])

            # ---------------------------
            # EFFECT 1: COLOUR SHIFT
            # ---------------------------
            if choice == "colour":

                # Convert image region from BGR to HSV colour space
                hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

                # Slightly shift hue values to change colours subtly
                hsv[:, :, 0] = (hsv[:, :, 0] + 10) % 180

                # Convert back to BGR colour format
                roi = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

            # ---------------------------
            # EFFECT 2: BLUR
            # ---------------------------
            elif choice == "blur":

                # Apply Gaussian blur to soften the selected region
                roi = cv2.GaussianBlur(roi, (9, 9), 0)

            # ---------------------------
            # EFFECT 3: BRIGHTNESS CHANGE
            # ---------------------------
            elif choice == "brightness":

                # Increase brightness slightly
                roi = cv2.convertScaleAbs(roi, alpha=1, beta=25)

            # Place the modified region back into the image
            self.modified[
                diff.y : diff.y + diff.h,
                diff.x : diff.x + diff.w
            ] = roi

            # Print debug information showing where changes were made
            if db:
                print(f"Modifying Image. X:{diff.x} Y:{diff.y}, W:{diff.w} H:{diff.h}")

    
    # Compare the newly generated candidate region for any overlap with existing regions
    def overlaps_with_existing(self, candidate):
        
        # Load the saved valid regions one by one to check against the candidate region
        for diff in self.differences:
                
                if not (
                    # If an overlap doesn't exist, then return True, else return False
                    diff.x + diff.w <= candidate.x or  candidate.x + candidate.w <= diff.x or
                    diff.y + diff.h <= candidate.y or  candidate.y + candidate.h <= diff.y
                    ):
                        return True
        return False
    
# Represent a hidden difference region, and detect if it's been clicked.
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
        min_size = int(0.10 * min(self.image_w, self.image_h))
        max_size = int(0.15 * min(self.image_w, self.image_h))

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

    # Create GUI window and give it a title
    root = tk.Tk()
    root.title("Spot the Difference")

    # Convert images
    img1 = to_tk_image(image.image)
    img2 = to_tk_image(image.modified)

    # Create image containers, called labels and assign them to the root window
    label1 = tk.Label(root, image=img1)
    label1.pack(side="left", padx=10, pady=10)

    canvas = tk.Canvas(root, width=image.width, height=image.height)
    canvas.pack(side="right", padx=10, pady=10)

    canvas_img = canvas.create_image(0, 0, anchor="nw", image=img2)

    # Assign labels to their image so garbage collector wont free the memory
    label1.image = img1
    canvas.image = img2

    # Create game object
    game = Game()

    # Store score and mistakes
    game.score = 0
    game.mistakes = 0

    # Detect clicks on the modified image
    def on_click(event):

        # Get mouse click coordinates
        x = event.x
        y = event.y

        found = False

        # Check every hidden difference region
        for diff in image.differences:

            # Skip already found differences
            if diff.found:
                continue

            # Check if click is inside region
            if (
                diff.x <= x <= diff.x + diff.w and
                diff.y <= y <= diff.y + diff.h
            ):

                diff.found = True
                found = True

                # Increase score
                game.score += 1

                # Find circle centre
                cx = diff.x + diff.w // 2
                cy = diff.y + diff.h // 2

                # Circle size
                radius = max(diff.w, diff.h) // 2

                # Draw red circle on both images
                cv2.circle(image.image, (cx, cy), radius, (0,0,255), 3)
                cv2.circle(image.modified, (cx, cy), radius, (0,0,255), 3)

                print(f"Correct! Score: {game.score}")

                break

        # Wrong click
        if not found:
            game.mistakes += 1
            print(f"Wrong click! Mistakes: {game.mistakes}/3")

        # Convert updated images
        new_img1 = to_tk_image(image.image)
        new_img2 = to_tk_image(image.modified)

        # Refresh displayed images
        label1.config(image=new_img1)
        label1.image = new_img1

        canvas.itemconfig(canvas_img, image=new_img2)
        canvas.image = new_img2

        # Win condition
        if game.score == 5:
            print("YOU FOUND ALL DIFFERENCES!")

        # Lose condition
        if game.mistakes >= 3:
            print("GAME OVER")

    canvas.bind("<Button-1>", on_click)

    # Start GUI engine
    root.mainloop()
