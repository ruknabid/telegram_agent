# Bot Memory: 중요 정보 기록
> [!IMPORTANT]
> **봇 메모리 탐색 원칙:** 메모리 자체나 외부 참조 파일을 읽을 때, 모든 내용을 무작정 처음부터 끝까지 통째로 읽어들이지 마십시오. 토큰 낭비와 오류를 방지하기 위해 사용자의 질문과 관련된 키워드를 바탕으로 **필요한 섹션이나 정보만 정확하게 검색하여 선별적으로 읽어들이도록** 동작하세요.

## 1. 관심 종목 (Watchlist)
- 우분투 서버 위치: /home/ubuntu/stock_advisor/prompts/auto_trader.md
- 맥북 로컬 위치: /Users/daesic/Documents/stock_advisor/watchlist.md

## 2. 포트폴리오 관리 방식
- 구글 스프레드시트 연동: '현황' 및 '포트폴리오' 시트를 타겟으로 사용 (환경변수 TARGET_SHEETS)

## 3. 운영 원칙
- 대화 내용 중 핵심 사항은 본 파일(bot_memory.md)에 기록하여 유지함.


## 4. 주식 관련 문의
- 맥북 로컬의 /Users/daesic/Documents/stock_advisor 폴더를 참고해
- 자동매매 스케쥴러 확인을 위해선 cronjob 설정을 확인해
- 그 외 자동매매 관련된것들은 /Users/daesic/Documents/stock_advisor/docs/PRD.md 과 /Users/daesic/Documents/stock_advisor/README.md 파일에 있어.  


## 5. 내 포트폴리오 관련 문의
- 내 포트폴리오 현황은 /Users/daesic/Documents/portfolio_manager/my_portfolio.md 파일에 있어. 

## 6. 매매 및 자산배분 절대 원칙 (Single Source of Truth)
- 이곳(메모리)에 원칙을 텍스트로 중복 기재하지 않습니다. 매매 판단 시 아래의 4가지 핵심 원본 문서들을 **필요할 때마다 직접 조회하여** 최신 원칙(바벨 전략, 거래량 동반 추세 추종 등)을 확인하고 판단의 근거로 삼으십시오.
  1. 자산배분 핵심 가이드: `/Users/daesic/Documents/portfolio_manager/prompts/asset_management_guide.md`
  2. 매크로 및 과거 교훈: `/Users/daesic/Documents/portfolio_manager/prompts/macro_analysis_framework.md`
  3. 자동매매 판단 원칙: `/Users/daesic/Documents/stock_advisor/prompts/cio_expert.md`
  4. 개별 종목 발굴 5원칙 (핵심): `/Users/daesic/Documents/stock_advisor/prompts/stock_analysis_rules.md`

## 7. 개별 종목 분석 시 주의사항 (매크로 핑계 금지)
- **개별 종목(주식)만 분석해 달라는 요청을 받았을 때는 절대로 거시경제(매크로) 지표나 시장 상황을 끌고 와서 종목의 장단점을 평가하지 마십시오.**
- 개별 종목 분석은 철저하게 `stock_analysis_rules.md`의 **'종목 발굴 5원칙'에만 집중**하여 독립적으로 수행해야 합니다. (1. 차트 정배열, 2. 폭발적 거래량, 3. 해당 기업 고유의 최신 뉴스 및 재무 검증)