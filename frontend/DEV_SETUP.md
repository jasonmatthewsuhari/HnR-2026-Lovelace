# 🎉 One Command to Rule Them All!

## ✨ Now You Can Start Everything with One Command

I've configured the frontend to **automatically start the backend** when you run `npm run dev`!

---

## 🚀 Usage

### **Start Both Servers (New!)**

```bash
cd frontend
npm run dev
```

This will start:
- ✅ **Backend** (FastAPI) on http://localhost:8000
- ✅ **Frontend** (Next.js) on http://localhost:3000

You'll see output from both servers in the same terminal with colored prefixes:
```
[backend] Starting Lovelace Backend API Server...
[frontend] ▲ Next.js 16.0.7
[backend] INFO: Application startup complete.
[frontend] - Local: http://localhost:3000
```

### **Start Only Frontend (If Backend Already Running)**

```bash
cd frontend
npm run dev:frontend-only
```

---

## 📦 What Changed

### **package.json Scripts**

```json
{
  "scripts": {
    "dev": "concurrently \"npm run dev:backend\" \"npm run dev:frontend\" ...",
    "dev:frontend": "next dev",
    "dev:backend": "cd ../backend && python main.py",
    "dev:frontend-only": "next dev"
  }
}
```

### **New Dependency**

- Added `concurrently` - Runs multiple commands simultaneously with colored output

---

## 🎯 Complete Workflow

### **First Time Setup**

```bash
# 1. Configure Firebase
# Edit frontend/.env.local with your Firebase config

# 2. Install dependencies (if not done)
cd frontend
npm install

cd ../backend
pip install -r requirements.txt

# 3. Start everything!
cd ../frontend
npm run dev
```

### **Daily Development**

```bash
cd frontend
npm run dev
```

That's it! Both servers start automatically! 🎉

---

## 🎨 Terminal Output

The terminal will show both servers with color-coded prefixes:

```
[backend] ============================================================
[backend] 🎀 LOVELACE - AI-Powered Fashion Assistant
[backend] ============================================================
[backend] 📍 Server: http://localhost:8000
[backend] 📚 API Docs: http://localhost:8000/docs
[frontend] ▲ Next.js 16.0.7
[frontend] - Local: http://localhost:3000
[frontend] ✓ Ready in 2.3s
```

---

## 🛑 Stopping the Servers

Press **Ctrl+C** once to stop both servers gracefully.

---

## 🔧 Troubleshooting

### **Backend won't start**

**Error:** `python: command not found`
- Make sure Python is in your PATH
- Or install Python from python.org

**Error:** `ModuleNotFoundError: No module named 'fastapi'`
- Install backend dependencies:
  ```bash
  cd backend
  pip install -r requirements.txt
  ```

### **Port already in use**

**Error:** `Port 8000 is already in use`
- Another process is using port 8000
- Kill the process or change the port in `backend/main.py`

**Error:** `Port 3000 is already in use`
- Run on different port:
  ```bash
  npm run dev:frontend-only -- -p 3001
  ```

### **Frontend starts but backend doesn't**

- Check that `backend/main.py` exists
- Check that Python is installed: `python --version`
- Try running backend manually:
  ```bash
  cd backend
  python main.py
  ```

---

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start both backend & frontend ⭐ |
| `npm run dev:frontend-only` | Start only frontend |
| `npm run build` | Build for production |
| `npm run start` | Start production build |
| `npm run lint` | Run ESLint |

---

## 🎁 Bonus: Alternative Methods

### **Method 1: npm run dev (Recommended)**
```bash
cd frontend
npm run dev
```
✅ Single command
✅ Both servers in one terminal
✅ Color-coded output

### **Method 2: Batch Script (Windows)**
```bash
start_servers.bat
```
✅ Opens separate terminal windows
✅ Can close main terminal

### **Method 3: Manual (Two Terminals)**
```bash
# Terminal 1
cd backend
python main.py

# Terminal 2
cd frontend
npm run dev:frontend-only
```
✅ Full control
✅ Separate logs

---

## 🎉 Summary

**Before:**
```bash
# Terminal 1
cd backend
python main.py

# Terminal 2  
cd frontend
npm run dev
```

**After:**
```bash
cd frontend
npm run dev
```

**One command, both servers, easy! 🚀**

---

## 📝 Notes

- The backend must complete startup before making API calls
- Usually takes 2-3 seconds
- Frontend will be ready at http://localhost:3000
- Backend will be ready at http://localhost:8000
- API docs available at http://localhost:8000/docs

---

**Made with 💜 for Lovelace**
