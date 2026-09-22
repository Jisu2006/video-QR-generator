# 🎥 Video QR Generator

A modern, responsive web application built with **Python (Flask)**, **MySQL / SQLite**, and **HTML5/CSS3** that enables users to upload video files, automatically generate unique video URLs, and produce crystal-clear, print-ready QR codes for instant mobile phone video streaming.

---

## 🌟 Key Features

1. **Video Upload & File Validation**:
   - Supports common formats: `.mp4`, `.webm`, `.mov`, `.mkv`, `.avi`, `.m4v`.
   - Drag-and-drop file upload with animated file preview and client/server validation.
   - Real-time upload progress bar displaying transfer percentage, speed (MB/s), and estimated time remaining.
   - Secure UUID-based server storage prevents path traversal or file overwrites.

2. **Automated High-Resolution QR Code Engine**:
   - Generates high-error-correction (Level H) QR codes pointing to unique public URLs (`/video/<unique-id>`).
   - Downloadable in high-resolution (300 DPI PNG) suitable for physical banners, posters, flyers, and merchandise.
   - Direct link copy and one-click printable flyer layout.

3. **HTTP 206 Partial-Content Video Streaming**:
   - Implements full byte-range request streaming headers.
   - Enables seamless video scrubbing, instant buffering, and zero lag on **iOS Safari** and **Android Chrome**.
   - Videos stream directly in the browser using a custom HTML5 video player without forcing file downloads.

4. **Modern UI & Aesthetic Experience**:
   - Sleek dark and light modes with persistent preference.
   - Glassmorphic translucent cards, fluid animations, and custom HTML5 video controls (play/pause, volume, speed selector, theater mode, picture-in-picture, fullscreen).
   - Fully responsive across mobile smartphones, tablets, laptops, and wide screens.

5. **Admin Dashboard & Management**:
   - Secure session-based admin authentication with password hashing.
   - Real-time statistics: Total Videos, Total Views/Scans, Disk Space Used, and Wi-Fi Streaming IP.
   - Search & filter toolbar, video metadata editing, and secure deletion (with physical file cleanup).

6. **Flexible Database & Domain Configuration**:
   - Seamlessly supports **MySQL** (production) and **SQLite** (instant zero-config local run).
   - Built-in Wi-Fi LAN IP auto-detection (`http://192.168.x.x:5000`) for effortless mobile phone camera scanning without external domains.

---

## 📁 Project Folder Structure

```
Swapna_mam/
│
├── app/
│   ├── __init__.py               # Flask application factory, error handlers, DB init
│   ├── models.py                 # SQLAlchemy Video, Admin, and AppSetting models
│   │
│   ├── routes/
│   │   ├── __init__.py           # Blueprint registrations
│   │   ├── auth.py               # Admin login, logout, and session guard
│   │   ├── admin.py              # Dashboard, statistics, video deletion, settings
│   │   ├── upload.py             # Video upload endpoint and QR generation handler
│   │   ├── video.py              # Public video watch page, range streaming, QR download
│   │   └── api.py                # REST API endpoints (JSON lists, details, system info)
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── qr_generator.py       # High-res QR code generator (Pillow + qrcode)
│   │   ├── file_handler.py       # File validation, UUID hashing, HTTP 206 streaming
│   │   └── network_helper.py     # Local Wi-Fi LAN IP detection & URL resolver
│   │
│   ├── static/
│   │   ├── css/
│   │   │   ├── style.css         # Modern design system, glassmorphism, responsive grid
│   │   │   └── player.css        # Custom HTML5 video player skin & controls
│   │   ├── js/
│   │   │   ├── main.js           # Theme switcher, toast manager, clipboard, modals
│   │   │   ├── upload.js         # Drag-and-drop, XHR upload progress, validation
│   │   │   ├── dashboard.js      # Search/filter, QR modal, delete confirmation
│   │   │   └── player.js         # Custom video player engine & keyboard shortcuts
│   │   ├── uploads/
│   │   │   └── videos/           # Stored video files
│   │   └── qr_codes/             # Generated QR code images
│   │
│   └── templates/
│       ├── base.html             # Base layout, navbar, toasts, footer
│       ├── auth/
│       │   └── login.html        # Glassmorphic admin login
│       ├── admin/
│       │   ├── dashboard.html    # Analytics metrics & video table
│       │   ├── upload.html       # Video upload dropzone & progress bar
│       │   ├── result.html       # QR code result, flyer print, copy link
│       │   └── settings.html     # Base URL, Wi-Fi setup & password manager
│       ├── video/
│       │   └── watch.html        # Responsive public video viewing page
│       └── errors/
│           ├── 404.html          # Page not found error screen
│           └── 500.html          # Server error screen
│
├── config.py                     # Configuration settings (Development / Production)
├── run.py                        # Entry point script with CLI options (--port, --host)
├── schema.sql                    # MySQL database schema definition
├── requirements.txt              # Python package dependencies
├── .env.example                  # Environment configuration template
├── .env                          # Active environment variables
├── .gitignore                    # Version control ignore rules
└── README.md                     # Comprehensive documentation
```

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
- Python 3.9+ installed on your system.
- Optional: MySQL Server 5.7+ / 8.0+ (SQLite is used automatically if MySQL is not running).

### 2. Installation
Open a terminal in the project root directory and run:

```bash
# 1. Install dependencies
pip install -r requirements.txt
```

### 3. Launching the Application
Run the application using:

```bash
python run.py
```

The terminal will display the server addresses:
```
=================================================================
  🎥 VIDEO QR GENERATOR - SYSTEM READY
=================================================================
  Local Access       : http://127.0.0.1:5000
  Network (Mobile)   : http://192.168.1.15:5000
  Admin Login        : http://127.0.0.1:5000/admin/login
  Default Credentials: admin / admin123
=================================================================
```

Open your browser to **`http://127.0.0.1:5000`** and log in using:
- **Username**: `admin`
- **Password**: `admin123`

---

## 📱 How Mobile Phone QR Scanning Works

### Why Localhost URLs (`127.0.0.1`) Don't Scan on Phones
When a QR code contains `http://127.0.0.1:5000/video/abc123`, a mobile phone scanning the QR code will look for a server running *on the phone itself* (which fails).

### How This Application Solves It:
1. **Local Wi-Fi Network Mode (Automatic)**:
   - When the server starts, it auto-detects your computer's local Wi-Fi IP (e.g. `http://192.168.1.15:5000`).
   - QR codes generated in this mode encode this Wi-Fi IP.
   - When your smartphone is connected to the **same Wi-Fi network**, scanning the QR code with your iPhone Camera or Android Google Lens will immediately open the video page and stream the video!

2. **Public Testing with Ngrok / Cloudflare (Optional)**:
   - Run: `ngrok http 5000`
   - Copy the public HTTPS URL (e.g. `https://your-tunnel.ngrok-free.app`).
   - Go to **Admin Settings** (`/admin/settings`) and paste the URL into **Base URL / Domain**.
   - All generated QR codes will now work anywhere in the world on mobile data (4G/5G)!

---

## 🗄️ MySQL Database Setup (Optional for Production)

By default, the application runs on SQLite for instant zero-configuration setup. To use **MySQL**:

1. Open your MySQL client / phpMyAdmin / terminal:
   ```bash
   mysql -u root -p < schema.sql
   ```
2. Edit `.env`:
   ```ini
   USE_MYSQL=true
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DB=video_qr_db
   ```
3. Restart `python run.py`. Flask-SQLAlchemy will connect directly to MySQL.

---

## 🌐 Production Deployment Guide (Linux / VPS / Nginx)

For production deployment on an Ubuntu / Debian VPS with Nginx and Gunicorn:

### 1. Install Gunicorn
```bash
pip install gunicorn
```

### 2. Create a Systemd Service (`/etc/systemd/system/videoqr.service`)
```ini
[Unit]
Description=Video QR Generator Web App
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/video_qr
Environment="PATH=/var/www/video_qr/venv/bin"
ExecStart=/var/www/video_qr/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 "app:create_app('production')"

[Install]
WantedBy=multi-user.target
```

### 3. Configure Nginx Reverse Proxy (`/etc/nginx/sites-available/videoqr`)
```nginx
server {
    listen 80;
    server_name video.yourdomain.com;
    client_max_body_size 500M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Serve static assets directly for high performance
    location /static/ {
        alias /var/www/video_qr/app/static/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
```

### 4. Enable SSL via Certbot
```bash
sudo certbot --nginx -d video.yourdomain.com
```

---

## 🛡️ Security Implementation

- **Sanitized Uploads**: Filenames are sanitized via `werkzeug.utils.secure_filename` and stored with random UUIDs to avoid directory traversal.
- **MIME & Extension Whitelist**: Only verified video formats (`mp4`, `webm`, `mov`, `mkv`, `avi`, `m4v`) are accepted.
- **HTTP 206 Range Stream Guard**: Validates byte-range boundaries and prevents out-of-bounds memory allocation.
- **Admin Session Security**: `HttpOnly` and `SameSite=Lax` cookies with password hashing (`scrypt`/`pbkdf2`).
- **No Direct Filesystem Exposure**: Video files are served via internal streaming endpoints (`/stream/<unique_id>`) rather than exposing server directory paths.
