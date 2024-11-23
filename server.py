import os
import http.server
import socketserver
import requests
from urllib.parse import unquote
from base64 import b64decode

PORT = 1024  # Define your port number here
USERNAME = "Username"  # Set your username
PASSWORD = "Password"  # Set your password
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/"  # Replace with your webhook URL

class DirectoryListingHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests, including authentication and directory navigation."""
        # Send IP address info to Discord if it's the main page
        if self.path == "/":
            self.send_ip_info_to_discord()

        # Check if user is authenticated
        if not self.is_authenticated():
            self.send_authentication_request()
            return
        
        # Serve the requested directory or file
        self.serve_path(self.path)

    def is_authenticated(self):
        """Check if the user provided correct credentials."""
        auth_header = self.headers.get('Authorization')
        if auth_header is None:
            return False
        
        # Decode the credentials from base64
        auth_type, credentials = auth_header.split(' ', 1)
        if auth_type.lower() != 'basic':
            return False
        
        decoded_credentials = b64decode(credentials).decode('utf-8')
        username, password = decoded_credentials.split(':', 1)
        
        return username == USERNAME and password == PASSWORD

    def send_authentication_request(self):
        """Send a 401 Unauthorized response with a WWW-Authenticate header."""
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="Directory"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<html><body><h1>Username & password required</h1><p>You must provide a username and password to access this folder. if you have username and password then reload the page.</p></body></html>')

    def serve_path(self, path):
        """Serve a directory listing or a file, depending on the path."""
        # Decode URL-encoded path
        decoded_path = unquote(path)
        local_path = os.path.join(os.getcwd(), decoded_path[1:])

        # Check if it's a directory and list contents
        if os.path.isdir(local_path):
            self.list_directory(local_path)
        elif os.path.isfile(local_path):
            self.serve_file(local_path)
        else:
            self.send_error(404, "Not Found")

    def list_directory(self, path):
        """List the files in the directory and return an HTML page."""
        try:
            file_list = os.listdir(path)
        except OSError:
            self.send_error(403, "Forbidden")
            return

        # Create HTML for the directory listing
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Directory Listing</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f9;
                    margin: 0;
                    padding: 20px;
                    overflow-x: hidden;
                }}
                h1 {{
                    color: #333;
                    word-wrap: break-word;
                    white-space: normal;
                }}
                .file-list {{
                    list-style-type: none;
                    padding: 0;
                    overflow-y: auto;
                    max-height: 80vh; /* Limit vertical scroll */
                }}
                .file-item {{
                    padding: 8px;
                    margin: 5px 0;
                    background-color: #fff;
                    border-radius: 4px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    display: flex;
                    align-items: center;
                    transition: background-color 0.3s;
                }}
                .file-item:hover {{
                    background-color: #e0f7fa;
                }}
                .file-icon {{
                    font-size: 20px;
                    margin-right: 10px;
                    color: #333;
                }}
                a {{
                    text-decoration: none;
                    color: #007BFF;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                /* Ensure content wraps and no horizontal scrolling */
                .file-item, a {{
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                }}
            </style>
        </head>
        <body>
            <h1>Directory:</h1>
            <ul class="file-list">
        """

        # Add link to go up a directory, if not at root
        if path != os.getcwd():
            parent_path = os.path.join("/", os.path.relpath(os.path.dirname(path), os.getcwd()))

        # List each file/folder in the directory
        for name in file_list:
            full_path = os.path.join(path, name)
            display_name = name + ('/' if os.path.isdir(full_path) else '')
            href = os.path.join(self.path, name)
            icon = "📂" if os.path.isdir(full_path) else "📄"
            html += f'<li class="file-item"><span class="file-icon">{icon}</span><a href="{href}">{display_name}</a></li>'

        html += """
            </ul>
        </body>
        </html>
        """
        
        # Send the HTML response
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))    

    def serve_file(self, path):
        """Serve a static file (like HTML, CSS, or others) if it's requested."""
        # Set response headers and serve the file
        self.send_response(200)
        self.send_header("Content-type", self.get_content_type(path))
        self.end_headers()
        with open(path, 'rb') as f:
            self.wfile.write(f.read())

    def get_content_type(self, path):
        """Determine the content type based on the file extension."""
        ext = os.path.splitext(path)[1].lower()
        if ext == '.html':
            return 'text/html'
        elif ext == '.css':
            return 'text/css'
        elif ext == '.js':
            return 'application/javascript'
        elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
            return 'image/jpeg'
        else:
            return 'application/octet-stream'

    def send_ip_info_to_discord(self):
        """Send IP address information to Discord using ipinfo.io."""
        # Get client IP address from headers, defaulting to self.client_address if not provided
        client_ip = self.headers.get('X-Forwarded-For', self.client_address[0])

        # Get IP info from ipinfo.io
        try:
            ip_info = requests.get(f"https://ipinfo.io/{client_ip}/json").json()
            if ip_info.get("bogon"):
                discord_message = {
                    "content": f"**New visitor IP info:**\nIP: {client_ip}\nNote: This IP is a bogon (private or unallocated IP)."
                }
            else:
                discord_message = {
                    "content": f"**New visitor IP info:**\nIP: {ip_info.get('ip')}\nCity: {ip_info.get('city')}\nRegion: {ip_info.get('region')}\nCountry: {ip_info.get('country')}\nOrg: {ip_info.get('org')}"
                }
            # Send to Discord webhook
            requests.post(DISCORD_WEBHOOK_URL, json=discord_message)
        except Exception as e:
            print(f"Error sending IP info to Discord: {e}")

# Set up the server
Handler = DirectoryListingHandler
httpd = socketserver.TCPServer(("", PORT), Handler)

print(f"Serving on port {PORT}...")
httpd.serve_forever()
