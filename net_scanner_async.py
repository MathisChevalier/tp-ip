import argparse
import csv
import ipaddress
import platform
import asyncio
import os
import time


async def ping_ip_async(ip):
    """
    Ping une IP de manière asynchrone.
    Retourne (IP, statut, ping_time_ms)
    """
    system = platform.system().lower()
    param = "-n" if system == "windows" else "-c"
    command = ["ping", param, "1", str(ip)]

    try:
        start_time = time.perf_counter()
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        end_time = time.perf_counter()

        if proc.returncode == 0:
            ping_ms = int((end_time - start_time) * 1000)
            return str(ip), "Active", ping_ms
        else:
            return str(ip), "Inactive", ""
    except Exception:
        return str(ip), "Error", ""


async def scan_ips(ip_list):
    """
    Scanne une liste d'IPs de manière asynchrone
    """
    tasks = [ping_ip_async(ip) for ip in ip_list]
    return await asyncio.gather(*tasks)


def get_ip_list_from_range(ip_range):
    """
    Retourne une liste d'IPs depuis une plage CIDR
    """
    return list(ipaddress.ip_network(ip_range, strict=False))


def get_ip_list_from_file(file_path):
    """
    Retourne une liste d'IPs depuis un fichier
    """
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def save_to_csv(results, filename=None):
    """
    Sauvegarde les résultats dans un fichier CSV en UTF-8
    """
    if filename is None:
        filename = r"C:\Users\mathi\Documents\Roussille\results.csv"
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["IP", "Status", "Ping (ms)"])
        writer.writerows(results)
    print(f"\n✅ Résultats sauvegardés dans : {filename}")


def main():
    parser = argparse.ArgumentParser(description="Scanner IP Asynchrone")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--range", help="Plage CIDR à scanner (ex: 192.168.1.0/24)")
    group.add_argument("--file", help="Fichier contenant des IPs")
    args = parser.parse_args()

    if args.range:
        ip_list = get_ip_list_from_range(args.range)
    else:
        ip_list = get_ip_list_from_file(args.file)

    print(f"🔍 Lancement du scan de {len(ip_list)} IPs...\n")

    results = asyncio.run(scan_ips(ip_list))

    for ip, status, ping in results:
        print(f"{ip} {status}" + (f" (Ping: {ping}ms)" if ping != "" else ""))

    save_to_csv(results)


if __name__ == "__main__":
    main()
