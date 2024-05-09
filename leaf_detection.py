# Import libraries
import os
import time

import numpy as np
import matplotlib.pyplot as plt
import cv2

########################################################################################################

# Constants
BLUR_KERNEL_SIZE = (80, 80)

THRESHOLD_AREA = 600000
BINARY_THRESHOLD = 128
MAX_BINARY_VALUE = 255
BINARY_INV_THRESHOLD = 245

MIN_WIDTH = 400
MIN_HEIGHT = 5000

MIN_HEIGHT_FILE = 11000
MAX_HEIGHT_FILE = 22500

########################################################################################################

def leaf_detection(input_image,
                   kernel_size = BLUR_KERNEL_SIZE,
                   bin_threshold = BINARY_THRESHOLD,
                   max_value = MAX_BINARY_VALUE,
                   inv_threshold = BINARY_INV_THRESHOLD,
                   threshold_area = THRESHOLD_AREA,
                   min_width = MIN_WIDTH,
                   min_height = MIN_HEIGHT):

    blurred_image = cv2.blur(input_image, kernel_size)

    _, binarized_image = cv2.threshold(blurred_image, bin_threshold, max_value, cv2.THRESH_BINARY)
    grayscale_image = cv2.cvtColor(binarized_image, cv2.COLOR_BGR2GRAY)
    _, inverted_image = cv2.threshold(grayscale_image, inv_threshold, max_value, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(inverted_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    bounding_boxes = []

    for c in contours:
        area = cv2.contourArea(c)
        if area > threshold_area:
            x, y, w, h = cv2.boundingRect(c)
            if w > min_width and h > min_height:
                bounding_boxes.append([x, y, x+w, y+h])
    
    # Sort the bounding boxes from left to right
    bounding_boxes = sorted(bounding_boxes, key=lambda b: b[0])
    
    return np.array(bounding_boxes)

def is_image_usable(image):
    """
    Checks if the image is usable based on its dimensions.
    
    Args:
    image (numpy.ndarray): Input image to check for usability.
    
    Returns:
    bool: True if the image is usable, False otherwise.
    """

    # Get the height of the image
    height = image.shape[0]
    
    # Check if the height is within the acceptable range
    return MIN_HEIGHT_FILE <= height <= MAX_HEIGHT_FILE


########################################################################################################

# img = cv2.imread('Prototyping/1.jpg')
# bounding_boxes = leaf_detection(img)
# print(bounding_boxes)