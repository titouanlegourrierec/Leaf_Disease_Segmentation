import os
import time

import cv2
import numpy as np

########################################################################################################

# Constants
NEW_RESULTS_DIR = 'Results'
FILE_DIR = 'File'
UNUSABLE_FILE_DIR = 'Unusable_File'
LABELS_DIR = 'Labels'

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']

########################################################################################################

def setup_workspace(output_directory):
    
    # Create a new directory for the results
    results_path = os.path.join(output_directory, NEW_RESULTS_DIR)
    os.makedirs(results_path, exist_ok=True)

    # Create subdirectories for the processed and unusable images
    file_path = os.path.join(results_path, FILE_DIR)
    unusable_file_path = os.path.join(results_path, UNUSABLE_FILE_DIR)
    labels_path = os.path.join(results_path, LABELS_DIR)
    os.makedirs(file_path)
    os.makedirs(unusable_file_path)
    os.makedirs(labels_path)

    return results_path, file_path, unusable_file_path, labels_path


def convert_color_space(input_directory,
                     output_directory,
                     color_space):
    
    conversion_flags = {
        'YUV': cv2.COLOR_BGR2YUV,
        'HSV': cv2.COLOR_BGR2HSV,
        'LAB': cv2.COLOR_BGR2LAB,
        'HLS': cv2.COLOR_BGR2HLS,
    }

    for filename in os.listdir(input_directory):
        if os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS:
            
            img = cv2.imread(os.path.join(input_directory, filename))

            converted_img = cv2.cvtColor(img, conversion_flags[color_space])
                
            output_subdir = os.path.join(output_directory, 'color_space')

            if not os.path.exists(output_subdir):
                os.makedirs(output_subdir)

            # Define the output filename
            output_filename = os.path.join(output_subdir, filename)
                
            # Save the converted image
            cv2.imwrite(output_filename, converted_img)

    return output_subdir

def leaves_analysis(results_dataframe, segmented_leaves_path, PIXEL_AREA):
    
    background_list = []
    leaf_list = []
    healthy_leaf_list = []
    oidium_leaf_list = []
    rust_leaf_list = []
    
    for elt in results_dataframe["New_File_Name"]:

        path = '/Users/titouanlegourrierec/Desktop/results/segmented_leaves/' + os.path.splitext(elt)[0] + '_Simple_Segmentation.png'

        img = cv2.imread(path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        background_list.append(round(np.sum(img == 63) * PIXEL_AREA, 3))
        oidium_leaf_list.append(round(np.sum(img == 191) * PIXEL_AREA, 3))
        rust_leaf_list.append(round(np.sum(img == 255) * PIXEL_AREA, 3))
        healthy_leaf_list.append(round(np.sum(img == 127) * PIXEL_AREA, 3))
        leaf_list = [round(sum(x), 3) for x in zip(healthy_leaf_list, oidium_leaf_list, rust_leaf_list)]

    return background_list, leaf_list, healthy_leaf_list, oidium_leaf_list, rust_leaf_list

def status_update(update_status, message):
    """Print a status update with a timestamp and return the start time."""
    if update_status is not None:
        update_status(message)
        start = time.time()
        return start

########################################################################################################