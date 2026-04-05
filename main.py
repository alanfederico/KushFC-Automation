import requests
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
from datetime import datetime
import numpy as np

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

def get_image_from_url(url, size=(100, 100)): # הגדלת גודל ברירת המחדל של הלוגואים
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        img.thumbnail(size, Image.Resampling.LANCZOS)
        return img
    except:
        return None

def create_gradient_mask(size, alpha_max=40):
    """ יוצר מסיכת גרדיאנט לבנה חצי שקופה שהופכת לשקופה לגמרי בצדדים """
    width, height = size
    mask = Image.new("L", size, 0)
    
    # הגדרת מעבר מלבן מלא (במרכז) לשקוף (בצדדים)
    gradient = np.zeros((height, width), dtype=np.uint8)
    for x in range(width):
        # חישוב שקיפות: 0 בצדדים, עולה למרכז
        dist_from_edge = min(x, width - 1 - x)
        center_width = width // 2
        
        if dist_from_edge > center_width // 2: # חלק מרכזי מלא
             opacity = alpha_max
        else: # מעבר לשקוף
             opacity = int(alpha_max * (dist_from_edge / (center_width // 2)))
        
        gradient[:, x] = opacity

    mask = Image.fromarray(gradient, mode="L")
    return mask

def create_carousel():
    matches = get_la_liga_finished_matches()
    if not matches:
        print("⚠️ לא נמצאו משחקים שהסתיימו מהיום בליגה הספרדית.")
        return

    # חלוקה ל-5 משחקים לעמוד
    chunks = [matches[i:i + 5] for i in range(0, len(matches), 5)]
    
    # הורדת לוגו הליגה מראש
    liga_logo = get_image_from_url(LA_LIGA_LOGO_URL, size=(120, 120)) # לוגו ליגה גדול יותר
    
    for i, chunk in enumerate(chunks):
        img = Image.open(BG_PATH).convert("RGBA")
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay)
        
        # טעינת פונטים (הגדלת הגדלים ל-45 ו-75)
        try:
            font_main = ImageFont.truetype(FONT_PATH, 45) # הגדלה
            font_score = ImageFont.truetype(FONT_PATH, 75) # הגדלה
        except:
            font_main = font_score = ImageFont.load_default()

        # 1. הוספת לוגו לה-ליגה למעלה במרכז (נקי, בלי טקסט)
        if liga_logo:
            # מיקום הלוגו לבד
            overlay.paste(liga_logo, (452, 120), liga_logo)

        # 2. יצירת התיבות הלבנות עם אפקט גרדיאנט
        y_pos = 350
        box_width = 850 # הגדלת רוחב התיבה כדי להכיל לוגואים גדולים יותר
        box_height = 130 # הגדלת גובה התיבה
        left_margin = (1024 - box_width) // 2 
        
        # יצירת מסיכת הגרדיאנט מראש
        gradient_mask = create_gradient_mask((box_width, box_height), alpha_max=50) # מעט יותר שקוף (20%)
        white_box = Image.new("RGBA", (box_width, box_height), (255, 255, 255, 255))
        
        for m in chunk:
            # הדבקת המלבן הלבן עם מסיכת הגרדיאנט על ה-Overlay
            overlay.paste(white_box, (left_margin, y_pos), gradient_mask)
            
            # הורדת לוגואים גדולים יותר
            home_img = get_image_from_url(m['homeTeam']['crest'], size=(90, 90)) # הגדלה
            away_img = get_image_from_url(m['awayTeam']['crest'], size=(90, 90)) # הגדלה
            
            # הדבקת לוגואים (הגדלת המיקומים בהתאם)
            if home_img:
                overlay.paste(home_img, (left_margin + 40, y_pos + 20), home_img)
            if away_img:
                overlay.paste(away_img, (left_margin + box_width - 130, y_pos + 20), away_img)
            
            # הגדרות נתונים
            home_name = m['homeTeam']['shortName']
            away_name = m['awayTeam']['shortName']
            score = f"{m['score']['fullTime']['home']} - {m['score']['fullTime']['away']}"
            
            # הדפסת טקסט במרכז (תיקון מיקומים לטקסט מוגדל)
            # קבוצת בית (anchor="rm")
            draw_overlay.text((left_margin + 360, y_pos + 65), home_name, font=font_main, fill="white", anchor="rm")
            
            # תוצאה (anchor="mm")
            draw_overlay.text((512, y_pos + 65), score, font=font_score, fill="white", anchor="mm")
            
            # קבוצת חוץ (anchor="lm")
            draw_overlay.text((left_margin + box_width - 360, y_pos + 65), away_name, font=font_main, fill="white", anchor="lm")
            
            y_pos += box_height + 20 # רווח לשורה הבאה
            
        final_img = Image.alpha_composite(img, overlay).convert("RGB")
        filename = f"la_liga_post_{i+1}.jpg"
        final_img.save(filename)
        print(f"✅ נוצר עמוד מעוצב ותקין: {filename}")

if __name__ == "__main__":
    create_carousel()
