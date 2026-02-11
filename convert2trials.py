#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to convert images from the images folder to trials folder.
Resizes all images to external screen resolution and saves them as trial1, trial2, etc.
"""

import os
import subprocess
from PIL import Image


def get_display_info(display_index=1):
    """
    Get external screen resolution and offset using xrandr.
    
    :param display_index: 0 for primary, 1 for secondary/external screen
    :return: Tuple of (width, height, x_offset, y_offset)
    """
    try:
        # Run xrandr command to get display information
        result = subprocess.check_output(['xrandr']).decode('utf-8')
        lines = result.strip().split('\n')
        
        displays = []
        current_display = 0
        
        for line in lines:
            if 'connected' in line:
                parts = line.split()
                display_name = parts[0]
                
                # Parse resolution and offset from lines like "HDMI-1 connected 1920x1080+1920+0"
                for part in parts:
                    if 'x' in part and '+' in part:
                        # Format: WIDTHxHEIGHT+XOFFSET+YOFFSET
                        res_part = part.split('+')[0]
                        width, height = map(int, res_part.split('x'))
                        x_offset = int(part.split('+')[1])
                        y_offset = int(part.split('+')[2])
                        displays.append((width, height, x_offset, y_offset))
                        current_display += 1
                        break
        
        # Sort by x_offset to ensure correct order (left to right)
        displays.sort(key=lambda x: x[2])
        
        if len(displays) > display_index:
            return displays[display_index]
        elif displays:
            print("Display index {} not found, using last display".format(display_index))
            return displays[-1]
        else:
            print("No displays detected with xrandr, using default secondary display")
            return (1920, 1080, 1920, 0)
            
    except Exception as e:
        print("Error detecting display info: {}. Using default secondary display".format(str(e)))
        return (1920, 1080, 1920, 0)


def get_image_files(images_dir):
    """
    Get all image files from the images directory.
    
    :param images_dir: Path to images directory
    :return: Sorted list of image file paths
    """
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp')
    image_files = []
    
    if not os.path.exists(images_dir):
        print("Error: Images directory not found: {}".format(images_dir))
        return []
    
    for filename in os.listdir(images_dir):
        if filename.lower().endswith(valid_extensions):
            image_files.append(os.path.join(images_dir, filename))
    
    # Sort to ensure consistent ordering
    image_files.sort()
    return image_files


def resize_and_save_images(image_files, trials_dir, target_width, target_height):
    """
    Resize images to target resolution and save them in trials directory.
    
    :param image_files: List of source image file paths
    :param trials_dir: Path to trials directory
    :param target_width: Target width for resized images
    :param target_height: Target height for resized images
    """
    # Create trials directory if it doesn't exist
    if not os.path.exists(trials_dir):
        os.makedirs(trials_dir)
        print("Created trials directory: {}".format(trials_dir))
    
    for idx, image_path in enumerate(image_files, start=1):
        try:
            # Open image
            img = Image.open(image_path)
            
            # Get original size
            orig_width, orig_height = img.size
            print("Processing {} - Original size: {}x{}".format(
                os.path.basename(image_path), orig_width, orig_height))
            
            # Resize image to target resolution
            # Using LANCZOS for high-quality downsampling
            resized_img = img.resize((target_width, target_height), Image.LANCZOS)
            
            # Convert to RGB if necessary (for PNG compatibility)
            if resized_img.mode in ('RGBA', 'LA', 'P'):
                # Keep transparency for RGBA/LA, convert palette images
                if resized_img.mode == 'P':
                    resized_img = resized_img.convert('RGBA')
            elif resized_img.mode not in ('RGB', 'RGBA'):
                resized_img = resized_img.convert('RGB')
            
            # Save resized image as PNG
            output_path = os.path.join(trials_dir, "trial{}.png".format(idx))
            resized_img.save(output_path, format='PNG')
            
            print("  -> Saved as {} ({}x{})".format(
                os.path.basename(output_path), target_width, target_height))
            
        except Exception as e:
            print("Error processing {}: {}".format(image_path, str(e)))


def main():
    """Main function to convert images from images folder to trials folder."""
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths
    images_dir = os.path.join(script_dir, "images")
    trials_dir = os.path.join(script_dir, "trials")
    
    print("=" * 60)
    print("Image Conversion Script")
    print("=" * 60)
    
    # Get external screen resolution
    screen_width, screen_height, x_offset, y_offset = get_display_info(display_index=1)
    print("External screen resolution: {}x{}".format(screen_width, screen_height))
    print()
    
    # Get all image files
    image_files = get_image_files(images_dir)
    
    if not image_files:
        print("No image files found in {}".format(images_dir))
        return
    
    print("Found {} image(s) in {}".format(len(image_files), images_dir))
    print()
    
    # Resize and save images
    resize_and_save_images(image_files, trials_dir, screen_width, screen_height)
    
    print()
    print("=" * 60)
    print("Conversion complete! {} image(s) processed.".format(len(image_files)))
    print("=" * 60)


if __name__ == "__main__":
    main()
