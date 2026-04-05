import requests
import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# הגדרות
API_KEY = os.getenv('FOOTBALL_API_KEY')
BASE_URL = "https://api.football-data.org/v4/matches"
FONT_PATH = "font.ttf" # וודא שהעלית קובץ כזה
BG_PATH = "background.jpg"

def get_la_liga_matches():
    headers = {'X-Auth-Token': API_KEY}
    # סינון לליגה הספרדית (PD) וטווח תאריכים (למשל השבוע האחרון)
    params = {"competitions": "PD"} 
    res = requests.get(BASE_URL, headers=headers, params=params)
    return res.json().get('matches', []) if res.status_code == 200 else []

def draw_match_row(draw, match, y_pos, font_main, font_score):
    home = match['homeTeam']['shortName']
    away = match['awayTeam']['shortName']
    score = f"{match['score']['fullTime']['home']} - {match['score']['fullTime']['away']}"
    
    # מיקומים (לפי הרקע שלך - כדאי לכוונן)
    draw.text((250, y_pos), home, font=font_main, fill="white", anchor="rm")
    draw.text((512, y_pos), score, font=font_score, fill="white", anchor="mm")
    draw.text((774, y_pos), away, font=font_main, fill="white", anchor="lm")

def create_carousel():
    matches = get_la_liga_matches()
    if not matches:
        print("No matches found.")
        return

    # חלוקה לקבוצות של 5
    chunked_matches = [matches[i:i + 5] for i in range(0, len(matches), 5)]
    
    for page_index, chunk in enumerate(chunked_matches):
        img = Image.open(BG_PATH)
        draw = ImageDraw.Draw(img)
        
        # טעינת פונטים
        try:
            f_main = ImageFont.truetype(FONT_PATH, 40)
            f_score = ImageFont.truetype(FONT_PATH, 60)
        except:
            f_main = f_score = ImageFont.load_default()

        y_start = 300 # להתחיל לצייר מגובה 300 פיקסלים
        for match in chunk:
            draw_match_row(draw, match, y_start, f_main, f_score)
            y_start += 120 # רווח בין שורות
            
        img.save(f"kushfc_post_{page_index + 1}.jpg")
        print(f"✅ Created page {page_index + 1}")

if __name__ == "__main__":
    create_carousel()
