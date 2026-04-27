# Imports
import math
import qwiic_otos
import cv2 as cv
from ulab import numpy as np
from board_hardware import color_sensor
from rv_init import display, touch_screen

# Create and initialize the OTOS
otos = qwiic_otos.QwiicOTOS()
otos.begin()
offset = qwiic_otos.Pose2D(0, 4, 0)
otos.setOffset(offset)
otos.calibrateImu()
otos.resetTracking()

# Initialize the color sensor
color_sensor.begin()
color_sensor.set_mode_hsv()

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

# Initialize reset button image
img_button_reset = np.zeros(button_shape, dtype=np.uint8)
img_button_reset[:, :] = (255, 0, 0)
img_button_reset = cv.ellipse( # Arc
    img_button_reset,
    (button_cx, button_cy),
    (stop_size // 2, stop_size // 2),
    0,
    -90,
    180,
    button_color,
    arrow_thickness
)
arrow_head_length = 10
img_button_reset = cv.arrowedLine( # Arrow head
    img_button_reset,
    (button_cx, button_cy - stop_size // 2),
    (button_cx - arrow_head_length, button_cy - stop_size // 2),
    button_color,
    arrow_thickness,
    tipLength=1
)

# Create images to be displayed
img = np.zeros((240, 320, 3), dtype=np.uint8)

# Create grid of lines to be drawn, with spacing of 8 pixels and size of 10 lines in each direction
# Grid lines are pairs of points to be drawn, for example:
# [[(-80, -80), (-80, 80)],
#  [(-72, -80), (-72, 80)],
# ...]
grid_size = 10
grid_spacing = 8
grid_lines = []
for i in range(-grid_size, grid_size + 1):
    x = i * grid_spacing
    grid_lines.append([(-x, -grid_size*grid_spacing), (-x, grid_size*grid_spacing)])
    grid_lines.append([(-grid_size*grid_spacing, x), (grid_size*grid_spacing, x)])

while True:
    h, s, v = color_sensor.get_hsv()
    print("H: {} S: {} V: {}".format(h, s, v))

    hsv_color = np.array([[[h//2, s//4, v//4]]], dtype=np.uint8)
    bgr_color = cv.cvtColor(hsv_color, cv.COLOR_HSV2BGR)
    b, g, r = bgr_color[0][0]
    print("BGR:", bgr_color[0][0])

    img[:] = bgr_color

    ui_color = (255 - b, 255 - g, 255 - r)

    _ = cv.putText(img, f"R: {r:03}", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, ui_color, 2)
    _ = cv.putText(img, f"G: {g:03}", (10, 60), cv.FONT_HERSHEY_SIMPLEX, 1, ui_color, 2)
    _ = cv.putText(img, f"B: {b:03}", (10, 90), cv.FONT_HERSHEY_SIMPLEX, 1, ui_color, 2)

    pos = otos.getPosition()
    print("OTOS Position - X: {:04.1f} Y: {:04.1f} H: {:05.1f}".format(pos.x, pos.y, pos.h))

    _ = cv.putText(img, f"X: {pos.x:04.1f}", (6, 170), cv.FONT_HERSHEY_SIMPLEX, 1, ui_color, 2)
    _ = cv.putText(img, f"Y: {pos.y:04.1f}", (8, 200), cv.FONT_HERSHEY_SIMPLEX, 1, ui_color, 2)
    _ = cv.putText(img, f" : {pos.h:05.1f}", (10, 230), cv.FONT_HERSHEY_SIMPLEX, 1, ui_color, 2)
    
    # Draw an ellipse and line to make a theta symbol instead of H for heading
    _ = cv.ellipse(img, (17, 222), (7, 13), 0, 0, 360, (255, 255, 255), 2)
    _ = cv.line(img, (10, 222), (24, 222), (255, 255, 255), 2)

    # Draw the grid around the center point, shifted by the position, rotated by the heading angle
    cx, cy = 235, 85
    side_length = 160
    angle = -math.radians(pos.h)
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    # Translate position using standard 2D rotation (heading angle)
    dx = pos.x * cos_angle - pos.y * sin_angle
    dy = pos.x * sin_angle + pos.y * cos_angle
    cx -= int(dx * (side_length//2) / 10)
    cy -= int(-dy * (side_length//2) / 10)
    angle = math.radians(pos.h)
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    for line in grid_lines:
        start = line[0]
        end = line[1]
        # Rotate the line by the heading angle
        rotated_start_x = int(start[0] * cos_angle - start[1] * sin_angle)
        rotated_start_y = int(start[0] * sin_angle + start[1] * cos_angle)
        rotated_end_x = int(end[0] * cos_angle - end[1] * sin_angle)
        rotated_end_y = int(end[0] * sin_angle + end[1] * cos_angle)
        # Translate the line to the center point
        start_x = cx + rotated_start_x
        start_y = cy + rotated_start_y
        end_x = cx + rotated_end_x
        end_y = cy + rotated_end_y
        if start[0] == 0:
            # Draw vertical grid lines in green and horizontal grid lines in red
            line_color = (0, 255, 0) if end[0] == 0 else (255, 0, 0)
            thickness = 2
            _ = cv.arrowedLine(img, (end_x, end_y), (start_x, start_y), line_color, thickness)
        elif start[1] == 0:
            # Draw horizontal grid lines in red
            line_color = (0, 0, 255)
            thickness = 2
            _ = cv.arrowedLine(img, (start_x, start_y), (end_x, end_y), line_color, thickness)
        else:
            line_color = (127, 127, 127)
            thickness = 1
            _ = cv.line(img, (start_x, start_y), (end_x, end_y), line_color, thickness)

    # Draw an arrow indicating the robot location
    cx, cy = 235, 85
    line_length = 20
    angle = math.radians(-90)
    end_x = int(cx + line_length * math.cos(angle))
    end_y = int(cy + line_length * math.sin(angle))
    _ = cv.arrowedLine(img, (cx, cy), (end_x, end_y), ui_color, 2, tipLength=0.3)

    # Draw the stop button in the bottom right corner
    img[
        -button_size:,
        -button_size:
    ] = img_button_stop

    # Draw the reset button left of the stop button
    img[
        -button_size:,
        -2*button_size:-button_size
    ] = img_button_reset

    cv.imshow(display, img)

    # Check if there is touch input
    if touch_screen.is_touched():
        # Read touch coordinates
        x, y = touch_screen.get_touch_xy()
        
        # Check if the stop button was pressed
        if (x >= ui_shape[1] - button_size and
            y >= ui_shape[0] - button_size):
            print("Stop")
            break

        # Check if the reset button was pressed
        if (ui_shape[1] - 2*button_size <= x < ui_shape[1] - button_size and
            y >= ui_shape[0] - button_size):
            print("Reset")
            otos.calibrateImu()
            otos.resetTracking()

    if cv.waitKey(1) != -1:
        break
