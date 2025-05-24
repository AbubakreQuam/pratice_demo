from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
CORS(app)  # Allow all origins for simplicity

# Database connection helper
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="*****",
            database="goods_db"
        )
    except Error as e:
        return None

# Routes
@app.route("/goods", methods=["GET"])
def get_goods():
    search = request.args.get("search")
    limit = request.args.get("limit", default=10, type=int)
    offset = request.args.get("offset", default=0, type=int)

    db = get_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed."}), 500

    try:
        cursor = db.cursor(dictionary=True)
        query = "SELECT id, name, status FROM goods"
        params = []

        if search:
            query += " WHERE name LIKE %s"
            params.append(f"%{search}%")

        query += " ORDER BY id LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, params)
        goods = cursor.fetchall()
        return jsonify(goods)
    except Error:
        return jsonify({"error": "Failed to fetch goods."}), 500
    finally:
        cursor.close()
        db.close()

@app.route("/lock", methods=["POST"])
def lock_good():
    data = request.get_json()
    good_id = data.get("id")
    status = data.get("status", "").lower()

    if status not in {"locked", "unlocked"}:
        return jsonify({"error": "Invalid status. Use 'locked' or 'unlocked'."}), 400

    db = get_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed."}), 500

    try:
        cursor = db.cursor()
        cursor.execute(
            "UPDATE goods SET status = %s WHERE id = %s",
            (status, good_id)
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "Good not found."}), 404
        db.commit()
        return jsonify({"message": f"Good {good_id} status set to {status}."})
    except Error:
        return jsonify({"error": "Failed to update status."}), 500
    finally:
        cursor.close()
        db.close()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
