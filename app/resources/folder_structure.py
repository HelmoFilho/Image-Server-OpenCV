## -- Importing External Modules -- ##
from flask import wrappers, abort
import os, cv2, re, shutil
import numpy as np

## -- Importing Internal Modules -- ##
from app.config import MAIN_FOLDER


def path_to_dict(path) -> dict:
    """
    returns the folder structure in a tree style dict

    Args:
        path (str): initial folder

    Returns:
        dict: dict_like structure
    """

    d = {'name': os.path.basename(path)}

    if os.path.isdir(path):
        d['type'] = "folder"
        d['content'] = [path_to_dict(os.path.join(path, x)) for x in os.listdir(path)]

    else:
        d['type'] = "file"

    return d


def folder_structure_get(**kwargs) -> wrappers.Response:
    """
    Returns the tree-like structure of the folders relative to the predetermined folder
    """

    if not os.path.exists(MAIN_FOLDER):
        abort(400, {'message': 'Main Folder does not exist.'})

    structure = path_to_dict(MAIN_FOLDER)

    return {
        "status": True,
        "message": "Structure send",
        "data": structure,
    }


def folder_structure_post(**kwargs) -> wrappers.Response:
    """
    Saves the image in the predetermined folder
    """

    if not os.path.exists(MAIN_FOLDER):
        abort(400, {'message': 'Main Folder does not exist.'})

    files = kwargs.get("files")
    if not files:
        return {
            "status": False,
            "message": "No image to save",
        }
    
    file_path, file = list(files.items())[0]

    # Checking the file
    try:
        file_bytes = np.fromstring(file.read(), np.uint8)
        cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
    except Exception as e:
        abort(400, {'message': 'Invalid image.'})
    
    file.seek(0)
    orig_name = str(file.filename).lower()
    orig_format = orig_name.split(".")[-1]

    if orig_format not in {"png", "jpg", "jpeg", "webp"}:
        abort(400, {'message': "Invalid format for image saving."})

    # Saving the file
    if not file_path:
        file.save(os.path.join(MAIN_FOLDER, orig_name))

    else:
        all_path = str(file_path).lower().split("/")

        save_folder = []

        for index, new_path in enumerate(all_path):

            if (index == len(all_path) - 1):

                if not re.match(r"^[a-z0-9\-_]+\.((png)|(jpg)|(jpeg)|(webp))$", new_path):

                    if not re.match(r"^[a-z0-9\-_]+$", new_path):
                        abort(400, {'message': "Invalid path for image saving."})

            else:
                if not re.match(r"^[a-z0-9\-_]+$", new_path):
                    abort(400, {'message': "Invalid path for image saving."})

            save_folder.append(new_path)

        path_to_file = f"{MAIN_FOLDER}"

        for index, path in enumerate(save_folder):

            path_to_file += f"/{path}"

            if (index == len(all_path) - 1):

                if "." in path:
                    file.save(path_to_file)

                else:
                    if not os.path.exists(path_to_file):
                        os.mkdir(path_to_file)

                    file.save(os.path.join(path_to_file, orig_name))

            else:
                if not os.path.exists(path_to_file):
                    os.mkdir(path_to_file)

    return {
        "status": True,
        "message": "Image saved",
    }


def folder_structure_delete(**kwargs) -> wrappers.Response:
    """
    Saves the image in the predetermined folder
    """

    if not os.path.exists(MAIN_FOLDER):
        abort(400, {'message': 'Main Folder does not exist.'})

    request = kwargs.get("request") if isinstance(kwargs.get("request"), dict) else {}

    to_delete = request.get("path")

    if not to_delete:

        for filename in os.listdir(MAIN_FOLDER):

            path = os.path.join(MAIN_FOLDER, filename)
            
            if os.path.isfile(path) or os.path.islink(path):
                os.remove(path)

            elif os.path.isdir(path):
                shutil.rmtree(path)

        return {
            "status": True,
            "message": "Subdirectories removed",
        }

    full_path = f"{MAIN_FOLDER}/{to_delete}"

    if not os.path.exists(full_path):
        abort(400, {'message': 'Chosen path does not exist.'})

    if os.path.isfile(full_path):
        os.remove(full_path)
        return {
            "status": True,
            "message": "File removed",
        }

    shutil.rmtree(full_path)

    return {
        "status": True,
        "message": "Directory removed",
    }