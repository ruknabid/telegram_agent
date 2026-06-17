import sys
import asyncio
import os
from playwright.async_api import async_playwright

sys.path.append("/Users/daesic/Documents/stock_advisor")
from skills.google_sheets_loader import load_portfolio_from_sheet

USER_DATA_DIR = os.path.join("/Users/daesic/Documents/telegram_agent", "browser_profile")

async def read_naver_my_holdings():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=False,
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = await browser.new_page()
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            await page.goto("https://stock.naver.com/my", wait_until="networkidle", timeout=30000)
            await asyncio.sleep(5)
            text_content = await page.evaluate("document.body.innerText")
            await browser.close()
            return text_content
    except Exception as e:
        return str(e)

async def main():
    naver_text = await read_naver_my_holdings()
    with open("naver_output.txt", "w") as f:
        f.write(naver_text)
    
    os.environ['GOOGLE_SPREADSHEET_ID'] = '140RTaah9uMlvfFDttAzjijzaXBJPqQt2kpzDxRziQ-c'
    os.environ['TARGET_SHEETS'] = '현황,포트폴리오,자산배분'
    sheets_data = load_portfolio_from_sheet(spreadsheet_id='140RTaah9uMlvfFDttAzjijzaXBJPqQt2kpzDxRziQ-c', target_sheets=['현황', '포트폴리오', '자산배분'])
    
    with open("sheets_output.txt", "w") as f:
        if sheets_data:
            for sheet_name, sheet_values in sheets_data.items():
                f.write(f"\n[Sheet: {sheet_name}]\n")
                for row in sheet_values:
                    f.write(str(row) + "\n")
        else:
            f.write("Could not load Google Sheets data.\n")

if __name__ == "__main__":
    asyncio.run(main())
