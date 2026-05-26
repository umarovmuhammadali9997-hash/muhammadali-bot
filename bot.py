import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackQueryHandler
)
from database import Database
from config import BOT_TOKEN, SUPER_ADMINS, SECTIONS, SOCIAL_LINKS, UMM_PER_REFERRAL, UMM_PER_PREMIUM_REF, UMM_FOR_PREMIUM, PREMIUM_PRICES, BOT_USERNAME
import re
import os

def validate_phone(phone: str) -> bool:
    """O'zbek telefon raqamini tekshirish"""
    phone = phone.strip().replace(" ", "").replace("-", "")
    # +998901234567 yoki 998901234567 yoki 901234567
    pattern = r'^(\+998|998)?[0-9]{9}$'
    return bool(re.match(pattern, phone))

def format_phone(phone: str) -> str:
    """Telefon raqamini standart formatga keltirish"""
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("+998"):
        return phone
    elif phone.startswith("998"):
        return "+" + phone
    else:
        return "+998" + phone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = Database()

# ========================
# KLAVIATURALAR
# ========================

def main_menu_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("👤 Shaxsiy kabinet"), KeyboardButton("🎯 Loyihalar")],
        [KeyboardButton("🔥 DTM 30 Testlar"), KeyboardButton("📝 Test xizmati")],
        [KeyboardButton("👨‍🏫 O'qituvchi haqida")],
    ], resize_keyboard=True)

def cabinet_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("💰 Balansim"), KeyboardButton("💎 UMM tangalarim")],
        [KeyboardButton("➕ Balans to'ldirish"), KeyboardButton("⚡ Pullik kurs sotib olish")],
        [KeyboardButton("🎁 UMM bilan premium olish")],
        [KeyboardButton("◀️ Orqaga")],
    ], resize_keyboard=True)

def test_xizmati_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("✅ DTM test tekshirish")],
        [KeyboardButton("🏅 MS test tekshirish")],
        [KeyboardButton("👨‍🏫 O'qituvchi paneli")],
        [KeyboardButton("◀️ Orqaga")],
    ], resize_keyboard=True)

def loyihalar_keyboard_new():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📚 Nazariya uchun tayyorgarlik")],
        [KeyboardButton("🔬 Masala — noldan boshlash")],
        [KeyboardButton("🏆 Masala — sertifikat darajasi")],
        [KeyboardButton("📝 DTM testlar arxivi")],
        [KeyboardButton("📩 Admin bilan bog'lanish")],
        [KeyboardButton("◀️ Orqaga")],
    ], resize_keyboard=True)

def nazariya_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📖 Nazariy mavzular darsi")],
        [KeyboardButton("📝 Mavzular yuzasidan testlar")],
        [KeyboardButton("🔍 Nazariy test tahlillari")],
        [KeyboardButton("◀️ Orqaga")],
    ], resize_keyboard=True)

def dtm_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📅 Yillar bo'yicha DTM testlar")],
        [KeyboardButton("🔬 Mavzular bo'yicha DTM testlar")],
        [KeyboardButton("◀️ Orqaga")],
    ], resize_keyboard=True)

def dtm_yillar_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📄 DTM 2019"), KeyboardButton("📄 DTM 2020")],
        [KeyboardButton("📄 DTM 2021"), KeyboardButton("📄 DTM 2022")],
        [KeyboardButton("📄 DTM 2023"), KeyboardButton("📄 DTM 2024")],
        [KeyboardButton("◀️ Orqaga")],
    ], resize_keyboard=True)

def dtm_mavzular_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🌿 Botanika"), KeyboardButton("🐾 Zoologiya")],
        [KeyboardButton("🧬 Sitologiya"), KeyboardButton("🧫 Genetika DTM")],
        [KeyboardButton("🦠 Mikrobiologiya"), KeyboardButton("🌱 Ekologiya")],
        [KeyboardButton("◀️ Orqaga")],
    ], resize_keyboard=True)

def sertifikat_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("📚 M.S Kitoblar yechimi")],
        [KeyboardButton("⚡ ATF murakkab masalalar")],
        [KeyboardButton("🧬 DNK murakkab masalalar")],
        [KeyboardButton("🔄 Gametogenez murakkab masalalar")],
        [KeyboardButton("🧪 Genetika murakkab masalalar")],
        [KeyboardButton("🌍 Xardi-Vaynberg masalalari")],
        [KeyboardButton("🔀 Qo'sh krosingover masalalari")],
        [KeyboardButton("🔁 Krosingover murakkab masalalari")],
        [KeyboardButton("◀️ Orqaga")],
    ], resize_keyboard=True)

def noldan_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("⚡ ATF"), KeyboardButton("🧬 DNK")],
        [KeyboardButton("🔄 Gametogenez"), KeyboardButton("🧪 Genetika")],
        [KeyboardButton("🔋 Energetik almashinuv")],
        [KeyboardButton("◀️ Orqaga")],
    ], resize_keyboard=True)

def admin_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🔥 DTM30: Yangi test qo'shish"), KeyboardButton("🗑 DTM30: Test o'chirish")],
        [KeyboardButton("➕ Kontent qo'shish"), KeyboardButton("🗑 Kontent o'chirish")],
        [KeyboardButton("📋 Testlar"), KeyboardButton("➕ Test qo'shish")],
        [KeyboardButton("📊 Test natijalari"), KeyboardButton("👥 Foydalanuvchilar")],
        [KeyboardButton("👥 Adminlar"), KeyboardButton("📊 Statistika")],
        [KeyboardButton("📢 Hammaga xabar"), KeyboardButton("◀️ Orqaga")],
    ], resize_keyboard=True)

def sections_keyboard():
    return ReplyKeyboardMarkup([
        # Nazariya
        [KeyboardButton("📖 Nazariy mavzular darsi")],
        [KeyboardButton("📝 Mavzular yuzasidan testlar")],
        [KeyboardButton("🔍 Nazariy test tahlillari")],
        # Noldan masalalar
        [KeyboardButton("⚡ noldan: ATF"), KeyboardButton("🧬 noldan: DNK")],
        [KeyboardButton("🔄 noldan: Gametogenez"), KeyboardButton("🧪 noldan: Genetika")],
        [KeyboardButton("🔋 noldan: Energetik almashinuv")],
        # Sertifikat darajasi
        [KeyboardButton("📚 sert: M.S Kitoblar")],
        [KeyboardButton("⚡ sert: ATF murakkab"), KeyboardButton("🧬 sert: DNK murakkab")],
        [KeyboardButton("🔄 sert: Gametogenez"), KeyboardButton("🧪 sert: Genetika")],
        [KeyboardButton("🌍 sert: Xardi-Vaynberg")],
        [KeyboardButton("🔀 sert: Qo'sh krosingover")],
        [KeyboardButton("🔁 sert: Krosingover")],
        # DTM arxivi - yillar
        [KeyboardButton("📄 dtm: 2019"), KeyboardButton("📄 dtm: 2020")],
        [KeyboardButton("📄 dtm: 2021"), KeyboardButton("📄 dtm: 2022")],
        [KeyboardButton("📄 dtm: 2023"), KeyboardButton("📄 dtm: 2024")],
        # DTM arxivi - mavzular
        [KeyboardButton("🌿 dtm: Botanika"), KeyboardButton("🐾 dtm: Zoologiya")],
        [KeyboardButton("🧬 dtm: Sitologiya"), KeyboardButton("🧫 dtm: Genetika")],
        [KeyboardButton("🦠 dtm: Mikrobio"), KeyboardButton("🌱 dtm: Ekologiya")],
        # O'qituvchi rasmlari
        [KeyboardButton("👨‍🏫 Muhammadali rasmi"), KeyboardButton("👨‍🏫 Asadulloh rasmi")],
        [KeyboardButton("◀️ Bekor qilish")],
    ], resize_keyboard=True)

# ========================
# YORDAMCHI
# ========================

def is_admin(user_id):
    return db.is_admin(user_id, SUPER_ADMINS)

SECTION_MAP = {
    "⚡ noldan: ATF": "atf",
    "🧬 noldan: DNK": "dnk",
    "🔄 noldan: Gametogenez": "gametogenez",
    "🧪 noldan: Genetika": "genetika",
    "🔋 noldan: Energetik almashinuv": "energetik",
    # Sertifikat (admin panel uchun)
    "📚 sert: M.S Kitoblar": "sert_ms",
    "⚡ sert: ATF murakkab": "sert_atf",
    "🧬 sert: DNK murakkab": "sert_dnk",
    "🔄 sert: Gametogenez": "sert_gamet",
    "🧪 sert: Genetika": "sert_genetika",
    "🌍 sert: Xardi-Vaynberg": "sert_xardi",
    "🔀 sert: Qo'sh krosingover": "sert_qosh",
    "🔁 sert: Krosingover": "sert_krosing",
    # DTM arxivi (admin panel uchun)
    "📄 dtm: 2019": "dtm_2019",
    "📄 dtm: 2020": "dtm_2020",
    "📄 dtm: 2021": "dtm_2021",
    "📄 dtm: 2022": "dtm_2022",
    "📄 dtm: 2023": "dtm_2023",
    "📄 dtm: 2024": "dtm_2024",
    "🌿 dtm: Botanika": "dtm_botanika",
    "🐾 dtm: Zoologiya": "dtm_zoologiya",
    "🧬 dtm: Sitologiya": "dtm_sitologiya",
    "🧫 dtm: Genetika": "dtm_genetika",
    "🦠 dtm: Mikrobio": "dtm_mikrobio",
    "🌱 dtm: Ekologiya": "dtm_ekologiya",
    # Nazariya (admin panel uchun)
    "📖 Nazariy mavzular darsi": "nazariy_dars",
    "📝 Mavzular yuzasidan testlar": "mavzu_testlar",
    "🔍 Nazariy test tahlillari": "test_tahlil",
    # O'qituvchi rasmlari
    "👨‍🏫 Muhammadali rasmi": "teacher_photo",
    "👨‍🏫 Asadulloh rasmi": "teacher2_photo",
    "⚡ ATF": "atf",
    "🧬 DNK": "dnk",
    "🔄 Gametogenez": "gametogenez",
    "🧪 Genetika": "genetika",
    "🔋 Energetik almashinuv": "energetik",
    # Sertifikat bo'limlari
    "📅 Yillar bo'yicha DTM testlar": "dtm_yillar_menu",
    "🔬 Mavzular bo'yicha DTM testlar": "dtm_mavzular_menu",
    "📄 DTM 2019": "dtm_2019",
    "📄 DTM 2020": "dtm_2020",
    "📄 DTM 2021": "dtm_2021",
    "📄 DTM 2022": "dtm_2022",
    "📄 DTM 2023": "dtm_2023",
    "📄 DTM 2024": "dtm_2024",
    "🌿 Botanika": "dtm_botanika",
    "🐾 Zoologiya": "dtm_zoologiya",
    "🧬 Sitologiya": "dtm_sitologiya",
    "🧫 Genetika DTM": "dtm_genetika",
    "🦠 Mikrobiologiya": "dtm_mikrobio",
    "🌱 Ekologiya": "dtm_ekologiya",
    "📚 M.S Kitoblar yechimi": "sert_ms",
    "⚡ ATF murakkab masalalar": "sert_atf",
    "🧬 DNK murakkab masalalar": "sert_dnk",
    "🔄 Gametogenez murakkab masalalar": "sert_gamet",
    "🧪 Genetika murakkab masalalar": "sert_genetika",
    "🌍 Xardi-Vaynberg masalalari": "sert_xardi",
    "🔀 Qo'sh krosingover masalalari": "sert_qosh",
    "🔁 Krosingover murakkab masalalari": "sert_krosing",
    "📖 Nazariy mavzular darsi": "nazariy_dars",
    "📝 Mavzular yuzasidan testlar": "mavzu_testlar",
    "🔍 Nazariy test tahlillari": "test_tahlil",
}

# ========================
# /start
# ========================

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    user = update.effective_user
    await update.message.reply_text(
        f"Bosh menyu 👇",
        reply_markup=main_menu_keyboard()
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_new = db.get_user(user.id) is None  # add_user DAN OLDIN tekshirish
    db.add_user(user.id, user.full_name, user.username)
    context.user_data.clear()

    # Referal tekshirish — faqat yangi foydalanuvchi uchun, bir marta
    args = context.args
    if args and is_new:
        try:
            referrer_id = int(args[0])
            # referrer o'zi bilan bir xil bo'lmasligi kerak
            if referrer_id != user.id:
                success = db.set_referred_by_safe(user.id, referrer_id)
                if success:
                    # Taklif qilganga UMM ber
                    db.add_umm(referrer_id, UMM_PER_REFERRAL)
                    db.add_referral(referrer_id, user.id, "join", UMM_PER_REFERRAL)
                    try:
                        ref_count = db.get_referral_count(referrer_id)
                        await context.bot.send_message(
                            referrer_id,
                            f"🎉 *Do'stingiz botga qo'shildi!*\n"
                            f"💎 Sizga *+{UMM_PER_REFERRAL} UMM* tanga berildi!\n"
                            f"👥 Jami taklif qilganlar: *{ref_count} ta*",
                            parse_mode="Markdown"
                        )
                    except:
                        pass
        except:
            pass

    caption = (
        f"Assalomu aleykum, *{user.first_name}*! 👋\n\n"
        "🎓 Siz *Muhammadali Umarov* — biologiya fan ustozi botiga xush kelibsiz!\n\n"
        "👨‍🏫 Men biologiya fanidan *Milliy sertifikat* va *DTM* imtihonlariga "
        "o'quvchilarni tayyorlash bilan shug'ullanaman.\n\n"
        "📌 *Bu bot orqali siz:*\n"
        "✅ Nazariy testlarni tahlil qilishni o'rganasiz\n"
        "✅ Mavzular bo'yicha ma'ruzalarni ko'rasiz\n"
        "✅ Masalalarni noldan o'rganasiz\n"
        "✅ Sertifikat darajasidagi masalalarni yechasiz\n"
        "✅ Bepul tayyorgarlik ko'rasiz!\n\n"
        "👇 Kerakli bo'limni tanlang:"
    )
    await update.message.reply_text(
        caption, parse_mode="Markdown", reply_markup=main_menu_keyboard()
    )

    # Profil to'ldirilmagan bo'lsa so'rash
    if is_new and not db.is_profile_complete(user.id):
        context.user_data["action"] = "profile_name"
        await update.message.reply_text(
            "📋 *Bir marta ma'lumotlaringizni kiriting*\n\n"
            "Bu ma'lumotlar test natijalaringizni saqlash uchun kerak.\n\n"
            "1️⃣ To'liq ismingizni yozing:\n_(Masalan: Karimov Jasur)_",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("⏭ O'tkazib yuborish")]],
                resize_keyboard=True
            )
        )

# ========================
# ASOSIY MENYULAR
# ========================

async def shaxsiy_kabinet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        db.add_user(user.id, user.full_name, user.username or "")
        user_data = db.get_user(user.id) or {}
        balance = user_data.get('balance', 0)
        umm = db.get_umm(user.id)
        is_prem = db.is_premium(user.id)
        ref_count = db.get_referral_count(user.id)
        premium_status = "✅ Aktiv" if is_prem else "❌ Yo'q"
        ref_link = f"{os.environ.get('REF_LINK_BASE', 'https://t.me/umm_biologiya_bot')}?start={user.id}"

        await update.message.reply_text(
            f"👤 *Shaxsiy kabinet*\n\n"
            f"🆔 ID: `{user.id}`\n"
            f"👤 Ism: *{user.full_name}*\n"
            f"💰 Balans: *{balance} so'm*\n"
            f"💎 UMM tangalar: *{umm} UMM*\n"
            f"⚡ Premium: {premium_status}\n"
            f"👥 Taklif qilinganlar: *{ref_count} ta*\n\n"
            f"🔗 *Referal havolangiz:*\n{ref_link}\n\n"
            f"Do'st taklif qiling → *+{UMM_PER_REFERRAL} UMM*\n"
            f"Do'st premium olsa → *+{UMM_PER_PREMIUM_REF} UMM*\n"
            f"*{UMM_FOR_PREMIUM} UMM* = 1 oy Premium!",
            parse_mode="Markdown",
            reply_markup=cabinet_keyboard()
        )
    except Exception as e:
        logger.error(f"Kabinet xato: {e}")
        await update.message.reply_text(
            "👤 Shaxsiy kabinet",
            reply_markup=cabinet_keyboard()
        )

async def umm_tangalarim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    umm = db.get_umm(user_id)
    ref_count = db.get_referral_count(user_id)
    ref_link = f"{os.environ.get('REF_LINK_BASE', 'https://t.me/umm_biologiya_bot')}?start={user_id}"
    await update.message.reply_text(
        f"💎 *UMM Tanga tizimi*\n\n"
        f"Sizda: *{umm} UMM*\n"
        f"Taklif qilinganlar: *{ref_count} ta*\n\n"
        f"📌 *Qanday UMM ishlash mumkin:*\n"
        f"• Do'st taklif qiling → *+{UMM_PER_REFERRAL} UMM*\n"
        f"• Do'st premium olsa → *+{UMM_PER_PREMIUM_REF} UMM*\n\n"
        f"💡 *{UMM_FOR_PREMIUM} UMM = 1 oy Premium*\n\n"
        f"🔗 Referal havolangiz:\n{ref_link}",
        parse_mode="Markdown",
        reply_markup=cabinet_keyboard()
    )

async def umm_premium_olish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    umm = db.get_umm(user_id)
    if umm >= UMM_FOR_PREMIUM:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"✅ {UMM_FOR_PREMIUM} UMM sarflash — 1 oy Premium", callback_data="umm_buy_premium")]
        ])
        await update.message.reply_text(
            f"💎 Sizda *{umm} UMM* bor\n\n"
            f"*{UMM_FOR_PREMIUM} UMM* sarflab *1 oy Premium* olasizmi?",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    else:
        kerak = UMM_FOR_PREMIUM - umm
        ref_link = f"{os.environ.get('REF_LINK_BASE', 'https://t.me/umm_biologiya_bot')}?start={user_id}"
        await update.message.reply_text(
            f"💎 Sizda *{umm} UMM* bor\n"
            f"Premium uchun *{UMM_FOR_PREMIUM} UMM* kerak\n"
            f"Yana *{kerak} UMM* yig'ing!\n\n"
            f"🔗 Do'stlaringizni taklif qiling:\n{ref_link}",
            parse_mode="Markdown",
            reply_markup=cabinet_keyboard()
        )

async def balansim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        db.add_user(user.id, user.full_name, user.username or "")
        user_data = db.get_user(user.id) or {}
        balance = user_data.get('balance', 0)
        umm = db.get_umm(user.id)
        is_prem = db.is_premium(user.id)
        premium_status = "✅ Aktiv" if is_prem else "❌ Yo'q"
        await update.message.reply_text(
            f"💰 *Balansingiz*\n\n"
            f"💵 Pul balansi: *{balance} so'm*\n"
            f"💎 UMM tangalar: *{umm} UMM*\n"
            f"⚡ Premium: {premium_status}\n\n"
            f"Balans to'ldirish uchun ➕ tugmasini bosing.",
            parse_mode="Markdown",
            reply_markup=cabinet_keyboard()
        )
    except Exception as e:
        logger.error(f"Balansim xato: {e}")
        await update.message.reply_text("💰 Balans ma'lumotlari", reply_markup=cabinet_keyboard())

async def balans_toldirish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        ref_link = f"{os.environ.get('REF_LINK_BASE', 'https://t.me/umm_biologiya_bot')}?start={user.id}"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Karta orqali to'ldirish", callback_data="pay_card")],
            [InlineKeyboardButton("👥 Referal orqali UMM ishlash", callback_data="pay_ref")],
        ])
        await update.message.reply_text(
            "➕ *Balans to'ldirish*\n\n"
            "Qaysi usulni tanlaysiz?\n\n"
            "💳 *Karta orqali* — pul to'lab premium oling\n"
            "👥 *Referal orqali* — do'stlarni taklif qilib UMM tanga ishlang\n"
            f"   (+{UMM_PER_REFERRAL} UMM = 1 do'st, +{UMM_PER_PREMIUM_REF} UMM = do'st premium olsa)\n"
            f"   {UMM_FOR_PREMIUM} UMM = 1 oy Premium!",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Balans toldirish xato: {e}")
        await update.message.reply_text("➕ Balans to'ldirish", reply_markup=cabinet_keyboard())

async def pullik_kurs_sotib_olish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ 1 oylik — 100,000 so'm", callback_data="buy_1")],
        [InlineKeyboardButton("⚡ 3 oylik — 250,000 so'm", callback_data="buy_3")],
        [InlineKeyboardButton("⚡ 1 yillik — 800,000 so'm", callback_data="buy_12")],
    ])
    await update.message.reply_text(
        "⚡ *Pullik kurs — Tariflar*\n\n"
        "Premium obuna bilan barcha materiallar ochiladi!\n\n"
        "Tarifni tanlang 👇",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def pay_card_ref_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "pay_card":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚡ 1 oylik — 50,000 so'm", callback_data="buy_1")],
            [InlineKeyboardButton("⚡ 3 oylik — 120,000 so'm", callback_data="buy_3")],
            [InlineKeyboardButton("⚡ 1 yillik — 400,000 so'm", callback_data="buy_12")],
        ])
        await query.edit_message_text(
            "💳 *Karta orqali to'lov*\n\n"
            "Tarifni tanlang 👇",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    elif query.data == "pay_ref":
        ref_link = f"{os.environ.get('REF_LINK_BASE', 'https://t.me/umm_biologiya_bot')}?start={user_id}"
        umm = db.get_umm(user_id)
        ref_count = db.get_referral_count(user_id)
        await query.edit_message_text(
            f"👥 *Referal orqali UMM ishlash*\n\n"
            f"💎 Sizda hozir: *{umm} UMM*\n"
            f"👥 Taklif qilganlar: *{ref_count} ta*\n\n"
            f"📌 *Qoidalar:*\n"
            f"• Do'st taklif qiling → *+{UMM_PER_REFERRAL} UMM*\n"
            f"• Do'st premium olsa → *+{UMM_PER_PREMIUM_REF} UMM*\n"
            f"• *{UMM_FOR_PREMIUM} UMM* = 1 oy Premium!\n\n"
            f"🔗 *Referal havolangiz:*\n{ref_link}\n\n"
            f"Ushbu havolani do'stlaringizga yuboring!",
            parse_mode="Markdown"
        )

async def umm_buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    umm = db.get_umm(user_id)
    if umm >= UMM_FOR_PREMIUM:
        success = db.spend_umm(user_id, UMM_FOR_PREMIUM)
        if success:
            db.activate_premium_with_umm(user_id)
            # Referrer ga UMM_PER_PREMIUM_REF UMM ber
            user_data = db.get_user(user_id)
            if user_data and user_data.get('referred_by'):
                referrer_id = user_data['referred_by']
                db.add_umm(referrer_id, UMM_PER_PREMIUM_REF)
                db.add_referral(referrer_id, user_id, "premium", UMM_PER_PREMIUM_REF)
                try:
                    await context.bot.send_message(
                        referrer_id,
                        f"🎉 Do'stingiz Premium oldi!\n💎 Sizga *+{UMM_PER_PREMIUM_REF} UMM* berildi!",
                        parse_mode="Markdown"
                    )
                except:
                    pass
            await query.edit_message_text(
                f"🎉 *Tabriklaymiz!*\n\n"
                f"⚡ *1 oy Premium faollashtirildi!*\n"
                f"💎 {UMM_FOR_PREMIUM} UMM sarflandi.",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text("❌ UMM yetarli emas!")
    else:
        await query.edit_message_text(f"❌ UMM yetarli emas! Kerak: {UMM_FOR_PREMIUM}")

async def buy_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    prices = {"buy_1": "100,000", "buy_3": "250,000", "buy_12": "800,000"}
    months = {"buy_1": "1 oy", "buy_3": "3 oy", "buy_12": "1 yil"}
    data = query.data
    await query.edit_message_text(
        f"⚡ *{months[data]} Premium*\n\n"
        f"Narxi: *{prices[data]} so'm*\n\n"
        f"💳 Karta: `8600 0000 0000 0000`\n\n"
        f"To'lovdan so'ng chekni yuboring: @biolog_UMM",
        parse_mode="Markdown"
    )

async def loyihalar_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎯 *Loyihalar*\n\nQaysi bo'limga kirishni xohlaysiz?",
        parse_mode="Markdown",
        reply_markup=loyihalar_keyboard_new()
    )

async def test_xizmati(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📝 *Test xizmati*\n\nNimani qilmoqchisiz?",
        parse_mode="Markdown",
        reply_markup=test_xizmati_keyboard()
    )

async def nazariya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 *Nazariya uchun tayyorgarlik*\n\nQaysi bo'limga kirishni xohlaysiz?",
        parse_mode="Markdown",
        reply_markup=nazariya_keyboard()
    )

async def nazariy_dars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_section(update, context, "nazariy_dars")

async def mavzu_testlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_section(update, context, "mavzu_testlar")

async def test_tahlil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_section(update, context, "test_tahlil")

async def masala_noldan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔬 *Masala — noldan boshlash*\n\nQaysi mavzuni o'rganmoqchisiz?",
        parse_mode="Markdown", reply_markup=noldan_keyboard()
    )

# ========================
# O'QITUVCHI PANEL
# ========================

def teacher_menu_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("➕ Test yaratish"), KeyboardButton("➕ MS Test yaratish")],
        [KeyboardButton("📋 Mening testlarim"), KeyboardButton("📊 Natijalarni ko'rish")],
        [KeyboardButton("🗑 Testni o'chirish"), KeyboardButton("◀️ Orqaga")],
    ], resize_keyboard=True)

async def teacher_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not db.is_teacher(user_id):
        # Ro'yxatdan o'tmagan — boshlash
        context.user_data["action"] = "teacher_reg_name"
        await update.message.reply_text(
            "👨‍🏫 *O'qituvchi paneli*\n\n"
            "Siz hali ro'yxatdan o'tmagansiz!\n\n"
            "1-qadam: To'liq ismingizni yozing:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("◀️ Orqaga")]], resize_keyboard=True)
        )
        return

    teacher = db.get_teacher(user_id)
    tests = db.get_teacher_tests(user_id)
    await update.message.reply_text(
        f"👨‍🏫 *O'qituvchi paneli*\n\n"
        f"Xush kelibsiz, *{teacher['full_name']}*!\n"
        f"📚 Fan: {teacher['subject']}\n"
        f"📝 Testlar soni: *{len(tests)} ta*\n\n"
        f"Nima qilmoqchisiz?",
        parse_mode="Markdown",
        reply_markup=teacher_menu_keyboard()
    )

async def teacher_my_tests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not db.is_teacher(user_id):
        await teacher_panel(update, context)
        return
    tests = db.get_teacher_tests(user_id)
    if not tests:
        await update.message.reply_text(
            "📭 Sizda hozircha test yo'q.\n\n➕ Test yaratish tugmasini bosing!",
            reply_markup=teacher_menu_keyboard()
        )
        return
    text = "📋 *Sizning testlaringiz:*\n\n"
    for t in tests:
        text += f"📝 *{t['title']}*\n🔑 Kod: `{t['code']}` | {t['question_count']} ta savol\n\n"
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=teacher_menu_keyboard())

async def teacher_create_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not db.is_teacher(user_id):
        await teacher_panel(update, context)
        return
    context.user_data["action"] = "teacher_test_step1"
    await update.message.reply_text(
        "➕ *Yangi test yaratish*\n\n"
        "1-qadam: Test uchun noyob kod kiriting\n"
        "_(Masalan: FIZIKA001 — boshqa o'qituvchi kodi bilan bir xil bo'lmasin)_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("◀️ Orqaga")]], resize_keyboard=True)
    )

async def teacher_delete_test_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not db.is_teacher(user_id):
        await teacher_panel(update, context)
        return
    tests = db.get_teacher_tests(user_id)
    if not tests:
        await update.message.reply_text("📭 O'chiradigan test yo'q.", reply_markup=teacher_menu_keyboard())
        return
    keyboard = [[InlineKeyboardButton(f"🗑 {t['title']} ({t['code']})", callback_data=f"del_ttest_{t['code']}")] for t in tests]
    await update.message.reply_text(
        "🗑 *Qaysi testni o'chirmoqchisiz?*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def teacher_create_ms_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not db.is_teacher(user_id):
        await teacher_panel(update, context)
        return
    context.user_data["action"] = "teacher_ms_step1"
    await update.message.reply_text(
        "➕ *MS Test yaratish (43 savol)*\n\n"
        "📌 Tuzilma:\n"
        "• 1-32: A/B/C/D variantlar\n"
        "• 33-40: Yozma javoblar\n"
        "• 41: 30 ball | 42: 35 ball | 43: 10 ball\n\n"
        "1-qadam: Test uchun noyob kod kiriting:\n"
        "_(Masalan: MS_BIO001)_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("◀️ Orqaga")]], resize_keyboard=True)
    )

async def dtm_testlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📝 *DTM testlar*\n\nQanday ko'rinishda qidirmoqchisiz?",
        parse_mode="Markdown",
        reply_markup=dtm_keyboard()
    )

async def dtm_yillar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📅 *Yillar bo'yicha DTM testlar*\n\nYilni tanlang:",
        parse_mode="Markdown",
        reply_markup=dtm_yillar_keyboard()
    )

async def dtm_mavzular(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔬 *Mavzular bo'yicha DTM testlar*\n\nMavzuni tanlang:",
        parse_mode="Markdown",
        reply_markup=dtm_mavzular_keyboard()
    )

# ========================
# TEST TEKSHIRISH
# ========================

def build_answer_keyboard(user_answers: dict, total: int):
    """30 ta savol uchun inline klaviatura"""
    keyboard = []
    for i in range(1, total + 1):
        ans = user_answers.get(str(i), "❓")
        row_btn = InlineKeyboardButton(f"{i}:{ans}", callback_data=f"q_{i}")
        if i % 5 == 1:
            keyboard.append([row_btn])
        else:
            keyboard[-1].append(row_btn)
    keyboard.append([
        InlineKeyboardButton("✅ Natijani ko'rish", callback_data="check_result"),
        InlineKeyboardButton("🔄 Qayta boshlash", callback_data="reset_answers")
    ])
    return InlineKeyboardMarkup(keyboard)

def build_variant_keyboard(q_num: int):
    """A/B/C/D/E variant tanlash uchun"""
    keyboard = [
        [
            InlineKeyboardButton("A", callback_data=f"ans_{q_num}_A"),
            InlineKeyboardButton("B", callback_data=f"ans_{q_num}_B"),
            InlineKeyboardButton("C", callback_data=f"ans_{q_num}_C"),
            InlineKeyboardButton("D", callback_data=f"ans_{q_num}_D"),
            InlineKeyboardButton("E", callback_data=f"ans_{q_num}_E"),
        ],
        [InlineKeyboardButton("◀️ Orqaga", callback_data="back_to_answers")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def test_tekshirish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["action"] = "student_reg_name"
    await update.message.reply_text(
        "✅ *Test tekshirish*\n\n"
        "Davom etish uchun bir necha ma'lumot kerak:\n\n"
        "1️⃣ To'liq ismingizni yozing:\n"
        "_(Masalan: Karimov Jasur)_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("◀️ Orqaga")]], resize_keyboard=True)
    )

async def handle_test_code(update: Update, context: ContextTypes.DEFAULT_TYPE, code: str):
    test = db.get_test(code.upper())
    if not test:
        await update.message.reply_text(
            "❌ *Bunday kodli test topilmadi!*\n\nKodni tekshirib qayta kiriting.",
            parse_mode="Markdown"
        )
        return

    context.user_data["current_test"] = test
    context.user_data["user_answers"] = {}
    context.user_data["action"] = "answering_test"

    total = test["question_count"]

    # PDF yuborish
    try:
        await update.message.reply_document(
            document=test["pdf_file_id"],
            caption=f"📄 *{test['title']}*\n\nTest savollari ({total} ta)",
            parse_mode="Markdown"
        )
    except:
        pass

    await update.message.reply_text(
        f"✅ *{test['title']}*\n\n"
        f"📊 Savollar soni: *{total} ta*\n\n"
        f"Har bir savol raqamini bosib, javobingizni tanlang 👇\n"
        f"_(❓ — hali javob berilmagan)_",
        parse_mode="Markdown",
        reply_markup=build_answer_keyboard({}, total)
    )

async def test_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    test = context.user_data.get("current_test")
    user_answers = context.user_data.get("user_answers", {})

    if not test:
        await query.edit_message_text("❌ Test topilmadi. /start bosing.")
        return

    total = test["question_count"]

    # Savol raqami bosildi
    if data.startswith("q_"):
        q_num = int(data.split("_")[1])
        context.user_data["current_question"] = q_num
        current_ans = user_answers.get(str(q_num), "❓")
        await query.edit_message_text(
            f"*{q_num}-savol* uchun javobni tanlang:\n"
            f"Hozirgi: *{current_ans}*",
            parse_mode="Markdown",
            reply_markup=build_variant_keyboard(q_num)
        )

    # Variant tanlandi
    elif data.startswith("ans_"):
        parts = data.split("_")
        q_num = parts[1]
        variant = parts[2]
        user_answers[q_num] = variant
        context.user_data["user_answers"] = user_answers
        answered = len(user_answers)
        await query.edit_message_text(
            f"📊 Javob berildi: *{answered}/{total}*\n\n"
            f"Qolgan savollarni ham belgilang 👇\n"
            f"_(❓ — hali javob berilmagan)_",
            parse_mode="Markdown",
            reply_markup=build_answer_keyboard(user_answers, total)
        )

    # Orqaga
    elif data == "back_to_answers":
        answered = len(user_answers)
        await query.edit_message_text(
            f"📊 Javob berildi: *{answered}/{total}*\n\n"
            f"Har bir savol raqamini bosib, javobingizni tanlang 👇",
            parse_mode="Markdown",
            reply_markup=build_answer_keyboard(user_answers, total)
        )

    # Qayta boshlash
    elif data == "reset_answers":
        context.user_data["user_answers"] = {}
        await query.edit_message_text(
            f"🔄 Javoblar tozalandi!\n\nQaytadan boshlang 👇",
            parse_mode="Markdown",
            reply_markup=build_answer_keyboard({}, total)
        )

    # Natijani ko'rish
    elif data == "check_result":
        answered = len(user_answers)
        if answered < total:
            await query.answer(
                f"⚠️ Hali {total - answered} ta savol javobsiz! Barchasiga javob bering.",
                show_alert=True
            )
            return

        correct_answers = test["answers"].upper().split(",")
        correct_count = 0
        wrong_list = []

        for i in range(1, total + 1):
            user_ans = user_answers.get(str(i), "").upper()
            correct_ans = correct_answers[i-1].strip() if i <= len(correct_answers) else "?"
            if user_ans == correct_ans:
                correct_count += 1
            else:
                wrong_list.append(f"{i}-savol: Siz *{user_ans}* | To'g'ri *{correct_ans}*")

        wrong_count = total - correct_count
        percentage = round((correct_count / total) * 100, 1)
        ball = correct_count * 3.1  # DTM hisobi

        if percentage >= 90:
            emoji = "🥇"
        elif percentage >= 70:
            emoji = "🥈"
        elif percentage >= 50:
            emoji = "🥉"
        else:
            emoji = "📚"

        result_text = (
            f"{emoji} *Natija: {test['title']}*\n\n"
            f"✅ To'g'ri: *{correct_count}/{total}*\n"
            f"❌ Noto'g'ri: *{wrong_count}/{total}*\n"
            f"📊 Foiz: *{percentage}%*\n"
            f"🏆 Ball: *{ball:.1f}*\n\n"
        )

        if wrong_list:
            result_text += "❌ *Noto'g'ri javoblar:*\n"
            result_text += "\n".join(wrong_list[:15])
            if len(wrong_list) > 15:
                result_text += f"\n_...va yana {len(wrong_list)-15} ta_"

        # Natijani database ga saqlash
        try:
            user_data = context.user_data
            db.save_test_result(
                user_id=query.from_user.id,
                full_name=user_data.get("s_name", "Noma'lum"),
                region=user_data.get("s_region", "—"),
                phone=user_data.get("s_phone", "—"),
                grade=user_data.get("s_grade", "—"),
                test_code=test["code"],
                correct=correct_count,
                wrong=wrong_count,
                total=total,
                percentage=percentage,
                ball=ball
            )
        except Exception as e:
            logger.error(f"Natija saqlashda xato: {e}")

        context.user_data.clear()
        await query.edit_message_text(result_text, parse_mode="Markdown")

        # Video yechimni avtomatik yuborish
        video = db.get_test_video(test["code"])
        if video:
            try:
                await context.bot.send_video(
                    chat_id=query.from_user.id,
                    video=video["video_file_id"],
                    caption=f"🎬 *{test['title']} — Video yechim*\n\nHar bir savolni tahlil bilan ko'ring!",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Video yuborishda xato: {e}")

async def masala_sertifikat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏆 *Masala — sertifikat darajasi*\n\nQaysi mavzuni o'rganmoqchisiz?",
        parse_mode="Markdown",
        reply_markup=sertifikat_keyboard()
    )

async def o_qituvchi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1-o'qituvchi: Muhammadali
    keyboard1 = InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Telegram", url=SOCIAL_LINKS["telegram"]),
         InlineKeyboardButton("📸 Instagram", url=SOCIAL_LINKS["instagram"])],
        [InlineKeyboardButton("▶️ YouTube", url=SOCIAL_LINKS["youtube"])],
    ])
    text1 = (
        "👨‍🏫 *Umarov Muhammadali*\n\n"
        "📚 Biologiya fan ustozi\n"
        "⏳ 8+ yillik tajriba\n"
        "🏆 100% lik milliy sertifikat sohibi\n"
        "🎯 Har bir sertifikat imtihonida 20+ natijalar\n"
        "📊 Oxirgi imtihonda 45+ natija (A+ dan C darajasigacha)\n\n"
        "📲 *Ijtimoiy tarmoqlar:*"
    )
    photos1 = db.get_content("teacher_photo")
    if photos1:
        try:
            await update.message.reply_photo(photo=photos1[0]["file_id"], caption=text1, parse_mode="Markdown", reply_markup=keyboard1)
        except:
            await update.message.reply_text(text1, parse_mode="Markdown", reply_markup=keyboard1)
    else:
        await update.message.reply_text(text1, parse_mode="Markdown", reply_markup=keyboard1)

    # 2-o'qituvchi: Asadulloh
    keyboard2 = InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Telegram", url="https://t.me/Asadulloh_rustamovv"),
         InlineKeyboardButton("📸 Instagram", url="https://instagram.com/Asadulloh_rustamov_")],
    ])
    text2 = (
        "👨‍🏫 *Rustamov Asadulloh*\n\n"
        "📚 Biologiya fan ustozi\n"
        "⏳ 8+ yillik tajriba\n"
        "🏆 100% lik milliy sertifikat sohibi\n"
        "🎯 Har bir sertifikat imtihonida 30+ natijalar\n"
        "📊 Oxirgi imtihonda 70+ natija (A+ dan C darajasigacha)\n\n"
        "📲 *Ijtimoiy tarmoqlar:*"
    )
    photos2 = db.get_content("teacher2_photo")
    if photos2:
        try:
            await update.message.reply_photo(photo=photos2[0]["file_id"], caption=text2, parse_mode="Markdown", reply_markup=keyboard2)
        except:
            await update.message.reply_text(text2, parse_mode="Markdown", reply_markup=keyboard2)
    else:
        await update.message.reply_text(text2, parse_mode="Markdown", reply_markup=keyboard2)

async def admin_boglanish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📩 @biolog_UMM ga yozish", url="https://t.me/biolog_UMM")]
    ])
    await update.message.reply_text(
        "📩 *Admin bilan bog'lanish*\n\n"
        "Savollaringiz yoki muammolaringiz bo'lsa,\n"
        "quyidagi tugma orqali adminga yozing 👇\n\n"
        "_Kerakli savolni yuboring, tez orada javob beramiz!_",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# ========================
# MAVZU KONTENTINI KO'RSATISH
# ========================

async def send_content_item(message, item):
    caption = item.get("caption") or ""
    try:
        if item["content_type"] == "video":
            await message.reply_video(video=item["file_id"], caption=caption)
        elif item["content_type"] == "document":
            await message.reply_document(document=item["file_id"], caption=caption)
        elif item["content_type"] == "photo":
            await message.reply_photo(photo=item["file_id"], caption=caption)
        elif item["content_type"] == "text":
            await message.reply_text(item["file_id"], parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Kontent yuborishda xato: {e}")

async def show_section(update: Update, context: ContextTypes.DEFAULT_TYPE, section_key: str):
    section_name = SECTIONS.get(section_key, section_key)
    user_id = update.effective_user.id
    is_prem = db.is_premium(user_id)
    contents = db.get_content(section_key)

    if not contents:
        await update.message.reply_text(
            f"*{section_name}*\n\n📭 Hozircha kontent qo'shilmagan.\nTez orada qo'shiladi! ⏳",
            parse_mode="Markdown"
        )
        return

    # Bepul va pullik kontentlarni ajratish (is_free ustuniga qarab)
    free_items = [c for c in contents if c.get("is_free", 1) == 1]
    paid_items = [c for c in contents if c.get("is_free", 1) == 0]

    await update.message.reply_text(
        f"*{section_name}* bo'yicha materiallar 👇",
        parse_mode="Markdown"
    )

    # Bepul kontentlar — hammaga ko'rinadi
    for item in free_items:
        await send_content_item(update.message, item)

    # Pullik kontentlar — faqat premiumga
    if paid_items:
        if is_prem:
            await update.message.reply_text("⚡ *Premium materiallar:*", parse_mode="Markdown")
            for item in paid_items:
                await send_content_item(update.message, item)
        else:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("⚡ Premium olish", callback_data="buy_1")],
            ])
            await update.message.reply_text(
                f"🔒 *Bu bo'limda yana {len(paid_items)} ta premium material bor!*\n\n"
                "Barchasini ko'rish uchun *Premium* oling 👇",
                parse_mode="Markdown",
                reply_markup=keyboard
            )

    if not free_items and not paid_items:
        await update.message.reply_text("📭 Hozircha kontent yo'q.")

# ========================
# ADMIN PANEL
# ========================

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Sizda ruxsat yo'q!")
        return
    await update.message.reply_text(
        "🛠 *Admin panel*\n\nNimani qilmoqchisiz?",
        parse_mode="Markdown", reply_markup=admin_keyboard()
    )

async def admin_statistika(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    stats = db.get_stats()
    await update.message.reply_text(
        f"📊 *Statistika*\n\n"
        f"👥 Jami foydalanuvchilar: *{stats['total']}*\n"
        f"📅 Bugun qo'shilganlar: *{stats['today']}*",
        parse_mode="Markdown"
    )

async def dtm30_delete_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    all_tests = db.get_all_tests()
    dtm_tests = [t for t in all_tests if t.get("question_count") == 30]
    if not dtm_tests:
        await update.message.reply_text("📭 DTM 30 testlar yo'q.", reply_markup=admin_keyboard())
        return
    keyboard = []
    for t in dtm_tests:
        video = db.get_test_video(t["code"])
        video_icon = "🎬" if video else "❌"
        keyboard.append([InlineKeyboardButton(
            f"🗑 {t['title']} {video_icon}",
            callback_data=f"del_dtm30_{t['code']}"
        )])
    await update.message.reply_text(
        "🗑 *DTM 30 test o'chirish*\n\nQaysi testni o'chirmoqchisiz?\n_(🎬 = video bor | ❌ = video yo'q)_",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def dtm30_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    context.user_data["action"] = "dtm30_admin_step1"
    await update.message.reply_text(
        "🔥 *DTM 30-talik test qo'shish*\n\n"
        "Bu yerda test PDF va video yechim birga saqlanadi.\n\n"
        "1-qadam: Test uchun noyob kod kiriting:\n_(Masalan: DTM2024V1)_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("◀️ Bekor qilish")]], resize_keyboard=True)
    )

async def kontent_qosh_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    context.user_data["action"] = "add_content_section"
    await update.message.reply_text(
        "➕ *Kontent qo'shish*\n\nQaysi bo'limga qo'shmoqchisiz?",
        parse_mode="Markdown", reply_markup=sections_keyboard()
    )

async def kontent_ochi_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    # Barcha bo'limlardan kontent borlarini topish
    non_empty = []
    for key in SECTIONS:
        try:
            items = db.get_content(key)
            if items:
                non_empty.append((key, SECTIONS[key], len(items)))
        except:
            pass

    if not non_empty:
        await update.message.reply_text(
            "📭 Hech bir bo'limda kontent yo'q.",
            reply_markup=admin_keyboard()
        )
        return

    keyboard = []
    for key, name, count in non_empty:
        keyboard.append([InlineKeyboardButton(
            f"{name} ({count} ta)",
            callback_data=f"del_section_{key}"
        )])

    await update.message.reply_text(
        "🗑 *Kontent o'chirish*\n\nQaysi bo'limdan o'chirmoqchisiz?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_test_qosh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Foydalanish: /test_qosh <kod> <savol_soni> <kalit> <sarlavha>
    Kalit: A,B,C,D,A,B,... (vergul bilan ajratilgan)
    Misol: /test_qosh BIO001 30 A,B,C,D,A,C,B,D,A,B,C,D,A,B,C,D,A,B,C,D,A,B,C,D,A,B,C,D,A,B Biologiya 1-variant
    """
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Ruxsat yo'q!")
        return
    context.user_data["action"] = "add_test_step1"
    await update.message.reply_text(
        "➕ *Test qo'shish*\n\n"
        "1-qadam: Test kodini yozing\n"
        "_(Masalan: BIO001)_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("◀️ Bekor qilish")]], resize_keyboard=True)
    )

async def admin_test_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    tests = db.get_all_tests()
    if not tests:
        await update.message.reply_text("📭 Hozircha test yo'q.")
        return
    text = "📋 *Testlar ro'yxati:*\n\n"
    keyboard = []
    for t in tests:
        text += f"📝 *{t['title']}* | Kod: `{t['code']}` | {t['question_count']} ta savol\n"
        keyboard.append([InlineKeyboardButton(f"🗑 {t['code']} o'chirish", callback_data=f"del_test_{t['code']}")])
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_premium_ber_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanish: /premium_ber <user_id>"""
    if not is_admin(update.effective_user.id):
        return
    args = context.args
    if not args:
        await update.message.reply_text("Foydalanish: /premium_ber <user_id>")
        return
    try:
        uid = int(args[0])
        db.set_premium(uid, True)
        await update.message.reply_text(f"✅ {uid} ga Premium berildi!")
        try:
            await context.bot.send_message(uid, "🎉 *Premium faollashtirildi!*\n\nBarcha materiallar ochiq!", parse_mode="Markdown")
        except:
            pass
    except Exception as e:
        await update.message.reply_text(f"Xato: {e}")

async def admin_balans_ber_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanish: /balans_ber <user_id> <miqdor>"""
    if not is_admin(update.effective_user.id):
        return
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Foydalanish: /balans_ber <user_id> <miqdor>")
        return
    try:
        uid, amount = int(args[0]), int(args[1])
        db.add_balance(uid, amount)
        await update.message.reply_text(f"✅ {uid} ga {amount} so'm qo'shildi!")
        try:
            await context.bot.send_message(uid, f"💰 Balansingizga *{amount} so'm* qo'shildi!", parse_mode="Markdown")
        except:
            pass
    except Exception as e:
        await update.message.reply_text(f"Xato: {e}")

async def admin_video_qosh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Foydalanish: /video_qosh <test_kodi>
    Keyin video yuborasiz
    """
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Ruxsat yo'q!")
        return
    args = context.args
    if not args:
        await update.message.reply_text(
            "Foydalanish: /video_qosh <test_kodi>\n"
            "Misol: /video_qosh BIO001\n\n"
            "Keyin video yuboring."
        )
        return
    code = args[0].upper()
    test = db.get_test(code)
    if not test:
        await update.message.reply_text(f"❌ *{code}* kodli test topilmadi!", parse_mode="Markdown")
        return
    context.user_data["action"] = "admin_add_video"
    context.user_data["video_test_code"] = code
    await update.message.reply_text(
        f"✅ Test: *{test['title']}* (`{code}`)\n\n"
        "Endi video yuboring:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("◀️ Bekor qilish")]], resize_keyboard=True)
    )

async def all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    try:
        with db.connect() as conn:
            conn.row_factory = __import__('sqlite3').Row
            users = [dict(r) for r in conn.execute(
                "SELECT * FROM users ORDER BY created_at DESC"
            ).fetchall()]
    except:
        users = []

    if not users:
        await update.message.reply_text("📭 Foydalanuvchilar yo'q.")
        return

    # Sahifalash - har safar 20 ta
    page = context.user_data.get("users_page", 0)
    start = page * 20
    chunk = users[start:start+20]

    text = f"👥 *Foydalanuvchilar ({len(users)} ta)*\n"
    text += f"_{start+1}-{min(start+len(chunk), len(users))} ko'rsatilmoqda_\n\n"

    for u in chunk:
        name = u.get("full_name") or "Noma'lum"
        phone = u.get("phone") or "—"
        region = u.get("region") or "—"
        grade = u.get("grade") or "—"
        username = f"@{u['username']}" if u.get("username") else "—"
        text += (
            f"👤 *{name}* ({username})\n"
            f"📍 {region} | 🎓 {grade} | 📞 {phone}\n\n"
        )

    # Oldingi/Keyingi tugmalar
    nav_buttons = []
    if start > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Oldingi", callback_data=f"users_page_{page-1}"))
    if start + 20 < len(users):
        nav_buttons.append(InlineKeyboardButton("Keyingi ➡️", callback_data=f"users_page_{page+1}"))

    keyboard = InlineKeyboardMarkup([nav_buttons]) if nav_buttons else None
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def users_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return
    page = int(query.data.replace("users_page_", ""))
    context.user_data["users_page"] = page

    try:
        with db.connect() as conn:
            conn.row_factory = __import__('sqlite3').Row
            users = [dict(r) for r in conn.execute(
                "SELECT * FROM users ORDER BY created_at DESC"
            ).fetchall()]
    except:
        users = []

    start = page * 20
    chunk = users[start:start+20]

    text = f"👥 *Foydalanuvchilar ({len(users)} ta)*\n"
    text += f"_{start+1}-{min(start+len(chunk), len(users))} ko'rsatilmoqda_\n\n"

    for u in chunk:
        name = u.get("full_name") or "Noma'lum"
        phone = u.get("phone") or "—"
        region = u.get("region") or "—"
        grade = u.get("grade") or "—"
        username = f"@{u['username']}" if u.get("username") else "—"
        text += (
            f"👤 *{name}* ({username})\n"
            f"📍 {region} | 🎓 {grade} | 📞 {phone}\n\n"
        )

    nav_buttons = []
    if start > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Oldingi", callback_data=f"users_page_{page-1}"))
    if start + 20 < len(users):
        nav_buttons.append(InlineKeyboardButton("Keyingi ➡️", callback_data=f"users_page_{page+1}"))

    keyboard = InlineKeyboardMarkup([nav_buttons]) if nav_buttons else None
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)

async def test_natijalari(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if is_admin(user_id):
        # Admin barcha natijalarni ko'radi
        results = db.get_test_results()
    elif db.is_teacher(user_id):
        # O'qituvchi faqat o'z testlari natijalarini ko'radi
        tests = db.get_teacher_tests(user_id)
        results = []
        for t in tests:
            results.extend(db.get_test_results(test_code=t["code"]))
    else:
        await update.message.reply_text("❌ Ruxsat yo'q!")
        return

    if not results:
        await update.message.reply_text("📭 Hozircha natijalar yo'q.")
        return

    text = f"📊 *Test natijalari ({len(results)} ta):*\n\n"
    for r in results[:20]:
        emoji = "🥇" if r["percentage"] >= 90 else "🥈" if r["percentage"] >= 70 else "🥉" if r["percentage"] >= 50 else "📚"
        text += (
            f"{emoji} *{r['full_name']}*\n"
            f"📍 {r['region']} | 🎓 {r['grade']} | 📞 {r['phone']}\n"
            f"📝 Test: `{r['test_code']}` | ✅ {r['correct']}/{r['total']} | {r['percentage']}%\n\n"
        )
    if len(results) > 20:
        text += f"_...va yana {len(results)-20} ta natija_"

    await update.message.reply_text(text, parse_mode="Markdown")

# ========================
# MILLIY SERTIFIKAT TEST TEKSHIRISH
# ========================
# Ball tizimi:
# 1-40 savol: jami 100 ball (RASH modeli asosida)
# 41-savol: 30 ball, 42-savol: 35 ball, 43-savol: 10 ball
# Jami max: 175 ball

MS_BALL_41 = 30
MS_BALL_42 = 35
MS_BALL_43 = 10
MS_BALL_1_40 = 100  # jami

def build_ms_answer_keyboard(user_answers: dict):
    """43 ta savol uchun inline klaviatura"""
    keyboard = []
    row = []
    for i in range(1, 44):
        if i <= 32:
            ans = user_answers.get(str(i), "❓")
        elif i <= 40:
            ans = "✏️" if str(i) in user_answers else "❓"
        else:
            ans = "✏️" if str(i) in user_answers else "❓"

        btn = InlineKeyboardButton(f"{i}:{ans}", callback_data=f"ms_{i}")
        row.append(btn)
        if len(row) == 5:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton("✅ Natijani ko'rish", callback_data="ms_check"),
        InlineKeyboardButton("🔄 Tozalash", callback_data="ms_reset")
    ])
    return InlineKeyboardMarkup(keyboard)

def build_ms_abcd_keyboard(q_num: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("A", callback_data=f"msans_{q_num}_A"),
            InlineKeyboardButton("B", callback_data=f"msans_{q_num}_B"),
            InlineKeyboardButton("C", callback_data=f"msans_{q_num}_C"),
            InlineKeyboardButton("D", callback_data=f"msans_{q_num}_D"),
        ],
        [InlineKeyboardButton("◀️ Orqaga", callback_data="ms_back")]
    ])

async def dtm_30_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """DTM 30-talik testlar ro'yxatini ko'rsatish"""
    user_id = update.effective_user.id
    all_tests = db.get_all_tests()
    dtm_tests = [t for t in all_tests if t.get("question_count") == 30]

    if not dtm_tests:
        await update.message.reply_text(
            "🔥 *DTM 30-TALIK TESTLAR*\n\n"
            "📭 Hozircha testlar qo'shilmagan.\n"
            "Tez orada qo'shiladi! ⏳",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        return

    # Foydalanuvchining oxirgi natijalarini ko'rsatish
    try:
        my_results = db.get_user_test_results(user_id, limit=3)
    except:
        my_results = []

    results_text = ""
    if my_results:
        results_text = "\n📊 *Sizning oxirgi natijalaringiz:*\n"
        for r in my_results:
            emoji = "🥇" if r["percentage"] >= 90 else "🥈" if r["percentage"] >= 70 else "🥉" if r["percentage"] >= 50 else "📚"
            results_text += f"{emoji} {r['test_code']}: *{r['correct']}/30* — {r['percentage']}%\n"
        results_text += "\n"

    keyboard = []
    for t in dtm_tests:
        done = my_results and any(r['test_code'] == t['code'] for r in my_results)
        label = f"✅ {t['title']}" if done else f"📝 {t['title']}"
        keyboard.append([InlineKeyboardButton(label, callback_data=f"dtm30_{t['code']}")])

    await update.message.reply_text(
        "🔥 *DTM 30-TALIK TESTLAR*\n\n"
        "Test ishlash uchun tanlang 👇\n"
        f"{results_text}"
        f"📊 Jami: *{len(dtm_tests)} ta test*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def ms_test_tekshirish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["action"] = "ms_student_name"
    await update.message.reply_text(
        "🏅 *Milliy Sertifikat Test Tekshirish*\n\n"
        "Davom etish uchun ma'lumotlaringiz kerak:\n\n"
        "1️⃣ To'liq ismingizni yozing:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("◀️ Orqaga")]], resize_keyboard=True)
    )

async def ms_handle_test_code(update: Update, context: ContextTypes.DEFAULT_TYPE, code: str):
    test = db.get_test(code.upper())
    if not test:
        await update.message.reply_text(
            "❌ *Bunday kodli test topilmadi!*\nKodni tekshirib qayta kiriting.",
            parse_mode="Markdown"
        )
        return
    if test.get("question_count") != 43:
        await update.message.reply_text(
            "❌ *Bu test MS format emas!*\n(MS test 43 savoldan iborat bo'lishi kerak)",
            parse_mode="Markdown"
        )
        return

    context.user_data["ms_test"] = test
    context.user_data["ms_answers"] = {}
    context.user_data["action"] = "ms_answering"

    try:
        await update.message.reply_document(
            document=test["pdf_file_id"],
            caption=f"📄 *{test['title']}*",
            parse_mode="Markdown"
        )
    except:
        pass

    await update.message.reply_text(
        f"🏅 *{test['title']}*\n\n"
        f"📊 Savollar: *43 ta*\n"
        f"• 1-32: A/B/C/D variantlar\n"
        f"• 33-40: Javobni o'zingiz yozasiz\n"
        f"• 41-43: Ochiq savollar (alohida ball)\n\n"
        f"Savol raqamini bosib javob bering 👇\n"
        f"_(❓ = javob berilmagan | ✏️ = yozma javob)_",
        parse_mode="Markdown",
        reply_markup=build_ms_answer_keyboard({})
    )

async def ms_test_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    ms_test = context.user_data.get("ms_test")
    ms_answers = context.user_data.get("ms_answers", {})

    if not ms_test:
        await query.edit_message_text("❌ Test topilmadi. /start bosing.")
        return

    # Savol raqami bosildi
    if data.startswith("ms_") and data[3:].isdigit():
        q_num = int(data[3:])
        context.user_data["ms_current_q"] = q_num
        current = ms_answers.get(str(q_num), "❓")

        if q_num <= 32:
            # A/B/C/D tanlash
            await query.edit_message_text(
                f"*{q_num}-savol* — variant tanlang:\nHozirgi: *{current}*",
                parse_mode="Markdown",
                reply_markup=build_ms_abcd_keyboard(q_num)
            )
        else:
            # Yozma javob
            context.user_data["action"] = "ms_text_answer"
            label = ""
            if q_num <= 40:
                label = "_(33-40 savollar: javobni yozing)_"
            elif q_num == 41:
                label = f"_(41-savol: {MS_BALL_41} ball)_"
            elif q_num == 42:
                label = f"_(42-savol: {MS_BALL_42} ball)_"
            else:
                label = f"_(43-savol: {MS_BALL_43} ball)_"

            await query.edit_message_text(
                f"*{q_num}-savol* — javobingizni yozing:\n{label}\n\nHozirgi: *{current}*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Orqaga", callback_data="ms_back")]])
            )

    # A/B/C/D tanlandi
    elif data.startswith("msans_"):
        parts = data.split("_")
        q_num = parts[1]
        variant = parts[2]
        ms_answers[q_num] = variant
        context.user_data["ms_answers"] = ms_answers
        answered = len(ms_answers)
        await query.edit_message_text(
            f"✅ {q_num}-savol: *{variant}*\n\n"
            f"📊 Javob berildi: *{answered}/43*\n\n"
            f"Qolgan savollarni belgilang 👇",
            parse_mode="Markdown",
            reply_markup=build_ms_answer_keyboard(ms_answers)
        )

    # Orqaga
    elif data == "ms_back":
        context.user_data["action"] = "ms_answering"
        answered = len(ms_answers)
        await query.edit_message_text(
            f"📊 Javob berildi: *{answered}/43*\n\nSavol raqamini bosing 👇",
            parse_mode="Markdown",
            reply_markup=build_ms_answer_keyboard(ms_answers)
        )

    # Tozalash
    elif data == "ms_reset":
        context.user_data["ms_answers"] = {}
        await query.edit_message_text(
            "🔄 Javoblar tozalandi! Qaytadan boshlang 👇",
            parse_mode="Markdown",
            reply_markup=build_ms_answer_keyboard({})
        )

    # Natija
    elif data == "ms_check":
        answered = len(ms_answers)
        if answered < 43:
            await query.answer(
                f"⚠️ Hali {43 - answered} ta savol javobsiz! Barchasiga javob bering.",
                show_alert=True
            )
            return

        correct_answers = ms_test["answers"].upper().split(",")
        
        # 1-40 tekshirish
        correct_1_40 = 0
        wrong_1_40 = []
        for i in range(1, 41):
            user_ans = ms_answers.get(str(i), "").strip().upper()
            correct_ans = correct_answers[i-1].strip() if i <= len(correct_answers) else "?"
            if user_ans == correct_ans:
                correct_1_40 += 1
            else:
                wrong_1_40.append(f"{i}: Siz *{user_ans}* | To'g'ri *{correct_ans}*")

        ball_1_40 = round((correct_1_40 / 40) * MS_BALL_1_40, 2)

        # 41-43 tekshirish
        correct_41 = ms_answers.get("41", "").strip().upper() == correct_answers[40].strip().upper() if len(correct_answers) > 40 else False
        correct_42 = ms_answers.get("42", "").strip().upper() == correct_answers[41].strip().upper() if len(correct_answers) > 41 else False
        correct_43 = ms_answers.get("43", "").strip().upper() == correct_answers[42].strip().upper() if len(correct_answers) > 42 else False

        ball_41 = MS_BALL_41 if correct_41 else 0
        ball_42 = MS_BALL_42 if correct_42 else 0
        ball_43 = MS_BALL_43 if correct_43 else 0
        ball_41_43 = ball_41 + ball_42 + ball_43

        total_ball = ball_1_40 + ball_41_43
        max_ball = MS_BALL_1_40 + MS_BALL_41 + MS_BALL_42 + MS_BALL_43  # 175

        # Rash modeli asosida rasmiy ball chegaralari
        # 1-40 + 41-43 umumiy ball 175 ga normallashtiriladi
        normalized = round((total_ball / 175) * 100, 2)

        if normalized >= 70:
            daraja = "🥇 A+"
        elif normalized >= 65:
            daraja = "🥈 A"
        elif normalized >= 60:
            daraja = "🥉 B+"
        elif normalized >= 55:
            daraja = "📘 B"
        elif normalized >= 50:
            daraja = "📗 C+"
        elif normalized >= 46:
            daraja = "📙 C"
        else:
            daraja = "📚 Sertifikat yo'q"

        result_text = (
            f"🏅 *Milliy Sertifikat Natija*\n"
            f"📝 *{ms_test['title']}*\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📊 *1-40 savol:*\n"
            f"✅ To'g'ri: *{correct_1_40}/40*\n"
            f"❌ Noto'g'ri: *{40-correct_1_40}/40*\n"
            f"🏆 Ball: *{ball_1_40}/100*\n\n"
            f"📊 *41-43 savollar:*\n"
            f"41-savol: {'✅' if correct_41 else '❌'} *{ball_41}/{MS_BALL_41}* ball\n"
            f"42-savol: {'✅' if correct_42 else '❌'} *{ball_42}/{MS_BALL_42}* ball\n"
            f"43-savol: {'✅' if correct_43 else '❌'} *{ball_43}/{MS_BALL_43}* ball\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🎯 *Jami: {total_ball:.1f}/{max_ball} ball*\n"
            f"📐 *O'rtacha: {round((ball_1_40/100 + ball_41_43/(MS_BALL_41+MS_BALL_42+MS_BALL_43))/2*100, 1)}%*\n"
            f"🏅 *Daraja: {emoji}*\n"
        )

        if wrong_1_40:
            result_text += f"\n❌ *Noto'g'ri javoblar (1-40):*\n"
            result_text += "\n".join(wrong_1_40[:10])
            if len(wrong_1_40) > 10:
                result_text += f"\n_...va yana {len(wrong_1_40)-10} ta_"

        # Saqlash
        try:
            db.save_test_result(
                user_id=query.from_user.id,
                full_name=context.user_data.get("s_name", "Noma'lum"),
                region=context.user_data.get("s_region", "—"),
                phone=context.user_data.get("s_phone", "—"),
                grade=context.user_data.get("s_grade", "—"),
                test_code=ms_test["code"],
                correct=correct_1_40,
                wrong=40-correct_1_40,
                total=43,
                percentage=round((total_ball/max_ball)*100, 1),
                ball=total_ball
            )
        except Exception as e:
            logger.error(f"MS natija saqlashda xato: {e}")

        context.user_data.clear()
        await query.edit_message_text(result_text, parse_mode="Markdown")

async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    context.user_data["action"] = "broadcast"
    await update.message.reply_text(
        "📢 *Hammaga xabar*\n\n"
        "Yubormoqchi bo'lgan xabaringizni yozing:\n"
        "_(Matn, rasm, video yoki fayl bo'lishi mumkin)_",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("◀️ Bekor qilish")]], resize_keyboard=True)
    )

async def adminlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    admins = db.get_admins()
    text = "👥 *Adminlar ro'yxati:*\n\n"
    for a in admins:
        text += f"• {a['full_name']} | `{a['user_id']}`\n"
    if not admins:
        text += "_Hozircha qo'shimcha admin yo'q_\n"
    text += "\n➕ Admin qo'shish: `/admin_qosh <user_id>`\n"
    text += "➖ Admin o'chirish: `/admin_ochi <user_id>`"
    await update.message.reply_text(text, parse_mode="Markdown")

async def admin_qosh_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in SUPER_ADMINS:
        await update.message.reply_text("❌ Faqat asosiy admin qo'sha oladi!")
        return
    args = context.args
    if not args:
        await update.message.reply_text("Foydalanish: /admin_qosh <user_id>")
        return
    try:
        uid = int(args[0])
        db.add_admin(uid, f"Admin {uid}")
        await update.message.reply_text(f"✅ {uid} admin qilindi!")
        try:
            await context.bot.send_message(uid, "🎉 Siz admin qildingiz! /admin buyrug'i bilan kirish mumkin.")
        except:
            pass
    except Exception as e:
        await update.message.reply_text(f"Xato: {e}")

async def admin_ochi_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in SUPER_ADMINS:
        await update.message.reply_text("❌ Faqat asosiy admin o'chira oladi!")
        return
    args = context.args
    if not args:
        await update.message.reply_text("Foydalanish: /admin_ochi <user_id>")
        return
    try:
        uid = int(args[0])
        db.remove_admin(uid)
        await update.message.reply_text(f"✅ {uid} adminlikdan olindi!")
    except Exception as e:
        await update.message.reply_text(f"Xato: {e}")

# ========================
# UNIVERSAL HANDLER
# ========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text if update.message.text else ""
    action = context.user_data.get("action")

    # ── O'QUVCHI MA'LUMOTLARI ──
    if action == "student_reg_name":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Bosh menyu 👇", reply_markup=main_menu_keyboard())
            return
        context.user_data["s_name"] = text
        context.user_data["action"] = "student_reg_region"
        await update.message.reply_text(
            f"✅ Ism: *{text}*\n\n"
            "2️⃣ Qayerdan ekansiz? (Viloyat/Shahar/Tuman):\n"
            "_(Masalan: Toshkent sh., Samarqand v., Andijon)_",
            parse_mode="Markdown"
        )
        return

    if action == "student_reg_region":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Bosh menyu 👇", reply_markup=main_menu_keyboard())
            return
        context.user_data["s_region"] = text
        context.user_data["action"] = "student_reg_phone"
        await update.message.reply_text(
            f"✅ Joylashuv: *{text}*\n\n"
            "3️⃣ Telefon raqamingiz:\n"
            "_(Masalan: +998901234567)_",
            parse_mode="Markdown"
        )
        return

    if action == "student_reg_phone":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Bosh menyu 👇", reply_markup=main_menu_keyboard())
            return
        context.user_data["s_phone"] = text
        context.user_data["action"] = "student_reg_grade"
        await update.message.reply_text(
            f"✅ Telefon: *{text}*\n\n"
            "4️⃣ Sinfingiz yoki guruhingiz:\n"
            "_(Masalan: 11-A, 10-B, Abituriyent)_",
            parse_mode="Markdown"
        )
        return

    if action == "student_reg_grade":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Bosh menyu 👇", reply_markup=main_menu_keyboard())
            return
        context.user_data["s_grade"] = text
        context.user_data["action"] = "waiting_test_code"
        name = context.user_data.get("s_name")
        region = context.user_data.get("s_region")
        phone = context.user_data.get("s_phone")
        await update.message.reply_text(
            f"✅ *Ma'lumotlar saqlandi!*\n\n"
            f"👤 Ism: *{name}*\n"
            f"📍 Joylashuv: *{region}*\n"
            f"📞 Telefon: *{phone}*\n"
            f"🎓 Sinf: *{text}*\n\n"
            f"Endi test kodini kiriting:\n_(Masalan: BIO001)_",
            parse_mode="Markdown"
        )
        return

    # ── TEST KODI KUTISH ──
    if action == "waiting_test_code":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Bosh menyu 👇", reply_markup=main_menu_keyboard())
            return
        await handle_test_code(update, context, text)
        return

    # ── DTM 30 O'QUVCHI MA'LUMOTLARI ──
    if action == "dtm30_student_name":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Bosh menyu 👇", reply_markup=main_menu_keyboard())
            return
        context.user_data["s_name"] = text
        context.user_data["action"] = "dtm30_student_region"
        await update.message.reply_text(
            f"✅ Ism: *{text}*\n\n2️⃣ Qayerdan ekansiz?",
            parse_mode="Markdown"
        )
        return

    if action == "dtm30_student_region":
        context.user_data["s_region"] = text
        context.user_data["action"] = "dtm30_student_phone"
        await update.message.reply_text(
            f"✅ Joylashuv: *{text}*\n\n3️⃣ Telefon raqamingiz:",
            parse_mode="Markdown"
        )
        return

    if action == "dtm30_student_phone":
        context.user_data["s_phone"] = text
        context.user_data["action"] = "dtm30_student_grade"
        await update.message.reply_text(
            f"✅ Telefon: *{text}*\n\n4️⃣ Sinfingiz:",
            parse_mode="Markdown"
        )
        return

    if action == "dtm30_student_grade":
        context.user_data["s_grade"] = text
        context.user_data["action"] = "dtm30_answering"
        code = context.user_data.get("selected_test_code")
        test = db.get_test(code)
        context.user_data["current_test"] = test
        context.user_data["user_answers"] = {}

        # PDF yuborish
        if test.get("pdf_file_id"):
            try:
                await update.message.reply_document(
                    document=test["pdf_file_id"],
                    caption=f"📋 *{test['title']}* — Test savollari",
                    parse_mode="Markdown"
                )
            except:
                pass

        # Tugmalar chiqarish - build_answer_keyboard ishlatiladi
        await update.message.reply_text(
            f"🔥 *{test['title']}*\n\n"
            f"📊 30 ta savol — har birini bosib A/B/C/D belgilang 👇\n"
            f"Barchasini belgilab bo'lsangiz natija avtomatik chiqadi!",
            parse_mode="Markdown",
            reply_markup=build_answer_keyboard({}, 30)
        )
        return

    # ── PROFIL TO'LDIRISH ──
    if action == "profile_name":
        if text == "⏭ O'tkazib yuborish":
            context.user_data.clear()
            await update.message.reply_text(
                "Yaxshi!",
                reply_markup=main_menu_keyboard()
            )
            return
        context.user_data["p_name"] = text
        context.user_data["action"] = "profile_region"
        await update.message.reply_text(
            f"✅ Ism: *{text}*\n\n"
            "2️⃣ Qayerdan ekansiz? (Viloyat/Tuman):\n"
            "_(Masalan: Toshkent sh., Farg'ona v.)_",
            parse_mode="Markdown"
        )
        return

    if action == "profile_region":
        if text == "⏭ O'tkazib yuborish":
            context.user_data.clear()
            await update.message.reply_text("Yaxshi!", reply_markup=main_menu_keyboard())
            return
        context.user_data["p_region"] = text
        context.user_data["action"] = "profile_phone"
        await update.message.reply_text(
            f"✅ Joylashuv: *{text}*\n\n"
            "3️⃣ Telefon raqamingizni yuboring:\n"
            "_(Tugmani bosing — bu sizning haqiqiy raqamingizni tasdiqlaydi)_",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([
                [KeyboardButton("📱 Telefon raqamimni yuborish", request_contact=True)],
                [KeyboardButton("⏭ O'tkazib yuborish")]
            ], resize_keyboard=True)
        )
        return

    if action == "profile_phone":
        if text == "⏭ O'tkazib yuborish":
            context.user_data.clear()
            await update.message.reply_text("Yaxshi!", reply_markup=main_menu_keyboard())
            return
        # Telefon tugma orqali yuborildi
        if update.message.contact:
            phone = update.message.contact.phone_number
            if not phone.startswith("+"):
                phone = "+" + phone
            context.user_data["p_phone"] = phone
            context.user_data["action"] = "profile_grade"
            await update.message.reply_text(
                f"✅ Telefon: *{phone}*\n\n"
                "4️⃣ Sinfingiz yoki guruhingiz:\n"
                "_(Masalan: 11-A, 10-B, Abituriyent)_",
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup(
                    [[KeyboardButton("⏭ O'tkazib yuborish")]],
                    resize_keyboard=True
                )
            )
        else:
            # Tugma bosilmay matn yozilgan — rad etish
            await update.message.reply_text(
                "❌ Iltimos, quyidagi *📱 Telefon raqamimni yuborish* tugmasini bosing!\n\n"
                "_(Bu sizning haqiqiy raqamingizni tasdiqlovchi yagona usul)_",
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup([
                    [KeyboardButton("📱 Telefon raqamimni yuborish", request_contact=True)],
                    [KeyboardButton("⏭ O'tkazib yuborish")]
                ], resize_keyboard=True)
            )
        return

    if action == "profile_grade":
        if text == "⏭ O'tkazib yuborish":
            context.user_data.clear()
            await update.message.reply_text("Yaxshi!", reply_markup=main_menu_keyboard())
            return
        user_id = update.effective_user.id
        name = context.user_data.get("p_name", update.effective_user.full_name)
        region = context.user_data.get("p_region", "—")
        phone = context.user_data.get("p_phone", "—")
        db.update_profile(user_id, name, region, phone, text)
        context.user_data.clear()
        await update.message.reply_text(
            "✅ *Ma'lumotlaringiz saqlandi!*\n\n"
            f"👤 Ism: *{name}*\n"
            f"📍 Joy: *{region}*\n"
            f"📞 Tel: *{phone}*\n"
            f"🎓 Sinf: *{text}*\n\n"
            "Endi barcha funksiyalardan foydalanishingiz mumkin! 👇",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        return

    # ── MS TEST O'QUVCHI MA'LUMOTLARI ──
    if action == "ms_student_name":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Bosh menyu 👇", reply_markup=main_menu_keyboard())
            return
        context.user_data["s_name"] = text
        context.user_data["action"] = "ms_student_region"
        await update.message.reply_text(
            f"✅ Ism: *{text}*\n\n2️⃣ Qayerdan ekansiz? (Viloyat/Tuman):",
            parse_mode="Markdown"
        )
        return

    if action == "ms_student_region":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Bosh menyu 👇", reply_markup=main_menu_keyboard())
            return
        context.user_data["s_region"] = text
        context.user_data["action"] = "ms_student_phone"
        await update.message.reply_text(
            f"✅ Joylashuv: *{text}*\n\n3️⃣ Telefon raqamingiz:",
            parse_mode="Markdown"
        )
        return

    if action == "ms_student_phone":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Bosh menyu 👇", reply_markup=main_menu_keyboard())
            return
        context.user_data["s_phone"] = text
        context.user_data["action"] = "ms_student_grade"
        await update.message.reply_text(
            f"✅ Telefon: *{text}*\n\n4️⃣ Sinfingiz yoki guruhingiz:",
            parse_mode="Markdown"
        )
        return

    if action == "ms_student_grade":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Bosh menyu 👇", reply_markup=main_menu_keyboard())
            return
        context.user_data["s_grade"] = text
        context.user_data["action"] = "ms_waiting_code"
        await update.message.reply_text(
            f"✅ *Ma'lumotlar saqlandi!*\n\n"
            f"👤 *{context.user_data.get('s_name')}*\n"
            f"📍 {context.user_data.get('s_region')} | 🎓 {text}\n\n"
            f"Endi MS test kodini kiriting:",
            parse_mode="Markdown"
        )
        return

    if action == "ms_waiting_code":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Bosh menyu 👇", reply_markup=main_menu_keyboard())
            return
        await ms_handle_test_code(update, context, text)
        return

    if action == "ms_text_answer":
        if text == "◀️ Orqaga":
            context.user_data["action"] = "ms_answering"
            ms_answers = context.user_data.get("ms_answers", {})
            await update.message.reply_text(
                "Savol raqamini bosing 👇",
                reply_markup=build_ms_answer_keyboard(ms_answers)
            )
            return
        q_num = str(context.user_data.get("ms_current_q", ""))
        if q_num:
            ms_answers = context.user_data.get("ms_answers", {})
            ms_answers[q_num] = text.strip()
            context.user_data["ms_answers"] = ms_answers
            context.user_data["action"] = "ms_answering"
            await update.message.reply_text(
                f"✅ {q_num}-savol: *{text.strip()}*\n\nDavom eting 👇",
                parse_mode="Markdown",
                reply_markup=build_ms_answer_keyboard(ms_answers)
            )
        return

    # ── O'QITUVCHI MS TEST YARATISH ──
    if action == "teacher_ms_step1":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Panel 👇", reply_markup=teacher_menu_keyboard())
            return
        existing = db.get_test(text.upper())
        if existing:
            await update.message.reply_text(f"❌ *{text.upper()}* kodi band! Boshqa kod tanlang.", parse_mode="Markdown")
            return
        context.user_data["ms_t_code"] = text.upper()
        context.user_data["action"] = "teacher_ms_step2"
        await update.message.reply_text(
            f"✅ Kod: *{text.upper()}*\n\n2-qadam: Test sarlavhasini yozing:\n_(Masalan: Biologiya MS 1-variant)_",
            parse_mode="Markdown"
        )
        return

    if action == "teacher_ms_step2":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Panel 👇", reply_markup=teacher_menu_keyboard())
            return
        context.user_data["ms_t_title"] = text
        context.user_data["action"] = "teacher_ms_step3"
        await update.message.reply_text(
            f"✅ Sarlavha: *{text}*\n\n"
            "3-qadam: 1-32 savollar kalitini yozing\n"
            "_(32 ta, vergul bilan: A,B,C,D,A,B,C,D,...)_",
            parse_mode="Markdown"
        )
        return

    if action == "teacher_ms_step3":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Panel 👇", reply_markup=teacher_menu_keyboard())
            return
        ans_list = [a.strip() for a in text.split(",")]
        if len(ans_list) != 32:
            await update.message.reply_text(
                f"❌ *{len(ans_list)} ta kalit* kiritdingiz, *32 ta* kerak!\nQayta kiriting.",
                parse_mode="Markdown"
            )
            return
        context.user_data["ms_t_ans_1_32"] = text
        context.user_data["action"] = "teacher_ms_step4"
        await update.message.reply_text(
            f"✅ 1-32 kalit saqlandi!\n\n"
            "4-qadam: 33-43 savollar kalitini yozing\n"
            "_(11 ta, vergul bilan: javob1,javob2,...)_",
            parse_mode="Markdown"
        )
        return

    if action == "teacher_ms_step4":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Panel 👇", reply_markup=teacher_menu_keyboard())
            return
        ans_list = [a.strip() for a in text.split(",")]
        if len(ans_list) != 11:
            await update.message.reply_text(
                f"❌ *{len(ans_list)} ta kalit* kiritdingiz, *11 ta* kerak!\nQayta kiriting.",
                parse_mode="Markdown"
            )
            return
        # 1-32 va 33-43 kalitlarini birlashtirish
        ans_1_32 = context.user_data.get("ms_t_ans_1_32")
        full_answers = ans_1_32 + "," + text
        context.user_data["ms_t_answers"] = full_answers
        context.user_data["action"] = "teacher_ms_step5"
        await update.message.reply_text(
            f"✅ 33-43 kalit saqlandi!\n\n"
            "5-qadam: Test PDF faylini yuboring\n"
            "_(Fayl bo'lmasa 'yo'q' deb yozing)_",
            parse_mode="Markdown"
        )
        return

    if action == "teacher_ms_step5":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Panel 👇", reply_markup=teacher_menu_keyboard())
            return
        msg = update.message
        pdf_id = None
        if msg.document:
            pdf_id = msg.document.file_id
        elif text and text.lower() in ["yo'q", "yoq"]:
            pdf_id = None
        else:
            await update.message.reply_text("❌ PDF fayl yuboring yoki 'yo'q' deb yozing.")
            return

        user_id = update.effective_user.id
        code = context.user_data.get("ms_t_code")
        title = context.user_data.get("ms_t_title")
        answers = context.user_data.get("ms_t_answers")

        db.add_teacher_test(code, title, pdf_id, answers, 43, user_id)
        context.user_data.clear()
        await update.message.reply_text(
            f"✅ *MS Test yaratildi!*\n\n"
            f"📝 Sarlavha: *{title}*\n"
            f"🔑 Kod: `{code}`\n"
            f"📊 Savollar: *43 ta* (32 test + 11 yozma)\n\n"
            f"O'quvchilar 🏅 MS Test tekshirish → *{code}* kodini kiritib ishlaydi!",
            parse_mode="Markdown",
            reply_markup=teacher_menu_keyboard()
        )
        return

    # ── O'QITUVCHI RO'YXATDAN O'TISH ──
    if action == "teacher_reg_name":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Bosh menyu 👇", reply_markup=main_menu_keyboard())
            return
        context.user_data["t_name"] = text
        context.user_data["action"] = "teacher_reg_subject"
        await update.message.reply_text(
            f"✅ Ism: *{text}*\n\n2-qadam: O'qitadigan faningizni yozing:\n_(Masalan: Fizika, Kimyo, Matematika)_",
            parse_mode="Markdown"
        )
        return

    if action == "teacher_reg_subject":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Bosh menyu 👇", reply_markup=main_menu_keyboard())
            return
        user = update.effective_user
        name = context.user_data.get("t_name")
        db.add_teacher(user.id, name, text, user.username or "")
        context.user_data.clear()
        await update.message.reply_text(
            f"🎉 *Ro'yxatdan o'tdingiz!*\n\n"
            f"👨‍🏫 Ism: *{name}*\n"
            f"📚 Fan: *{text}*\n\n"
            f"Endi test yaratishingiz mumkin!",
            parse_mode="Markdown",
            reply_markup=teacher_menu_keyboard()
        )
        return

    # ── O'QITUVCHI TEST YARATISH ──
    if action == "teacher_test_step1":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Panel 👇", reply_markup=teacher_menu_keyboard())
            return
        existing = db.get_test(text.upper())
        if existing:
            await update.message.reply_text(f"❌ *{text.upper()}* kodi band! Boshqa kod tanlang.", parse_mode="Markdown")
            return
        context.user_data["t_code"] = text.upper()
        context.user_data["action"] = "teacher_test_step2"
        await update.message.reply_text(
            f"✅ Kod: *{text.upper()}*\n\n2-qadam: Test sarlavhasini yozing:",
            parse_mode="Markdown"
        )
        return

    if action == "teacher_test_step2":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Panel 👇", reply_markup=teacher_menu_keyboard())
            return
        context.user_data["t_title"] = text
        context.user_data["action"] = "teacher_test_step3"
        await update.message.reply_text(
            f"✅ Sarlavha: *{text}*\n\n3-qadam: Savollar sonini yozing:\n_(Masalan: 30)_",
            parse_mode="Markdown"
        )
        return

    if action == "teacher_test_step3":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Panel 👇", reply_markup=teacher_menu_keyboard())
            return
        try:
            count = int(text)
            context.user_data["t_count"] = count
            context.user_data["action"] = "teacher_test_step4"
            await update.message.reply_text(
                f"✅ Savollar soni: *{count}*\n\n4-qadam: Kalit javoblarni yozing\n"
                f"_(Vergul bilan: A,B,C,D,A,B... — jami {count} ta)_",
                parse_mode="Markdown"
            )
        except:
            await update.message.reply_text("❌ Faqat raqam kiriting!")
        return

    if action == "teacher_test_step4":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Panel 👇", reply_markup=teacher_menu_keyboard())
            return
        count = context.user_data.get("t_count", 30)
        ans_list = [a.strip() for a in text.split(",")]
        if len(ans_list) != count:
            await update.message.reply_text(
                f"❌ *{len(ans_list)} ta kalit kiritdingiz, {count} ta kerak!*\nQayta kiriting.",
                parse_mode="Markdown"
            )
            return
        context.user_data["t_answers"] = text
        context.user_data["action"] = "teacher_test_step5"
        await update.message.reply_text(
            f"✅ Kalit saqlandi!\n\n5-qadam: Test PDF faylini yuboring\n_(Fayl bo'lmasa 'yo'q' deb yozing)_",
            parse_mode="Markdown"
        )
        return

    if action == "teacher_test_step5":
        if text == "◀️ Orqaga":
            context.user_data.clear()
            await update.message.reply_text("Panel 👇", reply_markup=teacher_menu_keyboard())
            return
        msg = update.message
        pdf_id = None
        if msg.document:
            pdf_id = msg.document.file_id
        elif text and text.lower() in ["yo'q", "yoq"]:
            pdf_id = None
        else:
            await update.message.reply_text("❌ PDF fayl yuboring yoki 'yo'q' deb yozing.")
            return

        user_id = update.effective_user.id
        code = context.user_data.get("t_code")
        title = context.user_data.get("t_title")
        count = context.user_data.get("t_count", 30)
        answers = context.user_data.get("t_answers")

        db.add_teacher_test(code, title, pdf_id, answers, count, user_id)
        context.user_data.clear()
        await update.message.reply_text(
            f"✅ *Test yaratildi!*\n\n"
            f"📝 Sarlavha: *{title}*\n"
            f"🔑 Kod: `{code}`\n"
            f"📊 Savollar: *{count} ta*\n\n"
            f"O'quvchilar ✅ Test tekshirish → *{code}* kodini kiritib test ishlaydi!",
            parse_mode="Markdown",
            reply_markup=teacher_menu_keyboard()
        )
        return

    # ── TEST QO'SHISH JARAYONI ──
    if action == "add_test_step1":
        if text == "◀️ Bekor qilish":
            context.user_data.clear()
            await update.message.reply_text("Bekor qilindi.", reply_markup=admin_keyboard())
            return
        context.user_data["new_test_code"] = text.upper()
        context.user_data["action"] = "add_test_step2"
        await update.message.reply_text(
            f"✅ Kod: *{text.upper()}*\n\n2-qadam: Test sarlavhasini yozing\n_(Masalan: Biologiya 1-variant)_",
            parse_mode="Markdown"
        )
        return

    if action == "add_test_step2":
        if text == "◀️ Bekor qilish":
            context.user_data.clear()
            await update.message.reply_text("Bekor qilindi.", reply_markup=admin_keyboard())
            return
        context.user_data["new_test_title"] = text
        context.user_data["action"] = "add_test_step3"
        await update.message.reply_text(
            f"✅ Sarlavha: *{text}*\n\n3-qadam: Savollar sonini yozing\n_(Masalan: 30)_",
            parse_mode="Markdown"
        )
        return

    if action == "add_test_step3":
        if text == "◀️ Bekor qilish":
            context.user_data.clear()
            await update.message.reply_text("Bekor qilindi.", reply_markup=admin_keyboard())
            return
        try:
            count = int(text)
            context.user_data["new_test_count"] = count
            context.user_data["action"] = "add_test_step4"
            await update.message.reply_text(
                f"✅ Savollar soni: *{count}*\n\n4-qadam: Kalit javoblarni yozing\n"
                f"_(Vergul bilan ajrating, masalan: A,B,C,D,A,B,C,D,A,B,C,D,A,B,C,D,A,B,C,D,A,B,C,D,A,B,C,D,A,B)_",
                parse_mode="Markdown"
            )
        except:
            await update.message.reply_text("❌ Faqat raqam kiriting!")
        return

    if action == "add_test_step4":
        if text == "◀️ Bekor qilish":
            context.user_data.clear()
            await update.message.reply_text("Bekor qilindi.", reply_markup=admin_keyboard())
            return
        answers = text.strip()
        count = context.user_data.get("new_test_count", 30)
        ans_list = [a.strip() for a in answers.split(",")]
        if len(ans_list) != count:
            await update.message.reply_text(
                f"❌ *{len(ans_list)} ta kalit kiritdingiz, {count} ta kerak!*\n\nQayta kiriting.",
                parse_mode="Markdown"
            )
            return
        context.user_data["new_test_answers"] = answers
        context.user_data["action"] = "add_test_step5"
        await update.message.reply_text(
            f"✅ Kalit saqlandi!\n\n5-qadam: Test PDF faylini yuboring\n_(Fayl bo'lmasa 'yo'q' deb yozing)_",
            parse_mode="Markdown"
        )
        return

    if action == "add_test_step5":
        if text == "◀️ Bekor qilish":
            context.user_data.clear()
            await update.message.reply_text("Bekor qilindi.", reply_markup=admin_keyboard())
            return
        msg = update.message
        pdf_id = None
        if msg.document:
            pdf_id = msg.document.file_id
        elif text and text.lower() == "yo'q":
            pdf_id = None
        else:
            await update.message.reply_text("❌ PDF fayl yuboring yoki 'yo'q' deb yozing.")
            return

        code = context.user_data.get("new_test_code")
        title = context.user_data.get("new_test_title")
        count = context.user_data.get("new_test_count", 30)
        answers = context.user_data.get("new_test_answers")

        db.add_test(code, title, pdf_id, answers, count, update.effective_user.id)
        context.user_data.clear()
        await update.message.reply_text(
            f"✅ *Test qo'shildi!*\n\n"
            f"📝 Sarlavha: *{title}*\n"
            f"🔑 Kod: `{code}`\n"
            f"📊 Savollar: *{count} ta*\n\n"
            f"O'quvchilar bu kodni botga kiritib test ishlaydi!",
            parse_mode="Markdown",
            reply_markup=admin_keyboard()
        )
        return

    # ── ADMIN VIDEO QO'SHISH ──
    if action == "admin_add_video":
        if text == "◀️ Bekor qilish":
            context.user_data.clear()
            await update.message.reply_text("Bekor qilindi.", reply_markup=admin_keyboard())
            return
        msg = update.message
        if msg.video:
            code = context.user_data.get("video_test_code")
            cap = msg.caption or f"{code} test tahlili"
            db.add_test_video(code, msg.video.file_id, cap, update.effective_user.id)
            context.user_data.clear()
            await update.message.reply_text(
                f"✅ *Video qo'shildi!*\n\nTest: `{code}`\n"
                "Endi test yakunlagandan so'ng o'quvchilarga '🎬 Video tahlilini ko'rish' tugmasi chiqadi!",
                parse_mode="Markdown",
                reply_markup=admin_keyboard()
            )
        else:
            await update.message.reply_text("❌ Faqat video yuboring!")
        return

    # ── BROADCAST ──
    if action == "broadcast":
        if text == "◀️ Bekor qilish":
            context.user_data.clear()
            await update.message.reply_text("Bekor qilindi.", reply_markup=admin_keyboard())
            return
        users = db.get_all_users()
        sent, failed = 0, 0
        for u in users:
            try:
                if update.message.video:
                    await context.bot.send_video(u["user_id"], update.message.video.file_id, caption=update.message.caption or "")
                elif update.message.document:
                    await context.bot.send_document(u["user_id"], update.message.document.file_id, caption=update.message.caption or "")
                elif update.message.photo:
                    await context.bot.send_photo(u["user_id"], update.message.photo[-1].file_id, caption=update.message.caption or "")
                else:
                    await context.bot.send_message(u["user_id"], text)
                sent += 1
            except:
                failed += 1
        context.user_data.clear()
        await update.message.reply_text(f"✅ Yuborildi: {sent}\n❌ Xato: {failed}", reply_markup=admin_keyboard())
        return

    # ── KONTENT QO'SHISH: bo'lim tanlash ──
    # ── DTM 30 TEST QO'SHISH (admin) ──
    if action == "dtm30_admin_step1":
        # Kod
        if text == "◀️ Bekor qilish":
            context.user_data.clear()
            await update.message.reply_text("Bekor qilindi.", reply_markup=admin_keyboard())
            return
        existing = db.get_test(text.upper())
        if existing:
            await update.message.reply_text(f"❌ *{text.upper()}* kodi band!", parse_mode="Markdown")
            return
        context.user_data["dtm30_code"] = text.upper()
        context.user_data["action"] = "dtm30_admin_step2"
        await update.message.reply_text(
            f"✅ Kod: *{text.upper()}*\n\n"
            "2-qadam: Test sarlavhasini yozing:\n"
            "_(Masalan: DTM 2024 - 1-variant)_",
            parse_mode="Markdown"
        )
        return

    if action == "dtm30_admin_step2":
        # Sarlavha
        if text == "◀️ Bekor qilish":
            context.user_data.clear()
            await update.message.reply_text("Bekor qilindi.", reply_markup=admin_keyboard())
            return
        context.user_data["dtm30_title"] = text
        context.user_data["action"] = "dtm30_admin_step3"
        await update.message.reply_text(
            f"✅ Sarlavha: *{text}*\n\n"
            "3-qadam: Test savollar PDF faylini yuboring\n"
            "_(Bu savolar fayli — o'quvchi test ishlash uchun oladi)_",
            parse_mode="Markdown"
        )
        return

    if action == "dtm30_admin_step3":
        # PDF yuklash
        msg = update.message
        if text and text == "◀️ Bekor qilish":
            context.user_data.clear()
            await update.message.reply_text("Bekor qilindi.", reply_markup=admin_keyboard())
            return
        if not msg.document:
            await update.message.reply_text(
                "📄 Test savollari PDF faylini yuboring:",
                parse_mode="Markdown"
            )
            return
        context.user_data["dtm30_pdf"] = msg.document.file_id
        context.user_data["action"] = "dtm30_admin_step4"
        await update.message.reply_text(
            "✅ *PDF yuklandi!*\n\n"
            "Endi kalit javoblarini yuboring.\n\n"
            "📌 *Namuna (30 ta, vergul bilan):*\n"
            "`A,B,C,D,A,B,C,D,A,B,C,D,A,B,C,D,A,B,C,D,A,B,C,D,A,B,C,D,A,B`",
            parse_mode="Markdown"
        )
        return

    if action == "dtm30_admin_step4":
        # Kalit javoblar
        if text == "◀️ Bekor qilish":
            context.user_data.clear()
            await update.message.reply_text("Bekor qilindi.", reply_markup=admin_keyboard())
            return
        if not text:
            return
        ans_list = [a.strip() for a in text.split(",")]
        if len(ans_list) != 30:
            await update.message.reply_text(
                f"❌ *{len(ans_list)} ta kalit* kiritdingiz, *30 ta* kerak!\n\n"
                "📌 *Namuna:*\n"
                "`A,B,C,D,A,B,C,D,A,B,C,D,A,B,C,D,A,B,C,D,A,B,C,D,A,B,C,D,A,B`\n\n"
                "Qayta yuboring:",
                parse_mode="Markdown"
            )
            return
        context.user_data["dtm30_answers"] = text
        context.user_data["action"] = "dtm30_admin_step5"
        await update.message.reply_text(
            "✅ *Kalit saqlandi!*\n\n"
            "Endi video tahlilni yuboring:\n"
            "_(O'quvchi test natijasini ko'rgandan so'ng bu video avtomatik yuboriladi)_",
            parse_mode="Markdown"
        )
        return

    if action == "dtm30_admin_step5":
        # Video tahlil
        msg = update.message
        if text and text == "◀️ Bekor qilish":
            context.user_data.clear()
            await update.message.reply_text("Bekor qilindi.", reply_markup=admin_keyboard())
            return
        if not msg.video:
            await update.message.reply_text(
                "🎬 Video tahlil faylini yuboring:",
                parse_mode="Markdown"
            )
            return

        user_id = update.effective_user.id
        code = context.user_data.get("dtm30_code")
        title = context.user_data.get("dtm30_title")
        answers = context.user_data.get("dtm30_answers")
        pdf_id = context.user_data.get("dtm30_pdf")
        video_id = msg.video.file_id

        db.add_teacher_test(code, title, pdf_id, answers, 30, user_id)
        db.add_test_video(code, video_id, f"{title} — Video tahlil", user_id)

        context.user_data.clear()
        await update.message.reply_text(
            f"🎉 *Variant muvaffaqiyatli yuklandi!*\n\n"
            f"📋 *{title}*\n"
            f"📄 PDF fayli: ✅\n"
            f"🔑 Kaliti: ✅\n"
            f"🎬 Video tahlili: ✅\n\n"
            f"Endi bu variantni foydalanuvchilarga tadbiq etishingiz mumkin!\n"
            f"U 🔥 *DTM 30 Testlar* bo'limida ko'rinadi.",
            parse_mode="Markdown",
            reply_markup=admin_keyboard()
        )
        return

    if action == "add_content_section":
        if text == "◀️ Bekor qilish":
            context.user_data.clear()
            await update.message.reply_text("Bekor qilindi.", reply_markup=admin_keyboard())
            return
        if text in SECTION_MAP:
            context.user_data["action"] = "add_content_file"
            context.user_data["section"] = SECTION_MAP[text]
            await update.message.reply_text(
                f"✅ Bo'lim: *{SECTIONS.get(SECTION_MAP[text], text)}*\n\n"
                "Endi video, fayl, rasm yoki matn yuboring.\n"
                "_(Izohlash uchun caption qo'shishingiz mumkin)_",
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardMarkup([[KeyboardButton("◀️ Bekor qilish")]], resize_keyboard=True)
            )
        return

    # ── KONTENT QO'SHISH: fayl qabul qilish ──
    if action == "add_content_file":
        if text == "◀️ Bekor qilish":
            context.user_data.clear()
            await update.message.reply_text("Bekor qilindi.", reply_markup=admin_keyboard())
            return
        section = context.user_data.get("section")
        user_id = update.effective_user.id
        msg = update.message
        cap = msg.caption or ""

        if msg.video:
            context.user_data["pending_file_id"] = msg.video.file_id
            context.user_data["pending_type"] = "video"
            context.user_data["pending_caption"] = cap
        elif msg.document:
            context.user_data["pending_file_id"] = msg.document.file_id
            context.user_data["pending_type"] = "document"
            context.user_data["pending_caption"] = cap
        elif msg.photo:
            context.user_data["pending_file_id"] = msg.photo[-1].file_id
            context.user_data["pending_type"] = "photo"
            context.user_data["pending_caption"] = cap
        elif text and text != "◀️ Bekor qilish":
            context.user_data["pending_file_id"] = text
            context.user_data["pending_type"] = "text"
            context.user_data["pending_caption"] = ""
        else:
            await update.message.reply_text("❌ Faqat video, fayl, rasm yoki matn yuboring.")
            return

        context.user_data["action"] = "add_content_free_or_paid"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🆓 Bepul", callback_data="content_free"),
             InlineKeyboardButton("💎 Pullik (premium)", callback_data="content_paid")]
        ])
        await update.message.reply_text(
            "Bu kontent *bepulmi* yoki *pullik* (premium)?",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        return

    # ── KONTENT O'CHIRISH: bo'lim tanlash ──
    if action == "delete_content_section":
        if text == "◀️ Bekor qilish":
            context.user_data.clear()
            await update.message.reply_text("Bekor qilindi.", reply_markup=admin_keyboard())
            return
        if text in SECTION_MAP:
            section = SECTION_MAP[text]
            contents = db.get_content(section)
            if not contents:
                await update.message.reply_text("📭 Bu bo'limda kontent yo'q.", reply_markup=admin_keyboard())
                context.user_data.clear()
                return
            keyboard = []
            for item in contents:
                label = f"[{item['id']}] {item['content_type'].upper()} — {item['caption'][:25] if item['caption'] else '(izohsiz)'}"
                keyboard.append([InlineKeyboardButton(label, callback_data=f"del_{item['id']}")])
            await update.message.reply_text(
                f"🗑 O'chirish uchun tanlang:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            context.user_data.clear()
        return

    # ── ASOSIY TUGMALAR ──
    main_handlers = {
        # Asosiy 4 tugma
        "👤 Shaxsiy kabinet": shaxsiy_kabinet,
        "🎯 Loyihalar": loyihalar_new,
        "🔥 DTM 30 Testlar": dtm_30_test,
        "📝 Test xizmati": test_xizmati,
        "👨‍🏫 O'qituvchi haqida": o_qituvchi,
        
        # Kabinet
        "💰 Balansim": balansim,
        "💎 UMM tangalarim": umm_tangalarim,
        "🎁 UMM bilan premium olish": umm_premium_olish,
        "➕ Balans to'ldirish": balans_toldirish,
        "⚡ Pullik kurs sotib olish": pullik_kurs_sotib_olish,
        # Test xizmati
        "✅ DTM test tekshirish": test_tekshirish,
        "🏅 MS test tekshirish": ms_test_tekshirish,
        "👨‍🏫 O'qituvchi paneli": teacher_panel,
        # Loyihalar
        "📚 Nazariya uchun tayyorgarlik": nazariya,
        "🔬 Masala — noldan boshlash": masala_noldan,
        "🏆 Masala — sertifikat darajasi": masala_sertifikat,
        "📝 DTM testlar arxivi": dtm_testlar,
        # O'qituvchi
        "➕ Test yaratish": teacher_create_test,
        "➕ MS Test yaratish": teacher_create_ms_test,
        "📋 Mening testlarim": teacher_my_tests,
        "🗑 Testni o'chirish": teacher_delete_test_start,
        # DTM
        "📝 DTM testlar": dtm_testlar,
        "🔥 DTM 30-TALIK TEST ISHLASH 🔥": dtm_30_test,
        "📅 Yillar bo'yicha DTM testlar": dtm_yillar,
        "🔬 Mavzular bo'yicha DTM testlar": dtm_mavzular,
        "📖 Nazariy mavzular darsi": nazariy_dars,
        "📝 Mavzular yuzasidan testlar": mavzu_testlar,
        "🔍 Nazariy test tahlillari": test_tahlil,
        "🔬 Masala — noldan boshlash": masala_noldan,
        "🏆 Masala — sertifikat darajasi": masala_sertifikat,
        "👨‍🏫 O'qituvchi haqida": o_qituvchi,
        "📩 Admin bilan bog'lanish": admin_boglanish,
        "◀️ Orqaga": back_to_main,
        "◀️ Bekor qilish": back_to_main,
        "🛠 Admin panel": admin_panel,
        "➕ Test qo'shish": admin_test_qosh,
        "📊 Test natijalari": test_natijalari,
        "👥 Foydalanuvchilar": all_users,
        "📊 Natijalarni ko'rish": test_natijalari,
        "📋 Testlar": admin_test_list,
        "➕ Kontent qo'shish": kontent_qosh_start,
        "🔥 DTM30: Yangi test qo'shish": dtm30_admin_start,
        "🗑 DTM30: Test o'chirish": dtm30_delete_start,
        "🗑 Kontent o'chirish": kontent_ochi_start,
        "📊 Statistika": admin_statistika,
        "👥 Adminlar": adminlar,
        "📢 Hammaga xabar": broadcast_start,
    }

    if text in main_handlers:
        context.user_data.clear()
        await main_handlers[text](update, context)
        return

    # ── MAVZU TUGMALARI ──
    if text in SECTION_MAP:
        await show_section(update, context, SECTION_MAP[text])
        return

    await update.message.reply_text("👇 Kerakli bo'limni tanlang:", reply_markup=main_menu_keyboard())


async def dtm30_select_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """DTM 30-talik test tanlandi"""
    query = update.callback_query
    await query.answer()
    code = query.data.replace("dtm30_", "")
    test = db.get_test(code)
    if not test:
        await query.edit_message_text("❌ Test topilmadi.")
        return

    user_id = query.from_user.id

    # Oldingi holatni tozalash
    context.user_data.clear()
    context.user_data["current_test"] = test
    context.user_data["user_answers"] = {}
    context.user_data["action"] = "dtm30_answering"
    context.user_data["s_name"] = query.from_user.full_name
    context.user_data["s_region"] = "—"
    context.user_data["s_phone"] = "—"
    context.user_data["s_grade"] = "—"

    # PDF yuborish
    if test.get("pdf_file_id"):
        try:
            await context.bot.send_document(
                chat_id=user_id,
                document=test["pdf_file_id"],
                caption=f"📋 *{test['title']}* — Test savollari",
                parse_mode="Markdown"
            )
        except:
            pass

    # Tugmalar chiqarish
    await query.edit_message_text(
        f"🔥 *{test['title']}*\n\n"
        f"📊 30 ta savol — har birini bosib A/B/C/D belgilang 👇\n"
        f"Barchasini belgilab bo'lsangiz natija avtomatik chiqadi!",
        parse_mode="Markdown",
        reply_markup=build_answer_keyboard({}, 30)
    )

async def watch_video_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    code = query.data.replace("watch_video_", "")
    video = db.get_test_video(code)
    if not video:
        await query.answer("❌ Video topilmadi!", show_alert=True)
        return
    caption = video.get("caption") or "🎬 Test tahlili"
    try:
        await context.bot.send_video(
            chat_id=query.from_user.id,
            video=video["video_file_id"],
            caption=f"🎬 *{caption}*",
            parse_mode="Markdown"
        )
    except Exception as e:
        await query.answer("Video yuborishda xato!", show_alert=True)

async def content_free_paid_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return

    is_free = 1 if query.data == "content_free" else 0
    section = context.user_data.get("section")
    file_id = context.user_data.get("pending_file_id")
    ctype = context.user_data.get("pending_type")
    cap = context.user_data.get("pending_caption", "")
    user_id = query.from_user.id

    db.add_content(section, ctype, file_id, cap, user_id, is_free=is_free)

    label = "🆓 Bepul" if is_free else "💎 Pullik"
    type_labels = {"video": "🎥 Video", "document": "📄 Fayl", "photo": "🖼 Rasm", "text": "📝 Matn"}
    ctype_label = type_labels.get(ctype, ctype)

    context.user_data.clear()
    await query.edit_message_text(
        f"✅ *{ctype_label} qo'shildi!*\n"
        f"Bo'lim: {SECTIONS.get(section, section)}\n"
        f"Tur: {label}",
        parse_mode="Markdown"
    )

async def del_section_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return
    section = query.data.replace("del_section_", "")
    contents = db.get_content(section)
    if not contents:
        await query.edit_message_text("📭 Bu bo'limda kontent yo'q.")
        return
    from config import SECTIONS
    section_name = SECTIONS.get(section, section)
    keyboard = []
    for item in contents:
        label = f"[{item['id']}] {item['content_type'].upper()} — {item['caption'][:25] if item['caption'] else '(izohsiz)'}"
        is_free = "🆓" if item.get("is_free", 1) == 1 else "💎"
        keyboard.append([InlineKeyboardButton(
            f"{is_free} {label}",
            callback_data=f"del_{item['id']}"
        )])
    keyboard.append([InlineKeyboardButton("◀️ Orqaga", callback_data="del_section_back")])
    await query.edit_message_text(
        f"🗑 *{section_name}* — o'chirish uchun tanlang:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def del_dtm30_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return
    code = query.data.replace("del_dtm30_", "")
    test = db.get_test(code)
    if not test:
        await query.edit_message_text("❌ Test topilmadi.")
        return
    # Test va videoni o'chirish
    db.delete_test(code)
    try:
        with db.connect() as conn:
            conn.execute("DELETE FROM test_videos WHERE test_code=?", (code,))
            conn.commit()
    except:
        pass
    await query.edit_message_text(
        f"✅ *{test['title']}* o'chirildi!\n(Test va video yechim ham o'chirildi)",
        parse_mode="Markdown"
    )

async def del_teacher_test_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if not db.is_teacher(user_id):
        await query.edit_message_text("❌ Ruxsat yo'q!")
        return
    code = query.data.replace("del_ttest_", "")
    db.delete_teacher_test(code, user_id)
    await query.edit_message_text(f"✅ *{code}* testi o'chirildi!", parse_mode="Markdown")

async def del_section_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    non_empty = []
    for key in SECTIONS:
        try:
            items = db.get_content(key)
            if items:
                non_empty.append((key, SECTIONS[key], len(items)))
        except:
            pass

    if not non_empty:
        await query.edit_message_text("📭 Hech bir bo'limda kontent yo'q.")
        return

    keyboard = []
    for key, name, count in non_empty:
        keyboard.append([InlineKeyboardButton(
            f"{name} ({count} ta)",
            callback_data=f"del_section_{key}"
        )])
    await query.edit_message_text(
        "🗑 *Kontent o'chirish*\n\nQaysi bo'limdan o'chirmoqchisiz?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def del_test_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return
    code = query.data.replace("del_test_", "")
    db.delete_test(code)
    await query.edit_message_text(f"✅ *{code}* testi o'chirildi!", parse_mode="Markdown")

async def delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.edit_message_text("❌ Ruxsat yo'q!")
        return
    content_id = int(query.data.replace("del_", ""))
    item = db.get_content_by_id(content_id)
    if item:
        db.delete_content(content_id)
        await query.edit_message_text(f"✅ O'chirildi: [{content_id}] {item['content_type'].upper()}")
    else:
        await query.edit_message_text("❌ Topilmadi yoki allaqachon o'chirilgan.")

# ========================
# MAIN
# ========================

def main():
    app = Application.builder().token(BOT_TOKEN).connect_timeout(30).read_timeout(30).write_timeout(30).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("admin_qosh", admin_qosh_cmd))
    app.add_handler(CommandHandler("admin_ochi", admin_ochi_cmd))
    app.add_handler(CallbackQueryHandler(buy_callback, pattern="^buy_"))
    app.add_handler(CallbackQueryHandler(pay_card_ref_callback, pattern="^pay_"))
    app.add_handler(CallbackQueryHandler(umm_buy_callback, pattern="^umm_buy_premium"))
    app.add_handler(CallbackQueryHandler(content_free_paid_callback, pattern="^content_"))
    app.add_handler(CallbackQueryHandler(delete_callback, pattern=r'^del_\d+$'))
    app.add_handler(CallbackQueryHandler(test_callback, pattern="^(q_|ans_|check_result|reset_answers|back_to_answers)"))
    app.add_handler(CallbackQueryHandler(ms_test_callback, pattern="^(ms_|msans_)"))
    app.add_handler(CallbackQueryHandler(del_test_callback, pattern="^del_test_"))
    app.add_handler(CallbackQueryHandler(users_page_callback, pattern="^users_page_"))
    app.add_handler(CallbackQueryHandler(del_dtm30_callback, pattern="^del_dtm30_"))
    app.add_handler(CallbackQueryHandler(del_section_back_callback, pattern="^del_section_back$"))
    app.add_handler(CallbackQueryHandler(del_section_callback, pattern="^del_section_(?!back)"))
    app.add_handler(CallbackQueryHandler(dtm30_select_callback, pattern="^dtm30_"))
    app.add_handler(CallbackQueryHandler(watch_video_callback, pattern="^watch_video_"))
    app.add_handler(CallbackQueryHandler(del_teacher_test_callback, pattern="^del_ttest_"))
    app.add_handler(CommandHandler("test_qosh", admin_test_qosh))
    app.add_handler(CommandHandler("testlar", admin_test_list))
    app.add_handler(CommandHandler("video_qosh", admin_video_qosh))
    app.add_handler(CommandHandler("premium_ber", admin_premium_ber_cmd))
    app.add_handler(CommandHandler("balans_ber", admin_balans_ber_cmd))
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.VIDEO | filters.Document.ALL | filters.PHOTO | filters.CONTACT) & ~filters.COMMAND,
        handle_message
    ))

    print("✅ Bot ishga tushdi!")
    app.run_polling(
        poll_interval=0.5,
        timeout=30,
        drop_pending_updates=False
    )

if __name__ == "__main__":
    main()
