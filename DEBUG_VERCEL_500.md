# 🔧 Debug Vercel 500 Error

## Đã thêm Error Handling

### File đã update:

1. **api/index.py** - Added try/catch để show error details
2. **api/debug.py** - Simple debug endpoint
3. **requirements.txt** - Added csv342 package

---

## Bước Debug:

### 1. Redeploy trên Vercel

```bash
vercel --prod
```

Hoặc trong Vercel Dashboard: Deployments → Redeploy

### 2. Check Error Message

Khi deploy xong, vào URL: `https://your-app.vercel.app/`

Nếu vẫn lỗi, bạn sẽ thấy JSON với error details:

```json
{
  "error": "Failed to import app",
  "message": "...",
  "traceback": "...",
  "sys_path": [...],
  "cwd": "..."
}
```

### 3. Check Vercel Logs

```bash
vercel logs
```

Hoặc: Vercel Dashboard → Deployments → Click deployment → View Function Logs

---

## Các lỗi thường gặp:

### ❌ Missing Environment Variables

**Triệu chứng:** `POSTGRES_URL missing`, Connection error

**Fix:** Trong Vercel Dashboard → Settings → Environment Variables, add:

- `POSTGRES_URL`
- `SECRET_KEY`
- `GROQ_API_KEY`
- `DIFY_API_KEY`

⚠️ Sau khi add env vars, phải **Redeploy**!

### ❌ Import Error

**Triệu chứng:** `ModuleNotFoundError: No module named 'xxx'`

**Fix:** Add package vào `requirements.txt`

### ❌ Database Connection

**Triệu chứng:** `connection refused`, `timeout`

**Fix:**

- Check POSTGRES_URL format đúng
- Railway database phải allow external connections

### ❌ CSV Files not found

**Triệu chứng:** `FileNotFoundError: data/subject_list.csv`

**Fix:**

- Verify folder `data/` có trong repo
- Check `.vercelignore` không ignore `data/`

---

## Test Endpoints:

### Main App

```
https://your-app.vercel.app/
```

### Debug Endpoint (nếu cần)

```
https://your-app.vercel.app/test
```

---

## Next Steps:

1. ✅ Deploy với code mới (có error handling)
2. ✅ Check error message từ `/` route
3. ✅ Paste error message ở đây để debug tiếp
4. ✅ Fix based on error
5. ✅ Redeploy

---

## Expected Working URLs sau khi fix:

- `/` → Redirect to `/login`
- `/login` → Login page
- `/home` → Home page (sau login)
- `/admin/` → Admin dashboard
- `/yourplan` → Your plan page
