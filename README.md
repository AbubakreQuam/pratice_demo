## Available Goods Dashboard

A simple Streamlit frontend and FastAPI backend application for listing, filtering, and locking goods stored in a MySQL database.

---

### 🚀 Features

* **View Goods**: Display all available goods with current status.
* **Filter**: Show all, locked, or unlocked goods.
* **Lock Goods**: Change a good’s status to `locked` via the UI.
* **Error Handling**: Robust feedback for network and database errors.

---

### 📦 Project Structure

```
/practice_demo
├── backend.py          # FastAPI application
├── frontend.py         # Streamlit dashboard
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

### 🔧 Prerequisites

* Python 3.10+
* MySQL Server

---

### ⚙️ Setup MySQL Database

1. **Install MySQL** if not already installed.
2. **Create database and table**:

   ```sql
   CREATE DATABASE goods_db;
   USE goods_db;
   CREATE TABLE goods (
       id INT AUTO_INCREMENT PRIMARY KEY,
       name VARCHAR(255) NOT NULL,
       status VARCHAR(50) NOT NULL DEFAULT 'unlocked'
   );
   INSERT INTO goods (name) VALUES
       ('Milk'), ('Bread'), ('Cheese');
   ```
3. **Create dedicated user (optional but recommended)**:

   ```sql
   CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'password123';
   GRANT ALL PRIVILEGES ON goods_db.* TO 'appuser'@'localhost';
   FLUSH PRIVILEGES;
   ```

---

### 🔨 Running the Backend

1. Configure credentials in `backend.py`:

   ```python
   conn = mysql.connector.connect(
       host="localhost",
       user="root",          # or 'appuser'
       password="your_password",
       database="goods_db"
   )
   ```
2. Start the server:

   ```bash
   python backend.py
   ```

   The FastAPI app will listen on `http://0.0.0.0:8000`.

---

### 🔨 Running the Frontend

1. Ensure backend is running.
2. Start Streamlit:

   ```bash
   streamlit run frontend.py
   ```
3. Open your browser at `http://localhost:8501`.

---

### ⚙️ Configuration

* **Backend URL**: Update `BACKEND_URL` in `frontend.py` if needed.
* **MySQL Settings**: Adjust host, user, password in `backend.py`.

---

### 📄 API Endpoints

| Method | Endpoint | Description       |
| ------ | -------- | ----------------- |
| GET    | /goods   | Fetch all goods   |
| POST   | /lock    | Lock a good by ID |

---

### 🛡️ Security & Error Handling

* Parameterized queries prevent SQL injection.
* Status values are validated by Pydantic.
* All DB operations wrapped in `try/except` with user-friendly messages.

---

### 🏗️ Future Improvements

* Add unlock functionality.
* Pagination and search.
* Authentication and authorization.
* Docker Compose for easy deployment.

---

### 🙋‍♂️ Contact

For issues or feature requests, please open an issue or reach out to the maintainer.

