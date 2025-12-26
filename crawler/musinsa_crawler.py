from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import re

# 1. 설정
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("detach", True)

print(">>> 브라우저를 실행합니다...")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

url = "https://www.musinsa.com/main/musinsa/ranking?gf=A&storeCode=musinsa&sectionId=200&contentsId=&categoryCode=000&ageBand=AGE_BAND_ALL"
driver.get(url)

print(">>> 데이터 로딩 대기 중...")

try:
    wait = WebDriverWait(driver, 20)
    # 이미지나 가격표가 뜰 때까지 대기
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-mds='Image']")))

    print(">>> 이미지를 로딩하기 위해 스크롤을 내립니다...")
    for _ in range(8):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(1.0)

    print(">>> [이미지]와 [가격표]가 함께 있는 '진짜 상품'만 찾아냅니다...")

    # 1. 화면의 모든 'MDS 이미지 박스'를 찾습니다.
    image_boxes = driver.find_elements(By.CSS_SELECTOR, "[data-mds='Image']")
    
    data_list = []
    seen_images = set() # 중복 방지용

    for img_box in image_boxes:
        try:
            # 2. 이미지 주소 추출
            img_url = ""
            try:
                img_tag = img_box.find_element(By.TAG_NAME, "img")
                img_url = img_tag.get_attribute("src")
            except:
                continue # 이미지 없으면 패스

            if not img_url or img_url in seen_images:
                continue
            seen_images.add(img_url)

            # 3. [핵심] 부모로 올라가면서 '가격표'를 가진 컨테이너 찾기
            # 최대 5단계 위까지 올라가 보며 가격표가 있는지 확인합니다.
            container = img_box
            found_price = False
            price_text = ""
            discount_text = "0%"
            
            for _ in range(5): # 부모, 할아버지, 증조할아버지... 탐색
                try:
                    container = container.find_element(By.XPATH, "./..")
                    
                    # 이 컨테이너 안에 가격표 클래스가 있는지 확인
                    # (회원님이 찾아주신 UIProductColumn__PriceText 클래스 사용)
                    price_els = container.find_elements(By.XPATH, ".//*[contains(@class, 'UIProductColumn__PriceText')]")
                    
                    if len(price_els) > 0:
                        # 가격표 발견! -> 이건 상품이다.
                        found_price = True
                        
                        # 가격과 할인율 구분해서 저장
                        for el in price_els:
                            txt = el.text.strip()
                            if "%" in txt:
                                discount_text = txt
                            elif "원" in txt or (txt.replace(',','').isdigit() and len(txt)>3):
                                price_text = txt
                        break # 컨테이너 찾았으니 루프 종료
                except:
                    break

            # 가격표를 못 찾았으면 배너라고 판단하고 스킵
            if not found_price or not price_text:
                continue

            # 4. 링크 찾기 (찾은 컨테이너 안에서 a 태그 찾기)
            link = ""
            try:
                link_tag = container.find_element(By.TAG_NAME, "a")
                link = link_tag.get_attribute("href")
            except: 
                # a 태그가 없다면 컨테이너 자체가 클릭 가능한지 확인 (button 등)
                pass

            # 5. 텍스트 정보 (브랜드, 상품명)
            # 찾아주신 클래스 이름 규칙 적용
            brand = ""
            name = ""
            try:
                brand = container.find_element(By.XPATH, ".//*[contains(@class, 'text-etc_11px_semibold')]").text
            except: pass
            
            try:
                name = container.find_element(By.XPATH, ".//*[contains(@class, 'text-body_13px_reg')]").text
            except: pass

            # 만약 클래스로 못 찾았으면, 컨테이너 텍스트를 분석해서 보완
            if not name:
                lines = container.text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and line != price_text and line != discount_text and line != brand:
                        name = line
                        break

            # 로그 출력
            print(f"[수집] {brand} | {name[:10]}.. | {price_text} | {discount_text}")

            data_list.append({
                "브랜드": brand,
                "상품명": name,
                "가격": price_text,
                "할인율": discount_text,
                "링크": link,
                "이미지": img_url
            })

        except Exception as e:
            continue

    print("-" * 50)
    print(f">>> 총 {len(data_list)}개의 상품 정보를 확보했습니다.")

    if len(data_list) > 0:
        df = pd.DataFrame(data_list)
        df.to_csv("musinsa_ranking_final.csv", encoding="utf-8-sig", index=False)
        print(">>> 'musinsa_ranking_final.csv' 저장 완료! (AI 검색으로 넘어가세요)")
    else:
        print(">>> 데이터 수집 실패. (여전히 0개라면 HTML 구조가 완전히 다름)")

except Exception as e:
    print(f"\n[오류] : {e}")

driver.quit()