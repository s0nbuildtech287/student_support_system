# 🚀 Hướng dẫn Deploy lên Vercel

## Vấn đề đã fix: 404 NOT_FOUND

### Nguyên nhân:

- ❌ Thư mục `api/` trống, không có file `index.py`
- ❌ Vercel không tìm thấy entry point

### Giải pháp:

- ✅ Tạo file `api/index.py` - Entry point cho Vercel
- ✅ Tạo file `.vercelignore` - Loại bỏ files không cần
- ✅ Cải thiện `vercel.json` - Config routes tốt hơn

---

## Các bước Deploy

### 1. Commit code mới

```bash
git add .
git commit -m "Fix: Add Vercel entry point api/index.py"
git push
```

### 2. Deploy lên Vercel

#### Option A: Vercel CLI (Khuyến nghị)

```bash
# Install Vercel CLI (nếu chưa có)
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

#### Option B: Vercel Dashboard

1. Vào https://vercel.com/dashboard
2. Click "Add New" → "Project"
3. Import repository từ GitHub
4. Vercel sẽ tự detect Flask app

### 3. Set Environment Variables

Trên Vercel Dashboard → Project Settings → Environment Variables, thêm:

```
POSTGRES_URL=<your-railway-postgres-url>

SECRET_KEY=<your-secret-key>

GROQ_API_KEY=<your-groq-api-key>

DIFY_API_KEY=<your-dify-api-key>

FLASK_ENV=production

ENVIRONMENT=production
```

⚠️ **Quan trọng**:

- Add cho cả Development, Preview, và Production environments
- Lấy values từ file `.env` local của bạn
- Không commit API keys vào Git!

### 4. Redeploy

Sau khi add environment variables:

```bash
vercel --prod
```

Hoặc trong Dashboard: Deployments → Click "..." → Redeploy

---

## Cấu trúc Files đã tạo

### `api/index.py`

```python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
handler = app  # Vercel calls this
```

**Giải thích:**

- Vercel serverless functions cần file trong folder `api/`
- Import `app` từ `app.py` ở root
- Export `handler` để Vercel gọi

### `vercel.json`

```json
{
  "builds": [{ "src": "api/index.py", "use": "@vercel/python" }],
  "routes": [
    { "src": "/static/(.*)", "dest": "/static/$1" },
    { "src": "/(.*)", "dest": "api/index.py" }
  ]
}
```

**Giải thích:**

- Build Python app từ `api/index.py`
- Route static files trực tiếp
- Route tất cả requests khác qua Flask app

### `.vercelignore`

```
venv/
__pycache__/
test_*.py
*.md
```

**Giải thích:**

- Không upload venv (Vercel tự cài từ requirements.txt)
- Không upload test files và docs

---

## Verify Deployment

### 1. Check URL

Sau khi deploy, Vercel sẽ cho URL như:

```
https://your-project.vercel.app
```

### 2. Test các routes

```bash
# Homepage (redirect to login)
https://your-project.vercel.app/

# Login
https://your-project.vercel.app/login

# Admin
https://your-project.vercel.app/admin/
```

### 3. Check logs

```bash
# Real-time logs
vercel logs

# Or in Dashboard: Deployments → Click deployment → View Function Logs
```

---

## Troubleshooting

### Lỗi 404 - NOT_FOUND

- ✅ **Fixed**: Đã tạo `api/index.py`
- Verify: File `api/index.py` có trong repo
- Verify: `vercel.json` có routes config

### Lỗi 500 - Internal Server Error

- Check environment variables đã set chưa
- Check database connection (POSTGRES_URL)
- Xem logs: `vercel logs`

### Lỗi Import Module

- Check `requirements.txt` có đầy đủ dependencies
- Check Python version (Vercel dùng Python 3.9 by default)

### Static files không load

- Verify `vercel.json` có route `/static/(.*)`
- Verify folder `static/` có trong repo (không trong `.vercelignore`)

---

## Performance trên Vercel

### Cold Start

- First request sau idle: ~2-5s (Vercel khởi động container)
- Subsequent requests: < 500ms

### Database Queries

- Vercel (US/EU) → Railway: ~100-200ms latency
- Với batch queries đã optimize: Most operations < 1s

### Expected Performance

| Thao tác               | Thời gian |
| ---------------------- | --------- |
| Login                  | < 1s      |
| View YourPlan          | < 1s      |
| Apply Roadmap (12 môn) | < 1s      |
| Add/Remove Subject     | < 500ms   |
| Submit Quiz            | < 500ms   |

---

## Next Steps

1. ✅ Deploy với câu lệnh:

   ```bash
   vercel --prod
   ```

2. ✅ Set environment variables trong Vercel Dashboard

3. ✅ Test app tại URL Vercel cung cấp

4. ✅ Setup custom domain (optional):
   - Vercel Dashboard → Settings → Domains
   - Add your domain
   - Update DNS records

---

## Notes

- **Database**: PostgreSQL trên Railway (đã config)
- **Static Files**: CSS, JS, images được serve trực tiếp
- **Sessions**: Flask sessions work (SECRET_KEY trong env vars)
- **Admin Access**: admin@gmail.com (đã có role)

**Ready to deploy!** 🎉
