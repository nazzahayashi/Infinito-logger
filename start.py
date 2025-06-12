import subprocess

# Avvia main.py (il server Flask)
subprocess.Popen(["python3", "main.py"])

# Avvia autopilot.py (il CPA automatico)
subprocess.Popen(["python3", "autopilot.py"])
