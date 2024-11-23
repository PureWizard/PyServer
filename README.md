# Password-Protected Python Web Server

A simple Python web server with password protection that allows users to list the contents of a directory. Notifications about server access can be sent to a Discord Webhook for monitoring purposes.

## Features
- **Password Protection**: Only authenticated users can access the directory listing.
- **Customizable**: Modify the port, username, and password to suit your needs.
- **Access Notifications**: Sends a notification to a Discord Webhook whenever someone accesses the server.
- **Easy Setup**: Place the script in the desired directory and run it directly.

## How to Set Up

1. **Change the Server Configuration**  
   Open the script file and change the following variables:  
   - `PORT`: Update the port to your desired value (currently using port `1024`).  
   - `USERNAME` and `PASSWORD`: Set your own login credentials.  
   - `DISCORD_WEBHOOK_URL`: Replace with your Discord Webhook URL if you want to receive access notifications.

   Example:
   ```python
   PORT = 1024  # Replace with your desired port
   USERNAME = "Username"  # Replace with your desired username
   PASSWORD = "Password"  # Replace with your desired password
   DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."  # Replace with your webhook URL
