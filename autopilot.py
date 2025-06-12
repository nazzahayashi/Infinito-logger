import time
import requests

# ✅ URL del tuo server Replit (modifica qui il dominio con il tuo)
URL = "https://eba7e20c-4363-4259-9b84-34869f8cb57a-00-7xegxqv5vdyy.pike.replit.dev/cpa"

print("🌀 AUTOPILOT INFINITO AVVIATO...")

while True:
    try:
        response = requests.get(URL)
        print(f"[CPA] Stato: {response.status_code}")
    except Exception as e:
        print(f"[ERRORE] {str(e)}")
    
    # 🔁 Attende 15 minuti (900 secondi)
    time.sleep(900)
    