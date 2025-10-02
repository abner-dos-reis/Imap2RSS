# 📁 FOLDER CONFIGURATION EXAMPLES

## 🌟 Recommended Configurations

### 📧 Basic - Standard Folders
```
INBOX, Sent, Drafts, Trash
```
**Result:** 4 RSS feeds + 1 combined feed

### 💼 Work - Professional Organization
```
INBOX, Work/Projects, Work/Meetings, Work/Clients, Sent
```
**Result:** 5 RSS feeds + 1 combined feed

### 🚀 Tech - For Developers
```
INBOX, Tech/Frontend, Tech/Backend, Tech/DevOps, Tech/Newsletters, Work, Personal
```
**Result:** 7 RSS feeds + 1 combined feed

### 🎯 Complete - Advanced Organization
```
INBOX, Work/Projects, Work/Meetings, Work/Administrative, Tech/Frontend, Tech/Backend, Tech/DevOps, Tech/Newsletters, Personal/Family, Personal/Friends, Personal/Shopping, Sent, Drafts
```
**Result:** 13 RSS feeds + 1 combined feed

## 🔧 How to Configure in Gmail

### 1. Creating Labels/Categories in Gmail:
1. Access Gmail
2. Click on "Settings" (gear icon)
3. Go to "Labels" tab
4. Click "Create new label"
5. For nested labels: Use format "Parent/Child"

### 2. Suggested Structure:
```
📁 Tech
  ├── 📁 Frontend
  ├── 📁 Backend
  ├── 📁 DevOps
  └── 📁 Newsletters

📁 Work
  ├── 📁 Projects
  ├── 📁 Meetings
  └── 📁 Clients

📁 Personal
  ├── 📁 Family
  ├── 📁 Friends
  └── 📁 Shopping
```

## 📋 Gmail-Specific Examples

### 💼 Professional Setup
```
INBOX, [Gmail]/Sent Mail, CATEGORY_PERSONAL, CATEGORY_WORK, CATEGORY_UPDATES, CATEGORY_PROMOTIONS
```

### 🎯 Label-Based Organization
```
INBOX, Work/Projects, Work/Meetings, Personal/Family, Tech/Newsletters, [Gmail]/Sent Mail
```

### � Email Marketing/Newsletter Setup
```
INBOX, Newsletters/Tech, Newsletters/Business, Newsletters/Personal, CATEGORY_PROMOTIONS, [Gmail]/Sent Mail
```

## 🔍 How to Find Your Mailbox Names

### Using the Web GUI (Recommended):
1. Go to http://localhost:9999
2. Enter your email credentials
3. Click "🔍 Detect Mailboxes"
4. Copy the exact names shown

### Gmail Category Names:
- `CATEGORY_PERSONAL` - Personal emails
- `CATEGORY_SOCIAL` - Social networks
- `CATEGORY_PROMOTIONS` - Promotional emails
- `CATEGORY_UPDATES` - Updates and notifications
- `CATEGORY_FORUMS` - Forums and mailing lists

### Gmail System Folders:
- `[Gmail]/All Mail` - All messages
- `[Gmail]/Sent Mail` - Sent messages
- `[Gmail]/Drafts` - Draft messages
- `[Gmail]/Spam` - Spam folder
- `[Gmail]/Trash` - Deleted messages
- `[Gmail]/Important` - Important messages
- `[Gmail]/Starred` - Starred messages

## ⚙️ Configuration Tips

### 🎯 Best Practices:
1. **Start simple** - Begin with `INBOX, Sent` and add more later
2. **Use exact names** - Copy names from mailbox detection
3. **Test incrementally** - Add one folder at a time
4. **Monitor logs** - Check `docker compose logs imap2rss` for errors
5. **Restart after changes** - Always restart container after configuration

### 🔄 Feed Modes:

#### Combined Mode (`FEED_MODE=combined`):
- **Single feed** with all emails mixed together
- **Best for:** Simple RSS reader setup
- **Access:** `http://localhost:8888/feed.xml`

#### Separate Mode (`FEED_MODE=separate`):
- **Individual feed** for each mailbox
- **Best for:** Organized reading, multiple categories
- **Access:** `http://localhost:8888/Mailbox_Name.xml`

## 🚀 Quick Start Examples

### Minimal Setup:
```env
MAILBOXES=INBOX
FEED_MODE=combined
```

### Balanced Setup:
```env
MAILBOXES=INBOX, Work, Personal, [Gmail]/Sent Mail
FEED_MODE=separate
```

### Power User Setup:
```env
MAILBOXES=INBOX, Work/Projects, Work/Meetings, Tech/Newsletters, Personal/Family, [Gmail]/Sent Mail, CATEGORY_PERSONAL, CATEGORY_WORK
FEED_MODE=separate
```

## 🔧 Troubleshooting Mailbox Names

### Common Issues:
1. **Spaces in names** - Use exact spacing: `Work Projects` not `Work_Projects`
2. **Special characters** - Copy from mailbox detection
3. **Case sensitivity** - Match exact case
4. **Unicode characters** - App handles UTF-7 decoding automatically

### Testing Mailbox Configuration:
```bash
# Check if mailboxes are detected correctly
docker compose logs imap2rss | grep "Available mailboxes"

# Test with single mailbox first
MAILBOXES=INBOX

# Add more gradually
MAILBOXES=INBOX, Work
```
  ├── 📁 Família
  ├── 📁 Amigos
  └── 📁 Compras
```

### 3. Na GUI do IMAP2RSS, configure:
```
Tech/Frontend, Tech/Backend, Tech/DevOps, Tech/Newsletters, Trabalho/Projetos, Trabalho/Reuniões, Trabalho/Clientes, Pessoal/Família, Pessoal/Amigos, Pessoal/Compras, INBOX, Sent
```

## 📰 Generated RSS Feeds

### Combined Mode (Recommended):
- **feed.xml** - All emails with folder categories
- Each email will have the category of its source folder

### Separate Mode:
- **feed.xml** - Main combined feed
- **Tech_Frontend.xml** - Only Tech/Frontend emails
- **Tech_Backend.xml** - Only Tech/Backend emails
- **Work_Projects.xml** - Only Work/Projects emails
- **etc.**

## 🎯 FreshRSS Usage Tips

### For Combined Feed:
1. Add: `http://localhost:8888/feed.xml`
2. In FreshRSS, emails will appear with categories
3. Use category filters to organize

### For Separate Feeds:
1. Create categories in FreshRSS: "Tech", "Work", "Personal"
2. Add each feed to corresponding category:
   - "Tech" category: `Tech_Frontend.xml`, `Tech_Backend.xml`
   - "Work" category: `Work_Projects.xml`, `Work_Meetings.xml`
   - "Personal" category: `Personal_Family.xml`, `Personal_Friends.xml`

## ⚡ Quick Setup

### 1. Run automatic detection:
- In GUI (http://localhost:9999)
- Fill in email and password
- Click "🔍 Detect Folders"
- Ajuste a lista conforme necessário

### 2. Ou configure manualmente:
```bash
# In the .env file
MAILBOXES=INBOX,Tech/Frontend,Tech/Backend,Trabalho/Projetos,Sent
FEED_MODE=combined
```

### 3. Reinicie e acesse:
```bash
docker-compose restart
```
- Feeds: http://localhost:8888/
- Status: http://localhost:9999/status

## 🚨 Resolução de Problemas

### ❓ Folder not found:
- Check if the folder exists in Zoho
- Use exact names (case-sensitive)
- Para subpastas, use "/" como separador

### ❓ Caracteres especiais:
- Pastas com acentos: use exatamente como no Zoho
- Espaços: são permitidos
- Caracteres especiais nos arquivos são normalizados

### ❓ Muitas pastas:
- Recomendado: máximo 10-15 pastas
- Para mais pastas, considere usar filtros
- Monitor de performance via logs

## 📊 Monitoramento

### Verificar feeds gerados:
```bash
ls -la ./data/
```

### Ver logs:
```bash
docker-compose logs -f
```

### Status via API:
```bash
curl http://localhost:8888/feeds.json
```