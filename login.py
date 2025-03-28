from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Hardcoded credentials (replace with a database in production)
USER_CREDENTIALS = {'admin': 'password'}

@app.route('/', methods=['GET', 'POST'])
def login():
    message = ""
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            session['user'] = username
            return redirect(url_for('dashboard'))  # Redirect to App.py's route
        else:
            message = "Invalid Username or Password"

    return render_template('login.html', message=message)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return redirect("http://127.0.0.1:5001/")  # Redirect to App.py running on port 5001


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
