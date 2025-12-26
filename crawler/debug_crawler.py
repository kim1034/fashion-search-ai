from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# 1. 설정
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("detach", True)

print(">>> [진단 시작] 브라우저를 실행합니다...")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

url = "https://www.musinsa.com/main/musinsa/ranking?gf=A&storeCode=musinsa&sectionId=200&contentsId=&categoryCode=000&ageBand=AGE_BAND_ALL"
driver.get(url)

time.sleep(3) # 기본 로딩 대기

print("\n" + "="*50)
print(f"1. 페이지 접속 상태 확인")
print(f" - 현재 제목: {driver.title}")
print(f" - 소스 코드 길이: {len(driver.page_source)} 글자")

if "Access Denied" in driver.title or len(driver.page_source) < 1000:
    print("!!! [차단 의심] 페이지 내용이 너무 짧거나 접근이 거부되었습니다.")
else:
    print(" - 접속 상태: 정상 (차단되지 않음)")

print("\n" + "="*50)
print(f"2. 핵심 요소(data-mds) 존재 여부 확인")

# 이미지를 감싸는 요소 찾기
try:
    mds_images = driver.find_elements(By.CSS_SELECTOR, "[data-mds='Image']")
    print(f" - 발견된 'data-mds=Image' 개수: {len(mds_images)}개")
except:
    print(" - 'data-mds=Image' 요소를 찾을 수 없음")

# 상품 링크 찾기
try:
    goods_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/goods/']")
    print(f" - 발견된 '상품 링크(/goods/)' 개수: {len(goods_links)}개")
except:
    print(" - 상품 링크를 찾을 수 없음")

print("\n" + "="*50)
print(f"3. 첫 번째 상품의 HTML 구조 정밀 분석")

if len(mds_images) > 0:
    target_img = mds_images[0]
    print(">> 첫 번째 이미지 박스를 기준으로 부모 요소들을 역추적합니다.\n")
    
    # 부모로 1단계씩 올라가면서 태그 이름과 클래스를 확인합니다.
    parent = target_img
    for i in range(1, 6): # 5단계 위까지 확인
        try:
            parent = parent.find_element(By.XPATH, "./..")
            tag_name = parent.tag_name
            class_name = parent.get_attribute("class")
            text_preview = parent.text.replace("\n", " | ")[:50] # 텍스트 미리보기
            
            print(f"[{i}단계 위 부모] <{tag_name} class='{class_name[:30]}...'>")
            print(f"   ㄴ 포함된 텍스트: {text_preview}...")
            
            # 만약 이 부모가 'a' 태그라면 링크 주소도 출력
            if tag_name == 'a':
                print(f"   ㄴ [LINK 발견]: {parent.get_attribute('href')}")
            
            print("-" * 30)
        except:
            print(f"[{i}단계 위] 더 이상 부모가 없습니다.")
            break
else:
    print("!!! 분석할 이미지가 없어서 구조 확인 불가")

print("\n" + "="*50)
print("[진단 종료] 이 로그 내용을 복사해서 알려주세요.")

# driver.quit()