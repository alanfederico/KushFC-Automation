import requests
import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime

# הגדרות
API_KEY = os.getenv('FOOTBALL_API_KEY')
BASE_URL = "https://api.football-data.org/v4/matches"
BG_PATH = "background.jpg"
FONT_PATH = "font.ttf" # וודא שיש לך קובץ פונט בשם זה ב-GitHub
LA_LIGA_LOGO_URL = "https://crests.football-data.org/PD.png" # לוגו לה ליגה

def get_la_liga_finished_matches():
    headers = {'X-Auth-Token': API_KEY}
    try:
        response = requests.get(BASE_URL, headers=headers)
        if response.status_code == 200:
            all_matches = response.json().get('matches', [])
            # סינון: רק ליגה ספרדית (2014) ורק משחקים שהסתיימו (FINISHED)
            return [m for m in all_matches if m['competition']['id'] == 2014 and m['status'] == 'FINISHED']
        return []
    except:
        return []

def get_image_from_url(url, size=(80, 80)):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        img.thumbnail(size, Image.Resampling.LANCZOS)
        return img
    except:
        return None

def draw_round_rectangle(draw, xy, corner_radius, fill_color):
    """ מצייר מלבן עם פינות מעוגלות חצי שקוף """
    draw.rounded_rectangle(xy, corner_radius, fill=fill_color, outline=None)

def create_carousel():
    matches = get_la_liga_finished_matches()
    if not matches:
        print("⚠️ לא נמצאו משחקים שהסתיימו מהיום בליגה הספרדית.")
        return

    # חלוקה ל-5 משחקים לעמוד
    chunks = [matches[i:i + 5] for i in range(0, len(matches), 5)]
    
    # הורדת לוגו הליגה מראש
    liga_logo = get_image_from_url(LA_LIGA_LOGO_URL, size=(100, 100))
    
    for i, chunk in enumerate(chunks):
        img = Image.open(BG_PATH).convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay)
        
        # טעינת פונטים (אם אין, משתמש בברירת מחדל)
        try:
            font_main = ImageFont.truetype(FONT_PATH, 40)
            font_score = ImageFont.truetype(FONT_PATH, 65)
        except:
            font_main = font_score = ImageFont.load_default()

        # 1. הוספת לוגו לה-ליגה למעלה במרכז
        if liga_logo:
            overlay.paste(liga_logo, (460, 150), liga_logo) # כוונון מיקום
            draw_overlay.text((512, 270), "La Liga Results", font=font_main, fill="white", anchor="mm")

        # 2. יצירת התיבות הלבנות חצי-שקופות עבור כל משחק
        y_pos = 350
        box_width = 800
        box_height = 110
        left_margin = (1024 - box_width) // 2 # 112 פיקסלים מהצד
        
        for m in chunk:
            draw_round_rectangle(draw_overlay, (left_margin, y_pos, left_margin + box_width, y_pos + box_height), 15, (255, 255, 255, 30)) # '30' זה ה-Opacity (12%)
            
            # הורדת לוגואים של הקבוצות
            home_logo_url = m['homeTeam']['crest']
            away_logo_url = m['awayTeam']['crest']
            home_img = get_image_from_url(home_logo_url)
            away_img = get_image_from_url(away_logo_url)
            
            # הדבקת לוגואים
            if home_img:
                overlay.paste(home_img, (left_margin + 50, y_pos + 15), home_img)
            if away_img:
                overlay.paste(away_img, (left_margin + box_width - 130, y_pos + 15), away_img)
            
            # הגדרות נתונים
            home_name = m['homeTeam']['shortName']
            away_name = m['awayTeam']['shortName']
            score = f"{m['score']['fullTime']['home']} - {m['score']['fullTime']['away']}"
            
            # הדפסת טקסט במרכז
            draw_overlay.text((512, y_pos + 45), home_name, font=font_main, fill="white", anchor="rm")
            draw_overlay.text((512, y_pos + 45), score, font=font_score, fill="white", anchor="mm")
            draw_overlay.text((512, y_pos + 45), away_name, font=font_main, fill="white", anchor="lm")
            
            y_pos += box_height + 20 # רווח לשורה הבאה
            
        # שילוב ה-Overlay על הרקע
        final_img = Image.alpha_composite(img, overlay).convert("RGB")
        filename = f"la_liga_post_{i+1}.jpg"
        final_img.save(filename)
        print(f"✅ נוצר עמוד מעוצב: {filename}")

if __name__ == "__main__":
    create_carousel()
