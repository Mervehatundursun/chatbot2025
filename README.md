Flask Chatbot | Öğrenci Yönlendirme Sistemi

Bu proje, öğrenci sorularını anlayarak cevaplayan ve gerektiğinde Öğrenci İşleri birimine yönlendiren basit bir chatbot uygulamasıdır.

 Özellikler

- Kullanıcı arayüzü (HTML tabanlı chat ekranı)
- Flask ile yazılmış backend
- Soru–cevap verileri `faq.json` dosyasında tutulur
- Anahtar kelimeye göre otomatik yönlendirme yapar

Proje Yapısı
chatbot/
├── app.py # Flask uygulaması
├── faq.json # Soru-cevap verisi
├── templates/
│ └── index.html # Chat arayüzü

Nasıl Çalıştırılır?
1. Flask kurulu değilse:
   pip install flask
2.Terminalde projeyi başlat:
   python app.py
3.Tarayıcıda şu adrese git:
   http://127.0.0.1:5000/
      

