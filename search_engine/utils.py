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
    
    # [핵심 변경 1] 헤드리스 모드 활성화 (화면에 창을 띄우지 않음)
    # 'headless=new'는 기존 headless보다 탐지될 확률이 낮습니다.
    options.add_argument("--headless=new") 
    
    # [핵심 변경 2] 화면 크기 고정 (창이 없어도 있는 것처럼 속임)
    # 이게 없으면 모바일 화면으로 인식되어 29CM 등이 구조를 바꿀 수 있음
    options.add_argument("--window-size=1920,1080")
    
    # [스텔스 유지] 봇 탐지 회피 설정
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # User-Agent 설정 (일반 사용자처럼 보이기)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # GPU 가속 끄기 (서버 환경 호환성 및 속도 향상)
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # [스텔스 유지] navigator.webdriver 속성 숨기기 (가장 중요!)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    
    return driver

def scroll_page(driver, times=3):
    """
    페이지를 부드럽게 스크롤하여 Lazy Loading 이미지를 불러옵니다.
    """
    for _ in range(times):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(0.5) # 스크롤 간격 살짝 단축

def smart_extract(driver, site_name, img_selector="img"):
    """
    (기존과 동일) 무신사, 지그재그, 4910용 범용 추출기
    """
    data = []
    seen = set()
    base_url = driver.current_url
    
    images = driver.find_elements(By.CSS_SELECTOR, img_selector)
    
    garbage_img_keywords = ["logo", "icon", "banner", "svg", "isms", "esc", "mark"]
    garbage_text_keywords = [
        "앱에서", "편리하게", "대표자", "사업자", "책임", "신고", "개인정보", 
        "이용약관", "인증", "수상", "고객센터", "채용", "입점", "facebook", "youtube"
    ]
    
    for img in images:
        try:
            src = img.get_attribute("src")
            if not src: continue
            
            if any(bad in src.lower() for bad in garbage_img_keywords): 
                continue

            src = urljoin(base_url, src)
            container = img
            link = ""
            price = ""
            name = ""
            discount = ""
            
            for _ in range(5):
                try:
                    container = container.find_element(By.XPATH, "./..")
                    
                    if not link:
                        try:
                            if container.tag_name == 'a': link = container.get_attribute("href")
                            else: link = container.find_element(By.TAG_NAME, "a").get_attribute("href")
                        except: pass
                    
                    text = container.text
                    if text:
                        lines = text.split('\n')
                        for line in lines:
                            line = line.strip()
                            if not line: continue
                            
                            if "%" in line and any(c.isdigit() for c in line):
                                if len(line) < 10: discount = line
                            elif ("원" in line or "," in line) and any(c.isdigit() for c in line):
                                if len(line) < 20 and "02-" not in line and "010-" not in line:
                                    price = line
                            
                        if not name:
                            candidates = []
                            for line in lines:
                                line = line.strip()
                                if line != price and line != discount and len(line) > 2:
                                    if "도착" not in line and "배송" not in line and "구매" not in line:
                                        candidates.append(line)
                            if candidates: name = max(candidates, key=len)

                    if link and price and name: break
                except: break
            
            if link and price and name:
                full_link = urljoin(base_url, link)
                
                if any(bad in name for bad in garbage_text_keywords): continue
                if any(bad in full_link.lower() for bad in ["login", "notice", "faq", "cs_center"]): continue
                if not any(char.isdigit() for char in full_link): continue

                final_price = price
                if discount and discount not in price:
                     final_price = f"{price} ({discount}↓)"

                if full_link not in seen:
                    seen.add(full_link)
                    data.append({
                        "site": site_name,
                        "name": name,
                        "price": final_price,
                        "link": full_link,
                        "img": src
                    })
        except: continue
        
    return data[:12]