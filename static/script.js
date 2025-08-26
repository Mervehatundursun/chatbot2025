// Basit chat arayüzü: fetch ile /chat'i çağırır, chatbox'a mesaj ekler
const chatbox = document.getElementById("chatbox");
const form = document.getElementById("chatform");
const input = document.getElementById("soru");

function addMsg(text, who="bot"){
  const div = document.createElement("div");
  div.className = "message " + who;
  div.textContent = text; // XSS güvenli
  chatbox.appendChild(div);
  chatbox.scrollTop = chatbox.scrollHeight;
}

form.addEventListener("submit", async (e)=>{
  e.preventDefault();
  const q = input.value.trim();
  if(!q){ input.focus(); return; }
  addMsg(q, "user");
  input.value = "";

  try{
    const res = await fetch("/chat", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({question:q})
    });
    const data = await res.json();
    if(data.error){ addMsg("Hata: " + data.error); return; }
    addMsg(data.answer, "bot");
    if(data.redirect){
      addMsg(`Gerekirse ${data.redirect.unit} ile iletişime geçin: ${data.redirect.url}`, "bot");
    }
  }catch(err){
    addMsg("Sunucuya ulaşılamadı.", "bot");
  }
});

window.onload = () => input.focus();
