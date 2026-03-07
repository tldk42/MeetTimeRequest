import requests
import datetime
import json
import os

# 1. 깃허브 금고에서 시놀로지 주소 꺼내오기 (이름 변경됨)
SYNOLOGY_WEBHOOK_URL = os.environ.get('SYNOLOGY_WEBHOOK_URL')

def get_upcoming_weekend():
    """오늘(수요일) 기준으로 돌아오는 토요일, 일요일 날짜를 계산합니다."""
    today = datetime.date.today()
    
    days_until_sat = 5 - today.weekday()
    if days_until_sat <= 0:
        days_until_sat += 7
        
    next_sat = today + datetime.timedelta(days=days_until_sat)
    next_sun = next_sat + datetime.timedelta(days=1)
    
    return next_sat.strftime("%Y-%m-%d"), next_sun.strftime("%Y-%m-%d")

def create_meeting_and_notify():
    # 주소가 잘 들어왔는지 확인
    if not SYNOLOGY_WEBHOOK_URL:
        print("❌ 오류: 웹훅 주소가 없습니다. schedule.yml 파일의 env 설정을 확인하세요.")
        return

    sat_date, sun_date = get_upcoming_weekend()
    print(f"📅 목표 날짜: {sat_date} (토) ~ {sun_date} (일)")

    api_url = "https://inspiration-quotes.fly.dev/api/meettime/new"
    
    payload = {
        "title": "주말 회의",
        "startDate": sat_date,
        "endDate": sun_date,
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
        response = requests.post(api_url, json=payload, headers=headers)
        
        if response.status_code in [200, 201]:
            data = response.json()
            
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
                f"?title=%EC%A3%BC%EB%A7%90%20%ED%9A%8C%EC%9D%98" 
                f"&startDate={sat_date}&endDate={sun_date}"
                f"&startTime=9&endTime=24"
            )

            # [변경됨] 1. 시놀로지 규격에 맞게 'text' 키 사용
            synology_payload = {
                "text": (
                    f"📢 **{sat_date} ~ {sun_date} 주말 회의 시간 조율**\n"
                    f"이번 주 토/일 가능한 시간을 입력해주세요! (09:00 ~ 24:00)\n\n"
                    f"👇 **아래 링크 클릭**\n{final_link}"
                )
            }
            
            # [변경됨] 2. payload=... 형태로 전송하기 위한 데이터 포장
            # requests 모듈에서 data 파라미터를 쓰면 자동으로 application/x-www-form-urlencoded로 전송됩니다.
            form_data = {
                "payload": json.dumps(synology_payload)
            }
            
            print("📨 시놀로지 챗으로 전송 시도 중...")
            chat_res = requests.post(SYNOLOGY_WEBHOOK_URL, data=form_data)
            
            # 시놀로지는 보통 성공 시 200 코드를 반환합니다.
            if chat_res.status_code in [200, 201]:
                print("✅ 시놀로지 챗 전송 완료!")
            else:
                print(f"❌ 시놀로지 챗 전송 실패: {chat_res.status_code}")
                print(f"내용: {chat_res.text}")
            
        else:
            print(f"❌ 방 생성 실패: {response.status_code}")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    create_meeting_and_notify()
