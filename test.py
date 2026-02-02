import requests
import datetime
import json
import os

# ==========================================
# [설정 구역] 본인의 디스코드 웹훅 URL을 다시 넣어주세요!
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')\
# ==========================================

def get_next_wednesday():
    """오늘 기준으로 돌아오는 수요일 날짜를 계산합니다."""
    today = datetime.date.today()
    days_ahead = 2 - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_wed = today + datetime.timedelta(days=days_ahead)
    return next_wed.strftime("%Y-%m-%d")

def create_meeting_and_notify():
    target_date = get_next_wednesday()
    print(f"📅 목표 날짜: {target_date}")

    api_url = "https://inspiration-quotes.fly.dev/api/meettime/new"
    
    payload = {
        "title": "회의",
        "startDate": target_date,
        "endDate": target_date,
        "startTime": 9,
        "endTime": 24
    }

    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'origin': 'https://wemeettime.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'
    }

    try:
        print("🚀 방 생성 요청 보내는 중...")
        response = requests.post(api_url, json=payload, headers=headers)
        
        if response.status_code in [200, 201]:
            data = response.json()
            
            # [수정된 부분] ID가 숨어있는 정확한 위치를 찾아갑니다
            # 구조: {'data': {'meet': {'_id': '...'}}}
            room_id = None
            try:
                room_id = data['data']['meet']['_id']
            except (KeyError, TypeError):
                # 만약 구조가 또 바뀌었을 경우를 대비한 안전장치
                pass

            if not room_id:
                print(f"❌ ID 추출 실패. 응답 데이터: {data}")
                return

            print(f"✅ 방 생성 성공! ID: {room_id}")

            final_link = (
                f"https://wemeettime.com/create-result/{room_id}/"
                f"?title=%ED%9A%8C%EC%9D%98"
                f"&startDate={target_date}&endDate={target_date}"
                f"&startTime=9&endTime=24"
