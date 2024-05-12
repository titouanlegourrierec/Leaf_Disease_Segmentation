import argparse
import sys

import tkinter as tk
from tkinter import filedialog, END

from main import main

def browse_directory(directory_var, button):
    """Open a file dialog and set the directory_var to the selected directory."""
    directory = filedialog.askdirectory()
    if directory:  # If a directory was selected
        directory_var.set(directory)
        button.config(fg='green')  # Change the button color to green

def run_main():
    """Run the main function with the selected directories."""
    input_directory = input_dir_var.get()
    output_directory = output_dir_var.get()
    main(input_directory, output_directory, update_status)

def update_status(status):
    """Update the status text with the given status."""
    status_text.insert(END, status + "\n")
    root.update()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run the main function with the selected directories.')
    parser.add_argument('-i', '--input', help='Input directory')
    parser.add_argument('-o', '--output', help='Output directory')
    return parser.parse_args()

def main_cli():
    """Run the main function with command line arguments."""
    args = parse_args()
    if args.input and args.output:
        main(args.input, args.output, print)
    else:
        print("Both input and output directories must be provided.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:  # If command line arguments were provided
        main_cli()
    else:  # If no command line arguments were provided, launch the GUI
        root = tk.Tk()
        root.geometry("500x400")

        # Create StringVars to hold the directories
        input_dir_var = tk.StringVar()
        output_dir_var = tk.StringVar()

        # Create a frame to hold the buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        # Create browse buttons for the directories
        input_dir_button = tk.Button(button_frame, text="Browse Input Directory", command=lambda: browse_directory(input_dir_var, input_dir_button))
        input_dir_button.pack(side='left', padx=10)

        output_dir_button = tk.Button(button_frame, text="Browse Output Directory", command=lambda: browse_directory(output_dir_var, output_dir_button))
        output_dir_button.pack(side='left', padx=10)

        # Create a text widget to display the status
        status_text = tk.Text(root, height=20, width=60)
        status_text.pack(pady=10)

        # Create a button to run the main function
        run_button = tk.Button(root, text="Run", command=run_main)
        run_button.pack(pady=10)

        root.mainloop()

        