#!/usr/bin/env python3
"""
Web GUI for IMAP to RSS configuration with multiple email providers
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import urllib.parse
import logging
from datetime import datetime
import imaplib
import base64
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_env_file():
    """Load environment variables from .env file"""
    env_file = '/app/.env'
    if not os.path.exists(env_file):
        env_file = './.env'
    if os.path.exists(env_file):
        logger.info(f"Loading environment variables from {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    logger.debug(f"Set {key}={value[:20]}...")
    else:
        logger.warning("No .env file found")

# Load .env file before doing anything else
load_env_file()

def decode_imap_utf7(s):
    """Decode IMAP modified UTF-7 string to normal UTF-8"""
    try:
        # Handle modified UTF-7 encoding used by IMAP
        # Replace & with + and &- with &
        s = s.replace('&-', '&')
        # Handle other encoded parts
        def decode_match(match):
            encoded = match.group(1)
            try:
                # Add padding if needed
                missing_padding = len(encoded) % 4
                if missing_padding:
                    encoded += '=' * (4 - missing_padding)
                decoded_bytes = base64.b64decode(encoded, validate=True)
                return decoded_bytes.decode('utf-16-be')
            except:
                return match.group(0)  # Return original if decode fails
        
        # Replace &<base64>- patterns
        result = re.sub(r'&([A-Za-z0-9+/=]+)-', decode_match, s)
        return result
    except Exception as e:
        logger.debug(f"Failed to decode IMAP UTF-7: {s} -> {e}")
        return s  # Return original string if decode fails

class ConfigHandler(BaseHTTPRequestHandler):
    
    # Email provider configurations
    EMAIL_PROVIDERS = {
        'gmail': {
            'name': 'Gmail',
            'server': 'imap.gmail.com',
            'port': 993,
            'instructions': 'Gmail: Enable IMAP in settings + Use app password (not regular password). See complete guide.'
        },
        'outlook': {
            'name': 'Outlook/Hotmail',
            'server': 'outlook.office365.com', 
            'port': 993,
            'instructions': 'Use your regular password or app password if you have 2FA enabled'
        },
        'yahoo': {
            'name': 'Yahoo Mail',
            'server': 'imap.mail.yahoo.com',
            'port': 993,
            'instructions': 'Use an app password. Go to: Settings → Account Security → Generate app password'
        },
        'zoho': {
            'name': 'Zoho Mail',
            'server': 'imap.zoho.com',
            'port': 993,
            'instructions': 'Free Zoho does not support IMAP. Use paid plan or another provider'
        },
        'custom': {
            'name': 'Customizado',
            'server': '',
            'port': 993,
            'instructions': 'Configure your IMAP server manually'
        }
    }
    
    def do_GET(self):
        if self.path == '/' or self.path == '/config':
            self.serve_config_page()
        elif self.path == '/status':
            self.serve_status_page()
        elif self.path.startswith('/static/'):
            self.serve_static()
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/save-config':
            self.save_configuration()
        elif self.path == '/detect-mailboxes':
            self.detect_mailboxes()
        else:
            self.send_error(404)
    
    def serve_config_page(self):
        """Serve the configuration page"""
        config = self.load_current_config()
        
        # Build provider options
        provider_options = ''
        current_provider = config.get('EMAIL_PROVIDER', 'gmail')
        for key, provider in self.EMAIL_PROVIDERS.items():
            selected = 'selected' if key == current_provider else ''
            provider_options += f'<option value="{key}" {selected}>{provider["name"]}</option>'
        
        # Build JavaScript providers object
        providers_js = json.dumps(self.EMAIL_PROVIDERS, indent=8)
        
        html_template = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IMAP2RSS - Configuration</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ 
            max-width: 800px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 15px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{ 
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white; 
            text-align: center; 
            padding: 30px;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; font-size: 1.1em; }}
        .content {{ padding: 40px; }}
        .form-group {{ margin-bottom: 25px; }}
        .form-group label {{ 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 600; 
            color: #333;
            font-size: 1.1em;
        }}
        .form-group input, .form-group select, .form-group textarea {{ 
            width: 100%; 
            padding: 12px 15px; 
            border: 2px solid #e1e5e9; 
            border-radius: 8px; 
            font-size: 1em;
            transition: border-color 0.3s;
        }}
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {{ 
            outline: none; 
            border-color: #4CAF50;
            box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
        }}
        .form-group small {{ 
            display: block; 
            margin-top: 5px; 
            color: #666; 
            font-size: 0.9em;
        }}
        .section {{ 
            border: 1px solid #e1e5e9; 
            border-radius: 10px; 
            padding: 25px; 
            margin-bottom: 25px;
            background: #f8f9fa;
        }}
        .section h3 {{ 
            color: #4CAF50; 
            margin-bottom: 20px; 
            font-size: 1.3em;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .btn {{ 
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white; 
            padding: 15px 30px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 1.1em;
            font-weight: 600;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
        }}
        .btn:hover {{ 
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
        }}
        .btn-secondary {{ 
            background: linear-gradient(45deg, #2196F3, #1976D2);
            margin-left: 10px;
            width: auto;
            min-width: 150px;
        }}
        .status-info {{ 
            background: #e3f2fd; 
            border-left: 4px solid #2196F3; 
            padding: 15px; 
            margin-bottom: 20px;
            border-radius: 0 8px 8px 0;
        }}
        .status-info h4 {{ color: #1976D2; margin-bottom: 10px; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .required {{ color: #f44336; }}
        .button-group {{ display: flex; justify-content: space-between; align-items: center; }}
        .gmail-warning {{
            background: #f8d7da; 
            border-left: 4px solid #dc3545; 
            padding: 15px; 
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }}
        .gmail-warning h4 {{ color: #721c24; margin-bottom: 10px; }}
        .gmail-warning p {{ color: #721c24; margin-bottom: 8px; }}
        @media (max-width: 768px) {{
            .grid {{ grid-template-columns: 1fr; }}
            .button-group {{ flex-direction: column; gap: 10px; }}
            .btn-secondary {{ margin-left: 0; width: 100%; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📧 IMAP2RSS</h1>
            <p>Configure your Email to RSS conversion</p>
        </div>
        
        <div class="content">
            <div class="status-info">
                <h4>📍 How to use:</h4>
                <p><strong>1.</strong> Select your email provider</p>
                <p><strong>2.</strong> Configure email and password</p>
                <p><strong>3.</strong> Choose folders to monitor</p>
                <p><strong>4.</strong> Save and restart: <code>docker-compose restart</code></p>
                <p><strong>5.</strong> Access: <a href="http://localhost:8888/" target="_blank">View all feeds</a></p>
            </div>
            
            <form id="configForm" method="POST" action="/save-config">
                <div class="section">
                    <h3>📧 Email Provider</h3>
                    
                    <div class="form-group">
                        <label for="email_provider">Email Provider</label>
                        <select id="email_provider" name="email_provider" onchange="updateProviderSettings()">
                            {provider_options}
                        </select>
                        <small id="provider_instructions">{current_instructions}</small>
                    </div>
                </div>
                
                <div id="gmail-checklist" class="gmail-warning" style="display: none;">
                    <h4>✅ REQUIRED GMAIL CHECKLIST:</h4>
                    <p><strong>□ 1.</strong> IMAP enabled: Gmail → ⚙️ → Settings → Forwarding and POP/IMAP → Enable IMAP</p>
                    <p><strong>□ 2.</strong> 2-Step Verification: <a href="https://myaccount.google.com/security" target="_blank" style="color: #0d6efd;">Google Account → Security</a></p>
                    <p><strong>□ 3.</strong> App password: App passwords → Other → "IMAP2RSS" → Generate</p>
                    <p><strong>□ 4.</strong> Use 16-character password <strong>WITHOUT SPACES</strong> (ex: abcdefghijklmnop)</p>
                    <p><strong>❌ DO NOT use your regular Gmail password!</strong></p>
                </div>
                
                <div class="section">
                    <h3>🔐 Email Settings (Required)</h3>
                    
                    <div class="form-group">
                        <label for="email_user">Email <span class="required">*</span></label>
                        <input type="email" id="email_user" name="email_user" value="{email_user}" required>
                        <small>Your complete email (ex: user@gmail.com)</small>
                    </div>
                    
                    <div class="form-group">
                        <label for="email_pass">Password <span class="required">*</span></label>
                        <input type="password" id="email_pass" name="email_pass" value="{email_pass}" required>
                        <small id="password_help">For Gmail: use app password (16 characters WITHOUT spaces)</small>
                    </div>
                </div>
                
                <div class="section">
                    <h3>⚙️ IMAP Settings (Automatic)</h3>
                    
                    <div class="grid">
                        <div class="form-group">
                            <label for="imap_server">IMAP Server</label>
                            <input type="text" id="imap_server" name="imap_server" value="{imap_server}" readonly>
                            <small>Automatically configured based on provider</small>
                        </div>
                        
                        <div class="form-group">
                            <label for="imap_port">IMAP Port</label>
                            <input type="number" id="imap_port" name="imap_port" value="{imap_port}" readonly>
                            <small>Default SSL port (993)</small>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="mailboxes">Email Folders (comma-separated)</label>
                        <input type="text" id="mailboxes" name="mailboxes" value="{mailboxes}" placeholder="INBOX, CATEGORY_PERSONAL, Work">
                        <small>
                            <strong>📁 Gmail - Examples:</strong><br>
                            • <code>INBOX</code> - Main inbox<br>
                            • <code>INBOX, CATEGORY_PERSONAL, CATEGORY_SOCIAL</code> - With categories<br>
                            • <code>INBOX, [Gmail]/Sent Mail, Work</code> - With custom labels<br>
                            <strong>💡 Tip:</strong> Use "🔍 Detect Folders" to see all available
                        </small>
                    </div>
                    
                    <div class="form-group">
                        <label for="feed_mode">Feed Mode</label>
                        <select id="feed_mode" name="feed_mode">
                            <option value="combined" {combined_selected}>Combined (one feed with all folders)</option>
                            <option value="separate" {separate_selected}>Separate (one feed per folder)</option>
                        </select>
                        <small>Combined: single RSS with emails from all folders. Separate: one RSS per folder</small>
                    </div>
                </div>
                
                <div class="section">
                    <h3>📰 RSS Feed Settings</h3>
                    
                    <div class="form-group">
                        <label for="feed_title">Feed Title</label>
                        <input type="text" id="feed_title" name="feed_title" value="{feed_title}">
                    </div>
                    
                    <div class="form-group">
                        <label for="feed_description">Feed Description</label>
                        <textarea id="feed_description" name="feed_description" rows="3">{feed_description}</textarea>
                    </div>
                    
                    <div class="grid">
                        <div class="form-group">
                            <label for="max_emails">Maximum Emails</label>
                            <input type="number" id="max_emails" name="max_emails" value="{max_emails}" min="1" max="200">
                            <small>Maximum number of emails in the feed</small>
                        </div>
                        
                        <div class="form-group">
                            <label for="check_interval">Check Interval (minutes)</label>
                            <input type="number" id="check_interval" name="check_interval" value="{check_interval}" min="1" max="1440">
                            <small>Frequency to check for new emails</small>
                        </div>
                    </div>
                </div>
                
                <div class="button-group">
                    <button type="submit" class="btn">💾 Save Configuration</button>
                    <button type="button" class="btn btn-secondary" onclick="detectMailboxes()">🔍 Detect Folders</button>
                    <a href="/status" class="btn btn-secondary">📊 View Status</a>
                    <a href="https://myaccount.google.com/security" target="_blank" class="btn btn-secondary" style="background: linear-gradient(45deg, #db4437, #c23321);">🔐 Config Gmail</a>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        const providers = {providers_js};
        
        function updateProviderSettings() {{
            const provider = document.getElementById('email_provider').value;
            const providerInfo = providers[provider];
            
            if (providerInfo) {{
                document.getElementById('imap_server').value = providerInfo.server;
                document.getElementById('imap_port').value = providerInfo.port;
                document.getElementById('provider_instructions').textContent = providerInfo.instructions;
                
                // Show/hide Gmail checklist
                const gmailChecklist = document.getElementById('gmail-checklist');
                if (provider === 'gmail') {{
                    gmailChecklist.style.display = 'block';
                    document.getElementById('password_help').textContent = 'Gmail: Use app password (16 characters WITHOUT spaces). See checklist above.';
                }} else {{
                    gmailChecklist.style.display = 'none';
                    if (provider === 'yahoo') {{
                        document.getElementById('password_help').textContent = 'Use a Yahoo app password, not your normal password';
                    }} else if (provider === 'outlook') {{
                        document.getElementById('password_help').textContent = 'Use your normal password or app password if you have 2FA';
                    }} else if (provider === 'zoho') {{
                        document.getElementById('password_help').textContent = 'WARNING: Free Zoho does not support IMAP!';
                    }} else {{
                        document.getElementById('password_help').textContent = 'Configure your provider credentials';
                    }}
                }}
                
                // Enable/disable server fields for custom provider
                const isCustom = provider === 'custom';
                document.getElementById('imap_server').readOnly = !isCustom;
                document.getElementById('imap_port').readOnly = !isCustom;
            }}
        }}
        
        // Initialize on page load
        updateProviderSettings();
        
        function detectMailboxes() {{
            const emailUser = document.getElementById('email_user').value;
            const emailPass = document.getElementById('email_pass').value;
            const emailProvider = document.getElementById('email_provider').value;
            
            if (!emailUser || !emailPass) {{
                alert('⚠️ Please fill in email and password before detecting folders.');
                return;
            }}
            
            const button = event.target;
            const originalText = button.textContent;
            button.textContent = '🔄 Detectando...';
            button.disabled = true;
            
            const formData = new URLSearchParams();
            formData.append('email_user', emailUser);
            formData.append('email_pass', emailPass);
            formData.append('email_provider', emailProvider);
            
            fetch('/detect-mailboxes', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/x-www-form-urlencoded'
                }},
                body: formData
            }})
            .then(response => response.json())
            .then(data => {{
                button.textContent = originalText;
                button.disabled = false;
                
                if (data.success) {{
                    document.getElementById('mailboxes').value = data.mailboxes.join(', ');
                    alert(`✅ Found ${{data.mailboxes.length}} folders:\\n\\n${{data.mailboxes.join('\\n')}}`);
                }} else {{
                    alert('❌ Error detecting folders: ' + data.error);
                }}
            }})
            .catch(error => {{
                button.textContent = originalText;
                button.disabled = false;
                alert('❌ Error: ' + error);
            }});
        }}
        
        document.getElementById('configForm').addEventListener('submit', function(e) {{
            e.preventDefault();
            
            const formData = new URLSearchParams(new FormData(this));
            
            fetch('/save-config', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/x-www-form-urlencoded'
                }},
                body: formData
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    alert('✅ Configuration saved successfully!\\n\\nRestart the container to apply changes:\\ndocker-compose restart\\n\\nThen access: http://localhost:8888/');
                }} else {{
                    alert('❌ Error saving: ' + data.error);
                }}
            }})
            .catch(error => {{
                alert('❌ Error: ' + error);
            }});
        }});
    </script>
</body>
</html>'''

        # Fill in template variables
        html = html_template.format(
            provider_options=provider_options,
            providers_js=providers_js,
            current_instructions=self.EMAIL_PROVIDERS.get(current_provider, {}).get('instructions', ''),
            email_user=config.get('EMAIL_USER', ''),
            email_pass=config.get('EMAIL_PASS', ''),
            imap_server=config.get('IMAP_SERVER', 'imap.gmail.com'),
            imap_port=config.get('IMAP_PORT', '993'),
            mailboxes=config.get('MAILBOXES', 'INBOX'),
            combined_selected='selected' if config.get('FEED_MODE', 'combined') == 'combined' else '',
            separate_selected='selected' if config.get('FEED_MODE') == 'separate' else '',
            feed_title=config.get('FEED_TITLE', 'My RSS Emails'),
            feed_description=config.get('FEED_DESCRIPTION', 'Feed RSS gerado dos meus emails'),
            max_emails=config.get('MAX_EMAILS', '50'),
            check_interval=str(int(config.get('CHECK_INTERVAL', '300')) // 60)
        )
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def detect_mailboxes(self):
        """Detect available mailboxes from IMAP server"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            email_user = form_data.get('email_user', [''])[0]
            email_pass = form_data.get('email_pass', [''])[0]
            email_provider = form_data.get('email_provider', ['gmail'])[0]
            
            # Get provider configuration
            if email_provider in self.EMAIL_PROVIDERS:
                provider_config = self.EMAIL_PROVIDERS[email_provider]
                imap_server = provider_config['server']
                imap_port = provider_config['port']
            else:
                imap_server = form_data.get('imap_server', ['imap.gmail.com'])[0]
                imap_port = int(form_data.get('imap_port', ['993'])[0])
            
            if not email_user or not email_pass:
                raise ValueError("Email and password are required")
            
            # Try to connect to IMAP and get mailbox list
            mail = imaplib.IMAP4_SSL(imap_server, imap_port)
            mail.login(email_user, email_pass)
            
            status, mailbox_list = mail.list()
            mail.logout()
            
            if status != 'OK':
                raise Exception("Failed to get folder list")
            
            mailboxes = []
            for item in mailbox_list:
                # Parse mailbox name from IMAP response
                if isinstance(item, bytes):
                    item = item.decode('utf-8')
                
                # Extract mailbox name (last quoted part)
                parts = item.split('"')
                if len(parts) >= 3:
                    encoded_name = parts[-2]  # Original IMAP name
                    # Decode IMAP modified UTF-7 to normal UTF-8
                    decoded_name = decode_imap_utf7(encoded_name)
                    mailboxes.append(decoded_name)
            
            # Sort mailboxes
            mailboxes.sort()
            
            response = {
                "success": True, 
                "mailboxes": mailboxes,
                "count": len(mailboxes)
            }
            
        except Exception as e:
            response = {"success": False, "error": str(e)}
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def save_configuration(self):
        """Save configuration to .env file"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            print(f"DEBUG: Received {content_length} bytes")
            print(f"DEBUG: Content-Type: {self.headers.get('Content-Type', 'missing')}")
            
            # Always try URL-encoded first (most common)
            try:
                form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
                print(f"DEBUG: URL-encoded success - fields: {list(form_data.keys())}")
            except:
                print("DEBUG: URL-encoded failed, trying multipart...")
                # Fallback to simple multipart parsing
                form_data = {}
                data_str = post_data.decode('utf-8', errors='ignore')
                
                # Extract form fields manually
                lines = data_str.split('\n')
                current_field = None
                for line in lines:
                    if 'name="' in line:
                        current_field = line.split('name="')[1].split('"')[0]
                    elif current_field and line.strip() and '--' not in line and 'Content-' not in line:
                        form_data[current_field] = [line.strip()]
                        current_field = None
                
                print(f"DEBUG: Multipart parsing - fields: {list(form_data.keys())}")
            
            # Required fields
            email_user = form_data.get('email_user', [''])[0].strip()
            email_pass = form_data.get('email_pass', [''])[0].strip()
            
            print(f"DEBUG: email_user='{email_user}' (length: {len(email_user)})")
            print(f"DEBUG: email_pass length: {len(email_pass)}")
            
            if not email_user or not email_pass:
                print("DEBUG: Validation failed - empty fields")
                raise ValueError("Email and password are required")
            
            print("DEBUG: Validation passed, creating env file...")
            
            # Convert form data to env format
            env_content = []
            env_content.append(f"EMAIL_USER={email_user}")
            env_content.append(f"EMAIL_PASS={email_pass}")
            
            # Email provider
            email_provider = form_data.get('email_provider', ['gmail'])[0]
            env_content.append(f"EMAIL_PROVIDER={email_provider}")
            
            # Optional fields
            env_content.append(f"IMAP_SERVER={form_data.get('imap_server', ['imap.gmail.com'])[0]}")
            env_content.append(f"IMAP_PORT={form_data.get('imap_port', ['993'])[0]}")
            env_content.append(f"MAILBOXES={form_data.get('mailboxes', ['INBOX'])[0]}")
            env_content.append(f"FEED_MODE={form_data.get('feed_mode', ['combined'])[0]}")
            env_content.append(f"FEED_TITLE={form_data.get('feed_title', ['My RSS Emails'])[0]}")
            env_content.append(f"FEED_DESCRIPTION={form_data.get('feed_description', ['Feed RSS gerado dos meus emails'])[0]}")
            env_content.append(f"MAX_EMAILS={form_data.get('max_emails', ['50'])[0]}")
            
            # Convert minutes to seconds for CHECK_INTERVAL
            interval_minutes = int(form_data.get('check_interval', ['5'])[0])
            env_content.append(f"CHECK_INTERVAL={interval_minutes * 60}")
            
            env_content.append("HTTP_PORT=8888")
            env_content.append("CONFIG_PORT=9999")
            env_content.append("RUN_MODE=daemon")
            
            # Write to .env file
            with open('/app/.env', 'w') as f:
                f.write('\n'.join(env_content))
            
            print(f"DEBUG: File written successfully!")
            response = {"success": True, "message": "Configuration saved successfully"}
            
        except Exception as e:
            print(f"DEBUG: Exception occurred: {str(e)}")
            print(f"DEBUG: Exception type: {type(e).__name__}")
            response = {"success": False, "error": str(e)}
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def serve_status_page(self):
        """Serve the status page"""
        config = self.load_current_config()
        
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IMAP2RSS - Status</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
        .status-ok {{ color: green; }}
        .status-error {{ color: red; }}
        .btn {{ padding: 10px 20px; margin: 5px; text-decoration: none; background: #007bff; color: white; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 IMAP2RSS Status</h1>
        <p><strong>Provider:</strong> {config.get('EMAIL_PROVIDER', 'gmail').title()}</p>
        <p><strong>Email:</strong> {config.get('EMAIL_USER', 'Not configured')}</p>
        <p><strong>Server:</strong> {config.get('IMAP_SERVER', 'imap.gmail.com')}</p>
        <p><strong>Folders:</strong> {config.get('MAILBOXES', 'INBOX')}</p>
        
        <h2>RSS Links:</h2>
        <p><a href="http://localhost:8888/feed.xml" target="_blank">Main Feed</a></p>
        <p><a href="http://localhost:8888/" target="_blank">All Feeds</a></p>
        
        <a href="/" class="btn">⚙️ Settings</a>
        <a href="http://localhost:8888/" class="btn" target="_blank">📰 View Feeds</a>
    </div>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def load_current_config(self):
        """Load current configuration from environment or .env file"""
        config = {}
        
        # Try to load from .env file
        env_file = '/app/.env'
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key] = value
        
        # Override with environment variables
        for key in ['EMAIL_USER', 'EMAIL_PASS', 'EMAIL_PROVIDER', 'IMAP_SERVER', 'IMAP_PORT', 'MAILBOXES', 'FEED_MODE',
                   'FEED_TITLE', 'FEED_DESCRIPTION', 'MAX_EMAILS', 'CHECK_INTERVAL']:
            if key in os.environ:
                config[key] = os.environ[key]
        
        return config
    
    def serve_static(self):
        """Serve static files (placeholder)"""
        self.send_error(404)
    
    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")

def run_config_server():
    port = int(os.getenv('CONFIG_PORT', '9999'))
    server_address = ('', port)
    
    httpd = HTTPServer(server_address, ConfigHandler)
    logger.info(f"Starting configuration server on port {port}")
    logger.info(f"Configuration interface: http://localhost:{port}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down configuration server")
        httpd.shutdown()

if __name__ == "__main__":
    run_config_server()