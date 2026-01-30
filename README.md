# 🌍 Telegram News Bot - GitHub Actions Version

Bot Telegram tự động thu thập tin tức chính trị thế giới, phân tích bằng AI (Google Gemini - MIỄN PHÍ), và đưa ra dự đoán xu hướng tài chính.

## 💰 Chi phí: HOÀN TOÀN MIỄN PHÍ!

| Thành phần | Chi phí |
|------------|---------|
| GitHub Actions | ✅ Miễn phí (2000 phút/tháng) |
| Google Gemini API | ✅ Miễn phí |
| Telegram Bot | ✅ Miễn phí |
| RSS Feeds | ✅ Miễn phí |

## ✨ Tính năng

- 📰 Thu thập tin tức từ Reuters, BBC, NPR, The Guardian
- 🤖 Phân tích bằng Google Gemini AI
- 🌐 Theo dõi: Mỹ, Trung Quốc, Nga, Nhật Bản
- 📊 Dự đoán: Giá dầu, vàng, bất động sản
- ⏰ Báo cáo tự động lúc 7:00 sáng (giờ VN)

## 🚀 Cách cài đặt

### Bước 1: Fork repository này

### Bước 2: Thêm Secrets

Vào **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Thêm 3 secrets:
- `TELEGRAM_BOT_TOKEN`: Token từ @BotFather
- `TELEGRAM_USER_ID`: ID từ @userinfobot  
- `GEMINI_API_KEY`: Key từ https://aistudio.google.com/app/apikey

### Bước 3: Chạy thử

Vào **Actions** → **Daily News Report** → **Run workflow**

## 📁 Cấu trúc

```
├── .github/workflows/
│   └── daily_news.yml    # GitHub Actions workflow
├── config.py             # Cấu hình
├── news_collector.py     # Thu thập tin RSS
├── ai_analyzer.py        # Phân tích bằng Gemini
├── database.py           # Lưu trữ SQLite
├── scheduled_task.py     # Script chạy định kỳ
└── requirements.txt      # Dependencies
```

## ⏰ Thay đổi giờ gửi báo cáo

Chỉnh file `.github/workflows/daily_news.yml`:

```yaml
schedule:
  - cron: '0 0 * * *'  # 00:00 UTC = 07:00 VN
```

| Giờ VN | Cron UTC |
|--------|----------|
| 6:00   | `0 23 * * *` |
| 7:00   | `0 0 * * *` |
| 8:00   | `0 1 * * *` |

## 📄 License

MIT License
