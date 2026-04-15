def get_recent_matches():
    headers = {'X-Auth-Token': API_KEY}
    
    # שימוש ב-UTC כדי להתאים לשרת של ה-API
    now_utc = datetime.utcnow()
    today_utc = now_utc.strftime('%Y-%m-%d')
    three_days_ago_utc = (now_utc - timedelta(days=2)).strftime('%Y-%m-%d')
    
    params = {'dateFrom': three_days_ago_utc, 'dateTo': today_utc}
    
    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        if response.status_code == 200:
            matches = response.json().get('matches', [])
            # הדפסה קטנה לדיבאג כדי שתראה כמה משחקים חזרו בכלל
            print(f"DEBUG: Found {len(matches)} matches total in API response.")
            return matches
        return []
    except Exception as e:
        print(f"Error fetching matches: {e}")
        return []

# ... (שאר הפונקציות ללא שינוי)

def create_posts():
    all_matches = get_recent_matches()
    if not all_matches:
        print("⚽ לא נמצאו משחקים.")
        return

    file_counter = 1
    for league in LEAGUES_ORDER:
        # עדכון הפילטר: לוקחים גם FINISHED וגם משחקים שהסתיימו אבל הסטטוס שלהם עוד לא התעדכן (כמו TIMED עם תוצאה)
        # הוספנו בדיקה שיש תוצאה (home is not None) כדי לא להכניס משחקים שעוד לא התחילו
        league_matches = [
            m for m in all_matches 
            if m['competition']['id'] == league['id'] 
            and (m['status'] in ['FINISHED', 'TIMED', 'REGULAR_TIME'])
            and m['score']['fullTime']['home'] is not None
        ]
        
        if not league_matches:
            continue

        # ... (שאר הקוד של יצירת התמונה ללא שינוי)
