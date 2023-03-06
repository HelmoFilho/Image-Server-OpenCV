## -- Importing External Modules -- ##
from flask import wrappers, make_response, abort
import numpy as np
import os, cv2

## -- Importing Internal Modules -- ##
from app.config import MAIN_FOLDER

def image_serving_get(**kwargs) -> wrappers.Response:
    """
    Get and process the image and returns it

    kwargs:
        full_path (str): The path to the image relative to the predetermined folder

        width (int): The width (in pixels) of the final image. Height will be proporcional if not given.
        height (int): The height (in pixels) of the final image. Width will be proporcional if not given.
        
        square (int): The edge length (in pixels) of all side of the final image.
        circle (int): The radius of the circle (in pixels) of the final image.
    """

    # Setting the parameters
    full_path: str = kwargs.get("full_path")

    full_path = f"{MAIN_FOLDER}/{full_path}"

    if not (os.path.isfile(full_path) and "." in full_path):
        abort(400, {'message': "Main Folder does not exist."})

    img_format = full_path.split(".")[-1]

    if img_format not in {"png", "jpg", "jpeg", "webp"}:
        abort(400, {'message': "Invalid format for image serving."})

    request: dict = kwargs.get("request") if kwargs.get("request") else {}

    width: int = int(request.get("width")) if request.get("width") else None
    height: int  = int(request.get("height")) if request.get("height") else None
    square: int  = int(request.get("square")) if request.get("square") else None
    circle: int  = int(request.get("circle")) if request.get("circle") else None

    # Getting the image
    img = cv2.imread(full_path, cv2.IMREAD_UNCHANGED)

    shape: tuple = img.shape
    len_shape: int = len(shape)

    orig_height: int = None
    orig_width: int = None
    channels: int = None

    if len_shape < 2: abort(404)

    elif len_shape == 2:
        orig_height, orig_width = shape
        channels = 2

    else:
        orig_height = shape[0]
        orig_width = shape[1]
        channels = shape[2]

    if channels not in {2,3,4}: abort(404)

    # Resizing the image
    if width or height:
        
        if width and not height:
            height = int(np.ceil((orig_height * width) / orig_width))

        elif height and not width:
            width = int(np.ceil((orig_width * height) / orig_height))

        dim = (width, height)
        img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

    elif square:

        bool_complement = orig_height != orig_width

        if bool_complement:

            if orig_width > orig_height:
                width = square
                height = int(np.ceil((orig_height * width) / orig_width))

                horizontal_edge = width
                vertical_edge = int(np.ceil((width - height) / 2))

            else:
                height = square
                width = int(np.ceil((orig_width * height) / orig_height))

                vertical_edge = height
                horizontal_edge = int(np.ceil((height - width) / 2))

        else:
            width, height = square, square

        dim = (width, height)
        img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

        if bool_complement:

            if height != width:

                if channels == 4:
                    sum_img = np.zeros((vertical_edge, horizontal_edge, 4), dtype=np.uint8)

                elif channels == 3:
                    sum_img = np.ones((vertical_edge, horizontal_edge, 3), dtype=np.uint8) * 255

                else:
                    sum_img = np.ones((vertical_edge, horizontal_edge), dtype=np.uint8) * 255

                if height > width:
                    img = cv2.hconcat([sum_img, img, sum_img])

                else:
                    img = cv2.vconcat([sum_img, img, sum_img])

    elif circle:

        # The way a "circle" image is treated here will be the same as the "width/height" way,
        # so the images will be stretched to fit the area of the circle.
        # If necessary you can change by putting the "square" way here before the backgroud creation
        dim = (circle * 2, circle * 2)
        img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

        # Creating the mask
        background = np.zeros(img.shape, dtype=np.uint8)
        
        color = tuple([255] * channels)
        center = (circle, circle)

        mask = cv2.circle(background, center, circle, color, -1)

        img = cv2.bitwise_and(img, mask)        

    # Serving the image
    buffer = cv2.imencode(f'.{img_format}', img)[1].tobytes()

    response = make_response(buffer)

    headers = {
        'Content-Type': f"image/{img_format}",
        "mimetype": 'multipart/x-mixed-replace; boundary=frame'
    }

    response.headers.update(headers)

    return response