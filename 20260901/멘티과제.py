# ============================================================
# [멘티 과제] IoT 서버·센서 로그 데이터 정제 · 전처리
# ============================================================
#
# 여러분이 할 일은 '받은 데이터를 분석할 수 있는 상태로 만들어 멘토에게 넘기는 것'입니다.
# 지시문을 그대로 따라가면 됩니다. 기대 출력이 적혀 있으니 스스로 채점하세요.
# 숫자가 다르면 앞 문제로 돌아가 확인하고, 그래도 안 맞으면 멘토에게 물어보세요.
#
# 최종 산출물: 정제결과_멘티.csv  (문제 10에서 만듭니다)
#
# 필요한 파일: 로그배치1.csv (같은 폴더에 두세요)
#   수집시각 / 구역(Z1-알파·Z2-브라보·Z3-찰리) / 센서ID / CPU온도 / 전력 / 응답시간 / 메모리 / 상태


from locale import normalize

import numpy as np
import pandas as pd
from pandas import read_csv

# csv 파일 읽어오기 (encoding="utf-8-sig" 옵션을 주어 한글 깨짐 방지)
df = pd.read_csv("로그배치1.csv", encoding="utf-8-sig")
지표 = ["CPU온도", "전력", "응답시간", "메모리"]

print("문제 1. 받은 파일을 열고 상태를 파악한다")
# 표 크기
print(df.shape)

error_dict = {}
for c in 지표:
    error_dict[c] = int(df[c].isna().sum())

# 딕셔너리 컴프리헨션
# => 만약 value가 0보다 크면 error_dict에 추가하고, 0이면 제거
error_dict = {key: value for key, value in error_dict.items() if value > 0}
print(error_dict)
print(df["전력"].head(0).dtype)

# 상태 열의 값별 개수를 차례로 출력
condition = {}
condition["정상"] = 0
condition["경고"] = 0
condition["장애"] = 0
for i in df["상태"]:
    if i == "정상":
        condition["정상"] += 1
    elif i == "경고":
        condition["경고"] += 1
    elif i == "장애":
        condition["장애"] += 1
print(condition)
print()

print("문제 2. 숫자로 저장되지 않은 열 고치기")
# 전력 열의 값을 숫자로 변환 (바꾸지 못하는 값은 NaN(결측)으로 처리 => errors="coerce")
df["전력"] = pd.to_numeric(df["전력"], errors="coerce")
# print(df["전력"].dtype)
# 결측 개수
print(df["전력"].isna().sum())
# 평균 (소수 둘째 자리)
print(np.round(df["전력"].mean(numeric_only=True), 2))
print()

print("문제 3. 중복 행 제거")
# 중복행 체크
print(df.duplicated().sum())  # 4개

# 제거 전 크기 (186, 8)
# print(df.shape)

# 중복행 제거
df = df.drop_duplicates()
# 제거 후 크기 (182, 8)
print(df.shape)

# 중복 제거 후 인덱스 번호 재정렬
df = df.drop_duplicates().reset_index(drop=True)
print()

print("문제 4. 결측 채우기")
# CPU 온도의 평균값
cpu_temp = df["CPU온도"].mean(numeric_only=True)
# 메모리의 중앙값
ram_median = df["메모리"].median()
# 전력 열의 전체 평균값
power_avg = df["전력"].mean(numeric_only=True)

# 결측 채우기
df["CPU온도"] = df["CPU온도"].fillna(cpu_temp)
df["메모리"] = df["메모리"].fillna(ram_median)
df["전력"] = df["전력"].fillna(power_avg)

# 남은 결측 개수 확인
print(df[지표].isna().sum().values.sum())
print(np.round(cpu_temp, 2), np.round(ram_median, 2))
print()

print("문제 5. 구역별 요약")
# 데이터를 특정 열의 값별로 묶고 그룹별로 집계할 때 사용하는 메서드는 groupby()
print(np.round(df.groupby("구역").mean(numeric_only=True), 2))
area_zone = {}
area_zone["Z1-알파"] = len(df[df["구역"] == "Z1-알파"])
area_zone["Z2-브라보"] = len(df[df["구역"] == "Z2-브라보"])
area_zone["Z3-찰리"] = len(df[df["구역"] == "Z3-찰리"])
print(area_zone)
print()

print("문제 6. z-점수로 CPU온도 이상 찾기")
# z-score = (원 자료 - 자료 평균) / 표준편차
# cpu_temp = df["CPU온도"].mean(numeric_only=True)
# CPU 표준편차
cpu_std = df["CPU온도"].std(ddof=0)
print(np.round(cpu_temp, 2), np.round(cpu_std, 2))

# CPU온도 열의 Z-점수
z_cpu = (df["CPU온도"] - cpu_temp) / cpu_std
print(sum(z_cpu > np.abs(-3)), sum(z_cpu > np.abs(-2)))
print()

print("문제 7. IQR로 메모리 이상 찾기")
q1 = np.percentile(df["메모리"], 25)
q3 = np.percentile(df["메모리"], 75)
iqr_ram = q3 - q1

bottom_bnd = q1 - 1.5 * iqr_ram
top_bnd = q3 + 1.5 * iqr_ram
print(round(bottom_bnd, 2), round(top_bnd, 2))

# 울타리를 벗어난 값의 개수 체크
out_val = (df["메모리"] > top_bnd) | (df["메모리"] < bottom_bnd)
print(out_val.sum())

# 위치는 어디?
wrong_picks = np.where(out_val)[0]
result = {}
# unique(): 고유값을 추출하는 역할의 메서드
result[df["구역"][wrong_picks].unique()[0]] = len(wrong_picks)
print(result)
print()

print("문제 8. 이상으로 판정된 행 제거")
# 제거 이전 자료 수
print(area_zone)

# 제거 작업 (drop())
df = df.drop(wrong_picks)
area_zone = {}
area_zone["Z1-알파"] = len(df[df["구역"] == "Z1-알파"])
area_zone["Z2-브라보"] = len(df[df["구역"] == "Z2-브라보"])
area_zone["Z3-찰리"] = len(df[df["구역"] == "Z3-찰리"])
# 제거 이후 자료 수
print(area_zone)

# 제거 후 행열 크기
print(df.shape)
print()

print("문제 9. 0~1로 스케일 맞추고 파일로 남기기")

# 기존 자료 복사본 생성
df_copy = df.copy()

# 열별 최솟값, 최댓값, 평균 계산
# 지표 = ["CPU온도", "전력", "응답시간", "메모리"]
# 정규화: (표 - 최솟값) / (최댓값 - 최솟값)
# 값을 배열로 만들기 위한 빈 리스트
normalize_ls = []
for n in 지표:
    min = df_copy[n].min()
    max = df_copy[n].max()
    # 소수점 넷째 자리를 적용한 정규화 값
    df_copy[n] = np.round((df_copy[n] - min) / (max - min), 4)
    # 정규화 값들 배열화를 위한 리스트 이동
    normalize_ls.append(df_copy[n])

print({n: float(df_copy[n].min()) for n in 지표})
print({n: float(df_copy[n].max()) for n in 지표})
print({n: float(round(df_copy[n].mean(), 3)) for n in 지표})

# 이어 붙일 열들 가져오기
add_time = df_copy["수집시각"].to_numpy()[:, None]
# [:, None] => 열 붙이기
# print(add_time.shape)
add_area = df_copy["구역"].to_numpy()[:, None]

# 정규화 값의 배열화 (행 맞춤을 위한 뒤집기 메서드 사용 => transpose())
normal_arr = np.array(normalize_ls).transpose()
# print(normal_arr.shape)

# 불러온 열들 포함해서 이어 붙이기
add_columns = np.concatenate([add_time, add_area, normal_arr], axis=1)

# csv 파일로 내보내기
import csv

header = [
    "수집시각",
    "구역",
    "CPU온도_정규",
    "전력_정규",
    "응답시간_정규",
    "메모리_정규",
]

with open("정규화_멘티.csv", "w", encoding="utf-8-sig", newline="") as f:
    write = csv.writer(f)
    write.writerow(header)
    write.writerows(add_columns)

# 파일 읽어오기
df_normal = pd.read_csv("정규화_멘티.csv", encoding="utf-8-sig")
print(df_normal.shape)
print()

print("문제 10. 구역 인코딩하고 저장하기")
# map()을 활용하여 '구역코드' 열 생성
area_map = {"Z1-알파": 0, "Z2-브라보": 1, "Z3-찰리": 2}
df["구역코드"] = df["구역"].map(area_map)

header = [
    "수집시각",
    "구역",
    "구역코드",
    "CPU온도",
    "전력",
    "응답시간",
    "메모리",
    "상태",
]

# 새로운 열을 추가하여 numpy 배열화 + 데이터 정제 작업
refine_datas = df[header].to_numpy()
# print(refine_datas)

# csv 파일로 내보내기
with open("정제결과_멘티.csv", "w", encoding="utf-8-sig", newline="") as f:
    write = csv.writer(f)
    write.writerow(header)
    write.writerows(refine_datas)

# 파일 읽어오기
df_refine = pd.read_csv("정제결과_멘티.csv", encoding="utf-8-sig")

# 표 크기, 결측 총 개수, 중복 개수
print(df_refine.shape, sum(df_refine.isna().sum().values), df_refine.duplicated().sum())
# 열 이름 목록 => 0번째(헤더) 순서 list화해서 호출
print(list(df_refine.head(0)))
