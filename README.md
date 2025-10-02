# IMAP to RSS Converter

A Docker application that converts IMAP emails into RSS feeds for integration with RSS readers like FreshRSS.

![IMAP2RSS Screenshot](screenshots/Screenshot2.png)

## 🌟 Features

- ✅ **Multiple email providers** support (Gmail, Outlook, Yahoo, Zoho)
- ✅ **Automatic provider configuration** with smart defaults
- ✅ **Multiple mailboxes/folders support** with proper UTF-7 decoding
- ✅ **Separate RSS feeds per folder or combined feed**
- ✅ **Web GUI for easy configuration** with mailbox auto-detection
- ✅ **Docker Compose ready** with persistent data
- ✅ **Security-focused** with localhost-only access by default
- ✅ **Automatic periodic updates** (configurable interval)
- ✅ **HTML and plain text email support**
- ✅ **Proper RSS 2.0 compliance** for RSS reader compatibility
- ✅ **Built-in HTTP server** for serving RSS feeds
- ✅ **Health check endpoint** for monitoring

## 📸 Screenshots

### Configuration Interface
The web interface provides an easy way to configure your email settings and manage RSS feeds:

| Provider Selection | Email Settings | Mailbox Detection |
|-------------------|----------------|-------------------|
| ![Provider Selection](screenshots/Screenshot1.png) | ![Email Settings](screenshots/Screenshot2.png) | ![Mailbox Detection](screenshots/Screenshot3.png) |

### RSS Feeds Dashboard
View all your available RSS feeds and access them directly:

| RSS Feed List | Status Dashboard |
|---------------|-----------------|
| ![RSS Feed List](screenshots/Screenshot4.png) | ![Status Dashboard](screenshots/Screenshot5.png) |

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/your-username/imap2rss.git
cd imap2rss

# Copy example configuration
cp .env.example .env
```

### 2. Configure Your Email Credentials

Edit the `.env` file with your email settings:

```bash
# Required - Your email credentials
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
EMAIL_PROVIDER=gmail

# Optional - Customization
MAILBOXES=INBOX
FEED_MODE=combined
FEED_TITLE=My Email RSS Feed
FEED_DESCRIPTION=RSS feed generated from my emails
MAX_EMAILS=50
CHECK_INTERVAL=300
```

### 3. Start with Docker Compose

```bash
# Start the application
docker compose up -d

# Check logs
docker compose logs -f imap2rss
```

### 4. Access the Application

- **Configuration GUI**: http://localhost:9999
- **RSS Feeds**: http://localhost:8888
- **Health Check**: http://localhost:8888/health

## 📧 Email Provider Setup

### Gmail Setup (Recommended)

1. **Enable 2-Factor Authentication** in your Google Account
2. **Generate App Password**:
   - Go to Google Account → Security → 2-Step Verification → App passwords
   - Select "Mail" and generate password
   - Use the generated 16-character password (e.g., `abcd efgh ijkl mnop`)
3. **Enable IMAP** in Gmail settings (Settings → Forwarding and POP/IMAP)

```env
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-16-char-app-password
EMAIL_PROVIDER=gmail
```

### Other Providers

<details>
<summary>Outlook/Hotmail</summary>

```env
EMAIL_USER=your-email@outlook.com
EMAIL_PASS=your-password
EMAIL_PROVIDER=outlook
```
</details>

<details>
<summary>Yahoo Mail</summary>

```env
EMAIL_USER=your-email@yahoo.com
EMAIL_PASS=your-app-password
EMAIL_PROVIDER=yahoo
```
</details>

<details>
<summary>Custom IMAP Server</summary>

```env
EMAIL_USER=your-email@example.com
EMAIL_PASS=your-password
EMAIL_PROVIDER=custom
IMAP_SERVER=mail.example.com
IMAP_PORT=993
```
</details>

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `EMAIL_USER` | - | **Required**: Your email address |
| `EMAIL_PASS` | - | **Required**: Your email password/app password |
| `EMAIL_PROVIDER` | `gmail` | Email provider: `gmail`, `outlook`, `yahoo`, `zoho`, `custom` |
| `IMAP_SERVER` | Auto | IMAP server hostname (auto-configured by provider) |
| `IMAP_PORT` | `993` | IMAP server port |
| `MAILBOXES` | `INBOX` | Comma-separated list of mailboxes to monitor |
| `FEED_MODE` | `combined` | `combined` (single feed) or `separate` (one feed per mailbox) |
| `FEED_TITLE` | `Email RSS Feed` | RSS feed title |
| `FEED_DESCRIPTION` | `RSS feed generated...` | RSS feed description |
| `MAX_EMAILS` | `50` | Maximum emails per feed |
| `CHECK_INTERVAL` | `300` | Check interval in seconds (5 minutes) |
| `HTTP_PORT` | `8888` | RSS server port |
| `CONFIG_PORT` | `9999` | Configuration GUI port |
| `RUN_MODE` | `daemon` | `daemon` (continuous) or `once` (single run) |

### Feed Modes

#### Combined Mode
- **Single RSS feed** with emails from all mailboxes
- Access: `http://localhost:8888/feed.xml`
- Best for: Simple setups, single RSS subscription

#### Separate Mode
- **Individual RSS feed** for each mailbox
- Access: `http://localhost:8888/Mailbox_Name.xml`
- Best for: Organizing emails by categories, multiple RSS subscriptions

### Mailbox Configuration

#### Using the Web GUI (Recommended)
1. Go to http://localhost:9999
2. Enter your email credentials
3. Click "🔍 Detect Mailboxes" to auto-discover available folders
4. Select desired mailboxes
5. Click "Save Configuration"
6. **Restart the container** to apply changes

#### Manual Configuration
Edit the `MAILBOXES` variable in `.env`:

```env
# Single mailbox
MAILBOXES=INBOX

# Multiple mailboxes
MAILBOXES=INBOX, Sent, Work, Personal

# Gmail categories/labels
MAILBOXES=INBOX, [Gmail]/Sent Mail, CATEGORY_PERSONAL, CATEGORY_WORK
```

## 🔄 Important: Restart Required

**Why restart is needed after configuration changes:**

1. **Container reads `.env` at startup** - Environment variables are loaded once when the container starts
2. **Docker Compose volume mounting** - The `.env` file is mounted as a volume, but changes require container restart to take effect
3. **Process environment** - The Python processes need to reload their environment variables

**How to restart:**
```bash
# Method 1: Restart the container
docker compose restart imap2rss

# Method 2: Stop and start
docker compose down
docker compose up -d

# Check if changes were applied
docker compose logs imap2rss
```

## 🔗 RSS Reader Integration

### FreshRSS Integration

1. **Single Feed (Combined Mode)**:
   ```
   http://localhost:8888/feed.xml
   ```

2. **Multiple Feeds (Separate Mode)**:
   ```
   http://localhost:8888/INBOX.xml
   http://localhost:8888/Work_Folder.xml
   http://localhost:8888/Personal_Emails.xml
   ```

3. **Category Organization**: Create categories in FreshRSS and assign feeds accordingly

### Other RSS Readers

The application generates standard RSS 2.0 feeds compatible with:
- FreshRSS
- Feedly
- Inoreader
- NewsBlur
- Any RSS 2.0 compatible reader

## 📁 Project Structure

```
imap2rss/
├── app.py              # Main IMAP to RSS converter
├── server.py           # HTTP server for RSS feeds
├── config_gui.py       # Web configuration interface
├── entrypoint.sh       # Docker entrypoint script
├── Dockerfile          # Docker image definition
├── docker-compose.yml  # Docker Compose configuration
├── requirements.txt    # Python dependencies
├── .env                # Environment configuration
├── .env.example        # Example configuration
├── data/               # Persistent data directory
│   ├── *.xml          # Generated RSS feeds
│   └── feeds_index.json # Feed metadata
└── screenshots/        # Documentation images
```

## 🛠️ Development

### Local Development

```bash
# Clone the repository
git clone https://github.com/your-username/imap2rss.git
cd imap2rss

# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run components separately
python app.py          # IMAP converter
python server.py       # RSS server
python config_gui.py   # Configuration GUI
```

### Building Docker Image

```bash
# Build image
docker build -t imap2rss .

# Run with Docker
docker run -d \
  --name imap2rss \
  -p 8888:8888 \
  -p 9999:9999 \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/data:/app/data \
  imap2rss
```

## 🔒 Security Considerations

- **App Passwords**: Always use app-specific passwords, never your main email password
- **Localhost Only**: Default configuration binds to `127.0.0.1` (localhost only)
- **No External Access**: RSS feeds are only accessible from the local machine
- **Credential Protection**: Keep your `.env` file secure and never commit credentials to version control
- **Network Security**: If exposing externally, use proper authentication and HTTPS

## 🐛 Troubleshooting

### Common Issues

#### 1. Authentication Failed
```
ERROR - Failed to connect to IMAP server: authentication failed
```
**Solution**: 
- Verify email and password are correct
- For Gmail: Ensure you're using App Password, not regular password
- Check if 2FA is enabled and app password is generated

#### 2. No Mailboxes Detected
```
INFO - Available mailboxes: ['INBOX']
```
**Solution**:
- Use the web GUI to auto-detect mailboxes
- Check mailbox names are spelled correctly
- Some providers use different naming conventions

#### 3. Container Restart Issues
```
ERROR - Address already in use
```
**Solution**:
```bash
docker compose down
docker compose up -d
```

#### 4. RSS Feed Empty
```
RSS feed generated but shows no items
```
**Solution**:
- Check if emails exist in specified mailboxes
- Verify `MAX_EMAILS` setting
- Check logs for IMAP connection errors

### Debug Mode

Enable detailed logging:
```bash
# Check container logs
docker compose logs -f imap2rss

# Run single conversion
docker compose exec imap2rss python -c "
import os
os.environ['RUN_MODE'] = 'once'
exec(open('app.py').read())
"
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/imap2rss/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/imap2rss/discussions)
- **Email**: [Create an issue](https://github.com/your-username/imap2rss/issues/new) for support requests

## 🙏 Acknowledgments

- Built for seamless integration with [FreshRSS](https://freshrss.org/)
- Inspired by the need for email-to-RSS conversion
- Thanks to all contributors and users providing feedback

---

**Made with ❤️ for the RSS community**

### 4. Acesse o Feed RSS

O feed estará disponível em: `http://localhost:8888/feed.xml`

### 5. 🎨 Interface Web de Configuração (NOVO!)

Acesse a interface gráfica para configurar facilmente: `http://localhost:9999`

- Configuração visual do IMAP
- Status do sistema em tempo real
- Links diretos para o FreshRSS

## 📍 Respostas das suas perguntas:

### 1. **Local dos XMLs:**
- Os arquivos XML são salvos em: `/app/data/feed.xml` (dentro do container)
- No seu sistema: `./data/feed.xml` (pasta data no diretório do projeto)

### 2. **Links para o FreshRSS:**
- **Feed Principal (todas as pastas):** `http://localhost:8888/feed.xml`
- **Feed específico por pasta:** `http://localhost:8888/NomeDaPasta.xml`
- **Lista de todos os feeds:** `http://localhost:8888/`
- **Interface de Configuração:** `http://localhost:9999`
- **Health Check:** `http://localhost:8888/health`

### 3. **Categorias e Pastas:**
- ✅ Monitora múltiplas pastas do Zoho (INBOX, Sent, Trabalho, etc.)
- ✅ Cria categorias automáticas por pasta
- ✅ Modo combinado: um feed com todas as pastas
- ✅ Modo separado: um feed RSS para cada pasta

### 3. **GUI de Configuração:**
- Acesse `http://localhost:9999` para configurar via interface web
- Não precisa mais editar arquivos `.env` manualmente!

## Configuração do Zoho Mail

### Criar Senha de Aplicativo

1. Acesse [Zoho Mail Settings](https://mail.zoho.com/zm/#settings/security)
2. Vá em **Security** → **App Passwords**
3. Clique em **Generate New Password**
4. Escolha um nome (ex: "RSS Converter")
5. Copie a senha gerada e use no arquivo `.env`

### Configurações IMAP do Zoho

- **Servidor**: `imap.zoho.com`
- **Porta**: `993`
- **SSL**: Sim

## Integração com FreshRSS

1. Acesse seu FreshRSS
2. Vá em **Subscription management** → **Add a subscription**
3. Cole a URL: `http://localhost:8888/feed.xml`
4. Configure a categoria e outras opções conforme desejado

## 🎨 Interface Web de Configuração

### Acesso à GUI
- **URL:** `http://localhost:9999`
- **Recursos:**
  - ✅ Configuração visual de todas as opções
  - ✅ Status do sistema em tempo real
  - ✅ Verificação do arquivo RSS
  - ✅ Links diretos para copiar
  - ✅ Validação de campos obrigatórios

### Como Usar a GUI
1. Acesse `http://localhost:9999`
2. Preencha email e senha de aplicativo do Zoho
3. Ajuste outras configurações se necessário
4. Clique em "Salvar Configuração"
5. Reinicie o container: `docker-compose restart`
6. Verifique o status em: `http://localhost:9999/status`

## Configurações Avançadas

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|---------|
| `EMAIL_USER` | Usuário do email (obrigatório) | - |
| `EMAIL_PASS` | Senha do email (obrigatório) | - |
| `IMAP_SERVER` | Servidor IMAP | `imap.zoho.com` |
| `IMAP_PORT` | Porta IMAP | `993` |
| `MAILBOXES` | Pastas para monitorar (separadas por vírgula) | `INBOX` |
| `FEED_MODE` | Modo de feed: `combined` ou `separate` | `combined` |
| `FEED_TITLE` | Título do feed RSS | `Email RSS Feed` |
| `FEED_DESCRIPTION` | Descrição do feed | `RSS feed generated from IMAP emails` |
| `MAX_EMAILS` | Máximo de emails no feed | `50` |
| `HTTP_PORT` | Porta do servidor HTTP | `8888` |
| `CHECK_INTERVAL` | Intervalo de verificação (segundos) | `300` |

### Outros Provedores de Email

Para usar com outros provedores, ajuste as configurações IMAP:

**Gmail:**
```bash
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
# Use senha de aplicativo, não a senha normal
```

**Outlook/Hotmail:**
```bash
IMAP_SERVER=outlook.office365.com
IMAP_PORT=993
```

**Yahoo:**
```bash
IMAP_SERVER=imap.mail.yahoo.com
IMAP_PORT=993
```

## Estrutura do Projeto

```
Imap2RSS/
├── app.py              # Aplicação principal IMAP→RSS
├── server.py           # Servidor HTTP para servir RSS
├── Dockerfile          # Configuração Docker
├── docker-compose.yml  # Orquestração Docker
├── entrypoint.sh       # Script de inicialização
├── requirements.txt    # Dependências Python
├── .env.example        # Exemplo de configuração
├── data/              # Dados persistentes (criado automaticamente)
│   └── feed.xml       # Feed RSS gerado
└── README.md          # Esta documentação
```

## Comandos Úteis

### Verificar logs
```bash
docker-compose logs -f
```

### Verificar status
```bash
docker-compose ps
```

### Reiniciar serviço
```bash
docker-compose restart
```

### Parar serviço
```bash
docker-compose down
```

### Reconstruir imagem
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Testar conectividade
```bash
curl http://localhost:8888/health
curl http://localhost:8888/feed.xml
```

## Troubleshooting

### Erro de autenticação
- Verifique se o `EMAIL_USER` e `EMAIL_PASS` estão corretos
- Para Zoho, certifique-se de usar uma senha de aplicativo, não a senha normal
- Verifique se o IMAP está habilitado na sua conta

### Feed vazio
- Verifique se há emails na caixa configurada (`MAILBOX`)
- Confira os logs: `docker-compose logs`
- Teste a conectividade IMAP manualmente

### Porta em uso
- A porta 8888 está em uso? Mude no `docker-compose.yml`:
```yaml
ports:
  - "9999:8888"  # Usa porta 9999 externamente
```

### Erro de SSL/TLS
- Verifique se o servidor IMAP e porta estão corretos
- Alguns provedores podem exigir configurações específicas de SSL

## Segurança

- ✅ Nunca commite o arquivo `.env` com credenciais
- ✅ Use senhas de aplicativo quando disponíveis
- ✅ O servidor HTTP é apenas local por padrão
- ⚠️ Para exposição externa, considere adicionar autenticação

## Limitações

- O feed RSS é gerado localmente - não há persistência em banco de dados
- Formato de email muito complexo pode não ser convertido perfeitamente
- Anexos não são processados no feed RSS

## Suporte

Para problemas ou sugestões, verifique:

1. **Logs do container**: `docker-compose logs`
2. **Saúde do serviço**: `curl http://localhost:8888/health`
3. **Conectividade**: teste manualmente as configurações IMAP

## License

MIT License