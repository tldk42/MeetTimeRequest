import requests
import datetime
import json
import os

# ==========================================
# [보안 설정] 깃허브 금고(Secrets)에서 주소를 가져옵니다.
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')
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
    # 웹훅 URL이 제대로 설정되었는지 확인
    if not DISCORD_WEBHOOK_URL:
        print("❌ 오류: 디스코드 웹훅 URL을 찾을 수 없습니다. Github Secrets 설정을 확인해주세요.")
        return

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
            
            # ID가 숨어있는 정확한 위치를 찾아갑니다
            room_id = None
            try:
                room_id = data['data']['meet']['_id']
            except (KeyError, TypeError):
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
            )

            discord_payload = {
                "content": (
                    f"📢 **{target_date} 수요 회의 시간 조율**\n"
                    f"매주 수요일 정기 알림입니다.\n\n"
                    f"👇 **아래 링크 클릭**\n{final_link}"
                )
            }
            
            print("📨 디스코드 전송 시도 중...")
            discord_res = requests.post(DISCORD_WEBHOOK_URL, json=discord_payload)
            
            if discord_res.status_code == 204:
                print("✅ 디스코드 전송 완료! (204 No Content)")
            else:
                print(f"❌ 디스코드 전송 실패! 상태 코드: {discord_res.status_code}")
                print(f"내용: {discord_res.text}")
            
        else:
            print(f"❌ 방 생성 실패 (Status: {response.status_code})")
            print(f"응답 본문: {response.text}")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    create_meeting_and_notify()
