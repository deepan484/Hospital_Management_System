from database import get_db_connection
from datetime import datetime

def validate_login(email, password):
    """Validate user login credentials."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE email=%s AND password=%s"
    cursor.execute(query, (email, password))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result


def signup_patient(name, email, password, role_id, medical_history, date_of_birth, gender, blood_group, address):
    """Register a new patient."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Insert into User table
        cursor.execute("INSERT INTO users (email, password, role_id) VALUES (%s, %s, %s) RETURNING user_id", 
                       (email, password, role_id))
        user_id = cursor.fetchone()[0]

        # Insert into Patient table
        cursor.execute("INSERT INTO patients (user_id, name, medical_history, date_of_birth, gender, blood_group, address) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                       (user_id, name, medical_history, date_of_birth, gender, blood_group, address))
        conn.commit()
        return True, "User registered successfully."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cursor.close()
        conn.close()


def get_patient_details(email):
    """Fetch patient details using the user's email."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT p.name, p.medical_history, p.date_of_birth, p.gender, p.blood_group, p.address
    FROM patients p
    JOIN users u ON p.user_id = u.user_id
    WHERE u.email = %s
    """
    cursor.execute(query, (email,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result

def get_doctors():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT d.doctor_id, d.name, dept.department_name
            FROM doctors d
            JOIN departments dept ON d.dept_id = dept.dept_id
            """
            
            # Execute the query and fetch all rows
        cursor.execute(query)
        doctors = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return doctors

    except Exception as e:
        print(f"Error fetching doctors: {e}")
        return []
    


def get_available_slots(doctor_id, appointment_date):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to fetch available slots
    query = """
    SELECT a.start_time, a.end_time 
    FROM availability a
    WHERE a.doctor_id = %s 
    AND a.available_date = %s 
    AND a.slot_status = 'available'
    ORDER BY a.start_time
    """
    cursor.execute(query, (doctor_id, appointment_date))
    available_slots = cursor.fetchall()

    cursor.close()
    conn.close()
    return available_slots

# Inside your patient_dashboard function, update this line:

def book_slot(patient_id, doctor_id, appointment_date, start_time):
    # Convert start_time (datetime.time) to a time object if not already
    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time, "%H:%M").time()  # Adjust format as needed

    # Check for existing appointments that conflict
    if check_conflict(patient_id, doctor_id, appointment_date, start_time):
        return False, "Booking failed: Time slot is already booked."

    # Logic to book the appointment (e.g., inserting into the database)
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Insert the appointment into the database
        insert_query = """INSERT INTO appointments (patient_id, doctor_id, appointment_date, start_time, status)
                          VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(insert_query, (patient_id, doctor_id, appointment_date, start_time, 'booked'))

        # Update slot status in availability (if required)
        update_query = """UPDATE availability 
                          SET slot_status = 'booked' 
                          WHERE doctor_id = %s AND available_date = %s AND start_time = %s"""
        cursor.execute(update_query, (doctor_id, appointment_date, start_time))

        # Commit the transaction
        connection.commit()

        return True, "Appointment booked successfully."

    except Exception as e:
        return False, f"Error: {str(e)}"
    
    finally:
        if connection:
            cursor.close()
            connection.close()

def check_conflict(patient_id, doctor_id, appointment_date, start_time):
    """Check for existing appointments that conflict with the requested time."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Query to check for overlapping appointments for the patient
        check_query = """
        SELECT COUNT(*) FROM appointments
        WHERE patient_id = %s 
          AND appointment_date = %s 
          AND start_time = %s
          AND status = 'booked'
        """
        cursor.execute(check_query, (patient_id, appointment_date, start_time))
        count = cursor.fetchone()[0]

        return count > 0  # Return True if there is a conflict

    except Exception as e:
        print(f"Error checking conflicts: {str(e)}")
        return True  # Assume conflict if there's an error
    
    finally:
        if connection:
            cursor.close()
            connection.close()



def get_patient_id(email):
    """Fetch the patient ID based on the user's email."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to fetch the patient_id based on the user's email
    query = """
        SELECT patient_id FROM patients
        JOIN users ON patients.user_id = users.user_id
        WHERE users.email = %s
    """
    cursor.execute(query, (email,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result[0] if result else None  # Return patient_id or None if not found
    

def get_scheduled_appointments(patient_id):
    """Fetch all scheduled appointments for the logged-in patient."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Fetch all appointments for the logged-in patient
        cursor.execute("""
            SELECT a.appointment_date, a.start_time, a.status, d.name, a.appointment_id
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.patient_id = %s and a.status = 'booked'
            ORDER BY a.appointment_date, a.start_time
        """, (patient_id,))

        appointments = cursor.fetchall()

        return appointments  # Return the list of appointments
    except Exception as e:
        print(f"Error in get_scheduled_appointments: {e}")  # Log the error
        return []  # Return an empty list
    finally:
        cursor.close()
        conn.close()
        
def delete_appointment(appointment_id):
    """Delete an appointment from the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT doctor_id, appointment_date, start_time FROM appointments WHERE appointment_id = %s", (appointment_id,))
        result = cursor.fetchone()
        
        if result:
            doctor_id, appointment_date, start_time = result
            
            cursor.execute("DELETE FROM appointments WHERE appointment_id = %s", (appointment_id,))
                
                # Update the availability table to set the status to 'available'
            cursor.execute("""
                UPDATE availability
                SET slot_status = 'available'
                WHERE doctor_id = %s AND available_date = %s AND start_time = %s
            """, (doctor_id, appointment_date, start_time))

            conn.commit()  # Commit the transaction

            return True, "Appointment deleted and slot marked as available."
        else:
            return False, "Appointment not found."
    except Exception as e:
        return False, str(e)
    finally:
        if conn:
            cursor.close()
            conn.close()

def get_completed_appointments_for_patient(patient_id): # To retrive the completed appointments foR the patients
    """Fetch completed appointments for the patient."""
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.appointment_date, a.start_time, d.name AS doctor_name, a.status, a.appointment_id
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.patient_id = %s AND a.status = 'completed'
            ORDER BY a.appointment_date DESC
        """, (patient_id,))
        return cursor.fetchall()


def get_doctor_details(email):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT doctor_id, name FROM doctors WHERE user_id = (SELECT user_id FROM users WHERE email = %s)", (email,))
        return cursor.fetchone()


def change_appointment_status(appointment_id, status):
    try:
        # Database operations
        conn = get_db_connection()
        cursor = conn.cursor()
        print(f"Updating appointment ID: {appointment_id} to status: {status}")  # Debug

        # Update the appointment status in the database
        cursor.execute("UPDATE appointments SET status = %s WHERE appointment_id = %s", (status, appointment_id))
        conn.commit()  # Commit the changes
        
        # Fetch the details of the appointment
        cursor.execute("SELECT doctor_id, appointment_date, start_time FROM appointments WHERE appointment_id = %s", (appointment_id,))
        appointment = cursor.fetchone()

        if appointment:  # Check if an appointment was found
            doctor_id, appointment_date, start_time = appointment
            
            # Update the slot_status in the availability table
            cursor.execute("UPDATE availability SET slot_status = 'completed' WHERE doctor_id = %s AND available_date = %s AND start_time = %s",
                           (doctor_id, appointment_date, start_time))
            conn.commit()  # Commit the changes
            print("Appointment status updated.")  # Debug

            return True, "Appointment status updated successfully."
        else:
            return False, "Appointment not found."

    except Exception as e:
        print(f"Error occurred in change_appointment_status: {e}")  # Debug
        return False, str(e)
    finally:
        cursor.close()  # Ensure the cursor is closed
        conn.close()    # Ensure the connection is closed



def get_upcoming_appointments(doctor_id):
    """Fetch upcoming appointments for the doctor."""
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.appointment_date, a.start_time, p.name, a.status, a.appointment_id
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            WHERE a.doctor_id = %s 
              AND a.appointment_date >= CURRENT_DATE
              AND a.status != 'completed'  
            ORDER BY a.appointment_date, a.start_time
        """, (doctor_id,))
        return cursor.fetchall()


def get_completed_appointments(doctor_id):  # For the doctor
    """Fetch completed appointments for the doctor."""
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT a.appointment_date, a.start_time, p.name, a.status, a.appointment_id
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            WHERE a.doctor_id = %s AND a.status = 'completed'
            ORDER BY a.appointment_date DESC
        """, (doctor_id,))
        return cursor.fetchall()
    

    
def add_doctor(name, dob, gender, address, email, password, dept_id):
    try:
        # Database logic to add doctor
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First, create a user entry
        cursor.execute("INSERT INTO users (email, password, role_id) VALUES (%s, %s, %s) RETURNING user_id",
                       (email, password, 2))  # role_id 2 for doctors
        user_id = cursor.fetchone()[0]  # Fetch the generated user_id
        
        # Now, insert the doctor record
        cursor.execute("INSERT INTO doctors (name, dob, gender, address, user_id, dept_id) VALUES (%s, %s, %s, %s, %s, %s)",
                       (name, dob, gender, address, user_id, dept_id))
        conn.commit()
        return True, "Doctor added successfully."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    
def remove_doctor(doctor_id):
    try:
        # Get the user_id associated with the doctor
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch the user_id for the given doctor_id
        cursor.execute("SELECT user_id FROM doctors WHERE doctor_id = %s", (doctor_id,))
        user_id = cursor.fetchone()

        if user_id:
            user_id = user_id[0]  # Extract the user_id from the result

            # Remove the doctor
            cursor.execute("DELETE FROM doctors WHERE doctor_id = %s", (doctor_id,))
            # Remove the corresponding user
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    
            conn.commit()
            return True, "Doctor and corresponding user removed successfully."
        else:
            return False, "Doctor not found."

    except Exception as e:
        conn.rollback()
        return False, str(e)
    
def get_departments():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT dept_id, department_name FROM departments")
        
        return cursor.fetchall()  # This will return a list of tuples (department_id, department_name)

    except Exception as e:
        print(f"An error occurred while fetching departments: {e}")
        return []  # Return an empty list in case of error

    finally:
        conn.close()  # Ensure the connection is closed
        
def view_departments_and_doctors():
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = '''
        SELECT departments.department_name, doctors.name, users.email
        FROM departments
        JOIN doctors ON departments.dept_id = doctors.dept_id
        JOIN users ON doctors.user_id = users.user_id
        ORDER BY departments.department_name;
        '''
        
        cursor.execute(query)
        result = cursor.fetchall()
        
        return result
        
        
    except Exception as e:
        print(f"error encountered : {e}")
        
    finally:
        if conn:
            cursor.close()
            conn.close()
            
def search_doctor_by_email(email):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = '''
        SELECT doctors.doctor_id, doctors.name, doctors.dob, doctors.gender, doctors.address,
               users.email, departments.department_name
        FROM doctors
        JOIN users ON doctors.user_id = users.user_id
        LEFT JOIN departments ON doctors.dept_id = departments.dept_id
        WHERE users.email = %s;
        '''
        cursor.execute(query, (email,))
        doctor_info = cursor.fetchone()

        if doctor_info:
            # Fetch appointments for the doctor
            doctor_id = doctor_info[0]
            query_appointments = '''
            SELECT appointment_id, appointment_date, start_time, status
            FROM appointments
            WHERE doctor_id = %s AND appointment_date >= CURRENT_DATE AND status = 'booked' 
            ORDER BY appointment_date, start_time;
            '''
            cursor.execute(query_appointments, (doctor_id,))
            appointments = cursor.fetchall()
            return doctor_info, appointments
        else:
            return None, None

    except Exception as e:
        print("Error while searching for doctor by email:", e)
        return None, None
    finally:
        cursor.close()
        conn.close()
        
def cancel_appointment(appointment_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        update_query = '''
        UPDATE appointments
        SET status = 'Canceled'
        WHERE appointment_id = %s;
        '''
        cursor.execute(update_query, (appointment_id,))
        conn.commit()
        
        # Fetch the details of the appointment
        cursor.execute("SELECT doctor_id, appointment_date, start_time FROM appointments WHERE appointment_id = %s", (appointment_id,))
        appointment = cursor.fetchone()

        if appointment:  # Check if an appointment was found
            doctor_id, appointment_date, start_time = appointment
            
            # Update the slot_status in the availability table
            cursor.execute("UPDATE availability SET slot_status = 'unavailable' WHERE doctor_id = %s AND available_date = %s AND start_time = %s",
                           (doctor_id, appointment_date, start_time))
            conn.commit()  # Commit the changes
            print("Appointment status updated.")  # Debug
        
        
        return True, "Appointment status updated to 'Canceled'."

    except Exception as e:
        print("Error while cancelling appointment:", e)
        return False, "Error occurred while cancelling the appointment."
    finally:
        cursor.close()
        conn.close()
        
def add_availability(doctor_id, available_date, start_time, end_time):  
    """Add a new availability slot for the doctor."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check for existing availability for the same doctor, date, and start time
        cursor.execute("""
            SELECT COUNT(*) FROM availability
            WHERE doctor_id = %s AND available_date = %s AND start_time = %s
        """, (doctor_id, available_date, start_time))
        
        count = cursor.fetchone()[0]
        
        if count > 0:
            return False, "Availability slot already exists for this doctor on the selected date and time."

        # If no existing slot, proceed to insert
        cursor.execute("""
            INSERT INTO availability (doctor_id, available_date, start_time, end_time, slot_status)
            VALUES (%s, %s, %s, %s, %s)
        """, (doctor_id, available_date, start_time, end_time, 'available'))
        
        connection.commit()
        return True, "Availability added successfully."
        
    except Exception as e:
        return False, f"Error adding availability: {str(e)}"
        
    finally:
        if connection:
            cursor.close()
            connection.close()
            
def remove_booked_availability(doctor_id, available_date, start_time):
    """Remove booked availability and the corresponding appointment."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if the availability exists and is booked
        cursor.execute("""
            SELECT availability_id FROM availability
            WHERE doctor_id = %s AND available_date = %s AND start_time = %s AND slot_status = 'available'
        """, (doctor_id, available_date, start_time))
        
        availability_record = cursor.fetchone()

        if not availability_record:
            return False, "No booked availability found for the given details."
        
        availability_id = availability_record[0]
        
        # Delete corresponding appointment (assuming appointments table has availability_id as reference)
        cursor.execute("""
            DELETE FROM appointments 
            WHERE doctor_id = %s AND appointment_date = %s AND start_time = %s
        """, (doctor_id, available_date, start_time))
        
        # Delete availability
        cursor.execute("""
            DELETE FROM availability
            WHERE availability_id = %s
        """, (availability_id,))
        
        # Commit the transaction
        connection.commit()
        return True, "Booked availability and corresponding appointment removed successfully."

    except Exception as e:
        return False, f"Error removing availability and appointment: {str(e)}"
    
    finally:
        if connection:
            cursor.close()
            connection.close()
 



    
        

    

    

    



    

    
