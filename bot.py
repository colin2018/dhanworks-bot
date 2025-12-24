import os
import time
import sqlite3
import requests
from datetime import datetime, timezone


# =========================
# ENV
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Backward compatible:
HELP_GROUP_LINK = os.getenv("HELP_GROUP_LINK", "").strip()

# New (recommended):
OFFICIAL_CHANNEL_LINK = os.getenv("OFFICIAL_CHANNEL_LINK", "").strip()
SUPPORT_GROUP_LINK = os.getenv("SUPPORT_GROUP_LINK", "").strip()

# Asset channel template (copyMessage)
ASSET_CHANNEL_ID = os.getenv("ASSET_CHANNEL_ID", "").strip()  # e.g. @DhanWorks
INVITE_ASSET_MESSAGE_ID = int((os.getenv("INVITE_ASSET_MESSAGE_ID", "0").strip() or "0"))

# Optional: show Chinese review notes for you (default off)
LANG_NOTE_CN = os.getenv("LANG_NOTE_CN", "0").strip()  # "1" to enable CN notes

# Optional: show Telegram "menu button" near input field (iOS/Android)
ENABLE_MENU_BUTTON = os.getenv("ENABLE_MENU_BUTTON", "1").strip()  # "1" to enable

if not BOT_TOKEN:
    raise SystemExit("Missing BOT_TOKEN env var")

if not HELP_GROUP_LINK and not SUPPORT_GROUP_LINK:
    raise SystemExit("Missing HELP_GROUP_LINK or SUPPORT_GROUP_LINK env var")

if not SUPPORT_GROUP_LINK:
    SUPPORT_GROUP_LINK = HELP_GROUP_LINK

API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def api(method: str, payload: dict | None = None):
    url = f"{API}/{method}"
    r = requests.post(url, json=payload or {}, timeout=45)
    r.raise_for_status()
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError(data)
    return data["result"]


# =========================
# DB
# =========================
conn = sqlite3.connect("dhanworks_bot.db")
cur = conn.cursor()
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
    return datetime.now(timezone.utc).isoformat()


def upsert_user(user_id: int, username: str | None, campaign: str | None):
    ts = now_iso()
    username = username or ""
    campaign = campaign or ""
    cur.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if row:
        cur.execute("SELECT campaign FROM users WHERE user_id=?", (user_id,))
        existing_campaign = (cur.fetchone()[0] or "") if row else ""
        final_campaign = campaign if campaign else existing_campaign
        cur.execute(
            """
            UPDATE users SET username=?, campaign=?, last_seen=?
            WHERE user_id=?
        """,
            (username, final_campaign, ts, user_id),
        )
    else:
        cur.execute(
            """
            INSERT INTO users (user_id, username, campaign, pledged, first_seen, last_seen)
            VALUES (?, ?, ?, 0, ?, ?)
        """,
            (user_id, username, campaign or "organic", ts, ts),
        )
    conn.commit()


def set_pledged(user_id: int, pledged: int):
    cur.execute("UPDATE users SET pledged=? WHERE user_id=?", (pledged, user_id))
    conn.commit()


def is_pledged(user_id: int) -> bool:
    cur.execute("SELECT pledged FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    return bool(row and row[0] == 1)


def add_pending_join(user_id: int, chat_id: int):
    cur.execute(
        """
        INSERT OR REPLACE INTO pending_joins (user_id, chat_id, requested_at)
        VALUES (?, ?, ?)
    """,
        (user_id, chat_id, now_iso()),
    )
    conn.commit()


def get_pending_joins(user_id: int):
    cur.execute("SELECT chat_id FROM pending_joins WHERE user_id=?", (user_id,))
    return [r[0] for r in cur.fetchall()]


def remove_pending_join(user_id: int, chat_id: int):
    cur.execute("DELETE FROM pending_joins WHERE user_id=? AND chat_id=?", (user_id, chat_id))
    conn.commit()


# =========================
# Messaging helpers
# =========================
def send_message(chat_id: int, text: str, reply_markup: dict | None = None):
    payload = {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return api("sendMessage", payload)


def copy_message(to_chat_id: int, from_chat_id: str, message_id: int, reply_markup: dict | None = None):
    payload = {
        "chat_id": to_chat_id,
        "from_chat_id": from_chat_id,
        "message_id": message_id,
        "disable_notification": False,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return api("copyMessage", payload)


def answer_callback(callback_query_id: str, text: str = ""):
    return api("answerCallbackQuery", {"callback_query_id": callback_query_id, "text": text})


def cn_note(s: str) -> str:
    if LANG_NOTE_CN == "1":
        return f"\n\n【中文备注】{s}"
    return ""


# =========================
# Main Menu (Reply Keyboard only)
# =========================
BTN_TUTORIALS = "📘 Tutorials"
BTN_NEWBIE = "🎁 Newbie Rewards"
BTN_TEAM = "👥 Team Earnings"
BTN_CHANNEL = "📢 Official Channel"
BTN_FAQ = "❓ FAQ"


def kb_main_menu():
    # 主菜单用 Reply Keyboard（固定）
    return {
        "keyboard": [
            [{"text": BTN_TUTORIALS}, {"text": BTN_NEWBIE}],
            [{"text": BTN_TEAM}, {"text": BTN_CHANNEL}],
            [{"text": BTN_FAQ}],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False,
        "input_field_placeholder": "Choose a menu option…",
    }


# =========================
# Inline Keyboards (all sub-menus)
# =========================
def inline_back_to_main():
    return {"inline_keyboard": [[{"text": "⬅️ Back to Main Menu", "callback_data": "nav:home"}]]}


def inline_tutorials_menu():
    return {
        "inline_keyboard": [
            [{"text": "① How to Start Earning", "callback_data": "tut:start"}],
            [{"text": "② Payment Tasks Guide", "callback_data": "tut:payment"}],
            [{"text": "③ USDT Deposit Guide", "callback_data": "tut:usdt"}],
            [{"text": "④ Withdrawal & Balance", "callback_data": "tut:withdraw"}],
            [{"text": "⑤ Common Beginner Mistakes", "callback_data": "tut:mistakes"}],
            [{"text": "⬅️ Back", "callback_data": "nav:home"}],
        ]
    }


def inline_team_menu():
    return {
        "inline_keyboard": [
            [{"text": "① How Invitation Rewards Work", "callback_data": "team:invite"}],
            [{"text": "② How Team Earnings Are Calculated", "callback_data": "team:calc"}],
            [{"text": "③ Become a Super Agent", "callback_data": "team:super"}],
            [{"text": "④ Team Income Examples", "callback_data": "team:examples"}],
            [{"text": "⬅️ Back", "callback_data": "nav:home"}],
        ]
    }


def inline_faq_menu():
    return {
        "inline_keyboard": [
            [{"text": "① Payment not approved?", "callback_data": "faq:pay"}],
            [{"text": "② Withdrawal failed?", "callback_data": "faq:wd"}],
            [{"text": "③ Task failed?", "callback_data": "faq:task"}],
            [{"text": "④ Safety & anti-scam", "callback_data": "faq:safety"}],
            [{"text": "⑤ Contact Support Group", "callback_data": "faq:support"}],
            [{"text": "⬅️ Back", "callback_data": "nav:home"}],
        ]
    }


# pledge inline button
def pledge_keyboard():
    return {"inline_keyboard": [[{"text": "I Agree ✅", "callback_data": "pledge_yes"}]]}


# Invite card inline buttons (ONLY Invite Friends)
def invite_inline_kb():
    return {"inline_keyboard": [[{"text": "👥 Invite Friends", "callback_data": "invite:friends"}]]}


# =========================
# Content
# =========================
#def home_text(campaign: str):
    return (
        "✅ Welcome to the DhanWorks EN Hub\n\n"
        f"Campaign: {campaign}\n\n"
        "Use the menu below to continue 👇"
        + cn_note("主菜单Reply Keyboard；其他均用Inline按钮。")
    )


def tutorials_intro_text():
    return (
        "📘 DhanWorks Tutorials Center\n\n"
        "Please choose what you want to learn 👇"
        + cn_note("教程展开使用 Inline Keyboard。")
    )


def tut_start_earning_text():
    return (
        "💰 How to Start Earning (10 Minutes Guide)\n\n"
        "Step 1: Register & login to DhanWorks\n"
        "Step 2: Bind your Telegram account\n"
        "Step 3: Add at least 1 UPI\n"
        "Step 4: Complete your first Payment task\n"
        "Step 5: Receive balance + reward\n\n"
        "👉 Start with a small amount (100 Rs recommended)"
        + cn_note("强调10分钟+小额。")
    )


def tut_payment_text():
    return (
        "📤 Payment Task Process\n\n"
        "1️⃣ Claim a Payment task\n"
        "2️⃣ Select your added UPI\n"
        "3️⃣ Pay using the SAME UPI\n"
        "4️⃣ Upload screenshot + reference number\n"
        "5️⃣ Wait 2–5 minutes for approval\n\n"
        "⚠️ Must complete within 20 minutes"
        + cn_note("同UPI与20分钟限制。")
    )


def tut_usdt_text():
    return (
        "🪙 USDT Deposit Instructions\n\n"
        "✔️ Only TRC20 network is supported\n"
        "✔️ Extra bonus for USDT deposit\n"
        "✔️ Deposit address valid for 20 minutes\n\n"
        "⚠️ Wrong network = funds cannot be recovered"
        + cn_note("USDT仅TRC20。")
    )


def tut_withdraw_text():
    return (
        "💳 Withdrawal & Balance Info\n\n"
        "✔️ Withdraw via UPI\n"
        "✔️ Processing time: usually minutes\n"
        "✔️ Make sure your UPI is active\n\n"
        "👉 Try small withdrawal first"
        + cn_note("先小额提现。")
    )


def tut_mistakes_text():
    return (
        "❌ Common Mistakes to Avoid\n\n"
        "× Exceeding 20 minutes\n"
        "× Paying with wrong UPI\n"
        "× Wrong USDT network\n"
        "× Missing screenshot or reference ID\n\n"
        "📌 Follow the tutorial carefully to avoid issues"
        + cn_note("减少重复问题。")
    )


def newbie_text():
    return (
        "🎁 Newbie Rewards (Total 50 Rs)\n\n"
        "Complete the tasks below to receive rewards 👇\n\n"
        "① Set account PIN\n"
        "② Bind Telegram account\n"
        "③ Add at least 1 KYC UPI\n"
        "④ Complete 1 Payment task\n"
        "⑤ Complete 1 USDT deposit\n\n"
        "📌 Rewards are added automatically after completion"
        + cn_note("新手奖励页面无需二级菜单，按需可加Inline按钮。")
    )


def team_intro_text():
    return (
        "👥 Team Earnings Overview\n\n"
        "You can earn not only by yourself,\n"
        "but also from your team’s activity.\n\n"
        "Choose a topic below 👇"
        + cn_note("团队收益展开使用 Inline Keyboard。")
    )


def team_invite_text():
    return (
        "👤 Invitation Rewards\n\n"
        "✔️ Friend completes task → you earn 0.3%–0.4%\n"
        "✔️ Friend invites others → you earn 0.1%–0.2%\n\n"
        "📌 Team income grows automatically"
        + cn_note("强调被动增长。")
    )


def team_calc_text():
    return (
        "📊 Simple Example\n\n"
        "Team daily volume: 100,000 Rs\n"
        "Estimated daily team income: 200–400 Rs\n\n"
        "👉 No daily operation required"
        + cn_note("用区间表达更稳妥。")
    )


def team_super_text():
    return (
        "👑 Super Agent Requirements\n\n"
        "✔️ Invite at least 30 users\n"
        "✔️ Team daily volume ≥ 1,000,000 Rs\n\n"
        "🎯 Unlock higher team income level"
        + cn_note("超级代理门槛。")
    )


def team_examples_text():
    return (
        "📈 Team Income Examples\n\n"
        "Check the official channel for earning proofs and success stories."
        + cn_note("案例沉淀到频道。")
    )


def channel_text():
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
    else:
        t += "⚠️ Channel link is not set yet. Ask admin to configure OFFICIAL_CHANNEL_LINK."
    return t + cn_note("频道链接用env配置。")


def faq_intro_text():
    return (
        "❓ FAQ Center\n\n"
        "Choose a question below 👇"
        + cn_note("FAQ展开使用 Inline Keyboard。")
    )


def faq_pay_text():
    return (
        "① Payment not approved?\n\n"
        "✔️ Payment exceeded 20 minutes\n"
        "✔️ Wrong UPI used\n"
        "✔️ Missing or incorrect reference ID\n\n"
        "📌 Most issues are caused by incorrect operation"
        + cn_note("引导用户回看教程。")
    )


def faq_wd_text():
    return (
        "② Withdrawal failed?\n\n"
        "✔️ Check if your UPI is active\n"
        "✔️ Try again with a small amount\n"
        "✔️ Make sure account info is correct\n\n"
        f"If still not resolved, contact Support Group:\n{SUPPORT_GROUP_LINK}"
        + cn_note("提现问题先自查。")
    )


def faq_task_text():
    return (
        "③ Task failed?\n\n"
        "✔️ Follow the tutorial steps\n"
        "✔️ Use the SAME UPI you selected\n"
        "✔️ Submit screenshot + reference ID\n\n"
        "Try a small amount task first."
        + cn_note("强调同UPI与提交凭证。")
    )


def faq_safety_text():
    return (
        "④ Safety & Anti-Scam Rules\n\n"
        "✅ We never ask for OTP / PIN / passwords\n"
        "✅ Do not send money to strangers\n"
        "✅ Use only official links from this bot/channel\n"
        "✅ Report impersonators immediately"
        + cn_note("安全声明常驻。")
    )


def faq_support_text():
    return (
        "⑤ Contact Support Group\n\n"
        f"Join the official support group:\n{SUPPORT_GROUP_LINK}\n\n"
        "If your join request is pending:\n"
        "1) Send /join\n"
        "2) Tap I Agree ✅\n"
        "3) Request access again"
        + cn_note("支持入口与自动审批。")
    )


# =========================
# Telegram UI setup (menu button + commands)
# =========================
def setup_bot_ui():
    # Commands shown when user types "/"
    try:
        api(
            "setMyCommands",
            {
                "commands": [
                    {"command": "start", "description": "Open main menu"},
                    {"command": "join", "description": "Join support group"},
                ]
            },
        )
    except Exception as e:
        print("setMyCommands warning:", e)

    # Show "menu button" near input (Telegram client controlled; icon cannot be customized)
    if ENABLE_MENU_BUTTON == "1":
        try:
            # Show commands menu button (the client displays a menu icon / "Open menu bot")
            api("setChatMenuButton", {"menu_button": {"type": "commands"}})
        except Exception as e:
            print("setChatMenuButton warning:", e)


# =========================
# Approval
# =========================
def approve_join(chat_id: int, user_id: int):
    return api("approveChatJoinRequest", {"chat_id": chat_id, "user_id": user_id})


# =========================
# Handlers
# =========================
def handle_start(message: dict):
    chat_id = message["chat"]["id"]
    user = message["from"]
    user_id = user["id"]
    username = user.get("username", "")

    text = message.get("text", "")
    parts = text.split(maxsplit=1)
    payload = parts[1].strip() if len(parts) > 1 else ""
    campaign = payload if payload else "organic"

    upsert_user(user_id, username, campaign)

    # 先推送第7条素材（你的需求1）
    if ASSET_CHANNEL_ID and INVITE_ASSET_MESSAGE_ID:
        try:
            copy_message(
                to_chat_id=chat_id,
                from_chat_id=ASSET_CHANNEL_ID,
                message_id=INVITE_ASSET_MESSAGE_ID,
                reply_markup=invite_inline_kb(),  # 仅Invite Friends（需求2）
            )
        except Exception as e:
            # 如果失败，至少让用户还能看到主菜单
            print("copyMessage on start failed:", e)

    # 再展示主菜单（Reply Keyboard）
    send_message(chat_id, home_text(campaign), reply_markup=kb_main_menu())


def handle_join(message: dict):
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]

    if is_pledged(user_id):
        send_message(
            chat_id,
            "✅ Safety rules accepted.\n\n"
            "Tap to request access:\n"
            f"{SUPPORT_GROUP_LINK}\n\n"
            "If you already requested to join, approval is automatic.",
            reply_markup=kb_main_menu(),
        )
    else:
        send_message(
            chat_id,
            "Before joining the Support Group, confirm:\n\n"
            "✅ I will not DM members for “help”\n"
            "✅ I will never share OTP / PIN / passwords\n"
            "✅ I will follow only official posts from this bot/channel\n\n"
            "Press I Agree to continue.",
            reply_markup=pledge_keyboard(),
        )


def handle_callback_query(update: dict):
    cq = update["callback_query"]
    data = cq.get("data", "")
    cq_id = cq["id"]
    user_id = cq["from"]["id"]
    chat_id = cq["message"]["chat"]["id"]

    # pledge
    if data == "pledge_yes":
        set_pledged(user_id, 1)
        answer_callback(cq_id, "Saved ✅")

        send_message(
            chat_id,
            "✅ Safety rules accepted.\n\n"
            "Tap to request access:\n"
            f"{SUPPORT_GROUP_LINK}\n\n"
            "If you already requested to join, approval will be processed automatically.",
            reply_markup=kb_main_menu(),
        )

        pending = get_pending_joins(user_id)
        for group_chat_id in pending:
            try:
                approve_join(group_chat_id, user_id)
            except Exception as e:
                print("Approve failed:", e)
            else:
                remove_pending_join(user_id, group_chat_id)
        return

    # Invite Friends under asset card
    if data == "invite:friends":
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

    # Inline navigation (需求4)
    if data == "nav:home":
        answer_callback(cq_id, "✅")
        send_message(chat_id, "✅ Main Menu\n\nUse the menu below 👇", reply_markup=kb_main_menu())
        return

    # Tutorials
    if data == "tut:start":
        answer_callback(cq_id, "✅")
        send_message(chat_id, tut_start_earning_text(), reply_markup=inline_back_to_main())
        return
    if data == "tut:payment":
        answer_callback(cq_id, "✅")
        send_message(chat_id, tut_payment_text(), reply_markup=inline_back_to_main())
        return
    if data == "tut:usdt":
        answer_callback(cq_id, "✅")
        send_message(chat_id, tut_usdt_text(), reply_markup=inline_back_to_main())
        return
    if data == "tut:withdraw":
        answer_callback(cq_id, "✅")
        send_message(chat_id, tut_withdraw_text(), reply_markup=inline_back_to_main())
        return
    if data == "tut:mistakes":
        answer_callback(cq_id, "✅")
        send_message(chat_id, tut_mistakes_text(), reply_markup=inline_back_to_main())
        return

    # Team
    if data == "team:invite":
        answer_callback(cq_id, "✅")
        send_message(chat_id, team_invite_text(), reply_markup=inline_back_to_main())
        return
    if data == "team:calc":
        answer_callback(cq_id, "✅")
        send_message(chat_id, team_calc_text(), reply_markup=inline_back_to_main())
        return
    if data == "team:super":
        answer_callback(cq_id, "✅")
        send_message(chat_id, team_super_text(), reply_markup=inline_back_to_main())
        return
    if data == "team:examples":
        answer_callback(cq_id, "✅")
        send_message(chat_id, team_examples_text(), reply_markup=inline_back_to_main())
        return

    # FAQ
    if data == "faq:pay":
        answer_callback(cq_id, "✅")
        send_message(chat_id, faq_pay_text(), reply_markup=inline_back_to_main())
        return
    if data == "faq:wd":
        answer_callback(cq_id, "✅")
        send_message(chat_id, faq_wd_text(), reply_markup=inline_back_to_main())
        return
    if data == "faq:task":
        answer_callback(cq_id, "✅")
        send_message(chat_id, faq_task_text(), reply_markup=inline_back_to_main())
        return
    if data == "faq:safety":
        answer_callback(cq_id, "✅")
        send_message(chat_id, faq_safety_text(), reply_markup=inline_back_to_main())
        return
    if data == "faq:support":
        answer_callback(cq_id, "✅")
        send_message(chat_id, faq_support_text(), reply_markup=inline_back_to_main())
        return

    answer_callback(cq_id, "")


def handle_join_request(update: dict):
    req = update["chat_join_request"]
    chat_id = req["chat"]["id"]
    user = req["from"]
    user_id = user["id"]
    username = user.get("username", "")
    user_chat_id = req.get("user_chat_id", user_id)

    upsert_user(user_id, username, None)

    if is_pledged(user_id):
        try:
            approve_join(chat_id, user_id)
            remove_pending_join(user_id, chat_id)
        except Exception as e:
            print("Approve failed:", e)
    else:
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
            print("Could not message user_chat_id:", e)


def route_main_menu_text(chat_id: int, text: str):
    """
    主菜单用 Reply Keyboard；点击后推送对应内容 + Inline 子菜单（需求4）
    """
    t = (text or "").strip()

    if t == BTN_TUTORIALS:
        send_message(chat_id, tutorials_intro_text(), reply_markup=inline_tutorials_menu())
        return
    if t == BTN_NEWBIE:
        # Newbie直接给信息，并给一个返回主菜单的inline按钮（可选）
        send_message(chat_id, newbie_text(), reply_markup=inline_back_to_main())
        return
    if t == BTN_TEAM:
        send_message(chat_id, team_intro_text(), reply_markup=inline_team_menu())
        return
    if t == BTN_CHANNEL:
        send_message(chat_id, channel_text(), reply_markup=inline_back_to_main())
        return
    if t == BTN_FAQ:
        send_message(chat_id, faq_intro_text(), reply_markup=inline_faq_menu())
        return

    # 其他文字输入 -> 回主菜单
    send_message(chat_id, "Please use the menu below 👇", reply_markup=kb_main_menu())


def handle_text_commands(message: dict):
    chat_id = message["chat"]["id"]
    text = (message.get("text", "") or "").strip()

    # Track user touch
    if "from" in message:
        upsert_user(message["from"]["id"], message["from"].get("username", ""), None)

    # Slash commands
    if text.startswith("/start"):
        handle_start(message)
        return
    if text.startswith("/join"):
        handle_join(message)
        return

    # 主菜单路由（Reply Keyboard）
    route_main_menu_text(chat_id, text)


# =========================
# Main loop
# =========================
def main():
    print("Bot is running (long polling)...")
    offset = 0

    # Ensure webhook is deleted for polling
    try:
        api("deleteWebhook", {"drop_pending_updates": False})
    except Exception as e:
        print("deleteWebhook warning:", e)

    # Configure Telegram client menu button / commands
    setup_bot_ui()

    while True:
        try:
            updates = api("getUpdates", {"timeout": 50, "offset": offset})
            for upd in updates:
                offset = upd["update_id"] + 1

                if "message" in upd:
                    handle_text_commands(upd["message"])

                elif "callback_query" in upd:
                    handle_callback_query(upd)

                elif "chat_join_request" in upd:
                    handle_join_request(upd)

        except Exception as e:
            print("Error:", e)
            time.sleep(2)


if __name__ == "__main__":
    main()
