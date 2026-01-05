
# 호흡기도우미 (Streamlit)

## 실행
1) rules.xlsx를 app.py와 같은 폴더에 두세요.
2) 설치:
   pip install -r requirements.txt
3) 실행:
   streamlit run app.py

## 환경변수(선택)
- RULES_XLSX: rules 파일 경로 (기본: rules.xlsx)
- RULES_LOCK: 락 파일 경로 (기본: rules.xlsx.lock)

## 구성
- app.py: 홈
- pages/1_규칙_검색_편집.py
- pages/2_Lung_TNM_v8.py
- pages/3_SOAP_빌더.py
- pages/4_외래기록_체크리스트.py
- pages/5_ILD_알고리즘.py
- utils_rules.py, utils_tnm.py

## 배포(병원 보안정책 대응)
- 내부망(인트라넷)에서만 서비스
- Reverse proxy(Nginx) + HTTPS
- 인증(SSO/BasicAuth) + 접근 IP 제한
- PHI 저장 금지(세션 메모리만 사용 권장)
