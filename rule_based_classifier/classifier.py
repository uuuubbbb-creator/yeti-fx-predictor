# classifier.py

def classify_customer_sensitivity_interactive_with_tiered_reason_score():
    """
    사용자로부터 직접 입력을 받아 환율 민감도 그룹을 판단합니다.
    """
    print("고객 비용 민감도 분석을 위한 정보 입력")

    # 1. 여행사 상품 구매 시기 입력
    while True:
        try:
            purchase_time = int(input(
                "AA.[해외] Q1-1. 여행사 상품 구매 시기는 언제였습니까? (숫자로 입력)\n"
                "  1: 1년 이내, 2: 6개월 이내, 3: 3개월 이내, 4: 2개월 이내, 5: 1개월 이내,\n"
                "  6: 2주 이내, 7: 1주 이내, 8: 3일 이내, 9: 당일\n"
                "  > "
            ))
            if 1 <= purchase_time <= 9:
                break
            else:
                print("1부터 9 사이의 숫자를 입력해주세요.")
        except ValueError:
            print("잘못된 입력입니다. 숫자를 입력해주세요.")

    # 2. 여행지 선택 이유 입력
    reason_map = {
        1: '여행지 지명도', 2: '볼거리 제공', 3: '저렴한 여행경비', 4: '이동 거리',
        5: '여행할수있는시간', 6: '숙박시설', 7: '쇼핑', 8: '음식',
        9: '교통편', 10: '체험 프로그램 유무', 11: '경험자의 추천',
        12: '관광지 편의시설', 13: '교육성', 14: '여행 동반자 유형', 15: '기타'
    }
    print("\nAA.[해외] Q3. 여행지 선택 이유를 3가지 선택해주세요.")
    selection_reasons_input = {}
    for i in range(1, 4):
        while True:
            try:
                reason = int(input(f"  {i}순위 선택 이유 ({', '.join([f'{k}: {v}' for k, v in reason_map.items()])})\n  > "))
                if 1 <= reason <= 15:
                    selection_reasons_input[i] = reason
                    break
                else:
                    print("1부터 15 사이의 숫자를 입력해주세요.")
            except ValueError:
                print("잘못된 입력입니다. 숫자를 입력해주세요.")

    # 3. 예상 여행 총경비 입력
    while True:
        try:
            estimated_cost = int(input("\nB. 여행 총경비 (원): "))
            if estimated_cost >= 0:
                break
            else:
                print("0 이상의 숫자를 입력해주세요.")
        except ValueError:
            print("잘못된 입력입니다. 숫자를 입력해주세요.")

    # 4. 월 평균 본인 소득 입력
    income_map = {
        1: '소득없음', 2: '100만원 미만', 3: '100~200만원', 4: '200~300만원', 5: '300~400만원',
        6: '400~500만원', 7: '500~600만원', 8: '600~700만원', 9: '700~800만원',
        10: '800~900만원', 11: '900~1000만원', 12: '1000만원 이상'
    }
    while True:
        try:
            monthly_income = int(input(
                "\nDQ6. 월 평균 본인 소득 구간 (숫자로 입력)\n"
                f"  ({', '.join([f'{k}: {v}' for k, v in income_map.items()])})\n"
                "  > "
            ))
            if 1 <= monthly_income <= 12:
                break
            else:
                print("1부터 12 사이의 숫자를 입력해주세요.")
        except ValueError:
            print("잘못된 입력입니다. 숫자를 입력해주세요.")

    # 점수 계산
    score_time = 1 if purchase_time in [5, 6] else -1 if purchase_time in [1, 2] else 0
    score_reason = 3 if selection_reasons_input.get(1) == 3 else 2 if selection_reasons_input.get(2) == 3 else 1 if selection_reasons_input.get(3) == 3 else 0
    score_income = 1 if monthly_income in [1, 2, 3] else -1 if monthly_income in [9, 10, 11, 12] else 0

    sensitivity_score = score_time + score_reason + score_income
    result_group = '고민감 그룹' if sensitivity_score >= 0 else '저민감 그룹'

    print(f"\n--- 분석 결과 ---")
    print(f"민감도 점수: {sensitivity_score}")
    print(f"이 고객은 '{result_group}'에 해당합니다.\n")

    return result_group
