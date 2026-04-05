import requests
import os
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

# הגדרות API מתוך ה-Secrets של GitHub
API_KEY = os.getenv('FOOTBALL_API_KEY')
BASE_URL = "https://api.football-data.org/v4/matches"

def get_matches():
    if not API_KEY:
        print("❌ Error: FOOTBALL_API_KEY is missing!")
        return []
    
    headers = {'X-Auth-Token': API_KEY}
    # בודקים את המשחקים של היום
    today = datetime.now().strftime('%Y-%m-%d')
    
    try:
        response = requests.get(BASE_URL, headers=headers, params={"dateFrom": today, "dateTo": today})
        if response.status_code == 200:
            return response.json().get('matches', [])
        else:
            print(f"❌ API Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return []

def create_branded_image(match):
    try:
        # פתיחת הרקע
        img = Image.open("background.jpg")
        draw = ImageDraw.Draw(img)
        
        # הגדרת נתוני המשחק
        home = match['homeTeam']['shortName']
        away = match['awayTeam']['shortName']
        score = f"{match['score']['fullTime']['home']} - {match['score']['fullTime']['away']}"
        league = match['competition']['name']
        
        # טקסט לעיצוב
        result_text = f"{home} {score} {away}"
        
        # הערה: בשלב זה נשתמש בפונט ברירת מחדל. 
        # בעתיד נוכל להוסיף קובץ פונט מעוצב לתיקייה.
        draw.text((50, 50), f"KushFC Updates", fill="white")
        draw.text((50, 150), league, fill="yellow")
        draw.text((50, 250), result_text, fill="white")
        
        output_path = f"results_{match['id']}.jpg"
        img.save(output_path)
        print(f"✅ Image created: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ Image Error: {e}")
        return None

if __name__ == "__main__":
    matches = get_matches()
    if matches:
        print(f"Found {len(matches)} matches. Generating images...")
        for m in matches[:3]: # ניצור תמונות ל-3 המשחקים הראשונים
            create_branded_image(m)
    else:
        print("No matches found for today.")
