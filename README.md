# Alien_BiBOT Telegram Botu

## Qısa Təsvir

Alien_BiBOT – Telegram üçün interaktiv, çoxfunksiyalı botdur. Bot aşağıdakı əsas imkanları təqdim edir:

- 🌟 Rəy və ulduzla qiymətləndirmə sistemi
- 🕹️ Komanda Köstəbək Oyunu (impostor tapma oyunu)
- 📄 PDF faylların alınması (balansdan RBCron tutulur)
- 💰 Balans izləmə və artırma
- 🚀 Qeydiyyat və giriş paneli
- 📢 Faydalı kanallar və sosial mühit
- 👀 Bütün istifadəçi rəylərini görmək
- 🤖 Bot haqqında məlumat
- Admin üçün istifadəçi tarixçəsi

## Quraşdırma

1. **Tələblər:**
   - Python 3.9+
   - `aiogram` kitabxanası (`pip install aiogram`)
   - Bot tokeni və admin ID-ni `config.py` faylında saxla:
     ````python
     BOT_TOKEN = "BOTUN_TOKENI"
     ADMIN_ID = 123456789
     ````

2. **Qovluq Strukturu:**
   ```
   Alien_BiBOT/
   ├── handlers/
   │   ├── start.py
   │   ├── entry.py
   │   ├── balance.py
   │   ├── review.py
   │   ├── game.py
   │   ├── admin.py
   │   └── balance_utils.py
   ├── config.py
   ├── run.py
   └── pdfs/
   ```

3. **Botun işə salınması:**
   Terminalda:
   ```
   python run.py
   ```

## İstifadəçi Komandaları və Funksiyalar

### `/start`  
- **Yalnız şəxsi mesajda işləyir.**
- Əsas menyu və bütün funksiyalara çıxış verir.

### `/game`  
- **Yalnız qrupda işləyir.**
- Komanda köstəbək oyunu başlayır. Ən azı 3 oyunçu lazımdır.
- Bot hər kəsə DM-də söz göndərir, birinə fərqli söz.
- 2 dəqiqə sonra səsvermə başlayır.

### Rəy və Qiymətləndirmə  
- İstifadəçi 5 ulduz seçir və rəy yazır.
- Bütün rəylər açıqdır, admin istəsə cavab verə bilər.

### PDF Almaq  
- PDF almaq üçün balansda kifayət qədər RBCron olmalıdır.
- Hər PDF üçün 2 RBCron çıxılır.

### Balans  
- Balansı göstərmək və artırmaq mümkündür.

### Qeydiyyat və Giriş  
- Qeydiyyat üçün balansdan RBCron çıxılır, unikal link göndərilir.

### Admin Paneli  
- `/admin` yalnız şəxsi mesajda və admin üçün aktivdir.
- Son 50 istifadəçi tarixçəsini göstərir.

## Əlavə Qeydlər

- Botun bütün inline buttonları maraqlı adlar və smayliklərlə hazırlanıb.
- Qrupda `/start` və `/admin` işləməz.
- Qrupda yalnız `/game` komandası aktivdir.
- Bütün funksiyalar `handlers` qovluğunda modullar şəklindədir.

## Əlaqə və Dəstək

Sual və ya problem yaranarsa, adminə müraciət edin:  
**@Rufat19**

---

## 2025-08-17 - Əlavə və düzəlişlər

- Əsas menyuya qayıt buttonu bütün handler-larda tam menyunu göstərir (get_main_buttons).
- Fast Test, Quiz, Cert, Balance, Review, Channel Access və Order Bot modullarında əsas menyu callback-ları standartlaşdırıldı.
- RBCron ilə bağlı bütün yanlış və aldatıcı mesajlar silindi.
- Test bitdikdə nəticə və tam menyu birgə göstərilir.
- Order Bot bölməsində "Razı deyiləm" buttonu çıxarıldı.
- README üçün bugünkü dəyişikliklər və kodun son vəziyyəti qeyd olundu.
- Bütün router-lar run.py faylında düzgün şəkildə əlavə olundu və botun işə düşməsi yoxlanıldı.
- Əlavə buttonlar, callback-lar və istifadəçi təcrübəsi üzrə düzəlişlər tətbiq olundu.

**Botun kodunu və funksiyalarını öz ehtiyacına uyğun dəyişə bilərsən!**

## Railway ilə Deploy

Bu bot Railway üzərində “worker” kimi işləyir.

- Python versiyası: `runtime.txt` → `python-3.12`
- Başlatma əmri: `Procfile` → `worker: python run.py`
- Lazım olan environment dəyişənləri:
   - `BOT_TOKEN` – Telegram bot tokeni
   - `ADMIN_ID` – admin Telegram ID (rəqəm)

Addımlar:
1. Bu layihəni yeni GitHub repoya push et (aşağıdakı “Repoya push” bölməsinə bax).
2. Railway-də yeni Project aç və “Deploy from GitHub” seç.
3. Repo seçildikdən sonra servisin tipini Worker olaraq saxla (Procfile avtomatik oxunur).
4. Settings → Variables bölməsində `BOT_TOKEN` və `ADMIN_ID` əlavə et.
5. Deploy et – Railway `requirements.txt` faylından asılılıqları quracaq və `python run.py` ilə botu işə salacaq.

Qeydlər:
- Lokal `logs/` və `*.db` faylları `.gitignore` ilə ignor edilir; prod istifadə üçün lazım deyil.
- Bot hazırda long polling ilə işləyir – webhook tələb etmir.