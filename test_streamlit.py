import streamlit as st

st.title("🧪 Streamlit Test")
st.write("If you can see this, Streamlit is working!")

if st.button("Test Button"):
    st.success("✅ Button works!")
    
st.write("**Environment Info:**")
st.write(f"- Python version: {st.__version__}")
st.write("- This is a simple test to verify Streamlit is working")