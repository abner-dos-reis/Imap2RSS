# 📧 GMAIL SETUP - COMPLETE GUIDE

## ⚠️ **IMPORTANT: Gmail requires special configuration!**

Gmail doesn't allow direct password login. You need to:
1. **Enable IMAP** in settings
2. **Enable 2-Step Verification**
3. **Create an app password**

## 🚀 **REQUIRED STEPS**

### 1. **Enable IMAP in Gmail**
1. Go to [Gmail](https://mail.google.com)
2. Click the **gear icon** (⚙️) → **See all settings**
3. Go to **Forwarding and POP/IMAP** tab
4. In **IMAP Access** section → **Enable IMAP**
5. Click **Save Changes**

### 2. **Enable 2-Step Verification**
1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. In the **How you sign in to Google** section
3. Click on **2-Step Verification**
4. **Enable** 2-step verification
5. Set up SMS, authenticator app, or security key

### 3. **Create App Password**
1. Still at [myaccount.google.com/security](https://myaccount.google.com/security)
2. In the **How you sign in to Google** section
3. Click on **App passwords**
4. **Select app** → **Other (Custom name)**
5. Type: `IMAP2RSS` or `RSS Converter`
6. Click **Generate**
7. **📋 COPY** the 16-character password (ex: `abcd efgh ijkl mnop`)
8. ⚠️ **IMPORTANT:** Use without spaces: `abcdefghijklmnop`

### 4. **Configure in Application**
```bash
# In .env file or GUI
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=abcdefghijklmnop  # App password WITHOUT SPACES
EMAIL_PROVIDER=gmail
```

⚠️ **WARNING:** 
- ❌ DO NOT use your regular Gmail password
- ❌ DO NOT include spaces in app password
- ✅ ONLY use the 16-character app password
- ✅ Verify that IMAP is enabled

## 🎯 **COMPLETE CONFIGURATION**

### Via GUI (Easiest):
1. Access: `http://localhost:9999`
2. **Provider:** Select "Gmail"
3. **Email:** `your-email@gmail.com`
4. **Password:** Paste app password (no spaces)
5. **Folders:** Use "🔍 Detect Folders" or type manually
6. **Save** and restart: `docker-compose restart`

### Via .env:
```bash
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
EMAIL_PROVIDER=gmail
MAILBOXES=INBOX,[Gmail]/Sent Mail,[Gmail]/Drafts
FEED_MODE=combined
```

## 📁 **TYPICAL GMAIL FOLDERS**

### Default Folders:
- `INBOX` - Inbox
- `[Gmail]/Sent Mail` - Sent messages
- `[Gmail]/Drafts` - Draft messages
- `[Gmail]/Spam` - Spam
- `[Gmail]/Trash` - Deleted messages
- `[Gmail]/All Mail` - All messages
- `[Gmail]/Starred` - Starred messages
- `[Gmail]/Important` - Important messages

### Labels/Categories:
- `CATEGORY_PERSONAL` - Personal
- `CATEGORY_SOCIAL` - Social
- `CATEGORY_PROMOTIONS` - Promotions
- `CATEGORY_UPDATES` - Updates
- `CATEGORY_FORUMS` - Forums

### Custom Labels:
- Any label you created (ex: `Work`, `Projects`, `Tech`)

## 🔧 **CONFIGURATION EXAMPLES**

### Basic (Recommended):
```
INBOX
```

### Gmail Categories:
```
INBOX,CATEGORY_PERSONAL,CATEGORY_SOCIAL,CATEGORY_UPDATES
```

### With Custom Labels:
```
INBOX,Work,Tech,Projects,[Gmail]/Sent Mail
```

### Complete:
```
INBOX,CATEGORY_PERSONAL,CATEGORY_SOCIAL,CATEGORY_PROMOTIONS,Work,Tech,Projects,[Gmail]/Sent Mail,[Gmail]/Starred
```

## ⚡ **QUICK TEST**

1. **Run:**
```bash
docker-compose up -d
```

2. **Configure via GUI:**
- URL: `http://localhost:9999`
- Provider: Gmail
- Use automatic folder detection

3. **Test:**
- Status: `http://localhost:9999/status`
- Feed: `http://localhost:8888/feed.xml`

## 🚨 **TROUBLESHOOTING GMAIL**

### ❌ **"Invalid credentials" or "Authentication failed":**
1. ✅ **Check IMAP enabled:** Gmail → Settings → IMAP active?
2. ✅ **2-step verification active:** [Check here](https://myaccount.google.com/security)
3. ✅ **App password correct:** No spaces, 16 characters
4. ✅ **Email correct:** Full @gmail.com address
5. ✅ **Don't use regular password:** Only app password

### ❌ **"IMAP access is disabled":**
1. Go to Gmail → ⚙️ → See all settings
2. **Forwarding and POP/IMAP** tab
3. **Enable IMAP** → Save

### ❌ **"Less secure app access":**
- ✅ Gmail **NO LONGER** allows "less secure apps"
- ✅ **MUST** use app password
- ✅ **MUST** have 2-step verification

### ❌ **Folders not found:**
1. Use "🔍 Detect Folders" in GUI
2. English names: `[Gmail]/Sent Mail` (not "Enviados")
3. Categorias: `CATEGORY_PERSONAL`, `CATEGORY_SOCIAL`, etc.

### ❌ **Erro de conexão:**
1. ✅ Internet funcionando?
2. ✅ Servidor: `imap.gmail.com` porta `993`
3. ✅ Firewall bloqueando?

## 📱 **APLICATIVO MÓVEL**

Se usar app Gmail no celular, pode precisar:
1. Configurações → Gerenciar conta
2. Segurança → Acesso de app menos seguro → Desabilitar
3. Usar senhas de aplicativo sempre

## 🔒 **SEGURANÇA**

- ✅ **Nunca** compartilhe a senha de aplicativo
- ✅ Se comprometer, revogue e crie nova
- ✅ Use nomes descritivos para as senhas de app
- ✅ Monitor atividade da conta regularmente

## 🎉 **PRONTO!**

Agora você tem Gmail integrado com IMAP2RSS:
- 📧 Emails convertidos para RSS
- 🏷️ Categories preservadas
- 📱 Atualizações automáticas
- 🔄 Sincronização contínua

**Para FreshRSS:** Use `http://localhost:8888/feed.xml` 🚀