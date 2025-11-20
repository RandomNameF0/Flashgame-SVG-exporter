import os
from PIL import Image

# Path to the folder containing PNGs
input_folder = "input"
output_folder = os.path.join(input_folder, "mirrored")

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Loop through files in the folder
for filename in os.listdir(input_folder):
    if filename.lower().endswith(".png"):
        input_path = os.path.join(input_folder, filename)

        # Open and mirror the image
        img = Image.open(input_path)
        mirrored = img.transpose(Image.FLIP_LEFT_RIGHT)

        # Save to the mirrored folder
        output_path = os.path.join(output_folder, filename)
        mirrored.save(output_path)

        print(f"Mirrored: {filename}")

print("Done!")
