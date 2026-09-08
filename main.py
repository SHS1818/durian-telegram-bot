import os
import asyncio
import threading
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

# ================= 🌐 DUMMY HTTP SERVER FOR RENDER PORT BINDING =================
class DummyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running successfully on Render!")

def run_dummy_server():
    # Render dynamic $PORT provide kare, na pelem default 8080 use korbe
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyServer)
    server.serve_forever()

# Background Thread-e Server run kora hocche jate Render Port timeout na dey
threading.Thread(target=run_dummy_server, daemon=True).start()
# ==============================================================================

# ================= ⚙️ CONFIGURATION =================
BOT_TOKEN = "8686692054:-WlhLFTA"
BOT_USERNAME = "@Durians3bot"

# 🔑 Official Durian API Credentials & Endpoint
DURIAN_USERNAME = "mrreset"
DURIAN_API_KEY = ""
BASE_URL = "https://api.durianrcs.com/out/ext_api"

# 🔌 Telegram Account Checker API Credentials
CHECKER_API_URL = ""
CHECKER_USERNAME = "user_9bdd01fe54"
CHECKER_PASSWORD = "pass_c2fce95675500035"

# 🆔 Project IDs Configuration
DEFAULT_PROJECT_ID = "0257"

# 🎯 Special Project 6003 Countries
SPECIAL_PROJECT_6003_COUNTRIES = ["eg", "us", "do", "gt", "ru", "tr", "ve", "it"]

# Panel Limits & Speeds
DAILY_PANEL_LIMIT = 1000
NUMBER_VALIDITY_SECONDS = 300
OTP_CHECK_INTERVAL = 15
MAX_TOTAL_RPM = 250  # ⚡ VIP1 Max RPM Limit
ITEMS_PER_PAGE = 30
# =====================================================

bot = telebot.TeleBot(BOT_TOKEN)

# 🛠️ Robust HTTP Session Creation
session = requests.Session()
retries = Retry(total=2, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))
session.mount('http://', HTTPAdapter(max_retries=retries))
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/115.0.0.0 Safari/537.36'
})

# 📊 Global State
user_reports = {}
user_settings = {}       # Chat ID -> {'checker_on': True/False}
target_workers = {}      # Chat ID -> { country_code: worker_dict }
stock_cache = {}         # Live stock cache system

COUNTRY_CODES = {
    "do": {"name": "Dominican Republic", "flag": "🇩🇴"},
    "in": {"name": "India", "flag": "🇮🇳"},
    "ng": {"name": "Nigeria", "flag": "🇳🇬"},
    "ve": {"name": "Venezuela", "flag": "🇻🇪"},
    "ly": {"name": "Libya", "flag": "🇱🇾"},
    "th": {"name": "Thailand", "flag": "🇹🇭"},
    "tz": {"name": "Tanzania", "flag": "🇹🇿"},
    "mx": {"name": "Mexico", "flag": "🇲🇽"},
    "ph": {"name": "Philippines", "flag": "🇵🇭"},
    "sn": {"name": "Senegal", "flag": "🇸🇳"},
    "tg": {"name": "Togo", "flag": "🇹🇬"},
    "cm": {"name": "Cameroon", "flag": "🇨🇲"},
    "ar": {"name": "Argentina", "flag": "🇦🇷"},
    "sy": {"name": "Syria", "flag": "🇸🇾"},
    "ht": {"name": "Haiti", "flag": "🇭🇹"},
    "ao": {"name": "Angola", "flag": "🇦🇴"},
    "bd": {"name": "Bangladesh", "flag": "🇧🇩"},
    "gh": {"name": "Ghana", "flag": "🇬🇭"},
    "cg": {"name": "Congo", "flag": "🇨🇬"},
    "mw": {"name": "Malawi", "flag": "🇲🇼"},
    "gb": {"name": "United Kingdom", "flag": "🇬🇧"},
    "dz": {"name": "Algeria", "flag": "🇩🇿"},
    "np": {"name": "Nepal", "flag": "🇳🇵"},
    "kz": {"name": "Kazakhstan", "flag": "🇰🇿"},
    "cd": {"name": "D R Congo", "flag": "🇨🇩"},
    "id": {"name": "Indonesia", "flag": "🇮🇩"},
    "ca": {"name": "Canada", "flag": "🇨🇦"},
    "cu": {"name": "Cuba", "flag": "🇨🇺"},
    "bf": {"name": "Burkina Faso", "flag": "🇧🇫"},
    "sl": {"name": "Sierra Leone", "flag": "🇸🇱"},
    "pk": {"name": "Pakistan", "flag": "🇵🇰"},
    "ls": {"name": "Lesotho", "flag": "🇱🇸"},
    "zm": {"name": "Zambia", "flag": "🇿🇲"},
    "kh": {"name": "Cambodia", "flag": "🇰🇭"},
    "us": {"name": "USA", "flag": "🇺🇸"},
    "et": {"name": "Ethiopia", "flag": "🇪🇹"},
    "ae": {"name": "United Arab Emirates", "flag": "🇦🇪"},
    "ni": {"name": "Nicaragua", "flag": "🇳🇮"},
    "hn": {"name": "Honduras", "flag": "🇭🇳"},
    "gt": {"name": "Guatemala", "flag": "🇬🇹"},
    "mr": {"name": "Mauritania", "flag": "🇲🇷"},
    "il": {"name": "Israel", "flag": "🇮🇱"},
    "fr": {"name": "France", "flag": "🇫🇷"},
    "tt": {"name": "Trinidad & Tobago", "flag": "🇹🇹"},
    "sv": {"name": "El Salvador", "flag": "🇸🇻"},
    "tn": {"name": "Tunisia", "flag": "🇹🇳"},
    "my": {"name": "Malaysia", "flag": "🇲🇾"},
    "de": {"name": "Germany", "flag": "🇩🇪"},
    "jm": {"name": "Jamaica", "flag": "🇯🇲"},
    "bz": {"name": "Belize", "flag": "🇧🇿"},
    "pe": {"name": "Peru", "flag": "🇵🇪"},
    "sd": {"name": "Sudan", "flag": "🇸🇩"},
    "lk": {"name": "Sri Lanka", "flag": "🇱🇰"},
    "ma": {"name": "Morocco", "flag": "🇲🇦"},
    "af": {"name": "Afghanistan", "flag": "🇦🇫"},
    "vn": {"name": "Vietnam", "flag": "🇻🇳"},
    "uz": {"name": "Uzbekistan", "flag": "🇺🇿"},
    "mm": {"name": "Myanmar", "flag": "🇲🇲"},
    "iq": {"name": "Iraq", "flag": "🇮🇶"},
    "ye": {"name": "Yemen", "flag": "🇾🇪"},
    "ge": {"name": "Georgia", "flag": "🇬🇪"},
    "fj": {"name": "Fiji Islands", "flag": "🇫🇯"},
    "au": {"name": "Australia", "flag": "🇦🇺"},
    "uy": {"name": "Uruguay", "flag": "🇺🇾"},
    "lb": {"name": "Lebanon", "flag": "🇱🇧"},
    "qa": {"name": "Qatar", "flag": "🇶🇦"},
    "rw": {"name": "Rwanda", "flag": "🇷🇼"},
    "gn": {"name": "Guinea", "flag": "🇬🇳"},
    "am": {"name": "Armenia", "flag": "🇦🇲"},
    "by": {"name": "Belarus", "flag": "🇧🇾"},
    "pl": {"name": "Poland", "flag": "🇵🇱"},
    "sr": {"name": "Suriname", "flag": "🇸🇷"},
    "md": {"name": "Moldova", "flag": "🇲🇩"},
    "gy": {"name": "Guyana", "flag": "🇬🇾"},
    "mu": {"name": "Mauritius", "flag": "🇲🇺"},
    "jp": {"name": "Japan", "flag": "🇯🇵"},
    "bw": {"name": "Botswana", "flag": "🇧🇼"},
    "sz": {"name": "Eswatini / Swaziland", "flag": "🇸🇿"},
    "bs": {"name": "Bahamas", "flag": "🇧🇸"},
    "ne": {"name": "Niger", "flag": "🇳🇪"},
    "zw": {"name": "Zimbabwe", "flag": "🇿🇼"},
    "ss": {"name": "South Sudan", "flag": "🇸🇸"},
    "rs": {"name": "Serbia", "flag": "🇷🇸"},
    "sg": {"name": "Singapore", "flag": "🇸🇬"},
    "cl": {"name": "Chile", "flag": "🇨🇱"},
    "td": {"name": "Chad", "flag": "🇹🇩"},
    "na": {"name": "Namibia", "flag": "🇳🇦"},
    "ro": {"name": "Romania", "flag": "🇷🇴"},
    "bb": {"name": "Barbados", "flag": "🇧🇧"},
    "dk": {"name": "Denmark", "flag": "🇩🇰"},
    "tr": {"name": "Türkiye", "flag": "🇹🇷"},
    "at": {"name": "Austria", "flag": "🇦🇹"},
    "nz": {"name": "New Zealand", "flag": "🇳🇿"},
    "nl": {"name": "Netherlands", "flag": "🇳🇱"},
    "bh": {"name": "Bahrain", "flag": "🇧🇭"},
    "gd": {"name": "Grenada", "flag": "🇬🇩"},
    "bi": {"name": "Burundi", "flag": "🇧🇮"},
    "so": {"name": "Somalia", "flag": "🇸🇴"},
    "vc": {"name": "St. Vincent & Grenadines", "flag": "🇻🇨"},
    "lt": {"name": "Lithuania", "flag": "🇱🇹"},
    "za": {"name": "South Africa", "flag": "🇿🇦"},
    "ru": {"name": "Russia", "flag": "🇷🇺"},
    "ke": {"name": "Kenya", "flag": "🇰🇪"},
    "ec": {"name": "Ecuador", "flag": "🇪🇨"},
    "eg": {"name": "Egypt", "flag": "🇪🇬"},
    "sa": {"name": "Saudi Arabia", "flag": "🇸🇦"},
    "mz": {"name": "Mozambique", "flag": "🇲🇿"},
    "ua": {"name": "Ukraine", "flag": "🇺🇦"},
    "ug": {"name": "Uganda", "flag": "🇺🇬"},
    "br": {"name": "Brazil", "flag": "🇧🇷"},
    "es": {"name": "Spain", "flag": "🇪🇸"},
    "gm": {"name": "Gambia", "flag": "🇬🇲"},
    "mg": {"name": "Madagascar", "flag": "🇲🇬"},
    "ml": {"name": "Mali", "flag": "🇲🇱"},
    "pg": {"name": "Papua New Guinea", "flag": "🇵🇬"},
    "jo": {"name": "Jordan", "flag": "🇯🇴"},
    "la": {"name": "Laos", "flag": "🇱🇦"},
    "kw": {"name": "Kuwait", "flag": "🇰🇼"},
    "it": {"name": "Italy", "flag": "🇮🇹"},
    "pt": {"name": "Portugal", "flag": "🇵🇹"},
    "ws": {"name": "Samoa", "flag": "🇼🇸"},
    "co": {"name": "Colombia", "flag": "🇨🇴"},
    "lr": {"name": "Liberia", "flag": "🇱🇷"},
    "tj": {"name": "Tajikistan", "flag": "🇹🇯"},
    "tl": {"name": "East Timor", "flag": "🇹🇱"},
    "mn": {"name": "Mongolia", "flag": "🇲🇳"},
    "mv": {"name": "Maldives", "flag": "🇲🇻"},
    "cz": {"name": "Czech Republic", "flag": "🇨🇿"},
    "pa": {"name": "Panama", "flag": "🇵🇦"},
    "cf": {"name": "Central African Republic", "flag": "🇨🇫"},
    "ir": {"name": "Iran", "flag": "🇮🇷"},
    "kn": {"name": "Saint Kitts and Nevis", "flag": "🇰🇳"},
    "kr": {"name": "South Korea", "flag": "🇰🇷"},
    "om": {"name": "Oman", "flag": "🇴🇲"},
    "pr": {"name": "Puerto Rico", "flag": "🇵🇷"},
    "ie": {"name": "Ireland", "flag": "🇮🇪"},
    "ch": {"name": "Switzerland", "flag": "🇨🇭"},
    "ag": {"name": "Antigua and Barbuda", "flag": "🇦🇬"},
    "az": {"name": "Azerbaijan", "flag": "🇦🇿"},
    "bt": {"name": "Bhutan", "flag": "🇧🇹"},
    "gr": {"name": "Greece", "flag": "🇬🇷"},
    "gw": {"name": "Guinea-Bissau", "flag": "🇬🇼"},
    "kg": {"name": "Kyrgyzstan", "flag": "🇰🇬"},
    "ki": {"name": "Kiribati", "flag": "🇰🇮"},
    "lv": {"name": "Latvia", "flag": "🇱🇻"},
    "tm": {"name": "Turkmenistan", "flag": "🇹🇲"},
    "vg": {"name": "Virgin Islands (British)", "flag": "🇻🇬"},
    "vu": {"name": "Vanuatu", "flag": "🇻🇺"},
    "fi": {"name": "Finland", "flag": "🇫🇮"},
    "hu": {"name": "Hungary", "flag": "🇭🇺"},
    "lu": {"name": "Luxembourg", "flag": "🇱🇺"},
    "no": {"name": "Norway", "flag": "🇳🇴"},
    "si": {"name": "Slovenia", "flag": "🇸🇮"},
    "mk": {"name": "North Macedonia", "flag": "🇲🇰"},
    "ad": {"name": "Andorra", "flag": "🇦🇩"},
    "ai": {"name": "Anguilla", "flag": "🇦🇮"},
    "al": {"name": "Albania", "flag": "🇦🇱"},
    "as": {"name": "American Samoa", "flag": "🇦🇸"},
    "aw": {"name": "Aruba", "flag": "🇦🇼"},
    "ba": {"name": "Bosnia and Herzegovina", "flag": "🇧🇦"},
    "be": {"name": "Belgium", "flag": "🇧🇪"},
    "bg": {"name": "Bulgaria", "flag": "🇧🇬"},
    "bj": {"name": "Benin", "flag": "🇧🇯"},
    "bm": {"name": "Bermuda", "flag": "🇧🇲"},
    "bn": {"name": "Brunei", "flag": "🇧🇳"},
    "bo": {"name": "Bolivia", "flag": "🇧🇴"},
    "ci": {"name": "Côte d'Ivoire", "flag": "🇨🇮"},
    "ck": {"name": "Cook Islands", "flag": "🇨🇰"},
    "cr": {"name": "Costa Rica", "flag": "🇨🇷"},
    "cv": {"name": "Cape Verde", "flag": "🇨🇻"},
    "cy": {"name": "Cyprus", "flag": "🇨🇾"},
    "dj": {"name": "Djibouti", "flag": "🇩🇯"},
    "dm": {"name": "Dominica", "flag": "🇩🇲"},
    "ee": {"name": "Estonia", "flag": "🇪🇪"},
    "er": {"name": "Eritrea", "flag": "🇪🇷"},
    "fm": {"name": "Micronesia", "flag": "🇫🇲"},
    "fo": {"name": "Faroe Islands", "flag": "🇫🇴"},
    "ga": {"name": "Gabon", "flag": "🇬🇦"},
    "gf": {"name": "French Guiana", "flag": "🇬🇫"},
    "gi": {"name": "Gibraltar", "flag": "🇬🇮"},
    "gl": {"name": "Greenland", "flag": "🇬🇱"},
    "gp": {"name": "Guadeloupe", "flag": "🇬🇵"},
    "gq": {"name": "Equatorial Guinea", "flag": "🇬🇶"},
    "gu": {"name": "Guam", "flag": "🇬🇺"},
    "hk": {"name": "Hong Kong, China", "flag": "🇭🇰"},
    "hr": {"name": "Croatia", "flag": "🇭🇷"},
    "im": {"name": "Isle of Man", "flag": "🇮🇲"},
    "is": {"name": "Iceland", "flag": "🇮🇸"},
    "km": {"name": "Comoros", "flag": "🇰🇲"},
    "ky": {"name": "Cayman Islands", "flag": "🇰🇾"},
    "lc": {"name": "Saint Lucia", "flag": "🇱🇨"},
    "li": {"name": "Liechtenstein", "flag": "🇱🇮"},
    "mc": {"name": "Monaco", "flag": "🇲🇨"},
    "me": {"name": "Montenegro", "flag": "🇲🇪"},
    "mf": {"name": "Saint Martin", "flag": "🇲🇫"},
    "mh": {"name": "Marshall Islands", "flag": "🇲🇭"},
    "mo": {"name": "Macau, China", "flag": "🇲🇴"},
    "mq": {"name": "Martinique", "flag": "🇲🇶"},
    "ms": {"name": "Montserrat", "flag": "🇲🇸"},
    "mt": {"name": "Malta", "flag": "🇲🇹"},
    "nc": {"name": "New Caledonia", "flag": "🇳🇨"},
    "pf": {"name": "French Polynesia", "flag": "🇵🇫"},
    "ps": {"name": "Palestinian Authority", "flag": "🇵🇸"},
    "pw": {"name": "Palau Islands", "flag": "🇵🇼"},
    "py": {"name": "Paraguay", "flag": "🇵🇾"},
    "re": {"name": "Réunion Island", "flag": "🇷🇪"},
    "sb": {"name": "Solomon Islands", "flag": "🇸🇧"},
    "sc": {"name": "Seychelles", "flag": "🇸🇨"},
    "se": {"name": "Sweden", "flag": "🇸🇪"},
    "sk": {"name": "Slovakia", "flag": "🇸🇰"},
    "st": {"name": "São Tomé and Príncipe", "flag": "🇸🇹"},
    "tc": {"name": "Turks and Caicos Islands", "flag": "🇹🇨"},
    "to": {"name": "Tonga", "flag": "🇹🇴"},
    "tv": {"name": "Tuvalu", "flag": "🇹🇻"},
    "tw": {"name": "Taiwan, China", "flag": "🇹🇼"},
    "wf": {"name": "Wallis and Futuna Islands", "flag": "🇼🇫"},
    "yt": {"name": "Mayotte", "flag": "🇾🇹"},
    "cc": {"name": "Cocos (Keeling) Islands", "flag": "🇨🇨"},
    "hm": {"name": "Heard and McDonald Islands", "flag": "🇭🇲"},
    "aq": {"name": "Antarctica", "flag": "🇦🇶"},
    "ax": {"name": "Åland Islands", "flag": "🇦🇽"},
    "bl": {"name": "Saint Barthélemy", "flag": "🇧🇱"},
    "bv": {"name": "Bouvet Island", "flag": "🇧🇻"},
    "cx": {"name": "Christmas Island", "flag": "🇨🇽"},
    "eh": {"name": "Western Sahara", "flag": "🇪🇭"},
    "fk": {"name": "Falkland Islands", "flag": "🇫🇰"},
    "gg": {"name": "Guernsey", "flag": "🇬🇬"},
    "gs": {"name": "South Georgia & S. Sandwich", "flag": "🇬🇸"},
    "io": {"name": "British Indian Ocean Territory", "flag": "🇮🇴"},
    "je": {"name": "Jersey", "flag": "🇯🇪"},
    "kp": {"name": "North Korea", "flag": "🇰🇵"},
    "mp": {"name": "Northern Mariana Islands", "flag": "🇲🇵"},
    "nf": {"name": "Norfolk Island", "flag": "🇳🇫"},
    "nr": {"name": "Nauru", "flag": "🇳🇷"},
    "nu": {"name": "Niue", "flag": "🇳🇺"},
    "pm": {"name": "Saint Pierre and Miquelon", "flag": "🇵🇲"},
    "pn": {"name": "Pitcairn Islands", "flag": "🇵🇳"},
    "sh": {"name": "Saint Helena", "flag": "🇸🇭"},
    "sj": {"name": "Svalbard and Jan Mayen", "flag": "🇸🇯"},
    "sm": {"name": "San Marino", "flag": "🇸🇲"},
    "tf": {"name": "French Southern Territories", "flag": "🇹🇫"},
    "tk": {"name": "Tokelau", "flag": "🇹🇰"},
    "um": {"name": "U.S. Outlying Islands", "flag": "🇺🇲"},
    "va": {"name": "Vatican City", "flag": "🇻🇦"},
    "vi": {"name": "Virgin Islands (U.S.)", "flag": "🇻🇮"},
    "xk": {"name": "Kosovo", "flag": "🇽🇰"},
    "an": {"name": "Netherlands Antilles", "flag": "🇳🇱"}
}


# --- 🛠️ HELPER FUNCTIONS ---

def get_project_id_for_country(country_code):
    if country_code.lower().strip() in SPECIAL_PROJECT_6003_COUNTRIES:
        return "6003"
    return DEFAULT_PROJECT_ID

def get_user_report(chat_id):
    if chat_id not in user_reports:
        user_reports[chat_id] = {"total_fetched": 0, "fresh_counts": 0, "otp_received": 0}
    return user_reports[chat_id]

def get_user_setting(chat_id):
    if chat_id not in user_settings:
        user_settings[chat_id] = {"checker_on": True}
    return user_settings[chat_id]

# 🔍 TELEGRAM CHECKER API FUNCTION
def is_telegram_registered(phone_number: str) -> bool:
    clean_phone = phone_number.replace("+", "").strip()
    payload = {
        "username": CHECKER_USERNAME,
        "password": CHECKER_PASSWORD,
        "phone_numbers": [clean_phone]
    }
    
    for attempt in range(2):
        try:
            res = session.post(CHECKER_API_URL, json=payload, timeout=5)
            if res.status_code == 200:
                data = res.json()
                fresh_list = [str(x) for x in data.get("fresh", [])]
                registered_list = [str(x) for x in data.get("registered", [])]
                banned_list = [str(x) for x in data.get("banned", [])]

                if clean_phone in fresh_list:
                    return False  # Fresh
                if clean_phone in registered_list or clean_phone in banned_list:
                    return True   # Old
                if len(registered_list) > 0 or len(banned_list) > 0:
                    return True
                if len(fresh_list) > 0:
                    return False
        except Exception:
            time.sleep(0.5)
            
    return True

# 💰 DURIAN BALANCE
def fetch_durian_balance():
    url = f"{BASE_URL}/getUserInfo"
    params = {'name': DURIAN_USERNAME, 'ApiKey': DURIAN_API_KEY}
    try:
        res = session.get(url, params=params, timeout=5)
        if res.status_code == 200 and str(res.json().get('code')) == '200':
            return res.json().get('data', {}).get('score', '0')
    except Exception:
        pass
    return "N/A"

# 📊 ACCURATE COUNTRY-SPECIFIC STOCK FETCHING
def fetch_durian_stock_for_country(country_code):
    current_time = time.time()
    if country_code in stock_cache and (current_time - stock_cache[country_code]['time'] < 30):
        return stock_cache[country_code]['val']

    pid = get_project_id_for_country(country_code)
    url = f"{BASE_URL}/getCounts"
    params = {
        'name': DURIAN_USERNAME,
        'ApiKey': DURIAN_API_KEY,
        'pid': pid,
        'cuy': country_code.lower().strip()
    }
    
    stock_count = 0
    try:
        res = session.get(url, params=params, timeout=4)
        if res.status_code == 200:
            res_json = res.json()
            if str(res_json.get('code')) == '200':
                data = res_json.get('data')
                if isinstance(data, dict):
                    stock_count = int(data.get(country_code.lower(), 0))
                elif isinstance(data, (int, str)):
                    stock_count = int(data)
    except Exception:
        stock_count = 0

    stock_cache[country_code] = {'val': stock_count, 'time': current_time}
    return stock_count

# 📲 DURIAN GET MOBILE
def durian_get_mobile(country_code="bd", prefix=""):
    pid = get_project_id_for_country(country_code)
    cuy = country_code.lower().strip()
    url = f"{BASE_URL}/getMobile"
    params = {
        'name': DURIAN_USERNAME,
        'ApiKey': DURIAN_API_KEY,
        'cuy': cuy,
        'pid': pid,
        'num': 1,
        'noblack': 0,
        'serial': 2
    }
    
    if prefix:
        params['prefix'] = prefix

    try:
        res = session.get(url, params=params, timeout=6)
        if res.status_code == 200:
            data = res.json()
            code = str(data.get('code'))
            if code == '200':
                phone = str(data.get('data'))
                if not phone.startswith('+'):
                    phone = '+' + phone
                return True, phone, pid
            else:
                return False, f"Code [{code}]: {data.get('msg', 'Error')}", pid
        return False, f"HTTP Error {res.status_code}", pid
    except Exception as e:
        return False, f"Error: {str(e)}", pid

# 🚫 DURIAN ADD BLACKLIST
def durian_add_blacklist(phone_number, pid):
    clean_phone = phone_number.replace("+", "").strip()
    url = f"{BASE_URL}/addBlack"
    params = {
        'name': DURIAN_USERNAME,
        'ApiKey': DURIAN_API_KEY,
        'pn': clean_phone,
        'pid': pid
    }
    try:
        session.get(url, params=params, timeout=4)
    except Exception:
        pass

# 📩 FIXED: DURIAN GET SMS
def durian_get_sms(phone_number, pid):
    clean_phone = phone_number.replace("+", "").strip()
    url = f"{BASE_URL}/getMsg"
    params = {
        'name': DURIAN_USERNAME,
        'ApiKey': DURIAN_API_KEY,
        'pn': clean_phone,
        'pid': pid,
        'serial': 2
    }
    try:
        res = session.get(url, params=params, timeout=5)
        if res.status_code == 200:
            res_json = res.json()
            if str(res_json.get('code')) == '200':
                sms_data = res_json.get('data')
                # Check valid sms text payload
                if sms_data and str(sms_data).strip() not in ["None", "", "WAITING", "NO_SMS"]:
                    return True, str(sms_data)
    except Exception:
        pass
    return False, None

# ⏱️ FIXED: OTP LISTENER
def check_real_otp(chat_id, phone_number, pid, country_code, message_id):
    max_loops = NUMBER_VALIDITY_SECONDS // OTP_CHECK_INTERVAL
    otp_received = False
    c_info = COUNTRY_CODES.get(country_code, {"name": country_code.upper(), "flag": "🌐"})

    for _ in range(max_loops):
        time.sleep(OTP_CHECK_INTERVAL)
        success, sms_data = durian_get_sms(phone_number, pid)

        if success and sms_data:
            otp_msg = (
                f"💬 Telegram <code>{phone_number}</code> ✅\n"
                f"••••••••••••••••••••••••••••••••••••\n"
                f"{c_info['flag']} {c_info['name']} (PID: {pid})\n"
                f"🔑 <b>OTP:</b> <code>{sms_data}</code>"
            )
            try:
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=otp_msg, parse_mode="HTML")
                bot.pin_chat_message(chat_id, message_id)
            except Exception:
                pass
            
            report = get_user_report(chat_id)
            report["otp_received"] += 1
            otp_received = True
            break

    if not otp_received:
        durian_add_blacklist(phone_number, pid)
        timeout_msg = (
            f"💬 Telegram <code>{phone_number}</code> 🟡\n"
            f"••••••••••••••••••••••••••••••••••••\n"
            f"{c_info['flag']} {c_info['name']} (PID: {pid})\n"
            f"⏰ <b>Status:</b> Timeout"
        )
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=timeout_msg, parse_mode="HTML")
        except Exception:
            pass

def issue_and_track_number(chat_id, phone, used_pid, country_code):
    c_info = COUNTRY_CODES.get(country_code, {"name": country_code.upper(), "flag": "🌐"})
    
    initial_msg = (
        f"💬 Telegram <code>{phone}</code> 🟡\n"
        f"••••••••••••••••••••••••••••••••••••\n"
        f"{c_info['flag']} {c_info['name']} (PID: {used_pid})"
    )
    sent_message = bot.send_message(chat_id, initial_msg, parse_mode="HTML")
    
    threading.Thread(
        target=check_real_otp, 
        args=(chat_id, phone, used_pid, country_code, sent_message.message_id)
    ).start()

# --- 🚀 MULTI-TARGET WORKER LOOP WITH DYNAMIC RPM ---
def run_target_loop(chat_id, message_id, country_code, prefix=""):
    worker = target_workers[chat_id][country_code]
    c_info = COUNTRY_CODES.get(country_code, {"name": country_code.upper(), "flag": "🌐"})
    last_update_time = time.time()

    while worker['status'] != 'stopped':
        if worker['status'] == 'paused':
            time.sleep(1)
            continue

        worker['requests'] += 1

        success, result, used_pid = durian_get_mobile(country_code, prefix)
        if success:
            phone = result
            clean_phone = phone.replace("+", "").strip()

            if prefix and not clean_phone.startswith(prefix.strip()):
                durian_add_blacklist(phone, used_pid)
                time.sleep(0.1)
                continue

            setting = get_user_setting(chat_id)

            if setting['checker_on']:
                worker['checked'] += 1
                registered = is_telegram_registered(phone)
                
                if not registered:
                    worker['got'] += 1
                    report = get_user_report(chat_id)
                    report["total_fetched"] += 1
                    report["fresh_counts"] += 1

                    issue_and_track_number(chat_id, phone, used_pid, country_code)
                else:
                    durian_add_blacklist(phone, used_pid)
            else:
                worker['got'] += 1
                report = get_user_report(chat_id)
                report["total_fetched"] += 1

                issue_and_track_number(chat_id, phone, used_pid, country_code)

        active_targets_count = 0
        for uid in target_workers:
            for c_code, w_info in target_workers[uid].items():
                if w_info.get('status') == 'running':
                    active_targets_count += 1

        active_targets_count = max(1, active_targets_count)
        current_target_rpm = MAX_TOTAL_RPM / active_targets_count

        if time.time() - last_update_time > 3:
            status_text = "Running..." if worker['status'] == 'running' else "Paused ⏸️"
            pause_btn_text = "⏸️ Pause" if worker['status'] == 'running' else "▶️ Resume"
            prefix_info = f" [P: {prefix}]" if prefix else ""

            text = (
                f"🚀 <b>Target Running ({country_code.upper()}{prefix_info})</b>   {current_target_rpm:.1f} RPM\n"
                f"•••••••••••••••••••••••••••••••••••••••••••••••\n"
                f"{c_info['flag']} <b>{c_info['name']}</b> (PID: {get_project_id_for_country(country_code)})\n"
                f"📡 <b>Requests:</b> {worker['requests']} | ✅ <b>Got:</b> {worker['got']}\n"
                f"🔍 <b>Checked:</b> {worker['checked']}\n"
                f"🔄 <b>{status_text}</b>"
            )

            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton(pause_btn_text, callback_data=f"tgt_pause_{country_code}"),
                InlineKeyboardButton("⏹️ Stop", callback_data=f"tgt_stop_{country_code}")
            )

            try:
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode="HTML", reply_markup=markup)
            except Exception:
                pass

            last_update_time = time.time()

        time.sleep(60.0 / current_target_rpm)

# --- ⌨️ KEYBOARDS ---

def main_reply_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        KeyboardButton("📲 Get Number"),
        KeyboardButton("🎯 Set Target"),
        KeyboardButton("🎯 Bulk Target"),
        KeyboardButton("📈 Daily Report"),
        KeyboardButton("📊 Live Stock"),
        KeyboardButton("💰 My Balance"),
        KeyboardButton("⚙️ Go Settings")
    )
    return markup

def generate_country_keyboard_page(page=0):
    items = list(COUNTRY_CODES.items())
    total_pages = (len(items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_items = items[start_idx:end_idx]

    markup = InlineKeyboardMarkup()

    for i in range(0, len(page_items), 2):
        row = []
        code1, info1 = page_items[i]
        stock1 = fetch_durian_stock_for_country(code1)
        row.append(InlineKeyboardButton(f"{info1['flag']} {info1['name']} [{stock1}]", callback_data=f"get_{code1}"))

        if i + 1 < len(page_items):
            code2, info2 = page_items[i+1]
            stock2 = fetch_durian_stock_for_country(code2)
            row.append(InlineKeyboardButton(f"{info2['flag']} {info2['name']} [{stock2}]", callback_data=f"get_{code2}"))

        markup.row(*row)

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"page_{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="noop"))
    
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"page_{page+1}"))

    markup.row(*nav_buttons)
    return markup

# --- 🤖 BOT HANDLERS ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = f"👋 <b>Welcome to @{BOT_USERNAME}!</b>\n\nমেনু থেকে আপনার অপশন সিলেক্ট করুন:"
    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=main_reply_keyboard())

# 💰 MY BALANCE
@bot.message_handler(func=lambda msg: "My Balance" in msg.text)
def handle_balance_msg(message):
    points = fetch_durian_balance()
    text = (
        f"💳 <b>Durians Panel Balance</b>\n"
        f"••••••••••••••••••••••••••••••••••••\n"
        f"🎯 <b>Available Credits:</b> <code>{points}</code> Points"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML")

# 📊 LIVE STOCK
@bot.message_handler(func=lambda msg: "Live Stock" in msg.text)
def handle_live_stock(message):
    loading = bot.reply_to(message, "🔄 <i>Updating live stock...</i>", parse_mode="HTML")
    
    lines = ["📊 <b>Live Stock:</b>", "•••••••••••••••••••••••••••••••••••••••••••••••"]
    for code, info in COUNTRY_CODES.items():
        count = fetch_durian_stock_for_country(code)
        pid = get_project_id_for_country(code)
        lines.append(f"{info['flag']} {info['name']} ({code.upper()} - PID:{pid}): {count}")

    bot.delete_message(message.chat.id, loading.message_id)

    chunk = ""
    for line in lines:
        if len(chunk) + len(line) > 3500:
            bot.send_message(message.chat.id, chunk, parse_mode="HTML")
            chunk = ""
        chunk += line + "\n"
    
    if chunk:
        bot.send_message(message.chat.id, chunk, parse_mode="HTML")

# 📲 GET NUMBER
@bot.message_handler(func=lambda msg: "Get Number" in msg.text)
def handle_get_number(message):
    chat_id = message.chat.id
    report = get_user_report(chat_id)

    if report["total_fetched"] >= DAILY_PANEL_LIMIT:
        bot.send_message(chat_id, "⚠️ <b>Daily Limit Reached!</b>", parse_mode="HTML")
        return

    loading = bot.send_message(chat_id, "🔄 <i>Fetching country stock...</i>", parse_mode="HTML")
    markup = generate_country_keyboard_page(page=0)
    bot.delete_message(chat_id, loading.message_id)
    bot.send_message(chat_id, "<b>Select Country:</b>", reply_markup=markup, parse_mode="HTML")

# 🎯 SET SINGLE TARGET HANDLER
@bot.message_handler(func=lambda msg: "Set Target" in msg.text)
def handle_set_target(message):
    msg = bot.send_message(
        message.chat.id,
        "🎯 <b>Enter Country Code & Prefix (Optional):</b>\n\n"
        "<i>Examples:</i>\n"
        "• Normal: <code>it</code> or <code>eg</code>\n"
        "• With Prefix: <code>it 3938</code> or <code>bd 88017</code>",
        parse_mode="HTML"
    )
    bot.register_next_step_handler(msg, process_single_target_input)

def process_single_target_input(message):
    chat_id = message.chat.id
    parts = message.text.strip().lower().split()
    
    if not parts:
        bot.send_message(chat_id, "❌ Invalid input!")
        return
        
    code = parts[0]
    prefix = parts[1] if len(parts) > 1 else ""
    start_target_for_country(chat_id, code, prefix)

# 🎯 BULK TARGET HANDLER
@bot.message_handler(func=lambda msg: "Bulk Target" in msg.text)
def handle_bulk_target(message):
    msg = bot.send_message(
        message.chat.id,
        "🎯 <b>Enter multiple Countries/Prefixes separated by commas:</b>\n\n"
        "<i>Example: <code>eg, us 1202, it 3938, bd 88017</code></i>",
        parse_mode="HTML"
    )
    bot.register_next_step_handler(msg, process_bulk_target_input)

def process_bulk_target_input(message):
    chat_id = message.chat.id
    raw_inputs = [item.strip() for item in message.text.split(',') if item.strip()]

    if not raw_inputs:
        bot.send_message(chat_id, "❌ No valid country codes found!")
        return

    started_count = 0
    for item in raw_inputs:
        parts = item.lower().split()
        code = parts[0]
        prefix = parts[1] if len(parts) > 1 else ""
        
        if start_target_for_country(chat_id, code, prefix):
            started_count += 1

    if started_count > 0:
        bot.send_message(chat_id, f"✅ Started Bulk Target for <b>{started_count}</b> targets!", parse_mode="HTML")

# ⚙️ GO SETTINGS
@bot.message_handler(func=lambda msg: "Go Settings" in msg.text or "Settings" in msg.text)
def handle_go_settings(message):
    chat_id = message.chat.id
    setting = get_user_setting(chat_id)
    status_icon = "🟢 ON" if setting['checker_on'] else "🔴 OFF"
    toggle_text = "🔴 Turn OFF Checker" if setting['checker_on'] else "🟢 Turn ON Checker"

    text = f"⚙️ <b>Checker Settings</b>\nStatus: <b>{status_icon}</b>"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(toggle_text, callback_data="toggle_checker"))
    bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "toggle_checker")
def callback_toggle_checker(call):
    chat_id = call.message.chat.id
    setting = get_user_setting(chat_id)
    setting['checker_on'] = not setting['checker_on']
    status_icon = "🟢 ON" if setting['checker_on'] else "🔴 OFF"
    toggle_text = "🔴 Turn OFF Checker" if setting['checker_on'] else "🟢 Turn ON Checker"

    text = f"⚙️ <b>Checker Settings</b>\nStatus: <b>{status_icon}</b>"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(toggle_text, callback_data="toggle_checker"))
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=text, parse_mode="HTML", reply_markup=markup)

# 🎯 TARGET CONTROLS & GET NUMBER CALLBACKS
def start_target_for_country(chat_id, code, prefix=""):
    if code in COUNTRY_CODES or len(code) == 2:
        c_info = COUNTRY_CODES.get(code, {"name": code.upper(), "flag": "🌐"})
        prefix_info = f" [Prefix: {prefix}]" if prefix else ""
        pid = get_project_id_for_country(code)

        text = (
            f"🚀 <b>Target Running ({code.upper()}{prefix_info})</b>\n"
            f"•••••••••••••••••••••••••••••••••••••••••••••••\n"
            f"{c_info['flag']} <b>{c_info['name']}</b> (PID: {pid})\n"
            f"📡 <b>Requests:</b> 0 | ✅ <b>Got:</b> 0\n"
            f"🔍 <b>Checked:</b> 0\n"
            f"🔄 <b>Running...</b>"
        )

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("⏸️ Pause", callback_data=f"tgt_pause_{code}"),
            InlineKeyboardButton("⏹️ Stop", callback_data=f"tgt_stop_{code}")
        )

        sent_msg = bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)

        if chat_id not in target_workers:
            target_workers[chat_id] = {}

        target_workers[chat_id][code] = {
            'status': 'running',
            'requests': 0,
            'got': 0,
            'checked': 0,
            'prefix': prefix
        }

        threading.Thread(target=run_target_loop, args=(chat_id, sent_msg.message_id, code, prefix)).start()
        return True
    return False

@bot.callback_query_handler(func=lambda call: True)
def handle_all_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data

    if data == "noop":
        bot.answer_callback_query(call.id)
        return

    if data.startswith("page_"):
        page_num = int(data.split("_")[1])
        new_markup = generate_country_keyboard_page(page=page_num)
        try:
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=new_markup)
        except Exception:
            pass
        bot.answer_callback_query(call.id)
        return

    if data.startswith("tgt_pause_") or data.startswith("tgt_stop_"):
        parts = data.split("_")
        action = parts[1]
        code = parts[2]

        if chat_id in target_workers and code in target_workers[chat_id]:
            worker = target_workers[chat_id][code]
            c_info = COUNTRY_CODES.get(code, {"name": code.upper(), "flag": "🌐"})

            if action == "pause":
                worker['status'] = 'paused' if worker['status'] == 'running' else 'running'
                bot.answer_callback_query(call.id, text=f"Target {code.upper()} Toggled")
            elif action == "stop":
                worker['status'] = 'stopped'
                bot.answer_callback_query(call.id, text=f"Target {code.upper()} Stopped")
                stopped_text = (
                    f"🛑 <b>Target Stopped ({code.upper()})</b>\n"
                    f"•••••••••••••••••••••••••••••••••••••••••••••••\n"
                    f"{c_info['flag']} <b>{c_info['name']}</b>\n"
                    f"📡 <b>Total Requests:</b> {worker['requests']} | ✅ <b>Got:</b> {worker['got']}"
                )
                bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=stopped_text, parse_mode="HTML")

    elif data.startswith("get_"):
        code = data.split("_")[1]
        c_info = COUNTRY_CODES.get(code, {"name": code.upper(), "flag": "🌐"})
        bot.answer_callback_query(call.id, text=f"🚀 Auto Target Started for {c_info['name']}...")
        start_target_for_country(chat_id, code, prefix="")

# 📈 DAILY REPORT
@bot.message_handler(func=lambda msg: "Daily Report" in msg.text)
def handle_daily_report(message):
    chat_id = message.chat.id
    report = get_user_report(chat_id)
    total = report["total_fetched"]
    fresh = report["fresh_counts"]
    otp = report["otp_received"]
    rem = DAILY_PANEL_LIMIT - total
    rate = (otp / total * 100) if total > 0 else 0.0

    rep_msg = (
        f"📊 <b>Today's Performance</b>\n"
        f"••••••••••••••••••••••••••••••••••••\n"
        f"• <b>Total Numbers Fetched:</b> {total} / {DAILY_PANEL_LIMIT}\n"
        f"• <b>Fresh Counts:</b> {fresh}\n"
        f"• <b>OTP Received:</b> {otp}\n"
        f"• <b>Success Rate:</b> {rate:.1f}%\n"
        f"••••••••••••••••••••••••••••••••••••\n"
        f"⚠️ <b>Remaining Limit:</b> {rem}"
    )
    bot.send_message(chat_id, rep_msg, parse_mode="HTML")

# 🚀 RUN BOT
if __name__ == "__main__":
    print(f"🤖 Bot @{BOT_USERNAME} Running with Updated Project 6003 Countries (eg, us, do, gt, ru, tr, ve, it)...")
    try:
        bot.remove_webhook()
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print(f"Polling Exception: {e}")
