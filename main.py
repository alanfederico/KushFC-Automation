import requests
import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime, timedelta
import numpy as np

# הגדרות
API_KEY = os.getenv('FOOTBALL_API_KEY')
BASE_URL = "https://api.football-data.org/v4/matches"
BG_PATH = "background.jpg"
FONT_PATH = "font.ttf"

# רשימת הליגות מסודרת לפי העדפה שלך: ספרד, אנגליה, איטליה, גרמניה, צרפת
LEAGUES_ORDER = [
    {'id': 2014, 'code': 'PD',  'name': 'La Liga'},
    {'id': 2021, 'code': 'PL',  'name': 'Premier League'},
    {'id': 2019, 'code': 'SA',  'name': 'Serie A'},
    {'id': 2002, 'code': 'BL1', 'name': 'Bundesliga'},
    {'id': 2015, 'code': 'FL1', 'name': 'Ligue 1'}
]

LEAGUE_LOGOS = {
    2014: 'https://crests.football-data.org/PD.png',
    2021: 'https://crests.football-data.org/PL.png',
    2019: 'https://crests.football-data.org/SA.png',
    2002: 'https://crests.football-data.org/BL1.png',
    2015: 'https://crests.football-data.org/FL1.png'
}

def get_recent_matches():
    headers = {'X-Auth-Token': API_KEY}
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    params = {'dateFrom': yesterday, 'dateTo': today}
    
    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get('matches', [])
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

def create_gradient_mask(size, alpha_max=50):
    width, height = size
    gradient = np.zeros((height, width), dtype=np.uint8)
    for x in range(width):
        dist_from_edge = min(x, width - 1 - x)
        center_width = width // 2
        opacity = int(alpha_max * (dist_from_edge / (center_width // 2))) if dist_from_edge < center_width // 2 else alpha_max
        gradient[:, x] = opacity
    return Image.fromarray(gradient, mode="L")

def create_posts():
    all_matches = get_recent_matches()
    if not all_matches:
        print("⚽ לא נמצאו משחקים מאתמול או מהיום.")
        return

    file_counter = 1 # מונה כדי לשמור על סדר הקבצים

    for league in LEAGUES_ORDER:
        league_matches = [m for m in all_matches if m['competition']['id'] == league['id'] and m['status'] == 'FINISHED']
        
        if not league_matches:
            print(f"ℹ️ אין תוצאות ל-{league['name']}, מדלג...")
            continue

        chunks = [league_matches[i:i + 5] for i in range(0, len(league_matches), 5)]
        liga_logo = get_image_from_url(LEAGUE_LOGOS[league['id']], size=(180, 180))

        for i, chunk in enumerate(chunks):
            img = Image.open(BG_PATH).convert("RGBA")
            overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            try:
                font_name = ImageFont.truetype(FONT_PATH, 38)
                font_score = ImageFont.truetype(FONT_PATH, 70)
                font_date = ImageFont.truetype(FONT_PATH, 22)
            except:
                font_name = font_score = font_date = ImageFont.load_default()

            if liga_logo:
                overlay.paste(liga_logo, (512 - 90, 90), liga_logo)

            box_height, y_gap = 140, 25
            total_h = (len(chunk) * box_height) + ((len(chunk)-1) * y_gap)
            y_pos = 675 - (total_h // 2)
            
            box_width = 880
            left_m = (1024 - box_width) // 2
            mask = create_gradient_mask((box_width, box_height))
            white_box = Image.new("RGBA", (box_width, box_height), (255, 255, 255, 255))

            for m in chunk:
                overlay.paste(white_box, (left_m, y_pos), mask)
                h_img = get_image_from_url(m['homeTeam']['crest'])
                a_img = get_image_from_url(m['awayTeam']['crest'])
                
                if h_img: overlay.paste(h_img, (left_m + 30, y_pos + 22), h_img)
                if a_img: overlay.paste(a_img, (left_m + box_width - 125, y_pos + 22), a_img)
                
                score = f"{m['score']['fullTime']['home']} - {m['score']['fullTime']['away']}"
                date_str = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y")
                
                draw.text((320, y_pos + 70), m['homeTeam']['shortName'], font=font_name, fill="white", anchor="mm")
                draw.text((512, y_pos + 60), score, font=font_score, fill="white", anchor="mm")
                draw.text((512, y_pos + 115), date_str, font=font_date, fill="white", anchor="mm")
                draw.text((704, y_pos + 70), m['awayTeam']['shortName'], font=font_name, fill="white", anchor="mm")
                
                y_pos += box_height + y_gap

            # שם הקובץ יכלול מספר סידורי כדי לשמור על הסדר: 01_PD, 02_PL וכו'
            filename = f"{file_counter:02d}_{league['code']}_{i+1}.jpg"
            final = Image.alpha_composite(img, overlay).convert("RGB")
            final.save(filename)
            print(f"✅ נוצר פוסט: {filename}")
            file_counter += 1

if __name__ == "__main__":
    create_posts()
