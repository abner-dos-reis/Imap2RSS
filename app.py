#!/usr/bin/env python3
"""
IMAP to RSS Converter
Converts emails from IMAP to RSS feed for FreshRSS integration
"""

import imaplib
import email
import time
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import logging
from email.utils import parsedate_to_datetime
import html
import re
from typing import List, Dict, Any
import hashlib
import json
import urllib.parse
import base64

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
        import re
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

class ImapToRss:
    
    # Email provider configurations
    PROVIDERS = {
        'gmail': {
            'name': 'Gmail',
            'server': 'imap.gmail.com',
            'port': 993,
            'ssl': True
        },
        'outlook': {
            'name': 'Outlook/Hotmail',
            'server': 'outlook.office365.com',
            'port': 993,
            'ssl': True
        },
        'yahoo': {
            'name': 'Yahoo Mail',
            'server': 'imap.mail.yahoo.com',
            'port': 993,
            'ssl': True
        },
        'zoho': {
            'name': 'Zoho Mail',
            'server': 'imap.zoho.com',
            'port': 993,
            'ssl': True
        },
        'custom': {
            'name': 'Custom IMAP',
            'server': None,
            'port': 993,
            'ssl': True
        }
    }
    
    def __init__(self):
        # Email provider setup
        self.email_provider = os.getenv('EMAIL_PROVIDER', 'gmail').lower()
        self.setup_provider_config()
        
        self.email_user = os.getenv('EMAIL_USER')
        self.email_pass = os.getenv('EMAIL_PASS')
        self.feed_title = os.getenv('FEED_TITLE', 'Email RSS Feed')
        self.feed_description = os.getenv('FEED_DESCRIPTION', 'RSS feed generated from IMAP emails')
        self.max_emails = int(os.getenv('MAX_EMAILS', '50'))
        
        # Support for multiple mailboxes
        mailboxes_str = os.getenv('MAILBOXES', 'INBOX')
        self.mailboxes = [mb.strip() for mb in mailboxes_str.split(',') if mb.strip()]
        
        # Feed generation mode
        self.feed_mode = os.getenv('FEED_MODE', 'combined')  # 'combined' or 'separate'
        
        # Mailbox name mapping (decoded -> encoded)
        self.mailbox_mapping = {}
        
        # Use local data dir if not running in Docker
        if os.path.exists('/app/data'):
            self.data_dir = '/app/data'
        else:
            self.data_dir = './data'
        
        if not self.email_user or not self.email_pass:
            raise ValueError("EMAIL_USER and EMAIL_PASS environment variables are required")
    
    def setup_provider_config(self):
        """Setup IMAP configuration based on email provider"""
        if self.email_provider in self.PROVIDERS:
            provider_config = self.PROVIDERS[self.email_provider]
            
            # Use provider defaults, but allow override via environment
            self.imap_server = os.getenv('IMAP_SERVER', provider_config['server'])
            self.imap_port = int(os.getenv('IMAP_PORT', str(provider_config['port'])))
            self.use_ssl = provider_config['ssl']
            
            logger.info(f"Using {provider_config['name']} configuration: {self.imap_server}:{self.imap_port}")
        else:
            # Fallback to manual configuration
            self.imap_server = os.getenv('IMAP_SERVER', 'imap.gmail.com')
            self.imap_port = int(os.getenv('IMAP_PORT', '993'))
            self.use_ssl = True
            logger.warning(f"Unknown provider '{self.email_provider}', using manual configuration")
    
    def connect_imap(self) -> imaplib.IMAP4_SSL:
        """Connect to IMAP server with optimized settings"""
        try:
            logger.info(f"Connecting to {self.imap_server}:{self.imap_port}")
            # Create connection with shorter timeout for faster response
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port, timeout=10)
            mail.login(self.email_user, self.email_pass)
            # Set shorter timeout for operations
            mail.sock.settimeout(30)
            logger.info("Successfully connected to IMAP server")
            return mail
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server: {e}")
            raise
    
    def get_available_mailboxes(self, mail: imaplib.IMAP4_SSL) -> List[str]:
        """Get list of available mailboxes from the server"""
        try:
            status, mailbox_list = mail.list()
            if status != 'OK':
                logger.error("Failed to get mailbox list")
                return ['INBOX']
            
            mailboxes = []
            self.mailbox_mapping = {}  # Store mapping of decoded -> encoded names
            
            for item in mailbox_list:
                # Parse mailbox name from IMAP response
                # Format: (flags) "delimiter" "mailbox_name"
                if isinstance(item, bytes):
                    item = item.decode('utf-8')
                
                # Extract mailbox name (last quoted part)
                parts = item.split('"')
                if len(parts) >= 3:
                    encoded_name = parts[-2]  # Original IMAP name
                    # Decode IMAP modified UTF-7 to normal UTF-8
                    decoded_name = decode_imap_utf7(encoded_name)
                    mailboxes.append(decoded_name)
                    # Store mapping for later use
                    self.mailbox_mapping[decoded_name] = encoded_name
            
            logger.info(f"Available mailboxes: {mailboxes}")
            return mailboxes
            
        except Exception as e:
            logger.error(f"Failed to get mailboxes: {e}")
            return ['INBOX']
    
    def fetch_emails_from_mailboxes(self, mail: imaplib.IMAP4_SSL) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch emails from all configured mailboxes"""
        all_emails = {}
        
        for mailbox in self.mailboxes:
            try:
                logger.info(f"Fetching emails from mailbox: {mailbox}")
                # Get the encoded name for IMAP commands
                encoded_mailbox = self.mailbox_mapping.get(mailbox, mailbox)
                # Properly encode mailbox name for IMAP - use UTF-7 encoding
                try:
                    quoted_mailbox = f'"{encoded_mailbox}"'
                    mail.select(quoted_mailbox)
                except UnicodeEncodeError:
                    # Fallback: try encoding to UTF-7 (IMAP standard)
                    utf7_mailbox = encoded_mailbox.encode('utf-7').decode('ascii')
                    quoted_mailbox = f'"{utf7_mailbox}"'
                    mail.select(quoted_mailbox)
                
                emails = self.fetch_emails_from_mailbox(mail, mailbox)
                all_emails[mailbox] = emails
                logger.info(f"Fetched {len(emails)} emails from {mailbox}")
                
            except Exception as e:
                logger.error(f"Failed to fetch from mailbox {mailbox}: {e}")
                all_emails[mailbox] = []
        
        return all_emails
    def fetch_emails_from_mailbox(self, mail: imaplib.IMAP4_SSL, mailbox: str) -> List[Dict[str, Any]]:
        """Fetch recent emails from a specific mailbox"""
        try:
            # Search for emails
            status, messages = mail.search(None, 'ALL')
            if status != 'OK':
                logger.error(f"Failed to search emails in {mailbox}")
                return []
            
            email_ids = messages[0].split()
            
            # Get the most recent emails
            recent_emails = email_ids[-self.max_emails:] if email_ids else []
            
            emails = []
            for email_id in reversed(recent_emails):  # Most recent first
                try:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        continue
                    
                    email_message = email.message_from_bytes(msg_data[0][1])
                    
                    # Extract email data
                    subject = self.decode_header(email_message.get('Subject', 'No Subject'))
                    sender = self.decode_header(email_message.get('From', 'Unknown Sender'))
                    date_str = email_message.get('Date', '')
                    
                    # Parse date
                    try:
                        date_obj = parsedate_to_datetime(date_str) if date_str else datetime.now()
                    except:
                        date_obj = datetime.now()
                    
                    # Extract body
                    body = self.extract_body(email_message)
                    
                    # Create unique ID for the email
                    email_id_str = f"{mailbox}_{sender}_{subject}_{date_obj.isoformat()}"
                    unique_id = hashlib.md5(email_id_str.encode()).hexdigest()
                    
                    emails.append({
                        'id': unique_id,
                        'subject': subject,
                        'sender': sender,
                        'date': date_obj,
                        'body': body,
                        'mailbox': mailbox,
                        'category': mailbox
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to process email {email_id} in {mailbox}: {e}")
                    continue
            
            return emails
            
        except Exception as e:
            logger.error(f"Failed to fetch emails from {mailbox}: {e}")
            return []
    
    def decode_header(self, header: str) -> str:
        """Decode email header"""
        if not header:
            return ""
        
        try:
            decoded_parts = email.header.decode_header(header)
            decoded_string = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_string += part.decode(encoding or 'utf-8', errors='ignore')
                else:
                    decoded_string += part
            return decoded_string.strip()
        except:
            return str(header)
    
    def extract_body(self, email_message) -> str:
        """Extract email body text with preserved HTML when available"""
        body = ""
        html_body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        continue
                elif content_type == "text/html" and "attachment" not in content_disposition:
                    try:
                        html_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        continue
        else:
            try:
                content = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                if email_message.get_content_type() == "text/html":
                    html_body = content
                else:
                    body = content
            except:
                body = str(email_message.get_payload())
        
        # Prefer HTML version for better link preservation, fallback to plain text
        if html_body:
            return self.clean_html_for_rss(html_body)
        return body.strip()
    
    def clean_html_for_rss(self, html_content: str) -> str:
        """Clean HTML content but preserve links and basic formatting"""
        import re
        
        # Remove dangerous or problematic tags but keep links and basic formatting
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<head[^>]*>.*?</head>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove ALL inline styles - this is the main culprit for borders
        html_content = re.sub(r'\s*style\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        
        # Remove ALL visual attributes that cause borders/styling
        html_content = re.sub(r'\s*border\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'\s*bgcolor\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'\s*background\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'\s*width\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'\s*height\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'\s*color\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'\s*align\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'\s*valign\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        
        # Remove table-related styling that causes visual issues
        html_content = re.sub(r'\s*cellpadding\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'\s*cellspacing\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'\s*frame\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'\s*rules\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        
        # Remove CSS class and id attributes that might reference external styles
        html_content = re.sub(r'\s*class\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'\s*id\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        
        # Remove font styling attributes  
        html_content = re.sub(r'\s*face\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'\s*size\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        
        # Clean up multiple spaces that might be left after attribute removal
        html_content = re.sub(r'\s+', ' ', html_content)
        html_content = re.sub(r'>\s+<', '><', html_content)
        html_content = re.sub(r'\s+>', '>', html_content)
        html_content = re.sub(r'<\s+', '<', html_content)
        
        # Decode HTML entities
        html_content = html.unescape(html_content)
        
        # Clean up excessive whitespace while preserving HTML structure
        html_content = re.sub(r'\s+', ' ', html_content)
        html_content = re.sub(r'>\s+<', '><', html_content)
        
        # Decode HTML entities
        html_content = html.unescape(html_content)
        
        return html_content.strip()
    
    def html_to_text(self, html_content: str) -> str:
        """Simple HTML to text conversion - kept for compatibility"""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_content)
        # Decode HTML entities
        text = html.unescape(text)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def generate_combined_rss(self, all_emails: Dict[str, List[Dict[str, Any]]]) -> str:
        """Generate a single RSS feed with all emails, categorized by mailbox"""
        # Create RSS root element
        rss = ET.Element("rss", version="2.0")
        rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")
        channel = ET.SubElement(rss, "channel")
        
        # Channel metadata
        ET.SubElement(channel, "title").text = self.feed_title
        ET.SubElement(channel, "description").text = self.feed_description
        ET.SubElement(channel, "link").text = "http://localhost:8888/feed.xml"
        ET.SubElement(channel, "lastBuildDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
        ET.SubElement(channel, "generator").text = "IMAP to RSS Converter with Categories"
        
        # Atom link for self-reference
        atom_link = ET.SubElement(channel, "atom:link")
        atom_link.set("href", "http://localhost:8888/feed.xml")
        atom_link.set("rel", "self")
        atom_link.set("type", "application/rss+xml")
        
        # Collect all emails and sort by date
        all_items = []
        for mailbox, emails in all_emails.items():
            all_items.extend(emails)
        
        # Sort by date (most recent first)
        all_items.sort(key=lambda x: x['date'], reverse=True)
        
        # Limit total items
        all_items = all_items[:self.max_emails]
        
        # Add items for each email
        for email_data in all_items:
            item = ET.SubElement(channel, "item")
            
            title = f"[{email_data['mailbox']}] [{email_data['sender']}] {email_data['subject']}"
            ET.SubElement(item, "title").text = title
            
            # Include mailbox in description with preserved HTML
            description = f"<p><strong>Folder:</strong> {email_data['mailbox']}</p><p><strong>From:</strong> {email_data['sender']}</p><hr/>"
            
            # Preserve HTML content with links
            body_content = email_data['body']
            if len(body_content) > 3000:  # Increased limit for HTML content
                body_content = body_content[:3000] + "..."
            
            description += body_content
            
            # Use CDATA to preserve HTML content
            desc_elem = ET.SubElement(item, "description")
            desc_elem.text = f"<![CDATA[{description}]]>"
            
            ET.SubElement(item, "guid").text = email_data['id']
            ET.SubElement(item, "pubDate").text = email_data['date'].strftime("%a, %d %b %Y %H:%M:%S +0000")
            ET.SubElement(item, "author").text = email_data['sender']
            ET.SubElement(item, "category").text = email_data['mailbox']
        
        # Convert to string
        xml_str = ET.tostring(rss, encoding='unicode')
        
        # Pretty format
        from xml.dom import minidom
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent="  ")
    
    def generate_separate_rss_feeds(self, all_emails: Dict[str, List[Dict[str, Any]]]) -> Dict[str, str]:
        """Generate separate RSS feeds for each mailbox"""
        feeds = {}
        
        for mailbox, emails in all_emails.items():
            if not emails:
                continue
                
            # Create RSS root element
            rss = ET.Element("rss", version="2.0")
            rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")
            channel = ET.SubElement(rss, "channel")
            
            # Channel metadata
            ET.SubElement(channel, "title").text = f"{self.feed_title} - {mailbox}"
            ET.SubElement(channel, "description").text = f"{self.feed_description} (Pasta: {mailbox})"
            ET.SubElement(channel, "link").text = f"http://localhost:8888/{mailbox}.xml"
            ET.SubElement(channel, "lastBuildDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
            ET.SubElement(channel, "generator").text = "IMAP to RSS Converter"
            ET.SubElement(channel, "category").text = mailbox
            
            # Atom link for self-reference
            atom_link = ET.SubElement(channel, "atom:link")
            atom_link.set("href", f"http://localhost:8888/{mailbox}.xml")
            atom_link.set("rel", "self")
            atom_link.set("type", "application/rss+xml")
            
            # Add items for each email
            for email_data in emails:
                item = ET.SubElement(channel, "item")
                
                title = f"[{email_data['sender']}] {email_data['subject']}"
                ET.SubElement(item, "title").text = title
                
                # Preserve HTML content with links
                body_content = email_data['body']
                if len(body_content) > 3000:  # Increased limit for HTML content
                    body_content = body_content[:3000] + "..."
                
                # Use CDATA to preserve HTML content
                desc_elem = ET.SubElement(item, "description")
                desc_elem.text = f"<![CDATA[{body_content}]]>"
                
                ET.SubElement(item, "guid").text = email_data['id']
                ET.SubElement(item, "pubDate").text = email_data['date'].strftime("%a, %d %b %Y %H:%M:%S +0000")
                ET.SubElement(item, "author").text = email_data['sender']
                ET.SubElement(item, "category").text = mailbox
            
            # Convert to string
            xml_str = ET.tostring(rss, encoding='unicode')
            
            # Pretty format
            from xml.dom import minidom
            dom = minidom.parseString(xml_str)
            feeds[mailbox] = dom.toprettyxml(indent="  ")
        
        return feeds
    
    def normalize_filename(self, mailbox_name: str) -> str:
        """Normalize mailbox name to valid filename"""
        # Replace invalid characters with underscores
        filename = re.sub(r'[<>:"/\\|?*]', '_', mailbox_name)
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        # Ensure it's not empty
        if not filename:
            filename = 'mailbox'
        return filename
    
    def save_feeds(self, feeds_data: Dict[str, str]):
        """Save RSS feeds to files"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            
            for feed_name, rss_content in feeds_data.items():
                file_path = os.path.join(self.data_dir, f"{feed_name}.xml")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(rss_content)
                logger.info(f"RSS feed saved to {file_path}")
                
            # Create index file with available feeds
            self.create_feeds_index(list(feeds_data.keys()))
            
        except Exception as e:
            logger.error(f"Failed to save RSS feeds: {e}")
    
    def create_feeds_index(self, feed_names: List[str]):
        """Create an index file listing all available feeds"""
        index_data = {
            'feeds': feed_names,
            'base_url': 'http://localhost:8888',
            'generated_at': datetime.now().isoformat(),
            'feed_mode': self.feed_mode,
            'mailboxes': self.mailboxes
        }
        
        index_path = os.path.join(self.data_dir, 'feeds_index.json')
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2)
    
    def save_rss(self, rss_content: str):
        """Save RSS content to file (legacy method for compatibility)"""
        try:
            os.makedirs(os.path.dirname(self.rss_file), exist_ok=True)
            with open(self.rss_file, 'w', encoding='utf-8') as f:
                f.write(rss_content)
            logger.info(f"RSS feed saved to {self.rss_file}")
        except Exception as e:
            logger.error(f"Failed to save RSS feed: {e}")
    
    def run_once(self):
        """Run one iteration of email fetching and RSS generation"""
        try:
            mail = self.connect_imap()
            
            # Get available mailboxes for logging
            available_mailboxes = self.get_available_mailboxes(mail)
            logger.info(f"Available mailboxes: {available_mailboxes}")
            
            # Fetch emails from all configured mailboxes
            all_emails = self.fetch_emails_from_mailboxes(mail)
            mail.close()
            mail.logout()
            
            total_emails = sum(len(emails) for emails in all_emails.values())
            
            if total_emails > 0:
                if self.feed_mode == 'separate':
                    # Generate separate feeds for each mailbox
                    feeds = self.generate_separate_rss_feeds(all_emails)
                    feeds['feed'] = self.generate_combined_rss(all_emails)  # Also create combined feed
                    
                    # Normalize feed names for files
                    normalized_feeds = {}
                    for mailbox, feed_content in feeds.items():
                        if mailbox == 'feed':
                            normalized_feeds['feed'] = feed_content
                        else:
                            normalized_name = self.normalize_filename(mailbox)
                            normalized_feeds[normalized_name] = feed_content
                    
                    self.save_feeds(normalized_feeds)
                    logger.info(f"Generated {len(normalized_feeds)} RSS feeds with {total_emails} total emails")
                else:
                    # Generate single combined feed
                    combined_rss = self.generate_combined_rss(all_emails)
                    self.save_feeds({'feed': combined_rss})
                    logger.info(f"Generated combined RSS feed with {total_emails} emails from {len(all_emails)} mailboxes")
            else:
                logger.warning("No emails found in any mailbox")
                
        except Exception as e:
            logger.error(f"Error in run_once: {e}")
    
    def run_daemon(self):
        """Run as daemon, checking for new emails periodically"""
        check_interval = int(os.getenv('CHECK_INTERVAL', '300'))  # 5 minutes default
        
        logger.info(f"Starting IMAP to RSS daemon (checking every {check_interval} seconds)")
        
        while True:
            self.run_once()
            time.sleep(check_interval)

if __name__ == "__main__":
    converter = ImapToRss()
    
    # Check if running as daemon
    if os.getenv('RUN_MODE', 'daemon') == 'daemon':
        converter.run_daemon()
    else:
        converter.run_once()