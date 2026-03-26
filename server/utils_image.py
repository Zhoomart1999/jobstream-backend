from PIL import Image, ImageDraw, ImageFont
import os

def generate_instagram_card(vacancy_title, salary, company_name, output_path, logo_path=None):
    # Standard Instagram Post size 1080x1080 (1:1) or Stories 1080x1920 (9:16)
    # We'll default to 1080x1080 for this example
    width, height = 1080, 1080
    background_color = (30, 30, 30)  # Dark gray
    text_color = (255, 255, 255)
    accent_color = (0, 255, 127)  # Spring Green
    
    img = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(img)
    
    # Try to load a font, fallback to default
    try:
        font_title = ImageFont.truetype("Arial.ttf", 80)
        font_details = ImageFont.truetype("Arial.ttf", 50)
    except:
        font_title = ImageFont.load_default()
        font_details = ImageFont.load_default()
    
    # Add Title
    draw.text((width//2, height//3), vacancy_title, fill=text_color, font=font_title, anchor="mm")
    
    # Add Salary
    draw.rectangle([width//4, height//2 - 60, 3*width//4, height//2 + 60], outline=accent_color, width=5)
    draw.text((width//2, height//2), f"Зарплата: {salary}", fill=accent_color, font=font_details, anchor="mm")
    
    # Add Branding
    draw.text((width//2, 4*height//5), "JobStream Platform", fill=(200, 200, 200), font=font_details, anchor="mm")
    
    # Save image
    img.save(output_path)
    return output_path
