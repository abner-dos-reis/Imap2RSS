# 📧➡️📰 IMAP2RSS - Email to RSS Converter

Transform your email newsletters into RSS feeds for better organization and reading experience!

![IMAP2RSS Interface](screenshots/Screenshot2.png)

## 🎯 What Does This Do?

**IMAP2RSS** converts emails from your inbox into RSS feeds that you can read in any RSS reader like FreshRSS, Feedly, or Inoreader. Perfect for newsletters, notifications, and any email content you want to organize better.

### 💡 Perfect For
- 📰 **Newsletters**: LinkedIn, Substack, Medium, The Hustle
- 🔔 **Notifications**: GitHub, project updates, system alerts
- 📊 **Reports**: Business updates, analytics, monitoring alerts
- 📧 **Email organization**: Keep inbox clean while reading content in RSS

### ✨ Why Email → RSS?
- **📖 Better reading experience** in dedicated RSS readers
- **🗂️ Better organization** with categories and folders
- **📱 Offline reading** - download for later
- **🧹 Clean inbox** - email stays organized
- **🔍 Advanced filtering** - powerful RSS reader features

## 🚀 Quick Start (3 Steps)

### 1. Start the Container
```bash
git clone https://github.com/abner-dos-reis/Imap2RSS.git
cd Imap2RSS
docker compose up -d
```

### 2. Initial Configuration
1. 🌐 Open **http://localhost:9999**
2. 📧 Enter your **email credentials** 
3. 🔍 Click **"Detect Mailboxes"** to find your folders
4. 💾 **Save Configuration**
5. 🔄 Run `docker compose restart`

### 3. Performance Optimization  
1. 🌐 Go back to **http://localhost:9999**
2. ⏱️ Set **"Check Interval" to "1 minute"** (don't detect mailboxes again!)
3. 💾 **Save Configuration**

**📥 Your RSS feeds are now available at http://localhost:8888**

## ⚠️ Important Setup Notes

### Why the 8-Step Process?
The configuration requires **2 saves** because:
1. **First save**: Stores email credentials and mailbox configuration
2. **Restart**: Required to apply mailbox settings to the container
3. **Second save**: Optimizes check interval (without restart, it resets to default 5 minutes)

> **This is a current limitation that will be fixed in a future update**

### Email Provider Setup

#### 📧 Gmail (Recommended)
1. Enable **2-Factor Authentication**
2. Generate **App Password**: Google Account → Security → 2-Step Verification → App passwords
3. Use the **16-character password** (not your regular password)

#### 📧 Other Providers
- **Outlook/Hotmail**: Use regular password or app password if 2FA enabled
- **Yahoo**: Generate app password in Account Security settings
- **Custom IMAP**: Configure server settings manually

## 🔧 Features

| Feature | Description |
|---------|-------------|
| 🔄 **Multiple Email Providers** | Gmail, Outlook, Yahoo, Zoho, Custom IMAP |
| 📁 **Multiple Mailboxes** | Monitor multiple folders/labels |
| 🎛️ **Feed Modes** | Combined feed or separate feeds per mailbox |
| 🌐 **Web Configuration** | Easy setup via web interface |
| 🐳 **Docker Ready** | Full Docker Compose setup |
| 🔒 **Secure** | Localhost-only access by default |
| ⏰ **Configurable Interval** | Set how often to check for emails |
| 🔗 **HTML Preservation** | Keeps links and formatting in RSS |
| 📊 **RSS 2.0 Standard** | Compatible with all RSS readers |

## 📡 Using Your RSS Feeds

### RSS Feed URLs
- **Combined feed**: `http://localhost:8888/feed.xml`
- **Individual mailboxes**: `http://localhost:8888/INBOX.xml`
- **Feed index**: `http://localhost:8888/` (lists all available feeds)

### Integration Examples

#### FreshRSS
1. Add subscription: `http://localhost:8888/feed.xml`
2. Create categories for different mailboxes
3. Set up filters for automatic organization

#### Other RSS Readers
Works with any RSS 2.0 compatible reader:
- Feedly, Inoreader, NewsBlur, etc.

## 📁 Configuration Options

### Environment Variables (.env file)
```bash
# Required
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
EMAIL_PROVIDER=gmail

# Optional
MAILBOXES=INBOX,Work,Personal    # Comma-separated
FEED_MODE=combined               # or 'separate'
CHECK_INTERVAL=60                # seconds (1 minute = optimal)
MAX_EMAILS=50                    # per feed
```

### Feed Modes
- **Combined**: Single RSS feed with all emails (organized by folder)
- **Separate**: Individual RSS feed for each mailbox

## 🔧 Customization

### Mailbox Selection
Use the web GUI to detect and select mailboxes, or manually configure:
```bash
# Gmail examples
MAILBOXES=INBOX,[Gmail]/Sent Mail,CATEGORY_PERSONAL

# Outlook examples  
MAILBOXES=INBOX,Sent Items,Junk Email

# Multiple folders
MAILBOXES=INBOX,Work,Personal,Newsletters
```

### Check Interval
- **1 minute** (60 seconds): Near real-time updates
- **5 minutes** (300 seconds): Default, good for most use cases
- **15+ minutes**: Light usage, reduces server load

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| **Authentication failed** | Use app password (not regular password) for Gmail |
| **No mailboxes detected** | Use web GUI to auto-detect available folders |
| **RSS feeds empty** | Check email credentials and mailbox names |
| **Still slow after setup** | Verify check interval is set to 1 minute |
| **Container won't restart** | Run `docker compose down && docker compose up -d` |

### Debug Commands
```bash
# Check container status
docker compose ps

# View logs  
docker compose logs -f app

# Restart container
docker compose restart

# Check environment variables
docker compose exec app env | grep EMAIL
```

## 🔒 Security

- ✅ **App passwords only** - never use main email password
- ✅ **Localhost binding** - accessible only from local machine  
- ✅ **No external exposure** - RSS feeds not accessible from internet
- ✅ **Credential protection** - keep .env file secure

## 📊 Project Structure

```
Imap2RSS/
├── 🐳 docker-compose.yml     # Container orchestration
├── 🐍 app.py                 # Main IMAP→RSS converter  
├── 🌐 config_gui.py          # Web configuration interface
├── 📡 server.py              # RSS feed HTTP server
├── ⚙️ .env                   # Configuration file
├── 📁 data/                  # Generated RSS feeds
│   ├── feed.xml             # Combined RSS feed
│   ├── INBOX.xml           # Mailbox-specific feeds
│   └── feeds_index.json    # Feed metadata
└── 📸 screenshots/          # Documentation images
```

## 🆘 Getting Help

- **🐛 Issues**: [GitHub Issues](https://github.com/abner-dos-reis/Imap2RSS/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/abner-dos-reis/Imap2RSS/discussions)
- **📧 Email**: Create an issue for support

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

---

### 🌟 Star this project if it helps you organize your email better!