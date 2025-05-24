# backend.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
import mysql.connector
from mysql.connector import Error
from typing import List, Optional
import uvicorn

app = FastAPI()

# CORS setup to allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    uvicorn.run(
        "backend:app",  # import string for reload support
        host="0.0.0.0",
        port=8000,
        reload=True
    )
# This code is a FastAPI backend that connects to a MySQL database to manage goods.