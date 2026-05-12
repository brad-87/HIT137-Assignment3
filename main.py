import cv2, os, time, sys, random
import tkinter as tk
from PIL import Image, ImageTk


db = 1 # debug info

image_file = "test_4k+.jpg"
    #test.png
    #test_long.png
    #test_4k+.jpg
    


def to_tk_image(cv_img):
    rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)
    return ImageTk.PhotoImage(pil_img)


# Handle loading and storing the image and the modified image.
class GameImage:

    """
    Handles reading an image file, scaling (if required) image while maintaining aspect ratio and
    generates 5 difference objects
    """

    def __init__(self):
        self.image = None
        self.modified = None
        self.height = None
        self.width = None
        self.screen_width = None
        self.screen_height = None
    
    # Loads image from file, checks scaling requirements, then created 5 difference objects
    def load_image(self, filename):
        try:
            # Build the full file path and read and store the image
            path = os.path.join(os.path.dirname(__file__), filename)
            self.image = cv2.imread(path)
            
            # Make sure something was read into the image variable
            if self.image is None:
                print("Error: Failed to load image")
                sys.exit()

            # Get image metrics
            self.height, self.width, _ = self.image.shape

            if db:
                print(f"File '{path}' loaded. width:{self.width} height:{self.height}")

            # Check image size, scale if required, then create an image copy we can modify
            self.check_dimensions()
            self.modified = self.image.copy()

        except Exception as errormsg:
            print("Error:", errormsg)
    
        # List of different objects
        self.differences = []

        # Generate a list of 5 regions to apply visual effects to
        while len(self.differences) < 5:
            # Generate a difference region
            new_diff = Difference(self.width, self.height)

            # Check if the new region overlaps any other stored region, and disregard if overlapping
            if new_diff.overlaps_with_existing(self.differences):
                continue
            
            # Non-overlapping regions are added to the differences list.
            self.differences.append(new_diff)
            new_diff.apply_effect(self.modified)

    # Function to see if the two images are too large to display on the users screen, and resize if required.
    def check_dimensions(self):
        scaled = False

        # Calculate aspect ratio of loaded image
        aspect_ratio = self.width / self.height

        # If two images side by side exceed width of screen resolution then scale image
        if (2 * (self.width) >= self.screen_width):
            self.image = cv2.resize(self.image,( int(     (0.45)*self.screen_width   ),  int(      (0.45)*self.screen_width / aspect_ratio)      ))
            self.height, self.width = self.image.shape[:2]
            scaled = True

        # If image height exceeds height of screen resolution then scale image
        if (self.height >= self.screen_height):
            self.image = cv2.resize(self.image,(    int(  aspect_ratio * (self.screen_height - 330)   ) ,    int(  self.screen_height - 330  )   ))
            self.height, self.width = self.image.shape[:2]
            scaled = True

        if db and scaled:
            print(f"Image Dimensions scaled to: w-{self.width}  h-{self.height}")

# Represent a hidden difference region, and detect if it's been clicked.
class Difference:
    """
    Responsible for generating scaled random width/height values for candidate regions, checks for region overlap 
    and applies visual effects on the 'modified' image
    """

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
            # Make the image modifications
        # Compare the newly generated candidate region for any overlap with existing regions
    
    # Checks object region doesn't with any other difference object's region
    def overlaps_with_existing(self, diff_list):
        
        # Load the saved valid regions one by one to check against the candidate region
        for diff in diff_list:
                
                if not (
                    # If an overlap doesn't exist, then return True, else return False
                    diff.x + diff.w <= self.x or  self.x + self.w <= diff.x or
                    diff.y + diff.h <= self.y or  self.y + self.h <= diff.y
                    ):
                        return True
        return False
    
    # Applies a random visual effect onto the modified image
    def apply_effect(self, image_to_modify):
        # Extract the selected region from the modified image
        # ROI = Region Of Interest
        roi = image_to_modify[
            self.y : self.y + self.h,
            self.x : self.x + self.w
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
        image_to_modify[
            self.y : self.y + self.h,
            self.x : self.x + self.w
        ] = roi

        # Print debug information showing where changes were made
        if db:
            cv2.rectangle(image_to_modify, (self.x,self.y), (self.x + self.w, self.y+  self.h), (255,50,50) ,1 )
            cv2.putText(image_to_modify, f"{self.x},{self.y}",(self.x + 10, self.y + 10),cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255,50,50))

# Controls game state, user interaction, scoring, etc.
class Game:

    def __init__(self, root):
        self.score = 0
        self.mistakes = 0
        self.game_start_time = time.time()
        self.gameover = False
        self.elapsed = 0
        self.timer_enabled = True

        self.hint_button = tk.Button(gui.score_frame, text="Hint - One use only", font=("Ariel", 10), command=self.get_hint)
        self.hint_button.grid(row=0, column=2, sticky="e")
        self.restart_button = tk.Button(gui.bottom_frame, text="Restart", font=("Ariel", 12), command=self.restart_game)
        self.restart_button.grid(row=0, column=3)
        gui.score_frame.pack(fill="x")
        gui.bottom_frame.pack(fill="x")
        
    def mouse_movement(self, event):
        offset_x = (event.widget.winfo_width() - image.width) / 2
        offset_y = (event.widget.winfo_height() - image.height) / 2

        x = int(event.x - offset_x)
        y = int(event.y - offset_y)
        gui.mouse_label.config(text=f"Mouse X:{x}  Y:{y}")
        if db:
            gui.mouse_label.grid(row=0, column=2, sticky="w")

    def on_click(self, event):

        if self.gameover:
            return

        # Get mouse click coordinates
        offset_x = (event.widget.winfo_width() - image.width) / 2
        offset_y = (event.widget.winfo_height() - image.height) / 2

        x = int(event.x - offset_x)
        y = int(event.y - offset_y)

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
                gui.status_label.config(text=f"Got one. Nice Work!")
                gui.found_label.config(text=f"Found {game.score} differences out of 5")

                # Find circle centre
                cx = diff.x + diff.w // 2
                cy = diff.y + diff.h // 2

                # Circle size
                radius = max(diff.w, diff.h) // 2

                # Draw red circle on both images
                #cv2.circle(image.image, (cx, cy), radius, (0,0,255), 3)
                cv2.circle(image.modified, (cx, cy), radius, (0,0,255), 3)
                break

        # Wrong click
        if not found:
            game.mistakes += 1
            gui.mistake_label.config(text=f"Incorrect: {game.mistakes}/3")
            gui.status_label.config(text=f"Nothing there!")
            gui.mistake_label.config(text=f"Incorrect Guesses: {game.mistakes}/3")
            if db:
                pass
                #game.mistakes -= 1


        # Convert updated images
        new_m_image = to_tk_image(image.modified)
        gui.label_m.config(image=new_m_image)
        gui.label_m.image = new_m_image
        

        # Win condition
        if game.score >= 5:
            self.player_wins()

        # Lose condition
        if game.mistakes >= 3:
            self.game_over()

    def get_hint(self):
        """
        check all difference objects untill first instance of found=False.
        change found to true, circle in different color. score++
        """
        if not db:
            self.hint_button.config(state="disabled")
    
        for diff in image.differences:

            # Skip already found differences
            if diff.found:
                continue

            diff.found = True

            # Increase score
            self.score += 1
            gui.found_label.config(text=f"Found {self.score} differences out of 5")

            # Find circle centre
            cx = diff.x + diff.w // 2
            cy = diff.y + diff.h // 2

            # Circle size
            radius = max(diff.w, diff.h) // 2
            cv2.circle(image.modified, (cx, cy), radius, (0,255,0), 3)
            print(f"Score: {self.score}")
            break
        
        new_m_image = to_tk_image(image.modified)
        gui.label_m.config(image=new_m_image)
        gui.label_m.image = new_m_image

        if(self.mistakes >= 3):
            self.game_over()

        if(self.score >=5):
            self.player_wins()

    def game_over(self):
        gui.status_label.config(text="GAME OVER!!!")
        self.gameover = True
        self.timer_enabled = False

    def player_wins(self):
        gui.status_label.config(text=f"Congratulations, you won in {game.elapsed} seconds")
        self.gameover = True
        self.timer_enabled = False


    def restart_game(self):
        
        self.game_start_time = time.time()
        self.elapsed = 0
        self.timer_enabled = True

        # Reset game state
        self.score = 0
        self.mistakes = 0
        gui.mistake_label.config(text="Incorrect Guesses: 0/3")
        gui.status_label.config(text=f"New game begins NOW!")
        self.gameover = False

        # Reload/regenerate image
        image.load_image(image_file)

        # Convert updated images
        new_o = to_tk_image(image.image)
        new_m = to_tk_image(image.modified)

        # Update labels
        gui.label_o.config(image=new_o)
        gui.label_o.image = new_o
        gui.label_m.config(image=new_m)
        gui.label_m.image = new_m

        # Reset text labels
        gui.found_label.config(text=f"Found {self.score} differences out of 5")
        gui.timer_label.config(text=f"Elapsed Time: {self.elapsed} Seconds")
        
        # Re-enable hint button
        self.hint_button.config(state="normal")

# Creates interface components and defines placement
class Tk_GUI:
    def __init__(self, root):
        self.ext_root = root

        # Get screen resolution information
        image.screen_width = root.winfo_screenwidth()
        image.screen_height = root.winfo_screenheight()

        # Load image
        image.load_image(image_file)
        
        # Setup window size and parameters
        root.title("Spot The Difference")
        window_size = f"{2*image.width + 100}x{image.height + 250}+0+0"
        root.minsize(700,500) # restrict window sizes
        root.maxsize(image.screen_width, image.screen_height)
        root.geometry(window_size) # define window size

        if db:
            print("Root window size:" + window_size)

        
        self.score_frame = tk.Frame(root, borderwidth=5, relief="groove",background="Grey")
        self.top_frame = tk.Frame(root, borderwidth=5, relief="groove",background="Grey")
        self.middle_frame = tk.Frame(root, borderwidth=5, relief="groove", background="Black")
        self.bottom_frame = tk.Frame(root, borderwidth=5, relief="groove", background="Grey")



        self.found_label= tk.Label(self.score_frame, text="Found 0 differences out of 5", font=("Aeial",12))
        self.mistake_label = tk.Label(self.score_frame, text="Incorrect Guesses: 0/3", font=("Aeial",12))
        self.score_frame.rowconfigure(0, weight=1)
        self.score_frame.columnconfigure(0, weight=1)
        self.score_frame.columnconfigure(1, weight=1)
        self.score_frame.columnconfigure(2, weight=1)
        self.found_label.grid(row=0, column=0, sticky="ew")
        self.mistake_label.grid(row=0, column=1, sticky="ew")
        


        self.original_label= tk.Label(self.top_frame, text="Original Image", font=("Aeial",16))
        self.modified_label = tk.Label(self.top_frame, text="Modified Image", font=("Aeial",16))
        self.mouse_label = tk.Label(self.top_frame, text="Modified Image", font=("Aeial",10))
        self.top_frame.rowconfigure(0, weight=1)
        self.top_frame.columnconfigure(0, weight=1)
        self.top_frame.columnconfigure(1, weight=1)
        self.top_frame.columnconfigure(2, weight=1)
        self.top_frame.columnconfigure(3, weight=1)
        self.original_label.grid(row=0, column=0, sticky="w")
        self.modified_label.grid(row=0, column=3, sticky="e")
        self.mouse_label.grid(row=0, column=2, sticky="e")



        # Convert images
        o_image = to_tk_image(image.image)
        m_image = to_tk_image(image.modified)
        # Create image containers, called labels and assign them to the root window
        self.label_o = tk.Label(self.middle_frame, image=o_image)
        self.label_m = tk.Label(self.middle_frame, image=m_image)
        self.middle_frame.rowconfigure(0, weight=1)
        self.middle_frame.grid_columnconfigure(0, weight=1)
        self.middle_frame.grid_columnconfigure(1, weight=1)
        self.label_o.grid(row=0, column=0, sticky="nsew")
        self.label_m.grid(row=0, column=1, sticky="nsew")
        

        
        self.timer_label= tk.Label(self.bottom_frame, text="Elapsed Time: 0 Seconds", font=("Aeial",12))
        self.status_label= tk.Label(self.bottom_frame, text="GameOver/Finished in x:xx time", font=("Aeial",12))
        self.bottom_frame.rowconfigure(0, weight=1)
        self.bottom_frame.columnconfigure(0, weight=1, )
        self.bottom_frame.columnconfigure(1, weight=1)
        self.bottom_frame.columnconfigure(2, weight=1)
        self.timer_label.grid(row=0, column=0, sticky="w")
        self.status_label.grid(row=0, column=1, sticky="ew")
        


        self.score_frame.pack(fill="x")
        self.top_frame.pack(fill="x")
        self.middle_frame.pack(fill="both", expand=True)
        self.bottom_frame.pack(fill="x")


if __name__ == "__main__":

    def calc_elapsed():
        # stuffs me how to make this work in a class.
        if (game.timer_enabled):
            game.elapsed = int(time.time() - game.game_start_time)
            gui.timer_label.config(text=f"Elapsed Time: {game.elapsed} Seconds")
        tk_obj.after(1000, calc_elapsed)



    tk_obj = tk.Tk()

    # Create image and window objects
    image = GameImage()
    gui = Tk_GUI(tk_obj)
    game = Game(tk_obj)
    # Begin game

    
    tk_obj.after(1000, calc_elapsed)
    gui.timer_label.config(text=f"Elapsed Time: {game.elapsed} Seconds")


    gui.label_m.bind("<Button-1>", game.on_click)
    if db:
        gui.label_m.bind("<Motion>", game.mouse_movement )

    # display images
    new_o_image = to_tk_image(image.image)
    new_m_image = to_tk_image(image.modified)
    gui.label_o.config(image=new_o_image)
    gui.label_m.config(image=new_m_image)

    # Start GUI engine
    tk_obj.mainloop()

