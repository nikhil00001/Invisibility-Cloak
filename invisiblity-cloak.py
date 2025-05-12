import cv2
import numpy as np
import time

# Dictionary mapping color names to HSV ranges
COLOR_RANGES = {
    "red": ([0, 120, 70], [10, 255, 255]),   # Red has two ranges (handled later)
    "blue": ([90, 50, 50], [130, 255, 255]),
    "green": ([35, 50, 50], [85, 255, 255]),
    "yellow": ([20, 100, 100], [40, 255, 255]),
    "purple": ([130, 50, 50], [160, 255, 255]),
    "orange": ([10, 100, 100], [25, 255, 255])
}

# Function to let user pick color
def get_user_color():
    while True:
        color_name = input("Pick a color for your cloak (red, blue, green, yellow, purple, orange): ").lower()
        if color_name in COLOR_RANGES:
            return np.array(COLOR_RANGES[color_name][0]), np.array(COLOR_RANGES[color_name][1])
        print("Invalid color! Please choose from the given options.")

# Capture background
def create_background(cap, num_frames=30):
    print("Capturing background. Please move out of frame.")
    backgrounds = []
    for i in range(num_frames):
        ret, frame = cap.read()
        if ret:
            backgrounds.append(frame)
        else:
            print(f"Warning: Could not read frame {i+1}/{num_frames}")
        time.sleep(0.1)
    if backgrounds:
        return np.median(backgrounds, axis=0).astype(np.uint8)
    else:
        raise ValueError("Could not capture any frames for background")

# Create mask for the selected color
def create_mask(frame, lower_color, upper_color):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_color, upper_color)

    # Handle RED separately because it appears in two HSV regions
    if np.all(lower_color == np.array([0, 120, 70])):  # If red was chosen
        mask2 = cv2.inRange(hsv, np.array([170, 120, 70]), np.array([180, 255, 255]))
        mask = mask + mask2  # Combine both masks for red

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, np.ones((3, 3), np.uint8), iterations=1)
    return mask

# Apply invisibility effect
def apply_cloak_effect(frame, mask, background):
    mask_inv = cv2.bitwise_not(mask)
    fg = cv2.bitwise_and(frame, frame, mask=mask_inv)
    bg = cv2.bitwise_and(background, background, mask=mask)
    return cv2.add(fg, bg)

# Main function
def main():
    print("OpenCV version:", cv2.__version__)

    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    lower_color, upper_color = get_user_color()  # Get user's color choice

    try:
        background = create_background(cap)
    except ValueError as e:
        print(f"Error: {e}")
        cap.release()
        return

    ##print(f"Hold something {color_name}")
    print("Starting main loop. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            time.sleep(1)
            continue

        mask = create_mask(frame, lower_color, upper_color)
        result = apply_cloak_effect(frame, mask, background)

        cv2.imshow('Invisible Cloak', result)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
