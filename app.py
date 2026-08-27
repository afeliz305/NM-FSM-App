import os
import random
import sqlite3
from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'  # Corrected configuration key and file name
app.config['SECRET_KEY'] = "random string"
db = SQLAlchemy(app)  # Corrected class name

class Students(db.Model):  # Corrected class name and capitalization
    id = db.Column('student_id', db.Integer, primary_key=True)  # Corrected column spelling and type
    name = db.Column(db.String(100))  # Corrected column type and spelling
    city = db.Column(db.String(50))  # Corrected column type and spelling
    addr = db.Column(db.String(200))  # Corrected column type and spelling
    pin = db.Column(db.String(10))  # Corrected column type and spelling
    phone_number = db.Column(db.String(20))

    def __init__(self, name, city, addr, pin, phone_number=None):
        self.name = name
        self.city = city
        self.addr = addr
        self.pin = pin
        self.phone_number = phone_number

def init_db():
    with app.app_context():
        db.create_all()
        # Handle SQLite schema migration if phone_number column is missing
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        if not os.path.isabs(db_path):
            db_path = os.path.join(app.instance_path, db_path)
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(students)")
            columns = [col[1] for col in cur.fetchall()]
            if 'phone_number' not in columns:
                cur.execute("ALTER TABLE students ADD COLUMN phone_number VARCHAR(20)")
                conn.commit()
            # Assign random phone numbers to existing records with null/empty phone numbers
            cur.execute("SELECT student_id, phone_number FROM students WHERE phone_number IS NULL OR phone_number = ''")
            rows = cur.fetchall()
            for sid, _ in rows:
                rand_phone = f"{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"
                cur.execute("UPDATE students SET phone_number = ? WHERE student_id = ?", (rand_phone, sid))
            conn.commit()
            conn.close()

@app.route('/')
def show_all():
    return render_template('show_all.html', students=Students.query.all())  # Corrected template rendering

@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        if not request.form['name'] or not request.form['city'] or not request.form['addr']:
            flash('Please enter all the fields', 'error')
        else:
            student = Students(
                request.form['name'],
                request.form['city'],
                request.form['addr'],
                request.form.get('pin'),
                request.form.get('phone_number')
            )
            db.session.add(student)
            db.session.commit()  # Fixed typo in commit
            flash('Record was successfully added')
            return redirect(url_for('show_all'))
    return render_template('new.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

