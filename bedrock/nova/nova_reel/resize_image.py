#!/usr/bin/env python3
"""
Resize Picture1.png to 1280x720 pixels
"""

from PIL import Image
import os

def resize_image(input_path, output_path, target_size=(1280, 720)):
    """
    Resize an image to the target size and remove transparency
    
    Args:
        input_path: Path to the input image
        output_path: Path to save the resized image
        target_size: Tuple of (width, height) for the target size
    """
    try:
        # Open the image
        with Image.open(input_path) as img:
            print(f"Original image size: {img.size}")
            print(f"Original image mode: {img.mode}")
            
            # Handle transparency by converting to RGB
            if img.mode in ('RGBA', 'LA', 'P'):
                print("Image has transparency, converting to RGB with white background...")
                # Create a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                # Paste the image onto the white background
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                print(f"Converting from {img.mode} to RGB...")
                img = img.convert('RGB')
            
            print(f"Final image mode: {img.mode}")
            
            # Resize the image using LANCZOS resampling for better quality
            resized_img = img.resize(target_size, Image.Resampling.LANCZOS)
            
            # Save the resized image as JPEG to ensure no transparency
            if output_path.lower().endswith('.png'):
                output_path = output_path.replace('.png', '.jpg')
            
            resized_img.save(output_path, 'JPEG', optimize=True, quality=95)
            
            print(f"Image resized to {target_size} and saved as: {output_path}")
            print(f"New file size: {os.path.getsize(output_path)} bytes")
            
    except Exception as e:
        print(f"Error resizing image: {e}")

if __name__ == "__main__":
    input_file = "Picture1.png"
    output_file = "picture1_resized.jpg"  # Changed to JPG to avoid transparency
    
    if os.path.exists(input_file):
        resize_image(input_file, output_file)
    else:
        print(f"Error: {input_file} not found in current directory")
