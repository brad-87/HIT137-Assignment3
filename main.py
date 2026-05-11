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
        self.screen_width = None
        self.screen_height = None

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
            self.check_dimensions()
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
    

    # Function to see if the two images are too large to display on the users screen, and resize if required.
    def check_dimensions(self):

        if db:
            print(f"Loaded image dimensions: w-{self.width}  h-{self.height}")

        aspect_ratio = self.width / self.height

        if (2 * (self.width) >= self.screen_width):
            self.image = cv2.resize(self.image,( int(     (0.45)*self.screen_width   ),  int(      (0.45)*self.screen_width / aspect_ratio)      ))
            self.height, self.width = self.image.shape[:2]

        if (self.height >= self.screen_height):
            self.image = cv2.resize(self.image,(    int(  aspect_ratio * (self.screen_height - 330)   ) ,    int(  self.screen_height - 330  )   ))
            self.height, self.width = self.image.shape[:2]


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

    root = tk.Tk()

    image.screen_width = root.winfo_screenwidth()
    image.screen_height = root.winfo_screenheight()
    #image.load_image("test.png")
    #image.load_image("test_long.png")
    image.load_image("test_4k+.jpg")
    root.title("Spot The Difference")
    window_size = f"{2*image.width + 100}x{image.height + 250}+0+0"

    if db:
        print("Root window size:" + window_size)

    
    root.minsize(700,500) # restrict window sizes
    root.maxsize(image.screen_width, image.screen_height)
    root.geometry(window_size) # define window size
    
    
    score_frame = tk.Frame(root, borderwidth=5, relief="groove",background="Grey")
    top_frame = tk.Frame(root, borderwidth=5, relief="groove",background="Grey")
    middle_frame = tk.Frame(root, borderwidth=5, relief="groove", background="Black")
    bottom_frame = tk.Frame(root, borderwidth=5, relief="groove", background="Grey")

    original_label= tk.Label(top_frame, text="Original Image", font=("Aeial",16))
    modified_label = tk.Label(top_frame, text="Modified Image", font=("Aeial",16))
    top_frame.rowconfigure(0, weight=1)
    top_frame.columnconfigure(1, weight=1)
    original_label.grid(row=0, column=0, sticky="w")
    modified_label.grid(row=0, column=1, sticky="e")
    

    found_label= tk.Label(score_frame, text="Found x differences out of 5", font=("Aeial",12))
    attempts_label = tk.Label(score_frame, text="Attempts: ", font=("Aeial",12))
    hint_button = tk.Button(score_frame, text="Hint - One use only", font=("Ariel", 10))
    score_frame.rowconfigure(0, weight=1)
    score_frame.columnconfigure(0, weight=1)
    score_frame.columnconfigure(1, weight=1)
    score_frame.columnconfigure(2, weight=1)
    found_label.grid(row=0, column=0, sticky="ew")
    attempts_label.grid(row=0, column=1, sticky="ew")
    hint_button.grid(row=0, column=2, sticky="e")


    # Convert images
    o_image = to_tk_image(image.image)
    m_image = to_tk_image(image.modified)
    # Create image containers, called labels and assign them to the root window
    label_o = tk.Label(middle_frame, image=o_image)
    label_m = tk.Label(middle_frame, image=m_image)

    middle_frame.rowconfigure(0, weight=1)
    middle_frame.grid_columnconfigure(0, weight=1)
    middle_frame.grid_columnconfigure(1, weight=1)
    label_o.grid(row=0, column=0, sticky="nsew")
    label_m.grid(row=0, column=1, sticky="nsew")

    
    timer_label= tk.Label(bottom_frame, text="Elapsed Time: ", font=("Aeial",12))
    status_label= tk.Label(bottom_frame, text="GameOver/Finished in x:xx time", font=("Aeial",12))
    restart_button = tk.Button(bottom_frame, text="Restart", font=("Ariel", 12))
    bottom_frame.rowconfigure(0, weight=1)
    bottom_frame.columnconfigure(0, weight=1, )
    bottom_frame.columnconfigure(1, weight=1)
    bottom_frame.columnconfigure(2, weight=1)
    timer_label.grid(row=0, column=0, sticky="ew")
    status_label.grid(row=0, column=1, sticky="ew")
    restart_button.grid(row=0, column=3)


    score_frame.pack(fill="x")
    top_frame.pack(fill="x")
    middle_frame.pack(fill="both", expand=True)
    bottom_frame.pack(fill="x")
 

# Create game object
    game = Game()

    # Store score and mistakes
    game.score = 0
    game.mistakes = 0
    # GUI score labels
    score_label = tk.Label(root, text=f"Score: {game.score}", font=("Arial", 14))
    score_label.pack()
    mistake_label = tk.Label(root, text=f"Mistakes: {game.mistakes}/3", font=("Arial", 14))
    mistake_label.pack()

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
                score_label.config(text=f"Score: {game.score}")

                # Find circle centre
                cx = diff.x + diff.w // 2
                cy = diff.y + diff.h // 2

                # Circle size
                radius = max(diff.w, diff.h) // 2

                # Draw red circle on both images
                #cv2.circle(image.image, (cx, cy), radius, (0,0,255), 3)
                cv2.circle(image.modified, (cx, cy), radius, (0,0,255), 3)

                print(f"Correct! Score: {game.score}")

                break

        # Wrong click
        if not found:
            game.mistakes += 1
            mistake_label.config(text=f"Mistakes: {game.mistakes}/3")
            print(f"Wrong click! Mistakes: {game.mistakes}/3")

        # Convert updated images
        #new_o_image = to_tk_image(image.image)
        new_m_image = to_tk_image(image.modified)

        #label_o.config(image=new_o_image)
        #label_o.image = new_o_image

        label_m.config(image=new_m_image)
        label_m.image = new_m_image
        


        # Win condition
        if game.score == 5:
            print("YOU FOUND ALL DIFFERENCES!")

        # Lose condition
        if game.mistakes >= 3:
            print("GAME OVER")

    label_m.bind("<Button-1>", on_click)

    # Start GUI engine
    root.mainloop()
