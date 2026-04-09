# 🚀 Phase 1: Complete Running Guide

## Step-by-Step Instructions

### **STEP 1: Activate Virtual Environment**

```powershell
# Navigate to project directory
cd c:\Users\E-TIME\Desktop\AIML\Quran_grammer\quranic_grammar_app

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

**Expected Output:**
```
(.venv) PS C:\Users\E-TIME\Desktop\AIML\Quran_grammer\quranic_grammar_app>
```

---

### **STEP 2: Verify Dependencies (Already Done)**

```powershell
# Check installed packages
pip list
```

**You should see:**
- Flask 2.3.2
- Flask-SQLAlchemy 3.0.5
- Flask-Login 0.6.2
- PyMySQL 1.1.0
- python-dotenv 1.0.0

---

### **STEP 3: Setup MySQL Database**

#### Option A: Using MySQL Command Line (Recommended)

```powershell
# Start MySQL (if running as service, skip this)
# Or use: mysql -u root -p

mysql -u root
```

Then in MySQL prompt:

```sql
-- Create database
CREATE DATABASE quran_grammar_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Show created database
SHOW DATABASES;

-- Exit MySQL
EXIT;
```

#### Option B: Using MySQL Workbench
1. Open MySQL Workbench
2. Create new schema: `quran_grammar_db`
3. Character set: `utf8mb4`
4. Collation: `utf8mb4_unicode_ci`

---

### **STEP 4: Verify .env File**

The `.env` file should have:

```
FLASK_ENV=development
SECRET_KEY=quranic-grammar-app-secret-key-dev
DATABASE_URL=mysql+pymysql://root:@localhost/quran_grammar_db
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_HOST=localhost
MYSQL_DB=quran_grammar_db
```

📝 **If your MySQL has a password**, update it:
```
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost/quran_grammar_db
```

---

### **STEP 5: Run the Flask Application**

```powershell
# Make sure virtual environment is activated
# Then run:

python run.py
```

**Expected Output:**
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
WARNING in app.run_app_context() - This is a development server. Do not use it in production
 * Restarting with reloader
```

---

### **STEP 6: Test the Application**

Open your browser and go to:

```
http://localhost:5000
```

**You should see:**
- 🕌 Quranic Grammar App homepage
- Navigation bar with: Home, Surahs, Login, Register
- Features list
- "Start Learning" button

---

### **STEP 7: Test All Routes**

#### Homepage
```
http://localhost:5000/
```

#### Register Page
```
http://localhost:5000/auth/register
```

#### Login Page
```
http://localhost:5000/auth/login
```

#### Surahs List (empty until Phase 2)
```
http://localhost:5000/quran/surahs
```

#### API Endpoints
```
http://localhost:5000/api/surahs
http://localhost:5000/api/surah/1/ayahs  (will return empty list for now)
```

---

## 🔧 Troubleshooting

### ❌ Error: Virtual Environment Not Activating

```powershell
# Fix: Set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate again
.\.venv\Scripts\Activate.ps1
```

---

### ❌ Error: "No module named 'app'"

```powershell
# Make sure you're in the correct directory:
cd c:\Users\E-TIME\Desktop\AIML\Quran_grammer\quranic_grammar_app

# Then run:
python run.py
```

---

### ❌ Error: "MySQL Connection Error"

**Solution 1:** Check if MySQL is running

```powershell
# Check MySQL service status
Get-Service MySQL*
```

**Solution 2:** If MySQL is not installed, install it first or use SQLite

To use SQLite instead (for testing):
Edit `.env`:
```
DATABASE_URL=sqlite:///quran_grammar_db.sqlite
```

---

### ❌ Error: "ModuleNotFoundError: No module named 'flask'"

```powershell
# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📋 Quick Command Summary

```powershell
# 1. Navigate to project
cd c:\Users\E-TIME\Desktop\AIML\Quran_grammer\quranic_grammar_app

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Check dependencies
pip list

# 4. Create MySQL database (in MySQL):
# CREATE DATABASE quran_grammar_db CHARACTER SET utf8mb4;

# 5. Run Flask app
python run.py

# 6. Open in browser
# http://localhost:5000
```

---

## ✅ Success Checklist

- [ ] Virtual environment activated (shows `.venv` in terminal)
- [ ] All dependencies installed (`pip list` shows 6+ packages)
- [ ] MySQL database created (`quran_grammar_db`)
- [ ] `.env` file configured correctly
- [ ] Flask app running on `http://localhost:5000`
- [ ] Homepage loads successfully
- [ ] Navigation bar visible
- [ ] No error messages in terminal

---

## 🛑 To Stop the Flask App

```powershell
# Press Ctrl + C in the terminal
Ctrl + C
```

---

## 💡 Pro Tips

1. **Keep Flask running** - Leave it running while developing
2. **Check terminal for errors** - All errors appear in terminal
3. **Auto-reload enabled** - Change code and page auto-refreshes
4. **Database tables auto-created** - First run creates all tables

---

## 🚀 Next Steps After Phase 1 Runs Successfully

Once everything is working:
1. Phase 2: Import Quran data into database
2. Phase 3: Implement additional routes
3. Phase 4: Add grammar tagging system
4. Phase 5: Build frontend features

Happy coding! 🎉
