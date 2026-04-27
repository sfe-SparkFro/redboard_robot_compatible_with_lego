# Imports
import time
import cv2 as cv
from ulab import numpy as np
from board_hardware import motor_l, motor_r
from rv_init import display, touch_screen

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

# Initialize arrow button image
img_arrow = np.zeros(button_shape, dtype=np.uint8)
img_arrow[:, :] = arrow_background_color
img_arrow = cv.arrowedLine(
    img_arrow,
    (button_cx, button_cy + arrow_length // 2),
    (button_cx, button_cy - arrow_length // 2),
    button_color,
    arrow_thickness,
    cv.FILLED,
    0,
    arrow_tip_length
)

# Initialize stop button image
img_button_stop = np.zeros(button_shape, dtype=np.uint8)
img_button_stop[:, :] = stop_background_color
img_button_stop = cv.rectangle(
    img_button_stop,
    (button_cx - stop_size // 2, button_cy - stop_size // 2),
    (button_cx + stop_size // 2, button_cy + stop_size // 2),
    button_color,
    cv.FILLED
)

# Initialize UI image
img_ui = np.zeros(ui_shape, dtype=np.uint8)

# Draw the stop button in the center
img_ui[
    ui_cy-button_cy:ui_cy+button_cy,
    ui_cx-button_cx:ui_cx+button_cx
] = img_button_stop

# Draw the forward arrow above the stop button
img_ui[
    ui_cy-button_spacing-button_cy:ui_cy-button_spacing+button_cy,
    ui_cx-button_cx:ui_cx+button_cx
] = img_arrow

# Draw the backward arrow below the stop button
img_ui[
    ui_cy+button_spacing-button_cy:ui_cy+button_spacing+button_cy,
    ui_cx-button_cx:ui_cx+button_cx
] = img_arrow[::-1, :]  # Flip the arrow image vertically

# Draw the left arrow to the left of the stop button
img_ui[
    ui_cy-button_cy:ui_cy+button_cy,
    ui_cx-button_spacing-button_cx:ui_cx-button_spacing+button_cx
] = img_arrow.transpose((1, 0, 2))

# Draw the right arrow to the right of the stop button
img_ui[
    ui_cy-button_cy:ui_cy+button_cy,
    ui_cx+button_spacing-button_cx:ui_cx+button_spacing+button_cx
] = img_arrow.transpose((1, 0, 2))[:, ::-1]  # Flip the arrow image horizontally

# Loop to continuously read touch input and drive around
cv.imshow(display, img_ui)
while True:
    # Check if there is touch input
    if touch_screen.is_touched():
        # Read touch coordinates
        x, y = touch_screen.get_touch_xy()
        
        # Check if the stop button was pressed
        if (ui_cx - button_cx <= x <= ui_cx + button_cx and
            ui_cy - button_cy <= y <= ui_cy + button_cy):
            print("Stop")
            break
        
        # Check if the forward arrow was pressed
        elif (ui_cx - button_cx <= x <= ui_cx + button_cx and
            ui_cy - button_spacing - button_cy <= y <= ui_cy - button_spacing + button_cy):
            print("Forward")
            motor_l.set_speed(1)
            motor_r.set_speed(1)
            time.sleep(0.5)
            motor_l.set_speed(0)
            motor_r.set_speed(0)
        
        # Check if the backward arrow was pressed
        elif (ui_cx - button_cx <= x <= ui_cx + button_cx and
            ui_cy + button_spacing - button_cy <= y <= ui_cy + button_spacing + button_cy):
            print("Backward")
            motor_l.set_speed(-1)
            motor_r.set_speed(-1)
            time.sleep(0.5)
            motor_l.set_speed(0)
            motor_r.set_speed(0)
        
        # Check if the right arrow was pressed
        elif (ui_cy - button_cy <= y <= ui_cy + button_cy and
            ui_cx + button_spacing - button_cx <= x <= ui_cx + button_spacing + button_cx):
            print("Right")
            motor_l.set_speed(1)
            motor_r.set_speed(-1)
            time.sleep(0.5)
            motor_l.set_speed(0)
            motor_r.set_speed(0)
        
        # Check if the left arrow was pressed
        elif (ui_cy - button_cy <= y <= ui_cy + button_cy and
            ui_cx - button_spacing - button_cx <= x <= ui_cx - button_spacing + button_cx):
            print("Left")
            motor_l.set_speed(-1)
            motor_r.set_speed(1)
            time.sleep(0.5)
            motor_l.set_speed(0)
            motor_r.set_speed(0)

    if cv.waitKey(1) != -1:
        break
