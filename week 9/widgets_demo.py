import streamlit as st

st.title("2. Basic Widgets Demo")

st.header("Buttons & text inputs")
name = st.text_input("Enter your name:", "")
if st.button("say hello"):
    if name:
         st.success(f"Hello, {name}!")
    else:
        st.warning("Please enter your name first.")

st.divider()

st.header("Numeric inputs")
age = st.number_input("your age:", min_value=0, max_value=120, 
value=25)
st.write("You entered age:", age)
         
st.slider("pick a value", min_value=0, max_value=100, value=50, key="slider_example")

st.divider()

st.header("Selection widgets")
color = st.selectbox("favourite color", ["Red", "Green", "Blue"])
options = st.multiselect("choose some fruits", ["Apple", "Banana", "Orange", "Grapes"])
st.write("colour:", color)
st.write("fruits:", options)

st.divider()

st.header("Booleans and dates")
agree = st.checkbox("i agree to the terms")
if agree:
    st.write("Thank you for agreeing!")

date = st.date_input("select a date")
st.write("chosen date:", date)
