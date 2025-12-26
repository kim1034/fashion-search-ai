# search_engine/musinsa.py
import sys
import os

# 현재 폴더(search_engine)의 부모 폴더를 경로에 추가해야 utils를 찾을 수 있음
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import utils # 같은 폴더에 있는 utils.py 불러오기
except ImportError:
    from . import utils # 패키지로 실행될 때

def search(keyword):
    print(f">>> [무신사] '{keyword}' 검색 시작...")
    driver = utils.get_driver()
    results = []
    
    try:
        # 1. 검색 페이지 이동
        url = f"https://www.musinsa.com/search/goods?keyword={keyword}"
        driver.get(url)
        utils.time.sleep(2) # 로딩 대기
        
        # 2. 스크롤
        utils.scroll_page(driver, 2)
        
        # 3. 데이터 추출 (무신사 이미지 셀렉터 사용)
        results = utils.smart_extract(driver, "무신사", "img")
        
    except Exception as e:
        print(f"!!! [무신사] 에러: {e}")
    finally:
        driver.quit()
        
    print(f">>> [무신사] {len(results)}개 찾음!")
    return results

# 테스트용 코드 (이 파일만 실행했을 때)
if __name__ == "__main__":
    data = search("청자켓")
    print(data)