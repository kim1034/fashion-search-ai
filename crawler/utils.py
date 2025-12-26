from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import re
from urllib.parse import urljoin

def get_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def scroll_page(driver, times=10):
    print(f"   ㄴ [스크롤] 데이터 로딩 중... ({times}회)")
    for _ in range(times):
        driver.execute_script("window.scrollBy(0, 1500);")
        time.sleep(1.5)

# 링크 수리공 (무신사 등)
def repair_link(site_name, link):
    if not link: return ""
    if site_name == "무신사":
        match = re.search(r'(\d+)', link)
        if match:
            goods_id = match.group(1)
            if len(goods_id) > 4:
                return f"https://www.musinsa.com/app/goods/{goods_id}"
    return link

# [핵심] 너그러운 수집가
def smart_extract(driver, site_name, img_selector="img"):
    data = []
    seen_ids = set() 
    base_url = driver.current_url

    images = driver.find_elements(By.CSS_SELECTOR, img_selector)
    print(f"   ㄴ [{site_name}] 이미지 {len(images)}개 발견. 분석 시작...")
    
    count = 0
    fail_count = 0 # 실패 로그용
    
    for img in images:
        try:
            src = img.get_attribute("src")
            if src: src = urljoin(base_url, src)

            # 광고/로고/아이콘 제외
            if not src or "icon" in src or "logo" in src or "banner" in src or "data:image" in src:
                continue
            
            container = img
            found_link = ""
            found_price = ""
            found_name = ""
            
            # 부모를 타고 올라가며 탐색 (5단계로 깊이 증가)
            for _ in range(5): 
                try:
                    container = container.find_element(By.XPATH, "./..")
                    
                    # 1. 링크 찾기 (재귀적으로 찾기)
                    if not found_link:
                        # (A) 현재 박스가 a 태그
                        if container.tag_name == 'a':
                            raw_link = container.get_attribute("href")
                        # (B) 박스 안에 a 태그 존재
                        else:
                            try:
                                link_el = container.find_element(By.TAG_NAME, "a")
                                raw_link = link_el.get_attribute("href")
                            except: raw_link = ""
                        
                        if raw_link and "javascript" not in raw_link:
                            full_link = urljoin(base_url, raw_link)
                            found_link = repair_link(site_name, full_link)

                    # 2. 가격 찾기 (정규표현식으로 강력하게 찾기)
                    # 텍스트 전체에서 "숫자+콤마+숫자" 패턴이 있는지 스캔
                    text = container.text
                    if text:
                        # 무신사 data-price 확인
                        if site_name == "무신사":
                            try:
                                dp = container.get_attribute("data-price")
                                if not dp and container.tag_name == 'a': 
                                    pass
                                elif not dp:
                                    try: dp = container.find_element(By.TAG_NAME, "a").get_attribute("data-price")
                                    except: pass
                                
                                if dp: found_price = f"{int(dp):,}"
                            except: pass

                        # 텍스트 기반 가격 찾기 (다른 사이트용)
                        if not found_price:
                            # 1,000 ~ 9,999,999 패턴 찾기
                            price_match = re.search(r'[\d,]+00원?', text)
                            if price_match:
                                temp_price = price_match.group()
                                # 너무 긴 숫자는 전화번호일 수 있으니 제외
                                if len(temp_price) < 15:
                                    found_price = temp_price

                    # 3. 상품명 찾기 (가격 뺀 나머지 중 긴 것)
                    if not found_name and text:
                        lines = text.split('\n')
                        for line in lines:
                            line = line.strip()
                            if len(line) > 3 and line != found_price and "%" not in line and "구매" not in line:
                                found_name = line
                                break # 첫 번째 긴 줄을 이름으로

                    # 다 찾았으면 탈출
                    if found_link and found_price:
                        break
                except:
                    break

            # --- 저장 ---
            if not found_name: found_name = "상품명 정보 없음"

            if found_link and found_price and found_link.startswith("http"):
                if found_link in seen_ids: continue
                seen_ids.add(found_link)
                
                data.append({
                    "쇼핑몰": site_name,
                    "상품명": found_name,
                    "가격": found_price,
                    "링크": found_link, 
                    "이미지": src
                })
                count += 1
            else:
                # [디버깅] 왜 실패했는지 5개만 출력해봄
                if fail_count < 3:
                    missing = []
                    if not found_link: missing.append("링크X")
                    if not found_price: missing.append("가격X")
                    print(f"      [탈락] {', '.join(missing)} | 텍스트: {container.text[:20]}...")
                    fail_count += 1
                
        except Exception as e:
            continue
            
    print(f"   ㄴ [{site_name}] 최종 {count}개 상품 수집 성공!")
    return data