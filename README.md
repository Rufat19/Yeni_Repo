# Sosial Instruktor — Telegram Botu

Modern, çoxfunksiyalı Telegram botu (Aiogram v3) — oyunlar, yeniliklər, rəy sistemi, faydalı kanallar və sadə balans idarəsi bir mərkəzdə.

## Xüsusiyyətlər

- 🕹️ Köstəbək Oyunu (qrupda /game) — komanda ilə əyləncə, min. 3 nəfər
- 🆕 Yeniliklər — admin əlavə edir, istifadəçilərə bildiriş gedir
- 🌟 İstifadəçi rəyləri — ulduzla qiymətləndir, rəy yaz, admin cavab verə bilər
- � RBCron balansı — balansı göstər/artır, qəbz adminə təsdiq üçün gedir
- � PDF hədiyyəsi — “Müsahibəyə hazırlıq texnikaları” faylı
- 🌐 Sosial Mühit kanalı — qısa təsvir, giriş və link dəstəyi
- ℹ️ DSMF/DOST haqqında məlumat blokları
- 🔔 Admin start bildirişi — hansı build-in işə düşdüyü görünür

Arxitektura: Aiogram Router-ları (`handlers/*`), SQLite (yerli `database.db`), bəzi asan saxlanılan JSON faylları (`reviews.json` və s.).

## Quraşdırma (lokal)

1) Tələblər
- Python 3.12 (runtime.txt ilə uyğun)
- Pip paketləri: `pip install -r requirements.txt`

2) Mühit dəyişənləri (`.env`)
```
BOT_TOKEN=xxxx:yyyy
ADMIN_ID=123456789
APP_VERSION=dev
REPO_NAME=Yeni_Repo
CARD_NUMBER=0000 0000 0000 0000
```

3) İşə salma
- VS Code task: Run Bot (venv)
- və ya terminaldan:
```
python run.py
```

## İstifadəçi axınları (qısa)

- `/start` (şəxsi mesaj): salam, qısa tanıtım videosu, iki sütunlu menyu
- “Köstəbək Oyunu” (qısayol) → qrupda `/game` üçün yönləndirmə
- “Yeniliklər” → başlıqlar siyahısı, oxu düyməsi
- “Rəylər” → ulduz seç, rəy yaz, bütün rəylərə bax
- “Balans” → balans göstər/artır; qəbz fotosu adminə gedir, təsdiqdən sonra artırılır
- “PDF” → hədiyyə sənədi bir düymə ilə
- “Sosial Mühit” → kanal haqqında məlumat və giriş

## Deploy (Railway)

- Procfile: `worker: python run.py`
- runtime.txt: `python-3.12`
- Environment: `BOT_TOKEN`, `ADMIN_ID`, opsional `APP_VERSION`, `REPO_NAME`, `CARD_NUMBER`

Addımlar:
1. Repo GitHub-da hazır olsun
2. Railway → New Project → Deploy from GitHub → bu repozitoriyanı seç
3. Variables bölməsində tələb olunan mühit dəyişənlərini əlavə et
4. Deploy — asılılıqlar avtomatik qurulacaq, worker prosesi işə düşəcək

Qeydlər:
- Long polling istifadə olunur (webhook tələb etmir)
- `logs/` və yerli `*.db` faylları git-də izlənmir

## Faydalı fayllar
- `run.py` — giriş nöqtəsi; router-ları qoşur, DB cədvəllərini yaradır, start bildirişi göndərir
- `handlers/` — modul-modul xüsusiyyətlər
- `database/` — SQLite köməkçiləri
- `pdfs/` — PDF resursları
- `media/` — video və media faylları

## Əlaqə
Sual və ya təklif üçün: **@Rufat19**

— Bu botu öz layihənə uyğun asanlıqla fərdiləşdirə bilərsən.