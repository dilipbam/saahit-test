import concurrent.futures
import io
import os
import uuid

from PIL import Image
from marshmallow import ValidationError

from vendor_app.callbacks.user_validators import FileSchema
from vendor_app.config import MEDIA_PATH


def save_image(image, user_id, image_name='', ):
    img_name = str(user_id) + '_' + image_name + '.' + 'jpg'
    image_path = os.path.join(MEDIA_PATH, img_name)

    # Check if the image already exists
    if os.path.exists(image_path):
        # Remove the existing image
        os.remove(image_path)

    with Image.open(image) as img:
        # Convert image to RGB mode
        img = img.convert('RGB')
        # Resize image to 300x300
        img.thumbnail((300, 300))
        # Save resized image to memory
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)

    # Save image to disk
    with open(image_path, 'wb') as f:
        f.write(img_io.read())

    return img_name


def validate_images(images):
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(validate_image, image): image for image in images}
        for future in concurrent.futures.as_completed(future_to_file):
            image = future_to_file[future]
            try:
                result = future.result()
            except Exception as e:
                result = {'filename': image.filename, 'error': str(e)}
            results.append(result)
    return results


def validate_image(image):
    try:
        schema = FileSchema()
        errors = schema.validate({'image': image.read()})
        if errors:
            return {'filename': image.filename, 'errors': errors}
        else:
            return {'filename': image.filename, 'valid': True}
    except Exception as e:
        return {'filename': image.filename, 'error': str(e)}