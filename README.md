<h1 align="center">
  ⚡ RDPX-Brute 🔓
</h1>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.x-green?logo=python">
  <img src="https://img.shields.io/badge/status-active-brightgreen">
  <img src="https://img.shields.io/badge/platform-kali--linux-blue?logo=linux">
  <img src="https://img.shields.io/badge/telegram-alerts-enabled-ff69b4?logo=telegram">
</p>

> 🎯 Advanced multi-threaded RDP bruteforcer with Telegram alert integration and live status bar.

---

## 🧠 Features

- 🔎 Auto port scan & RDP version detection (via `nmap`)
- 🧠 Multi-threaded brute-force with dynamic batching
- 🎛️ Wordlist + userlist support (custom or default)
- 🚨 Telegram alerts when valid credentials are found
- 📊 Live progress bar (with `tqdm`)
- 🎨 Hacker-style CLI (Colorama + PyFiglet)

---

## 🚀 Installation

Clone the repo:

```bash
git clone https://github.com/Sbinroot/RDPX-Brute-Telegram-Alerts.git
cd RDPX-Brute-Telegram-Alerts

Install dependencies:

sudo apt install nmap hydra python3-pip -y
pip3 install -r requirements.txt

Required Python modules:

pip3 install colorama tqdm pyfiglet requests

⚙️ Configuration

Open the script (RDPX.py) and set your Telegram bot token and chat ID:

TELEGRAM_BOT_TOKEN = "your_bot_token_here"
TELEGRAM_CHAT_ID = "your_chat_id_here"

    🛠 Create a bot and get your chat ID via @userinfobot or this guide.

🧪 Usage
Bruteforce a single user:

python3 RDPX.py 192.168.1.100 --user Administrator --dict rockyou.txt --threads 20

Bruteforce with userlist:

python3 RDPX.py 192.168.1.100 --userdict usernames.txt --dict passwords.txt --threads 30

⚠️ Disclaimer

    🛡️ Ethical Use Only — This tool is built for authorized penetration testing, red team simulations, or personal lab research only.
    🔥 Never use on targets you don’t own or have explicit permission to test.

👨‍💻 Author

    🔗 github.com/Sbinroot

    ✉️ Powered by a passion for 🔐 cybersecurity and automation.
