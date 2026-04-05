import requests
import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
import numpy as np

# הגדרות
API_KEY = os.getenv('FOOTBALL_API_KEY')
BASE_URL = "https://api.football-data.org/v4/matches"
BG_PATH = "background.jpg"
FONT_PATH = "font.ttf"
LA_LIGA_LOGO_URL = "https://crests.football-data.org/PD.png"

def get_la_liga_finished_matches():
    headers = {'X-Auth-Token': API_KEY}
    try:
        response = requests.get(BASE_URL, headers=headers)
        if response.status_code == 200:
            all_matches = response.json().get('matches', [])
            return [m for m in all_matches if m['competition']['id'] == 2014 and m['status'] == 'FINISHED']
        return []
    except:
        return []

def get_image_from_url(url, size=(95, 95)):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        img.thumbnail(size, Image.Resampling.LANCZOS)
        return img
    except:
        return None

def create_gradient_mask(size, alpha_max=55):
    width, height = size
    gradient = np.zeros((height, width), dtype=np.uint8)
    for x in range(width):
        dist_from_edge = min(x, width - 1 - x)
        center_width = width // 2
        if dist_from_edge > center_width // 2:
             opacity = alpha_max
        else:
             opacity = int(alpha_max * (dist_from_edge / (center_width // 2)))
        gradient[:, x] = opacity
    return Image.fromarray(gradient, mode="L")

def create_carousel():
    matches = get_la_liga_finished_matches()
    if not matches:
        print("⚠️ לא נמצאו משחקים שהסתיימו.")
        return

    chunks = [matches[i:i + 5] for i in range(0, len(matches), 5)]
    # הגדלת לוגו הליגה ל-140
    liga_logo = get_image_from_url(LA_LIGA_LOGO_URL, size=(140, 140))
    
    for i, chunk in enumerate(chunks):
        img = Image.open(BG_PATH).convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay)
        
        try:
            font_name = ImageFont.truetype(FONT_PATH, 38)
            font_score = ImageFont.truetype(FONT_PATH, 70)
            font_date = ImageFont.truetype(FONT_PATH, 22)
        except:
            font_name = font_score = font_date = ImageFont.load_default()

        if liga_logo:
            # מיקום הלוגו המוגדל (מרכז ב-512, גובה 100)
            overlay.paste(liga_logo, (512 - 70, 100), liga_logo)

        y_pos = 350
        box_width = 880
        box_height = 140
        left_margin = (1024 - box_width) // 2 
        
        gradient_mask = create_gradient_mask((box_width, box_height), alpha_max=50)
        white_box = Image.new("RGBA", (box_width, box_height), (255, 255, 255, 255))
        
        for m in chunk:
            overlay.paste(white_box, (left_margin, y_pos), gradient_mask)
            
            home_img = get_image_from_url(m['homeTeam']['crest'])
            away_img = get_image_from_url(m['awayTeam']['crest'])
            
            if home_img:
                overlay.paste(home_img, (left_margin + 30, y_pos + 22), home_img)
            if away_img:
                overlay.paste(away_img, (left_margin + box_width - 125, y_pos + 22), away_img)
            
            home_name = m['homeTeam']['shortName']
            away_name = m['awayTeam']['shortName']
            score = f"{m['score']['fullTime']['home']} - {m['score']['fullTime']['away']}"
            
            match_date = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y")
            
            center_x = 512
            # שם קבוצת בית - מוזז שמאלה למניעת חפיפה
            draw_overlay.text((320, y_pos + 70), home_name, font=font_name, fill="white", anchor="mm")
            
            # תוצאה
            draw_overlay.text((center_x, y_pos + 60), score, font=font_score, fill="white", anchor="mm")
            
            # תאריך
            draw_overlay.text((center_x, y_pos + 115), match_date, font=font_date, fill="white", anchor="mm")
            
            # שם קבוצת חוץ - מוזז ימינה למניעת חפיפה
            draw_overlay.text((704, y_pos + 70), away_name, font=font_name, fill="white", anchor="mm")
            
            y_pos += box_height + 25
            
        final_img = Image.alpha_composite(img, overlay).convert("RGB")
        filename = f"la_liga_post_{i+1}.jpg"
        final_img.save(filename)
        print(f"✅ נוצר פוסט עם לוגו מוגדל ותאריך: {filename}")

if __name__ == "__main__":
    create_carousel()
