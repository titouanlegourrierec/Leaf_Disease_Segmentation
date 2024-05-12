# Import libraries
import os
import time

import numpy as np
import matplotlib.pyplot as plt
import cv2

########################################################################################################
############################           Parameters & Constants              #############################
########################################################################################################

# the size of the kernel for the blurring operation to reduce noise in the image and to enable better leaf detection
BLUR_KERNEL_SIZE = (80, 80)

# the minimum area of a contour to be considered a leaf
THRESHOLD_AREA = 600000

# parameters for the binarization of the image
BINARY_THRESHOLD = 128
MAX_BINARY_VALUE = 255
BINARY_INV_THRESHOLD = 245

# the minimum width and height of a bounding box to be considered a leaf
MIN_WIDTH = 400
MIN_HEIGHT = 5000

# the minimum and maximum height of the input image
MIN_HEIGHT_FILE = 11000
MAX_HEIGHT_FILE = 22500

########################################################################################################
############################                 Main Functions                 #############################
########################################################################################################

def leaf_detection(input_image,
                   kernel_size = BLUR_KERNEL_SIZE,
                   bin_threshold = BINARY_THRESHOLD,
                   max_value = MAX_BINARY_VALUE,
                   inv_threshold = BINARY_INV_THRESHOLD,
                   threshold_area = THRESHOLD_AREA,
                   min_width = MIN_WIDTH,
                   min_height = MIN_HEIGHT) -> np.ndarray :
    """
    Function to detect leaves in an image.

    Parameters:
        - input_image (numpy.ndarray): The input image where leaves are to be detected.
        - kernel_size (tuple): The size of the kernel used for blurring the image.
        - bin_threshold (int): Threshold for binary thresholding.
        - max_value (int): Maximum value used for binary THRESH_BINARY thresholding.
        - inv_threshold (int): Threshold for inverse binary thresholding.
        - threshold_area (int): Minimum area of a contour to be considered a leaf.
        - min_width (int): Minimum width of a bounding box to be considered a leaf.
        - min_height (int): Minimum height of a bounding box to be considered a leaf.

    Returns:
        - numpy.ndarray: An array of bounding boxes for the detected leaves.
    """

    # Blur the image to reduce noise
    blurred_image = cv2.blur(input_image, kernel_size)

    # Binarize the image
    # Convert the image to grayscale
     # Invert the grayscale image
    _, binarized_image = cv2.threshold(blurred_image, bin_threshold, max_value, cv2.THRESH_BINARY)
    grayscale_image = cv2.cvtColor(binarized_image, cv2.COLOR_BGR2GRAY)
    _, inverted_image = cv2.threshold(grayscale_image, inv_threshold, max_value, cv2.THRESH_BINARY_INV)

    # Find contours in the inverted image
    contours, _ = cv2.findContours(inverted_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    bounding_boxes = []

    # Check if the contour is a leaf based on the area and dimensions
    for c in contours:
        area = cv2.contourArea(c)
        if area > threshold_area:
            x, y, w, h = cv2.boundingRect(c)
            if w > min_width and h > min_height:
                bounding_boxes.append([x, y, x+w, y+h])
    
    # Sort the bounding boxes from left to right
    bounding_boxes = sorted(bounding_boxes, key=lambda b: b[0])
    
    return np.array(bounding_boxes)


def is_image_usable(image) -> bool:
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