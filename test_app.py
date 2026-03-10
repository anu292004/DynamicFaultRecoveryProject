import streamlit as st

st.set_page_config(page_title="Test", page_icon="✅")
st.title("✅ App is working!")
st.write("If you can see this, Streamlit deployment is fine.")
st.write("Secrets test:")

try:
    uri = st.secrets["REDIRECT_URI"]
    st.success(f"✅ REDIRECT_URI found: {uri}")
except Exception as e:
    st.error(f"❌ REDIRECT_URI missing: {e}")

try:
    cid = st.secrets["google_secrets"]["client_id"]
    st.success(f"✅ google_secrets.client_id found")
except Exception as e:
    st.error(f"❌ google_secrets missing: {e}")
