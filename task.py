import streamlit as st
st.sidebar.title("Menu")
st.write("Choose an option:")
option = st.sidebar.radio(
"Choose page",
["Register", "Login"]
)
if option == "Register":
    st.header("Registration Form")
    with st.form("register"):
        fname = st.text_input("First Name")
        lname = st.text_input("Last Name")
        uname = st.text_input("User Name")
        pwd = st.text_input("Password",type= "password")
        register = st.form_submit_button("register")
        if register:
            st.success("Registration Successful")
            st.write(fname, lname, uname)
elif option == "Login":
    st.header("login")
    with st.form("login_from"):
        uname = st.text_input("User Name")
        pwd = st.text_input("Password",type="password")
        login = st.form_submit_button("login")
        if login:
            st.success("Login Successful")
            st.write(uname)