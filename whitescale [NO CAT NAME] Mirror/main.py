import os
from xml.etree import ElementTree as ET
import cairosvg
from io import BytesIO
from PIL import Image
from concurrent.futures import ProcessPoolExecutor
from PIL import Image, ImageOps

# Define the paths
svg_folder = 'SVGFolder'
output_folder = 'OutputFile'

# Target dimensions
target_width = 2000
target_height = 2000

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
        scale_png(filepath)

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
    from pathlib import Path
    from PIL import ImageOps

    # Open original image
    with Image.open(png_filepath) as img:
        width, height = img.size
        target_size = 2000

        # Scale proportionally
        if width > height:
            scale_factor = target_size / width if width > target_size else 1
        else:
            scale_factor = target_size / height if height > target_size else 1

        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Make all visible pixels solid white
        if img.mode == 'RGBA':
            r, g, b, a = img.split()
            white_rgb = Image.new("RGB", img.size, (255, 255, 255))
            img = Image.merge("RGBA", (*white_rgb.split(), a))
        else:
            white = Image.new("RGB", img.size, (255, 255, 255))
            img = white.convert("RGBA")

        # Save original
        img.save(png_filepath)

        # Create mirrored image
        mirrored_img = ImageOps.mirror(img)

        # Prepare mirrored folder path
        original_path = Path(png_filepath)
        mirrored_folder = original_path.parent / "mirrored"
        mirrored_folder.mkdir(parents=True, exist_ok=True)

        # Save mirrored image inside mirrored folder
        mirrored_path = mirrored_folder / original_path.name
        mirrored_img.save(mirrored_path)





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