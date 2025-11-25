from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'debug_key'

@app.route('/')
def index():
    return """
    <html>
    <body>
        <h1>DEBUG - Home</h1>
        <form method="POST" action="/select_role">
            <button name="role" value="admin">Admin</button>
        </form>
    </body>
    </html>
    """

@app.route('/select_role', methods=['POST'])
def select_role():
    role = request.form.get('role')
    print(f"DEBUG: Role selected: {role}")
    return redirect('/admin/login')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    print(f"DEBUG: Method received: {request.method}")
    
    if request.method == 'POST':
        print("DEBUG: POST request received")
        admin_id = request.form.get('admin_id')
        print(f"DEBUG: Form data - admin_id: {admin_id}")
        return "DEBUG: Login successful - POST working!"
    
    return """
    <html>
    <body>
        <h1>DEBUG - Admin Login</h1>
        <form method="POST" action="/admin/login">
            <input type="text" name="admin_id" placeholder="Admin ID">
            <button type="submit">Login</button>
        </form>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("🚀 DEBUG Server Starting...")
    app.run(debug=True, port=5001)