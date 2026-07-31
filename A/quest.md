✅ 기본 확인

원본: 101,766행 × 50열
결측치는 ?로 표기돼 있어서 NaN으로 변환 필요했음
결측 비율: weight 96.9%, max_glu_serum 94.7%, A1Cresult 83.3%, medical_specialty 49.1%, payer_code 39.6%, race 2.2%, diag_2/3 <2%

✅ 정제 작업

사망(Expired, discharge_disposition_id 11/19/20/21) 환자 1,652건 제거 → 101,766 → 100,114행
불필요 컬럼 7개 제거: weight, max_glu_serum, medical_specialty, payer_code, diag_1, diag_2, diag_3 (결측 과다 또는 분석 질문과 무관)
race의 결측치 → 'Unknown' 범주로 채움
A1Cresult는 NaN 그대로 유지 (검사 안 함을 의미하는 유효한 값이라 건드리지 않음)

✅ 중복 확인 완료

encounter_id 중복: 0건
전체 행 완전 중복: 0건
patient_nbr 중복 29,675건 → 환자당 첫 입원만 남기는 걸로 제거 완료

✅ 배정 일관성 확인 완료

readmitted: NO, >30, <30 — 예상한 3개 값만 있음, 정상
age: [0-10) ~ [90-100), 10개 구간 전부 정상
A1Cresult: nan(검사안함), >7, >8, Norm — 예상한 값만 있음, 정상
gender: Female, Male, Unknown/Invalid 값 발견 → 이번 분석에서 gender를 사용하지 않으므로 그대로 두되, 존재를 확인해둠

✅ SRM 점검 (변형 적용)

A1C 검사함: 12,878명
A1C 검사 안함: 57,561명
검사함:검사안함 비율이 약 18:82로 크게 치우쳐 있음



4단계 완료 요약

결과: 검사함 8.39% vs 검사안함 9.06%, 절대차이 -0.68%p, 상대차이 0.93배
χ²(1)=5.81, p=.008(단측) → 통계적으로 유의
95% CI [-1.21%p, -0.14%p] → 0을 포함 안 해서 유의성과 일치, 폭이 좁아 추정이 정밀함
Cramér's V=0.009 → 효과크기는 무시할 수 있는 수준
핵심 해석: "유의하지만 실질적 효과는 미미함" — 표본이 커서 생긴 결과