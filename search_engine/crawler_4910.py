import sys
import os
import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys # [필수] 키보드 입력을 위해 필요
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 부모 폴더 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import utils
except ImportError:
    from . import utils

def search(keyword):
    print(f">>> [4910] '{keyword}' 검색 시작 (직접 입력 모드)...")
    
    driver = utils.get_driver()
    results = []
    
    try:
        # 1. 검색 페이지로 이동 (키워드 없이)
        driver.get("https://4910.kr/search")
        
        # 2. [핵심] 검색창 찾아서 직접 타이핑 + 엔터
        try:
            # 검색창(input)이 뜰 때까지 대기
            search_box = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.TAG_NAME, "input"))
            )
            print("   [행동] 검색창 발견! 키워드 입력 중...")
            
            search_box.click()
            time.sleep(0.5)
            search_box.clear() # 기존 내용 지우기
            search_box.send_keys(keyword) # 타이핑
            time.sleep(0.5)
            search_box.send_keys(Keys.RETURN) # 엔터키 쾅!
            
            print("   [행동] 엔터 입력 완료. 결과 로딩 대기...")
            
        except Exception as e:
            print(f"   [경고] 검색창 입력 실패: {e}")

        # 3. 로딩 대기 (이미지가 뜰 때까지)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a img"))
            )
            print("   [상태] 상품 리스트 로딩 성공")
        except:
            print("   [경고] 로딩이 늦어지거나 상품이 없습니다.")

        # 4. 스크롤 (데이터 확보)
        for i in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)

        # 5. 데이터 수집 (전방위 링크 스캔 방식 재사용)
        # 이제 화면에 상품이 떴을 테니, 링크를 긁어오면 됩니다.
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"   ㄴ 링크 {len(links)}개 발견. 분석 시작...")
        
        seen = set()
        
        for link_el in links:
            try:
                # [1] 이미지 확인
                try:
                    img_tag = link_el.find_element(By.TAG_NAME, "img")
                    img = img_tag.get_attribute("src")
                    # 로고, 아이콘 제외
                    if not img or "icon" in img or "logo" in img or "button" in img: continue
                except: continue

                # [2] 텍스트 정보 확인
                full_text = link_el.text
                if not full_text: continue
                
                # 가격(숫자)이 포함되어 있어야 함
                if not any(c.isdigit() for c in full_text): continue

                # [3] 이름 & 가격 추출
                name = ""
                price = ""
                
                lines = full_text.split('\n')
                
                # 이름 찾기 (body4 태그 우선, 없으면 긴 텍스트)
                try:
                    name_el = link_el.find_element(By.CSS_SELECTOR, "p[type='body4']")
                    name = name_el.text.strip()
                except:
                    # 텍스트 분석
                    candidates = []
                    for line in lines:
                        line = line.strip()
                        if len(line) < 2: continue
                        if any(x in line for x in ["관심", "리뷰", "배송", "도착", "%", "쿠폰", "원"]): continue
                        if re.match(r'^[\d,]+$', line): continue # 숫자만 있는거 제외
                        candidates.append(line)
                    if candidates: name = max(candidates, key=len)

                if not name or "관심" in name: continue

                # 가격 찾기
                for line in lines:
                    line = line.strip()
                    if any(c.isdigit() for c in line) and ("," in line or "원" in line):
                        if "관심" not in line and "리뷰" not in line and "%" not in line:
                             if len(line) < 20:
                                 price = line
                                 break
                
                # 할인율
                for line in lines:
                    if "%" in line and len(line) < 6:
                        if price and "%" not in price:
                            price = f"{price} ({line}↓)"
                            break
                            
                if not price: continue

                # 링크 주소
                href = link_el.get_attribute("href")
                if not href or "javascript" in href: continue

                # 저장
                if href not in seen:
                    seen.add(href)
                    results.append({
                        "site": "4910",
                        "name": name,
                        "price": price,
                        "link": href,
                        "img": img
                    })

            except: continue
                
    except Exception as e:
        print(f"!!! [4910] 에러: {e}")
    finally:
        driver.quit()
        
    print(f">>> [4910] {len(results)}개 찾음!")
    return results[:12]

if __name__ == "__main__":
    search("나이키 에어포스")