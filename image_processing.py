import re

def can_process_image(image_path):
    # Basic check: You might want to add more sophisticated checks here,
    # like verifying the file type or image dimensions.
    return True  # For now, assume all images can be processed

def extract_text_from_region(image_path, region_coords):
    # Placeholder: In a real implementation, this would use OCR to
    # extract text from the specified region of the image.
    print(f"Simulating text extraction from {image_path} at {region_coords}")
    # Replace with actual OCR logic
    if region_coords == "top_right":
        return "SN12345_PN67890"  # Example composite_snpn
    elif region_coords == "bottom_center":
        return "Failure: Motor Overload"  # Example raw_failure
    else:
        return ""

def separate_sn_pn(composite_snpn):
    match = re.match(r"(.*?)\_(.*?)", composite_snpn)
    if match:
        return match.group(1), match.group(2)
    else:
        return None, None