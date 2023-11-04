from flask import Flask, render_template, request
from flask_mail import Mail, Message
import requests
import socket
import re

app = Flask(__name__)

# Configuration (replace with your own email configuration)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
app.config['DEBUG'] = True
app.config['MAIL_SERVER'] = 'smtp.mail.yahoo.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'YOUR_EMAIL'
app.config['MAIL_PASSWORD'] = 'YOUR_PASSWORD'

mail = Mail(app)

# Function to track sender's IP address and location
def track_sender_info(email_address):
    # Extract the domain from the email address
    domain = re.search(r'@([\w.]+)', email_address).group(1)

    try:
        # Use DNS to find the mail server's IP address
        mail_server_ip = socket.gethostbyname(domain)
        print(f"Mail server IP address: {mail_server_ip}")

        # Use the obtained IP address to track location
        try:
            response = requests.get(f"http://ipinfo.io/{mail_server_ip}/json")
            data = response.json()
            data['mail_server_ip'] = mail_server_ip

            # Extract location and time zone data from the response
            location = data.get('city', '') + ', ' + data.get('region', '') + ', ' + data.get('country', '')
            time_zone = data.get('timezone', '')

            # Add location and time zone to the data dictionary
            data['location'] = location
            data['time_zone'] = time_zone

            # Get the host name of the mail server
            try:
                host_name = socket.gethostbyaddr(mail_server_ip)[0]
                data['mail_server_host'] = host_name
            except Exception as e:
                data['mail_server_host'] = 'Host name not found'

            return data
        except Exception as e:
            print(f"Error getting location information: {e}")
    except Exception as e:
        print(f"Error: {e}")

# Define a route for the web application
@app.route('/', methods=['GET', 'POST'])
def index():
    tracking_info = None

    if request.method == 'POST':
        sender_email = request.form['email_address']
        tracking_info = track_sender_info(sender_email)

    return render_template('index.html', tracking_info=tracking_info)

if __name__ == '__main__':
    app.run()
