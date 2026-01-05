
import streamlit as st

st.set_page_config(page_title="ILD 알고리즘", layout="wide")
st.title("ILD 진단 알고리즘 (조직검사/급성악화 포함)")

st.caption("원본(Tkinter) 알고리즘을 Streamlit로 그대로 이식했습니다. 결과가 나오면 해당 진단 규칙(name)을 규칙 페이지에서 바로 열 수 있습니다.")

# ====== 원본 globals 그대로 ======
========== ILD 진단 알고리즘(조직검사/급성악화 포함) ================= #

ILD_RULE_MAP = {
    "IPF": "IPF 진단 치료",
    "HP": "HP 진단 치료",
    "CTD-ILD": "CTD-ILD 진단 치료",
    "iNSIP": "iNSIP 진단 치료",
    "DIP": "DIP 진단 치료",
    "COP": "COP 진단치료",
    "AFOP": "AFOP 진단 치료",
    "AIP": "AIP 진단 치료",
    "idiopathic LIP": "idiopathic LIP 진단 치료",
    "PPFE": "PPFE",
    "Unclassifiable IIP": "Unclassifiable IIP",
}


# AE(급성악화) 상황에서 우선 열 규칙(name) 후보들.
# rules.xlsx에 아래 name이 존재하면 순서대로 열기를 시도합니다.
AE_RULE_SEQUENCE = [
    "ILD 급성악화 – 감별진단",
    "ILD 급성악화 – 초기 처치",
    "ILD 급성악화 – 스테로이드",
    "ILD 급성악화 – 기계환기 판단",
    "ILD 급성악화 – 예후 및 목표 치료",
    "ILD 급성악화",  # 사용자가 단일 이름으로 만들어둔 경우 대비
]




def _open_rule(name: str):
    st.session_state.rule_to_open = name
    try:
        st.switch_page("pages/1_규칙_검색_편집.py")
    except Exception:
        st.info("규칙 검색/편집 페이지로 이동하신 뒤, 전달된 규칙이 선택되는지 확인해 주세요.")

tabs = st.tabs(["AE(급성악화)", "만성 진단"])

with tabs[0]:
    st.subheader("급성악화(AE) 평가")
    st.markdown("- AE-IPF(2016 개정) 핵심 요소(간이) 기반")

    ae_sudden30 = st.checkbox("최근 30일 이내 급성 악화(호흡곤란/저산소증 급격 악화...)")
    ae_known_ipf = st.checkbox("기저에 IPF(또는 fibrotic ILD) 진단/강력 의심")
    ae_new_bilat_ggo = st.checkbox("HRCT에서 신규 양측 GGO/경화(기저 UIP 위에) 동반")
    ae_not_hf_overload = st.checkbox("심부전/수액과다로 설명되기 어려움")

    if st.button("AE 판정", key="btn_ae"):
        checks = [ae_sudden30, ae_known_ipf, ae_new_bilat_ggo, ae_not_hf_overload]
        if sum(checks) >= 3 and ae_sudden30 and ae_new_bilat_ggo:
            st.success("✅ AE-IPF 의심(간이 기준)")
            st.write("- 최근 30일 이내 급성 악화 + CT 신규 양측 GGO/경화 + HF/수액과다로 설명 어려움")
            st.write("➡ AE 관련 규칙을 순서대로 열기(존재하는 항목부터).")
            st.session_state.ae_candidates = AE_RULE_SEQUENCE
        else:
            st.warning("⚠ 급성악화(AE)는 의심될 수 있으나, AE-IPF 간이 기준을 충분히 만족하지 않습니다.")
            st.session_state.ae_candidates = []

    cand = st.session_state.get("ae_candidates", [])
    if cand:
        st.divider()
        st.write("열기 후보(우선순위):")
        for nm in cand:
            if st.button(f"규칙 열기: {nm}", key=f"open_ae_{nm}"):
                _open_rule(nm)

with tabs[1]:
    st.subheader("만성 ILD 진단(간이)")
    st.markdown("**우선순위:** 원인 단서(CTD/HP/PPFE/LIP/OP/DAD/흡연) → Fibrotic 여부 + UIP 패턴")

    fibrotic = st.radio("A. HRCT에서 fibrosis 여부", ["fibrotic", "non-fibrotic"], index=0, horizontal=True)
    uip = st.radio("B. (Fibrotic ILD) HRCT UIP 패턴", ["uip", "probable", "indeterminate", "alternative"], index=2, horizontal=True)

    st.markdown("C. 원인 단서(있으면 해당 질환 우선)")
    ctd_clue = st.checkbox("CTD 단서(관절/피부/근염/레이노 등) 또는 자가항체 양성")
    hp_clue = st.checkbox("HP 단서(노출력+air-trapping/mosaic 등)")
    smoking_related = st.checkbox("흡연 관련 ILD 의심(DIP 등)")
    op_pattern = st.checkbox("OP 패턴(이동성 침윤/patchy consolidation) → COP 우선")
    dad_ards_like = st.checkbox("급성 ARDS-like + DAD 의심 → AIP/AFOP 감별(조직검사 고려)")
    lip_clue = st.checkbox("LIP 단서(낭종+GGO, Sjogren/HIV 배제 후)")
    ppfe_clue = st.checkbox("상엽 흉막하 우세 섬유화/반복 기흉 → PPFE 의심")

    def diagnose():
        if ctd_clue:
            return "CTD-ILD", "CTD 단서가 있어 CTD-ILD 우선 고려(자가항체/류마협진/MDD)."
        if hp_clue:
            return "HP", "노출력/air-trapping 등 HP 단서가 있어 HP 우선 고려(항원 회피/필요 시 BAL/조직)."
        if ppfe_clue:
            return "PPFE", "상엽 흉막하 우세 섬유화/pleural thickening → PPFE 의심."
        if lip_clue:
            return "idiopathic LIP", "LIP 단서(낭종+GGO). 이차 원인 배제 후 idiopathic LIP 고려."
        if op_pattern:
            return "COP", "OP 패턴(이동성/patchy consolidation). 이차 원인 배제 후 COP 고려."
        if dad_ards_like:
            return "AIP", "급성 ARDS-like + DAD 의심. 원인 배제 후 AIP/AFOP 감별(조직검사 고려)."
        if smoking_related:
            return "DIP", "흡연 관련 ILD(DIP 등) 가능. 금연 및 스테로이드 반응 가능."

        if fibrotic == "fibrotic":
            if uip in ("uip", "probable"):
                return "IPF", ("Fibrotic ILD에서 UIP/Probable UIP이며 뚜렷한 다른 원인이 없어 IPF 가능성이 높습니다.\n"
                               "- 다른 원인 배제 후: 조직검사 없이도 진단 가능할 수 있습니다.")
            return "iNSIP", ("UIP로 확정되지 않는 fibrotic ILD(Indeterminate/Alternative).\n"
                            "➡ NSIP/기타 IIP 감별이 필요하며 치료결정(면역억제 vs 항섬유화)에 중요하면 조직검사(TBLC/SLB)를 고려합니다.")
        else:
            return "iNSIP", ("Non-fibrotic ILD에서 NSIP 패턴 가능.\n"
                            "CTD/HP/약물/감염 배제 후 필요 시 조직검사로 확진합니다.")

    if st.button("진단 도출", key="btn_chronic"):
        dx, reason = diagnose()
        st.success(f"✅ 제안 진단: {dx}")
        st.write(reason)

        if dx in ("iNSIP", "AIP") or (fibrotic=="fibrotic" and uip in ("indeterminate","alternative")):
            st.info("조직검사 고려 포인트: HRCT가 UIP/UIP-Probable이 아니거나 임상-영상 불일치 시 / MDD 후 결정")

        rule_name = ILD_RULE_MAP.get(dx, dx)
        st.divider()
        if st.button(f"규칙 열기: {rule_name}", key="open_dx_rule"):
            _open_rule(rule_name)
