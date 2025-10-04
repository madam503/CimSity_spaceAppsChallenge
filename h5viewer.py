import os
import h5py
import pandas as pd
import glob

# --- 1. 설정 ---
# H5 파일이 저장된 폴더 경로
data_directory = "./data_jeju_recent"
# 저장할 파일 이름 (확장자 제외)
output_filename = "jeju_atl08_analysis"


# --- 2. 모든 파일과 빔 트랙을 순회하며 데이터 추출 ---
print(f"'{data_directory}' 폴더에서 H5 파일 데이터를 추출합니다...")

# 추출한 데이터를 DataFrame 형태로 저장할 리스트
all_data_frames = []
# 처리할 위성 빔 트랙 목록
ground_tracks = ['gt1l', 'gt1r', 'gt2l', 'gt2r', 'gt3l', 'gt3r']

# 지정된 폴더에서 .h5 확장자를 가진 모든 파일 경로를 찾음
h5_files = glob.glob(os.path.join(data_directory, '*.h5'))

if not h5_files:
    print(f"오류: '{data_directory}' 폴더에 H5 파일이 없습니다.")
    exit()

# 각 H5 파일을 순회
for file_path in h5_files:
    filename = os.path.basename(file_path)
    try:
        with h5py.File(file_path, 'r') as f:
            # 각 파일 내의 6개 빔 트랙을 순회
            for track in ground_tracks:
                # 해당 트랙이 파일에 존재하는지 확인
                if f'{track}/land_segments' not in f:
                    continue
                
                # 필요한 데이터셋(파라미터)을 추출
                lon = f[f'{track}/land_segments/longitude'][:]
                lat = f[f'{track}/land_segments/latitude'][:]
                h_canopy = f[f'{track}/land_segments/canopy/h_canopy'][:]
                h_canopy_uncertainty = f[f'{track}/land_segments/canopy/h_canopy_uncertainty'][:]
                canopy_openness = f[f'{track}/land_segments/canopy/canopy_openness'][:]
                urban_flag = f[f'{track}/land_segments/urban_flag'][:]
                
                # 추출한 데이터로 DataFrame 생성
                df = pd.DataFrame({
                    'longitude': lon,
                    'latitude': lat,
                    'canopy_height_m': h_canopy,
                    'canopy_uncertainty_m': h_canopy_uncertainty,
                    'canopy_openness_percent': canopy_openness,
                    'urban_flag': urban_flag
                })
                
                # 전체 리스트에 현재 트랙의 DataFrame 추가
                all_data_frames.append(df)

    except Exception as e:
        print(f"'{filename}' 처리 중 오류 발생: {e}")

# --- 3. 모든 데이터를 하나의 DataFrame으로 통합 및 정리 ---
if not all_data_frames:
    print("추출할 데이터가 없습니다.")
else:
    # 모든 DataFrame을 하나로 합침
    final_df = pd.concat(all_data_frames, ignore_index=True)

    # 데이터 클리닝: 유효하지 않은 값(매우 큰 수)을 가진 행 제거
    # 수목 높이가 0 이상 100 미터 이하인 데이터만 유효하다고 간주
    final_df = final_df[(final_df['canopy_height_m'] >= 0) & (final_df['canopy_height_m'] < 100)]
    
    print(f"\n총 {len(final_df)}개의 유효한 데이터 포인트를 추출했습니다.")
    print("데이터 미리보기:")
    print(final_df.head()) # 상위 5개 데이터 출력

    # --- 4. CSV 및 JSON 파일로 저장 ---
    csv_path = f"{output_filename}.csv"
    json_path = f"{output_filename}.json"

    # CSV 파일로 저장 (인덱스 제외)
    final_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"\nCSV 파일 저장 완료: {csv_path}")

    # JSON 파일로 저장 (레코드 형식, 가독성 좋게)
    final_df.to_json(json_path, orient='records', indent=4)
    print(f"JSON 파일 저장 완료: {json_path}")