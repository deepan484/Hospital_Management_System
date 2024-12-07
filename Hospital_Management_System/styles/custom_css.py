import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
    body {
        background-color: #f0f4f8;
        font-family: 'Arial', sans-serif;
    }
    .header {
        background-color: #007bff;
        color: white;
        padding: 20px;
        text-align: center;
        border-radius: 10px;
    }
    .header img {
        width: 120px;
    }
 
    .custom-tagline {
        color: #FFD700; 
        font-size: 1.2em; 
        text-align: center; 
}

    h1 {
        font-size: 36px;
        margin: 0;
    }
    .content {
        text-align: center;
        padding: 30px;
        color: black;
        background-color: white  ;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        margin: 20px;
    }
    
    .content h2{
        color: #007bff;
    }

    .custom-button {
        background-color: #007bff;
        border: none;
        color: white;
        padding: 15px 25px;
        font-size: 18px;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.3s;
        margin: 10px;
    }
    .footer {
        text-align: center;
        margin-top: 40px;
        color: #666;
        font-size: 14px;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
