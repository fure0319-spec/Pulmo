
import streamlit as st
from utils_rules import load_rules, categories, filter_rules

st.set_page_config(page_title="SOAP 빌더", layout="wide")
st.title("외래 기록(SOAP) 빌더")

FINAL_NOTE = "환자 P/E 및 검사 결과 확인하였으며, 검사 결과 설명하고, 경과 악화 시 병원 내원할 것 설명함"

@st.cache_data
def _rules():
    return load_rules()

rules = _rules()
cats = categories(rules)

if "soap" not in st.session_state:
    st.session_state.soap = {"S": [], "O": [], "A": [], "P": []}

left, right = st.columns([1, 2])

with left:
    st.subheader("규칙 검색")
    cat = st.selectbox("카테고리", cats, index=0)
    q = st.text_input("검색어", value="")
    filtered = filter_rules(rules, category=cat, query=q)[:200]
    pick = st.selectbox("규칙 선택", ["(선택)"] + [f"[{r['category']}] {r['name']}" for r in filtered])

    if pick != "(선택)":
        category_sel = pick.split("]")[0].strip("[")
        name_sel = pick.split("] ", 1)[1]
        rule = next((r for r in rules if r["category"]==category_sel and r["name"]==name_sel), None)
        if rule:
            st.caption("advice 미리보기")
            st.code(rule.get("advice",""), language="text")

            cols = st.columns(4)
            for i, sec in enumerate(["S","O","A","P"]):
                if cols[i].button(f"{sec}에 추가"):
                    st.session_state.soap[sec].append(rule.get("advice","").strip())
                    st.rerun()

    st.divider()
    if st.button("전체 초기화", type="secondary"):
        st.session_state.soap = {"S": [], "O": [], "A": [], "P": []}
        st.rerun()

with right:
    st.subheader("출력")
    extra = st.text_area("추가 메모(자유 텍스트)", value="", height=120)

    def _join(lines):
        lines = [x for x in lines if x and x.strip()]
        # 중복 제거(순서 유지)
        seen = set()
        out=[]
        for x in lines:
            if x not in seen:
                out.append(x)
                seen.add(x)
        return "\n".join(out)

    S = _join(st.session_state.soap["S"])
    O = _join(st.session_state.soap["O"])
    A = _join(st.session_state.soap["A"])
    P = _join(st.session_state.soap["P"])

    output = []
    if S: output.append("S:\n" + S)
    if O: output.append("O:\n" + O)
    if A: output.append("A:\n" + A)
    if P: output.append("P:\n" + P)
    if extra.strip(): output.append(extra.strip())
    output.append(FINAL_NOTE)

    st.code("\n\n".join(output), language="text")

    st.caption("웹에서는 OS 클립보드 직접 제어가 제한될 수 있어, 위 코드 블록에서 복사해 사용하시는 방식을 권장합니다.")

    # Remove item controls
    st.divider()
    st.subheader("항목 관리(삭제)")
    for sec in ["S","O","A","P"]:
        items = st.session_state.soap[sec]
        if not items:
            continue
        st.write(f"**{sec}**")
        for idx, txt in list(enumerate(items)):
            col1, col2 = st.columns([8,1])
            col1.write(txt[:120] + ("..." if len(txt)>120 else ""))
            if col2.button("삭제", key=f"del_{sec}_{idx}"):
                st.session_state.soap[sec].pop(idx)
                st.rerun()
