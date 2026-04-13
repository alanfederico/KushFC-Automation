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

# רשימת הליגות מסודרת: ליגת האלופות, ספרד, אנגליה, איטליה, גרמניה, צרפת
LEAGUES_ORDER = [
    {'id': 2001, 'code': 'CL',  'name': 'Champions League'},
    {'id': 2014, 'code': 'PD',  'name': 'La Liga'},
    {'id': 2021, 'code': 'PL',  'name': 'Premier League'},
    {'id': 2019, 'code': 'SA',  'name': 'Serie A'},
    {'id': 2002, 'code': 'BL1', 'name': 'Bundesliga'},
    {'id': 2015, 'code': 'FL1', 'name': 'Ligue 1'}
]

LEAGUE_LOGOS = {
    2001: 'https://crests.football-data.org/CL.png',
    2014: 'https://crests.football-data.org/PD.png',
    2021: 'https://crests.football-data.org/PL.png',
    2019: 'https://crests.football-data.org/SA.png',
    2002: 'https://crests.football-data.org/BL1.png',
    2015: 'https://crests.football-data.org/FL1.png'
}

# תיקון ידני לשמות קבוצות בעייתיים
TEAM_NAME_OVERRIDES = {
    'Olympique Lyonnais': 'Lyon',
    'Paris Saint-Germain FC': 'PSG',
    'Wolverhampton Wanderers FC': 'Wolves',
    'Club Atlético de Madrid': 'Atletico',
    'Borussia Dortmund': 'BVB',
    'Manchester City FC': 'Man City',
    'FC Bayern München': 'Bayern'
}

def get_recent_matches():
    headers = {'X-Auth-Token': API_KEY}
    
    # תאריכים לשימוש חד פעמי: מה-10 באפריל ועד היום
    today = datetime.now().strftime('%Y-%m-%d')
    start_date = "2026-04-10" 
    
    params = {'dateFrom': start_date, 'dateTo': today}
    
    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get
