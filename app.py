from flask import Flask, request, jsonify, render_template, redirect, url_for
from datetime import datetime
from difflib import SequenceMatcher
import os, csv, re, json

app = Flask(__name__)

# -----------------------------
# Yardımcı fonksiyonlar
# -----------------------------
TR_MAP = str.maketrans({
    "ç": "c", "ğ": "g", "ı": "i", "ö": "o", "ş": "s", "ü": "u",
    "Ç": "c", "Ğ": "g", "İ": "i", "I": "i", "Ö": "o", "Ş": "s", "Ü": "u"
})

def normalize(text: str) -> str:
    text = text.lower().translate(TR_MAP)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

# -----------------------------
# Yollar / Dosyalar
# -----------------------------
BASE_DIR = os.path.dirname(__file__)
FAQ_PATH = os.path.join(BASE_DIR, "faq.json")

with open(FAQ_PATH, "r", encoding="utf-8") as fp:
    faq_data = json.load(fp)

# Log dosyaları
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
CSV_PATH = os.path.join(LOG_DIR, "messages.csv")
if not os.path.exists(CSV_PATH):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as csv_init:
        csv.writer(csv_init).writerow(
            ["timestamp", "user_message", "reply", "needs_redirect"]
        )

# Basit admin anahtarı
ADMIN_TOKEN = "ktu123"

# -----------------------------
# Rotalar
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    raw_msg = data.get("message", "")
    user_msg = normalize(raw_msg)

    # 1) Doğrudan içerme
    response = None
    for keyword, reply in faq_data.items():
        if normalize(keyword) in user_msg:
            response = reply
            break

    # 2) Benzerlik (eşik = 0.75)
    if not response:
        best_key, best_score = None, 0.0
        for keyword in faq_data.keys():
            score = similarity(user_msg, normalize(keyword))
            if score > best_score:
                best_key, best_score = keyword, score
        if best_score >= 0.75:
            response = faq_data[best_key]

    # 3) Varsayılan
    if not response:
        response = "Bu konuyu anlayamadım, Öğrenci İşlerine danışman faydalı olabilir."

    # Loglama
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    needs_redirect = any(k in response.lower() for k in ["öğrenci", "danışman", "obs", "yönlendir"])
    flag = " *** YÖNLENDİRME GEREKİYOR ***" if needs_redirect else ""

    # TXT log
    txt_path = os.path.join(LOG_DIR, "messages.txt")
    with open(txt_path, "a", encoding="utf-8") as log_fp:
        log_fp.write(f"[{timestamp}]{flag} Kullanıcı: {user_msg} | Cevap: {response}\n")

    # CSV log
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as out_csv:
        csv.writer(out_csv).writerow(
            [timestamp, user_msg, response, "yes" if needs_redirect else "no"]
        )

    return jsonify({"reply": response})

# -----------------------------
# Admin Paneli
# -----------------------------
@app.route("/admin", methods=["GET"])
def admin_form():
    # Türkçe karakterler bozulmadan görünsün diye JSON'u burada biçimlendiriyoruz
    faq_json = json.dumps(faq_data, indent=2, ensure_ascii=False)
    return render_template("admin.html", faq_json=faq_json)

@app.route("/admin/add", methods=["POST"])
def admin_add():
    token = request.form.get("token", "")
    if token != ADMIN_TOKEN:
        return "Yetkisiz erişim", 403

    q = request.form.get("question", "").strip()
    a = request.form.get("answer", "").strip()
    if not q or not a:
        return "Soru ve cevap zorunludur", 400

    # Bellekte güncelle ve diske yaz
    faq_data[q] = a
    content = json.dumps(faq_data, ensure_ascii=False, indent=2)
    with open(FAQ_PATH, "w", encoding="utf-8") as faq_out:
        faq_out.write(content)

    return redirect(url_for("admin_form"))

@app.route("/admin/delete", methods=["POST"])
def admin_delete():
    token = request.form.get("token", "")
    if token != ADMIN_TOKEN:
        return "Yetkisiz erişim", 403

    q = request.form.get("question", "").strip()
    if q in faq_data:
        faq_data.pop(q)
        content = json.dumps(faq_data, ensure_ascii=False, indent=2)
        with open(FAQ_PATH, "w", encoding="utf-8") as faq_out:
            faq_out.write(content)

    return redirect(url_for("admin_form"))

# -----------------------------
# Çalıştır
# -----------------------------
if __name__ == "__main__":
    # Rotalar yüklendi mi görmek istersen:
    print(app.url_map)
    app.run(debug=True)
