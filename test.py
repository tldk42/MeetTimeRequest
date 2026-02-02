import requests
import datetime
import json

# ==========================================
# [설정 구역] 아래 주소를 본인의 디스코드 웹훅 URL로 바꿔주세요
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1467905849442959564/ckjFHrZ2fgE9mdaFIbCzIolho7boUjS1LcmmUfT-a9TDlataETSFXHN3k0s1QkMpy9fQ"
# ==========================================

def get_next_wednesday():
    """오늘 기준으로 돌아오는 수요일 날짜를 계산합니다."""
    today = datetime.date.today()
    # 월(0), 화(1), 수(2)...
    # 수요일(2) - 오늘요일 = 며칠 남았는지 계산
    days_ahead = 2 - today.weekday()
    if days_ahead <= 0:  # 오늘이 수요일이거나 이미 지났으면 다음 주 수요일로
        days_ahead += 7
    next_wed = today + datetime.timedelta(days=days_ahead)
    return next_wed.strftime("%Y-%m-%d")

def create_meeting_and_notify():
    target_date = get_next_wednesday()
    print(f"📅 목표 날짜: {target_date}")

    # 1. 방 생성 요청 (보내주신 cURL 기반)
    api_url = "https://inspiration-quotes.fly.dev/api/meettime/new"
    
    payload = {
        "title": "회의",        # 제목
        "startDate": target_date,
        "endDate": target_date,
        "startTime": 9,         # 오전 9시
        "endTime": 24           # 자정 (24시)
    }

    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'origin': 'https://wemeettime.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        
        if response.status_code in [200, 201]:
            # 응답에서 ID 추출 (MongoDB ID 형식으로 추정)
            # 보통 {'_id': '...', ...} 또는 {'id': '...'} 형태로 옵니다.
            data = response.json()
            
            # ID를 찾기 위한 안전장치
            room_id = data.get('_id') or data.get('id') or data.get('insertedId')
            
            if not room_id:
                print(f"❌ ID 추출 실패. 응답 데이터: {data}")
                return

            # 2. 최종 링크 생성
            final_link = (
                f"https://wemeettime.com/create-result/{room_id}/"
                f"?title=%ED%9A%8C%EC%9D%98"  # '회의'를 URL 인코딩한 값
                f"&startDate={target_date}&endDate={target_date}"
                f"&startTime=9&endTime=24"
            )

            # 3. 디스코드 전송
            discord_payload = {
                "content": (
                    f"📢 **{target_date} 수요 회의 시간 조율**\n"
                    f"매주 수요일 정기 알림입니다. 09:00 ~ 24:00 사이 가능한 시간을 입력해주세요!\n\n"
                    f"👇 **아래 링크 클릭**\n{final_link}"
                )
            }
            requests.post(DISCORD_WEBHOOK_URL, json=discord_payload)
            print("✅ 디스코드 전송 완료!")
            
        else:
            print(f"❌ 방 생성 실패 (Status: {response.status_code})")
            print(response.text)

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    create_meeting_and_notify()
