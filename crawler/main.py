import pandas as pd
# 우리가 만든 파일들 불러오기
import crawler_musinsa
import crawler_29cm
import crawler_wconcept
import crawler_zigzag

print("="*50)
print(">>> 통합 패션 크롤러를 가동합니다.")
print("="*50)

all_data = []

# 1. 각 사이트 수집 실행
# 필요 없는 사이트는 주석처리(#) 하면 건너뜁니다.
all_data += crawler_musinsa.run()
all_data += crawler_29cm.run()
all_data += crawler_wconcept.run()
all_data += crawler_zigzag.run()

# 2. 결과 저장
print("\n" + "="*50)
if len(all_data) > 0:
    df = pd.DataFrame(all_data)
    
    # 가격 정보 깔끔하게 정리 (콤마 제거 등)
    # df['가격'] = df['가격'].astype(str).str.replace(r'[^\d]', '', regex=True)
    
    filename = "fashion_ranking_all.csv"
    df.to_csv(filename, encoding="utf-8-sig", index=False)
    
    print(f">>> [최종 완료] 총 {len(df)}개의 상품 데이터를 저장했습니다!")
    print(f">>> 파일명: {filename}")
else:
    print(">>> [실패] 데이터를 하나도 수집하지 못했습니다.")