import numpy as np
import pandas as pd

# 최종 산출물: 정제결과_멘티.csv  (문제 10에서 만듭니다)
#
# 필요한 파일: 설비배치1.csv (같은 폴더에 두세요)
#   검사일시 / 생산라인(A·B·C) / 설비번호 / 온도 / 진동 / 회전수 / 압력 / 판정

df = pd.read_csv("설비배치1.csv", encoding="utf-8-sig")
센서 = ["온도", "진동", "회전수", "압력"]

# ----------------------------------------
# 문제 1. 받은 파일을 열고 상태를 파악한다
# ----------------------------------------
print("문제 1. 받은 파일을 열고 상태를 파악한다")
# 표 크기
print(df.shape)

# 결측 열과 개수
# => df[특정 열].isna(): 해당 열에서 결측 구하기 (결측이 있으면 True)
print(f"'온도': {df['온도'].isna().sum()}, '압력': {df['압력'].isna().sum()}")

# 진동 열 첫 값의 자료형 이름
print(df["진동"].dtype)

# 판정 열의 값별 개수를 차례로 출력
result = {}
result["정상"] = 0
result["주의"] = 0
result["이상"] = 0
for i in df["판정"]:
    if i == "정상":
        result["정상"] += 1
    elif i == "주의":
        result["주의"] += 1
    elif i == "이상":
        result["이상"] += 1

print(result)
print()

# ----------------------------------------
# 문제 2. 숫자로 저장되지 않은 열 고치기
# ----------------------------------------
print("문제 2. 숫자로 저장되지 않은 열 고치기")
df["진동"] = pd.to_numeric(df["진동"], errors="coerce")
print(df["진동"].isna().sum())
print(np.round(df["진동"].mean(), 2))
print()

# ----------------------------------------
# 문제 3. 중복 행 제거
# ----------------------------------------
print("문제 3. 중복 행 제거")
print(df.duplicated().sum())
df = df.drop_duplicates()
print(df.shape)
print()

# ----------------------------------------
# 문제 4. 결측 채우기
# ----------------------------------------
print("문제 4. 결측 채우기")
temp_avg = df["온도"].mean()
press_median = df["압력"].median()
vib_avg = df["진동"].mean()

# 해당 열들의 결측에 값을 채우기
for column in ["온도", "진동", "압력"]:
    if column == "압력":
        # 빈 칸을 그 열의 중앙값으로
        df[column] = df[column].fillna(df[column].median())
    else:
        # 빈 칸을 그 열의 평균값으로
        df[column] = df[column].fillna(df[column].mean())

print(df.duplicated().sum())
print(round(temp_avg, 2), round(press_median, 2))
print()

# ----------------------------------------
# 문제 5. 생산라인별 요약
# ----------------------------------------
print("문제 5. 생산라인별 요약")
# 특정 열의 특정 값을 지정하기
# df[df[특정 열 이름] == 열의 값 이름]
# numeric_only=True: 결측 필터링 ("측정불가", "NaN"과 같은 문자값들 거르기)

# 의문점: 앞에서 결측값들을 for문으로 수정했는데 왜 결측값이 남아서
# 평균 구할 때, 'numeric_only=True'를 선언해야 하는지 의문입니다
print(round(df.groupby("생산라인").mean(numeric_only=True), 2))

prod_line = {}
prod_line["A라인"] = len(df[df["생산라인"] == "A라인"])
prod_line["B라인"] = len(df[df["생산라인"] == "B라인"])
prod_line["C라인"] = len(df[df["생산라인"] == "C라인"])
print(prod_line)
print()

# ----------------------------------------
# 문제 6. z-점수로 온도 이상 찾기
# ----------------------------------------
print("문제 6. z-점수로 온도 이상 찾기")
print(np.round(df["온도"].mean(), 2), np.round(df["온도"].std(ddof=0), 2))
z_temp = (df["온도"] - df["온도"].mean()) / df["온도"].std(ddof=0)
print((z_temp > np.abs(-3)).sum(), (z_temp > np.abs(-2)).sum())
print()

# ----------------------------------------
# 문제 7. IQR로 압력 이상 찾기
# ----------------------------------------
print("문제 7. IQR로 압력 이상 찾기")
q1 = np.percentile(df["압력"], 25)
q3 = np.percentile(df["압력"], 75)
iqr = q3 - q1
low = q1 - 1.5 * iqr
high = q3 + 1.5 * iqr
print(round(low, 2), round(high, 2))
wrong_num = ((df["압력"] < low) | (df["압력"] > high)).sum()
print(wrong_num)
# 이상값 열 번호 저장
c_idx = np.where((df["압력"] < low) | (df["압력"] > high))[0]
# print(c_idx)
# df.iloc[...]로 접근해서 행 구하기
# unique()를 이용하여 행 값을 저장 => 적절한 인덱스 번호로 호출
# print(df.iloc[c_idx]["생산라인"].unique()[0])
result = {}
result[df.iloc[c_idx]["생산라인"].unique()[0]] = int(wrong_num)
print(result)
print()

# ----------------------------------------
# 문제 8. 이상으로 판정된 행 제거
# ----------------------------------------
print("문제 8. 이상으로 판정된 행 제거")
print(prod_line)
# 제거 (drop())

# 의문점: 인덱스 따로 저장한 것(c_idx)과 열의 인덱스 번호가 다릅니다 (3씩 차이)
df = df.drop(c_idx + 3)
prod_line = {}
prod_line["A라인"] = len(df[df["생산라인"] == "A라인"])
prod_line["B라인"] = len(df[df["생산라인"] == "B라인"])
prod_line["C라인"] = len(df[df["생산라인"] == "C라인"])
print(prod_line)
print(df.shape)
print()

# ----------------------------------------
# 문제 9. 0~1로 스케일 맞추고 파일로 남기기
# ----------------------------------------
print("문제 9. 0~1로 스케일 맞추고 파일로 남기기")
# 센서 = ["온도", "진동", "회전수", "압력"]

# Min-Max 정규화 계산
# 정규화 값 = (현재값 - 최솟값) / (최댓값 - 최솟값)
normal_list = []
for c in 센서:
    최소 = df[c].min()
    최대 = df[c].max()
    df[c] = (df[c] - 최소) / (최대 - 최소)
    # 정규화 값들 배열화 + 소수점 넷째 자리
    normal_list.append(df[c])

print(
    {c: float(df[c].min()) for c in 센서}
)  # {'온도': 0.0, '진동': 0.0, '회전수': 0.0, '압력': 0.0}
print(
    {c: float(df[c].max()) for c in 센서}
)  # {'온도': 1.0, '진동': 1.0, '회전수': 1.0, '압력': 1.0}
print({c: float(round((df[c].mean()), 3)) for c in 센서})
normal_arr = np.round(np.array(normal_list).T, 4)
# print(normal_arr.shape)

# 이어 붙일 앞 열들 (각각 179개짜리 1차원 → (179, 1)로 변형)
add_date = df["검사일시"].to_numpy()[:, None]  # (179, 1)
add_line = df["생산라인"].to_numpy()[:, None]  # (179, 1)

# 이어 붙이기 작업 => (179, 6) 모양의 행렬
add_1 = np.concatenate([add_date, add_line, normal_arr], axis=1)


import csv

# CSV 파일의 열 헤더값 설정
header = [
    "검사일시",
    "생산라인",
    "정규화_온도",
    "정규화_진동",
    "정규화_회전수",
    "정규화_압력",
]

with open("정규화_멘티.csv", "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(add_1)

# 내보낸 파일 다시 읽기 1
df_normal = pd.read_csv("정규화_멘티.csv", encoding="utf-8-sig")
print(df_normal.shape)
print()

# ----------------------------------------
# 문제 10. 라인 인코딩하고 저장하기
# ----------------------------------------
print("문제 10. 라인 인코딩하고 저장하기")

# map()을 활용하여
# # 생산라인을 A라인 0, B라인 1, C라인 2 로 바꾼 라인코드 열을 만들기
mapping = {"A라인": 0, "B라인": 1, "C라인": 2}
df["라인코드"] = df["생산라인"].map(mapping)

header = ["검사일시", "생산라인", "라인코드", "온도", "진동", "회전수", "압력", "판정"]

# 새로운 열(라인코드)을 추가한 데이터프레임을 numpy 배열로
# 정제한 데이터 값을 저장한 부분
정제결과 = df[header].to_numpy()

with open("정제결과_멘티.csv", "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(정제결과)

# 내보낸 파일 다시 읽기
df_result = pd.read_csv("정제결과_멘티.csv", encoding="utf-8-sig")
# numpy 배열, 문자열 섞임 (object)
# pd.isna(arr).sum() — pandas가 문자열/숫자 섞여도 처리해줌
print(
    df_result.shape,
    sum(df_result.isna().sum().values),
    int(df_result.duplicated().sum()),
)
print(header)
