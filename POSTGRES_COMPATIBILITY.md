# PostgreSQL vs MySQL Compatibility Guide

## ✅ **Fixed Issues:**

### 1. **Boolean Values**

- ❌ MySQL: `is_started = 0/1`
- ✅ PostgreSQL: `is_started = FALSE/TRUE`
- **Fixed in:** `roadmap_service.py`, `yourplan_service.py`

### 2. **Auto-detection Logic**

- Development (Local) → MySQL
- Production/Vercel/Railway → PostgreSQL

### 3. **Connection & Cursor**

- MySQL: `cursor(dictionary=True)`
- PostgreSQL: `cursor(cursor_factory=RealDictCursor)`

## 🔄 **Database Auto-Switch:**

```python
# Environment variables control which DB to use:
ENVIRONMENT=development  # → MySQL (Local)
ENVIRONMENT=production   # → PostgreSQL (Railway)
```

## 🚀 **Deploy Commands:**

**Local (MySQL):**

```bash
python app.py
```

**Vercel (PostgreSQL):**

```bash
vercel --prod
```

## 📝 **Schema Differences:**

| Feature        | MySQL              | PostgreSQL                                 |
| -------------- | ------------------ | ------------------------------------------ |
| Boolean        | `0/1`              | `FALSE/TRUE`                               |
| Auto ID        | `AUTO_INCREMENT`   | `SERIAL` or `GENERATED ALWAYS AS IDENTITY` |
| Last Insert ID | `LAST_INSERT_ID()` | `cursor.lastrowid`                         |

## ⚡ **Next Steps:**

1. Test roadmap apply functionality
2. Verify all CRUD operations work
3. Deploy to Vercel with PostgreSQL
