import requests
import random
import string
import telebot
import time
import threading
import json
from flask import Flask, request, render_template_string
from concurrent.futures import ThreadPoolExecutor

# Configuration
BOT_TOKEN = "YOUR BOT_TOKEN" #put your BOT_TOKEN
DATA_FILE = "users.json"
PROXY_SOURCES = [
    "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&timeout=500",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://proxylist.geonode.com/api/proxy-list?limit=100&page=1&sort_by=lastChecked&sort_type=desc&protocols=http"
]
REGISTRATION_INTERVAL = 120  # 2 minutes between registrations
MAX_PROXY_WORKERS = 20
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
]

app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN)
users_lock = threading.Lock()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FaucetEarner Account Generator</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        .gradient-bg {
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        }
        .card-shadow {
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }
    </style>
</head>
<body class="gradient-bg min-h-screen">
    <div class="container mx-auto px-4 py-16">
        <div class="max-w-md mx-auto bg-white rounded-lg card-shadow overflow-hidden">
            <div class="px-6 py-8">
                <div class="text-center mb-8">
                    <img src="https://img.icons8.com/fluency/96/000000/money-bag.png" class="mx-auto h-20 w-20"/>
                    <h1 class="text-3xl font-bold text-gray-800 mt-4">FaucetEarner Generator</h1>
                    <p class="text-gray-600 mt-2">Register to receive automated accounts</p>
                </div>
                
                <form method="POST" class="space-y-6">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">📱 Telegram ID</label>
                        <input type="text" name="telegram_id" required
                            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                            placeholder="123456789">
                    </div>
                    
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">🔑 Referral Code</label>
                        <input type="text" name="referral_code" required
                            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                            placeholder="FAUCET123">
                    </div>
                    
                    <button type="submit" 
                        class="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200">
                        🚀 Start Generation
                    </button>
                </form>
                
                {% if message %}
                <div class="mt-6 p-4 rounded-lg {% if 'Success' in message %}bg-green-50{% else %}bg-red-50{% endif %}">
                    <p class="text-sm {% if 'Success' in message %}text-green-800{% else %}text-red-800{% endif %}">
                        {{ message|safe }}
                    </p>
                </div>
                {% endif %}
            </div>
            
            <div class="bg-gray-50 px-6 py-4 border-t border-gray-200">
                <p class="text-xs text-gray-600 text-center">
                    ℹ️ Get Telegram ID from @userinfobot | Support: @YourSupport
                </p>
            </div>
        </div>
    </div>
</body>
</html>
"""

def load_users():
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            # Initialize proxy tracking if not exists
            data.setdefault("proxy_list", [])
            data.setdefault("current_proxy_index", 0)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {"users": {}, "proxy_list": [], "current_proxy_index": 0}

def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def test_proxy(proxy):
    """Test if proxy works with faucetearner.org"""
    try:
        test_url = "https://faucetearner.org/api.php?act=login"
        response = requests.post(
            test_url,
            json={"username": "test", "password": "test"},
            proxies={'http': f'http://{proxy}', 'https': f'http://{proxy}'},
            timeout=15,
            headers={"User-Agent": random.choice(USER_AGENTS)}
        )
        
        if response.status_code == 200 and "status" in response.json():
            return True
        if "cf-chl-bypass" in response.text:
            return False
    except:
        pass
    return False

def fetch_and_test_proxies():
    """Fetch and test new proxies, maintaining order"""
    proxies = []
    for source in PROXY_SOURCES:
        try:
            response = requests.get(source, timeout=10)
            if response.status_code == 200:
                proxies.extend([p.strip() for p in response.text.splitlines() if p.strip()])
        except:
            continue
    
    # Test proxies in original order
    with ThreadPoolExecutor(max_workers=MAX_PROXY_WORKERS) as executor:
        results = list(executor.map(test_proxy, proxies))
    
    return [p for p, valid in zip(proxies, results) if valid]

def get_next_proxy():
    """Get next proxy in sequential order"""
    data = load_users()
    
    if not data["proxy_list"]:
        # Fetch new proxies if list is empty
        new_proxies = fetch_and_test_proxies()
        if not new_proxies:
            return None
        data["proxy_list"] = new_proxies
        data["current_proxy_index"] = 0
        save_users(data)
    
    # Get current proxy
    proxy = data["proxy_list"][data["current_proxy_index"]]
    
    # Update index for next request
    data["current_proxy_index"] = (data["current_proxy_index"] + 1) % len(data["proxy_list"])
    save_users(data)
    
    return proxy

def register_account(referral_code):
    """Create account using sequential proxies"""
    proxy = get_next_proxy()
    if not proxy:
        return None
    
    try:
        credentials = {
            "username": f"{random_string(6)}_{random.randint(100,999)}",
            "password": random_string(12),
            "email": f"{random_string()}@gmail.com",
            "confirm_password": random_string(12),
            "referrer": referral_code
        }
        
        response = requests.post(
            "https://faucetearner.org/api.php?act=register",
            json=credentials,
            headers={
                "User-Agent": random.choice(USER_AGENTS),
                "Content-Type": "application/json",
                "Origin": "https://faucetearner.org",
                "Referer": "https://faucetearner.org/register.php"
            },
            proxies={'http': f'http://{proxy}', 'https': f'http://{proxy}'},
            timeout=20
        )
        
        if response.json().get("status") == "success":
            return {
                "username": credentials["username"],
                "password": credentials["password"],
                "email": credentials["email"],
                "proxy": proxy
            }
    except:
        pass
    return None

def account_worker(referral_code, telegram_id):
    """Worker thread with sequential proxy usage"""
    while True:
        account = None
        try:
            account = register_account(referral_code)
            if account:
                message = (
                    "🎉 New Account Created!\n\n"
                    f"👤 Username: `{account['username']}`\n"
                    f"🔑 Password: `{account['password']}`\n"
                    f"📧 Email: `{account['email']}`\n"
                    f"🌐 Proxy: `{account['proxy']}`\n"
                    f"🔗 Your Referral: `{referral_code}`"
                )
                bot.send_message(telegram_id, message, parse_mode="Markdown")
                time.sleep(REGISTRATION_INTERVAL)
            else:
                time.sleep(60)
        except Exception as e:
            print(f"Worker error: {str(e)}")
            time.sleep(120)

# Flask routes and other helper functions remain similar to previous version
# with adjustments for sequential proxy usage

@app.route('/', methods=['GET', 'POST'])
def index():
    message = None
    if request.method == 'POST':
        telegram_id = request.form['telegram_id'].strip()
        referral_code = request.form['referral_code'].strip().upper()

        if not telegram_id.isdigit():
            message = "❌ Invalid Telegram ID! Must be numeric."
        else:
            data = load_users()
            if referral_code in data["users"]:
                message = "❌ Referral code already registered!"
            else:
                data["users"][referral_code] = telegram_id
                save_users(data)
                threading.Thread(target=account_worker, args=(referral_code, telegram_id), daemon=True).start()
                message = f"""
                    ✅ Registration Successful!<br><br>
                    ▫️ Telegram ID: {telegram_id}<br>
                    ▫️ Referral Code: {referral_code}<br><br>
                    Accounts will be created sequentially with different proxies.
                """

    return render_template_string(HTML_TEMPLATE, message=message)

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def start_services():
    data = load_users()
    for referral_code, telegram_id in data["users"].items():
        threading.Thread(target=account_worker, args=(referral_code, telegram_id), daemon=True).start()

if __name__ == '__main__':
    start_services()
    app.run(host='0.0.0.0', port=5000)
  # use paid proxy to avoid bloking.
