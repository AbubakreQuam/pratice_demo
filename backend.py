# backend.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
import mysql.connector
from mysql.connector import Error
from typing import List, Optional
import uvicorn
import os

app = FastAPI()

# CORS setup to allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setting up Database Connection Key
database_connection_key = st.secrets['database_connection_secret']
os.environ['database_connection_secret'] = database_connection_key


# Database connection helper
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",        
            password=database_connection_key,
            database="goods_db"
        )
    except Error as e:
        # Log the exception as needed
        raise HTTPException(status_code=500, detail="Database connection failed.")

# Pydantic models
class Good(BaseModel):
    id: int
    name: str
    status: str

class GoodUpdate(BaseModel):
    id: int
    status: str

    @field_validator('status')
    def validate_status(cls, v):
        allowed = {'locked', 'unlocked'}
        if v.lower() not in allowed:
            raise ValueError(f"Invalid status '{v}'. Allowed: {allowed}")
        return v.lower()

# GET /goods with optional search, pagination
@app.get("/goods", response_model=List[Good])
def get_goods(
    search: Optional[str] = Query(None, description="Search goods by name."),
    limit: int = Query(10, ge=1, description="Number of items to return."),
    offset: int = Query(0, ge=0, description="Number of items to skip.")
):
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        base_query = "SELECT id, name, status FROM goods"
        params = []
        if search:
            base_query += " WHERE name LIKE %s"
            params.append(f"%{search}%")
        base_query += " ORDER BY id LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(base_query, params)
        goods = cursor.fetchall()
    except Error:
        raise HTTPException(status_code=500, detail="Failed to fetch goods.")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'db' in locals(): db.close()
    return goods

# POST /lock to lock/unlock goods
@app.post("/lock")
def lock_good(update: GoodUpdate):
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE goods SET status = %s WHERE id = %s",
            (update.status, update.id)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Good not found.")
        db.commit()
    except HTTPException:
        raise
    except Error:
        raise HTTPException(status_code=500, detail="Failed to update status.")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'db' in locals(): db.close()
    return {"message": f"Good {update.id} status set to {update.status}."}
# Error handling

if __name__ == "__main__":
    uvicorn.run(
        "backend:app",  # import string for reload support
        host="0.0.0.0",
        port=8000,
        reload=True
    )
# This code is a FastAPI backend that connects to a MySQL database to manage goods.
