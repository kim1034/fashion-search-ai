import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
from deep_translator import GoogleTranslator
import requests  # [중요] 이게 빠져서 에러가 났었습니다!
from io import BytesIO

# --- 1. 모델 로딩 ---
print(">>> [AI] 모델을 불러오는 중입니다 (잠시만 기다려주세요)...")

device = "cuda" if torch.cuda.is_available() else "cpu"

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)
translator = GoogleTranslator(source='auto', target='ko')

print(">>> [AI] 준비 완료!")

# --- 2. 이미지 분석 함수 ---
def get_search_keywords(image_input):
    """
    이미지 파일 경로, URL, 또는 PIL Image 객체를 받아서
    한국어 검색 키워드를 반환합니다.
    """
    raw_image = None
    
    # 봇 차단 방지용 신분증
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # (A) 인터넷 주소(URL)인 경우
        if isinstance(image_input, str) and image_input.startswith("http"):
            response = requests.get(image_input, headers=headers)
            if response.status_code != 200:
                print(f"!!! 이미지 다운로드 실패 (코드: {response.status_code})")
                return None, None
            raw_image = Image.open(BytesIO(response.content)).convert('RGB')
        
        # (B) 내 컴퓨터 파일 경로인 경우
        elif isinstance(image_input, str):
            raw_image = Image.open(image_input).convert('RGB')
        
        # (C) 이미 PIL 이미지인 경우
        else:
            raw_image = image_input.convert('RGB')

        # AI에게 보여주기
        inputs = processor(raw_image, return_tensors="pt").to(device)

        # 텍스트 생성
        out = model.generate(**inputs, max_new_tokens=50)
        description_en = processor.decode(out[0], skip_special_tokens=True)
        
        # 한국어 번역
        description_ko = translator.translate(description_en)
        
        return description_en, description_ko

    except Exception as e:
        print(f"!!! AI 분석 중 에러 발생: {e}")
        return None, None

# --- 3. 테스트 실행 ---
if __name__ == "__main__":
    # 절대 사라지지 않는 위키백과 '청자켓' 사진
    test_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Denim_jacket.jpg/440px-Denim_jacket.jpg"
    
    # (원하면 아래 주석을 풀고 다른 걸로 해보세요)
    # test_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Trench_coat.jpg/360px-Trench_coat.jpg" # 트렌치 코트
    
    print(f"\n>>> [패션 테스트] 이미지 분석 중: {test_url}")
    en_text, ko_text = get_search_keywords(test_url)
    
    if en_text:
        print("="*40)
        print(f"🇺🇸 AI가 본 것: {en_text}")
        print(f"🇰🇷 한국어 번역: {ko_text}")
        print("="*40)
        print(">>> 성공! '청자켓'이나 '데님' 같은 단어가 나왔나요?")
    else:
        print(">>> 분석 실패 (이미지 주소를 확인해주세요)")