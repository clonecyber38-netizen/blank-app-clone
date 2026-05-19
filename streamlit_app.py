import streamlit as st

st.title("🎈 MAGALI BELOM MANDI")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
import streamlit as st

st.markdown("*magali* itu **males** ***mandi***.")
st.markdown('''
    :red[kita] :orange[semua] :green[gatau] :blue[kenapa] :violet[magali]
    :gray[males] :rainbow[mandi] dan :blue-background[magali] mager.''')
st.markdown("Here's a bouquet FOR magali si males mandi &mdash;\
            :tulip::cherry_blossom::rose::hibiscus::sunflower::blossom:")

multi = '''mandi lah sebelum di mandikan

biarkan air yg menemuiku
'''
st.markdown(multi)
import streamlit as st

number = st.number_input("Insert a number")
st.write("The current number is ", number)
