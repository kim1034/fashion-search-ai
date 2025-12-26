import streamlit as st
import os
import re
import concurrent.futures
from PIL import Image
from ai_analyzer import get_search_keywords
# 크롤러 모듈 임포트
from search_engine import musinsa, zigzag, crawler_29cm, crawler_4910

# --- [1] 페이지 기본 설정 (가장 중요: 사이드바 강제 확장) ---
st.set_page_config(
    page_title="AI Fashion Search",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded" # [핵심] 앱 켤 때 사이드바 무조건 열기
)

# --- [2] 고급 CSS 스타일링 ---
st.markdown("""
<style>
    /* 1. 폰트 및 배경 */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    html, body, [class*="css"] {
        font-family: 'Pretendard', sans-serif; 
    }
    
    .stApp {
        background-color: #Fdfdfd;
    }

    /* 2. 헤더 설정 (중요: header visibility hidden을 제거했습니다!) */
    footer {visibility: hidden;}
    
    /* 3. 상품 카드 디자인 */
    .product-card {
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
        overflow: hidden;
        height: 100%;
        border: 1px solid #f0f0f0;
        cursor: pointer;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.12);
    }

    /* 4. 뱃지 스타일 */
    .badge {
        font-size: 11px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
        color: white;
        display: inline-block;
        margin-bottom: 6px;
    }
    .badge-musinsa { background-color: #000000; }
    .badge-zigzag { background-color: #FF3366; }
    .badge-29cm { background-color: #303033; }
    .badge-4910 { background-color: #6C5CE7; }

    /* 5. 텍스트 스타일 */
    .product-name {
        font-size: 14px;
        color: #333;
        line-height: 1.4;
        margin-bottom: 4px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        height: 40px;
    }
    .product-price { font-size: 16px; font-weight: 800; color: #111; }
    .discount-rate { color: #FF3366; font-size: 13px; font-weight: 700; margin-left: 4px; }
    
    /* 링크 스타일 초기화 */
    a { text-decoration: none !important; color: inherit !important; }
    div.stButton > button { width: 100%; border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- [3] 헤더 영역 ---
st.markdown("<h1 style='text-align: center;'>✨ AI Fashion Finder</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: grey; margin-bottom: 40px;'>사진 한 장으로 4대 패션몰 최저가를 찾아냅니다.</p>", unsafe_allow_html=True)

# --- [4] 사이드바 ---
with st.sidebar:
    st.header("🔎 검색 옵션")
    tab1, tab2 = st.tabs(["텍스트", "이미지"])
    
    keyword = ""
    with tab1:
        keyword = st.text_input("검색어", placeholder="예: 나이키 에어포스")
        
    with tab2:
        uploaded_file = st.file_uploader("이미지 업로드", type=["png", "jpg", "jpeg", "webp"])
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
            temp_path = "temp_upload_image.jpg"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            if st.button("✨ AI 분석 시작", type="secondary"):
                with st.spinner("Analyzing..."):
                    en_text, ko_text = get_search_keywords(temp_path)
                    if ko_text:
                        st.success(f"키워드: {ko_text}")
                        st.session_state['ai_keyword'] = ko_text
                    else: st.error("분석 실패")

    if 'ai_keyword' in st.session_state and not keyword:
        keyword = st.session_state['ai_keyword']
        st.info(f"AI 추천: **{keyword}**")

    st.markdown("---")
    start_search = st.button("🚀 통합 검색 시작", type="primary")

# --- [5] 메인 로직 ---
if start_search:
    if not keyword:
        st.toast("검색어를 입력해주세요!", icon="⚠️")
    else:
        st.subheader(f"Results for '{keyword}'")
        
        def run_crawler(crawler, name, search_keyword):
            try: return crawler.search(search_keyword)
            except Exception as e:
                print(f"{name} 에러: {e}")
                return []

        with st.spinner("🛒 4대 쇼핑몰을 스캔 중입니다..."):
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                f1 = executor.submit(run_crawler, musinsa, "무신사", keyword)
                f2 = executor.submit(run_crawler, zigzag, "지그재그", keyword)
                f3 = executor.submit(run_crawler, crawler_29cm, "29CM", keyword)
                f4 = executor.submit(run_crawler, crawler_4910, "4910", keyword)
                
                d1, d2, d3, d4 = f1.result(), f2.result(), f3.result(), f4.result()

        all_data = d1 + d2 + d3 + d4
        
        if not all_data:
            st.warning("상품을 찾지 못했습니다.")
        else:
            # 정렬 로직
            for item in all_data:
                raw = item['price']
                nums = re.findall(r'\d+', raw.replace(",", ""))
                try: item['price_int'] = int(nums[0])
                except: item['price_int'] = 99999999
            
            sorted_data = sorted(all_data, key=lambda x: x['price_int'])
            st.success(f"총 {len(sorted_data)}개의 최저가 상품을 찾았습니다.")
            st.markdown("<br>", unsafe_allow_html=True)

            # 결과 출력 (Grid)
            cols = st.columns(4)
            for i, item in enumerate(sorted_data):
                with cols[i % 4]:
                    badge_cls = "badge-musinsa"
                    if item['site'] == "지그재그": badge_cls = "badge-zigzag"
                    elif item['site'] == "29CM": badge_cls = "badge-29cm"
                    elif item['site'] == "4910": badge_cls = "badge-4910"
                    
                    p_html = f'<span class="product-price">{item["price"]}</span>'
                    if "(" in item["price"]:
                        p, d = item["price"].split("(", 1)
                        p_html = f'<span class="product-price">{p}</span><span class="discount-rate">{d.replace(")","")}</span>'
                    
                    img_src = item['img'] if item['img'] else "https://via.placeholder.com/300x400"

                    st.markdown(f"""
                    <a href="{item['link']}" target="_blank">
                        <div class="product-card">
                            <div style="width:100%; height:200px; overflow:hidden; display:flex; align-items:center; justify-content:center; background:#f8f8f8;">
                                <img src="{img_src}" style="width:100%; height:100%; object-fit:cover;">
                            </div>
                            <div style="padding: 12px;">
                                <span class="badge {badge_cls}">{item['site']}</span>
                                <div class="product-name">{item['name']}</div>
                                <div style="margin-top:4px;">{p_html}</div>
                            </div>
                        </div>
                    </a>
                    """, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)