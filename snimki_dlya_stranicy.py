#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Свежие снимки кабинета для продающей страницы «Протокол денег».

Заводит одноразового участника с прогрессом, снимает нужные экраны в тех же
размерах, что уже стоят на странице, и убирает его за собой.
Служебный адрес на кадрах не показываем: в подписи участника стоит понятный пример.
"""
import datetime, pathlib, sys
sys.path.insert(0, str(pathlib.Path.home() / 'moneyprogram2/_test'))
from tester import KABINETY, klyuch, sluzhebnyy, vojti, otkryt_den, zapolnit_den
from playwright.sync_api import sync_playwright
from PIL import Image

ADRES, PAPKA = KABINETY['boevoy']
OUT = pathlib.Path.home() / 'moneyaccess'
TEL = (660, 1428)      # как на странице сейчас
PK = (1280, 800)

m = datetime.datetime.now().strftime('%m%d%H%M%S')
POCHTA, PAROL = 'test-lend%s@proverka.local' % m, 'Lend-%s' % m
START = (datetime.date.today() - datetime.timedelta(days=6)).isoformat()
kl = klyuch(PAPKA)


def demo(page):
    page.evaluate("""()=>{const e=document.querySelector('.sb-user .who .e');
      if (e) e.textContent='maria@pochta.ru';}""")
    page.wait_for_timeout(150)


def v_razdel(page, hash_):
    page.goto(ADRES + hash_, wait_until='domcontentloaded')
    page.wait_for_timeout(2600)


def snyat(page, imya, razmer):
    put = OUT / (imya + '.png')
    page.screenshot(path=str(put))
    im = Image.open(put).convert('RGB')
    im = im.resize(razmer, Image.LANCZOS)
    im.save(OUT / (imya + '.webp'), quality=88, method=6)
    put.unlink()
    print('  %-16s %d КБ' % (imya + '.webp', (OUT / (imya + '.webp')).stat().st_size // 1024))


print('завожу участника для съёмки')
sluzhebnyy(ADRES, kl, POCHTA, 'zavesti', imya='Мария', parol=PAROL, start=START)
try:
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        # наполняем шесть дней, чтобы экраны были живыми
        ctx = br.new_context(viewport={'width': 1280, 'height': 900})
        pg = ctx.new_page(); vojti(pg, ADRES, POCHTA, PAROL, '.sidebar')
        for n in range(1, 7):
            if otkryt_den(pg, n):
                zapolnit_den(pg, n)
        print('шесть дней заполнены')
        ctx.close()

        # телефон
        ctx = br.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True,
                             has_touch=True, device_scale_factor=2)
        pg = ctx.new_page(); vojti(pg, ADRES, POCHTA, PAROL, '.bottomnav')
        for imya, hash_ in [('app2-progress', '#/dashboard'), ('app2-karta', '#/map'),
                            ('app2-sdvig', '#/sdvig'), ('app2-manualy', '#/manualy'),
                            ('app2-vmeste', '#/vmeste')]:
            v_razdel(pg, hash_); snyat(pg, imya, TEL)
        # замеры показываем не пустой формой, а точкой Б: ради неё раздел и снимаем.
        # Значения ставим по смыслу поля, иначе в кадр попадает «спокойствие 120000».
        v_razdel(pg, '#/zamery')
        pg.evaluate("""()=>{
          const set=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
          const rubli=[120000,180000,25000];
          let r=0;
          document.querySelectorAll('.zam-form .zam-field').forEach(f=>{
            const t=(f.querySelector('span')||{}).textContent||'';
            const i=f.querySelector('input'); if(!i) return;
            let v;
            if(/из 10/i.test(t)) v=6;
            else if(/раз/i.test(t)) v=3;
            else if(/мес/i.test(t) && !/₽/.test(t)) v=2;
            else v=rubli[r++ % rubli.length];
            set.call(i, String(v)); i.dispatchEvent(new Event('input',{bubbles:true}));});
          const b=[...document.querySelectorAll('button')].find(x=>/Сохранить замеры/.test(x.innerText||''));
          if(b) b.click();}""")
        pg.wait_for_timeout(1800)
        # цель заполняем по смыслу каждого поля, иначе в кадр лезет «запас 300000 месяцев»
        pg.evaluate("""()=>{
          const set=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
          const c=document.querySelector('.tochka-b'); if(!c) return;
          c.querySelectorAll('.zam-field').forEach(f=>{
            const t=((f.querySelector('span')||{}).textContent||'').toLowerCase();
            const i=f.querySelector('input'); if(!i) return;
            let v;
            if(/к какому месяцу/.test(t)) v='К декабрю';
            else if(/пойму/.test(t)) v='Плачу за месяц вперёд и не считаю';
            else if(/первым/.test(t)) v='Поеду с семьёй к морю';
            else if(/из 10/.test(t)) v='9';
            else if(/мес/.test(t) && !/₽/.test(t)) v='6';
            else if(/доход/.test(t)) v='250000';
            else v='180000';
            set.call(i, v); i.dispatchEvent(new Event('input',{bubbles:true}));});
          const b=[...c.querySelectorAll('button')].find(x=>/Сохранить|Записать/.test(x.innerText||''));
          if(b) b.click();}""")
        pg.wait_for_timeout(1600)
        pg.evaluate("""()=>{const c=document.querySelector('.tochka-b'); if(c) c.scrollIntoView({block:'start'});}""")
        pg.wait_for_timeout(900)
        snyat(pg, 'app2-zamery', TEL)
        v_razdel(pg, '#/den-6'); snyat(pg, 'app2-den', TEL)
        ctx.close()

        # компьютер
        ctx = br.new_context(viewport={'width': 1280, 'height': 800}, device_scale_factor=2)
        pg = ctx.new_page(); vojti(pg, ADRES, POCHTA, PAROL, '.sidebar')
        v_razdel(pg, '#/dashboard'); demo(pg); snyat(pg, 'app2-desktop', PK)
        ctx.close()
        br.close()
finally:
    u = sluzhebnyy(ADRES, kl, POCHTA, 'ubrat')
    print('участник убран:', u.get('ok'))
