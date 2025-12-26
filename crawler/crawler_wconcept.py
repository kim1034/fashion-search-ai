import utils
import time
from selenium.webdriver.common.by import By

def run():
    driver = utils.get_driver()
    try:
        print(">>> [W컨셉] 접속 중...")
        driver.get("https://display.wconcept.co.kr/rn/best?displayCategoryType=10101&gnbType=Y")
        time.sleep(3)
        
        # 팝업 닫기 시도
        try: driver.find_element(By.CSS_SELECTOR, ".btn_close").click()
        except: pass
        
        utils.scroll_page(driver, 5)
        return utils.smart_extract(driver, "W컨셉")
    except Exception as e:
        print(f"   !!! W컨셉 에러: {e}")
        return []
    finally:
        driver.quit()