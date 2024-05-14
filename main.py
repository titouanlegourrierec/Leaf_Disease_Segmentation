import os
import shutil
import time

import cv2
import pandas
from EasIlastik.run_ilastik import run_ilastik

from leaf_detection import leaf_detection
from leaf_detection import is_image_usable

from text_detection import text_detection

from utils import setup_workspace
from utils import convert_color_space
from utils import leaves_analysis
from utils import status_update

########################################################################################################
############################           Parameters & Constants              #############################
########################################################################################################

# Parameters
COLOR_SPACE = 'LAB'
PROJECT_PATH = '/Users/titouanlegourrierec/Desktop/color_space_evaluation_OK 2/LAB/new_LAB.ilp'
LABELS_WIDTH_PIXELS = 700
LABELS_WIDTH_MM = 12.7

# Constants
COLOR_SPACES = ['YUV', 'HSV', 'LAB', 'HLS']
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']
PIXEL_AREA = (LABELS_WIDTH_MM/LABELS_WIDTH_PIXELS)**2

########################################################################################################
############################                 Main Function                 #############################
########################################################################################################

def main(input_directory, output_directory, update_status = None, project_path = PROJECT_PATH, color_space = COLOR_SPACE):
    """
    Main function to process the images of leaves and extract the required information.

    Parameters:
        - input_directory (str): The directory where the input images are located.
        - output_directory (str): The directory where the output will be saved.
        - update_status (function, optional): A function to update the status of the process. Defaults to None.
        - project_path (str, optional): The path to the project. Defaults to PROJECT_PATH.
        - color_space (str, optional): The color space to be used for image processing. Defaults to COLOR_SPACE.
    """
    # Start of process
    start_process = status_update(update_status, "Start of process.\n")
    
    # Extraction of leaves and labels
    start = status_update(update_status, "Start of extraction of leaves and labels.")
    results_path, file_path, _, _, results_dataframe, _, _ = save_leaves(input_directory, output_directory)
    status_update(update_status, f"End of extraction of leaves and labels. ({round(time.time() - start)}s)\n")
    
    # Color space conversion
    start = status_update(update_status, "Start of color space conversion.")
    if color_space in COLOR_SPACES:
        color_space_subdir = convert_color_space(file_path, results_path, color_space)
    else:
        color_space_subdir = file_path
    status_update(update_status, f"End of color space conversion. ({round(time.time() - start)}s)\n")

    # Leaves segmentation
    start = status_update(update_status, "Start of leaves segmentation.")
    segmented_leaves_path = os.path.join(results_path, 'segmented_leaves') + '/'
    os.makedirs(segmented_leaves_path, exist_ok=True)

    if color_space in COLOR_SPACES:
        input_path = color_space_subdir
    else:
        input_path = file_path

    run_ilastik(input_path = input_path,
                project_path = project_path,
                result_base_path = segmented_leaves_path)
    
    if color_space in COLOR_SPACES:
        shutil.rmtree(color_space_subdir)
    status_update(update_status, f"End of leaves segmentation. ({round(time.time() - start)}s)\n")

    # Results analysis
    start = status_update(update_status, "Start of results analysis.")

    # Extract leaf number from the new file name
    leaf_number = []
    for leaf in results_dataframe['New_File_Name']:
        leaf_number.append(leaf.split('_')[1].split('.')[0][-1])

    # Insert the new column 'Leaf_Number' after 'New_File_Name'
    loc = results_dataframe.columns.get_loc("New_File_Name") + 1
    results_dataframe.insert(loc, 'Leaf_Number', leaf_number)

    # Analyze the leaves and get the areas of different parts
    _, leaf_area, healthy_leaf_area, oidium_area, rust_area = leaves_analysis(results_dataframe, segmented_leaves_path, PIXEL_AREA)

    # Add the areas to the dataframe
    results_dataframe['leaf_area'] = leaf_area
    results_dataframe['healthy_leaf_area'] = healthy_leaf_area
    results_dataframe['oidium_area'] = oidium_area
    results_dataframe['rust_area'] = rust_area

    # Save the results to a CSV file
    results_dataframe.to_csv(os.path.join(results_path, 'results.csv'), index=False)
    status_update(update_status, f"End of results analysis. ({round(time.time() - start)}s)\n")
    
    # End of process
    status_update(update_status, f"End of process. ({round(time.time() - start_process)}s)")

########################################################################################################
############################           Helper Functions                    #############################
########################################################################################################

def save_leaves(input_directory, output_directory):
    """
    This function extracts leaves and labels from images and saves them to files.
    
    Parameters:
    input_directory (str): The directory where the input images are stored.
    output_directory (str): The directory where the output files should be saved.

    Returns:
    tuple: A tuple containing the paths to the results, file, unusable file, and labels directories, 
           and a DataFrame containing the results.
    """
    
    # Set up the workspace
    results_path, file_path, unusable_file_path, labels_path = setup_workspace(output_directory)

    # Initialize lists to store the results
    R_list, P_list, code_champ_list, M_list, EPO_list = [], [], [], [], []
    labels_index = []
    original_file_names = []
    new_file_names = []
    
    count_usable_files = 1
    count_unusable_files = 0

    for filename in os.listdir(input_directory):
        # Check if the file is an image file
        if os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS:

            # Create the full path to the image file
            full_path = os.path.join(input_directory, filename)

            # Read the image file
            img = cv2.imread(full_path)

            # Check if the image is usable
            if not is_image_usable(img):
                # Save the unusable file to the unusable_file_path directory
                cv2.imwrite(os.path.join(unusable_file_path, f"Unusable_File_{filename}"), img)
                count_unusable_files += 1

            else:
                R, P, code_champ, M, EPO, text_box_result = text_detection(img)

                # Save the labels to the labels_path directory
                cv2.imwrite(os.path.join(labels_path, f"Labels_{count_usable_files}.jpg"), text_box_result)

                # Detect leaves in the image
                bounding_boxes = leaf_detection(img)
                #original_file_name, extension = os.path.splitext(os.path.basename(full_path))
                
                # Save the processed image to the file_path directory
                for j, box in enumerate(bounding_boxes):
                    x1, y1, x2, y2 = box
                    part = img[y1:y2, x1:x2]
                    #new_file_name = f"{count_usable_files}_leaf{j + 1}{extension}"
                    new_file_name = f"{count_usable_files}_leaf{j + 1}.png"
                    cv2.imwrite(os.path.join(file_path, new_file_name), part)

                    R_list.append(R)
                    P_list.append(P)
                    code_champ_list.append(code_champ)
                    M_list.append(M)
                    EPO_list.append(EPO)
                    labels_index.append(count_usable_files)
                    original_file_names.append(filename)
                    new_file_names.append(new_file_name)

                count_usable_files += 1
    
    # Create a DataFrame to store the results
    results = pandas.DataFrame({
        'Original_File_Name': original_file_names,
        'New_File_Name': new_file_names,
        'Label': labels_index,
        'R': R_list,
        'P': P_list,
        'Code_Champ': code_champ_list,
        'M': M_list,
        'EPO': EPO_list
    })

    return results_path, file_path, unusable_file_path, labels_path, results, count_usable_files, count_unusable_files