import os
from xml.etree import ElementTree as ET
import cairosvg
from io import BytesIO
from PIL import Image
from concurrent.futures import ProcessPoolExecutor

# Define paths
svg_folder = 'SVGFolder'
output_folder = 'OutputFile'

# Target dimensions
target_width = 2000
target_height = 2000

# Split parameters
split_x = 1169
image_height = 911  # expected height of the final PNG after scaling
image_width = 2000  # expected width of the final PNG after scaling

left_eye_dir = 'LeftEye'
right_eye_dir = 'RightEye'


def convert_svg_to_png(input_svg_path, output_png_path):
    scale_factor = get_scale_factor(input_svg_path)

    with open(input_svg_path, 'rb') as f:
        svg_content = f.read()

    # Convert SVG to PNG with scale factor to retain colors
    cairosvg.svg2png(bytestring=svg_content, write_to=output_png_path, scale=scale_factor)

    # Scale the PNG file to target size (if needed)
    img = scale_png(output_png_path)
    return img


def get_scale_factor(input_svg_path):
    svg_bytes = BytesIO()
    tree = ET.parse(input_svg_path)
    tree.write(svg_bytes, encoding='utf-8')
    svg_content = svg_bytes.getvalue()

    output_png = BytesIO()
    cairosvg.svg2png(bytestring=svg_content, write_to=output_png, scale=1)

    with Image.open(output_png) as img:
        width, height = img.size

    return min(target_width / width, target_height / height, 10)


def scale_png(png_filepath):
    with Image.open(png_filepath) as img:
        width, height = img.size
        scale_factor = min(target_width / width, target_height / height, 1)

        new_size = (int(width * scale_factor), int(height * scale_factor))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

        # Ensure image is RGBA to support transparency for splitting
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        img.save(png_filepath)
        return img


def split_and_save(img, original_filepath, output_subfolder):
    base_name = os.path.basename(original_filepath)
    name, _ = os.path.splitext(base_name)

    # Create copies for left and right images
    left_img = img.copy()
    right_img = img.copy()

    left_pixels = left_img.load()
    right_pixels = right_img.load()

    # Make right half transparent in left image
    for x in range(split_x, image_width):
        for y in range(image_height):
            if x < left_img.width and y < left_img.height:
                left_pixels[x, y] = (0, 0, 0, 0)

    # Make left half transparent in right image
    for x in range(0, split_x):
        for y in range(image_height):
            if x < right_img.width and y < right_img.height:
                right_pixels[x, y] = (0, 0, 0, 0)

    # Create output subfolders for left and right eyes
    left_output_dir = os.path.join(output_subfolder, left_eye_dir)
    right_output_dir = os.path.join(output_subfolder, right_eye_dir)
    os.makedirs(left_output_dir, exist_ok=True)
    os.makedirs(right_output_dir, exist_ok=True)

    # Save the split images
    left_img.save(os.path.join(left_output_dir, f"{name}.png"))
    right_img.save(os.path.join(right_output_dir, f"{name}.png"))


def process_svg(input_svg_path, output_subfolder):
    svg_name = os.path.splitext(os.path.basename(input_svg_path))[0]
    os.makedirs(output_subfolder, exist_ok=True)

    output_filename = f"shape_{svg_name}.png"
    output_filepath = os.path.join(output_subfolder, output_filename)

    # Convert SVG to PNG with colors retained and scaling
    img = convert_svg_to_png(input_svg_path, output_filepath)

    # Split the image into left and right parts
    split_and_save(img, output_filepath, output_subfolder)

    print(f"Processed and split '{svg_name}' saved in '{output_subfolder}'")


def process_folder(input_subfolder, output_subfolder):
    svg_files = sorted([f for f in os.listdir(input_subfolder) if f.endswith('.svg')])
    if not svg_files:
        return

    os.makedirs(output_subfolder, exist_ok=True)

    with ProcessPoolExecutor() as executor:
        futures = []
        for svg_file in svg_files:
            input_path = os.path.join(input_subfolder, svg_file)
            futures.append(executor.submit(process_svg, input_path, output_subfolder))

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
            process_folder(category_path, output_subfolder)

    print("All SVGs converted and split with correct naming and colors retained.")


if __name__ == "__main__":
    main()
