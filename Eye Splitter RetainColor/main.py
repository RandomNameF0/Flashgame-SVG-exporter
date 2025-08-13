
import os
from xml.etree import ElementTree as ET
import cairosvg
from io import BytesIO
from PIL import Image
from concurrent.futures import ProcessPoolExecutor

# Define the paths
svg_folder = 'SVGFolder'
output_folder = 'OutputFile'

# Target dimensions
target_width = 2000
target_height = 2000

split_x = 1169
image_height = 911  # known image height
image_width = 2000  # known image width
left_eye_dir = 'LeftEye'
right_eye_dir = 'RightEye'


# Function to process each SVG file and its shapes
def process_svg(input_svg_path, output_subfolder, scale_factor, category_name):
    svg_name = os.path.splitext(os.path.basename(input_svg_path))[0]

    # Parse the SVG content
    tree = ET.parse(input_svg_path)
    root = tree.getroot()

    # Namespace for SVG
    namespace = '{http://www.w3.org/2000/svg}'
    defs = root.find(f'{namespace}defs')

    # Collect all shape IDs
    shape_ids = []
    if defs is not None:
        for shape_elem in defs.findall(f'{namespace}g'):
            shape_id = shape_elem.attrib.get('id')
            if shape_id and shape_id.startswith('shape'):
                shape_ids.append(shape_id)

    # Generate PNGs with the given scale factor
    for loop_index, shape_id in enumerate(shape_ids, start=1):
        # Create new parse each time
        tree = ET.parse(input_svg_path)
        root = tree.getroot()
        newDef = root.find(f'{namespace}defs')

        for sid in shape_ids:
            if sid != shape_id:
                for shape_elem in newDef.findall(f'{namespace}g'):
                    if shape_elem.attrib.get('id') == sid:
                        newDef.remove(shape_elem)

        # Convert the modified SVG to PNG
        svg_bytes = BytesIO()
        tree.write(svg_bytes, encoding='utf-8')
        svg_content = svg_bytes.getvalue()

        # Create a folder for this shape if it doesn't exist
        shape_folder = os.path.join(output_subfolder, f'shape_{loop_index}')
        os.makedirs(shape_folder, exist_ok=True)

        # Rename the PNG based on the category, shape number, and SVG file number
        filename = f"shape{loop_index}_{svg_name}.png"
        filepath = os.path.join(shape_folder, filename)

        cairosvg.svg2png(bytestring=svg_content, write_to=filepath, scale=scale_factor)
       
        img = scale_png(filepath)
        split_and_save(img, filepath, shape_folder)

    print(f"All shapes from '{svg_name}' have been saved in '{output_subfolder}'\n")


def get_scale_factor(input_svg_path):
    svg_bytes = BytesIO()
    tree = ET.parse(input_svg_path)
    tree.write(svg_bytes, encoding='utf-8')
    svg_content = svg_bytes.getvalue()

    output_png = BytesIO()
    cairosvg.svg2png(bytestring=svg_content, write_to=output_png, scale=1)

    with Image.open(output_png) as img:
        width, height = img.size

    if width > height:
        scale_factor = target_width / width
    else:
        scale_factor = target_height / height

    return min(scale_factor, 10)


def scale_png(png_filepath):
    with Image.open(png_filepath) as img:
        # Resize logic (same as before)
        width, height = img.size
        target_size = 2000

        if width > height:
            scale_factor = target_size / width if width > target_size else 1
        else:
            scale_factor = target_size / height if height > target_size else 1

        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

 
        img.save(png_filepath)

        return img  # Return for further processing


def split_and_save(img, original_filepath, shape_folder):
    base_name = os.path.basename(original_filepath)
    name, ext = os.path.splitext(base_name)

    # Create transparent images for left and right
    left_img = img.copy()
    right_img = img.copy()

    # Make right side transparent in left_img
    left_pixels = left_img.load()
    for x in range(split_x, image_width):
        for y in range(image_height):
            left_pixels[x, y] = (0, 0, 0, 0)

    # Make left side transparent in right_img
    right_pixels = right_img.load()
    for x in range(0, split_x):
        for y in range(image_height):
            right_pixels[x, y] = (0, 0, 0, 0)

    # Save both
    left_output_dir = os.path.join(left_eye_dir, os.path.basename(shape_folder))
    right_output_dir = os.path.join(right_eye_dir, os.path.basename(shape_folder))
    os.makedirs(left_output_dir, exist_ok=True)
    os.makedirs(right_output_dir, exist_ok=True)

    left_img.save(os.path.join(left_output_dir, f"{name}.png"))
    right_img.save(os.path.join(right_output_dir, f"{name}.png"))






def process_folder(input_subfolder, output_subfolder, category_name):
    svg_files = [f for f in os.listdir(input_subfolder) if f.endswith('.svg')]
    if not svg_files:
        return

    first_svg_path = os.path.join(input_subfolder, svg_files[0])
    scale_factor = get_scale_factor(first_svg_path)

    os.makedirs(output_subfolder, exist_ok=True)

    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(process_svg, os.path.join(input_subfolder, svg_file), output_subfolder, scale_factor, category_name)
            for svg_file in svg_files
        ]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Error processing file: {e}")


def main():
    for category in os.listdir(svg_folder):
        category_path = os.path.join(svg_folder, category)
        if os.path.isdir(category_path):
            output_subfolder = os.path.join(output_folder, category)
            process_folder(category_path, output_subfolder, category)

    print("Processing complete!")


if __name__ == "__main__":
    main()


