
import streamlit as st
from utils_rules import load_rules, save_rules, categories, filter_rules, upsert_rule, delete_rule

st.set_page_config(page_title="규칙 검색/편집", layout="wide")

@st.cache_data
def _cached_rules():
    return load_rules()

def _refresh_cache():
    st.cache_data.clear()

st.title("규칙 검색/편집 (rules.xlsx)")

# Load
try:
    rules = _cached_rules()
except Exception as e:
    st.error(f"rules.xlsx 로딩 오류: {e}")
    st.stop()

cats = categories(rules)

# If coming from TNM page
if "rule_to_open" in st.session_state and st.session_state.rule_to_open:
    preset_name = st.session_state.rule_to_open
else:
    preset_name = None

left, right = st.columns([1, 2])

with left:
    st.subheader("필터")
    cat = st.selectbox("카테고리", cats, index=0, key="rules_cat")
    q = st.text_input("검색어", value="", key="rules_q")
    filtered = filter_rules(rules, category=cat, query=q)

    names = [f"[{r['category']}] {r['name']}" for r in filtered]
    options = ["(선택)"] + names

    default_index = 0
    if preset_name:
        for i, opt in enumerate(options):
            if opt.endswith(f"] {preset_name}"):
                default_index = i
                break

    sel = st.selectbox("규칙 선택", options, index=default_index, key="rules_sel")

    st.divider()
    st.subheader("새 규칙/수정")
    with st.form("rule_form", clear_on_submit=False):
        c = st.text_input("category", value="" if sel=="(선택)" else sel.split("]")[0].strip("["))
        n = st.text_input("name", value="" if sel=="(선택)" else sel.split("] ",1)[1])
        kw = st.text_input("keywords (comma-separated)", value="")
        adv = st.text_area("advice", value="", height=180)

        submitted = st.form_submit_button("저장(추가/수정)")
        if submitted:
            try:
                rule = {
                    "category": c.strip(),
                    "name": n.strip(),
                    "keywords": [k.strip() for k in (kw or "").split(",") if k.strip()],
                    "advice": adv or "",
                }
                new_rules, created = upsert_rule(rules, rule)
                save_rules(new_rules)
                _refresh_cache()
                st.success("추가되었습니다." if created else "수정되었습니다.")
                st.rerun()
            except Exception as e:
                st.error(f"저장 실패: {e}")

    if sel != "(선택)":
        if st.button("선택 규칙 삭제", type="secondary"):
            try:
                category_sel = sel.split("]")[0].strip("[")
                name_sel = sel.split("] ", 1)[1]
                new_rules = delete_rule(rules, category_sel, name_sel)
                save_rules(new_rules)
                _refresh_cache()
                st.success("삭제되었습니다.")
                st.session_state.rule_to_open = None
                st.rerun()
            except Exception as e:
                st.error(f"삭제 실패: {e}")

with right:
    st.subheader("내용")
    if sel == "(선택)":
        st.info("좌측에서 규칙을 선택해 주세요.")
    else:
        category_sel = sel.split("]")[0].strip("[")
        name_sel = sel.split("] ", 1)[1]
        rule = next((r for r in rules if r["category"]==category_sel and r["name"]==name_sel), None)
        if not rule:
            st.warning("규칙을 찾지 못했습니다. 필터를 조정해 보세요.")
        else:
            st.markdown(f"**[{rule['category']}] {rule['name']}**")
            if rule.get("keywords"):
                st.caption("keywords: " + ", ".join(rule["keywords"]))
            st.code(rule.get("advice",""), language="text")

            # preload form values into session state for editing convenience
            if st.button("이 규칙을 편집 폼에 불러오기"):
                st.session_state["rule_form_category"] = rule["category"]
                st.session_state["rule_form_name"] = rule["name"]
                st.session_state["rule_form_keywords"] = ", ".join(rule.get("keywords", []))
                st.session_state["rule_form_advice"] = rule.get("advice","")
                st.info("좌측 폼에 직접 복사/붙여넣기 방식으로 수정하시면 됩니다. (웹 보안 정책상 자동 주입은 최소화했습니다.)")
