from flask import Flask, request, jsonify, render_template, redirect, url_for
from datetime import datetime
from difflib import SequenceMatcher
import os, csv, re, json

app = Flask(__name__)

# -----------------------------
# Ayarlar ve yol sabitleri
# -----------------------------
BASE_DIR = os.path.dirname(__file__)
FAQ_PATH = os.path.join(BASE_DIR, "faq.json")
LOG_DIR = os.path.join(BASE_DIR, "logs")
CSV_PATH = os.path.join(LOG_DIR, "messages.csv")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "change-me")  # Güvenlik: .env veya deployment ortamından gelsin

# -----------------------------
# Yardımcı fonksiyonlar
# -----------------------------
TR_MAP = str.maketrans({
    "ç": "c", "ğ": "g", "ı": "i", "ö": "o", "ş": "s", "ü": "u",
    "Ç": "c", "Ğ": "g", "İ": "i", "I": "i", "Ö": "o", "Ş": "s", "Ü": "u"
})

def normalize(t: str) -> str:
    t = (t or "").translate(TR_MAP).lower()
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def load_faq():
    if not os.path.exists(FAQ_PATH):
        return {}
    with open(FAQ_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def best_match(question: str, data):
    qn = normalize(question)
    best_a, best_score, best_key = "", 0.0, ""
    # destek: hem exact anahtar eşleşme hem text benzerlik
    for key, ans in data.items():
        kn = normalize(key)
        # karışık metin benzerlik + kelime kümeleri jaccard
        sm = SequenceMatcher(None, qn, kn).ratio()
        tokens_q = set(qn.split())
        tokens_k = set(kn.split())
        jac = len(tokens_q & tokens_k) / max(1, len(tokens_q | tokens_k))
        score = 0.7 * sm + 0.3 * jac
        if score > best_score:
            best_score, best_a, best_key = score, ans, key
    return best_a, float(best_score), best_key

def ensure_logdir():
    os.makedirs(LOG_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["ts", "question", "answer", "score"])

def log_message(user_q, bot_a, score):
    ensure_logdir()
    with open(CSV_PATH, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([datetime.now().isoformat(timespec="seconds"), user_q, bot_a, f"{score:.3f}"])

# -----------------------------
# Yönlendirme anahtar kelimeleri
# -----------------------------
REDIRECT = {
    "unit": "Öğrenci İşleri",
    "url": "mailto:ogrenciisleri@universite.edu.tr",
    "triggers": {"dondurma","itiraz","disiplin","kayıt silme","belge onay","askerlik","mezuniyet","yatay geçiş"}
}

def should_redirect(question: str) -> bool:
    qn = normalize(question)
    return any(normalize(t) in qn for t in REDIRECT["triggers"])

# -----------------------------
# Rotalar
# -----------------------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status":"ok"})

@app.route("/chat", methods=["POST"])
def chat():
    data = load_faq()
    q = (request.json.get("question") if request.is_json else request.form.get("soru", "")).strip()
    if not q:
        return jsonify({"error":"Boş soru"}), 400
    ans, score, key = best_match(q, data)
    src = "faq" if score >= 0.55 else "fallback"
    if not ans:
        ans = "Sorunuzu Öğrenci İşlerine yönlendirebilirim."
    response = {"answer": ans, "confidence": round(score,3), "source": src}
    if score < 0.55 or should_redirect(q):
        response["redirect"] = {"unit": REDIRECT["unit"], "url": REDIRECT["url"]}
    log_message(q, ans, score)
    return jsonify(response)

@app.route("/admin", methods=["GET"])
def admin_form():
    faq_data = load_faq()
    faq_json = json.dumps(faq_data, indent=2, ensure_ascii=False)
    return render_template("admin.html", faq_json=faq_json)

@app.route("/admin/add", methods=["POST"])
def admin_add():
    if request.form.get("token","") != ADMIN_TOKEN:
        return "Yetkisiz erişim", 403
    q = request.form.get("question","").strip()
    a = request.form.get("answer","").strip()
    if not q or not a:
        return redirect(url_for("admin_form"))
    faq_data = load_faq()
    faq_data[q] = a
    with open(FAQ_PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(faq_data, ensure_ascii=False, indent=2))
    return redirect(url_for("admin_form"))

@app.route("/admin/delete", methods=["POST"])
def admin_delete():
    if request.form.get("token","") != ADMIN_TOKEN:
        return "Yetkisiz erişim", 403
    q = request.form.get("question","").strip()
    if q:
        faq_data = load_faq()
        faq_data.pop(q, None)
        with open(FAQ_PATH, "w", encoding="utf-8") as f:
            f.write(json.dumps(faq_data, ensure_ascii=False, indent=2))
    return redirect(url_for("admin_form"))

# -----------------------------
# Çalıştır
# -----------------------------
if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)
