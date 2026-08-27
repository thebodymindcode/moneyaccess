#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кладёт продающую страницу «Протокола денег» на свой домен, в /protokol/.

Зачем. Страница живёт на гитхабе, и письма ведут людей туда. Чужой домен в ссылке
это минус к доверию у почтовых фильтров и потерянная польза для поиска: страницу
на своём домене видит Яндекс и Google как часть сайта.

Гитхаб остаётся живым, ничего не ломается: просто у страницы появляется второй,
основной адрес https://thebodymindcode.ru/protokol/

Запуск:
    python3 ~/moneyaccess/zalit_na_domen.py
"""
import ftplib
import pathlib
import sys
import urllib.request

ZDES = pathlib.Path(__file__).resolve().parent
DOSTUP = pathlib.Path.home() / ".business/sites/.beget_ftp_tbc"
PAPKA = "/protokol"
SAJT = "https://thebodymindcode.ru"

# страница и всё, что она грузит рядом с собой
FAJLY = ["index.html", "og-cover (1).jpg", "app-desktop.webp", "app-map.webp",
         "app-progress.webp", "favicon.ico", "favicon-32.png", "favicon-512.png",
         "apple-touch-icon.png", "404.html"]


def main():
    cfg = dict(l.strip().split("=", 1) for l in DOSTUP.read_text().splitlines()
               if "=" in l and not l.startswith("#"))
    koren = cfg["root"].rstrip("/") + PAPKA

    ftp = ftplib.FTP(cfg["host"], cfg["user"], cfg["pass"], timeout=120)
    ftp.set_pasv(True)
    try:
        ftp.mkd(koren)
    except ftplib.error_perm:
        pass

    horosho, plohо = 0, 0
    for imya in FAJLY:
        mestno = ZDES / imya
        if not mestno.is_file():
            print(f"нет файла: {imya}")
            continue
        cel = f"{koren}/{imya}"
        with mestno.open("rb") as fh:
            ftp.storbinary("STOR " + cel, fh)
        # Beget умеет ответить «ок» на пустую заливку, поэтому сверяем размер
        na_servere = ftp.size(cel)
        if na_servere == mestno.stat().st_size:
            print(f"ok  {imya:<26} {na_servere} б")
            horosho += 1
        else:
            print(f"ПЛОХО {imya}: локально {mestno.stat().st_size}, на сервере {na_servere}")
            plohо += 1
    ftp.quit()

    print(f"\nзалито {horosho}, с ошибкой {plohо}")

    # живая проверка: страница обязана отвечать 200 и содержать платёжные ссылки
    try:
        with urllib.request.urlopen(f"{SAJT}{PAPKA}/", timeout=30) as r:
            telo = r.read().decode("utf-8", "replace")
            kod = r.status
    except Exception as e:
        sys.exit(f"🚫 страница не открылась: {e}")
    est_oplata = "payform.ru" in telo
    est_data = "1 сентября" in telo
    print(f"{SAJT}{PAPKA}/ отвечает {kod}, оплата на месте: {est_oplata}, дата на месте: {est_data}")
    if not (kod == 200 and est_oplata and est_data):
        sys.exit("🚫 страница залилась криво, письма туда вести нельзя")
    print("✅ страница живая")


if __name__ == "__main__":
    main()
