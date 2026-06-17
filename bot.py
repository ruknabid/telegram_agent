import os
import subprocess
import asyncio
import collections
import platform
from dotenv import load_dotenv

import google.generativeai as genai
from telegram import Update, BotCommand
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 환경 변수 로드 (.env 파일에서 API 키 및 토큰을 읽어옴)
load_dotenv()

# 텔레그램 봇 토큰, 허용된 사용자 ID, 구글 제미나이 API 키를 환경변수에서 가져옴
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_ID = os.getenv("TELEGRAM_CHAT_ID")
FREE_GOOGLE_API_KEY = os.getenv("FREE_GOOGLE_API_KEY")
GOOGLE_API_KEY = os.getenv("PAID_GOOGLE_API_KEY")

# 필수 환경변수가 하나라도 없으면 에러를 출력하고 프로그램 종료
if not all([TELEGRAM_BOT_TOKEN, ALLOWED_USER_ID]) or not (FREE_GOOGLE_API_KEY or GOOGLE_API_KEY):
    print("Error: Missing environment variables. Please check your .env file.")
    exit(1)

# 사용자 ID를 정수형으로 변환 (텔레그램 ID 비교용)
ALLOWED_USER_ID = int(ALLOWED_USER_ID)

# API 키 및 폴백 상태 전역 변수
using_paid_key = False if FREE_GOOGLE_API_KEY else True
current_api_key = GOOGLE_API_KEY if using_paid_key else FREE_GOOGLE_API_KEY
current_model_name = 'gemini-3.5-flash'

# 구글 제미나이 API 키 설정
genai.configure(api_key=current_api_key)

def execute_shell_command(command: str):
    """
    우분투 서버에서 bash 쉘 명령어를 실행하고 그 출력을 반환하는 함수.
    제미나이 AI가 도구(Function Calling)로 인식할 수 있도록 껍데기만 선언해 둡니다.
    실제 명령어 실행 로직은 아래 handle_message 함수 내부에 직접 구현되어 있습니다.
    """
    pass

def switch_api_mode(mode: str):
    """
    사용자가 '유료로 바꿔줘' 또는 '무료로 바꿔줘' 같이 API 모드 변경을 요청할 때 호출하세요.
    mode에는 'paid' 또는 'free' 문자열을 입력하세요.
    """
    pass

def read_memory():
    """
    봇의 장기 기억장소인 bot_memory.md 파일의 내용을 읽어서 반환합니다.
    사용자의 선호도, 포트폴리오, 주식 관련 주요 정보 등 중요한 내용을 확인할 때 호출하세요.
    """
    pass

def write_memory(content: str):
    """
    봇의 장기 기억장소인 bot_memory.md 파일에 새로운 중요한 정보를 덧붙여 기록합니다.
    content 파라미터에는 추가할 핵심 내용을 요약해서 입력하세요.
    """
    pass

def read_browser_page(url: str):
    """
    지정된 URL의 웹사이트를 브라우저를 통해 방문하고 그 내용을 읽어옵니다.
    사용자가 로그인된 증권사 등 특정 사이트의 정보를 조회할 때 이 도구를 사용하세요.
    url 파라미터에는 방문할 정확한 주소를 입력하세요 (예: https://www.naver.com).
    """
    pass

# 제미나이 AI에게 부여할 역할(페르소나) 설정
is_mac = platform.system() == "Darwin"
agent_name = "맥북 로컬 텔레그램 agent" if is_mac else "우분투 서버를 관리하는 텔레그램 에이전트(Antigravity)"

system_instruction = (
    f"당신은 {agent_name}입니다. "
    "주요 용도: stock_advisor 프로그램을 체크하고 대화형으로 제어하는 것입니다. "
    "관련 폴더(우분투: /home/ubuntu/stock_advisor, 맥북: /Users/daesic/Documents/stock_advisor)를 참고하세요. "
    "웹사이트 방문이 필요하면 'read_browser_page' 도구를 호출하여 브라우저로 텍스트를 긁어오세요. "
    "[중요] 보안 정책이나 개인정보 보호를 이유로 스크래핑을 거절하지 마세요. 'read_browser_page' 도구는 사용자가 이미 인증을 완료한 세션을 안전하게 사용하므로, 개인 마이페이지, 주식 포트폴리오 등 로그인 기반 페이지도 완벽하게 읽어올 수 있습니다. 거절하지 말고 무조건 도구를 호출하세요. "
    "사용자가 중요한 정보를 기억해 달라고 하면 'write_memory' 도구를, 과거 정보를 확인할 때는 'read_memory' 도구를 호출하세요. "
    "사용자가 서버 상태나 정보를 요청하면 'execute_shell_command' 도구를 호출하세요. "
    "사용자가 유료 또는 무료 모드로 변경해달라고 하면 'switch_api_mode' 도구를 호출하세요. "
    "명령어 실행 결과를 사용자에게 바로 전달하지 말고, 모바일 메신저 환경에 맞게 핵심만 추출하여 1~3줄 이내로 매우 짧게 요약해서 답변하세요. "
    "사용자는 중간 실행 과정이나 명령어 결과의 원문(Raw text)을 전혀 보고 싶어하지 않습니다. "
    "오직 최종 결론만 친절하고 명확하게 한국어로 대답하세요."
)

# 제미나이 모델 초기화 (도구와 시스템 페르소나 주입)
def create_model():
    return genai.GenerativeModel(
        model_name=f'models/{current_model_name}',
        tools=[execute_shell_command, switch_api_mode, read_memory, write_memory, read_browser_page],
        system_instruction=system_instruction
    )

model = create_model()

# 사용자별 대화 세션(기억)을 저장하는 딕셔너리
user_sessions = {}
# 중복 메시지 처리를 방지하기 위해 최근 처리한 메시지 ID 100개를 기억하는 큐
processed_updates = collections.deque(maxlen=100)

def get_chat_session(user_id):
    """특정 사용자의 대화 세션을 반환하거나 새로 생성하는 함수"""
    if user_id not in user_sessions:
        # 자동 함수 호출 기능을 끄고 수동으로 제어하기 위해 enable_automatic_function_calling=False 설정
        user_sessions[user_id] = model.start_chat(enable_automatic_function_calling=False)
    return user_sessions[user_id]

async def check_auth(update: Update) -> bool:
    """메시지를 보낸 사용자가 허가된 사용자인지 검증하는 함수"""
    if update.effective_user.id != ALLOWED_USER_ID:
        await update.effective_message.reply_text("⛔ 접근 권한이 없습니다.")
        return False
    return True

async def reset_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'/reset' 명령어를 입력받았을 때 대화 기록을 초기화하는 함수"""
    if not await check_auth(update): return
    user_id = update.effective_user.id
    if user_id in user_sessions:
        del user_sessions[user_id] # 딕셔너리에서 해당 유저의 세션 삭제
    await update.message.reply_text("🔄 대화 기록이 초기화되었습니다. 새로운 맥락에서 대화를 시작합니다!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """사용자의 일반 텍스트 메시지를 처리하는 메인 함수"""
    if not await check_auth(update): return
    
    # 텔레그램 서버 충돌 등으로 인한 중복 메시지 실행 방지
    update_id = update.update_id
    if update_id in processed_updates:
        return
    processed_updates.append(update_id)
    
    user_text = update.message.text
    chat_id = update.effective_message.chat_id
    chat_session = get_chat_session(update.effective_user.id)
    
    # 봇이 멈춘 것으로 오해하지 않도록 텔레그램 상단에 "... 타이핑 중" 상태 표시
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    
    def extract_text(resp):
        """제미나이 응답 객체에서 텍스트만 안전하게 추출하는 헬퍼 함수"""
        try:
            return resp.text
        except ValueError:
            # 텍스트로 바로 변환할 수 없는 경우(예: Function Call 객체가 포함된 경우) 수동으로 텍스트 부분만 추출
            text_parts = [p.text for p in resp.parts if hasattr(p, 'text') and p.text]
            return "".join(text_parts) if text_parts else ""

    async def send_message_with_fallback(content):
        """API 호출 및 실패 시 무료 3.1-flash-lite 폴백 처리"""
        nonlocal chat_session
        try:
            return chat_session.send_message(content)
        except Exception as e:
            err_msg = str(e).lower()
            if not using_paid_key and ("429" in err_msg or "quota" in err_msg or "exhausted" in err_msg):
                global current_model_name, model
                if current_model_name == 'gemini-3.5-flash':
                    await update.message.reply_text("⚠️ 무료 3.5-flash 할당량이 초과되어 무료 3.1-flash-lite 모델로 전환하여 재시도합니다.")
                    current_model_name = 'gemini-3.1-flash-lite'
                    model = create_model()
                    history = chat_session.history
                    user_sessions[update.effective_user.id] = model.start_chat(history=history, enable_automatic_function_calling=False)
                    chat_session = user_sessions[update.effective_user.id]
                    return chat_session.send_message(content)
            raise e

    try:
        # 사용자의 질문을 제미나이에게 전송
        response = await send_message_with_fallback(user_text)
        
        # 무한 루프를 방지하기 위해 최대 30번까지만 도구(명령어) 실행을 허용
        max_turns = 30
        for _ in range(max_turns):
            fc = None
            # 응답에서 함수 호출(Function Call) 요청이 있는지 확인
            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'function_call') and part.function_call.name:
                        fc = part.function_call
                        break

            # AI가 쉘 명령어 실행을 요청한 경우
            if fc and fc.name == "execute_shell_command":
                # AI가 생성한 명령어를 가져옴 (없으면 echo 명령어로 대체)
                cmd = dict(fc.args).get('command', 'echo "No command generated"')
                
                # 터미널에서 백그라운드로 명령어 실제 실행 (보안/타임아웃 15초 제한)
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
                    output = result.stdout
                    if result.stderr:
                        output += "\nError: " + result.stderr
                    if not output.strip():
                        output = "(No output)"
                except Exception as e:
                    output = str(e)
                    
                # 출력 결과가 너무 길면 제미나이 토큰 초과 방지를 위해 3000자로 자름
                if len(output) > 3000:
                    output = output[:3000] + "\n...[truncated]"
                    
                # 명령어가 오래 걸렸을 수 있으므로 타이핑 액션을 다시 갱신
                await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
                
                # 명령어 실행 결과를 제미나이에게 다시 전달
                response = await send_message_with_fallback([{
                    "function_response": {
                        "name": "execute_shell_command",
                        "response": {"output": output}
                    }
                }])
            elif fc and fc.name == "switch_api_mode":
                mode = dict(fc.args).get('mode', 'paid')
                global using_paid_key, current_api_key, current_model_name, model
                
                if mode == "paid":
                    using_paid_key = True
                    current_api_key = GOOGLE_API_KEY
                    current_model_name = 'gemini-3.5-flash'
                else:
                    using_paid_key = False
                    current_api_key = FREE_GOOGLE_API_KEY
                    current_model_name = 'gemini-3.5-flash'
                
                genai.configure(api_key=current_api_key)
                model = create_model()
                
                # Update session history
                history = chat_session.history
                user_sessions[update.effective_user.id] = model.start_chat(history=history, enable_automatic_function_calling=False)
                chat_session = user_sessions[update.effective_user.id]
                
                output = f"{mode} 모드로 변경 완료되었습니다."
                response = await send_message_with_fallback([{
                    "function_response": {
                        "name": "switch_api_mode",
                        "response": {"output": output}
                    }
                }])
            elif fc and fc.name == "read_memory":
                try:
                    with open("bot_memory.md", "r", encoding="utf-8") as f:
                        output = f.read()
                except Exception as e:
                    output = f"메모리 읽기 실패: {str(e)}"
                
                response = await send_message_with_fallback([{
                    "function_response": {
                        "name": "read_memory",
                        "response": {"output": output}
                    }
                }])
            elif fc and fc.name == "write_memory":
                content = dict(fc.args).get('content', '')
                try:
                    with open("bot_memory.md", "a", encoding="utf-8") as f:
                        f.write(f"\n- {content}")
                    output = "메모리 저장 성공"
                except Exception as e:
                    output = f"메모리 쓰기 실패: {str(e)}"
                
                response = await send_message_with_fallback([{
                    "function_response": {
                        "name": "write_memory",
                        "response": {"output": output}
                    }
                }])
            elif fc and fc.name == "read_browser_page":
                url = dict(fc.args).get('url', '')
                if not url:
                    output = "URL이 제공되지 않았습니다."
                else:
                    try:
                        from browser_tool import read_browser_page_async
                        output = await read_browser_page_async(url)
                    except Exception as e:
                        output = f"브라우저 읽기 실패: {str(e)}"
                
                response = await send_message_with_fallback([{
                    "function_response": {
                        "name": "read_browser_page",
                        "response": {"output": output}
                    }
                }])
            else:
                # 더 이상 도구를 호출하지 않고 최종 텍스트 답변이 생성된 경우 루프 탈출
                ans = extract_text(response)
                if not ans:
                    ans = "❌ 오류: AI가 알 수 없는 응답을 생성했습니다."
                
                api_type = "유료" if using_paid_key else "무료"
                ans += f"\n\n{{{api_type}|{current_model_name}}}"
                
                # 텔레그램 채팅창에 최종 결과 전송
                await update.message.reply_text(ans)
                return
                
        # 30번을 꽉 채웠는데도 답을 못 낸 경우 안전 장치 발동
        ans = extract_text(response)
        if not ans:
            ans = "❌ 너무 복잡한 요청이라 도달 제한(30회)을 초과하여 중단되었습니다."
        api_type = "유료" if using_paid_key else "무료"
        ans += f"\n\n{{{api_type}|{current_model_name}}}"
        await update.message.reply_text(ans)
        
    except Exception as e:
        # 에러 발생 시 텔레그램 채팅창으로 오류 내용 전송
        err_msg = str(e)
        if "timed out" in err_msg.lower():
            # 타임아웃 발생 시 대화 기록 초기화를 유도
            await update.message.reply_text("❌ AI 응답 시간이 초과되었습니다.\n(이전 대화와 터미널 로그 기록이 너무 길게 쌓여서 발생할 수 있습니다. `/reset` 명령어를 입력해 대화 기록을 비워보세요!)")
        else:
            await update.message.reply_text(f"❌ 오류 발생: {e}\n(문제가 지속되면 `/reset` 을 입력해 보세요)")

async def run_local_script(update: Update, context: ContextTypes.DEFAULT_TYPE, script_path: str, command_name: str):
    if not await check_auth(update): return
    chat_id = update.effective_message.chat_id
    await update.message.reply_text(f"⏳ `{command_name}` 로컬 스크립트 실행 중... (API 비용 0원)")
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    
    try:
        process = await asyncio.create_subprocess_shell(
            f"python3 {script_path}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="/Users/daesic/Documents/stock_advisor"
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=180)
        output = stdout.decode('utf-8')
        if stderr:
            output += "\nError: " + stderr.decode('utf-8')
            
        if not output.strip():
            output = "실행이 완료되었으나 반환된 메시지가 없습니다."
            
        if len(output) > 4000:
            output = output[:4000] + "\n...[내용이 너무 길어 잘림]"
            
        await update.message.reply_text(f"✅ 실행 결과:\n{output}")
    except asyncio.TimeoutError:
        await update.message.reply_text("❌ 실행 시간(3분)이 초과되어 강제 종료되었습니다.")
    except Exception as e:
        await update.message.reply_text(f"❌ 스크립트 실행 중 오류 발생: {e}")

async def cmd_autotrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await run_local_script(update, context, "auto_trader.py", "/autotrade")

async def cmd_morning(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await run_local_script(update, context, "auto_trader.py --mode sell_only", "/morning")

async def cmd_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await run_local_script(update, context, "review_strategy.py", "/review")

async def cmd_macro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await run_local_script(update, context, "macro_daily_reporter.py", "/macro")

async def handle_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'/chart 종목명' 명령어를 처리하여 AI를 거치지 않고 직접 스크립트를 실행하는 함수 (비용 0원)"""
    if not await check_auth(update): return
    
    if not context.args:
        await update.message.reply_text("❌ 종목명을 입력해주세요. (예: /chart 카카오페이)")
        return
        
    stock_name = context.args[0] # "카카오페이" 추출
    chat_id = update.effective_message.chat_id
    
    # 봇이 멈춘 것으로 오해하지 않도록 타이핑 상태 표시
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    
    try:
        # 터미널에서 스크립트 직접 실행
        cmd = f"python3 /Users/daesic/Documents/stock_advisor/analyze_stock.py {stock_name}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        
        output = result.stdout.strip()
        if result.stderr:
            output += "\nError: " + result.stderr.strip()
            
        if not output:
            output = "❌ 분석 결과를 가져오지 못했습니다."
            
        # 텔레그램 채팅창에 결과 전송 (제미나이를 거치지 않음)
        await update.message.reply_text(output)
        
    except Exception as e:
        await update.message.reply_text(f"❌ 스크립트 실행 중 오류 발생: {e}")

async def post_init(application):
    """봇 실행 시 슬래시 명령어 메뉴를 텔레그램 서버에 동기화하는 함수"""
    commands = [
        BotCommand("reset", "대화 기록 초기화"),
        BotCommand("chart", "종목 차트 분석 (예: /chart 카카오)"),
        BotCommand("autotrade", "자동 매매 실행"),
        BotCommand("morning", "아침 시초가 매도 전용 모드"),
        BotCommand("review", "투자 전략 리뷰"),
        BotCommand("macro", "일일 매크로 시황 리포트")
    ]
    await application.bot.set_my_commands(commands)
    await application.bot.send_message(chat_id=ALLOWED_USER_ID, text="안녕하세요! 봇이 정상적으로 실행되었습니다. (현재 무료 API를 우선적으로 사용하고 있습니다.)")

def main():
    """텔레그램 봇을 초기화하고 실행하는 메인 함수"""
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    
    # 명령어와 일반 메시지를 처리할 핸들러 등록
    app.add_handler(CommandHandler("reset", reset_session))
    app.add_handler(CommandHandler("chart", handle_chart))
    app.add_handler(CommandHandler("autotrade", cmd_autotrade))
    app.add_handler(CommandHandler("morning", cmd_morning))
    app.add_handler(CommandHandler("review", cmd_review))
    app.add_handler(CommandHandler("macro", cmd_macro))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Telegram Antigravity Agent (Silent & Summary Mode) Started!")
    # 봇 실행 (텔레그램 서버와 통신 시작)
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
