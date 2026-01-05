
import streamlit as st

st.set_page_config(page_title="호흡기도우미 (웹)", layout="wide")

st.title("호흡기도우미 (웹)")
st.caption("데스크톱(Tkinter) 버전을 Streamlit로 이식한 웹 버전 뼈대입니다. 좌측 페이지 메뉴에서 기능을 선택하세요.")

st.markdown("""
### 포함된 페이지
- **규칙 검색/편집**: rules.xlsx 기반 검색/추가/수정/삭제
- **Lung TNM v8**: T/N/M 입력 → Stage 자동 산출, Stage 이름 규칙 바로 열기
- **SOAP 빌더**: 규칙을 S/O/A/P로 쌓아 출력(복사)
- **외래기록(체크리스트)**: 최소 템플릿(예시) + 자유 텍스트 출력
- **ILD 알고리즘(자리표시자)**: 추후 체크 기반 플로우로 확장
""")

st.info("배포 시에는 병원 내부망 + 인증(SSO/BasicAuth) + HTTPS 프록시(Nginx) 구성을 권장합니다.")
