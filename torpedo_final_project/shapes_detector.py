import cv2 
import numpy as np 

def shape_detector(frame):
    gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gaussian_img = cv2.GaussianBlur(gray_img, (7, 7), 0)
    canny = cv2.Canny(gaussian_img, 50, 150)
    
    # Morphological operations
    kernel = np.ones((5, 5), np.uint8)
    closed = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel)
    
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    filtered_contours = []
    detected_boxes = []
    detected_shapes = []
    detected_colors = []
    min_area = 300  # Adjust this based on the smallest shapes you want to detect

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_area:
            shape = detect_shape(contour)
            if shape in ["triangle", "square", "circle"]:
                bounding_box = cv2.boundingRect(contour)
                
                is_duplicate = False
                for detected_box in detected_boxes:
                    if boxes_overlap(bounding_box, detected_box):
                        is_duplicate = True
                        break

                if not is_duplicate:
                    filtered_contours.append(contour)
                    detected_boxes.append(bounding_box)

                    color = detect_color_inside_shape(frame, contour)
                    detected_shapes.append(shape)
                    detected_colors.append(color)

    # Draw contours
    for contour, shape in zip(filtered_contours, detected_shapes):
        contour_color = (0, 0, 255) if shape == "triangle" else (0, 255, 0) if shape == "square" else (255, 0, 0)
        cv2.drawContours(frame, [contour], -1, contour_color, 3)
    
    return frame, len(filtered_contours), detected_shapes, detected_colors

def detect_shape(contour):
    # Adjust epsilon (approximation accuracy) for better detection
    epsilon = 0.02 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    
    if len(approx) == 3:
        return "triangle"
    elif len(approx) == 4:
        (x, y, w, h) = cv2.boundingRect(approx)
        aspect_ratio = float(w) / h
        if 0.95 <= aspect_ratio <= 1.05:
            return "square"
        else:
            return "rectangle"
    elif len(approx) > 4:
        return "circle"
    return "unknown"

def detect_color_inside_shape(frame, contour):
    # Mask the shape and use HSV for color detection
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, thickness=cv2.FILLED)

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mean_color = cv2.mean(hsv_frame, mask=mask)[:3]  # Get HSV values

    return get_color_name(mean_color)

def get_color_name(mean_color):
    h, s, v = mean_color
    
    if s < 50 and v > 200:
        return "White"
    elif v < 50:
        return "Black"
    elif 100 <= h <= 140:
        return "Blue"
    elif 35 <= h <= 85:
        return "Green"
    elif 15 <= h <= 35:
        return "Yellow"
    elif 0 <= h <= 15 or 160 <= h <= 180:
        return "Red"
    else:
        return "Unknown"

def boxes_overlap(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    margin = 10
    return not (x1 > x2 + w2 + margin or x1 + w1 + margin < x2 or y1 > y2 + h2 + margin or y1 + h1 + margin < y2)

