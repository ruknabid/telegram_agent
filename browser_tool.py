import asyncio
from playwright.async_api import async_playwright
import os

# 프로필(쿠키/세션)을 저장할 경로
USER_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "browser_profile")

async def read_browser_page_async(url: str) -> str:
    """
    비동기로 브라우저 페이지를 읽는 실제 구현부
    """
    try:
        async with async_playwright() as p:
            # 프로필 기반으로 브라우저 컨텍스트 실행
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=True,  # AI가 읽을 때는 화면을 띄우지 않음
                args=["--disable-blink-features=AutomationControlled"] # 봇 탐지 우회 보조
            )
            
            page = await browser.new_page()
            
            # 봇 탐지 우회를 위한 User-Agent 설정
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            # 페이지 이동 및 로딩 대기 (네트워크 요청이 어느정도 잠잠해질 때까지)
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # 화면에 보이는 텍스트만 추출 (HTML 태그 제거)
            text_content = await page.evaluate("document.body.innerText")
            
            await browser.close()
            
            if not text_content or not text_content.strip():
                return f"'{url}'에서 텍스트를 찾을 수 없거나 페이지 로딩에 실패했습니다."
            
            # 너무 길면 자르기 (약 10000자 이내)
            if len(text_content) > 10000:
                text_content = text_content[:10000] + "\n...[내용이 너무 길어 잘림]"
                
            return f"[{url} 페이지 내용 요약]\n" + text_content
            
    except Exception as e:
        return f"브라우저 실행 중 오류 발생: {str(e)}"

def read_browser_page(url: str):
    """
    지정된 URL에 접속하여 브라우저 내의 텍스트 정보를 긁어옵니다.
    기존에 로그인해둔 세션(browser_profile)을 활용하여 Headless(화면 없음) 모드로 접속합니다.
    (동기 래퍼 함수 - Gemini Function Calling 용도)
    """
    # 이미 텔레그램 봇의 이벤트 루프 안에 있으므로 기존 루프 활용 필요.
    # 단, Gemini Function Calling 자체는 비동기 호출을 지원하지만, 
    # 핸들러에서 어떻게 감싸는지에 따라 달라짐.
    # bot.py에서 비동기로 다루기 쉽게 분리.
    pass

async def login_browser():
    """
    최초 1회 실행하여 사용자가 증권사 등에 수동으로 로그인할 수 있도록
    화면을 띄우는(Headful) 모드입니다.
    """
    print(f"로그인 전용 브라우저를 엽니다... 프로필 저장 경로: {USER_DATA_DIR}")
    print("브라우저 창이 열리면 원하시는 사이트(증권사 등)에 접속하여 로그인해 주세요.")
    print("로그인이 끝나면 터미널에서 Ctrl+C를 눌러 종료하시면 됩니다.")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False, # 화면 띄움
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = await browser.new_page()
        await page.goto("https://www.google.com")
        
        # 사용자가 수동으로 브라우저를 닫을 때까지 무한 대기
        await page.wait_for_timeout(999999999)

if __name__ == "__main__":
    # 직접 스크립트 실행 시 로그인 모드로 작동
    asyncio.run(login_browser())
