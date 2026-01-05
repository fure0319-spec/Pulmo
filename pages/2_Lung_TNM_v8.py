
import streamlit as st
from utils_tnm import parse_size_cm, compute_T, tnm_stage_group

st.set_page_config(page_title="Lung TNM v8", layout="wide")
st.title("Lung TNM v8 (NSCLC)")

st.caption("입력값이 바뀌면 자동으로 T/Stage가 재계산됩니다. 'Stage 규칙 열기'를 누르면 규칙 검색 페이지에서 해당 Stage 이름 규칙을 자동 선택합니다.")

c1, c2, c3 = st.columns([1,1,1])

with c1:
    st.subheader("T")
    size_str = st.text_input("Tumor size (cm)", value="", help="예: 2.3")
    size = parse_size_cm(size_str)

    tis = st.checkbox("Tis (carcinoma in situ)", value=False)
    mia = st.checkbox("MIA (minimally invasive adenocarcinoma)", value=False, help="<=0.5cm일 때 T1mi")

    main_bronchus = st.checkbox("Main bronchus involvement", value=False)
    visceral_pleura = st.checkbox("Visceral pleural invasion", value=False)
    atelectasis = st.checkbox("Atelectasis / obstructive pneumonitis", value=False)

    chest_wall = st.checkbox("Chest wall / parietal pleura invasion", value=False)
    same_lobe = st.checkbox("Separate tumor nodule in same lobe", value=False)
    diff_lobe = st.checkbox("Separate tumor nodule in different ipsilateral lobe", value=False)

    critical_organs = st.checkbox("Invasion: diaphragm/mediastinum/heart/great vessels/RLN/vertebra/esophagus", value=False)

    T = compute_T(
        size_cm=size,
        mia=mia,
        main_bronchus=main_bronchus,
        visceral_pleura=visceral_pleura,
        atelectasis=atelectasis,
        chest_wall=chest_wall,
        same_lobe_nodule=same_lobe,
        diff_lobe_nodule=diff_lobe,
        critical_organs=critical_organs,
        tis=tis,
    )

with c2:
    st.subheader("N")
    N = st.radio("N category", ["N0","N1","N2","N3"], index=0, horizontal=False)
    n_desc = {
        "N0": "림프절 전이 없음",
        "N1": "같은 쪽 폐문/기관지 주위/폐내 림프절",
        "N2": "같은 쪽 종격동 또는 carinal 림프절",
        "N3": "반대쪽 종격동/폐문 또는 쇄골상 림프절",
    }
    st.caption(n_desc.get(N,""))

with c3:
    st.subheader("M")
    M = st.radio("M category", ["M0","M1a","M1b","M1c"], index=0, horizontal=False)
    m_desc = {
        "M0": "원격 전이 없음",
        "M1a": "반대쪽 폐 결절 또는 흉막/심낭 병변/삼출",
        "M1b": "단일 장기 단일 전이 병소",
        "M1c": "다발 원격 전이",
    }
    st.caption(m_desc.get(M,""))

stage = tnm_stage_group(T, N, M)

st.divider()
k1, k2 = st.columns([1,1])
with k1:
    st.metric("Computed T", T)
with k2:
    st.metric("Stage", stage)

if st.button("Stage 규칙 열기 (규칙 검색 페이지로 전달)"):
    st.session_state.rule_to_open = stage
    st.success("규칙 검색/편집 페이지로 이동하셔서 해당 Stage 규칙이 선택된 것을 확인하시면 됩니다.")
