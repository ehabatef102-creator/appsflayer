import os
import time
import json
import random
import string
import threading
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

CONFIG_FILE = "config.json"

GAMES_DATA = [
    {"name": "Zombie Waves", "package": "com.ddup.zombiewaves.zw", "dev_key": "wiQMRPvGaAYTGBCgM5yN9N", "template": "af_zw_lv_{}"},
    {"name": "Board Adventure", "package": "com.moonactive.cmboard", "dev_key": "H3KjoCRVTiVgA5mWSAHtCe", "template": "village_{}_complete"},
    {"name": "Color Sort Woody Puzzle", "package": "games.burny.color.sort.woody.puzzle", "dev_key": "CkyYk6ThNSr9MPEvmCNZRN", "template": "level_completed"},
    {"name": "Wooden Word Puzzle", "package": "games.burny.wooden.word.puzzle", "dev_key": "CkyYk6ThNSr9MPEvmCNZRN", "template": "level_completed_{}"},
    {"name": "Associations Word Puzzle", "package": "games.burny.associations.word.puzzle", "dev_key": "CkyYk6ThNSr9MPEvmCNZRN", "template": "level_completed_{}"},
    {"name": "Coin Master", "package": "com.moonactive.coinmaster", "dev_key": "H3KjoCRVTiVgA5mWSAHtCe", "template": "village_{}_complete"},
    {"name": "Domino Dreams", "package": "com.screenshake.dominodreams", "dev_key": "Hn5qYjVAaRNJYDcwF4LaWF", "template": "af_area_{}_completed"},
    {"name": "Solitaire Grand Harvest", "package": "net.supertreat.solitaire", "dev_key": "X8aGgdWELNb5L96fCy44oL", "template": "level_up_{}"},
    {"name": "Cuisine Master", "package": "com.FortuneMine.CuisineMaster", "dev_key": "im6mgZbZJsHKGVowkkxkGm", "template": "level{}_completed"},
    {"name": "Match Factory", "package": "net.peakgames.match", "dev_key": "F9M4SkdtH8WHcAt86ESrF3", "template": "level_{}_completed"},
    {"name": "Toon Blast", "package": "net.peakgames.toonblast", "dev_key": "F9M4SkdtH8WHcAt86ESrF3", "template": "level_{}_completed"},
    {"name": "Toy Blast", "package": "net.peakgames.amy", "dev_key": "F9M4SkdtH8WHcAt86ESrF3", "template": "level_{}_completed"},
    {"name": "Box Jam", "package": "com.playoneer.boxjam", "dev_key": "cSJjCEwX2cCtJrNH92xM7n", "template": "level_completed"},
    {"name": "Gardenscapes", "package": "com.playrix.gardenscapes", "dev_key": "ixMH7WQi4SqLAmPWuyAtkH", "template": "AchievedLevel{}"},
    {"name": "Dice Dreams", "package": "com.superplaystudios.dicedreams", "dev_key": "Hn5qYjVAaRNJYDcwF4LaWF", "template": "af_kingdom_{}_restored"},
    {"name": "Taylor's Secret", "package": "com.mergegames.taylorsecret", "dev_key": "qbKVyawAiwNX3b4D3Frijm", "template": "level_{}"},
    {"name": "Big Farm Homestead", "package": "com.newmoonproduction.bigfarmhomestead", "dev_key": "FtaT5WH9rMJjJkMd4LfBCT", "template": "af_level{}_achieved"},
    {"name": "Sunshine Island", "package": "com.newmoonproduction.sunshineisland", "dev_key": "FtaT5WH9rMJjJkMd4LfBCT", "template": "af_level{}_achieved"},
    {"name": "Idle Bank Tycoon", "package": "com.luckyskeletonstudios.idlebanktycoon", "dev_key": "DwzgMQDkEVMy3ntcgz7utV", "template": "af_bank{}_started"},
    {"name": "FarmVille 3", "package": "com.zynga.farmville3", "dev_key": "KVJuxDJVXQRPoqUVdyWJtj", "template": "Player_Level{}"},
    {"name": "Township", "package": "com.playrix.township", "dev_key": "ixMH7WQi4SqLAmPWuyAtkH", "template": "achievedlevel{}"},
    {"name": "Merge Match", "package": "com.futureplay.mergematch", "dev_key": "nr8SibwpFjcKGBQNpDdttd", "template": "Incent_Player_Level_Up_{}"},
    {"name": "FarmVille 2 Country Escape", "package": "com.zynga.FarmVille2CountryEscape", "dev_key": "438VCPmX2ZLYvsDPfGLZXb", "template": "Level{}Complete"},
    {"name": "Merge Studio", "package": "com.paxiegames.mergestudio", "dev_key": "mFaiXvTWy8votzp3UpsSfS", "template": "level_completed_{}"},
    {"name": "Goods Master 3D", "package": "com.goods.master3d.triple.puzzle", "dev_key": "oUYXWsx5SVDbJwtSCCymUD", "template": "af_Level_{}"},
    {"name": "Tiles Mosaic", "package": "com.tripledot.tiles.mosaic", "dev_key": "j7J8eEwxvuQbDDFo3agC9X", "template": "level_reached_{}"},
    {"name": "Bingo Vacation", "package": "com.aemobile.games.bingo.vacation", "dev_key": "NFfcQbKF65HGqDyA3uH5pC", "template": "bingo_reach_level_{}"},
    {"name": "Yarn Loop!", "package": "com.combo.yarnflow", "dev_key": "TGm97uKTJF7qFCvREggWtf", "template": "level_complete_{}"}
]

logs = []

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"device_name": "", "ad_id": "", "selected_game": 0, "status": "Idle"}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def generate_random_af_id():
    p1 = ''.join(random.choices(string.digits, k=13))
    p2 = ''.join(random.choices(string.digits, k=19))
    return f"{p1}-{p2}"

def send_af_event(game, ad_id, event_name):
    import requests
    url = f"https://api2.appsflyer.com/inappevent/{game['package']}"
    headers = {
        "authentication": game['dev_key'], 
        "Content-Type": "application/json"
    }
    af_id = generate_random_af_id()
    payload = {
        "appsflyer_id": af_id,
        "advertising_id": ad_id,
        "eventName": event_name,
        "eventValue": json.dumps({"af_revenue": "0", "af_currency": "USD"}),
        "eventTime": time.strftime("%Y-%m-%d %H:%M:%S.000"),
        "af_events_api": "true"
    }
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        return res.status_code, res.text
    except Exception as e:
        return 0, str(e)

def background_worker():
    while True:
        config = load_config()
        if config.get("status") == "Running":
            ad_id = config.get("ad_id")
            game_idx = config.get("selected_game", 0)
            game = GAMES_DATA[game_idx]
            
            # الخطة الزمنية للمستويات (5، 10، 20، 30، 40، 50) والأزمنة المحددة
            schedule = [
                {"level": 5, "delay": 60},       # بعد دقيقة (60 ثانية)
                {"level": 10, "delay": 86400},   # بعد يوم (24 ساعة)
                {"level": 20, "delay": 172800},  # بعد يومين
                {"level": 30, "delay": 259200},  # بعد 3 أيام
                {"level": 40, "delay": 345600},  # بعد 4 أيام
                {"level": 50, "delay": 432000}   # بعد 5 أيام
            ]
            
            logs.insert(0, f"[*] بدء خطة العمل للجهاز: {config.get('device_name')} واللعبة: {game['name']}")
            
            for item in schedule:
                if load_config().get("status") != "Running":
                    break
                
                delay = item["delay"]
                lv = item["level"]
                
                logs.insert(0, f"⏳ الانتظار المجدول لإرسال لفل {lv} (المدة: {delay} ثانية)...")
                
                elapsed = 0
                while elapsed < delay:
                    if load_config().get("status") != "Running":
                        break
                    time.sleep(1)
                    elapsed += 1
                
                if load_config().get("status") != "Running":
                    break
                
                event_name = game['template'].format(lv) if "{}" in game['template'] else game['template']
                status_code, response_text = send_af_event(game, ad_id, event_name)
                
                log_msg = f"🚀 إرسال لفل {lv} ({event_name}) | الحالة: {status_code} | الرد: {response_text}"
                logs.insert(0, log_msg)
            
            if load_config().get("status") == "Running":
                config["status"] = "Completed"
                save_config(config)
                logs.insert(0, f"✅ اكتملت خطة المستويات بالكامل للجهاز: {config.get('device_name')}")
            
        time.sleep(5)

t = threading.Thread(target=background_worker, daemon=True)
t.start()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pharaoh Pusher - لوحة التحكم الذكية</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --accent-color: #38bdf8;
            --accent-hover: #0ea5e9;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: #334155;
        }
        body {
            font-family: 'Cairo', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 850px;
            margin: 30px auto;
            background: var(--card-bg);
            padding: 35px;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
            border: 1px solid var(--border-color);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: var(--accent-color);
            font-size: 28px;
            margin: 0 0 10px;
        }
        .header p {
            color: var(--text-muted);
            font-size: 14px;
            margin: 0;
        }
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group.full {
            grid-column: span 2;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            font-size: 14px;
            color: var(--text-main);
        }
        input[type="text"], select {
            width: 100%;
            padding: 12px 15px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            background: var(--bg-color);
            color: var(--text-main);
            box-sizing: border-box;
            font-family: 'Cairo', sans-serif;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus, select:focus {
            border-color: var(--accent-color);
            outline: none;
        }
        .btn-container {
            display: flex;
            gap: 15px;
        }
        button {
            flex: 1;
            background: var(--accent-color);
            color: #0f172a;
            border: none;
            padding: 14px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 700;
            font-family: 'Cairo', sans-serif;
            transition: background 0.3s, transform 0.1s;
        }
        button:hover {
            background: var(--accent-hover);
        }
        button:active {
            transform: scale(0.98);
        }
        .stop-btn {
            background: #ef4444;
            color: white;
        }
        .stop-btn:hover {
            background: #dc2626;
        }
        .status-card {
            background: var(--bg-color);
            padding: 15px 20px;
            border-radius: 8px;
            margin-top: 25px;
            border: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .status-badge {
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 700;
        }
        .status-running { background: rgba(74, 222, 128, 0.15); color: #4ade80; }
        .status-stopped { background: rgba(248, 113, 113, 0.15); color: #f87171; }
        .status-completed { background: rgba(56, 189, 248, 0.15); color: #38bdf8; }
        
        .logs-section {
            margin-top: 25px;
        }
        .logs-section h3 {
            font-size: 16px;
            margin-bottom: 10px;
            color: var(--text-muted);
        }
        .logs {
            background: #020617;
            padding: 15px;
            border-radius: 8px;
            height: 220px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 12px;
            color: #4ade80;
            direction: ltr;
            text-align: left;
            border: 1px solid var(--border-color);
        }
        .schedule-info {
            background: rgba(56, 189, 248, 0.05);
            border: 1px dashed var(--accent-color);
            padding: 12px 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 13px;
            color: var(--text-muted);
        }
        .schedule-info strong {
            color: var(--accent-color);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Pharaoh Pusher Cloud</h1>
            <p>لوحة التحكم السحابية التلقائية لإرسال الأحداث والمستويات (24/7)</p>
        </div>

        <div class="schedule-info">
            📌 <strong>خطة المستويات الآلية:</strong> يتم إرسال لفلات <strong>(5، 10، 20، 30، 40، 50)</strong> بجدول زمني تبدأ بـ دقيقة لفل 5، ثم يوم لكل لفل لاحق. أدخل بياناتك مرة واحدة واحفظها لتعمل مع نفسها!
        </div>

        <form method="POST" action="/save">
            <div class="form-grid">
                <div class="form-group">
                    <label>اسم الجهاز (Device Name):</label>
                    <input type="text" name="device_name" value="{{ config.device_name }}" required placeholder="مثال: Phone_A_01">
                </div>
                <div class="form-group">
                    <label>المعرف الإعلاني (GAID):</label>
                    <input type="text" name="ad_id" value="{{ config.ad_id }}" required placeholder="c6239d88-c403-4060-8f8e-a971317cf473">
                </div>
                <div class="form-group full">
                    <label>اختر اللعبة المستهدفة:</label>
                    <select name="selected_game">
                        {% for idx, game in games %}
                        <option value="{{ idx }}" {% if config.selected_game == idx %}selected{% endif %}>{{ game.name }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>

            <div class="btn-container">
                <button type="submit">حفظ وبدء الخطة الزمنية 🚀</button>
            </div>
        </form>

        <form method="POST" action="/stop" style="margin-top: 12px;">
            <div class="btn-container">
                <button type="submit" class="stop-btn">إيقاف النظام مؤقتاً ⏹</button>
            </div>
        </form>

        <div class="status-card">
            <span>حالة التشغيل الحالية:</span>
            <span class="status-badge {% if config.status == 'Running' %}status-running{% elif config.status == 'Completed' %}status-completed{% else %}status-stopped{% endif %}">
                {{ config.status }}
            </span>
        </div>

        <div class="logs-section">
            <h3>سجل العمليات الحية (Live Logs):</h3>
            <div class="logs">
                {% for log in logs %}
                <div>{{ log }}</div>
                {% endfor %}
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    config = load_config()
    return render_template_string(HTML_TEMPLATE, config=config, games=enumerate(GAMES_DATA), logs=logs)

@app.route("/save", methods=["POST"])
def save():
    config = load_config()
    config["device_name"] = request.form.get("device_name")
    config["ad_id"] = request.form.get("ad_id")
    config["selected_game"] = int(request.form.get("selected_game"))
    config["status"] = "Running"
    save_config(config)
    logs.insert(0, f"⚙️ تم حفظ الإعدادات وبدء التشغيل التلقائي للجهاز: {config['device_name']}")
    return redirect(url_for("index"))

@app.route("/stop", methods=["POST"])
def stop():
    config = load_config()
    config["status"] = "Stopped"
    save_config(config)
    logs.insert(0, "🛑 تم إيقاف النظام يدوياً من لوحة التحكم.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)