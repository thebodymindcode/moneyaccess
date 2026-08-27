#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Собирает копию продающей страницы для гитхаба из того же исходника.

Зачем копия, а не переброс. На гитхабе живёт своя цепочка: лид-магнит на гитхабе
ведёт на продающую на гитхабе. Если продающая там переброс, человека дважды
перекидывает и это выглядит как сбой.

Почему поиск при этом не двоится: у копии стоит каноникал на домен и noindex,
поэтому Яндекс и Google считают настоящей только страницу на домене.
"""
import pathlib, re

ZDES = pathlib.Path(__file__).resolve().parent
ISTOCHNIK = ZDES / '_istochnik' / 'stranica.html'
CEL = ZDES / 'index.html'
DOMEN = 'https://thebodymindcode.ru/moneyaccess/'

s = ISTOCHNIK.read_text(encoding='utf-8')

# каноникал ведёт на домен: настоящая страница там
if 'rel="canonical"' not in s:
    raise SystemExit('в исходнике нет каноникала, чинить руками')
s = re.sub(r'<link rel="canonical" href="[^"]*"', '<link rel="canonical" href="%s"' % DOMEN, s)

# копию в поиск не пускаем, ссылки с неё пусть работают
metka = '<meta name="robots" content="noindex, follow">'
if 'name="robots"' in s:
    s = re.sub(r'<meta name="robots"[^>]*>', metka, s)
else:
    s = s.replace('<link rel="canonical"', metka + '\n<link rel="canonical"', 1)

CEL.write_text(s, encoding='utf-8')
print('копия для гитхаба собрана: %d КБ, каноникал на домен, noindex' % (CEL.stat().st_size // 1024))
