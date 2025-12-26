import sys
import os
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 부모 폴더 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import utils
except ImportError:
    from . import utils

def search(keyword):
    print(f">>> [29CM] '{keyword}' 검색 시작 (클래스 정밀 타격)...")
    
    driver = utils.get_driver()
    results = []
    
    try:
        url = f"https://search.29cm.co.kr/search?keyword={keyword}"
        driver.get(url)
        
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except: pass

        utils.scroll_page(driver, 6)
        
        # 상품명(a 태그) 기준 탐색
        items = driver.find_elements(By.CSS_SELECTOR, "a[class*='break-all']")
        print(f"   ㄴ 상품 후보 {len(items)}개 분석 중...")
        
        seen = set()
        
        for item in items:
            try:
                name = item.text.strip()
                link = item.get_attribute("href")
                if not link: continue

                # 최상위 Root 찾기 (상품 박스 전체)
                root = item
                for _ in range(4):
                    try:
                        temp = root.find_element(By.XPATH, "./..")
                        if temp.tag_name == "body": break
                        root = temp
                    except: break
                
                # --- [핵심 수정] 가격 추출 로직 (클래스 기반) ---
                price = ""
                discount = ""
                
                try:
                    # 알려주신 태그 특징: text-primary (정가) 또는 text-accent (할인가)
                    # 이 클래스가 붙은 요소만 콕 집어서 가져옵니다.
                    target_els = root.find_elements(By.CSS_SELECTOR, "[class*='text-primary'], [class*='text-accent']")
                    
                    for el in target_els:
                        txt = el.text.strip()
                        if not txt: continue
                        
                        # 1. 할인율 (%)
                        if "%" in txt:
                            discount = txt
                        
                        # 2. 가격 (숫자)
                        # text-primary가 붙어있으면 리뷰수일 확률 0%입니다.
                        elif any(c.isdigit() for c in txt):
                            # 혹시 모를 텍스트 정제 ("149,000" -> "149,000")
                            # 날짜나 이상한 숫자 제외
                            if "." not in txt and len(txt) < 15:
                                # 빨간색(accent) 가격이 발견되면 그게 우선순위 (할인가)
                                if "text-accent" in el.get_attribute("class"):
                                    price = txt
                                # 아직 가격 못 찾았으면 primary 가격 저장
                                elif not price:
                                    price = txt

                    # 최종 포맷팅
                    if price:
                        if discount and discount not in price:
                            price = f"{price} ({discount}↓)"
                            
                except Exception as e:
                    pass
                
                if not price: continue

                # --- 이미지 찾기 (기존 유지) ---
                img = ""
                try:
                    imgs = root.find_elements(By.TAG_NAME, "img")
                    candidate_imgs = []
                    for i in imgs:
                        src = i.get_attribute("src")
                        if src and "http" in src and "29cm.co.kr" in src:
                            if "icon" not in src and "logo" not in src:
                                candidate_imgs.append(src)
                    
                    if candidate_imgs: img = candidate_imgs[0]
                    else:
                        for i in imgs:
                            data_src = i.get_attribute("data-src")
                            if data_src: img = data_src; break
                except: pass
                if not img: img = "https://img.29cm.co.kr/next-product/2023/01/01/ad2f009363a042c194519c9e88730413_20230101123456.jpg"

                # 브랜드
                brand = ""
                try:
                    brand_el = root.find_element(By.CSS_SELECTOR, "span[class*='text-s-bold']")
                    brand = brand_el.text.strip()
                    if brand and brand not in name: name = f"[{brand}] {name}"
                except: pass

                # 저장
                if link not in seen:
                    seen.add(link)
                    results.append({
                        "site": "29CM",
                        "name": name,
                        "price": price,
                        "link": link,
                        "img": img
                    })

            except: continue
                
    except Exception as e:
        print(f"!!! [29CM] 에러: {e}")
    finally:
        driver.quit()
        
    print(f">>> [29CM] {len(results)}개 찾음!")
    return results[:12]

if __name__ == "__main__":
    search("나이키 에어포스")