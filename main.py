import requests
import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# הגדרות
API_KEY = os.getenv('FOOTBALL_API_KEY')
BASE_URL = "https://api.football-data.org/v4/matches"
BG_PATH = "background.jpg"
FONT_PATH = "font.ttf" # וודא שהעלית את קובץ הפונט שלך ל-GitHub

def get_la_liga_results():
    headers = {'X-Auth-Token': API_KEY}
    # שליחת בקשה למשחקים של היום/אתמול
    try:
        response = requests.get(BASE_URL, headers=headers)
        if response.status_code == 200:
            all_matches = response.json().get('matches', [])
            # סינון לליגה הספרדית (ID: 2014)
            return [m for m in all_matches if m['competition']['id'] == 2014]
        return []
    except:
        return []

def create_carousel():
    matches = get_la_liga_results()
    if not matches:
        print("⚠️ לא נמצאו משחקים של הליגה הספרדית כרגע.")
        return

    # חלוקה ל-5 משחקים לעמוד
    chunks = [matches[i:i + 5] for i in range(0, len(matches), 5)]
    
    for i, chunk in enumerate(chunks):
        img = Image.open(BG_PATH)
        draw = ImageDraw.Draw(img)
        
        # טעינת פונט (אם אין, משתמש בברירת מחדל)
        try:
            font = ImageFont.truetype(FONT_PATH, 45)
        except:
            font = ImageFont.load_default()

        y_pos = 350
        for m in chunk:
            home = m['homeTeam']['shortName']
            away = m['awayTeam']['shortName']
            score = f"{m['score']['fullTime']['home']} - {m['score']['fullTime']['away']}"
            
            # כתיבת התוצאה במרכז
            text = f"{home}   {score}   {away}"
            draw.text((540, y_pos), text, font=font, fill="white", anchor="mm")
            y_pos += 130 # רווח לשורה הבאה
            
        filename = f"results_page_{i+1}.jpg"
        img.save(filename)
        print(f"✅ נוצר עמוד: {filename}")

if __name__ == "__main__":
    create_carousel()
