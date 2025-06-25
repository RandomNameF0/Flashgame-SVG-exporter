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


def convert_svg_to_png(input_svg_path, output_png_path):
    # Determine scale factor to fit the target size
    scale_factor = get_scale_factor(input_svg_path)

    # Read SVG content
    with open(input_svg_path, 'rb') as f:
        svg_content = f.read()

    # Convert SVG to PNG
    cairosvg.svg2png(bytestring=svg_content, write_to=output_png_path, scale=scale_factor)

    # Scale PNG to ensure max dimension is 2000
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

    if width > height:
        return min(target_width / width, 10)
    else:
        return min(target_height / height, 10)


def scale_png(png_filepath):
    with Image.open(png_filepath) as img:
        width, height = img.size

        scale_factor = min(target_width / width, target_height / height, 1)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)

        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        img.save(png_filepath)


def process_folder(input_subfolder, output_subfolder):
    svg_files = [f for f in os.listdir(input_subfolder) if f.endswith('.svg')]
    if not svg_files:
        return

    os.makedirs(output_subfolder, exist_ok=True)

    with ProcessPoolExecutor() as executor:
        futures = []
        for svg_file in svg_files:
            input_path = os.path.join(input_subfolder, svg_file)
            filename_wo_ext = os.path.splitext(svg_file)[0]
            output_path = os.path.join(output_subfolder, f"{filename_wo_ext}.png")
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

    print("All SVGs have been converted to combined PNGs!")


if __name__ == "__main__":
    main()
