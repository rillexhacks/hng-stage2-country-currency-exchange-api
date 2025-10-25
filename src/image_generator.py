from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timezone
import os

def generate_summary_image(total_countries: int, top_countries: list, cache_dir: str = "cache"):
    """
    Generate a summary image with country statistics.
    
    Args:
        total_countries: Total number of countries in database
        top_countries: List of tuples (name, estimated_gdp)
        cache_dir: Directory to save the image
    """
    # Create cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)
    
    # Image dimensions
    width = 800
    height = 600
    
    # Create image with white background
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a better font, fall back to default if not available
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Colors
    title_color = (25, 25, 112)  # Midnight blue
    header_color = (70, 130, 180)  # Steel blue
    text_color = (50, 50, 50)  # Dark gray
    border_color = (200, 200, 200)  # Light gray
    
    # Draw border
    draw.rectangle([10, 10, width-10, height-10], outline=border_color, width=3)
    
    # Title
    title = "Country Data Summary"
    draw.text((50, 40), title, fill=title_color, font=title_font)
    
    # Total countries
    total_text = f"Total Countries: {total_countries}"
    draw.text((50, 100), total_text, fill=text_color, font=header_font)
    
    # Top 5 countries header
    draw.text((50, 160), "Top 5 Countries by Estimated GDP:", fill=header_color, font=header_font)
    
    # Draw top countries
    y_position = 210
    for idx, (name, gdp) in enumerate(top_countries, 1):
        if gdp is not None:
            gdp_formatted = f"${gdp:,.2f}"
        else:
            gdp_formatted = "N/A"
        
        country_text = f"{idx}. {name}: {gdp_formatted}"
        draw.text((70, y_position), country_text, fill=text_color, font=text_font)
        y_position += 40
    
    # Timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    timestamp_text = f"Last Refreshed: {timestamp}"
    draw.text((50, height - 60), timestamp_text, fill=text_color, font=small_font)
    
    # Save image
    image_path = os.path.join(cache_dir, "summary.png")
    image.save(image_path)
    
    return image_path