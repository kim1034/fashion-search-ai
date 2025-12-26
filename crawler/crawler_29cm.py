import utils
import time

def run():
    driver = utils.get_driver()
    try:
        print(">>> [29CM] 접속 중...")
        # 베스트 카테고리
        driver.get("https://home.29cm.co.kr/best-products?period=HOURLY&ranking=POPULARITY&gender=F&age=30")
        time.sleep(3)
        utils.scroll_page(driver, 5)
        
        return utils.smart_extract(driver, "29CM")
    except Exception as e:
        print(f"   !!! 29CM 에러: {e}")
        return []
    finally:
        driver.quit()