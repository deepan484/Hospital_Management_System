import streamlit as st
from auth import validate_login, signup_patient
from utils import load_image, is_valid_email
from dashboard import patient_dashboard, doctor_dashboard, manager_dashboard  # Import patient_dashboard function
import datetime


today = datetime.date.today()

# Load the logo image
image_data = load_image('logo.png')  # Path to logo

# Custom CSS
from styles.custom_css import apply_custom_css
apply_custom_css()  # Call the function to apply CSS

# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role_id = None
    st.session_state.email = None

# Header Section
st.markdown(f"""
<div class="header">
    <div style="display: flex; align-items: center; color: blue;">
        <img src="data:image/png;base64,{image_data}" alt="Health Hub Logo" style="width: 120px; margin-right: 20px;">
        <div>
            <h1 style="margin: 0;">Health Hub</h1>
            <p class="custom-tagline">Your Trusted Partner in Comprehensive Healthcare Solutions</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ("Home", "Login"))

# Main Content
if page == "Home":
    st.markdown('<div class="content"><h2 style="color: #007bff;">Welcome to Health Hub!</h2><p>Your health is our priority. Explore our services tailored for patients, doctors, and healthcare managers. Join us in taking charge of your health today!</p></div>', unsafe_allow_html=True)

    # Additional Information Section
    st.markdown("""
        <div class="content">
            <h3 style="color: #007bff;" >What You Can Do:</h3>
            <ul>
                <li><strong>Patients:</strong> Schedule, view, and cancel appointments.</li>
                <li><strong>Doctors:</strong> Manage appointments, review patient records.</li>
                <li><strong>Managers:</strong> Oversee staff, manage resources.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
elif page == "Login":
    st.markdown('<div class="content"><h2>Login</h2></div>', unsafe_allow_html=True)

    # If the user is not logged in, show the login form
    if not st.session_state.logged_in:
        email = st.text_input('Email')
        password = st.text_input('Password', type='password')
    
        if st.button('Login'):
            user = validate_login(email, password)
            if user:
                role_id = user[3]  # Assuming role_id is the fourth column
                st.session_state.logged_in = True
                st.session_state.role_id = role_id
                st.session_state.email = email
                st.success("Login successful!")
                
                # No need to immediately display the dashboard here
                # It will be handled in the next session state check below

            else:
                st.error("Invalid credentials.")
    
    # If the user is logged in and role is 'Patient', show patient dashboard
    if st.session_state.logged_in and st.session_state.role_id == 1:
        patient_dashboard(st.session_state.email)
        
    elif st.session_state.logged_in and st.session_state.role_id == 2:
        doctor_dashboard(st.session_state.email)
        
    elif st.session_state.logged_in and st.session_state.role_id == 3:
        manager_dashboard()

    

    # Show the signup form only if the user is not logged in
    if not st.session_state.logged_in:
        selected_role = st.radio("Would you like to sign up as a patient?", ["Yes", "No"])
        if selected_role == 'Yes':
            st.markdown('<h2 style="color: #007bff;">Patient Signup</h2>', unsafe_allow_html=True)
            
            with st.form(key='signup_form', clear_on_submit=True):
                name = st.text_input('Full Name')
                email = st.text_input('Email')
                password = st.text_input('Password', type='password')
                date_of_birth = st.date_input('Date of Birth', min_value=datetime.date(1900, 1, 1), max_value=today)
                gender = st.selectbox('Gender', ['Male', 'Female', 'Other'])
                medical_history = st.text_area('Medical History')
                blood_group = st.selectbox('Blood Group', ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'])
                address = st.text_input('Address')

                signup_button = st.form_submit_button(label='Sign Up')
                
                if signup_button:
                    if not name or not email or not password or not address:
                        st.error("Full Name, Email, Password, and Address are required fields.")
                    elif not date_of_birth or not gender:
                        st.error("Date of Birth and Gender are required fields.")
                    elif not is_valid_email(email):
                        st.error("Please enter a valid email address.")
                    else:
                        success, message = signup_patient(name, email, password, 1, medical_history, date_of_birth, gender, blood_group, address)
                        if success:
                            st.success("Sign-up successful!")
                        else:
                            st.error(f"Sign-up failed: {message}")


# Footer
st.markdown('<footer><div class="footer">© 2024 Health Hub. All rights reserved.</div></footer>', unsafe_allow_html=True)
