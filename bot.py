import os
import time
import sqlite3
import requests
from datetime import datetime, timezone

# ================================================================
# 【配置部分】环境变量和常量设置
# ================================================================

# 从环境变量读取 Telegram Bot Token（用于安全考虑）
BOT_TOKEN = os. getenv("BOT_TOKEN", "").strip()

# -------- 主要链接配置 --------
HELP_GROUP_LINK = "t.me/+RRgv2_wgu6gwNGNh"           # 帮助群组链接
OFFICIAL_CHANNEL_LINK = "t.me/DhanWorksMember"      # 官方频道链接
SUPPORT_GROUP_LINK = "https://t.me/YourSupportGroup" # 支持群组链接

# -------- 资源频道配置 --------
ASSET_CHANNEL_ID = "@DhanWorksMember"  # 存储资源素材的频道 ID

# 1. /start 欢迎素材消息 IDs（在用户启动机器人时转发）
ASSET_MESSAGE_IDS = [4, 5, 6, 7]

# 2. 教程素材 - 如何开始赚取 IDs
TUT_START_MESSAGE_IDS = [12, 13, 14]

# 3. 教程素材 - 启动第一个任务 IDs
TUT_TASK_MESSAGE_IDS = [15]

# -------- 功能开关 --------
# 是否显示中文备注（0=关闭，1=开启）
LANG_NOTE_CN = os.getenv("LANG_NOTE_CN", "0").strip()

# 是否启用 Telegram 菜单按钮（iOS/Android 输入框附近）
ENABLE_MENU_BUTTON = os.getenv("ENABLE_MENU_BUTTON", "1").strip()

# -------- 启动检查 --------
if not BOT_TOKEN:
    raise SystemExit("缺少必要的环境变量:  BOT_TOKEN")

# Telegram API 基础 URL
API = f"https://api.telegram.org/bot{BOT_TOKEN}"


# ================================================================
# 【API 通信】与 Telegram API 的交互
# ================================================================

def api(method:  str, payload: dict | None = None):
    """
    发送 HTTP POST 请求到 Telegram API
    
    参数:
        method:  Telegram API 方法名称 (如 'sendMessage', 'getUpdates')
        payload: 请求体数据字典
    
    返回: 
        API 响应的 'result' 字段内容
    
    异常:
        RuntimeError: 当 API 响应的 'ok' 字段为 False 时抛出
    """
    url = f"{API}/{method}"
    r = requests.post(url, json=payload or {}, timeout=45)
    r.raise_for_status()  # 处理 HTTP 错误（如 4xx, 5xx）
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError(data)  # API 返回错误
    return data["result"]


# ================================================================
# 【数据库操作】用户数据和待加入请求的存储
# ================================================================

# 初始化 SQLite 数据库连接
conn = sqlite3.connect("dhanworks_bot.db")
cur = conn.cursor()

# 创建用户表（如果不存在）
cur.execute(
    """
CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY,
  username TEXT,
  campaign TEXT,
  pledged INTEGER DEFAULT 0,
  first_seen TEXT,
  last_seen TEXT
)
"""
)

# 创建待加入请求表（用于追踪用户的群组加入请求）
cur.execute(
    """
CREATE TABLE IF NOT EXISTS pending_joins (
  user_id INTEGER,
  chat_id INTEGER,
  requested_at TEXT,
  PRIMARY KEY (user_id, chat_id)
)
"""
)
conn.commit()


def now_iso():
    """
    获取当前 UTC 时间的 ISO 8601 格式字符串
    用于数据库时间戳记录
    """
    return datetime.now(timezone.utc).isoformat()


def upsert_user(user_id: int, username: str | None, campaign: str | None):
    """
    插入或更新用户记录
    
    逻辑:
    - 如果用户存在：更新 username, campaign, last_seen
    - 如果用户不存在：新建用户，campaign 默认为 'organic'（有机用户）
    
    参数:
        user_id:  Telegram 用户 ID
        username:  Telegram 用户名（可选）
        campaign: 推荐活动名称（如 'facebook', 'twitter'，可选）
    """
    ts = now_iso()
    username = username or ""
    campaign = campaign or ""
    
    # 检查用户是否已存在
    cur.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    
    if row:
        # 用户已存在：获取现有的 campaign，保留现有值或使用新值
        cur.execute("SELECT campaign FROM users WHERE user_id=?", (user_id,))
        existing_campaign = (cur.fetchone()[0] or "") if row else ""
        final_campaign = campaign if campaign else existing_campaign
        
        # 执行更新
        cur.execute(
            """
            UPDATE users SET username=?, campaign=?, last_seen=? 
            WHERE user_id=? 
        """,
            (username, final_campaign, ts, user_id),
        )
    else:
        # 用户不存在：新建记录，campaign 默认为 'organic'
        cur.execute(
            """
            INSERT INTO users (user_id, username, campaign, pledged, first_seen, last_seen)
            VALUES (?, ?, ?, 0, ?, ?)
        """,
            (user_id, username, campaign or "organic", ts, ts),
        )
    
    conn.commit()


def set_pledged(user_id: int, pledged: int):
    """
    标记用户已接受安全协议（承诺）
    
    参数:
        user_id:  Telegram 用户 ID
        pledged: 1=已接受，0=未接受
    """
    cur. execute("UPDATE users SET pledged=? WHERE user_id=?", (pledged, user_id))
    conn.commit()


def is_pledged(user_id:  int) -> bool:
    """
    检查用户是否已接受安全协议
    
    返回:
        True 如果 pledged 字段 = 1，否则 False
    """
    cur.execute("SELECT pledged FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    return bool(row and row[0] == 1)


def add_pending_join(user_id: int, chat_id: int):
    """
    记录用户的群组加入请求（待审批状态）
    在用户还未接受安全协议时使用
    
    参数: 
        user_id: Telegram 用户 ID
        chat_id: 群组/频道 ID
    """
    cur.execute(
        """
        INSERT OR REPLACE INTO pending_joins (user_id, chat_id, requested_at)
        VALUES (?, ?, ?)
    """,
        (user_id, chat_id, now_iso()),
    )
    conn.commit()


def get_pending_joins(user_id: int):
    """
    获取用户所有待加入的群组列表
    
    参数: 
        user_id: Telegram 用户 ID
    
    返回:
        群组 chat_id 列表
    """
    cur.execute("SELECT chat_id FROM pending_joins WHERE user_id=?", (user_id,))
    return [r[0] for r in cur. fetchall()]


def remove_pending_join(user_id: int, chat_id: int):
    """
    移除用户的待加入请求记录（已批准或已处理）
    
    参数:
        user_id:  Telegram 用户 ID
        chat_id: 群组/频道 ID
    """
    cur.execute("DELETE FROM pending_joins WHERE user_id=?  AND chat_id=?", (user_id, chat_id))
    conn.commit()


# ================================================================
# 【消息发送助手】简化 Telegram API 调用
# ================================================================

def send_message(chat_id: int, text: str, reply_markup: dict | None = None):
    """
    向指定聊天发送文本消息
    
    参数:
        chat_id:  目标聊天 ID（用户 ID 或群组 ID）
        text:  消息文本内容
        reply_markup: 键盘或内联按钮配置（可选）
    """
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True,  # 禁用链接预览
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return api("sendMessage", payload)


def forward_messages(chat_id: int, from_chat_id: str, message_ids: list[int]):
    """
    批量转发多条消息到目标聊天
    使用 Telegram 的 forwardMessages API（复数形式）
    
    参数:
        chat_id:  目标聊天 ID
        from_chat_id:  源频道/群组 ID（字符串格式）
        message_ids:  要转发的消息 ID 列表
    """
    payload = {
        "chat_id": chat_id,
        "from_chat_id": from_chat_id,
        "message_ids": message_ids,
        "disable_notification": False,  # 接收者会收到通知
    }
    return api("forwardMessages", payload)


def forward_message(chat_id: int, from_chat_id: str, message_id: int):
    """
    转发单条消息到目标聊天
    使用 Telegram 的 forwardMessage API（单数形式）
    
    参数:
        chat_id:  目标聊天 ID
        from_chat_id:  源频道/群组 ID
        message_id: 要转发的消息 ID
    """
    payload = {
        "chat_id": chat_id,
        "from_chat_id": from_chat_id,
        "message_id": message_id,
        "disable_notification": False,
    }
    return api("forwardMessage", payload)


def answer_callback(callback_query_id: str, text: str = ""):
    """
    响应内联按钮的回调查询
    在用户点击内联按钮时显示弹出提示
    
    参数: 
        callback_query_id:  回调查询 ID
        text: 弹窗提示文本（如果为空则无提示）
    """
    return api("answerCallbackQuery", {"callback_query_id": callback_query_id, "text": text})


def cn_note(s: str) -> str:
    """
    条件性添加中文备注到消息
    如果 LANG_NOTE_CN=1，则在消息末尾附加中文说明
    
    参数: 
        s: 中文备注文本
    
    返回: 
        如果启用则返回 "\n\n【中文备注】{s}"，否则返回空字符串
    """
    if LANG_NOTE_CN == "1":
        return f"\n\n【中文备注】{s}"
    return ""


# ================================================================
# 【键盘配置】Reply Keyboard（底部菜单）和 Inline Keyboard（内联按钮）
# ================================================================

# -------- 主菜单按钮文本 --------
BTN_TUTORIALS = "📘 Tutorials"
BTN_NEWBIE = "🎁 Newbie Rewards"
BTN_TEAM = "💎 Team Earnings"
BTN_CHANNEL = "📢 Official Channel"
BTN_FAQ = "❓ FAQ"


def kb_main_menu():
    """
    生成主菜单的 Reply Keyboard（常驻键盘）
    用户始终可以通过这些按钮访问主要功能
    
    返回:
        Reply Keyboard 配置字典
    """
    return {
        "keyboard": [
            [{"text": BTN_TUTORIALS}, {"text": BTN_NEWBIE}],
            [{"text": BTN_TEAM}, {"text": BTN_CHANNEL}],
            [{"text": BTN_FAQ}],
        ],
        "resize_keyboard": True,           # 键盘高度自适应
        "one_time_keyboard": False,        # 始终显示键盘（不自动隐藏）
        "input_field_placeholder": "Choose a menu option…",  # 输入框占位符
    }


# -------- 内联键盘配置 --------

def inline_tutorials_menu():
    """
    教程子菜单的内联按钮
    显示各类教程选项
    """
    return {
        "inline_keyboard": [
            [{"text": "💸Start Earning", "callback_data": "tut: start"}],
            [{"text": "🟢 Start First Task (100 Rs)", "callback_data": "tut:payment"}],
            [{"text":  "💲 USDT Deposit Task(Easy)", "callback_data": "tut:usdt"}],
            [{"text": "🤑 Withdrawal & Balance", "callback_data": "tut:withdraw"}],
            [{"text": "⚠️ Common Beginner Mistakes", "callback_data": "tut:mistakes"}],
        ]
    }


def inline_team_menu():
    """
    团队收益子菜单的内联按钮
    显示邀请奖励、计算方式、超级代理等选项
    """
    return {
        "inline_keyboard": [
            [{"text": "👥 How Invitation Rewards Work", "callback_data":  "team:invite"}],
            [{"text": "💰 How Team Earnings Are Calculated", "callback_data":  "team:calc"}],
            [{"text": "🤴 Become a Super Agent", "callback_data": "team:super"}],
            [{"text":  "👨‍💻 Team Income Examples", "callback_data": "team:examples"}],
        ]
    }


def inline_faq_menu():
    """
    FAQ 子菜单的内联按钮
    显示常见问题分类
    """
    return {
        "inline_keyboard": [
            [{"text": "① Payment not approved? ", "callback_data": "faq:pay"}],
            [{"text":  "② Withdrawal failed?", "callback_data": "faq: wd"}],
            [{"text": "③ Task failed?", "callback_data": "faq:task"}],
            [{"text": "④ Safety & anti-scam", "callback_data": "faq:safety"}],
            [{"text": "⑤ Contact Support Group", "callback_data": "faq:support"}],
        ]
    }


def pledge_keyboard():
    """
    安全协议接受按钮（用于 /join 命令）
    用户需要确认后才能加入支持群组
    """
    return {"inline_keyboard": [[{"text": "I Agree ✅", "callback_data": "pledge_yes"}]]}


def invite_inline_kb():
    """
    邀请朋友的内联按钮
    （可选，当前未被充分使用）
    """
    return {"inline_keyboard": [[{"text": "👥 Invite Friends", "callback_data": "invite: friends"}]]}


# ================================================================
# 【内容文本】各个菜单选项的文本内容
# ================================================================

def tutorials_intro_text():
    """教程中心介绍文本"""
    return "📘 DhanWorks Tutorials Center\n\nPlease choose what you want to learn 👇" + cn_note("教程展开")


def tut_start_earning_text():
    """如何开始赚取的教程（此函数未被直接调用，通过转发实现）"""
    return (
        "💰 How to Start Earning (10 Minutes Guide)\n\n"
        "Step 1: Register & login to DhanWorks\n"
        "Step 2: Bind your Telegram account\n"
        "Step 3: Add at least 1 UPI\n"
        "Step 4: Complete your first Payment task\n"
        "Step 5: Receive balance + reward\n\n"
        "👉 Start with a small amount (100 Rs recommended)"
    )


def tut_payment_text():
    """支付任务流程教程（此函数未被直接调用，通过转发实现）"""
    return (
        "📤 Payment Task Process\n\n"
        "1️⃣ Claim a Payment task\n"
        "2️⃣ Select your added UPI\n"
        "3️⃣ Pay using the SAME UPI\n"
        "4️⃣ Upload screenshot + reference number\n"
        "5️⃣ Wait 2–5 minutes for approval\n\n"
        "⚠️ Must complete within 20 minutes"
    )


def tut_usdt_text():
    """USDT 存款说明文本"""
    return (
        "🪙 USDT Deposit Instructions\n\n"
        "✔️ Only TRC20 network is supported\n"
        "✔️ Extra bonus for USDT deposit\n"
        "✔️ Deposit address valid for 20 minutes\n\n"
        "⚠️ Wrong network = funds cannot be recovered"
    )


def tut_withdraw_text():
    """提现和余额文本"""
    return (
        "💳 Withdrawal & Balance Info\n\n"
        "✔️ Withdraw via UPI\n"
        "✔️ Processing time: usually minutes\n"
        "✔️ Make sure your UPI is active\n\n"
        "👉 Try small withdrawal first"
    )


def tut_mistakes_text():
    """常见初学者错误文本"""
    return (
        "❌ Common Mistakes to Avoid\n\n"
        "× Exceeding 20 minutes\n"
        "× Paying with wrong UPI\n"
        "× Wrong USDT network\n"
        "× Missing screenshot or reference ID\n\n"
        "📌 Follow the tutorial carefully to avoid issues"
    )


def newbie_text():
    """新手奖励说明文本"""
    return (
        "🎁 Newbie Rewards (Total 50 Rs)\n\n"
        "Complete the tasks below to receive rewards 👇\n\n"
        "① Set account PIN\n"
        "② Bind Telegram account\n"
        "③ Add at least 1 KYC UPI\n"
        "④ Complete 1 Payment task\n"
        "⑤ Complete 1 USDT deposit\n\n"
        "📌 Rewards are added automatically after completion"
    )


def team_intro_text():
    """团队收益介绍文本"""
    return (
        "💎 Team Earnings Overview\n\n"
        "You can earn not only by yourself,\n"
        "but also from your team's activity.\n\n"
        "Choose a topic below 👇"
    )


def team_invite_text():
    """邀请奖励说明文本"""
    return (
        "👤 Invitation Rewards\n\n"
        "✔️ Friend completes task → you earn 0.3%–0.4%\n"
        "✔️ Friend invites others → you earn 0.1%–0.2%\n\n"
        "📌 Team income grows automatically"
    )


def team_calc_text():
    """团队收益计算示例文本"""
    return (
        "📊 Simple Example\n\n"
        "Team daily volume: 100,000 Rs\n"
        "Estimated daily team income: 200–400 Rs\n\n"
        "👉 No daily operation required"
    )


def team_super_text():
    """超级代理要求文本"""
    return (
        "👑 Super Agent Requirements\n\n"
        "✔️ Invite at least 30 users\n"
        "✔️ Team daily volume ≥ 1,000,000 Rs\n\n"
        "🎯 Unlock higher team income level"
    )


def team_examples_text():
    """团队收益示例文本"""
    return "📈 Team Income Examples\n\nCheck the official channel for earning proofs and success stories."


def channel_text():
    """官方频道说明文本"""
    t = (
        "📢 Official DhanWorks Channel\n\n"
        "Here you can find:\n"
        "✔️ Daily earning proofs\n"
        "✔️ Step-by-step tutorials\n"
        "✔️ Important notices\n"
        "✔️ Team success stories\n\n"
    )
    if OFFICIAL_CHANNEL_LINK:
        t += f"Join here:\n{OFFICIAL_CHANNEL_LINK}"
    return t


def faq_intro_text():
    """FAQ 中心介绍文本"""
    return "❓ FAQ Center\n\nChoose a question below 👇"


def faq_pay_text():
    """支付未批准的 FAQ 文本"""
    return (
        "① Payment not approved?\n\n"
        "✔️ Payment exceeded 20 minutes\n"
        "✔️ Wrong UPI used\n"
        "✔️ Missing or incorrect reference ID\n\n"
        "📌 Most issues are caused by incorrect operation"
    )


def faq_wd_text():
    """提现失败的 FAQ 文本"""
    return (
        "② Withdrawal failed?\n\n"
        "✔️ Check if your UPI is active\n"
        "✔️ Try again with a small amount\n"
        "✔️ Make sure account info is correct\n\n"
        f"If still not resolved, contact Support Group:\n{SUPPORT_GROUP_LINK}"
    )


def faq_task_text():
    """任务失败的 FAQ 文本"""
    return (
        "③ Task failed?\n\n"
        "✔️ Follow the tutorial steps\n"
        "✔️ Use the SAME UPI you selected\n"
        "✔️ Submit screenshot + reference ID\n\n"
        "Try a small amount task first."
    )


def faq_safety_text():
    """安全和反诈骗的 FAQ 文本"""
    return (
        "④ Safety & Anti-Scam Rules\n\n"
        "✅ We never ask for OTP / PIN / passwords\n"
        "✅ Do not send money to strangers\n"
        "✅ Use only official links from this bot/channel\n"
        "✅ Report impersonators immediately"
    )


def faq_support_text():
    """联系支持群组的 FAQ 文本"""
    return (
        "⑤ Contact Support Group\n\n"
        f"Join the official support group:\n{SUPPORT_GROUP_LINK}\n\n"
        "If your join request is pending:\n"
        "1) Send /join\n"
        "2) Tap I Agree ✅\n"
        "3) Request access again"
    )


# ================================================================
# 【Telegram 界面设置】Bot 命令和菜单按钮配置
# ================================================================

def setup_bot_ui():
    """
    配置 Telegram Bot 的界面元素
    - 设置 /start 和 /join 命令及其描述
    - 可选：在输入框附近添加菜单按钮
    """
    try:
        # 设置 Bot 命令列表（用户可通过 / 查看）
        api(
            "setMyCommands",
            {
                "commands": [
                    {"command": "start", "description": "Open main menu"},
                    {"command":  "join", "description": "Join support group"},
                ]
            },
        )
    except Exception as e:
        print("⚠️ setMyCommands 警告:", e)

    # 可选：启用菜单按钮（iOS/Android 用户界面）
    if ENABLE_MENU_BUTTON == "1":
        try:
            api("setChatMenuButton", {"menu_button": {"type": "commands"}})
        except Exception as e:
            print("⚠️ setChatMenuButton 警告:", e)


# ================================================================
# 【群组批准】自动批准用户加入群组
# ================================================================

def approve_join(chat_id:  int, user_id: int):
    """
    批准用户加入群组或频道
    在用户已接受安全协议后调用
    
    参数: 
        chat_id: 群组/频道 ID
        user_id: 用户 ID
    """
    return api("approveChatJoinRequest", {"chat_id": chat_id, "user_id": user_id})


# ================================================================
# 【事件处理器】处理 Telegram 更新事件
# ================================================================

def handle_start(message:  dict):
    """
    处理 /start 命令
    
    流程:
    1. 提取用户信息和推荐活动参数
    2. 插入/更新数据库用户记录
    3. 转发欢迎素材消息
    4. 显示主菜单
    
    参数:
        message:  Telegram message 对象
    """
    chat_id = message["chat"]["id"]
    user = message["from"]
    user_id = user["id"]
    username = user. get("username", "")

    # 提取 /start 后的参数（推荐活动来源）
    text = message.get("text", "")
    parts = text.split(maxsplit=1)
    payload = parts[1]. strip() if len(parts) > 1 else ""
    campaign = payload if payload else "organic"  # 默认为有机用户

    # 更新用户信息
    upsert_user(user_id, username, campaign)

    # 1. 转发欢迎素材消息（如果配置了资源频道）
    if ASSET_CHANNEL_ID and ASSET_MESSAGE_IDS:
        try:
            forward_messages(
                chat_id=chat_id,
                from_chat_id=ASSET_CHANNEL_ID,
                message_ids=ASSET_MESSAGE_IDS,
            )
        except Exception as e:
            print(f"❌ 转发欢迎消息失败: {e}")

    # 2. 显示主菜单键盘
    send_message(chat_id, "Menu 👇", reply_markup=kb_main_menu())


def handle_join(message:  dict):
    """
    处理 /join 命令
    
    流程:
    - 如果用户已接受协议：显示支持群组链接
    - 如果用户未接受协议：要求用户接受安全协议
    
    参数:
        message: Telegram message 对象
    """
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]

    if is_pledged(user_id):
        # 用户已接受协议
        send_message(
            chat_id,
            "✅ Safety rules accepted.\n\n"
            "Tap to request access:\n"
            f"{SUPPORT_GROUP_LINK}\n\n"
            "If you already requested to join, approval is automatic.",
            reply_markup=kb_main_menu(),
        )
    else:
        # 用户未接受协议：显示协议内容
        send_message(
            chat_id,
            "Before joining the Support Group, confirm:\n\n"
            "✅ I will not DM members for "help"\n"
            "✅ I will never share OTP / PIN / passwords\n"
            "✅ I will follow only official posts from this bot/channel\n\n"
            "Press I Agree to continue.",
            reply_markup=pledge_keyboard(),
        )


def handle_callback_query(update: dict):
    """
    处理内联按钮点击事件（callback_query）
    
    支持的按钮数据:
    - pledge_yes: 接受安全协议
    - invite: friends: 邀请朋友
    - nav: home: 返回主菜单
    - tut:*: 教程相关
    - team:*: 团队相关
    - faq:*: FAQ 相关
    
    参数:
        update:  Telegram update 对象
    """
    cq = update["callback_query"]
    data = cq.get("data", "")
    cq_id = cq["id"]
    user_id = cq["from"]["id"]
    chat_id = cq["message"]["chat"]["id"]

    # -------- 安全协议接受 --------
    if data == "pledge_yes":
        set_pledged(user_id, 1)  # 标记用户已接受协议
        answer_callback(cq_id, "Saved ✅")
        
        send_message(
            chat_id,
            "✅ Safety rules accepted.\n\n"
            "Tap to request access:\n"
            f"{SUPPORT_GROUP_LINK}\n\n"
            "If you already requested to join, approval will be processed automatically.",
            reply_markup=kb_main_menu(),
        )
        
        # 自动批准用户所有待加入的群组
        pending = get_pending_joins(user_id)
        for group_chat_id in pending:
            try:
                approve_join(group_chat_id, user_id)
            except Exception as e: 
                print(f"❌ 批准加入失败: {e}")
            else:
                remove_pending_join(user_id, group_chat_id)
        return

    # -------- 邀请朋友 --------
    if data == "invite: friends":
        answer_callback(cq_id, "✅")
        send_message(
            chat_id,
            "👥 Invite Friends\n\n"
            "Open DhanWorks App → Team → Copy link\n"
            "Share it to Telegram / WhatsApp.\n\n"
            "📌 When your friends complete tasks, you earn team rewards.",
            reply_markup=kb_main_menu(),
        )
        return

    # -------- 返回主菜单（代码保留，按钮已删除） --------
    if data == "nav:home": 
        answer_callback(cq_id, "✅")
        send_message(chat_id, "✅ Main Menu\n\nUse the menu below 👇", reply_markup=kb_main_menu())
        return

    # -------- 教程：如何开始赚取（使用批量转发） --------
    if data == "tut:start":
        answer_callback(cq_id, "✅")
        try:
            forward_messages(chat_id, ASSET_CHANNEL_ID, TUT_START_MESSAGE_IDS)
        except Exception as e:
            print(f"❌ 转发教程失败: {e}")
        return

    # -------- 教程：支付任务流程（使用批量转发） --------
    if data == "tut:payment":
        answer_callback(cq_id, "✅")
        try:
            forward_messages(chat_id, ASSET_CHANNEL_ID, TUT_TASK_MESSAGE_IDS)
        except Exception as e: 
            print(f"❌ 转发支付任务指南失败: {e}")
        return

    # -------- 其他内容响应的映射 --------
    map_responses = {
        "tut:usdt": tut_usdt_text,
        "tut: withdraw": tut_withdraw_text,
        "tut:mistakes": tut_mistakes_text,
        "team:invite": team_invite_text,
        "team:calc":  team_calc_text,
        "team:super": team_super_text,
        "team:examples":  team_examples_text,
        "faq:pay": faq_pay_text,
        "faq:wd": faq_wd_text,
        "faq:task": faq_task_text,
        "faq:safety":  faq_safety_text,
        "faq:support": faq_support_text,
    }

    if data in map_responses:
        answer_callback(cq_id, "✅")
        send_message(chat_id, map_responses[data]())
        return

    # 未知的回调数据
    answer_callback(cq_id, "")


def handle_join_request(update: dict):
    """
    处理用户加入群组的请求（chat_join_request 事件）
    
    流程:
    1. 记录用户信息到数据库
    2. 如果用户已接受协议：自动批准加入
    3. 如果用户未接受协议：
       - 记录待加入请求
       - 向用户发送接受协议的提示
    
    参数:
        update:  Telegram update 对象
    """
    req = update["chat_join_request"]
    chat_id = req["chat"]["id"]
    user = req["from"]
    user_id = user["id"]
    username = user.get("username", "")
    user_chat_id = req. get("user_chat_id", user_id)  # 用户的私聊 ID

    # 记录用户信息
    upsert_user(user_id, username, None)

    if is_pledged(user_id):
        # 用户已接受协议，直接批准
        try:
            approve_join(chat_id, user_id)
            remove_pending_join(user_id, chat_id)
        except Exception as e:
            print(f"❌ 批准加入失败: {e}")
    else:
        # 用户未接受协议，记录待处理并发送提示
        add_pending_join(user_id, chat_id)
        try:
            send_message(
                user_chat_id,
                "✅ Your join request is pending.\n\n"
                "To get auto-approved:\n"
                "1) Open this bot\n"
                "2) Send /join\n"
                "3) Tap I Agree ✅",
                reply_markup=kb_main_menu(),
            )
        except Exception as e:
            print(f"⚠️ 无法发送消息给用户: {e}")


def route_main_menu_text(chat_id: int, text: str):
    """
    路由主菜单文本命令到相应的处理函数
    
    参数:
        chat_id: 聊天 ID
        text: 用户发送的文本
    """
    t = (text or "").strip()
    
    if t == BTN_TUTORIALS:
        # 教程中心
        send_message(chat_id, tutorials_intro_text(), reply_markup=inline_tutorials_menu())
    elif t == BTN_NEWBIE:
        # 新手奖励
        send_message(chat_id, newbie_text())
    elif t == BTN_TEAM:
        # 团队收益
        send_message(chat_id, team_intro_text(), reply_markup=inline_team_menu())
    elif t == BTN_CHANNEL:
        # 官方频道
        send_message(chat_id, channel_text())
    elif t == BTN_FAQ:
        # FAQ 中心
        send_message(chat_id, faq_intro_text(), reply_markup=inline_faq_menu())
    else:
        # 未识别的命令，提示使用菜单
        send_message(chat_id, "Please use the menu below 👇", reply_markup=kb_main_menu())


def handle_text_commands(message: dict):
    """
    处理文本消息和命令
    
    流程: 
    1. 提取消息内容和用户信息
    2. 更新用户最后活动时间
    3. 路由 /start 或 /join 命令
    4. 路由主菜单按钮文本
    
    参数:
        message:  Telegram message 对象
    """
    chat_id = message["chat"]["id"]
    text = (message. get("text", "") or "").strip()
    
    # 记录用户活动
    if "from" in message:
        upsert_user(
            message["from"]["id"],
            message["from"]. get("username", ""),
            None
        )

    # 路由命令
    if text. startswith("/start"):
        handle_start(message)
        return
    
    if text.startswith("/join"):
        handle_join(message)
        return

    # 路由主菜单文本
    route_main_menu_text(chat_id, text)


# ================================================================
# 【主循环】长轮询获取 Telegram 更新
# ================================================================

def main():
    """
    Bot 主函数
    
    使用长轮询（long polling）方式获取 Telegram 更新：
    1. 删除 Webhook（确保使用轮询模式）
    2. 配置 Bot UI
    3. 无限循环获取和处理更新
    """
    print("🤖 Bot is running (long polling)...")
    offset = 0
    
    # 删除 Webhook（确保使用轮询模式而非 Webhook）
    try:
        api("deleteWebhook", {"drop_pending_updates": False})
    except Exception as e:
        print(f"⚠️ deleteWebhook 警告: {e}")
    
    # 配置 Bot 界面（命令、菜单等）
    setup_bot_ui()

    # 主循环：持续获取和处理更新
    while True:
        try:
            # 获取更新（超时 50 秒）
            updates = api("getUpdates", {"timeout": 50, "offset": offset})
            
            # 处理每个更新
            for upd in updates:
                offset = upd["update_id"] + 1  # 更新偏移量以避免重复处理
                
                if "message" in upd:
                    # 处理文本消息和命令
                    handle_text_commands(upd["message"])
                elif "callback_query" in upd:
                    # 处理内联按钮点击
                    handle_callback_query(upd)
                elif "chat_join_request" in upd: 
                    # 处理群组加入请求
                    handle_join_request(upd)
        
        except Exception as e:
            print(f"❌ 错误:  {e}")
            time.sleep(2)  # 出错时等待 2 秒后重试


# ================================================================
# 【程序入口】
# ================================================================

if __name__ == "__main__":
    main()