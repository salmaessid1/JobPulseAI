import streamlit as st

st.set_page_config(page_title="Test", layout="wide")

st.sidebar.markdown("# Test Navigation")
page = st.sidebar.radio("Pages", ["A", "B", "C"])

if page == "A":
    st.title("Page A")
    st.write("Contenu de A")
elif page == "B":
    st.title("Page B")
    st.write("Contenu de B")
elif page == "C":
    st.title("Page C")
    st.write("Contenu de C")