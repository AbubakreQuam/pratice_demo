# frontend.py
import streamlit as st
import requests
import pandas as pd
from requests.exceptions import RequestException

# ===================== CONFIG =====================
BACKEND_URL = st.secrets.get("BACKEND_URL", "https://praticedemo-bodpogd8vsnpgrebbeczcc.streamlit.app/")
# ==================================================

st.set_page_config(page_title="Goods Dashboard", layout="wide")
st.title("📦 Available Goods Dashboard")

# ===== Session State Defaults =====
if 'goods' not in st.session_state:
    st.session_state.goods = []
if 'search' not in st.session_state:
    st.session_state.search = ""
if 'limit' not in st.session_state:
    st.session_state.limit = 10
if 'page' not in st.session_state:
    st.session_state.page = 1

# ===== Fetch Goods =====
def fetch_goods(show_debug=False):
    params = {
        'search': st.session_state.search or None,
        'limit': st.session_state.limit,
        'offset': (st.session_state.page - 1) * st.session_state.limit
    }
    try:
        with st.spinner("Loading goods..."):
            response = requests.get(f"{BACKEND_URL}/goods", params=params, timeout=5)
            if show_debug:
                st.write("Status code:", response.status_code)
                st.write("Content-Type:", response.headers.get('content-type'))
                st.write("Response body (first 200 chars):", response.text[:200])
            response.raise_for_status()
            st.session_state.goods = response.json()
    except RequestException as e:
        st.error(f"Error fetching goods: {e}")
        # Attempt to display response details if available
        try:
            st.write("Debug info:")
            st.write("Response text:", response.text)
        except Exception:
            pass
        st.session_state.goods = []

# ===== Update Status (Lock/Unlock) =====
def update_status_callback(good_id, status):
    try:
        with st.spinner(f"Updating status for ID {good_id}..."):
            resp = requests.post(
                f"{BACKEND_URL}/lock", 
                json={"id": good_id, "status": status},
                timeout=5
            )
            resp.raise_for_status()
            st.success(f"Good {good_id}: {status}")
            fetch_goods()
    except RequestException as e:
        st.error(f"Error updating status: {e}")

# ===== Sidebar Controls =====
with st.sidebar:
    st.header("Controls")
    st.session_state.search = st.text_input("Search by name", st.session_state.search)
    st.session_state.limit = st.number_input(
        "Items per page", min_value=1, max_value=100, value=st.session_state.limit
    )
    nav_col1, nav_col2 = st.columns(2)
    with nav_col1:
        if st.button("Previous") and st.session_state.page > 1:
            st.session_state.page -= 1
    with nav_col2:
        if st.button("Next"):
            st.session_state.page += 1
    if st.button("Refresh"):
        st.session_state.page = 1
    # Debug toggle
    show_debug = st.checkbox("Show Debug Info", value=False)

# ===== Initial Load =====
fetch_goods(show_debug=show_debug)

# ===== Display Goods =====
goods = st.session_state.goods
if goods:
    df = pd.DataFrame(goods)[['id', 'name', 'status']]
    st.dataframe(df, use_container_width=True)
    for g in goods:
        col1, col2 = st.columns([3, 1])
        col1.write(f"**{g['id']}**: {g['name']}" )
        btn_label = "Unlock" if g['status']=='locked' else "Lock"
        new_status = 'unlocked' if g['status']=='locked' else 'locked'
        col2.button(
            btn_label,
            key=f"btn-{g['id']}",
            on_click=update_status_callback,
            args=(g['id'], new_status)
        )
else:
    st.info("No goods to display.")

# ===== Footer Style Hide =====
st.markdown(
    """
    <style>
        footer {visibility: hidden;} 
        .css-1d391kg {display: none;}
    </style>
    """, unsafe_allow_html=True
)

