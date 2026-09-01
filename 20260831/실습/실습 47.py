# ============================================================
# [멘토 과제] 멘티 정제 결과 검수 · 재처리 · 기준 배포
# ============================================================
#
# 멘티는 지시받은 절차를 성실히 따랐습니다. 코드에 오류도 없습니다.
# 그런데 결과물에는 그대로 쓰면 안 되는 부분이 남아 있습니다.
# 여러분의 일은 '무엇이, 왜 잘못됐는지 숫자로 밝히고 고치는 것'입니다.
#
#
# 이 파일에는 정답 출력이 없습니다. 정답이 하나가 아니기 때문입니다.
# 대신 문제마다 [확인 항목]이 있습니다. 그 조건을 만족시키면 됩니다.
# 문제마다 마지막에 [멘티에게 한 문장으로]가 있습니다. 이게 진짜 과제입니다.
#
# 필요한 파일: 설비배치1.csv / 설비배치2.csv / 정제결과_멘티.csv / 정규화_멘티.csv
# 산출물: 스케일링기준.csv / 정제결과_최종.csv / 검수보고서.md
 
import numpy as np
import pandas as pd

from pathlib import Path
BASE = Path(__file__).resolve().parent


First = pd.read_csv(BASE / "설비배치1.csv", encoding="utf-8-sig")
First["진동"] = pd.to_numeric(First["진동"], errors="coerce") 
Menti = pd.read_csv(BASE / "정제결과_멘티.csv", encoding="utf-8-sig")
MentiNorm = pd.read_csv(BASE / "정규화_멘티.csv", encoding="utf-8-sig")
Sensor = ["온도", "진동", "회전수", "압력"]
Keys = ["검사일시", "생산라인", "설비번호"]


 
# ----------------------------------------
# 문제 1. 무엇이 달라졌는지부터 센다
# ----------------------------------------
# 원본, 원본에서 완전 중복만 제거한 표, 멘티 결과 세 표의 행 수를 한 줄에 출력하세요.
# 이어서 생산라인별 행 수를 두 표에서 각각 출력하고,
# 생산라인별 온도 평균을 원본 / 멘티 / 차이 세 칸짜리 표로 출력하세요.
# 원본의 평균은 결측을 뺀 값으로 구합니다.
#
# [확인 항목]
#   - 라인 하나에서만 행이 줄었다. 어느 라인이고 몇 행인가
#   - 라인 하나에서 온도 평균이 0.5도 이상 올라갔다. 어느 라인이고 얼마인가
#   - 세 라인의 행 수가 처음부터 60개씩 균등하지 않다. 이건 또 다른 문제의 신호다
#
# [멘티에게 한 문장으로]
#   "○○라인만 △행이 사라졌는데, 그 이유는 ..."

print("1번")
Dup_removed = First.drop_duplicates() 

print(f"원본 {len(First)}행 / 완전중복 제거 {len(Dup_removed)}행 / 멘티 {len(Menti)}행")

print()
print("[생산라인별 행 수]")
rows = pd.DataFrame({
    "원본": Dup_removed["생산라인"].value_counts(),
    "멘티": Menti["생산라인"].value_counts(),
}).sort_index()

print(rows)

print()
print("[생산라인별 온도 평균]")
temp_mean = pd.DataFrame({
    "원본": First.groupby("생산라인")["온도"].mean(),
    "멘티": Menti.groupby("생산라인")["온도"].mean(),
}).sort_index()
temp_mean["차이"] = temp_mean["멘티"] - temp_mean["원본"]

print(temp_mean.round(3))

print()






# ----------------------------------------
# 문제 2. 완전히 같은 행만 중복이 아니다
# ----------------------------------------
# 멘티는 '모든 값이 똑같은 행'만 지웠습니다. 그것만으로 충분한지 확인하세요.
# 검사일시·생산라인·설비번호 세 열이 같은 행이 몇 쌍 남아 있는지 세고,
# 해당 행들을 세 열과 온도·압력까지 붙여 출력하세요.
# 같은 시각에 같은 설비를 두 번 잰 기록입니다. 앞의 것만 남기고 정리한 뒤
# 표 크기와 라인별 행 수를 출력하세요.
#
# [확인 항목]
#   - 값이 미세하게 다르기 때문에 완전 중복 제거로는 안 걸린다. 얼마나 다른가
#   - 정리하고 나면 라인별 행 수가 60개씩 균등해진다
#   - 이 행들을 그대로 두면 그 라인의 평균이 어떻게 되는가
#
# [멘티에게 한 문장으로]
#   "값이 0.03 다르면 컴퓨터는 다른 행으로 보지만, 현실에서는 ..."

print("2번") 
key = ["검사일시", "생산라인", "설비번호"]

pairs = Dup_removed.duplicated(subset=key).sum()
print(f"세 열이 같은 행: {pairs}개")

triple = Dup_removed[Dup_removed.duplicated(subset=key, keep=False)]
print(triple.sort_values(key)[key + ["온도", "압력"]])

cleaned = Dup_removed.drop_duplicates(subset=key, keep="first").reset_index(drop=True)

print(f"정리 후 표 크기: {cleaned.shape}")
print("[정리 후 생산라인별 행 수]")
print(cleaned["생산라인"].value_counts().sort_index())




# ----------------------------------------
# 문제 3. 이상 탐지를 다시 한다
# ----------------------------------------
# 온도의 z-점수를 (가) 표 전체 기준, (나) 같은 생산라인 기준 두 가지로 구해
# 임계값 2.5를 넘는 개수를 한 줄에 출력하세요. 표준편차는 ddof=0 입니다.
# 이어서 (나)로 걸린 행의 검사일시·생산라인·설비번호·온도를 라인 순으로 출력하고,
# 라인별 온도 평균도 출력해 근거로 삼으세요.
#
# [확인 항목]
#   - (가)는 0건이다. 멘티가 "이상 없음"이라고 판단한 이유가 여기 있다
#   - (나)에서는 0건이 아니다
#   - 걸린 값 중에 '숫자만 보면 정상 같은데 그 라인에서는 비정상'인 것이 있다. 어느 것인가
#
# [멘티에게 한 문장으로]
#   "온도 73.5도는 A라인이면 정상이지만 C라인에서는 ..."

print()
print("3번")

#(가)
allavg = cleaned["온도"].mean()
allstd = cleaned["온도"].std(ddof=0)
allz = (cleaned["온도"] - allavg) / allstd

Ga = (allz.abs() > 2.5).sum()
print(f"(가) 표 전체 기준: {Ga}개")

#(나)

lineavg = cleaned.groupby("생산라인")["온도"].transform("mean")
linestd = cleaned.groupby("생산라인")["온도"].transform("std", ddof=0)
linez = (cleaned["온도"] - lineavg) / linestd
Na = (linez.abs() > 2.5).sum()
print(f"(나) 라인별 기준: {Na}개")

#(나)로 걸린 행

Na_rows = cleaned[linez.abs() > 2.5].sort_values("생산라인")[key + ["온도"]]
print(Na_rows)

print("[라인별 온도 평균]")
print(cleaned.groupby("생산라인")["온도"].mean().round(2))

# ----------------------------------------
# 문제 4. 채우기 전에 무엇을 먼저 해야 하는가
# ----------------------------------------
# 이제 결측을 라인별 값으로 채웁니다. 그런데 순서를 조심해야 합니다.
# 문제 3에서 찾은 이상값이 아직 표 안에 있습니다. 그 상태로 라인 평균을 구하면
# 그 평균 자체가 이미 오염되어 있습니다.
#
# 라인별 온도 평균을 '이상값 포함'과 '이상값 제외' 두 가지로 구해
# 두 값과 차이를 세 칸짜리 표로 출력하세요.
# 그다음 '이상값을 뺀 라인 평균'으로 온도 결측을 채우고,
# 압력과 진동은 라인 중앙값으로 채우세요.
# 채운 뒤 남은 결측 총 개수, 라인별 온도 평균, 그리고 멘티의 라인별 온도 평균을
# 차례로 출력해 세 값을 비교하세요.
#
# [확인 항목]
#   - 이상값을 포함해 구한 A라인 평균과 제외하고 구한 평균이 1도 넘게 차이 난다
#   - 어느 쪽으로 채우는 것이 맞는가. 근거를 댈 수 있는가
#   - 중앙값을 쓰면 이 문제가 덜 생긴다. 왜 그런가
#
# [멘티에게 한 문장으로]
#   "결측을 채우기 전에 이상값부터 봐야 하는 이유는 ..."


print("4번")

outlier = linez.abs() > 2.5 
clean_only = cleaned.loc[~outlier]

line_temp_mean = pd.DataFrame({
	"이상값 포함": cleaned.groupby("생산라인")["온도"].mean(),
	"이상값 제외": clean_only.groupby("생산라인")["온도"].mean(),
})
line_temp_mean["차이"] = line_temp_mean["이상값 포함"] - line_temp_mean["이상값 제외"]

print(line_temp_mean)


#채우기
filled = cleaned.copy()
filled["온도"] = filled.groupby("생산라인")["온도"].transform(lambda x: x.fillna(x.mean()))
filled["압력"] = filled.groupby("생산라인")["압력"].transform(lambda x: x.fillna(x.median()))
filled["진동"] = filled.groupby("생산라인")["진동"].transform(lambda x: x.fillna(x.median()))

print(f"남은 결측 총 개수: {filled.isna().sum().sum()}")
print("[라인별 온도 평균]")
print(filled.groupby("생산라인")["온도"].mean().round(2))
print("[멘티 라인별 온도 평균]")
print(Menti.groupby("생산라인")["온도"].mean().round(2))


 
# ----------------------------------------
# 문제 5. 한 번 걸러내고 끝내면 안 된다
# ----------------------------------------
# 압력 이상값을 라인별 z-점수 임계값 3으로 찾으세요.
# 먼저 C라인 압력의 표준편차를 출력하고, 걸린 개수와 걸린 행의 라인·압력을 출력합니다.
# 걸린 값을 그 라인의 중앙값으로 바꾼 뒤, C라인 압력의 표준편차를 다시 출력하세요.
# 그리고 같은 방법으로 한 번 더 탐지해 개수와 걸린 행을 출력하세요.
# 2차에서도 걸리면 같은 방법으로 처리하고, 3차에서 0건이 되는지 확인하세요.
# 마지막으로 라인별 행 수를 출력하세요.
#
# [확인 항목]
#   - 1차 처리 전후로 C라인 압력 표준편차가 크게 줄어든다. 얼마에서 얼마로 줄었는가
#   - 2차에서 1차 때는 안 걸리던 값이 새로 걸린다. 왜 1차에서는 안 걸렸는가
#   - 3차에서 0건이 되어야 멈춘다. 한 번만 돌리고 끝냈다면 무엇을 놓쳤겠는가
#   - 행을 지우지 않았으므로 라인별 행 수가 그대로여야 한다
#
# [멘티에게 한 문장으로]
#   "큰 이상값 하나가 표준편차를 부풀려서 작은 이상값을 ..."
 

print()
print("5번")

capped = filled.copy()

def find_outlier(df, col, k=3):
    """라인별 z-점수로 이상값 마스크 만들기"""
    m = df.groupby("생산라인")[col].transform("mean")
    s = df.groupby("생산라인")[col].transform("std", ddof=0)
    z = (df[col] - m) / s
    return z.abs() > k

def c_std(df):
    return df[df["생산라인"] == "C라인"]["압력"].std(ddof=0)

# ---- 1차 ----
print(f"[처리 전] C라인 압력 표준편차: {c_std(capped):.3f}")

mask = find_outlier(capped, "압력")
print(f"\n1차 걸린 개수: {mask.sum()}")
print(capped[mask][["생산라인", "압력"]])

med = capped.groupby("생산라인")["압력"].median()
capped.loc[mask, "압력"] = capped.loc[mask, "생산라인"].map(med)

print(f"\n[1차 처리 후] C라인 압력 표준편차: {c_std(capped):.3f}")

# ---- 2차 ----
mask = find_outlier(capped, "압력")
print(f"\n2차 걸린 개수: {mask.sum()}")
print(capped[mask][["생산라인", "압력"]])

med = capped.groupby("생산라인")["압력"].median()
capped.loc[mask, "압력"] = capped.loc[mask, "생산라인"].map(med)

print(f"\n[2차 처리 후] C라인 압력 표준편차: {c_std(capped):.3f}")

# ---- 3차 ----
mask = find_outlier(capped, "압력")
print(f"\n3차 걸린 개수: {mask.sum()}")

print()
print("[라인별 행 수]")
print(capped["생산라인"].value_counts().sort_index())





# ----------------------------------------
# 문제 6. 같은 행인데 스케일 값이 다르다
# ----------------------------------------
# 멘티가 넘긴 정규화_멘티.csv 와, 문제 5까지 정리한 여러분의 표를 같은 방식으로
# (표 전체 min·max 기준) 정규화한 결과를 나란히 놓고 비교하세요.
# 검사일시와 생산라인을 이어 붙인 값을 키로 두 표를 맞추면 됩니다.
#
# (1) 맞춰진 행 수
# (2) 센서별 두 값의 차이 최댓값
# (3) 센서별 차이가 0.05를 넘는 행의 개수
# (4) 온도 차이가 큰 상위 4개 행의 키·멘티값·멘토값
# (5) 라인별 정규화 온도 평균 - 멘티 / 멘토 두 칸짜리 표
#
# [확인 항목]
#   - 같은 검사 기록인데 스케일 값이 0.4 넘게 벌어진 행이 있다. 어느 행들인가
#   - 손대지 않은 열은 차이가 0이다. 어느 열이고, 그게 무엇을 뜻하는가
#   - 어느 쪽이 옳은지는 (5)로 판정한다. A라인 정상 온도가 정규화되면 0.1 근처여야 하는데
#     0.536이라는 값은 A라인 어디에도 없는 값이다
#
# [멘티에게 한 문장으로]
#   "같은 A라인 기록인데 0.061이 아니라 0.536으로 찍힌 이유는 ..."

print()
print("6번")

# --- 내 표 정규화 (표 전체 min-max) ---
MyNorm = capped[["검사일시", "생산라인"] + Sensor].copy()
for c in Sensor:
    lo, hi = MyNorm[c].min(), MyNorm[c].max()
    MyNorm[c] = (MyNorm[c] - lo) / (hi - lo)

# --- 키 만들기 ---
MyNorm["키"] = MyNorm["검사일시"] + "_" + MyNorm["생산라인"]

Mn = MentiNorm.copy()
Mn.columns = [c.replace("정규화_", "") for c in Mn.columns]   # 열 이름 맞추기
Mn["키"] = Mn["검사일시"] + "_" + Mn["생산라인"]


merged = Mn.merge(MyNorm, on="키", suffixes=("_멘티", "_멘토"))
print(f"맞춰진 행: {len(merged)}행  (멘티 {len(Mn)} / 멘토 {len(MyNorm)})")

print()
print("센서별 차이")
for c in Sensor:
    d = (merged[f"{c}_멘티"] - merged[f"{c}_멘토"]).abs()
    print(f"  {c}: 최대 {d.max():.4f}, 0.05 초과 {int((d > 0.05).sum())}행")


merged["온도차"] = (merged["온도_멘티"] - merged["온도_멘토"]).abs()
print()
print("온도 차이 상위 4행")
print(merged.nlargest(4, "온도차")[["키", "온도_멘티", "온도_멘토", "온도차"]].round(4))


print()
print("라인별 정규화 온도 평균")
cmp5 = pd.DataFrame({
    "멘티": Mn.groupby("생산라인")["온도"].mean(),
    "멘토": MyNorm.groupby("생산라인")["온도"].mean(),
}).sort_index()
print(cmp5.round(3))



 
# ----------------------------------------
# 문제 7. 스케일 기준은 학습에서만 잡는다
# ----------------------------------------
# 시드 6으로 행 순서를 섞어 6:2:2 로 학습·검증·테스트를 나누고 각 크기를 출력하세요.
# (경계는 전체 길이의 0.6, 0.8 지점을 정수로 자릅니다)
# 센서 4열에 대해 '학습 데이터만'의 min·max 기준표를 만들고,
# '표 전체'의 min·max 와 나란히 출력하세요. 학습 기준표는 스케일링기준.csv 로 저장합니다.
# 이어서 테스트 데이터를 두 기준으로 각각 변환해 비교하세요.
#   (1) 0~1 밖으로 나간 값의 개수 - 전체 기준 / 학습 기준
#   (2) 정확히 0 또는 1인 칸의 개수 - 전체 기준 / 학습 기준
#   (3) 학습 기준 변환값의 열별 최댓값
#
# [확인 항목]
#   - 전체 기준으로는 0~1 밖 값이 하나도 안 나온다. 좋아 보이지만 이게 누출의 증거다
#   - 전체 기준에서는 테스트 행이 정확히 0이나 1이 되는 칸이 더 많이 나온다.
#     그 행의 값이 곧 기준의 min 또는 max 였다는 뜻이다. 왜 이게 문제인가
#   - 학습 기준에서는 0~1 밖 값이 나온다. 이건 오류가 아니다. 왜 정상인가
#
# [멘티에게 한 문장으로]
#   "테스트 값이 1을 넘은 건 잘못된 게 아니라 ..."
 
 
print()
print("7번")


shuffled = capped.sample(frac=1, random_state=6).reset_index(drop=True)
n = len(shuffled)
i1, i2 = int(n * 0.6), int(n * 0.8)

train = shuffled.iloc[:i1]
valid = shuffled.iloc[i1:i2]
test  = shuffled.iloc[i2:]

print(f"학습 {len(train)} / 검증 {len(valid)} / 테스트 {len(test)}")


train_ref = pd.DataFrame({"min": train[Sensor].min(), "max": train[Sensor].max()})
all_ref   = pd.DataFrame({"min": capped[Sensor].min(), "max": capped[Sensor].max()})

print()
print("[학습 기준]")
print(train_ref.round(3))
print()
print("[전체 기준]")
print(all_ref.round(3))

train_ref.to_csv(BASE / "스케일링기준.csv", encoding="utf-8-sig")


def scale(df, ref):
    out = pd.DataFrame(index=df.index)
    for c in Sensor:
        lo, hi = ref.loc[c, "min"], ref.loc[c, "max"]
        out[c] = (df[c] - lo) / (hi - lo)
    return out

test_by_all   = scale(test, all_ref)
test_by_train = scale(test, train_ref)

out_all   = ((test_by_all < 0) | (test_by_all > 1)).sum().sum()
out_train = ((test_by_train < 0) | (test_by_train > 1)).sum().sum()
edge_all   = ((test_by_all == 0) | (test_by_all == 1)).sum().sum()
edge_train = ((test_by_train == 0) | (test_by_train == 1)).sum().sum()

print()
print(f"0~1 밖: 전체기준 {out_all}개 / 학습기준 {out_train}개")
print(f"정확히 0 또는 1: 전체기준 {edge_all}개 / 학습기준 {edge_train}개")
print()
print("학습 기준 변환값의 열별 최댓값")
print(test_by_train.max().round(4))


# ----------------------------------------
# 문제 8. 새 배치가 들어왔다
# ----------------------------------------
# 스케일링기준.csv 를 다시 읽어 기준을 되살리고, 설비배치2.csv 를 변환하세요.
# 먼저 배치2의 라인별 행 수를 출력하고, 배치1에 없던 생산라인이 있는지
# 개수와 이름을 출력하세요.
# 저장된 기준으로 변환한 뒤 라인별 온도 변환값의 최소·최대를 출력하세요.
# 이어서 A라인 0, B라인 1, C라인 2 로 라인코드를 매길 때 코드가 안 붙는 행이
# 몇 개인지 출력하세요.
# 그다음 배치1에 있던 라인만 남겨 다시 변환하고, 0~1 밖으로 나간 값의 개수와
# 열별 최소·최대를 출력하세요. 마지막으로 같은 기준으로 한 번 더 변환해
# 결과가 완전히 같은지 True/False 로 출력하세요.
# 그리고 문제 5까지 정리한 표를 정제결과_최종.csv 로 저장하고, 다시 읽어
# 표 크기·결측 총 개수·라인별 행 수를 출력하세요.
#
# [확인 항목]
#   - 배치1에 없던 라인이 섞여 있다. 몇 행이고 어느 라인인가
#   - 그 라인의 변환값은 1을 한참 넘는다. 문제 7의 '1.001'과는 성격이 완전히 다르다.
#     하나는 정상이고 하나는 경보다. 무엇으로 구분하는가
#   - 라인코드가 안 붙는 행이 그대로 모델에 들어가면 무슨 일이 생기는가
#   - 이 라인을 어떻게 처리할지 결정하고, 그 이유를 적으세요.
#     (버린다 / 따로 뺀다 / 새 기준을 만든다 - 정답은 하나가 아닙니다)
#
# [멘티에게 한 문장으로]
#   "처음 보는 라인이 들어왔을 때 기존 기준을 그대로 쓰면 ..."
 
print()
print("8번")


saved_ref = pd.read_csv(BASE / "스케일링기준.csv", encoding="utf-8-sig", index_col=0)
Second = pd.read_csv(BASE / "설비배치2.csv", encoding="utf-8-sig")
Second["진동"] = pd.to_numeric(Second["진동"], errors="coerce")

print("[배치2 라인별 행 수]")
print(Second["생산라인"].value_counts().sort_index())

known = set(First["생산라인"].unique())
new_lines = sorted(set(Second["생산라인"].unique()) - known)
new_mask = Second["생산라인"].isin(new_lines)
print(f"\n새 라인 {len(new_lines)}종 {new_mask.sum()}행: {new_lines}")


def scale(df, ref):
    out = pd.DataFrame(index=df.index)
    for c in Sensor:
        lo, hi = ref.loc[c, "min"], ref.loc[c, "max"]
        out[c] = (df[c] - lo) / (hi - lo)
    return out

s2 = scale(Second, saved_ref)
s2["생산라인"] = Second["생산라인"]

print("\n[라인별 정규화 온도 min/max]")
print(s2.groupby("생산라인")["온도"].agg(["min", "max"]).round(3))


mapping = {"A라인": 0, "B라인": 1, "C라인": 2}
code = Second["생산라인"].map(mapping)
print(f"\n라인코드 미매핑: {code.isna().sum()}행")

Second_known = Second[~new_mask].reset_index(drop=True)
s2k = scale(Second_known, saved_ref)

outside = ((s2k < 0) | (s2k > 1)).sum().sum()
print(f"\n기존 라인만: {len(Second_known)}행, 0~1 밖 {outside}개")
print(pd.DataFrame({"min": s2k.min(), "max": s2k.max()}).round(4))


s2k_again = scale(Second_known, saved_ref)
print("\n같은 기준 재변환 동일:", s2k.equals(s2k_again))

final = capped.copy()
final["라인코드"] = final["생산라인"].map(mapping)
final.to_csv(BASE / "정제결과_최종.csv", index=False, encoding="utf-8-sig")

check = pd.read_csv(BASE / "정제결과_최종.csv", encoding="utf-8-sig")
print(f"\n최종 {check.shape} / 결측 {int(check.isna().sum().sum())}")
print(check["생산라인"].value_counts().sort_index())





# ----------------------------------------
# 마무리. 검수보고서.md 작성
# ----------------------------------------
# 아래 형식으로 검수보고서.md 를 직접 작성하세요. 코드가 아니라 글입니다.
#
#   ## 멘티 결과에서 발견한 문제
#   1. (무엇이 잘못됐는지) - (근거가 되는 숫자) - (그대로 두면 생기는 일)
#
#   ## 고치는 과정에서 내가 조심한 것
#   1. (순서를 어떻게 잡았는지, 왜 그 순서인지)
#   2. (한 번 처리하고 끝내지 않은 이유)
#
#   ## 판단이 필요했던 지점
#   (정답이 없어서 내가 결정한 것과 그 근거)
#
#   ## 멘티에게 전할 한 가지
#   (다음에 같은 데이터를 받으면 가장 먼저 무엇을 확인해야 하는가)
#
# 멘티 결과의 문제는 최소 3개, 내가 조심한 것은 최소 2개를 적어야 합니다.