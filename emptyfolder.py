import os
import shutil

# get the current directory of the python file
current_directory = os.path.dirname(os.path.abspath(__file__))

# set the path of the folder to empty
folder_path = os.path.join(current_directory, "church dashboard pictures")

# check if folder exists before emptying
if os.path.exists(folder_path):
    # empty the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")
    print("Folder emptied successfully!")
else:
    print("Folder does not exist.")
