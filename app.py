import os
import time
from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL configuration (FORCE TCP, NO SOCKET)
app.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST", "mysql")
app.config["MYSQL_USER"] = os.environ.get("MYSQL_USER", "root")
app.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD", "admin")
app.config["MYSQL_DB"] = os.environ.get("MYSQL_DB", "testdb")
app.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT", 3306))

mysql = MySQL(app)

def wait_for_mysql(retries=10, delay=3):
    for i in range(retries):
        try:
            with app.app_context():
                cur = mysql.connection.cursor()
                cur.execute("SELECT 1")
                cur.close()
            print("â MySQL is ready")
            return
        except Exception as e:
            print(f"â³ Waiting for MySQL... ({i+1}/{retries})")
            time.sleep(delay)
    raise Exception("â MySQL not available after retries")

def init_db():
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            message TEXT
        );
        """)
        mysql.connection.commit()
        cur.close()

@app.route("/")
def hello():
    cur = mysql.connection.cursor()
    cur.execute("SELECT message FROM messages")
    messages = cur.fetchall()
    cur.close()
    return render_template("index.html", messages=messages)

@app.route("/submit", methods=["POST"])
def submit():
    new_message = request.form.get("new_message")
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO messages (message) VALUES (%s)", (new_message,))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": new_message})

if __name__ == "__main__":
    wait_for_mysql()
    init_db()
    app.run(host="0.0.0.0", port=5000)


