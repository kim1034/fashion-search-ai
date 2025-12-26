from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd 
import time
import random # 사람처럼 보이기 위해 랜덤 시간 대기

# --- 1. 설정 및 공통 함수 ---
def get_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    # 봇 탐지 회피용 헤더
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def scroll_page(driver, times=5):
    print("   ㄴ 스크롤 내려서 데이터 로딩 중...")
    for _ in range(times):
        driver.execute_script("window.scrollBy(0, 1500);")
        time.sleep(random.uniform(1.5, 2.5)) # 랜덤하게 쉬기

# --- [핵심] 범용 상품 수집기 (Step 17 기술 적용) ---
def universal_extractor(driver, site_name):
    print(f"   ㄴ [{site_name}] 데이터 추출 시작...")
    data = []
    seen_images = set()

    # 1. 사이트마다 이미지 태그를 찾는 방법이 조금씩 다를 수 있음
    img_selector = "img" 
    if site_name == "무신사":
        img_selector = "[data-mds='Image'] img" # 무신사 전용 규칙
    
    # 화면의 모든 이미지 찾기
    images = driver.find_elements(By.CSS_SELECTOR, img_selector)
    
    for img in images:
        try:
            # 이미지 주소
            src = img.get_attribute("src")
            if not src or src in seen_images or "icon" in src or "logo" in src:
                continue
                
            # 부모를 타고 올라가며 '가격' 찾기 (최대 6단계)
            container = img
            price = ""
            name = ""
            link = ""
            found_product = False
            
            for _ in range(6):
                try:
                    container = container.find_element(By.XPATH, "./..")
                    
                    # 텍스트 전체 가져오기
                    text_blob = container.text
                    lines = text_blob.split('\n')
                    
                    # 가격 패턴 찾기 (숫자 + 원, 또는 30,000 같은 형태)
                    for line in lines:
                        line = line.strip()
                        # 가격 조건: '원'이 있거나, 콤마가 있고 숫자로 된 것 (단, 너무 짧거나 긴 건 제외)
                        if ("원" in line or ("," in line and line.replace(',', '').isdigit())) and len(line) < 15:
                            price = line
                            found_product = True
                            break
                    
                    if found_product:
                        # 링크 찾기
                        try:
                            link = container.find_element(By.TAG_NAME, "a").get_attribute("href")
                        except: pass
                        
                        # 이름 찾기 (가격이 아닌 가장 긴 텍스트를 이름으로 추정)
                        candidates = [l for l in lines if l != price and len(l) > 5]
                        if candidates:
                            name = candidates[0]
                        break
                except:
                    break
            
            if found_product and name and price:
                # 데이터 저장
                seen_images.add(src)
                data.append({
                    "쇼핑몰": site_name,
                    "상품명": name,
                    "가격": price,
                    "링크": link,
                    "이미지": src
                })
                # print(f"      [수집] {name[:10]}.. | {price}")
                
        except: continue
        
    print(f"   ㄴ [{site_name}] {len(data)}개 수집 성공!")
    return data

# --- 2. 사이트별 크롤링 실행 ---

def run_crawling():
    driver = get_driver()
    all_data = []

    # [1] 무신사
    try:
        print("\n>>> 1. 무신사 접속 중...")
        driver.get("https://www.musinsa.com/main/musinsa/ranking?gf=A")
        time.sleep(3)
        scroll_page(driver, 5)
        all_data += universal_extractor(driver, "무신사")
    except Exception as e:
        print(f"   !!! 무신사 실패: {e}")

    # [2] 29CM (여성 베스트)
    try:
        print("\n>>> 2. 29CM 접속 중...")
        driver.get("https://product.29cm.co.kr/catalog/best-items?category_large_code=268100100") # 여성의류 베스트
        time.sleep(3)
        scroll_page(driver, 5)
        all_data += universal_extractor(driver, "29CM")
    except Exception as e:
        print(f"   !!! 29CM 실패: {e}")

    # [3] W Concept (베스트)
    try:
        print("\n>>> 3. W Concept 접속 중...")
        driver.get("https://www.wconcept.co.kr/Best") 
        time.sleep(3)
        
        # W컨셉은 팝업창이 뜰 수 있어서 닫기 시도 (선택)
        try: driver.find_element(By.CSS_SELECTOR, ".btn_close").click()
        except: pass
        
        scroll_page(driver, 5)
        all_data += universal_extractor(driver, "W컨셉")
    except Exception as e:
        print(f"   !!! W Concept 실패: {e}")

    # [4] 지그재그 (직잭 베스트)
    try:
        print("\n>>> 4. 지그재그 접속 중...")
        driver.get("https://zigzag.kr/categories/-1?title=%EB%B2%A0%EC%8A%A4%ED%8A%B8") # 베스트 페이지
        time.sleep(5) # 지그재그는 로딩이 느림
        scroll_page(driver, 7) # 더 많이 스크롤
        all_data += universal_extractor(driver, "지그재그")
    except Exception as e:
        print(f"   !!! 지그재그 실패: {e}")

    driver.quit()

    # --- 3. 저장 ---
    if all_data:
        df = pd.DataFrame(all_data)
        # 가격 정제 (원, 콤마 제거)
        # df['가격'] = df['가격'].str.replace('원', '').str.replace(',', '') 
        
        df.to_csv("fashion_ranking_all.csv", encoding="utf-8-sig", index=False)
        print("\n" + "="*50)
        print(f">>> 대성공! 총 {len(df)}개의 통합 데이터를 저장했습니다.")
        print(">>> 이제 'python make_embeddings.py'를 실행해서 AI에게 공부시키세요!")
        print("="*50)
    else:
        print("\n>>> 데이터 수집 실패. 하나도 못 건졌습니다.")

if __name__ == "__main__":
    run_crawling()