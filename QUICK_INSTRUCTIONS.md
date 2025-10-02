# 🚀 QUICK INSTRUCTIONS - IMAP2RSS (Gmail)

## 1️⃣ Run the System
```bash
cd /home/luke/VSCode/Imap2RSS
docker-compose up -d
```

## 2️⃣ Configure via Web Interface
📱 **Access:** http://localhost:9999

- **Provider:** Select "Gmail"
- **Email:** your-email@gmail.com
- **Password:** Use Google app password
- Save settings
- Restart: `docker-compose restart`

## 2.1️⃣ Gmail App Password
🔐 **Create app password:**
1. https://myaccount.google.com/security
2. 2-Step Verification → App passwords
3. Select app → Other → "IMAP2RSS"
4. Copy the 16-character password
5. Use this password in web interface (no spaces)

## 3️⃣ Important Links

### 📰 For FreshRSS:

**Main Feed (all folders):**
```
http://localhost:8888/feed.xml
```

**Specific folder feeds:**
```
http://localhost:8888/INBOX.xml
http://localhost:8888/Sent.xml
http://localhost:8888/Work.xml
```

**List of all feeds:**
```
http://localhost:8888/
```

### 🎛️ Configuration Interface:
```
http://localhost:9999
```

### 📊 System Status:
```
http://localhost:9999/status
```

### 🩺 Health Check:
```
http://localhost:8888/health
```

## 4️⃣ Folder Configuration

### 📁 Gmail - Typical Folders:
In the web interface (http://localhost:9999):

**Basic example:**
```
INBOX
```

**Example with categories:**
```
INBOX,CATEGORY_PERSONAL,CATEGORY_SOCIAL,CATEGORY_UPDATES
```

**Example with labels:**
```
INBOX,Work,Tech,Projects,[Gmail]/Sent Mail
```

### 📋 Feed Modes:
- **Combined:** One feed with emails from all folders
- **Separate:** One feed per folder

### 🏷️ How categories work:
- Combined feed: emails tagged with folder category
- Separate feeds: one RSS per folder

## 5️⃣ XML Files

### System Location:
```
./data/feed.xml          # Main feed
./data/INBOX.xml         # INBOX folder feed
./data/Work.xml          # Work folder feed
./data/feeds_index.json  # Feeds index
```

### Container Location:
```
/app/data/feed.xml          # Main feed
/app/data/INBOX.xml         # INBOX folder feed
/app/data/Work.xml          # Work folder feed
/app/data/feeds_index.json  # Feeds index
```

## 6️⃣ Useful Commands

### View logs:
```bash
docker-compose logs -f
```

### Restart:
```bash
docker-compose restart
```

### Stop:
```bash
docker-compose down
```

### Rebuild:
```bash
docker-compose build --no-cache
docker-compose up -d
```

## 7️⃣ Supported Providers

🔐 **Gmail (Recommended):**
- ✅ Free and unlimited IMAP
- ✅ App password required
- ✅ Complete guide: GMAIL_SETUP.md

🔐 **Other providers:**
- Outlook/Hotmail: Free IMAP
- Yahoo: Free IMAP (app password)
- Zoho: Paid plans only

---

✅ **NOW WITH MULTIPLE PROVIDERS!**

🎯 **Gmail is most recommended**
📊 **Updated interface with provider selection**
🏷️ **Automatic configuration detection**