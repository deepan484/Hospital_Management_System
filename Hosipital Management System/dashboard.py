import streamlit as st
from auth import get_patient_details, get_patient_id, get_available_slots, book_slot, get_scheduled_appointments, delete_appointment
from auth import get_doctor_details, get_upcoming_appointments, get_completed_appointments, change_appointment_status, get_doctors
from auth import add_doctor, remove_doctor, get_departments
from auth import view_departments_and_doctors, search_doctor_by_email, cancel_appointment, get_completed_appointments_for_patient
from auth import add_availability, remove_booked_availability
from datetime import date
import datetime

today = datetime.date.today()

def patient_dashboard(email):
    # Title and Introduction
    st.markdown('<h2 style="color: #007bff; text-align: center;">Patient Dashboard</h2>', unsafe_allow_html=True)

    # Fetch and display patient details
    patient_details = get_patient_details(email)

    if patient_details:
        name, medical_history, date_of_birth, gender, blood_group, address = patient_details
        medical_history = medical_history if medical_history else "None"
        
        st.markdown(f"""<div style="background-color: #f0f8ff; padding: 10px; border-radius: 10px;">
        <h3 style="color: #343a40;">Welcome back, {name}!</h3>
        <p style="color: black;"><strong>Email: {email}</p>
        <p style="color: black;"><strong>Date of Birth:</strong> {date_of_birth}</p>
        <p style="color: black;"><strong>Gender:</strong> {gender}</p>
        <p style="color: black;"><strong>Blood Group:</strong> {blood_group}</p>
        <p style="color: black;"><strong>Address:</strong> {address}</p>
        <p style="color: black;"><strong>Medical History:</strong> {medical_history}</p>
        </div> """, unsafe_allow_html=True)

    else:
        st.error("No patient details found.")
        return

    # Horizontal divider
    st.markdown("<hr>", unsafe_allow_html=True)

    # Appointment Booking Section
    st.markdown('<h3 style="color: #007bff;">Book an Appointment</h3>', unsafe_allow_html=True)

    # Doctor list with specializations
    doctors = get_doctors()
    doctor_dict = {doctor[0]: f"{doctor[1]} - {doctor[2]}" for doctor in doctors}

    # Select Doctor and Date
    doctor_id = st.selectbox("Choose your doctor", options=list(doctor_dict.keys()), 
                             format_func=lambda x: doctor_dict[x])  # Show names and specializations
                             
                             
    appointment_date = st.date_input("Select appointment date", min_value=date.today())

    # Fetch available slots based on selected doctor and date
    available_slots = get_available_slots(doctor_id, appointment_date)

    if available_slots:
        # Format the available slots for selection
        formatted_slots = [(slot[0].strftime("%H:%M"), slot[1].strftime("%H:%M")) for slot in available_slots]
        selected_slot = st.selectbox("Available Time Slots", options=formatted_slots, 
                                      format_func=lambda x: f"{x[0]} to {x[1]}")

        if st.button("Book Appointment", key="book_btn"):
            with st.spinner("Booking your appointment..."):
                patient_id = get_patient_id(email)  # Fetch patient ID based on email
                if not patient_id:
                    st.error("Error: Patient ID not found.")
                    return
                
                # Find the corresponding start_time from the selected slot
                start_time = next((slot[0] for slot in available_slots if slot[0].strftime("%H:%M") == selected_slot[0]), None)
                if not start_time:
                    st.error("Error: Start time not found for selected slot.")
                    return

                success, message = book_slot(patient_id, doctor_id, appointment_date, start_time)  # Pass the patient_id
                if success:
                    st.success(f"Appointment booked for {appointment_date} at {selected_slot[0]}.")
                else:
                    st.error(f"Booking failed: {message}")

    else:
        st.warning("No available slots for this doctor on the selected date.")

    # Horizontal divider
    st.markdown("<hr>", unsafe_allow_html=True)

    # Display Scheduled Appointments
    st.subheader("Your Scheduled Appointments")

    patient_id = get_patient_id(email)
    appointments = get_scheduled_appointments(patient_id)

    if appointments:
        for appointment in appointments:
            st.write("Debug: Appointment data:", appointment)  # Display the full appointment tuple for debugging
            
            # Try to adjust based on actual structure of appointment
            try:
                appointment_date = appointment[0]
                start_time = appointment[1]
                status = appointment[2]
                doctor_name = appointment[3]
                appointment_id = appointment[4]  # Check if appointment_id is in position 4

                st.markdown(f"""
                    <div style="background-color: #e0f7fa; padding: 10px; margin-bottom: 10px; border-radius: 5px;">
                        <p style="color: black;">Doctor: {doctor_name}</p>
                        <p style="color: black;">Date: {appointment_date}</p>
                        <p style="color: black;">Time: {start_time}</p>
                        <p style="color: black;">Status: {status}</p>
                    </div>
                """, unsafe_allow_html=True)

                # Add a button for deletion of this appointment
                if st.button(f"Cancel Appointment with {doctor_name} on {appointment_date} at {start_time}", key=f"del_btn_{appointment_id}"):

                    with st.spinner("Deleting your appointment..."):
                        success, message = delete_appointment(appointment_id)
                        if success:
                            st.success(f"Appointment with {doctor_name} on {appointment_date} at {start_time} successfully deleted.")
                        else:
                            st.error(f"Failed to delete appointment: {message}")

            except IndexError:
                st.error("Error: Appointment data structure is not as expected.")
    else:
        st.write("No scheduled appointments found or an error occurred.")

        
        # Horizontal divider
        st.markdown("<hr>", unsafe_allow_html=True)

        # Display Completed Appointments
    st.subheader("Completed Appointments")
    
    completed_appointments = get_completed_appointments_for_patient(patient_id)

    if completed_appointments:
        for appointment in completed_appointments:
            appointment_date = appointment[0]
            start_time = appointment[1]
            doctor_name = appointment[2]  # Adjusted index to access doctor_name
            appointment_id = appointment[4]  # Added to access appointment_id

            st.markdown(f"""
            <div style="background-color: #d1f0d1; padding: 10px; margin-bottom: 10px; border-radius: 5px;">
                <p style="color: black; font-weight: bold;">Doctor: {doctor_name}</p>
                <p style="color: black;">Date: {appointment_date}</p>
                <p style="color: black;">Time: {start_time}</p>
                <p style="color: black;">Appointment ID: {appointment_id}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("No completed appointments found.")

        
def doctor_dashboard(email):
    doctor_details = get_doctor_details(email)
    if not doctor_details:
        st.error("Doctor not found.")
        return
    
    doctor_id = doctor_details[0]
    st.title(f"Welcome back, {doctor_details[1]}!")

    # Fetch upcoming appointments
    upcoming_appointments = get_upcoming_appointments(doctor_id)
    completed_appointments = get_completed_appointments(doctor_id)

    # Display Upcoming Appointments
    st.subheader("Upcoming Appointments")
    if upcoming_appointments:
        for appointment in upcoming_appointments:
            appointment_date, start_time, patient_name, status, appointment_id = appointment
            
            st.markdown(f"""<div style="background-color: #e0f7fa; padding: 10px; margin-bottom: 10px; border-radius: 5px;">
                        <p style="color: black;">Patient_name: {patient_name}</p>
                        <p style="color: black;">Date: {appointment_date}</p>
                        <p style="color: black;">Time: {start_time}</p>
                        <p style="color: black;">Status: {status}</p>
                        <p style="color: black;">Appointment_ID: {appointment_id}</p>
                        </div> """,unsafe_allow_html=True)

            
            if st.button(f"Mark as Completed: ID --> {appointment_id}"):
                st.write("Mark as Completed button clicked.")  # Debug
                # Change the appointment status to completed
                success, message = change_appointment_status(appointment_id, 'completed')

                if success:
                    st.success(f"Appointment marked as completed.")
                else:
                    st.error(f"Failed to mark appointment as completed: {message}")

    else:
        st.write("No upcoming appointments found.")

    # Completed Appointments Section
    st.subheader("Completed Appointments")
    if completed_appointments:
        for appointment in completed_appointments:
            appointment_date, start_time, patient_name, status, appointment_id = appointment
            st.markdown(f"""
                    <div style="background-color: #e0f7fa; padding: 10px; margin-bottom: 10px; border-radius: 5px;">
                        <p style="color: black;">Patient_name: {patient_name}</p>
                        <p style="color: black;">Date: {appointment_date}</p>
                        <p style="color: black;">Time: {start_time}</p>
                        <p style="color: black;">Status: {status}</p>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.write("No completed appointments found.")
            
def manager_dashboard():
    st.title("Manager Dashboard")
    st.write("Welcome back, Admin!")

    # Option to select action
    option = st.selectbox("Choose an action", ["Add Doctor", "Remove Doctor", "View Department wise doctors", "Search Doctor by email", "Add Availability", "Drop Availability"])

    if option == "Add Doctor":
        with st.form(key='add_doctor_form'):
            name = st.text_input("Name")
            dob = st.date_input('Date of Birth', min_value=datetime.date(1900, 1, 1), max_value=today)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            address = st.text_area("Address")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            departments = get_departments()

            # Create a dictionary to map department IDs to names
            dept_dict = {dept[0]: dept[1] for dept in departments}  # Fixed the issue here
            
            # Select department by name
            dept_id = st.selectbox("Department", options=list(dept_dict.keys()), format_func=lambda x: dept_dict[x])
            submit_button = st.form_submit_button("Add Doctor")

            if submit_button:
                success, message = add_doctor(name, dob, gender, address, email, password, dept_id)
                if success:
                    st.success(message)
                else:
                    st.error(f"Failed to add doctor: {message}")


    elif option == "Remove Doctor":
        # Fetch the list of doctors to remove
        doctors = get_doctors()  # Assuming this returns a list of tuples (doctor_id, name, specialization)
        doctor_dict = {doctor[0]: f"{doctor[1]} - {doctor[2]}" for doctor in doctors}

        doctor_id_to_remove = st.selectbox("Select Doctor to Remove", options=list(doctor_dict.keys()), 
                                            format_func=lambda x: doctor_dict[x])  # Show names and specializations

        if st.button("Remove Doctor"):
            with st.spinner("Removing doctor..."):
                success, message = remove_doctor(doctor_id_to_remove)  # Call the remove_doctor function
                if success:
                    st.success(message)
                else:
                    st.error(f"Failed to remove doctor: {message}")
    
    elif option == "View Department wise doctors":
        result = view_departments_and_doctors() 
        departments = {}
           
        for row in result:
            dept_name = row[0]
            doctor_name = row[1]
            doctor_email = row[2]
            if dept_name not in departments:
                departments[dept_name] = []
            departments[dept_name].append(f'{doctor_name} ({doctor_email})')

        for dept, doctors in departments.items():
            st.write(f"**Department: {dept}**")
            for doctor in doctors:
                st.write(f"- {doctor}")
                
    elif option == "Search Doctor by email":
        email = st.text_input("Enter Doctor's Email")

        # Use session state to persist doctor info and appointments
        if 'doctor_info' not in st.session_state:
            st.session_state['doctor_info'] = None
        if 'appointments' not in st.session_state:
            st.session_state['appointments'] = None

        if st.button("Search"):
            doctor_info, appointments = search_doctor_by_email(email)  # Fetch doctor and appointment data
            st.session_state['doctor_info'] = doctor_info
            st.session_state['appointments'] = appointments

        # Check if doctor info exists in session state and display it
        if st.session_state['doctor_info']:
            doctor_info = st.session_state['doctor_info']
            appointments = st.session_state['appointments']

            st.write("**Doctor Details:**")
            st.write(f"Name: {doctor_info[1]}")
            st.write(f"Doctor - ID:{doctor_info[0]}")
            st.write(f"Date of Birth: {doctor_info[2]}")
            st.write(f"Gender: {doctor_info[3]}")
            st.write(f"Address: {doctor_info[4]}")
            st.write(f"Email: {doctor_info[5]}")
            st.write(f"Department: {doctor_info[6]}")

            if appointments:
                st.write("**Upcoming Appointments:**")
                for appointment in appointments:
                    appointment_id = appointment[0]
                    appointment_date = appointment[1]
                    appointment_time = appointment[2]
                    status = appointment[3]

                    st.write(f"- Appointment ID: {appointment_id}, Date: {appointment_date}, Time: {appointment_time}, Status: {status}")
                    
                    # Add cancel button for each appointment with a unique key
                    if st.button(f"Cancel Appointment {appointment_id}", key=f"cancel_{appointment_id}"):
                        cancel_appointment(appointment_id)  # Ensure cancel_appointment is implemented correctly
                        st.success(f"Appointment {appointment_id} has been cancelled.")

                        # Refresh appointments after cancellation
                        _, updated_appointments = search_doctor_by_email(email)
                        st.session_state['appointments'] = updated_appointments
            else:
                st.write("No upcoming appointments.")
        else:
            st.write("No doctor found with the given email.")
            
    elif option == "Add Availability":
        doctors = get_doctors()  # Fetch the list of doctors
        doctor_dict = {doctor[0]: doctor[1] for doctor in doctors}  # doctor[0] is doctor_id, doctor[1] is doctor_name
        doctor_id = st.selectbox("Select Doctor", options=list(doctor_dict.keys()), format_func=lambda x: doctor_dict[x])

        appointment_date = st.date_input("Select Date", min_value=today)  # Prevent past dates
        
        # Start time options from 10:00 AM to 5:00 PM in 30-minute increments
        start_time_options = [
            datetime.time(10, 0), datetime.time(10, 30), 
            datetime.time(11, 0), datetime.time(11, 30), 
            datetime.time(1, 30), datetime.time(2, 0), 
            datetime.time(2, 30), datetime.time(3, 0), 
            datetime.time(3, 30), datetime.time(4, 0), 
            datetime.time(4, 30), datetime.time(5, 0)
        ]
        
        start_time = st.selectbox("Select Start Time", start_time_options)

        # Calculate end time as 30 minutes after start time
        end_time = (datetime.datetime.combine(datetime.date.today(), start_time) + datetime.timedelta(minutes=30)).time()

        if st.button("Add Availability"):
            success, message = add_availability(doctor_id, appointment_date, start_time, end_time)  # Implement this function
            if success:
                st.success(message)
            else:
                st.error(message)
                
    elif option == "Remove Booked Availability":
        doctors = get_doctors()  # Fetch the list of doctors
        doctor_dict = {doctor[0]: doctor[1] for doctor in doctors}
        doctor_id = st.selectbox("Select Doctor", options=list(doctor_dict.keys()), format_func=lambda x: doctor_dict[x])
        
        appointment_date = st.date_input("Select Date")
        start_time = st.time_input("Select Start Time")

        if st.button("Remove Booked Availability"):
            success, message = remove_booked_availability(doctor_id, appointment_date, start_time)
            if success:
                st.success(message)
            else:
                st.error(message)

        
