import streamlit as st

st.title("🎈 MAGALI BELOM MANDI")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
import streamlit as st

st.markdown("*FIKRI* is **really** ***cool***.")
st.markdown('''
    :red[FIKRI] :orange[can] :green[DO] :blue[ALL] :violet[ACTIVITY]
    :gray[SO] :rainbow[EASY] and :blue-background[highlight] text.''')
st.markdown("Here's a bouquet FOR FIKRI &mdash;\
            :tulip::cherry_blossom::rose::hibiscus::sunflower::blossom:")

multi = '''Be yourself; and never surrender

Two (or more) newline characters in a row will result in a hard return.
'''
st.markdown(multi)
import streamlit as st

number = st.number_input("Insert a number")
st.write("The current number is ", number)
