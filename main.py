'''
################################################################################

HIT137 - Assignment 3

################################################################################
'''

import cv2, os, time, sys, random
import tkinter as tk
import tkinter.filedialog as fd
from PIL import Image, ImageTk


######################
db = 0 # DEBUG ONLY  #
######################

# Choose a random HARDCODED image file
def select_image():
    return str(  random.choice( ["test1.png", "test2.png", "test3.png", "test4.png", "test5.png"] )   )

# Allows OpenCV to pass images to tKinter
def to_tk_image(cv_img):
    rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)
    return ImageTk.PhotoImage(pil_img)

# Handle loading and storing the image and the modified image.
class GameImage:

    """
    Handles reading an image file. 
    Collects information about the image(height width) and about the users screen resolution.
    Scales image (if required) while maintaining aspect ratio.
    Generates a list of 5 difference objects.
    """

    # Image variables
    def __init__(self):
        self.image = None
        self.modified = None
        self.height = None
        self.width = None
        self.screen_width = 1920
        self.screen_height = 1080
        self.differences = []
    
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

            # Debug information
            if db:
                print(f"File '{path}' loaded. width:{self.width} height:{self.height}")

            # Check image size, scale if required.
            self.check_dimensions()

            # Make a copy of the scaled image for visual modifications
            self.modified = self.image.copy()


        except Exception as errormsg:
            print("Error:", errormsg)
    
        # Generate the difference list
        self.generate_differences()

    # Creates a list of valid difference objects
    def generate_differences(self):

        # Generate a list of 5 regions to apply visual effects to
        while len(self.differences) < 5:

            # Generate a difference region
            new_diff = Difference(self.width, self.height)

            # Check if the new region overlaps any other stored region, and disregard if overlapping
            if new_diff.overlaps_with_existing(self.differences):
                continue
            
            # Non-overlapping regions are added to the differences list.
            self.differences.append(new_diff)

            # Apply a visual effect to the second image
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
    Generates (scaled-with respect to the image size) random width/height values for candidate regions.
    Stores coordinate information for later comparison.
    Checks for region overlap with other all other difference objects.
    Applies visual effect transformations on the 'modified' image.
    """

    # Create variables
    def __init__(self, image_w, image_h):
        self.x = None
        self.y = None
        self.w = None
        self.h = None
        self.found = False
        self.image_w = image_w
        self.image_h = image_h
        self.randomise()

        # Debug information
        if db:
            print(f"Difference created: {self.__dict__}")

    # Create region within specified parameters - Called on object init
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

    # Checks object region doesn't with any other difference object's region
    def overlaps_with_existing(self, diff_list):
        
        # Load the saved valid regions one by one to check against the candidate region
        for diff in diff_list:
                
            if not (
                # If an overlap doesn't exist, then return True
                diff.x + diff.w <= self.x or  self.x + self.w <= diff.x or
                diff.y + diff.h <= self.y or  self.y + self.h <= diff.y
                ):
                    return True
        return False
    
    # Applies a random visual effect onto the modified image
    def apply_effect(self, image_to_modify):
        # Extract the pixels of the selected region from the modified image
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

        # Debug Information - Draw rectangle around transformation area, and show area top/left coordinates.
        if db:
            cv2.rectangle(image_to_modify, (self.x,self.y), (self.x + self.w, self.y+  self.h), (255,50,50) ,1 )
            cv2.putText(image_to_modify, f"{self.x},{self.y}",(self.x + 10, self.y + 10),cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,50,50))

# Controls game state, user interaction functions, scoring, etc.
class Game:

    # Game variables
    def __init__(self, root):
        self.ext_root = root
        self.score = 0
        self.mistakes = 0
        self.game_start_time = time.time()
        self.gameover = False
        self.elapsed = 0
        self.timer_enabled = True

        '''
        Button objects created here instead of GUI class!
        This avoids the situation of two objects that reference on eachother at runtime(when one is created before the other).
        '''
        self.hint_button = tk.Button(gui.score_frame, text="Hint - One use only", font=("Arial", 10), command=self.get_hint)
        self.hint_button.grid(row=0, column=2, sticky="e")
        self.restart_button = tk.Button(gui.bottom_frame, text="Restart", font=("Arial", 12), command=self.restart_game)
        self.restart_button.grid(row=0, column=3)
        self.reveal_button = tk.Button(gui.bottom_frame, text="Reveal All", font=("Arial",12), command=self.reveal_all)
        self.reveal_button.grid(row=0, column=4)
        self.load_button = tk.Button(gui.bottom_frame, text ="Load Image", font=("Arial", 12), command=self.load_new_image)
        self.load_button.grid(row=0, column=5)
        gui.score_frame.pack(fill="x")
        gui.bottom_frame.pack(fill="x")
        
    # Debuging function - Show mouse coordinates on the modified image
    def mouse_movement(self, event):
        offset_x = (event.widget.winfo_width() - image.width) / 2
        offset_y = (event.widget.winfo_height() - image.height) / 2
        x = int(event.x - offset_x)
        y = int(event.y - offset_y)
        gui.mouse_label.config(text=f"Mouse X:{x}  Y:{y}")
        if db:
            gui.mouse_label.grid(row=0, column=2, sticky="w")

    # Call back from 'mouse click' interaction
    def on_click(self, event):
        
        # If the game is over, ignore interaction
        if self.gameover:
            return

        # Get mouse click coordinates from frame grid cell, calculate offset so that mouse coordinates and difference coordinates match.
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

                # Increase score and update text fields
                game.score += 1
                gui.status_label.config(text=f"Got one. Nice Work!")
                gui.found_label.config(text=f"Found {game.score} | Remaining: {5 - game.score}")

                # Find circle centre
                cx = diff.x + diff.w // 2
                cy = diff.y + diff.h // 2

                # Circle size
                radius = max(diff.w, diff.h) // 2

                # Draw red circle on difference
                cv2.circle(image.image, (cx,cy), radius, (0,0,255), 2)
                cv2.circle(image.modified, (cx,cy), radius, (0,0,255), 2)
                break

        # Wrong click: Increase mistake score, update text fields
        if not found and not game.gameover:
            game.mistakes += 1
            cv2.circle(image.modified, (x, y), 5, (0,0,255), 9)
            gui.status_label.config(text=f"Nothing there!")
            gui.mistake_label.config(text=f"Incorrect Guesses: {game.mistakes}/3")
            # Debug information
            if db:
                game.mistakes -= 1

        # Convert updated images
        new_o_image = to_tk_image(image.image)
        gui.label_o.config(image=new_o_image)
        gui.label_o.image = new_o_image
        new_m_image = to_tk_image(image.modified)
        gui.label_m.config(image=new_m_image)
        gui.label_m.image = new_m_image

        # Check for win condition
        if game.score >= 5:
            gui.status_label.config(text=f"Congratulations, you won in {game.elapsed} seconds")
            # Set function to run after 2 seconds
            self.ext_root.after(1000, self.player_wins)      


        # Check for lose condition
        if game.mistakes >= 3:
            self.gameover = True
            self.reveal_all()
            gui.status_label.config(text="GAME OVER!!!")
            # Set function to run after 2 seconds
            self.ext_root.after(3000, self.game_over)  

    # Auto-find a region at the users request
    def get_hint(self):
        """
        check all difference objects untill first instance of found=False.
        change found to true, circle in different color. score++
        """

        # Disable button to enfore 'one use only'
        if not db:
            self.hint_button.config(state="disabled")
    
        # Cycle through difference objects
        for diff in image.differences:

            # Skip already found differences
            if diff.found:
                continue

            # Declare object found
            diff.found = True

            # Increase score and update text fields - required to increment score so the level can actually finish
            game.score += 1
            gui.status_label.config(text=f"Here is a free hint!")
            gui.found_label.config(text=f"Found {game.score} | Remaining: {5 - game.score}")

            # Find circle centre
            cx = diff.x + diff.w // 2
            cy = diff.y + diff.h // 2

            # Circle size
            radius = max(diff.w, diff.h) // 2
            cv2.circle(image.modified, (cx, cy), radius, (0,255,0),2)
            cv2.circle(image.image, (cx, cy), radius, (0,255,0), 2)
            print(f"Score: {self.score}")
            break

        # Convert updated images
        new_o_image = to_tk_image(image.image)
        gui.label_o.config(image=new_o_image)
        gui.label_o.image = new_o_image
        new_m_image = to_tk_image(image.modified)
        gui.label_m.config(image=new_m_image)
        gui.label_m.image = new_m_image

        # Check for win condition
        if game.score >= 5:
            gui.status_label.config(text=f"Congratulations, you won in {game.elapsed} seconds")
            # Set function to run after 2 seconds
            self.ext_root.after(1000, self.player_wins)      

    # Option to visually show all difference regions to the player
    def reveal_all(self):
        for diff in image.differences:
            if not diff.found:
                diff.found = True
                cx = diff.x + diff.w //2
                cy = diff.y + diff.h //2
                radius = max(diff.w, diff.h) //2
                cv2.circle(image.modified, (cx,cy), radius, (255,0,0), 3)
                cv2.circle(image.image, (cx,cy), radius, (255,0,0), 3)
        new_o = to_tk_image(image.image)
        new_m = to_tk_image(image.modified)
        gui.label_o.config(image=new_o)
        gui.label_o.image = new_o
        gui.label_m.config(image=new_m)
        gui.label_m.image = new_m
        self.gameover = True
        self.timer_enabled = False
        gui.status_label.config(text="Differences shown.")

    # Allow player to select image file
    def load_new_image(self):

        # Open file dialogue with constraints on file type
        filepath = fd.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp")])

        if db:
            print(f"User selected file path: {filepath}")
        
        # If file is selected pass the file path to reset game function
        if (filepath != ""):
            self.restart_game(filepath)    

    # Set state to game over
    def game_over(self):
        self.timer_enabled = False
        
        # Cover images
        gui.gameover_label1.grid(row=0, column=0, sticky="nsew")
        gui.gameover_label2.grid(row=0, column=1, sticky="nsew")

    # Set state to 'player wins'
    def player_wins(self):
        self.gameover = True
        self.timer_enabled = False
        
        # Run restart game after 1 second
        self.ext_root.after(1000, self.restart_game)

    # Reset all game variables and reload image
    def restart_game(self, user_file=""):
        
        # Reset timer variables and enable counter
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
        image.differences = []
        if(user_file != ""):
            image.load_image(user_file)
        else:
            image_file = select_image()
            image.load_image(image_file)

        # Resize GUI if required
        window_size = f"{2*image.width + 100}x{image.height + 250}+0+0"
        self.ext_root.maxsize(image.screen_width, image.screen_height)
        self.ext_root.geometry(window_size) # define window size

        # Convert updated images
        new_o = to_tk_image(image.image)
        new_m = to_tk_image(image.modified)

        # Update labels
        gui.label_o.config(image=new_o)
        gui.label_o.image = new_o
        gui.label_m.config(image=new_m)
        gui.label_m.image = new_m

        # Reset text labels
        gui.found_label.config(text=f"Found {self.score} | Remaining: {5 - game.score}")
        gui.mistake_label.config(text="Incorrect Guesses: 0/3")
        gui.timer_label.config(text=f"Elapsed Time: {self.elapsed} Seconds")
        gui.gameover_label1.grid_remove()
        gui.gameover_label2.grid_remove()

        # Re-enable hint button
        self.hint_button.config(state="normal")

# Creates interface components and defines placement
class Tk_GUI:
    '''
    Contains layout information for frames, labels, buttons, images.
    Initiates opening the image file
    '''

    def __init__(self, root):
        self.ext_root = root

        # Get screen resolution information
        image.screen_width = root.winfo_screenwidth()
        image.screen_height = root.winfo_screenheight()

        # Load image
        image_file = select_image()
        image.load_image(image_file)
        
        # Setup window size and parameters
        root.title("Spot The Difference")
        window_size = f"{2*image.width + 100}x{image.height + 250}+0+0"
        root.minsize(700,500) # restrict window sizes
        root.maxsize(image.screen_width, image.screen_height)
        root.geometry(window_size) # define window size

        # Debug Information
        if db:
            print("Root window size:" + window_size)

        # Setup multiple frames so multiple layout managers can be ues
        self.score_frame = tk.Frame(root, borderwidth=5, relief="groove",background="Grey")
        self.top_frame = tk.Frame(root, borderwidth=5, relief="groove",background="Grey")
        self.middle_frame = tk.Frame(root, borderwidth=5, relief="groove", background="Black")
        self.bottom_frame = tk.Frame(root, borderwidth=5, relief="groove", background="Grey")


        # Setup objects on 'score' frame
        self.found_label= tk.Label(self.score_frame, text="Found 0 differences out of 5", font=("Arial",12))
        self.mistake_label = tk.Label(self.score_frame, text="Incorrect Guesses: 0/3", font=("Arial",12))
        self.score_frame.rowconfigure(0, weight=1)
        self.score_frame.columnconfigure(0, weight=1)
        self.score_frame.columnconfigure(1, weight=1)
        self.score_frame.columnconfigure(2, weight=1)
        self.found_label.grid(row=0, column=0, sticky="ew")
        self.mistake_label.grid(row=0, column=1, sticky="ew")
        

        # Setup objects on 'top' frame
        self.original_label= tk.Label(self.top_frame, text="Original Image", font=("Arial",16))
        self.modified_label = tk.Label(self.top_frame, text="Modified Image", font=("Arial",16))
        self.mouse_label = tk.Label(self.top_frame, text="Mouse X:n Y:n", font=("Arial",10)) # Dont pack() or grid() this here - its only for debug mode
        self.top_frame.rowconfigure(0, weight=1)
        self.top_frame.columnconfigure(0, weight=1)
        self.top_frame.columnconfigure(1, weight=1)
        self.top_frame.columnconfigure(2, weight=1)
        self.top_frame.columnconfigure(3, weight=1)
        self.original_label.grid(row=0, column=0, sticky="w")
        self.modified_label.grid(row=0, column=3, sticky="e")


        # Prep images for display
        o_image = to_tk_image(image.image)
        m_image = to_tk_image(image.modified)
        # Create image containers, called labels and assign images to the frame
        self.label_o = tk.Label(self.middle_frame, image=o_image)
        self.label_m = tk.Label(self.middle_frame, image=m_image)

        # Setup objects on 'middle' frame
        self.gameover_label1= tk.Label(self.middle_frame, text="GAME", font=("Arial",72))
        self.gameover_label2= tk.Label(self.middle_frame, text="OVER", font=("Arial",72))
        self.middle_frame.rowconfigure(0, weight=1)
        self.middle_frame.grid_columnconfigure(0, weight=1)
        self.middle_frame.grid_columnconfigure(1, weight=1)
        self.label_o.grid(row=0, column=0, sticky="nsew")
        self.label_m.grid(row=0, column=1, sticky="nsew")
        

        # Setup objects on 'bottom' frame
        self.timer_label= tk.Label(self.bottom_frame, text="Elapsed Time: 0 Seconds", font=("Arial",12))
        self.status_label= tk.Label(self.bottom_frame, text=f"New game begins NOW!", font=("Arial",12))
        self.bottom_frame.rowconfigure(0, weight=1)
        self.bottom_frame.columnconfigure(0, weight=1, )
        self.bottom_frame.columnconfigure(1, weight=1)
        self.bottom_frame.columnconfigure(2, weight=1)
        self.timer_label.grid(row=0, column=0, sticky="w")
        self.status_label.grid(row=0, column=1, sticky="ew")
        

        # Have each frame display the objects defined above
        self.score_frame.pack(fill="x")
        self.top_frame.pack(fill="x")
        self.middle_frame.pack(fill="both", expand=True)
        self.bottom_frame.pack(fill="x")


# Program start/entry point
if __name__ == "__main__":

    
    def calc_elapsed():
        # Couldn't get this into a class because it references both game and gui. So it had to be defined after class initialisation.

        # If timer is enabled then calculate elapsed time, and update the text in the label.
        if (game.timer_enabled):
            game.elapsed = int(time.time() - game.game_start_time)
            gui.timer_label.config(text=f"Elapsed Time: {game.elapsed} Seconds")

        # Set a timed callback to this function
        tk_obj.after(1000, calc_elapsed)

    

    # Initialise a tk window
    tk_obj = tk.Tk()

    # Create class objects for image manipupation, GUI, and game logic
    image = GameImage()
    gui = Tk_GUI(tk_obj)
    game = Game(tk_obj)


    # Start the initial timer callback    
    tk_obj.after(1000, calc_elapsed)
    gui.timer_label.config(text=f"Elapsed Time: {game.elapsed} Seconds")

    # Bind user inputs for mouse movement and button(left click) to functions
    gui.label_m.bind("<Button-1>", game.on_click)
    if db:
        gui.label_m.bind("<Motion>", game.mouse_movement )

    # Update image labels to display images
    new_o_image = to_tk_image(image.image)
    new_m_image = to_tk_image(image.modified)
    gui.label_o.config(image=new_o_image)
    gui.label_m.config(image=new_m_image)

    # Start GUI engine
    tk_obj.mainloop()
    
