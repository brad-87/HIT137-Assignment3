# HIT137 Assignment 3 – Spot the Difference Game

## Overview
This assignment requires the creation of a "Spot the Difference" game.
This program will load an image, generate a modified version with 5 visual differences, and presents both images side-by-side in a GUI.  

Players must spot the differences by clicking on the image.

---

## Features
- Random generation of multiple differences in an image  
- Differences are non-overlapping and vary in type  
- Side-by-side display of original and modified images  
- Interactive click detection  
- Score tracking and mistake handling  

---

## Assignment Requirements (Summary)
This project satisfies the requirements of HIT137 Assignment 3, which include:

- Loading and displaying images correctly  
- Creating a modified version of an image with multiple differences  
- Ensuring differences are randomly positioned and non-overlapping  
- Implementing a GUI to display both images  
- Detecting user clicks and identifying correct/incorrect selections  
- Providing feedback such as score updates and completion detection  

---

## Design Approach
The program is structured using object-oriented principles, separating:

- Image handling and processing  
- Difference generation and storage  
- Game logic (scoring, validation)  
- GUI interaction  

---


## Requirements

# A Python virtual environment is required to run this project.
# Create and activate a virtual environment before installing dependencies.

# Packages
opencv - Modify and process images.
pillow - Makes images usable in Tkinter.

```bash
pip install opencv-python pillow
```

---


## Troubleshooting
### Tkinter not working (Linux)
If you get an error related to Tkinter, install:

```bash
sudo apt install python3-tk
```


