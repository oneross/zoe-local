import streamlit as st
import simplecache as sc

# Set up the cache
cache = sc.SimpleCache('tmp')

def save_jwt_to_cache(jwt_token, expiry=7200):
    # Save the JWT token to cache with a 2-hour expiry
    cache.set('jwt_token', jwt_token, expire=expiry)  # 7200 seconds = 2 hours

# Streamlit app layout
st.sidebar.title("JWT Token Configuration")
# Retrieve the current cached JWT token if available
default_jwt_token = cache['jwt_token']

# Text input for JWT token in the sidebar with a default value from the cache
jwt_token = st.sidebar.text_input("Enter JWT Token", value=default_jwt_token or "")

# Check if the input JWT token is different from the cached value
if jwt_token and jwt_token != default_jwt_token:
    # Update the cache with the new JWT token
    save_jwt_to_cache(jwt_token)
    st.sidebar.success("JWT Token updated and cached!")

# Main page display
st.write("Welcome to the JWT Token Configurator!")
if jwt_token:
    st.write("Current JWT Token:", jwt_token)
else:
    st.write("No JWT Token provided yet.")
