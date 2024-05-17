"""
Utils Module
---------------------

Description:
This file contains utility functions for leaf detection in an image. It includes functions for setting up
the workspace, converting the color space of images, analyzing segmented leaves, and updating the process
status.

Authors: LE GOURRIEREC Titouan, CONNESSON Léna, PROUVOST Axel
Date: 17/05/2024
"""

import os
import time

import cv2
import numpy as np

########################################################################################################
############################           Parameters & Constants              #############################
########################################################################################################

# Parameters & Constants
NEW_RESULTS_DIR = 'Results'
FILE_DIR = 'File'
UNUSABLE_FILE_DIR = 'Unusable_File'
LABELS_DIR = 'Labels'

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']

########################################################################################################
############################                 Main Functions                 #############################
########################################################################################################

def setup_workspace(output_directory) -> tuple:
    """
    Sets up the workspace for the image processing task.

    This function creates a new directory for the results within the specified output directory. 
    It also creates subdirectories for the processed images, unusable images, and labels.

    Parameters:
        - output_directory (str): The path to the directory where the results should be stored.

    Returns:
        - tuple: A tuple containing the paths to the results directory, the processed images directory, 
        - the unusable images directory, and the labels directory.
    """
    # Create a new directory for the results
    results_path = os.path.join(output_directory, NEW_RESULTS_DIR)
    os.makedirs(results_path, exist_ok=True)

    # Create subdirectories for the processed and unusable images and the labels
    file_path = os.path.join(results_path, FILE_DIR)
    unusable_file_path = os.path.join(results_path, UNUSABLE_FILE_DIR)
    labels_path = os.path.join(results_path, LABELS_DIR)
    os.makedirs(file_path)
    os.makedirs(unusable_file_path)
    os.makedirs(labels_path)

    return results_path, file_path, unusable_file_path, labels_path


def convert_color_space(input_directory,
                     output_directory,
                     color_space) -> str:
    """
    Converts the color space of all images in the input directory and saves them in the output directory.

    Parameters:
        - input_directory (str): The path to the directory containing the input images.
        - output_directory (str): The path to the directory where the converted images should be saved.
        - color_space (str): The target color space. Supported values are 'YUV', 'HSV', 'LAB', and 'HLS'.

    Returns:
        - str: The path to the directory containing the converted images.
    """
    
    # Mapping from color space names to OpenCV conversion flags
    conversion_flags = {
        'YUV': cv2.COLOR_BGR2YUV,
        'HSV': cv2.COLOR_BGR2HSV,
        'LAB': cv2.COLOR_BGR2LAB,
        'HLS': cv2.COLOR_BGR2HLS,
    }

    for filename in os.listdir(input_directory):
        if os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS:
            
            # Read the image
            img = cv2.imread(os.path.join(input_directory, filename))

            # Convert the color space of the image
            converted_img = cv2.cvtColor(img, conversion_flags[color_space])
            
            # Create the output subdirectory if it doesn't exist
            output_subdir = os.path.join(output_directory, 'color_space')
            if not os.path.exists(output_subdir):
                os.makedirs(output_subdir)

            # Define the output filename
            output_filename = os.path.join(output_subdir, filename)
                
            # Save the converted image
            cv2.imwrite(output_filename, converted_img)

    return output_subdir


def leaves_analysis(results_dataframe, segmented_leaves_path, PIXEL_AREA) -> tuple:
    """
    Analyzes the segmented leaves and calculates the area of each type of region.

    Parameters:
        - results_dataframe (pandas.DataFrame): The dataframe containing the results.
        - segmented_leaves_path (str): The path to the directory containing the segmented leaves images.
        - PIXEL_AREA (float): The area represented by each pixel.

    Returns:
        - list: A list containing the areas of the background, leaf, healthy leaf, oidium leaf, and rust leaf regions.
    """

    # Initialize lists to store the areas of each type of region
    background_list = []
    leaf_list = []
    healthy_leaf_list = []
    oidium_leaf_list = []
    rust_leaf_list = []
    
    for elt in results_dataframe["New_File_Name"]:

        # Define the path to the segmented leaves image
        path = '/Users/titouanlegourrierec/Desktop/results/segmented_leaves/' + os.path.splitext(elt)[0] + '_Simple_Segmentation.png'

        # Read the image and convert it to grayscale
        img = cv2.imread(path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Calculate the area of each type of region and append it to the corresponding list
        background_list.append(round(np.sum(img == 63) * PIXEL_AREA, 3))
        oidium_leaf_list.append(round(np.sum(img == 191) * PIXEL_AREA, 3))
        rust_leaf_list.append(round(np.sum(img == 255) * PIXEL_AREA, 3))
        healthy_leaf_list.append(round(np.sum(img == 127) * PIXEL_AREA, 3))
        leaf_list = [round(sum(x), 3) for x in zip(healthy_leaf_list, oidium_leaf_list, rust_leaf_list)]

    return background_list, leaf_list, healthy_leaf_list, oidium_leaf_list, rust_leaf_list

def status_update(update_status, message):
    """Update the status of the process."""
    start = time.time()  # Record the start time

    if callable(update_status):
        update_status(message)
    else:
        print(message)

    return start  # Return the start time

########################################################################################################