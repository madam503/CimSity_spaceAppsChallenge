import earthaccess
import datetime # 날짜 계산을 위해 datetime 라이브러리를 추가합니다.

# --- 1. 검색 조건 설정 ---

# 검색 지역: 대한민국 제주특별자치도 제주시
# 형식: [서쪽 경도, 남쪽 위도, 동쪽 경도, 북쪽 위도]
jeju_city_bbox = (126.1, 33.2, 126.9, 33.6)

# 검색 기간: 오늘을 기준으로 최근 30일
# 오늘 날짜를 가져옵니다.
end_date = datetime.datetime.now()
# 오늘로부터 30일 전 날짜를 계산합니다.
start_date = end_date - datetime.timedelta(days=365)
# API가 요구하는 'YYYY-MM-DD' 형식으로 날짜를 변환합니다.
temporal_range = (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

# 검색할 데이터: ICESat-2 육지/수목 높이 데이터 (이전에 분석하던 데이터)
# 만약 지표면 반사율 데이터를 원하시면 'VNP09GA'로 변경하세요.
short_name = 'ATL08'

# --- 2. 데이터 검색 및 다운로드 ---

# Earthdata 로그인 (.netrc 파일이 있으면 자동으로 처리됩니다)
earthaccess.login()

print(f"로그인 성공! 데이터 검색을 시작합니다...")
print(f"검색 지역: 제주시")
print(f"검색 기간: {temporal_range[0]} ~ {temporal_range[1]}")

# 설정된 조건으로 데이터 검색
results = earthaccess.search_data(
    short_name=short_name,
    bounding_box=jeju_city_bbox,
    temporal=temporal_range
)

# --- 3. 결과 확인 및 다운로드 ---

if not results:
    print("해당 조건에 맞는 데이터를 찾지 못했습니다.")
else:
    # 검색된 데이터의 개수와 첫 번째 결과의 정보를 출력
    print(f"\n총 {len(results)}개의 데이터를 찾았습니다.")
    print("첫 번째 검색 결과:", results[0])

    # 검색된 모든 데이터를 './data_jeju_recent' 폴더에 다운로드합니다.
    print("\n다운로드를 시작합니다...")
    file_paths = earthaccess.download(results, local_path="./data_jeju_recent")
    print(f"다운로드 완료! 총 {len(file_paths)}개의 파일이 저장되었습니다.")