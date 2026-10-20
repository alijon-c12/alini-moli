# Telegram AI Userbot (Telethon)

Ushbu loyiha shaxsiy Telegram akkauntingiz orqali avtomatik AI (Google Gemini) yordamida javob qaytaruvchi **Telegram Userbot** hisoblanadi. BotFather yoki bot token kerak emas — dastur shaxsiy akkaunt nomidan ishlaydi.

---

## 🚀 Imkoniyatlari

- **Shaxsiy akkaunt orqali javob:** Rasmiy Telegram sessiyasi orqali sizning nomingizdan yozadi.
- **Faqat shaxsiy chatlar:** Guruhlar va kanallar e'tiborga olinmaydi.
- **Saved Messages orqali qulay boshqaruv:**
  - `/ai on` — AI javob berishini yoqish.
  - `/ai off` — AI ni vaqtincha to'xtatish.
  - `/ai status` — Joriy holat va statistika.
  - *(Standart holat: o'chiq / OFF)*.
- **Qo'lda aralashuvni sezish:** Agar siz biror shaxsiy chatga o'zingiz yozsangiz, AI shu chatda **10 daqiqa** davomida aralashmaydi (jim turadi).
- **Kontekst xotirasi:** Har bir chat bo'yicha oxirgi 10 ta xabar xotirada saqlanadi.
- **"typing..." indikatori:** AI javob o'ylayotgan vaqtda suhbatdoshga "yozmoqda..." holati ko'rinadi.
- **Spam va FloodWait himoyasi:** Bir chatga 3 soniyada 1 tadan ko'p javob berilmaydi, Telegram cheklovlari xavfsiz ushlanadi.
- **Moslashuvchan AI arxitekturasi:** Standart Google Gemini, keyinchalik boshqa provayderlarga oson almashtirish mumkin.

---

## 🛠 O'rnatish va Ishga tushirish

### 1. Loyihani yuklab olish va papkaga kirish
Terminal (yoki PowerShell / CMD) orqali loyiha papkasiga o'ting:
```bash
cd "C:\Users\777 comp service\Desktop\1 AI"
```

### 2. Virtual muhit (venv) yaratish va faollashtirish
- **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
  *(Agar xatolik bersa: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

- **Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. `.env` faylini sozlash
`.env.example` faylidan nusxa olib, `.env` faylini yarating:
```bash
cp .env.example .env
```
Keyin `.env` faylini ochib, kerakli kalitlarni kiriting:
```ini
TG_API_ID=12345678
TG_API_HASH=abcdef1234567890abcdef1234567890
AI_API_KEY=AIzaSy...
AI_MODEL=gemini-2.5-flash
ALLOWED_USERS=
```
- `TG_API_ID` va `TG_API_HASH`: [my.telegram.org](https://my.telegram.org) saytidan ("API development tools") olinadi.
- `AI_API_KEY`: [Google AI Studio](https://aistudio.google.com/) saytidan bepul olinadi.
- `ALLOWED_USERS`: Faqat ma'lum odamlarga javob berish uchun ularning Telegram ID larini vergul bilan yozing (masalan: `123456,789101`). Bo'sh qoldirsangiz, barcha shaxsiy chatlarga javob beradi.

### 5. Dasturni ishga tushirish
```bash
python main.py
```

> **Birinchi ishga tushirishda:**
> Konsolda telefon raqamingiz (masalan, `+998901234567`) va Telegram orqali kelgan tasdiqlash kodi so'raladi (agar 2FA parol bo'lsa, u ham kiritiladi). Sessiya `userbot_session.session` fayliga saqlanadi va keyingi safar kod so'ralmaydi.

---

## 📱 Boshqarish qoidalari

Dastur ishga tushgach, standart holatda AI o'chiq bo'ladi.
Uni yoqish uchun Telegram'da o'zingizning **"Saqlangan xabarlar" (Saved Messages)** chatiga quyidagi buyruqlardan birini yozing:

- `/ai on` — AIni yoqish
- `/ai off` — AIni to'xtatish
- `/ai status` — Holatni tekshirish

---

## 📁 Loyiha tarkibi

- [main.py](file:///C:/Users/777%20comp%20service/Desktop/1%20AI/main.py) — Telethon mantiqi, buyruqlar, xabarlar filtri va hodisalar.
- [ai.py](file:///C:/Users/777%20comp%20service/Desktop/1%20AI/ai.py) — Gemini AI bilan asinxron muloqot va javob olish moduli.
- [config.py](file:///C:/Users/777%20comp%20service/Desktop/1%20AI/config.py) — Sozlamalar, konfiguratsiya va doimiylar.
- [.env.example](file:///C:/Users/777%20comp%20service/Desktop/1%20AI/.env.example) — Muhit o'zgaruvchilari namunasi.
- [requirements.txt](file:///C:/Users/777%20comp%20service/Desktop/1%20AI/requirements.txt) — Kerakli kutubxonalar ro'yxati.
- [.gitignore](file:///C:/Users/777%20comp%20service/Desktop/1%20AI/.gitignore) — Git uchun e'tiborga olinmaydigan fayllar ro'yxati.
- [README.md](file:///C:/Users/777%20comp%20service/Desktop/1%20AI/README.md) — Qo'llanma.
