import requests
import datetime
import json
import os

# 1. 깃허브 금고에서 주소 꺼내오기
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

def get_upcoming_weekend():
    """오늘(수요일) 기준으로 돌아오는 토요일, 일요일 날짜를 계산합니다."""
    today = datetime.date.today()
    
    # 토요일(5)까지 며칠 남았는지 계산
    # 수요일(2) 기준: 5 - 2 = 3일 뒤가 토요일
    days_until_sat = 5 - today.weekday()
    if days_until_sat <= 0: # 이미 지났으면 다음주 토요일로
        days_until_sat += 7
        
    next_sat = today + datetime.timedelta(days=days_until_sat)
    next_sun = next_sat + datetime.timedelta(days=1) # 일요일은 토요일 + 1일
    
    return next_sat.strftime("%Y-%m-%d"), next_sun.strftime("%Y-%m-%d")

def create_meeting_and_notify():
    # 주소가 잘 들어왔는지 확인
    if not DISCORD_WEBHOOK_URL:
        print("❌ 오류: 웹훅 주소가 없습니다. schedule.yml 파일의 env 설정을 확인하세요.")
        return

    # 주말 날짜 가져오기
    sat_date, sun_date = get_upcoming_weekend()
    print(f"📅 목표 날짜: {sat_date} (토) ~ {sun_date} (일)")

    api_url = "https://inspiration-quotes.fly.dev/api/meettime/new"
    
    payload = {
        "title": "주말 회의",    # 제목 변경
        "startDate": sat_date,  # 시작: 토요일
        "endDate": sun_date,    # 끝: 일요일
        "startTime": 9,         # 9시
        "endTime": 24           # 24시
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
            data = response.json()
            
            # ID 찾기
            room_id = None
            try:
                room_id = data['data']['meet']['_id']
            except (KeyError, TypeError):
                pass

            if not room_id:
                print(f"❌ ID 추출 실패. 응답 데이터: {data}")
                return

            print(f"✅ 방 생성 성공! ID: {room_id}")

            # 링크에도 토~일 기간 적용
            final_link = (
                f"https://wemeettime.com/create-result/{room_id}/"
                f"?title=%EC%A3%BC%EB%A7%90%20%ED%9A%8C%EC%9D%98" 
                f"&startDate={sat_date}&endDate={sun_date}"
                f"&startTime=9&endTime=24"
            )

            discord_payload = {
                "content": (
                    f"📢 **{sat_date} ~ {sun_date} 주말 회의 시간 조율**\n"
                    f"이번 주 토/일 가능한 시간을 입력해주세요! (09:00 ~ 24:00)\n\n"
                    f"👇 **아래 링크 클릭**\n{final_link}"
                )
            }
            
            discord_res = requests.post(DISCORD_WEBHOOK_URL, json=discord_payload)
            
            if discord_res.status_code == 204:
                print("✅ 디스코드 전송 완료!")
            else:
                print(f"❌ 디스코드 전송 실패: {discord_res.status_code}")
            
        else:
            print(f"❌ 방 생성 실패: {response.status_code}")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    create_meeting_and_notify()
