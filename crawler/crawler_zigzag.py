import utils
import time

def run():
    driver = utils.get_driver()
    try:
        print(">>> [지그재그] 접속 중...")
        driver.get("https://zigzag.kr/categories/-1?title=%EB%B2%A0%EC%8A%A4%ED%8A%B8")
        time.sleep(5) # 로딩 느림
        utils.scroll_page(driver, 7) # 스크롤 더 많이
        
        return utils.smart_extract(driver, "지그재그")
    except Exception as e:
        print(f"   !!! 지그재그 에러: {e}")
        return []
    finally:
        driver.quit()