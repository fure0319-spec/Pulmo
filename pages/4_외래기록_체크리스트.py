
import re
import streamlit as st

st.set_page_config(page_title="외래기록(체크리스트)", layout="wide")
st.title("외래 기록(체크리스트)")

FINAL_OUTPATIENT_NOTE = "환자 P/E 및 검사 결과 확인하였으며, 검사 결과 설명하고, 경과 악화 시 병원 내원할 것 설명함"

# ====== 원본(Tkinter) decision_helper1.py의 체크리스트 항목을 그대로 이식 ======
============ 외래 기록(체크리스트) 작성 도구 ================= #

# 1) 공통(호흡기 일반) 현재 증상 + mMRC
SYMPTOMS_BASE_YN = [
    "Cough (기침)",
    "Sputum (가래)",
    "Rhinorrhea (콧물)",
    "Nasal congestion (코막힘)",
    "Sore throat (인후통)",
    "Hemoptysis (혈담/객혈)",
    "Dyspnea (호흡곤란, at rest / exertional)",
    "Wheezing (천명음)",
    "Chest pain or tightness (흉통/답답함)",
    "Fever/chill (발열/오한)",
    "Fatigue (피로)",
    "Weight loss (체중 감소)",
    "현재 흡연 중",
]

# 2) ILD 재진 추가 문항
ILD_FU_YN = [
    "Dry, persistent cough (건성·지속 기침)",
    "Progressive dyspnea (점진적 악화 호흡곤란)",
    "Orthopnea/PND (기좌호흡/야간발작호흡곤란)",
]

# 3) ILD 초진 추가 문항
ILD_NEW_YN = [
    "증상 시작 후 기간 6개월 이상",
    "점진적 호흡곤란/건성기침 지속",
    "체중 감소/식욕 저하(최근 6개월)",
    "손가락지팡이증/관절통/피부 변화",
    "가족력(ILD/IPF/CTD) 있음",
    "흡연력(현재/과거 팩-이어) 있음",
    "직업/환경 노출(석면/분진/조류/농약) 있음",
    "약제 노출(암약제/면역억제제/항암제) 있음",
    "CTD 증상(레이노/관절염/근력 저하/피부 경화) 있음",
    "동반질환(고혈압/GERD/당뇨/심부전) 있음",
    "이전 PFT(6MWT) 결과 악화 추세",
    "급성 악화(AE) 병력 있음",
]

# 4) 폐암 환자용 추가 문항
LUNG_CA_YN = [
    "최근 수주–수개월간 기침/호흡곤란 악화",
    "객혈 또는 혈담 경험",
    "설명되지 않는 체중 감소/식욕 저하",
    "흉통/어깨통증/뼈 통증",
    "쉰목소리(hoarseness) 또는 삼킴 곤란",
    "두통, 어지러움, 신경학적 증상(마비, 감각저하 등)",
    "이전 항암/방사선 치료력 있음",
    "마지막 치료 후 악화된 증상 있음",
    "현재 복용 중 항암제/표적치료제/면역항암제 있음",
    "관련 의심 부작용(피부, 호흡, 위장, 간/신장 기능 이상 등) 있음",
]

# 5) COPD 환자용 추가 문항
COPD_YN = [
    "만성 기침(3개월 이상/2년 이상 반복)",
    "만성 가래(아침/계절성 포함)",
    "최근 1년간 악화(Exacerbation)로 응급실/입원 경험",
    "계단 오르기/평지 보행 시 숨참 증가",
    "야간/새벽에 악화되는 호흡곤란",
    "흡연 중이거나 과거 흡연력(팩-이어) 있음",
    "직업적/환경적 노출(분진, 화학물질, 실내·실외 공기오염) 있음",
    "흡입제(ICS/LABA/LAMA 등) 규칙적 사용",
    "흡입기 사용법 교육 받은 적 있음",
    "최근 흡입제 종류 변경/중단 있음",
    "산소치료(가정 산소) 사용 중",
    "처방된 시간/유량대로 사용함",
    "흡입제/산소 사용과 관련된 불편감/부작용 있음",
    "기타 호흡기 질환 공통 질문 생활습관 및 위험인자",
]

# 6) 약제 사용 및 부작용
MED_AE_YN = [
    "약제 처방대로 복용/사용함",
    "경구 항생제 복용함",
    "최근 약제 중단/용량 변경 있음",
    "스테로이드 부작용(부종, 고혈당, 불면 등) 있음",
    "항섬유화제 부작용(GI, 피부, 간기능 등) 있음",
    "흡입제 사용법 숙지/규칙적 사용",
    "흡입제 부작용(구강칸디다, 쉰목소리 등) 있음",
]

# 7) Lab / 영상 검사 결과
LAB_IMG_YN = [
    "CBC abnormality",
    "BUN/Cr abnl",
    "OT/PT/T.bil elevation",
    "e' abnl",
    "CXR abnl",
    "CT result",
    "PFT FEV1/FVC/Ratio ///",
    "DLco",
    "5MWT",
]

# 8) Further Plan
PLAN_YN = [
    "Add",
    "d/c",
    "다음 PFT 검사",
    "다음 CT 검사",
    "입원",
]

# 특수 항목 키(라디오 그룹)
_SPECIAL_MMRC = "__MMRC__"
_SPECIAL_OPDFU = "__OPDFU__"

OPD_FU_CHOICES = [
    ("1wk", "1wk"),
    ("2wk", "2wk"),
    ("1m", "1m"),
    ("3m", "3m"),
    ("6m", "6m"),
]

# 템플릿 → 탭 구성
# 각 탭: (탭 제목, yn_items(list[str]), include_mmrc(bool), include_opdfu(bool))
TEMPLATE_TO_TABS = {
    "호흡기 일반": [
        ("현재 증상", SYMPTOMS_BASE_YN, True, False),
        ("약제/부작용", MED_AE_YN, False, False),
        ("Lab/영상", LAB_IMG_YN, False, False),
        ("Further Plan", PLAN_YN, False, True),
    ],
    "ILD 초진": [
        ("현재 증상", SYMPTOMS_BASE_YN, True, False),
        ("ILD 초진 추가", ILD_NEW_YN, False, False),
        ("약제/부작용", MED_AE_YN, False, False),
        ("Lab/영상", LAB_IMG_YN, False, False),
        ("Further Plan", PLAN_YN, False, True),
    ],
    "ILD 재진": [
        ("현재 증상", SYMPTOMS_BASE_YN, True, False),
        ("ILD 재진 추가", ILD_FU_YN, False, False),
        ("약제/부작용", MED_AE_YN, False, False),
        ("Lab/영상", LAB_IMG_YN, False, False),
        ("Further Plan", PLAN_YN, False, True),
    ],
    "폐암": [
        ("현재 증상", SYMPTOMS_BASE_YN, True, False),
        ("폐암 추가", LUNG_CA_YN, False, False),
        ("약제/부작용", MED_AE_YN, False, False),
        ("Lab/영상", LAB_IMG_YN, False, False),
        ("Further Plan", PLAN_YN, False, True),
    ],
    "COPD": [
        ("현재 증상", SYMPTOMS_BASE_YN, True, False),
        ("COPD 추가", COPD_YN, False, False),
        ("약제/부작용", MED_AE_YN, False, False),
        ("Lab/영상", LAB_IMG_YN, False, False),
        ("Further Plan", PLAN_YN, False, True),
    ],
}




def strip_korean_parentheses(text: str) -> str:
    # 원본 로직: 한글이 포함된 괄호는 제거
    return re.sub(r"\s*\([^)]*[가-힣][^)]*\)", "", text).strip()

def tri_state_radio(label: str, key: str) -> int:
    # -1: blank, 1: yes, 0: no
    opts = ["(빈칸)", "Yes", "No"]
    v = st.radio(label, opts, index=0, horizontal=True, key=key)
    if v == "Yes":
        return 1
    if v == "No":
        return 0
    return -1

# ====== 템플릿 선택 ======
templates = list(TEMPLATE_TO_TABS.keys())
if "check_template" not in st.session_state:
    st.session_state.check_template = templates[0]

template = st.selectbox("템플릿", templates, index=templates.index(st.session_state.check_template))
st.session_state.check_template = template

tabs_def = TEMPLATE_TO_TABS.get(template, TEMPLATE_TO_TABS.get("호흡기 일반", []))

# 세션 상태 초기화(템플릿 바뀌면 키 충돌 방지)
if "check_state" not in st.session_state:
    st.session_state.check_state = {}

cbtn1, cbtn2 = st.columns([1, 1])
with cbtn1:
    if st.button("전체 초기화", type="secondary"):
        st.session_state.check_state = {}
        st.rerun()
with cbtn2:
    st.caption("빈칸은 출력에서 제외됩니다. Yes는 +, No는 - 로 표시됩니다.")

# ====== 입력 UI ======
tab_titles = [t[0] for t in tabs_def]
tabs = st.tabs(tab_titles)

for i, (tab_title, yn_items, include_mmrc, include_opdfu) in enumerate(tabs_def):
    with tabs[i]:
        st.subheader(tab_title)

        for item in yn_items:
            key = f"yn::{template}::{tab_title}::{item}"
            if key not in st.session_state.check_state:
                st.session_state.check_state[key] = -1
            val = tri_state_radio(strip_korean_parentheses(item), key=key)
            st.session_state.check_state[key] = val

        if include_mmrc:
            st.divider()
            mmrc_key = f"mmrc::{template}"
            mmrc_opts = ["(빈칸)", "0", "1", "2", "3", "4"]
            mmrc_val = st.radio("mMRC", mmrc_opts, index=0, horizontal=True, key=mmrc_key)
            st.session_state.check_state[mmrc_key] = -1 if mmrc_val == "(빈칸)" else int(mmrc_val)

        if include_opdfu:
            st.divider()
            fu_key = f"opdfu::{template}"
            choices = [""] + [c[0] for c in OPD_FU_CHOICES]
            fu = st.selectbox("OPD f/u", choices, index=0, key=fu_key)
            st.session_state.check_state[fu_key] = fu

# ====== 출력 ======
st.divider()
st.subheader("출력")

lines = []
for (tab_title, yn_items, include_mmrc, include_opdfu) in tabs_def:
    chosen = []
    for item in yn_items:
        key = f"yn::{template}::{tab_title}::{item}"
        val = st.session_state.check_state.get(key, -1)
        if val == -1:
            continue
        cleaned = strip_korean_parentheses(item)
        if not cleaned:
            continue
        if val == 1:
            chosen.append(f"{cleaned} +")
        elif val == 0:
            chosen.append(f"{cleaned} -")

    if include_mmrc:
        mmrc_key = f"mmrc::{template}"
        mmrc = st.session_state.check_state.get(mmrc_key, -1)
        if mmrc != -1:
            chosen.append(f"mMRC {mmrc}")

    if include_opdfu:
        fu_key = f"opdfu::{template}"
        fu = str(st.session_state.check_state.get(fu_key, "")).strip()
        if fu:
            chosen.append(f"OPD f/u {fu}")

    if chosen:
        lines.append(", ".join(chosen))
        lines.append("")

base_text = "\n".join(lines).rstrip()
if base_text:
    text_out = base_text + "\n\n" + FINAL_OUTPATIENT_NOTE + "\n"
else:
    text_out = FINAL_OUTPATIENT_NOTE + "\n"

st.code(text_out, language="text")
st.caption("웹 환경에서는 코드 블록에서 복사해 EMR에 붙여넣기 하시면 됩니다.")
