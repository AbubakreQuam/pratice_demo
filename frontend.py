# frontend.py
import streamlit as st
import requests
import pandas as pd
from requests.exceptions import RequestException

BACKEND_URL = "https://praticedemo-bodpogd8vsnpgrebbeczcc.streamlit.app/"

# Page config
st.set_page_config(page_title="Goods Dashboard", layout="wide")
st.title("📦 Available Goods Dashboard")

# Session state defaults
if 'goods' not in st.session_state:
    st.session_state.goods = []
if 'search' not in st.session_state:
    st.session_state.search = ""
if 'limit' not in st.session_state:
    st.session_state.limit = 10
if 'page' not in st.session_state:
    st.session_state.page = 1

# Fetch goods from backend
def fetch_goods():
    params = {
        'search': st.session_state.search or None,
        'limit': st.session_state.limit,
        'offset': (st.session_state.page - 1) * st.session_state.limit
    }
    try:
        with st.spinner("Loading goods..."):
            resp = requests.get(f"{BACKEND_URL}/goods", params=params, timeout=5)
            resp.raise_for_status()
            st.session_state.goods = resp.json()
    except RequestException as e:
        st.error(f"Error fetching goods: {e}")
        st.session_state.goods = []

# Update status callback (lock/unlock)
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

# Controls: search, limit, navigation
with st.sidebar:
    st.header("Controls")
    st.session_state.search = st.text_input("Search by name", st.session_state.search)
    st.session_state.limit = st.number_input("Items per page", min_value=1, max_value=100, value=st.session_state.limit)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Previous") and st.session_state.page > 1:
            st.session_state.page -= 1
    with col2:
        if st.button("Next"):
            st.session_state.page += 1
    if st.button("Refresh"):
        st.session_state.page = 1
    st.write(f"Page: {st.session_state.page}")

# Initial load
fetch_goods()

# Display goods table
goods = st.session_state.goods
if goods:
    df = pd.DataFrame(goods)[['id', 'name', 'status']]
    st.dataframe(df, use_container_width=True)
    for g in goods:
        col1, col2 = st.columns([3,1])
        col1.write(f"**{g['id']}**: {g['name']}" )
        if g['status'] == 'locked':
            col2.button(
                "Unlock",
                key=f"unlock-{g['id']}",
                on_click=update_status_callback,
                args=(g['id'], 'unlocked')
            )
        else:
            col2.button(
                "Lock",
                key=f"lock-{g['id']}",
                on_click=update_status_callback,
                args=(g['id'], 'locked')
            )
else:
    st.info("No goods to display.")
