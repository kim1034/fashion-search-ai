import utils
import time

def run():
    driver = utils.get_driver()
    try:
        print(">>> [무신사] 접속 중...")
        driver.get("https://www.musinsa.com/main/musinsa/ranking?gf=A")
        time.sleep(3)
        utils.scroll_page(driver, 5)
        
        # 무신사 전용 이미지 선택자 사용
        return utils.smart_extract(driver, "무신사", "[data-mds='Image'] img")
    except Exception as e:
        print(f"   !!! 무신사 에러: {e}")
        return []
    finally:
        driver.quit()