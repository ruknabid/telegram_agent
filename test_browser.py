import asyncio
from browser_tool import read_browser_page_async

async def main():
    print(await read_browser_page_async("https://finance.naver.com/mystock/"))

asyncio.run(main())
