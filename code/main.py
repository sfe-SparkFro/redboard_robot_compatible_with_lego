# Initialize the board hardware early so it's ready ASAP
# Lego devices take a while to advertsize themselves, happens asynchronously
from board_hardware import *

# Run Red Vision initialization, this will display a splash screen
from rv_init import display, touch_screen

# Import everything else
import os
import time
import cv2 as cv
from ulab import numpy as np

# Dimensions and properties for the UI elements
ui_shape = (240, 320, 3)
ui_cx = ui_shape[1] // 2
ui_cy = ui_shape[0] // 2
button_size = 50
button_cx = button_size // 2
button_cy = button_size // 2
button_spacing = 75
button_shape = (button_size, button_size, 3)
button_color = (255, 255, 255)
arrow_length = 30
arrow_thickness = 5
arrow_tip_length = 0.5
arrow_background_color = (255, 0, 0)
stop_size = 25
stop_background_color = (0, 0, 255)

# Initialize play button image
img_button_play = np.zeros(button_shape, dtype=np.uint8)
img_button_play[:, :] = (0, 255, 0)
points = np.array([
    [button_cx - stop_size // 2, button_cy - stop_size // 2],
    [button_cx + stop_size // 2, button_cy],
    [button_cx - stop_size // 2, button_cy + stop_size // 2]
], dtype=np.int16)
img_button_play = cv.fillPoly(img_button_play, [points], button_color)

# Initialize program selection image
img_pgm = np.zeros(ui_shape, dtype=np.uint8)

# Add header text
_ = cv.putText(img_pgm, "Select Program:", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

# Add program options
programs = os.listdir("programs")
for i, program in enumerate(programs):
    y = 70 + i * 60
    # Write the program name
    _ = cv.putText(img_pgm, program, (65, y+10), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    # Draw the play button next to the program name
    img_pgm[y - button_cy:y + button_cy, 10:10 + button_size] = img_button_play

# Initialize loading image
img_loading = np.zeros(ui_shape, dtype=np.uint8)
_ = cv.putText(img_loading, "Loading...", (ui_cx - 80, ui_cy), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

cv.imshow(display, img_pgm)
while True:
    # Check if there is touch input
    if touch_screen.is_touched():
        # Read touch coordinates
        x, y = touch_screen.get_touch_xy()
        
        # Check if any play button was pressed
        for i, program in enumerate(programs):
            y_program = 70 + i * 60
            if (10 <= x <= 10 + button_size and
                y_program - button_cy <= y <= y_program + button_cy):
                print(f"Selected Program: {program}")
                cv.imshow(display, img_loading)
                # Run the selected program
                f = open(f"programs/{program}", "r")
                exec(f.read())
                f.close()
                cv.imshow(display, img_pgm)
                time.sleep(1)

    if cv.waitKey(1) != -1:
        break
