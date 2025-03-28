from flask import Flask, render_template, request, redirect, url_for, session
import subprocess

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Hardcoded credentials (replace with a database in production)
USER_CREDENTIALS = {'admin': 'password'}

# Function to read suspicious IPs from a text file
def get_suspicious_ips():
    """Reads suspicious IPs from the file and returns them as a list."""
    suspicious_ips = []
    try:
        with open('suspicious_ips.txt', 'r') as file:
            suspicious_ips = [line.strip() for line in file.readlines()]
    except Exception as e:
        print(f"Error reading suspicious IP file: {e}")
    return suspicious_ips

# Route for Login Page
@app.route('/', methods=['GET', 'POST'])
def login():
    message = ""
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            session['user'] = username
            return redirect(url_for('dashboard'))  # Redirect to Dashboard
        else:
            message = "Invalid Username or Password"

    return render_template('login.html', message=message)

# Route for Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('tableau.html')

# Route for IP Management (Block IP Page)
@app.route('/block_ip', methods=['GET', 'POST'])
def ip_management():
    if 'user' not in session:
        return redirect(url_for('login'))

    message = ""  # Initialize message
    
    # Handle the form submission for blocking or unblocking
    if request.method == 'POST':
        action = request.form.get('action')  # Get action (block or unblock)
        selected_ips = request.form.getlist('selected_ips')  # Get selected IPs

        if selected_ips:
            for ip_address in selected_ips:
                if action == "block":
                    command = f'netsh advfirewall firewall add rule name="Block {ip_address}" dir=in action=block remoteip={ip_address}'
                elif action == "unblock":
                    command = f'netsh advfirewall firewall delete rule name="Block {ip_address}"'

                try:
                    subprocess.run(command, check=True, shell=True)  # Execute the command
                    message = f"IPs {', '.join(selected_ips)} {action}ed successfully."
                except subprocess.CalledProcessError as e:
                    message = f"Failed to {action} IPs. Error: {e}"

    # Get the list of suspicious IPs
    suspicious_ips = get_suspicious_ips()

    # Render the block_ip.html template and pass the message and suspicious_ips
    return render_template('block_ip.html', message=message, suspicious_ips=suspicious_ips)

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
