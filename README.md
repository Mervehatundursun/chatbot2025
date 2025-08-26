Üniversite Chatbot (Flask) – Öğrenci İşleri Yönlendirme

Bu proje, öğrencilerin sık sorularına yanıt veren ve güven düşükse/anahtar kelime tetiklenirse kullanıcıyı Öğrenci İşleri birimine yönlendiren basit bir chatbot uygulamasıdır.
Arayüz tek sayfadır; arka uç Flask ile REST endpoint sağlar. Yönetim panelinden SSS (FAQ) verileri düzenlenebilir.

Özellikler

✅ Tek sayfa arayüz (HTML + JS)

✅ Flask arka uç: POST /chat, GET /health, GET /admin

✅ SSS verisi: faq.json (UTF‑8, TR karakter desteği)

✅ Basit benzerlik puanı (SequenceMatcher + Jaccard)

✅ Düşük güven veya tetikleyici kelimelerde Öğrenci İşleri yönlendirmesi

✅ Yönetim paneli ile SSS ekleme/silme

✅ Loglama (CSV): kullanıcı sorusu, cevap, skor

Mimari
chatbot/
├─ app.py                 # Flask uygulaması ve endpoint’ler
├─ faq.json               # SSS veritabanı (soru=key, cevap=value)
├─ logs/
│  └─ messages.csv        # Log (otomatik oluşur)
├─ static/
│  └─ script.js           # fetch ile /chat çağrısı, sohbet arayüzü
└─ templates/
   ├─ index.html          # sohbet arayüzü
   └─ admin.html          # SSS yönetim paneli

Kurulum
Python 3.10+ önerilir. Windows PowerShell örneği aşağıda.
cd D:\staj2025
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r .\chatbot\requirements.txt
# (Hata olursa minimum için: pip install flask)
Ortam Değişkeni
Yönetim paneli işlemleri için admin anahtarı:
$env:ADMIN_TOKEN = "ktu123"

Çalıştırma
python .\chatbot\app.py


Sohbet: http://127.0.0.1:5000

Sağlık: http://127.0.0.1:5000/health
 → {"status":"ok"}

Yönetim: http://127.0.0.1:5000/admin
 (Token: ktu123)

API
POST /chat

Body (JSON):

{"question": "Transkriptimi nereden alırım?"}


Response (JSON):

{
  "answer": "OBS > Transkript menüsünden indirebilirsiniz...",
  "confidence": 0.73,
  "source": "faq",
  "redirect": {
    "unit": "Öğrenci İşleri",
    "url": "mailto:ogrenciisleri@universite.edu.tr"
  }
}

GET /health

Servis durum kontrolü, {"status":"ok"} döner.

SSS Verisini Güncelleme

Yer: chatbot/faq.json

Format:

{
  "Öğrenci belgesi nasıl alınır?": "E-Devlet veya OBS > Belgeler menüsünden...",
  "Transkriptimi nereden indirebilirim?": "OBS > Transkript menüsünden..."
}


Yönetim Paneli: /admin sayfasından Ekle/Sil yapabilirsiniz (Token gerekir).

Loglama

Yer: chatbot/logs/messages.csv

Alanlar: zaman damgası, soru, cevap, skor

Bu dosya staj raporunda “analitik” olarak kullanılabilir (en çok sorulanlar vb.).

Güvenlik Notları

ADMIN_TOKEN kodda sabit değil, ortam değişkeninden okunur.

Arayüzde kullanıcı metni textContent ile yazdırılır (XSS’e karşı güvenli).

Yönlendirme tetikleyicileri (örn. “kayıt dondurma”, “itiraz”, “disiplin”, “mezuniyet”, “askerlik”, “yatay geçiş”) otomatik mail linki gösterir.

Üretim ortamı için WSGI (gunicorn/uwsgi) ve ters proxy (Nginx) önerilir.

Ekran Görüntüleri (örnek)

docs/screens/health.png – /health çıktısı

docs/screens/chat.png – sohbet arayüzü

docs/screens/admin.png – yönetim paneli

İpucu: Bu görselleri repo’ya eklersen README’de ![başlık](dosya-yolu) ile gösterebilirsin.

Geliştirme Yol Haritası (opsiyonel)

 Eşleştirmeyi RapidFuzz/TF‑IDF ile iyileştirme

 Çok dilli (TR/EN) destek

 Admin için yetkilendirme/oturum

 Dockerfile + Nginx dağıtım

 Basit metrik sayfası (top sorular, yönlendirme oranı)

Katkı / Lisans

PR’lar memnuniyetle. Lisans: MIT (isterseniz ekleyin).

Küçük temizlik (öneri)

.gitignore içine şunları yazıp takipten çıkar (Desktop’ta dosyaya sağ tık → Ignore):

.idea/
.vs/
__pycache__/
*.pyc
.venv/
logs/*.csv
logs/*.txt

