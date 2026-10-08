from flask import Flask, request, jsonify, send_from_directory
import os
from flask_cors import CORS

from database import get_db_connection, init_db

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
CORS(app)

# Initialize database
init_db()


# ---------------------------------------------------
# HOME
# ---------------------------------------------------

@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# ---------------------------------------------------
# ADD STUDENT - POST
# ---------------------------------------------------

@app.route("/api/students", methods=["POST"])
def add_student():

    data = request.get_json()

    # Check whether JSON data is provided
    if not data:
        return jsonify({
            "error": "No data provided"
        }), 400

    name = data.get("name", "").strip()
    roll_no = data.get("roll_no", "").strip()
    student_class = data.get("student_class", "").strip()
    marks = data.get("marks")
    contact = data.get("contact", "").strip()

    # Required field validation
    if not name or not roll_no or not student_class or marks is None or not contact:
        return jsonify({
            "error": "All fields are required"
        }), 400

    # Name validation
    if not all(char.isalpha() or char.isspace() for char in name):
        return jsonify({
            "error": "Name should contain only letters"
        }), 400

    # Roll number validation
    if len(roll_no) < 1:
        return jsonify({
            "error": "Invalid roll number"
        }), 400

    # Marks validation
    try:
        marks = float(marks)
    except (ValueError, TypeError):
        return jsonify({
            "error": "Marks must be a number"
        }), 400

    if marks < 0 or marks > 100:
        return jsonify({
            "error": "Marks must be between 0 and 100"
        }), 400

    # Contact validation
    if not contact.isdigit() or len(contact) != 10:
        return jsonify({
            "error": "Contact number must contain exactly 10 digits"
        }), 400

    conn = get_db_connection()

    # Check duplicate roll number
    existing_student = conn.execute(
        "SELECT * FROM students WHERE roll_no = ?",
        (roll_no,)
    ).fetchone()

    if existing_student:
        conn.close()

        return jsonify({
            "error": "Roll number already exists"
        }), 409

    # Insert student
    cursor = conn.execute("""
        INSERT INTO students
        (name, roll_no, student_class, marks, contact)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        roll_no,
        student_class,
        marks,
        contact
    ))

    conn.commit()

    student_id = cursor.lastrowid

    conn.close()

    return jsonify({
        "message": "Student added successfully",
        "student_id": student_id
    }), 201


# ---------------------------------------------------
# GET ALL STUDENTS
# ---------------------------------------------------

@app.route("/api/students", methods=["GET"])
def get_students():

    conn = get_db_connection()

    students = conn.execute("""
        SELECT * FROM students
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    student_list = [dict(student) for student in students]

    return jsonify(student_list), 200


# ---------------------------------------------------
# SEARCH STUDENT
# ---------------------------------------------------

@app.route("/api/students/search", methods=["GET"])
def search_student():

    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({
            "error": "Search query is required"
        }), 400

    conn = get_db_connection()

    students = conn.execute("""
        SELECT * FROM students
        WHERE name LIKE ?
           OR roll_no LIKE ?
    """, (
        f"%{query}%",
        f"%{query}%"
    )).fetchall()

    conn.close()

    student_list = [dict(student) for student in students]

    return jsonify(student_list), 200


# ---------------------------------------------------
# GET SINGLE STUDENT
# ---------------------------------------------------

@app.route("/api/students/<int:student_id>", methods=["GET"])
def get_student(student_id):

    conn = get_db_connection()

    student = conn.execute("""
        SELECT * FROM students
        WHERE id = ?
    """, (student_id,)).fetchone()

    conn.close()

    if student is None:
        return jsonify({
            "error": "Student not found"
        }), 404

    return jsonify(dict(student)), 200


# ---------------------------------------------------
# UPDATE STUDENT - PUT
# ---------------------------------------------------

@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No data provided"
        }), 400

    name = data.get("name", "").strip()
    roll_no = data.get("roll_no", "").strip()
    student_class = data.get("student_class", "").strip()
    marks = data.get("marks")
    contact = data.get("contact", "").strip()

    if not name or not roll_no or not student_class or marks is None or not contact:
        return jsonify({
            "error": "All fields are required"
        }), 400

    if not all(char.isalpha() or char.isspace() for char in name):
        return jsonify({
            "error": "Name should contain only letters"
        }), 400

    try:
        marks = float(marks)
    except (ValueError, TypeError):
        return jsonify({
            "error": "Marks must be a number"
        }), 400

    if marks < 0 or marks > 100:
        return jsonify({
            "error": "Marks must be between 0 and 100"
        }), 400

    if not contact.isdigit() or len(contact) != 10:
        return jsonify({
            "error": "Contact number must contain exactly 10 digits"
        }), 400

    conn = get_db_connection()

    # Check whether student exists
    student = conn.execute("""
        SELECT * FROM students
        WHERE id = ?
    """, (student_id,)).fetchone()

    if student is None:
        conn.close()

        return jsonify({
            "error": "Student not found"
        }), 404

    # Check duplicate roll number belonging to another student
    duplicate = conn.execute("""
        SELECT * FROM students
        WHERE roll_no = ?
        AND id != ?
    """, (roll_no, student_id)).fetchone()

    if duplicate:
        conn.close()

        return jsonify({
            "error": "Roll number already exists"
        }), 409

    conn.execute("""
        UPDATE students
        SET name = ?,
            roll_no = ?,
            student_class = ?,
            marks = ?,
            contact = ?
        WHERE id = ?
    """, (
        name,
        roll_no,
        student_class,
        marks,
        contact,
        student_id
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Student updated successfully"
    }), 200


# ---------------------------------------------------
# DELETE STUDENT
# ---------------------------------------------------

@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):

    conn = get_db_connection()

    student = conn.execute("""
        SELECT * FROM students
        WHERE id = ?
    """, (student_id,)).fetchone()

    if student is None:
        conn.close()

        return jsonify({
            "error": "Student not found"
        }), 404

    conn.execute("""
        DELETE FROM students
        WHERE id = ?
    """, (student_id,))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Student deleted successfully"
    }), 200


# ---------------------------------------------------
# RUN SERVER
# ---------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)