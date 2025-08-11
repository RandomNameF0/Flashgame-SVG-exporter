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

def convert_svg_to_png(input_svg_path, output_png_path):
    scale_factor = get_scale_factor(input_svg_path)

    with open(input_svg_path, 'rb') as f:
        svg_content = f.read()

    cairosvg.svg2png(bytestring=svg_content, write_to=output_png_path, scale=scale_factor)
    scale_png(output_png_path)


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
        img.save(png_filepath)


def process_folder(input_subfolder, output_subfolder):
    svg_files = sorted([f for f in os.listdir(input_subfolder) if f.endswith('.svg')])
    if not svg_files:
        return

    os.makedirs(output_subfolder, exist_ok=True)

    with ProcessPoolExecutor() as executor:
        futures = []
        for svg_file in svg_files:
            input_path = os.path.join(input_subfolder, svg_file)
            base_name = os.path.splitext(svg_file)[0]  # e.g., "3" from "3.svg"
            output_filename = f"hape_{base_name}.png"
            output_path = os.path.join(output_subfolder, output_filename)

            futures.append(executor.submit(convert_svg_to_png, input_path, output_path))

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

    print("All SVGs converted with correct names like 'combined_shape_3.png'")


if __name__ == "__main__":
    main()
