from flask import Flask, request
import requests
from datetime import datetime
import os
import json
import random

app = Flask(__name__)

# ✅ LINK ATTIVI GUMROAD (o qualsiasi altro link da monitorare)
links = [
    "https://nazzahayashi.gumroad.com/l/dionar",
    "https://nazzahayashi.gumroad.com/l/azmny",
]

# ✅ FILE E BUFFER
log_buffer = []
STATS_FILE = "link_stats.json"
CLICK_VALIDI_FILE = "click_validi.csv"
STATUS_LOG_FILE = "status_log.txt"

# ✅ CARICA STATISTICHE
def load_stats():
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    return {url: {"success": 0, "error": 0} for url in links}

# ✅ SALVA STATISTICHE
def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

# ✅ AGGIORNA CONTATORI
def update_stats(url, status):
    stats = load_stats()
    if url not in stats:
        stats[url] = {"success": 0, "error": 0}
    if status == 200:
        stats[url]["success"] += 1
    else:
        stats[url]["error"] += 1
    save_stats(stats)

# ✅ LOG IN MEMORIA E SU FILE
def save_to_memory_log(timestamp, url, status, latency=None):
    entry = f"{timestamp} - {url} - STATUS: {status}"
    if latency:
        entry += f" - LATENZA: {latency:.2f}s"
    log_buffer.append(entry)
    with open(STATUS_LOG_FILE, "a") as f:
        f.write(entry + "\n")
    if len(log_buffer) > 100:
        log_buffer.pop(0)

# ✅ CONTROLLO MANUALE DEI LINK ATTIVI
def check_links():
    results = []
    for url in links:
        try:
            start_time = datetime.now()
            resp = requests.get(url, timeout=10)
            latency = (datetime.now() - start_time).total_seconds()
            results.append((url, resp.status_code, latency))
        except Exception:
            results.append((url, "ERROR", None))
    return results

# ✅ SALVATAGGIO CLICKS VALIDI
def salva_click_valido(timestamp, url, status, latency):
    if status == 200 and latency and latency < 2.0:
        with open(CLICK_VALIDI_FILE, "a") as f:
            f.write(f"{timestamp},{url},{status},{latency:.2f}\n")
        stats = load_stats()
        if stats[url]["success"] >= 5:
            print(f"🔥 POSSIBILE CONVERSIONE PER: {url}")

# ✅ CARICAMENTO LINK CPA DA FILE JSON
def load_cpa_links():
    try:
        with open("cpa_links.json", "r") as f:
            return json.load(f)
    except Exception as e:
        save_to_memory_log(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "CPA", f"ERRORE LETTURA FILE: {str(e)}")
        return []

# ✅ ESECUZIONE CPA
def execute_cpa():
    links = load_cpa_links()
    if not links:
        save_to_memory_log(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "CPA", "NESSUN LINK")
        return
    url = random.choice(links)
    try:
        start = datetime.now()
        resp = requests.get(url, timeout=10)
        latency = (datetime.now() - start).total_seconds()
        save_to_memory_log(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), url, resp.status_code, latency)
    except Exception as e:
        save_to_memory_log(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), url, f"ERRORE: {str(e)}")

# === ENDPOINTS FLASK ===

@app.route('/')
def home():
    return '✅ INFINITO LOGGER è attivo e pronto!'

@app.route('/check')
def run_check():
    data = check_links()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("log_click.csv", "a") as f:
        for u, s, l in data:
            f.write(f"{now},{u},{s},{l}\n")
            save_to_memory_log(now, u, s, l)
            update_stats(u, s)
            salva_click_valido(now, u, s, l)
    return '✅ Controllo completato e salvato in log_click.csv'

@app.route('/cpa')
def run_cpa():
    execute_cpa()
    return '✅ CPA eseguito.'

@app.route('/log')
def view_log():
    try:
        with open("status_log.txt", "r") as f:
            lines = f.readlines()[-50:]  # Mostra solo gli ultimi 50
            return "<br>".join(line.strip() for line in lines)
    except FileNotFoundError:
        return "⚠️ Nessun log ancora disponibile."

@app.route('/status', methods=["POST"])
def status_post():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = request.json or {}
    msg = data.get("msg", "Nessun messaggio")
    with open("external_status_log.csv", "a") as f:
        f.write(f"{now},EXTERNAL_STATUS,{msg}\n")
    save_to_memory_log(now, "EXTERNAL", msg)
    return '✅ Status ricevuto e loggato'

@app.route('/status', methods=["GET"])
def status_get():
    return "<br>".join(log_buffer[-5:])

@app.route('/stats')
def view_stats():
    stats = load_stats()
    return json.dumps(stats, indent=2)

# ✅ AVVIO SERVER
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
