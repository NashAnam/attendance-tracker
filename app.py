from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd

# Initialize Flask app
app = Flask(__name__)

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), default=datetime.today().strftime('%Y-%m-%d'))
    student_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(10), nullable=False)

# Home Page - Mark Attendance
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("student_name")
        status = request.form.get("status")
        if name:
            new_entry = Attendance(student_name=name, status=status)
            db.session.add(new_entry)
            db.session.commit()
    return render_template("index.html")

# View Attendance Records
@app.route("/records")
def records():
    all_records = Attendance.query.order_by(Attendance.date.desc()).all()
    
    # Ensure an empty dataset if no records exist
    if not all_records:
        all_records = []

    # Create attendance chart data
    attendance_count = {"Present": 0, "Absent": 0}
    for record in all_records:
        attendance_count[record.status] = attendance_count.get(record.status, 0) + 1

    chart_data = {
        "labels": list(attendance_count.keys()),
        "data": list(attendance_count.values())
    }

    return render_template("records.html", records=all_records, chart_data=chart_data)


# Delete a specific record
@app.route("/delete/<int:id>")
def delete_record(id):
    record = Attendance.query.get(id)
    if record:
        db.session.delete(record)
        db.session.commit()
    return redirect(url_for("records"))

# Export to Excel
@app.route("/export")
def export():
    data = Attendance.query.all()
    df = pd.DataFrame([(d.id, d.date, d.student_name, d.status) for d in data], columns=["ID", "Date", "Student Name", "Status"])
    df.to_excel("attendance_records.xlsx", index=False)
    return "Data exported successfully!"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables within app context
    app.run(debug=True)

# Enhancements to UI
# - Added professional animations and doodles
# - Included modern styling for an engaging experience
# - Implemented delete functionality for specific records
