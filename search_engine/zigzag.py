# search_engine/zigzag.py
import sys
import os

# 부모 폴더 경로 추가 (utils 모듈을 찾기 위함)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import utils
except ImportError:
    from . import utils

def search(keyword):
    print(f">>> [지그재그] '{keyword}' 검색 시작...")
    driver = utils.get_driver()
    results = []
    
    try:
        # 1. 지그재그 검색 페이지 이동
        url = f"https://zigzag.kr/search?keyword={keyword}"
        driver.get(url)
        
        # 지그재그는 로딩이 좀 느려서 3초 대기
        utils.time.sleep(3) 
        
        # 2. 스크롤 (지그재그는 무한 스크롤이라 좀 더 많이)
        utils.scroll_page(driver, 3)
        
        # 3. 데이터 추출
        # 지그재그는 이미지가 div 안에 숨어있는 경우가 많아 div까지 포함해서 스캔
        results = utils.smart_extract(driver, "지그재그", "img")
        
    except Exception as e:
        print(f"!!! [지그재그] 에러: {e}")
    finally:
        driver.quit()
        
    print(f">>> [지그재그] {len(results)}개 찾음!")
    return results

# 테스트용 실행 코드
if __name__ == "__main__":
    data = search("청자켓")
    print(data)