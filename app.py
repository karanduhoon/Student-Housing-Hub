
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from db_connection import DatabaseConnection
import re  # Importing the regex module for validation

# Base Screen Class
class Screen:
    def __init__(self, root):
        self.root = root

    def display(self):
        raise NotImplementedError("Subclasses must implement the 'display' method.")


# Notification Manager (Observer Pattern)
class NotificationManager:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, user_id, callback):
        if user_id not in self.subscribers:
            self.subscribers[user_id] = []
        self.subscribers[user_id].append(callback)

    def notify(self, user_id, message):
        db = DatabaseConnection()
        db.query("INSERT INTO notifications (user_id, message) VALUES (?, ?)", (user_id, message))
        if user_id in self.subscribers:
            for callback in self.subscribers[user_id]:
                callback(message)


notification_manager = NotificationManager()

# Welcome Screen
class WelcomeScreen(Screen):
    def display(self):
        self.clear_screen()
        tk.Label(self.root, text="Welcome to Housing Management App", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Login", width=20, command=self.show_login_screen).pack(pady=5)
        tk.Button(self.root, text="Register", width=20, command=self.show_register_screen).pack(pady=5)
        tk.Button(self.root, text="Exit", width=20, command=self.root.quit).pack(pady=5)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_screen(self):
        LoginScreen(self.root).display()

    def show_register_screen(self):
        RegisterScreen(self.root).display()

# Login Screen
class LoginScreen(Screen):
    def display(self):
        self.clear_screen()
        tk.Label(self.root, text="Login", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.root, text="Username:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        tk.Button(self.root, text="Login", command=self.login).pack(pady=10)
        tk.Button(self.root, text="Back", command=lambda: WelcomeScreen(self.root).display()).pack()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        db = DatabaseConnection()
        user = db.fetch("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        if user:
            role = user[0][4]
            if role == "student":
                StudentDashboard(self.root, username).display()
            elif role == "homeowner":
                HomeownerDashboard(self.root, username).display()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials.")

# Validation Functions
def validate_phone(phone):
    return bool(re.match(r"^\d{10}$", phone))

def validate_password(password):
    return len(password) >= 8

def validate_email(email):
    return bool(re.match(r"^[\w._%+-]+@[\w.-]+\.[a-zA-Z]{2,}$", email))




#CHAT BOT 
class ChatBotScreen(Screen):
    def __init__(self, root, username):
        self.root = root
        self.username = username

    def display(self):
        self.clear_screen()
        tk.Label(self.root, text="Chatbot", font=("Arial", 16)).pack(pady=10)

        self.chat_log = tk.Text(self.root, height=15, width=50, state="disabled")
        self.chat_log.pack(pady=10)

        self.user_input = tk.Entry(self.root, width=50)
        self.user_input.pack(pady=5)
        self.user_input.bind("<Return>", self.process_input)

        tk.Button(self.root, text="Send", command=self.process_input).pack(pady=5)
        tk.Button(self.root, text="Return", command=self.return_to_previous_screen).pack(pady=5)  

        # Display options
        self.display_options()

    def display_options(self):
        options = "Select an option:\n1. Properties\n2. Events\n3. Carpools\n4. Roommates"
        self.display_message(options)

    def process_input(self, event=None):
        user_message = self.user_input.get().strip()
        if user_message:
            self.user_input.delete(0, tk.END)
            self.handle_selection(user_message)

    def handle_selection(self, selection):
        if selection == "1":
            properties = self.fetch_properties()  # Fetch properties from the database
            if properties:
                self.display_message("Available Properties:\n" + "\n".join(properties))
            else:
                self.display_message("No properties posted now.")
        elif selection == "2":
            events = self.fetch_events()  # Fetch events from the database
            if events:
                self.display_message("Upcoming Events:\n" + "\n".join(events))
            else:
                self.display_message("No events posted now.")
        elif selection == "3":
            carpools = self.fetch_carpools()  # Fetch carpools from the database
            if carpools:
                self.display_message("Available Carpools:\n" + "\n".join(carpools))
            else:
                self.display_message("No carpools posted now.")
        elif selection == "4":
            roommates = self.fetch_roommates()  # Fetch available students from the database
            if roommates:
                self.display_message("Available Students:\n" + "\n".join(roommates))
            else:
                self.display_message("No available students at the moment.")
        else:
            self.display_message("Invalid selection. Please choose a valid option.")

    def display_message(self, message):
        self.chat_log.config(state="normal")
        self.chat_log.insert(tk.END, message + "\n")
        self.chat_log.config(state="disabled")
        self.chat_log.see(tk.END)

    def return_to_previous_screen(self):
        # to return to the appropriate dashboard based on user role
        db = DatabaseConnection()
        user = db.fetch("SELECT role FROM users WHERE username = ?", (self.username,))  # Fetch user role
        if user:
            role = user[0][0]
            if role == "student":
                StudentDashboard(self.root, self.username).display()  # Return to Student Dashboard
            elif role == "homeowner":
                HomeownerDashboard(self.root, self.username).display()  # Return to Homeowner Dashboard

    def fetch_properties(self):
        # Logic to fetch properties from the database
        db = DatabaseConnection()
        properties = db.fetch("SELECT address FROM properties WHERE visible = 1")  # Example query
        return [property[0] for property in properties]  # Return a list of property addresses

    def fetch_carpools(self):
        # Logic to fetch carpools from the database
        db = DatabaseConnection()
        carpools = db.fetch("SELECT start_point, destination FROM carpools WHERE seats > 0")  # Example query
        return [f"{carpool[0]} to {carpool[1]}" for carpool in carpools]  # Return formatted carpool info

    def fetch_events(self):
        # Logic to fetch events from the database
        db = DatabaseConnection()
        events = db.fetch("SELECT name, date, time FROM community_events WHERE date >= DATE('now')")  # Example query
        return [f"{event[0]} on {event[1]} at {event[2]}" for event in events]  # Return formatted event info

    def fetch_roommates(self):
        # Logic to fetch available students who are not currently tenants
        db = DatabaseConnection()
        available_students = db.fetch("""
            SELECT username 
            FROM users 
            WHERE role = 'student' 
            AND user_id NOT IN (
                SELECT tenant_id 
                FROM leases 
                WHERE status = 'active'
            )
        """)  # Example query to fetch available students
        return [student[0] for student in available_students]  # Return a list of available student usernames

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()




# Register Screen
class RegisterScreen(Screen):
    def display(self):
        self.clear_screen()
        tk.Label(self.root, text="Register", font=("Arial", 16)).pack(pady=10)

        # Username field
        tk.Label(self.root, text="Username:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()

        # Password field
        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()

        # Email field
        tk.Label(self.root, text="Email:").pack()
        self.email_entry = tk.Entry(self.root)
        self.email_entry.pack()

        # Phone number field
        tk.Label(self.root, text="Phone Number:").pack()
        self.phone_entry = tk.Entry(self.root)
        self.phone_entry.pack()

        # Role selection with radio buttons
        tk.Label(self.root, text="Role:").pack()
        self.role_var = tk.StringVar(value="student")  # Default value
        tk.Radiobutton(self.root, text="Student", variable=self.role_var, value="student").pack(anchor=tk.W)
        tk.Radiobutton(self.root, text="Homeowner", variable=self.role_var, value="homeowner").pack(anchor=tk.W)

        # Register and Back buttons
        tk.Button(self.root, text="Register", command=self.register).pack(pady=10)
        tk.Button(self.root, text="Back", command=lambda: WelcomeScreen(self.root).display()).pack()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        role = self.role_var.get()

        # Basic field checks
        if not username or not password or not email or not phone:
            messagebox.showerror("Error", "All fields are mandatory.")
            return

        # Validate inputs
        if not validate_phone(phone):
            messagebox.showerror("Error", "Phone number must be exactly 10 digits.")
            return
        if not validate_password(password):
            messagebox.showerror("Error", "Password must be at least 8 characters long.")
            return
        if not validate_email(email):
            messagebox.showerror("Error", "Invalid email address format.")
            return

        # Database insertion
        db = DatabaseConnection()
        try:
            db.query(
                "INSERT INTO users (username, password, email, phone_number, role) VALUES (?, ?, ?, ?, ?)",
                (username, password, email, phone, role),
            )
            messagebox.showinfo("Success", "Registered successfully!")
            WelcomeScreen(self.root).display()
        except Exception as e:
            messagebox.showerror("Error", f"Registration failed: {e}")



# Homeowner Dashboard
class HomeownerDashboard(Screen):
    def __init__(self, root, username):
        self.root = root
        self.username = username
        
        
        
    def add_tenant_to_lease(self, property_id):
        self.clear_screen()
        tk.Label(self.root, text="Add Tenant to Lease", font=("Arial", 16)).pack(pady=10)

        db = DatabaseConnection()

        # Calculate rooms available dynamically
        rooms_available = db.fetch("""
            SELECT bedrooms - (
                SELECT COUNT(*) 
                FROM leases 
                WHERE property_id = ?
            ) AS rooms_available
            FROM properties
            WHERE property_id = ?
        """, (property_id, property_id))

        if not rooms_available or rooms_available[0][0] <= 0:
            messagebox.showerror("Error", "No rooms available for this property.")
            self.view_properties()
            return

        # Fetch students who have scheduled visits for this property
        students = db.fetch("""
            SELECT DISTINCT u.user_id, u.username
            FROM property_visits pv
            JOIN users u ON pv.student_id = u.user_id
            WHERE pv.property_id = ? AND pv.status = 'accepted'
        """, (property_id,))

        if not students:
            tk.Label(self.root, text="No students have scheduled visits for this property.").pack()
            tk.Button(self.root, text="Back", command=self.display).pack()
            return

        # Create dropdown for selecting a student
        tk.Label(self.root, text="Select Tenant:").pack()
        tenant_var = tk.StringVar(value="Select a student")
        student_dropdown = tk.OptionMenu(self.root, tenant_var, *[f"{s[1]} (ID: {s[0]})" for s in students])
        student_dropdown.pack()

        tk.Label(self.root, text="Start Date (YYYY-MM-DD):").pack()
        start_date_entry = tk.Entry(self.root)
        start_date_entry.pack()

        tk.Label(self.root, text="End Date (YYYY-MM-DD):").pack()
        end_date_entry = tk.Entry(self.root)
        end_date_entry.pack()

        tk.Label(self.root, text="Rent Amount:").pack()
        rent_entry = tk.Entry(self.root)
        rent_entry.pack()

        def submit_lease():
            selected_student = tenant_var.get()
            if selected_student == "Select a student":
                messagebox.showerror("Error", "Please select a student.")
                return

            tenant_id = int(selected_student.split("ID: ")[1].rstrip(")"))
            start_date = start_date_entry.get().strip()
            end_date = end_date_entry.get().strip()
            rent_amount = rent_entry.get().strip()

            if not start_date or not end_date or not rent_amount:
                messagebox.showerror("Error", "All fields are mandatory.")
                return

            # Insert lease details into the database
            db.query("""
                INSERT INTO leases (property_id, tenant_id, start_date, end_date, rent_amount)
                VALUES (?, ?, ?, ?, ?)
            """, (property_id, tenant_id, start_date, end_date, float(rent_amount)))

            # Dynamically update property visibility
            db.query("""
                UPDATE properties
                SET visible = CASE 
                    WHEN bedrooms - (
                        SELECT COUNT(*) 
                        FROM leases 
                        WHERE leases.property_id = properties.property_id
                    ) > 0 THEN 1 
                    ELSE 0 
                END
                WHERE property_id = ?
            """, (property_id,))

            # Notify the homeowner about the update
            homeowner_id = db.fetch("SELECT homeowner_id FROM properties WHERE property_id = ?", (property_id,))[0][0]
            notification_manager.notify(homeowner_id, f"Property {property_id} visibility updated after adding a tenant.")

            messagebox.showinfo("Success", "Tenant added to lease.")
            self.view_properties()

        tk.Button(self.root, text="Submit", command=submit_lease).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.display).pack()


    def select_property_for_lease(self):
        self.clear_screen()
        tk.Label(self.root, text="Select a Property for Lease", font=("Arial", 16)).pack(pady=10)

        db = DatabaseConnection()
        homeowner_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]
        properties = db.fetch("""
            SELECT property_id, address
            FROM properties
            WHERE homeowner_id = ?
        """, (homeowner_id,))

        if properties:
            for property in properties:
                tk.Button(self.root, text=property[1], command=lambda p=property[0]: self.add_tenant_to_lease(p)).pack(pady=5)
        else:
            tk.Label(self.root, text="No properties available for lease.").pack()

        tk.Button(self.root, text="Back", command=self.display).pack()




    def display(self):
        """Display the Homeowner Dashboard."""
        self.clear_screen()
        tk.Label(self.root, text="Homeowner Dashboard", font=("Arial", 16)).pack(pady=10)

        # Buttons for Homeowner Dashboard
        tk.Button(self.root, text="Upcoming Visits", width=20, command=self.view_upcoming_visits).pack(pady=5)
        tk.Button(self.root, text="Post Property", width=20, command=self.post_property).pack(pady=5)
        tk.Button(self.root, text="Manage Listings", width=20, command=self.manage_listings).pack(pady=5)
        tk.Button(self.root, text="View Visit Requests", width=20, command=self.view_visit_requests).pack(pady=5)
        tk.Button(self.root, text="Add Tenant to Lease", width=20, command=self.select_property_for_lease).pack(pady=5)
        tk.Button(self.root, text="My Properties", width=20, command=self.view_properties).pack(pady=5)
        tk.Button(self.root, text="Logout", width=20, command=lambda: WelcomeScreen(self.root).display()).pack(pady=5)
        

    def view_upcoming_visits(self):
        """View upcoming visits for the homeowner's properties."""
        self.clear_screen()
        tk.Label(self.root, text="Upcoming Property Visits", font=("Arial", 16)).pack(pady=10)

        db = DatabaseConnection()
        homeowner_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]

        # Fetch upcoming visits
        visits = db.fetch("""
            SELECT pv.visit_id, p.address, u.username AS visitor, pv.visit_type, pv.date, pv.time, pv.status
            FROM property_visits pv
            JOIN properties p ON pv.property_id = p.property_id
            JOIN users u ON pv.student_id = u.user_id
            WHERE p.homeowner_id = ? AND pv.status = 'accepted' AND pv.date >= DATE('now')
            ORDER BY pv.date, pv.time
        """, (homeowner_id,))

        if visits:
            for visit in visits:
                tk.Label(self.root, text=f"Property Address: {visit[1]}").pack()
                tk.Label(self.root, text=f"Visitor: {visit[2]}").pack()
                tk.Label(self.root, text=f"Visit Type: {visit[3].capitalize()}").pack()
                tk.Label(self.root, text=f"Date: {visit[4]}").pack()
                tk.Label(self.root, text=f"Time: {visit[5]}").pack()
                tk.Label(self.root, text=f"Status: {visit[6].capitalize()}").pack()
                tk.Label(self.root, text="").pack()
        else:
            tk.Label(self.root, text="No upcoming visits found.").pack()

        tk.Button(self.root, text="Back", command=self.display).pack()


    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def post_property(self):
        self.clear_screen()
        tk.Label(self.root, text="Post Property", font=("Arial", 16)).pack(pady=10)

        # Input fields
        fields = {
            "Address": tk.Entry(self.root),
            "State": tk.Entry(self.root),
            "City": tk.Entry(self.root),
            "Zipcode": tk.Entry(self.root),
            "Bedrooms": tk.Entry(self.root),
            "Kitchens": tk.Entry(self.root),
            "Bathrooms": tk.Entry(self.root),
            "Description": tk.Text(self.root, height=5, width=40),
        }
        photo_path = tk.StringVar()

        for label, widget in fields.items():
            tk.Label(self.root, text=f"{label}:").pack()
            widget.pack()

        def upload_photo():
            file_path = filedialog.askopenfilename(title="Select Property Photo", filetypes=[("Image Files", "*.jpg;*.png")])
            if file_path:
                photo_path.set(file_path)
                messagebox.showinfo("Photo Uploaded", f"Photo successfully uploaded: {os.path.basename(file_path)}")

        tk.Button(self.root, text="Upload Photo", command=upload_photo).pack(pady=5)

        def submit():
            data = {key: (widget.get("1.0", tk.END).strip() if isinstance(widget, tk.Text) else widget.get().strip()) for key, widget in fields.items()}
            if not data["Address"] or not data["State"] or not data["Bedrooms"] or not data["Kitchens"] or not data["Bathrooms"]:
                messagebox.showerror("Error", "All fields except City and Zipcode are mandatory.")
                return

            db = DatabaseConnection()
            homeowner_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]
            db.query("""
                INSERT INTO properties (homeowner_id, address, state, city, zipcode, bedrooms, kitchens, bathrooms, description, photo_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (homeowner_id, data["Address"], data["State"], data["City"], data["Zipcode"], data["Bedrooms"], data["Kitchens"], data["Bathrooms"], data["Description"], photo_path.get()))
            messagebox.showinfo("Success", "Property posted successfully!")
            self.display()

        tk.Button(self.root, text="Submit", command=submit).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.display).pack()

    def manage_listings(self):
        """Manage property listings."""
        self.clear_screen()
        tk.Label(self.root, text="Manage Listings", font=("Arial", 16)).pack(pady=10)

        db = DatabaseConnection()
        homeowner_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]
        listings = db.fetch("""
            SELECT property_id, address, state, city, zipcode, bedrooms, kitchens, bathrooms, description, photo_path
            FROM properties
            WHERE homeowner_id = ?
        """, (homeowner_id,))

        if listings:
            for listing in listings:
                tk.Label(self.root, text=f"Address: {listing[1]}").pack()
                tk.Label(self.root, text=f"State: {listing[2]}, City: {listing[3]}, Zipcode: {listing[4]}").pack()
                tk.Label(self.root, text=f"Bedrooms: {listing[5]}, Kitchens: {listing[6]}, Bathrooms: {listing[7]}").pack()
                tk.Label(self.root, text=f"Description: {listing[8]}").pack()
                tk.Label(self.root, text=f"Photo: {listing[9]}").pack()

                tk.Button(self.root, text="Edit", command=lambda l=listing: self.edit_property(l)).pack()
                tk.Button(self.root, text="Take Down", command=lambda l=listing: self.take_down_property(l[0])).pack()
                tk.Label(self.root, text="").pack()
        else:
            tk.Label(self.root, text="No listings found.").pack()

        tk.Button(self.root, text="Back", command=self.display).pack()

    def take_down_property(self, property_id):
        db = DatabaseConnection()
        db.query("DELETE FROM properties WHERE property_id = ?", (property_id,))
        messagebox.showinfo("Success", "Property removed.")
        self.manage_listings()

    def edit_property(self, listing):
        """Edit property details."""
        self.clear_screen()
        tk.Label(self.root, text="Edit Property", font=("Arial", 16)).pack(pady=10)

        fields = {
            "Address": tk.Entry(self.root),
            "State": tk.Entry(self.root),
            "City": tk.Entry(self.root),
            "Zipcode": tk.Entry(self.root),
            "Bedrooms": tk.Entry(self.root),
            "Kitchens": tk.Entry(self.root),
            "Bathrooms": tk.Entry(self.root),
            "Description": tk.Text(self.root, height=5, width=40),
        }
        photo_path = tk.StringVar(value=listing[9])  # Pre-fill photo path upcomming feature

        # Populate fields with current property values
        fields["Address"].insert(0, listing[1])
        fields["State"].insert(0, listing[2])
        fields["City"].insert(0, listing[3])
        fields["Zipcode"].insert(0, listing[4])
        fields["Bedrooms"].insert(0, listing[5])
        fields["Kitchens"].insert(0, listing[6])
        fields["Bathrooms"].insert(0, listing[7])
        fields["Description"].insert("1.0", listing[8])

        for label, widget in fields.items():
            tk.Label(self.root, text=f"{label}:").pack()
            widget.pack()

        def upload_photo():
            file_path = filedialog.askopenfilename(title="Select Property Photo", filetypes=[("Image Files", "*.jpg;*.png")])
            if file_path:
                photo_path.set(file_path)
                messagebox.showinfo("Photo Uploaded", f"Photo successfully uploaded: {os.path.basename(file_path)}")

        tk.Button(self.root, text="Upload Photo", command=upload_photo).pack(pady=5)

        def save_changes():
            data = {key: (widget.get("1.0", tk.END).strip() if isinstance(widget, tk.Text) else widget.get().strip()) for key, widget in fields.items()}
            if not data["Address"] or not data["State"] or not data["Bedrooms"] or not data["Kitchens"] or not data["Bathrooms"]:
                messagebox.showerror("Error", "All mandatory fields must be filled.")
                return

            db = DatabaseConnection()
            db.query("""
                UPDATE properties
                SET bedrooms = ?, kitchens = ?, bathrooms = ?, description = ?, photo_path = ?,
                    visible = CASE 
                        WHEN bedrooms - (
                            SELECT COUNT(*) 
                            FROM leases 
                            WHERE leases.property_id = properties.property_id
                        ) > 0 THEN 1 
                        ELSE 0 
                    END
                WHERE property_id = ?
            """, (data["Bedrooms"], data["Kitchens"], data["Bathrooms"], data["Description"], photo_path.get(), listing[0]))

            messagebox.showinfo("Success", "Property updated successfully!")
            self.manage_listings()

        tk.Button(self.root, text="Save Changes", command=save_changes).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.manage_listings).pack()
        
    def view_visit_requests(self):
        self.clear_screen()
        tk.Label(self.root, text="Visit Requests", font=("Arial", 16)).pack(pady=10)

        db = DatabaseConnection()
        homeowner_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]
        requests = db.fetch("""
            SELECT pv.visit_id, p.address, pv.visit_type, pv.date, pv.time, pv.status, pv.note, u.username
            FROM property_visits pv
            JOIN properties p ON pv.property_id = p.property_id
            JOIN users u ON pv.student_id = u.user_id
            WHERE pv.homeowner_id = ?
        """, (homeowner_id,))

        if requests:
            for req in requests:
                tk.Label(self.root, text=f"Property: {req[1]}").pack()
                tk.Label(self.root, text=f"Visit Type: {req[2]}, Date: {req[3]}, Time: {req[4]}").pack()
                tk.Label(self.root, text=f"Status: {req[5]}").pack()
                tk.Label(self.root, text=f"Note: {req[6] if req[6] else 'None'}").pack()
                tk.Label(self.root, text=f"Requested by: {req[7]}").pack()

                if req[5] == "pending":
                    tk.Button(self.root, text="Accept", command=lambda r=req: self.respond_to_request(r[0], "accepted")).pack()
                    tk.Button(self.root, text="Reject", command=lambda r=req: self.respond_to_request(r[0], "rejected")).pack()
                tk.Label(self.root, text="").pack()
        else:
            tk.Label(self.root, text="No visit requests.").pack()

        tk.Button(self.root, text="Back", command=self.display).pack()

    def respond_to_request(self, visit_id, status):
        db = DatabaseConnection()
        db.query("UPDATE property_visits SET status = ? WHERE visit_id = ?", (status, visit_id))

        # Fetch student ID and send notification
        student_id = db.fetch("SELECT student_id FROM property_visits WHERE visit_id = ?", (visit_id,))[0][0]
        if status == "accepted":
            message = "Your visit request has been accepted."
        elif status == "rejected":
            message = "Your visit request has been rejected."
        else:
            message = "Your visit request status has been updated."

        # Notify student
        notification_manager.notify(student_id, message)
        messagebox.showinfo("Success", f"Request {status}.")
        self.view_visit_requests()  
        
    def view_properties(self):
        self.clear_screen()
        tk.Label(self.root, text="My Properties", font=("Arial", 16)).pack(pady=10)

        db = DatabaseConnection()
        homeowner_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]
        properties = db.fetch("""
            SELECT property_id, address, bedrooms - (
                SELECT COUNT(*) 
                FROM leases 
                WHERE leases.property_id = properties.property_id
            ) AS rooms_available, bedrooms
            FROM properties
            WHERE homeowner_id = ?
        """, (homeowner_id,))

        if properties:
            for property in properties:
                tk.Label(self.root, text=f"Address: {property[1]}").pack()
                tk.Label(self.root, text=f"Rooms Available: {property[2]} / {property[3]}").pack()

                tenants = db.fetch("""
                    SELECT u.username, u.email
                    FROM leases l
                    JOIN users u ON l.tenant_id = u.user_id
                    WHERE l.property_id = ?
                """, (property[0],))

                if tenants:
                    tk.Label(self.root, text="Tenants:").pack()
                    for tenant in tenants:
                        tk.Label(self.root, text=f"   Name: {tenant[0]}, Email: {tenant[1]}").pack()
                else:
                    tk.Label(self.root, text="No tenants yet.").pack()

                tk.Button(self.root, text="Manage Maintenance Requests", 
                        command=lambda p=property[0]: self.manage_maintenance_requests(p)).pack(pady=5)
                tk.Label(self.root, text="").pack()
        else:
            tk.Label(self.root, text="No properties found.").pack()

        tk.Button(self.root, text="Back", command=self.display).pack()


#manage_maintenance_requests
    def manage_maintenance_requests(self, property_id):
        self.clear_screen()
        tk.Label(self.root, text="Maintenance Requests", font=("Arial", 16)).pack(pady=10)

        db = DatabaseConnection()
        requests = db.fetch("""
            SELECT request_id, description, location, date, status, resolution_date 
            FROM maintenance_requests 
            WHERE property_id = ?
        """, (property_id,))

        if requests:
            for request in requests:
                tk.Label(self.root, text=f"Issue: {request[1]}").pack()
                tk.Label(self.root, text=f"Location: {request[2] if request[2] else 'Not specified'}").pack()
                tk.Label(self.root, text=f"Date: {request[3]}").pack()
                tk.Label(self.root, text=f"Status: {request[4].capitalize()}").pack()
                if request[4] == "pending":
                    tk.Label(self.root, text="Set Resolution Date:").pack()
                    resolution_date_entry = tk.Entry(self.root)
                    resolution_date_entry.pack()

                    def resolve_request():
                        resolution_date = resolution_date_entry.get().strip()
                        if not resolution_date:
                            messagebox.showerror("Error", "Resolution date is mandatory.")
                            return

                        db.query("""
                            UPDATE maintenance_requests 
                            SET status = 'resolved', resolution_date = ?
                            WHERE request_id = ?
                        """, (resolution_date, request[0]))

                        # Notify all tenants
                        tenant_ids = db.fetch("""
                            SELECT tenant_id 
                            FROM leases 
                            WHERE property_id = ?
                        """, (property_id,))
                        for tenant in tenant_ids:
                            notification_manager.notify(tenant[0], f"Maintenance issue resolved on {resolution_date}.")

                        messagebox.showinfo("Success", "Issue resolved and tenants notified.")
                        self.manage_maintenance_requests(property_id)

                    tk.Button(self.root, text="Resolve", command=resolve_request).pack(pady=5)
                elif request[4] == "resolved":
                    tk.Label(self.root, text=f"Resolved on: {request[5]}").pack()
                tk.Label(self.root, text="").pack()
        else:
            tk.Label(self.root, text="No maintenance requests found.").pack()

        tk.Button(self.root, text="Back", command=self.view_properties).pack()


#STUDNET DASHBOARD
class StudentDashboard(Screen):
    def __init__(self, root, username):
        self.root = root
        self.username = username
        
    def display(self):
        """Display the Student Dashboard."""
        self.clear_screen()
        tk.Label(self.root, text="Student Dashboard", font=("Arial", 16)).pack(pady=10)

        # Add all the buttons
        tk.Button(self.root, text="Chat with Assistant", command=lambda: ChatBotScreen(self.root, self.username).display()).pack(pady=5)
        tk.Button(self.root, text="View My Lease", width=20, command=self.view_my_lease).pack(pady=5)
        tk.Button(self.root, text="Search Properties", width=20, command=self.search_properties).pack(pady=5)
        tk.Button(self.root, text="View Bookmarked Properties", width=20, command=self.view_bookmarked_properties).pack(pady=5)
        tk.Button(self.root, text="View Notifications", width=20, command=self.view_notifications).pack(pady=5)
        tk.Button(self.root, text="Upcoming Visits", width=20, command=self.view_upcoming_visits).pack(pady=5)
        tk.Button(self.root, text="Community Events", width=20, command=self.community_events_menu).pack(pady=5)
        tk.Button(self.root, text="Carpooling", width=20, command=self.carpooling_menu).pack(pady=5)
        tk.Button(self.root, text="Upcoming Carpools", width=20, command=self.view_upcoming_carpools).pack(pady=5)  
        tk.Button(self.root, text="View Roommates", width=20, command=self.view_roommates).pack(pady=5)
        tk.Button(self.root, text="Logout", width=20, command=lambda: WelcomeScreen(self.root).display()).pack(pady=5)
        
    def view_roommates(self):
        self.clear_screen()
        tk.Label(self.root, text="My Roommates", font=("Arial", 16)).pack(pady=10)

        db = DatabaseConnection()
        student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]
        property_id = db.fetch("""
            SELECT property_id
            FROM leases
            WHERE tenant_id = ? AND status = 'active'
        """, (student_id,))
        
        if not property_id:
            tk.Label(self.root, text="You are not currently on any lease.").pack()
            tk.Button(self.root, text="Back", command=self.display).pack()
            return

        roommates = db.fetch("""
            SELECT u.username, u.email
            FROM leases l
            JOIN users u ON l.tenant_id = u.user_id
            WHERE l.property_id = ? AND l.tenant_id != ?
        """, (property_id[0][0], student_id))

        if roommates:
            for roommate in roommates:
                tk.Label(self.root, text=f"Name: {roommate[0]}").pack()
                tk.Label(self.root, text=f"Email: {roommate[1]}").pack()
                tk.Label(self.root, text="").pack()
        else:
            tk.Label(self.root, text="No roommates found.").pack()

        tk.Button(self.root, text="Back", command=self.display).pack()



    def view_my_lease(self):    #view_my_lease
        self.clear_screen()
        tk.Label(self.root, text="My Lease", font=("Arial", 16)).pack(pady=10)

        db = DatabaseConnection()
        student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]
        leases = db.fetch("""
            SELECT l.lease_id, p.address, l.start_date, l.end_date, l.rent_amount, l.status
            FROM leases l
            JOIN properties p ON l.property_id = p.property_id
            WHERE l.tenant_id = ? AND l.status = 'active'
        """, (student_id,))

        if leases:
            for lease in leases:
                tk.Label(self.root, text=f"Property Address: {lease[1]}").pack()
                tk.Label(self.root, text=f"Start Date: {lease[2]}").pack()
                tk.Label(self.root, text=f"End Date: {lease[3]}").pack()
                tk.Label(self.root, text=f"Rent Amount: ${lease[4]:.2f}").pack()
                tk.Label(self.root, text=f"Status: {lease[5].capitalize()}").pack()

                tk.Button(self.root, text="Submit Maintenance Request", 
                        command=self.submit_maintenance_request).pack(pady=5)
                tk.Button(self.root, text="View Maintenance Requests", 
                        command=self.view_maintenance_requests).pack(pady=5)
                tk.Label(self.root, text="").pack()
        else:
            tk.Label(self.root, text="You have no active leases.").pack()

        tk.Button(self.root, text="Back", command=self.display).pack()


    #view_maintenance_requests
    def view_maintenance_requests(self):
        self.clear_screen()
        tk.Label(self.root, text="My Maintenance Requests", font=("Arial", 16)).pack(pady=10)

        db = DatabaseConnection()
        student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]
        requests = db.fetch("""
            SELECT mr.description, mr.location, mr.date, mr.status, mr.resolution_date
            FROM maintenance_requests mr
            JOIN leases l ON mr.property_id = l.property_id
            WHERE l.tenant_id = ? AND l.status = 'active'
        """, (student_id,))

        if requests:
            for request in requests:
                tk.Label(self.root, text=f"Issue: {request[0]}").pack()
                tk.Label(self.root, text=f"Location: {request[1] if request[1] else 'Not specified'}").pack()
                tk.Label(self.root, text=f"Date: {request[2]}").pack()
                tk.Label(self.root, text=f"Status: {request[3].capitalize()}").pack()
                if request[3] == "resolved":
                    tk.Label(self.root, text=f"Resolved on: {request[4]}").pack()
                tk.Label(self.root, text="").pack()
        else:
            tk.Label(self.root, text="No maintenance requests found.").pack()

        tk.Button(self.root, text="Back", command=self.view_my_lease).pack()





#view_upcoming_visits
    def view_upcoming_visits(self):
        """View all upcoming visits for the student."""
        self.clear_screen()
        tk.Label(self.root, text="Upcoming Visits", font=("Arial", 16)).pack(pady=10)

        db = DatabaseConnection()
        student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]

        visits = db.fetch("""
            SELECT pv.visit_type, pv.date, pv.time, p.address
            FROM property_visits pv
            JOIN properties p ON pv.property_id = p.property_id
            WHERE pv.student_id = ? AND pv.status = 'accepted'
            ORDER BY pv.date, pv.time
        """, (student_id,))

        if visits:
            for idx, visit in enumerate(visits, start=1):
                tk.Label(self.root, text=f"Visit #{idx}").pack()
                tk.Label(self.root, text=f"   Type: {visit[0]}").pack()
                tk.Label(self.root, text=f"   Date: {visit[1]}").pack()
                tk.Label(self.root, text=f"   Time: {visit[2]}").pack()
                tk.Label(self.root, text=f"   Address: {visit[3]}").pack()
                tk.Label(self.root, text="").pack()
        else:
            tk.Label(self.root, text="No upcoming visits found.").pack()

        tk.Button(self.root, text="Back", command=self.display).pack()


    #community_events_menu
    def community_events_menu(self):
        """Community Events main menu."""
        self.clear_screen()
        tk.Label(self.root, text="Community Events", font=("Arial", 16)).pack(pady=10)

        tk.Button(self.root, text="View Available Events", width=20, command=self.view_available_events).pack(pady=5)
        tk.Button(self.root, text="Post an Event", width=20, command=self.post_event).pack(pady=5)
        tk.Button(self.root, text="Manage Events", width=20, command=self.manage_events).pack(pady=5)
        tk.Button(self.root, text="Manage Requests", width=20, command=self.manage_event_requests).pack(pady=5)  # New option
        tk.Button(self.root, text="View Upcoming Events", width=20, command=self.view_upcoming_events).pack(pady=5)  # New button for upcoming events
        tk.Button(self.root, text="Back", width=20, command=self.display).pack(pady=5)


    def post_event(self):
        """Allow the user to post a new event."""
        self.clear_screen()
        tk.Label(self.root, text="Post a Community Event", font=("Arial", 16)).pack(pady=10)

        # Input fields for event details
        fields = {
            "Name": tk.Entry(self.root),
            "Location": tk.Entry(self.root),
            "Date (YYYY-MM-DD)": tk.Entry(self.root),
            "Time": tk.Entry(self.root),  # Corrected key to match the logic
            "Max Participants": tk.Entry(self.root),
            "Description": tk.Text(self.root, height=5, width=40),
        }
        event_type_var = tk.StringVar(value="social")  # Default event type

        for label, widget in fields.items():
            tk.Label(self.root, text=f"{label}:").pack()
            widget.pack()

        tk.Label(self.root, text="Event Type:").pack()
        for event_type in ["social", "academic", "sports", "potluck", "other"]:
            tk.Radiobutton(self.root, text=event_type.capitalize(), variable=event_type_var, value=event_type).pack(anchor=tk.W)

        def submit_event():
            """Submit the new event to the database."""
            data = {key: (widget.get("1.0", tk.END).strip() if isinstance(widget, tk.Text) else widget.get().strip()) for key, widget in fields.items()}
            if not data["Name"] or not data["Location"] or not data["Date (YYYY-MM-DD)"] or not data["Time"] or not data["Max Participants"]:
                messagebox.showerror("Error", "All fields except Description are mandatory.")
                return

            db = DatabaseConnection()
            student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]
            db.query("""
                INSERT INTO community_events (organizer_id, name, location, date, time, max_participants, description, event_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (student_id, data["Name"], data["Location"], data["Date (YYYY-MM-DD)"], data["Time"], data["Max Participants"], data["Description"], event_type_var.get()))
            messagebox.showinfo("Success", "Event posted successfully!")
            self.community_events_menu()

        tk.Button(self.root, text="Submit", command=submit_event).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.community_events_menu).pack()

    
    
    def create_event(self):
        """Create a new community event."""
        self.clear_screen()
        tk.Label(self.root, text="Create Event", font=("Arial", 16)).pack(pady=10)

        # Define input fields
        fields = {
            "Name": tk.Entry(self.root),
            "Location": tk.Entry(self.root),
            "Date (YYYY-MM-DD)": tk.Entry(self.root),
            "Time": tk.Entry(self.root),
            "Max Participants": tk.Entry(self.root),
            "Description": tk.Text(self.root, height=5, width=40),
        }

        # Create input widgets for each field
        for label, widget in fields.items():
            tk.Label(self.root, text=f"{label}:").pack()
            widget.pack()

        # Radio buttons for event type
        event_type_var = tk.StringVar(value="social")
        tk.Label(self.root, text="Event Type:").pack()
        event_types = ["Social", "Academic", "Sports", "Potluck", "Other"]
        for event_type in event_types:
            tk.Radiobutton(self.root, text=event_type, variable=event_type_var, value=event_type.lower()).pack()

        def submit():
            # Collect data from input fields
            data = {
                key: (widget.get("1.0", tk.END).strip() if isinstance(widget, tk.Text) else widget.get().strip())
                for key, widget in fields.items()
            }

            # Validate required fields
            if not data["Name"] or not data["Location"] or not data["Date (YYYY-MM-DD)"] or not data["Time"] or not data["Max Participants"]:
                messagebox.showerror("Error", "All fields except Description are mandatory.")
                return

            # Insert event into database
            db = DatabaseConnection()
            student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]
            db.query("""
                INSERT INTO community_events (organizer_id, name, location, date, time, max_participants, description, event_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (student_id, data["Name"], data["Location"], data["Date (YYYY-MM-DD)"], data["Time"], data["Max Participants"], data["Description"], event_type_var.get()))
            messagebox.showinfo("Success", "Event created successfully!")
            self.community_events_menu()

        # Add Submit and Back buttons
        tk.Button(self.root, text="Submit", command=submit).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.community_events_menu).pack()
        
    def view_available_events(self):
        """Display a list of all available events."""
        self.clear_screen()
        tk.Label(self.root, text="Available Events", font=("Arial", 16)).pack(pady=10)

        db = DatabaseConnection()
        student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]

        # Fetch all events that have space left for participants and exclude events organized by the student
        events = db.fetch("""
            SELECT e.event_id, e.name, e.location, e.date, e.time, e.max_participants, 
                SUM(CASE WHEN ep.status = 'accepted' THEN 1 ELSE 0 END) AS current_participants,
                e.description, e.event_type, e.organizer_id
            FROM community_events e
            LEFT JOIN event_participants ep ON e.event_id = ep.event_id
            GROUP BY e.event_id, e.name, e.location, e.date, e.time, e.max_participants, e.description, e.event_type, e.organizer_id
            HAVING current_participants < e.max_participants AND e.organizer_id != ?
        """, (student_id,))

        if events:
            for event in events:
                tk.Label(self.root, text=f"Event Name: {event[1]}").pack()
                tk.Label(self.root, text=f"Location: {event[2]}").pack()
                tk.Label(self.root, text=f"Date: {event[3]} Time: {event[4]}").pack()
                tk.Label(self.root, text=f"Max Participants: {event[5]}").pack()
                tk.Label(self.root, text=f"Current Participants: {event[6]}").pack()
                tk.Label(self.root, text=f"Description: {event[7]}").pack()
                tk.Label(self.root, text=f"Event Type: {event[8].capitalize()}").pack()

                # Exclude the organizer from seeing the "Request to Join" button
                if event[9] != student_id:
                    response = db.fetch("""
                        SELECT status FROM event_participants
                        WHERE event_id = ? AND student_id = ?
                    """, (event[0], student_id))

                    if response:
                        status = response[0][0]
                        if status == "pending":
                            tk.Button(self.root, text="Pending", state=tk.DISABLED).pack()
                        elif status == "accepted":
                            tk.Button(self.root, text="Accepted", state=tk.DISABLED).pack()
                        elif status == "rejected":
                            tk.Button(self.root, text="Rejected", state=tk.DISABLED).pack()
                    else:
                        tk.Button(self.root, text="Request to Join", command=lambda e=event: self.request_to_join_event(e)).pack()

                tk.Label(self.root, text="").pack()
        else:
            tk.Label(self.root, text="No available events.").pack()

        tk.Button(self.root, text="Back", command=self.community_events_menu).pack()

    
    def request_to_join_event(self, event):
        """Send a request to join an event."""
        db = DatabaseConnection()
        student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]

        # Insert request into event_participants table with 'pending' status
        db.query("""
            INSERT INTO event_participants (event_id, student_id, status)
            VALUES (?, ?, 'pending')
        """, (event[0], student_id))
        messagebox.showinfo("Success", f"Request sent for event: {event[1]}")
        self.view_available_events()  # Refresh the event list


    

        #to display_event_results
    def display_event_results(self, events):
        self.clear_screen()
        tk.Label(self.root, text="Event Results", font=("Arial", 16)).pack(pady=10)

        if events:
            for event in events:
                tk.Label(self.root, text=f"Name: {event[1]}").pack()
                tk.Label(self.root, text=f"Location: {event[2]}").pack()
                tk.Label(self.root, text=f"Date: {event[3]}, Time: {event[4]}").pack()
                tk.Label(self.root, text=f"Participants: {event[6]}/{event[5]}").pack()
                tk.Label(self.root, text=f"Description: {event[7]}").pack()
                tk.Button(self.root, text="Join", command=lambda e=event: self.join_event(e)).pack()
                tk.Label(self.root, text="").pack()
        else:
            tk.Label(self.root, text="No events found.").pack()

        tk.Button(self.root, text="Back", command=self.search_events).pack()
        
    def manage_event_requests(self):
        """View and manage requests for events organized by the user."""
        self.clear_screen()
        tk.Label(self.root, text="Manage Event Requests", font=("Arial", 16)).pack(pady=10)

        db = DatabaseConnection()
        organizer_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]

        # Fetch all requests for events organized by the user
        requests = db.fetch("""
            SELECT ep.participant_id, ep.event_id, ep.student_id, ep.status, e.name, u.username
            FROM event_participants ep
            JOIN community_events e ON ep.event_id = e.event_id
            JOIN users u ON ep.student_id = u.user_id
            WHERE e.organizer_id = ?
        """, (organizer_id,))

        if requests:
            for request in requests:
                tk.Label(self.root, text=f"Event: {request[4]}").pack()
                tk.Label(self.root, text=f"Requested by: {request[5]}").pack()
                tk.Label(self.root, text=f"Status: {request[3]}").pack()

                if request[3] == "pending":
                    tk.Button(self.root, text="Accept", command=lambda r=request: self.accept_event_request(r)).pack()
                    tk.Button(self.root, text="Reject", command=lambda r=request: self.reject_event_request(r)).pack()
                tk.Label(self.root, text="").pack()
        else:
            tk.Label(self.root, text="No requests found.").pack()

        tk.Button(self.root, text="Back", command=self.community_events_menu).pack()

        
    def accept_event_request(self, request):
        """Accept a request to join an event."""
        db = DatabaseConnection()
        db.query("UPDATE event_participants SET status = 'accepted' WHERE participant_id = ?", (request[0],))
        
        # Notify the student
        db.query("""
            INSERT INTO notifications (user_id, message)
            VALUES (?, ?)
        """, (request[2], f"Your request to join the event '{request[4]}' has been accepted."))
        messagebox.showinfo("Success", f"Request accepted for {request[5]}.")
        self.manage_event_requests()

        
    def reject_event_request(self, request):
        """Reject a request to join an event."""
        db = DatabaseConnection()
        db.query("UPDATE event_participants SET status = 'rejected' WHERE participant_id = ?", (request[0],))
        
        # Notify the student
        db.query("""
            INSERT INTO notifications (user_id, message)
            VALUES (?, ?)
        """, (request[2], f"Your request to join the event '{request[4]}' has been rejected."))
        messagebox.showinfo("Success", f"Request rejected for {request[5]}.")
        self.manage_event_requests()



    def submit_maintenance_request(self):
        self.clear_screen()
        tk.Label(self.root, text="Submit Maintenance Request", font=("Arial", 16)).pack(pady=10)

        # Maintenance request fields
        tk.Label(self.root, text="Description of the Issue:").pack()
        description_entry = tk.Entry(self.root, width=40)
        description_entry.pack()

        tk.Label(self.root, text="Location of the Issue (Optional):").pack()
        location_entry = tk.Entry(self.root, width=40)
        location_entry.pack()

        tk.Label(self.root, text="Date (YYYY-MM-DD):").pack()
        date_entry = tk.Entry(self.root)
        date_entry.pack()

        def submit_request():
            description = description_entry.get().strip()
            location = location_entry.get().strip()
            date = date_entry.get().strip()

            if not description or not date:
                messagebox.showerror("Error", "Description and Date are mandatory.")
                return

            db = DatabaseConnection()
            student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]
            property_id = db.fetch("""
                SELECT property_id 
                FROM leases 
                WHERE tenant_id = ? AND status = 'active'
            """, (student_id,))[0][0]

            # Insert maintenance request into the database
            db.query("""
                INSERT INTO maintenance_requests (property_id, tenant_id, description, location, date, status) 
                VALUES (?, ?, ?, ?, ?, 'pending')
            """, (property_id, student_id, description, location, date))

            # Notify the homeowner and other tenants
            homeowner_id = db.fetch("SELECT homeowner_id FROM properties WHERE property_id = ?", (property_id,))[0][0]
            notification_manager.notify(homeowner_id, f"New maintenance request from Tenant {self.username}: {description} (Date: {date}).")

            tenant_ids = db.fetch("""
                SELECT tenant_id 
                FROM leases 
                WHERE property_id = ?
            """, (property_id,))
            for tenant in tenant_ids:
                if tenant[0] != student_id:  # Avoid notifying the requester
                    notification_manager.notify(tenant[0], f"A new maintenance request was submitted: {description}.")

            messagebox.showinfo("Success", "Maintenance request submitted and notifications sent.")
            self.view_my_lease()

        tk.Button(self.root, text="Submit", command=submit_request).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.view_my_lease).pack()


    def respond_to_request(self, request, status):
        """Respond to a student's request for an event."""
        db = DatabaseConnection()
        db.query("UPDATE event_responses SET status = ? WHERE response_id = ?", (status, request[0]))

        # Notify the student
        student_id = db.fetch("SELECT student_id FROM event_responses WHERE response_id = ?", (request[0],))[0][0]
        notification = f"Your request for the event has been {status}."
        db.query("INSERT INTO notifications (user_id, message) VALUES (?, ?)", (student_id, notification))

        messagebox.showinfo("Success", f"Request {status.capitalize()}.")
        self.manage_event_requests(request)


#  to edit_event

    def edit_event(self, event):
        """Edit an existing event."""
        self.clear_screen()
        tk.Label(self.root, text="Edit Event", font=("Arial", 16)).pack(pady=10)

        # Define input fields
        fields = {
            "Name": tk.Entry(self.root),
            "Location": tk.Entry(self.root),
            "Date (YYYY-MM-DD)": tk.Entry(self.root),
            "Time": tk.Entry(self.root),
            "Max Participants": tk.Entry(self.root),
            "Description": tk.Text(self.root, height=5, width=40),
        }

        # Pre-fill fields with current event data
        fields["Name"].insert(0, event[1])  # Name
        fields["Location"].insert(0, event[2])  # Location
        fields["Date (YYYY-MM-DD)"].insert(0, event[3])  # Date
        fields["Time"].insert(0, event[4])  # Time
        fields["Max Participants"].insert(0, event[5])  # Max Participants
        fields["Description"].insert("1.0", event[6])  # Description

        for label, widget in fields.items():
            tk.Label(self.root, text=f"{label}:").pack()
            widget.pack()

        # Radio buttons for event type
        event_type_var = tk.StringVar(value=event[7].lower())  # Pre-fill with the current event type
        tk.Label(self.root, text="Event Type:").pack()
        event_types = ["Social", "Academic", "Sports", "Potluck", "Other"]
        for event_type in event_types:
            tk.Radiobutton(self.root, text=event_type, variable=event_type_var, value=event_type.lower()).pack()

        def save_changes():
            # Collect updated data from input fields
            updated_data = {
                key: (widget.get("1.0", tk.END).strip() if isinstance(widget, tk.Text) else widget.get().strip())
                for key, widget in fields.items()
            }

            # Validate required fields
            if not updated_data["Name"] or not updated_data["Location"] or not updated_data["Date (YYYY-MM-DD)"] or not updated_data["Time"] or not updated_data["Max Participants"]:
                messagebox.showerror("Error", "All fields except Description are mandatory.")
                return

            # Update the event in the database
            db = DatabaseConnection()
            db.query("""
                UPDATE community_events
                SET name = ?, location = ?, date = ?, time = ?, max_participants = ?, description = ?, event_type = ?
                WHERE event_id = ?
            """, (updated_data["Name"], updated_data["Location"], updated_data["Date (YYYY-MM-DD)"], updated_data["Time"], updated_data["Max Participants"], updated_data["Description"], event_type_var.get(), event[0]))

            # Notify participants about the update
            participants = db.fetch("""
                SELECT participant_id FROM event_participants WHERE event_id = ?
            """, (event[0],))
            for participant in participants:
                notification_manager.notify(participant[0], f"The event '{event[1]}' has been updated.")

            messagebox.showinfo("Success", "Event updated successfully!")
            self.manage_events()

        # Add Save Changes and Back buttons
        tk.Button(self.root, text="Save Changes", command=save_changes).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.manage_events).pack()

    
    
    def remove_event(self, event_id):
        """Remove an event."""
        db = DatabaseConnection()
        db.query("DELETE FROM community_events WHERE event_id = ?", (event_id,))
        messagebox.showinfo("Success", "Event removed successfully.")
        self.manage_events()

    def manage_events(self):
        """Manage events created by the student."""
        self.clear_screen()
        tk.Label(self.root, text="Manage Your Events", font=("Arial", 16)).pack(pady=10)

        db = DatabaseConnection()
        student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]
        events = db.fetch("""
            SELECT event_id, name, location, date, time, max_participants, description, event_type
            FROM community_events
            WHERE organizer_id = ?
        """, (student_id,))

        if events:
            for event in events:
                tk.Label(self.root, text=f"Event: {event[1]}").pack()
                tk.Label(self.root, text=f"Location: {event[2]}").pack()
                tk.Label(self.root, text=f"Date: {event[3]}, Time: {event[4]}").pack()
                tk.Label(self.root, text=f"Max Participants: {event[5]}").pack()
                tk.Label(self.root, text=f"Description: {event[6]}").pack()
                tk.Label(self.root, text=f"Type: {event[7]}").pack()

                tk.Button(self.root, text="Edit", command=lambda e=event: self.edit_event(e)).pack()
                tk.Button(self.root, text="Remove", command=lambda e=event: self.remove_event(e[0])).pack()
                tk.Label(self.root, text="").pack()
        else:
            tk.Label(self.root, text="You have no active events.").pack()

        tk.Button(self.root, text="Back", width=20, command=self.community_events_menu).pack()

    def view_upcoming_events(self):
        """View events the user is participating in or owns."""
        self.clear_screen()
        tk.Label(self.root, text="Upcoming Events", font=("Arial", 16)).pack(pady=10)

        db = DatabaseConnection()
        student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]

        # Fetch events the user is participating in or owns
        events = db.fetch("""
            SELECT e.event_id, e.name, e.location, e.date, e.time, e.max_participants, e.description, e.event_type, u.username AS organizer
            FROM community_events e
            LEFT JOIN event_participants ep ON e.event_id = ep.event_id
            LEFT JOIN users u ON e.organizer_id = u.user_id
            WHERE (ep.student_id = ? AND ep.status = 'accepted') OR e.organizer_id = ?
            GROUP BY e.event_id
        """, (student_id, student_id))

        if events:
            for event in events:
                tk.Label(self.root, text=f"Event: {event[1]}").pack()
                tk.Label(self.root, text=f"Location: {event[2]}").pack()
                tk.Label(self.root, text=f"Date: {event[3]}, Time: {event[4]}").pack()
                tk.Label(self.root, text=f"Max Participants: {event[5]}").pack()
                tk.Label(self.root, text=f"Description: {event[6]}").pack()
                tk.Label(self.root, text=f"Event Type: {event[7].capitalize()}").pack()  # Correct index for event_type
                tk.Label(self.root, text=f"Organizer: {event[8]}").pack()
                tk.Label(self.root, text="").pack()
        else:
            tk.Label(self.root, text="No upcoming events found.").pack()

        tk.Button(self.root, text="Back", command=self.community_events_menu).pack()


    #carpooling_menu
    def carpooling_menu(self):
        """Carpooling main menu."""
        self.clear_screen()
        tk.Label(self.root, text="Carpooling", font=("Arial", 16)).pack(pady=10)

        tk.Button(self.root, text="Search Carpools", width=20, command=self.search_carpools).pack(pady=5)
        tk.Button(self.root, text="Post Carpool", width=20, command=self.post_carpool).pack(pady=5)
        tk.Button(self.root, text="Manage Carpools", width=20, command=self.manage_carpools).pack(pady=5)
        tk.Button(self.root, text="View Carpool Requests", width=20, command=self.view_carpool_requests).pack(pady=5)
        tk.Button(self.root, text="Back", width=20, command=self.display).pack(pady=5)


#search_carpools
    def search_carpools(self):
        """Search available carpools."""
        self.clear_screen()
        tk.Label(self.root, text="Search Carpools", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Starting Point:").pack()
        start_entry = tk.Entry(self.root)
        start_entry.pack()

        tk.Label(self.root, text="Destination:").pack()
        dest_entry = tk.Entry(self.root)
        dest_entry.pack()

        def submit_search():
            start = start_entry.get().strip()
            destination = dest_entry.get().strip()

            if not start or not destination:
                messagebox.showerror("Error", "Starting point and destination are required.")
                return

            db = DatabaseConnection()
            carpools = db.fetch("""
                SELECT c.carpool_id, c.start_point, c.destination, c.price, c.seats, c.date, c.time, c.stops, u.username
                FROM carpools c
                LEFT JOIN users u ON c.student_id = u.user_id
                WHERE (c.start_point LIKE ? OR c.stops LIKE ?) AND c.destination LIKE ? AND c.seats > 0
            """, (f"%{start}%", f"%{start}%", f"%{destination}%"))

            self.display_carpool_results(carpools)

        tk.Button(self.root, text="Search", command=submit_search).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.carpooling_menu).pack()

    def display_carpool_results(self, results):
        """Display search results for carpools."""
        self.clear_screen()
        tk.Label(self.root, text="Available Carpools", font=("Arial", 16)).pack(pady=10)

        if results:
            for idx, carpool in enumerate(results, start=1):
                tk.Label(self.root, text=f"Carpool #{idx}").pack()
                tk.Label(self.root, text=f"Driver: {carpool[8]}").pack()
                tk.Label(self.root, text=f"   From: {carpool[1]} to {carpool[2]}").pack()
                tk.Label(self.root, text=f"   Price: ${carpool[3]}").pack()
                tk.Label(self.root, text=f"   Seats Available: {carpool[4]}").pack()
                tk.Label(self.root, text=f"   Date: {carpool[5]}").pack()
                tk.Label(self.root, text=f"   Time: {carpool[6]}").pack()
                tk.Label(self.root, text=f"   Stops: {carpool[7] if carpool[7] else 'None'}").pack()
                tk.Button(self.root, text="Request to Join", command=lambda c=carpool: self.request_to_join_carpool(c)).pack()
                tk.Label(self.root, text="").pack()
        else:
            tk.Label(self.root, text="No carpools found.").pack()

        tk.Button(self.root, text="Back", command=self.search_carpools).pack()

    def request_to_join_carpool(self, carpool):
        """Send a request to join the carpool."""
        db = DatabaseConnection()
        student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]
        db.query("""
            INSERT INTO carpool_requests (carpool_id, student_id, status)
            VALUES (?, ?, 'pending')
        """, (carpool[0], student_id))
        messagebox.showinfo("Success", "Request sent to join carpool.")
        self.search_carpools()

    def post_carpool(self):
        """Post a new carpool."""
        self.clear_screen()
        tk.Label(self.root, text="Post Carpool", font=("Arial", 16)).pack(pady=10)

        # Input fields for carpool details
        fields = {
            "Starting Point": tk.Entry(self.root),
            "Destination": tk.Entry(self.root),
            "Seats Available": tk.Entry(self.root),
            "Price per Seat": tk.Entry(self.root),
            "Date (YYYY-MM-DD)": tk.Entry(self.root),
            "Time (HH:MM)": tk.Entry(self.root),
        }

        for label, widget in fields.items():
            tk.Label(self.root, text=label).pack()
            widget.pack()

        # Stops and ETA input
        stops_frame = tk.Frame(self.root)
        stops_frame.pack(pady=10)

        stops = []

        def add_stop():
            stop_frame = tk.Frame(stops_frame)
            stop_frame.pack(pady=5)
            
            # Add Stop Name label and entry
            tk.Label(stop_frame, text="Stop Name:").pack(side=tk.LEFT, padx=5)
            stop_entry = tk.Entry(stop_frame, width=20)
            stop_entry.pack(side=tk.LEFT, padx=5)
            
            # Add ETA label and entry
            tk.Label(stop_frame, text="ETA (HH:MM):").pack(side=tk.LEFT, padx=5)
            eta_entry = tk.Entry(stop_frame, width=10)
            eta_entry.pack(side=tk.LEFT, padx=5)
            
            # Add Remove button
            remove_button = tk.Button(stop_frame, text="Remove", command=lambda: remove_stop(stop_frame, stop_entry, eta_entry))
            remove_button.pack(side=tk.LEFT, padx=5)
            
            # Add to stops list
            stops.append((stop_entry, eta_entry))


        def remove_stop(stop_frame, stop_entry, eta_entry):
            stop_frame.destroy()
            stops.remove((stop_entry, eta_entry))

        tk.Button(self.root, text="Add Stop", command=add_stop).pack()

        def submit_carpool():
            data = {key: widget.get().strip() for key, widget in fields.items()}
            if not all(data.values()):
                messagebox.showerror("Error", "All fields are mandatory.")
                return

            stop_data = []
            for stop_entry, eta_entry in stops:
                stop = stop_entry.get().strip()
                eta = eta_entry.get().strip()
                if stop and eta:
                    stop_data.append(f"{stop} (ETA: {eta})")

            stops_string = "; ".join(stop_data) if stop_data else None

            db = DatabaseConnection()
            student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]
            db.query("""
                INSERT INTO carpools (student_id, start_point, destination, seats, price, date, time, stops)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (student_id, data["Starting Point"], data["Destination"], data["Seats Available"], data["Price per Seat"], data["Date (YYYY-MM-DD)"], data["Time (HH:MM)"], stops_string))
            messagebox.showinfo("Success", "Carpool posted successfully.")
            self.carpooling_menu()

        tk.Button(self.root, text="Submit", command=submit_carpool).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.carpooling_menu).pack()

#manage_carpools
    def manage_carpools(self):
        """Manage student's carpools."""
        self.clear_screen()
        tk.Label(self.root, text="Manage Your Carpools", font=("Arial", 16)).pack(pady=10)

        db = DatabaseConnection()
        student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]
        carpools = db.fetch("""
            SELECT carpool_id, start_point, destination, seats, price, stops, date, time
            FROM carpools
            WHERE student_id = ?
        """, (student_id,))

        if carpools:
            for carpool in carpools:
                tk.Label(self.root, text=f"From {carpool[1]} to {carpool[2]}").pack()
                tk.Label(self.root, text=f"Seats Available: {carpool[3]}").pack()
                tk.Label(self.root, text=f"Price: ${carpool[4]}").pack()
                tk.Label(self.root, text=f"Date: {carpool[6]}").pack()
                tk.Label(self.root, text=f"Time: {carpool[7]}").pack()
                tk.Button(self.root, text="Edit", command=lambda c=carpool: self.edit_carpool(c)).pack()
                tk.Button(self.root, text="Remove", command=lambda c=carpool: self.remove_carpool(c[0])).pack()
                tk.Label(self.root, text="").pack()
        else:
            tk.Label(self.root, text="You have no active carpools.").pack()

        tk.Button(self.root, text="Back", command=self.carpooling_menu).pack()

    def edit_carpool(self, carpool):
        """Edit an existing carpool."""
        self.clear_screen()
        tk.Label(self.root, text="Edit Carpool", font=("Arial", 16)).pack(pady=10)

        # Input fields for carpool details
        fields = {
            "Starting Point": tk.Entry(self.root),
            "Destination": tk.Entry(self.root),
            "Seats Available": tk.Entry(self.root),
            "Price per Seat": tk.Entry(self.root),
            "Date (YYYY-MM-DD)": tk.Entry(self.root),
            "Time (HH:MM)": tk.Entry(self.root),
        }

        # Pre-fill the fields with existing carpool data
        fields["Starting Point"].insert(0, carpool[1])
        fields["Destination"].insert(0, carpool[2])
        fields["Seats Available"].insert(0, carpool[3])
        fields["Price per Seat"].insert(0, carpool[4])
        fields["Date (YYYY-MM-DD)"].insert(0, carpool[6])
        fields["Time (HH:MM)"].insert(0, carpool[7])

        for label, widget in fields.items():
            tk.Label(self.root, text=label).pack()
            widget.pack()

        # Stops and ETA input
        stops_frame = tk.Frame(self.root)
        stops_frame.pack(pady=10)

        # Parse existing stops into a list
        existing_stops = carpool[5].split("; ") if carpool[5] else []
        stops = []

        def add_stop(stop_name="", eta=""):
            """Add a stop to the stops frame."""
            stop_frame = tk.Frame(stops_frame)
            stop_frame.pack(pady=5)
            stop_name_entry = tk.Entry(stop_frame, width=20)
            stop_name_entry.pack(side=tk.LEFT, padx=5)
            stop_name_entry.insert(0, stop_name)  # Pre-fill if data exists
            eta_entry = tk.Entry(stop_frame, width=10)
            eta_entry.pack(side=tk.LEFT, padx=5)
            eta_entry.insert(0, eta)  # Pre-fill if data exists
            remove_button = tk.Button(stop_frame, text="Remove", command=lambda: remove_stop(stop_frame, stop_name_entry, eta_entry))
            remove_button.pack(side=tk.LEFT)
            stops.append((stop_name_entry, eta_entry))

        def remove_stop(stop_frame, stop_name_entry, eta_entry):
            """Remove a stop from the stops frame."""
            stop_frame.destroy()
            stops.remove((stop_name_entry, eta_entry))

        # Populate existing stops
        for stop in existing_stops:
            if "(ETA: " in stop:
                stop_name, eta = stop.split(" (ETA: ")
                eta = eta.rstrip(")")
                add_stop(stop_name, eta)
            else:
                add_stop(stop, "")

        tk.Button(self.root, text="Add Stop", command=add_stop).pack()

        def save_changes():
            """Save changes to the carpool."""
            data = {key: widget.get().strip() for key, widget in fields.items()}
            if not all(data.values()):
                messagebox.showerror("Error", "All fields are mandatory.")
                return

            stop_data = []
            for stop_name_entry, eta_entry in stops:
                stop_name = stop_name_entry.get().strip()
                eta = eta_entry.get().strip()
                if stop_name and eta:
                    stop_data.append(f"{stop_name} (ETA: {eta})")

            stops_string = "; ".join(stop_data) if stop_data else None

            db = DatabaseConnection()
            db.query("""
                UPDATE carpools
                SET start_point = ?, destination = ?, seats = ?, price = ?, stops = ?, date = ?, time = ?
                WHERE carpool_id = ?
            """, (data["Starting Point"], data["Destination"], data["Seats Available"], data["Price per Seat"], stops_string, data["Date (YYYY-MM-DD)"], data["Time (HH:MM)"], carpool[0]))
            
            # Notify participants about the update
            participants = db.fetch("SELECT student_id FROM carpool_requests WHERE carpool_id = ? AND status = 'accepted'", (carpool[0],))
            for participant in participants:
                notification_manager.notify(participant[0], f"Carpool from {carpool[1]} to {carpool[2]} has been updated.")
            
            messagebox.showinfo("Success", "Carpool updated successfully.")
            self.manage_carpools()

        tk.Button(self.root, text="Save Changes", command=save_changes).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.manage_carpools).pack()


    def remove_carpool(self, carpool_id):
        db = DatabaseConnection()
        observer = CarpoolObserver(db)

        # Notify participants
        observer.notify_participants(carpool_id, "The carpool you joined has been canceled by the poster.")

        # Delete the carpool
        db.query("DELETE FROM carpools WHERE carpool_id = ?", (carpool_id,))
        db.query("DELETE FROM carpool_requests WHERE carpool_id = ?", (carpool_id,))
        messagebox.showinfo("Success", "Carpool removed and participants notified.")
        self.manage_carpools()


    def view_carpool_requests(self):
        """View and manage requests for student's carpools."""
        self.clear_screen()
        tk.Label(self.root, text="Carpool Requests", font=("Arial", 16)).pack(pady=10)

        db = DatabaseConnection()
        student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]
        requests = db.fetch("""
            SELECT cr.request_id, cr.carpool_id, cr.student_id, cr.status, c.start_point, c.destination, u.username
            FROM carpool_requests cr
            JOIN carpools c ON cr.carpool_id = c.carpool_id
            JOIN users u ON cr.student_id = u.user_id
            WHERE c.student_id = ?
        """, (student_id,))

        if requests:
            for req in requests:
                tk.Label(self.root, text=f"Request from {req[6]}").pack()
                tk.Label(self.root, text=f"Carpool: {req[4]} to {req[5]}").pack()
                tk.Label(self.root, text=f"Status: {req[3]}").pack()
                if req[3] == "pending":
                    tk.Button(self.root, text="Accept", command=lambda r=req: self.accept_carpool_request(r)).pack()
                    tk.Button(self.root, text="Reject", command=lambda r=req: self.reject_carpool_request(r)).pack()
                tk.Label(self.root, text="").pack()
        else:
            tk.Label(self.root, text="No carpool requests found.").pack()

        tk.Button(self.root, text="Back", command=self.carpooling_menu).pack()

    def accept_carpool_request(self, request):
        """Accept a carpool request."""
        db = DatabaseConnection()
        db.query("UPDATE carpool_requests SET status = 'accepted' WHERE request_id = ?", (request[0],))
        db.query("UPDATE carpools SET seats = seats - 1 WHERE carpool_id = ? AND seats > 0", (request[1],))
        notification_manager.notify(request[2], "Your carpool request has been accepted.")
        self.view_carpool_requests()

    def reject_carpool_request(self, request):
        """Reject a carpool request."""
        db = DatabaseConnection()
        db.query("UPDATE carpool_requests SET status = 'rejected' WHERE request_id = ?", (request[0],))
        notification_manager.notify(request[2], "Your carpool request has been rejected.")
        self.view_carpool_requests()

    def view_upcoming_carpools(self):
        """View upcoming carpools for the student."""
        self.clear_screen()
        tk.Label(self.root, text="Upcoming Carpools", font=("Arial", 16)).pack(pady=10)

        db = DatabaseConnection()
        student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]

        # Fetch carpools where the student is a driver or a passenger
        upcoming_carpools = db.fetch("""
            SELECT c.carpool_id, c.start_point, c.destination, c.seats, c.price, c.date, c.time, c.stops, u.username, c.student_id
            FROM carpools c
            LEFT JOIN carpool_requests cr ON c.carpool_id = cr.carpool_id
            LEFT JOIN users u ON c.student_id = u.user_id
            WHERE (c.student_id = ? OR cr.student_id = ?) AND (cr.status = 'accepted' OR c.student_id = ?)
        """, (student_id, student_id, student_id))

        if upcoming_carpools:
            for carpool in upcoming_carpools:
                driver_name = f"{carpool[8]} (You)" if carpool[9] == student_id else carpool[8]
                tk.Label(self.root, text=f"Carpool ID: {carpool[0]}").pack()
                tk.Label(self.root, text=f"Driver: {driver_name}").pack()
                tk.Label(self.root, text=f"From: {carpool[1]}").pack()
                tk.Label(self.root, text=f"To: {carpool[2]}").pack()
                tk.Label(self.root, text=f"Date: {carpool[5]}").pack()
                tk.Label(self.root, text=f"Time: {carpool[6]}").pack()
                tk.Label(self.root, text=f"Seats Available: {carpool[3]}").pack()
                tk.Label(self.root, text=f"Price: ${carpool[4]}").pack()
                tk.Label(self.root, text=f"Stops: {carpool[7] if carpool[7] else 'None'}").pack()
                tk.Label(self.root, text="").pack()
        else:
            tk.Label(self.root, text="No upcoming carpools found.").pack()

        tk.Button(self.root, text="Back", command=self.display).pack()


    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def search_properties(self):
        self.clear_screen()
        tk.Label(self.root, text="Search Properties", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="State (Mandatory):").pack()
        state_entry = tk.Entry(self.root)
        state_entry.pack()

        tk.Label(self.root, text="City (Optional):").pack()
        city_entry = tk.Entry(self.root)
        city_entry.pack()

        tk.Label(self.root, text="Bedrooms (Optional):").pack()
        bedrooms_entry = tk.Entry(self.root)
        bedrooms_entry.pack()

        def submit_search():
            state = state_entry.get().strip()
            city = city_entry.get().strip()
            bedrooms = bedrooms_entry.get().strip()

            if not state:
                messagebox.showerror("Error", "State is mandatory.")
                return

            db = DatabaseConnection()
            student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]

            # SQL query to include all required columns
            properties = db.fetch("""
                SELECT p.property_id, p.address, p.city, p.state, p.zipcode, 
                    p.bedrooms - (
                        SELECT COUNT(*) 
                        FROM leases 
                        WHERE leases.property_id = p.property_id
                    ) AS rooms_available, 
                    p.bedrooms, p.kitchens, p.bathrooms
                FROM properties p
                WHERE p.state = ? AND p.visible = 1 
                AND p.property_id NOT IN (
                    SELECT property_id FROM leases WHERE tenant_id = ?
                )
                AND (p.city LIKE ? OR ? = '') 
                AND (p.bedrooms = ? OR ? = '')
            """, (state, student_id, f"%{city}%", city, bedrooms, bedrooms))


            self.display_search_results(properties)

        tk.Button(self.root, text="Search", command=submit_search).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.display).pack()



    def display_search_results(self, results):
        self.clear_screen()
        tk.Label(self.root, text="Search Results", font=("Arial", 16)).pack(pady=10)

        if results:
            for idx, property in enumerate(results, start=1):
                tk.Label(self.root, text=f"{idx}. Address: {property[1]}").pack()
                tk.Label(self.root, text=f"   City: {property[2]}, State: {property[3]}, Zipcode: {property[4]}").pack()
                tk.Label(self.root, text=f"   Rooms Available: {property[5]}").pack()
                tk.Label(self.root, text=f"   Bedrooms: {property[6]}, Kitchens: {property[7]}, Bathrooms: {property[8]}").pack()

                # Add Bookmark and Schedule Visit Buttons
                tk.Button(self.root, text="Bookmark", command=lambda p=property: self.bookmark_property(p[0])).pack()
                tk.Button(self.root, text="Schedule Visit", command=lambda p=property: self.schedule_visit(p)).pack()
                tk.Label(self.root, text="").pack()
        else:
            tk.Label(self.root, text="No properties found.").pack()

        tk.Button(self.root, text="Back", command=self.search_properties).pack()




    def bookmark_property(self, property_id):
        db = DatabaseConnection()
        student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]
        existing = db.fetch("SELECT * FROM bookmarks WHERE student_id = ? AND property_id = ?", (student_id, property_id))

        if existing:
            db.query("DELETE FROM bookmarks WHERE student_id = ? AND property_id = ?", (student_id, property_id))
            messagebox.showinfo("Success", "Removed from bookmarks.")
        else:
            db.query("INSERT INTO bookmarks (student_id, property_id) VALUES (?, ?)", (student_id, property_id))
            messagebox.showinfo("Success", "Property bookmarked.")

    def schedule_visit(self, property):
        self.clear_screen()
        tk.Label(self.root, text="Schedule Visit", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text=f"Property Address: {property[1]}").pack()

        visit_type_var = tk.StringVar(value="virtual")

        tk.Label(self.root, text="Visit Type:").pack()
        tk.Radiobutton(self.root, text="Virtual", variable=visit_type_var, value="virtual").pack()
        tk.Radiobutton(self.root, text="In-person", variable=visit_type_var, value="in_person").pack()

        tk.Label(self.root, text="Date (YYYY-MM-DD):").pack()
        date_entry = tk.Entry(self.root)
        date_entry.pack()

        tk.Label(self.root, text="Time (HH:MM):").pack()
        time_entry = tk.Entry(self.root)
        time_entry.pack()

        def submit_request():
            visit_type = visit_type_var.get()
            date = date_entry.get().strip()
            time = time_entry.get().strip()

            db = DatabaseConnection()
            student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]
            homeowner_id = db.fetch("SELECT homeowner_id FROM properties WHERE property_id = ?", (property[0],))[0][0]

            db.query("""
                INSERT INTO property_visits (property_id, student_id, homeowner_id, visit_type, date, time)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (property[0], student_id, homeowner_id, visit_type, date, time))
            notification_manager.notify(homeowner_id, f"New visit request for property: {property[1]} by {self.username}.")
            messagebox.showinfo("Success", "Visit request submitted.")
            self.display()

        tk.Button(self.root, text="Submit", command=submit_request).pack(pady=10)
        tk.Button(self.root, text="Back", command=lambda: self.display_search_results([property])).pack()

    def view_bookmarked_properties(self):
        self.clear_screen()
        tk.Label(self.root, text="Bookmarked Properties", font=("Arial", 16)).pack(pady=10)

        db = DatabaseConnection()
        student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]
        bookmarks = db.fetch("""
            SELECT p.property_id, p.address, p.city, p.state, p.zipcode, p.bedrooms, p.kitchens, p.bathrooms, p.description
            FROM bookmarks b
            JOIN properties p ON b.property_id = p.property_id
            WHERE b.student_id = ?
        """, (student_id,))

        if bookmarks:
            for idx, bookmark in enumerate(bookmarks, start=1):
                tk.Label(self.root, text=f"{idx}. Address: {bookmark[1]}").pack()
                tk.Label(self.root, text=f"   City: {bookmark[2]}, State: {bookmark[3]}, Zipcode: {bookmark[4]}").pack()
                tk.Label(self.root, text=f"   Bedrooms: {bookmark[5]}, Kitchens: {bookmark[6]}, Bathrooms: {bookmark[7]}").pack()
                tk.Label(self.root, text=f"   Description: {bookmark[8]}").pack()

                tk.Button(self.root, text="Unbookmark", command=lambda b=bookmark: self.bookmark_property(b[0])).pack()
                tk.Button(self.root, text="Schedule Visit", command=lambda b=bookmark: self.schedule_visit(b)).pack()
                tk.Label(self.root, text="").pack()
        else:
            tk.Label(self.root, text="No bookmarked properties.").pack()

        tk.Button(self.root, text="Back", command=self.display).pack()
        
    def view_upcoming_carpools(self):
        """View upcoming carpools for the student."""
        self.clear_screen()
        tk.Label(self.root, text="Upcoming Carpools", font=("Arial", 16)).pack(pady=10)

        db = DatabaseConnection()
        student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]

        # Fetch carpools where the student is a driver or a passenger
        upcoming_carpools = db.fetch("""
            SELECT c.carpool_id, c.start_point, c.destination, c.seats, c.price, c.stops, u.username
            FROM carpools c
            LEFT JOIN carpool_requests cr ON c.carpool_id = cr.carpool_id
            LEFT JOIN users u ON c.student_id = u.user_id
            WHERE (c.student_id = ? OR cr.student_id = ?) AND cr.status = 'accepted'
        """, (student_id, student_id))

        if upcoming_carpools:
            for carpool in upcoming_carpools:
                tk.Label(self.root, text=f"Carpool ID: {carpool[0]}").pack()
                tk.Label(self.root, text=f"Driver: {carpool[6]}").pack()
                tk.Label(self.root, text=f"From: {carpool[1]}").pack()
                tk.Label(self.root, text=f"To: {carpool[2]}").pack()
                tk.Label(self.root, text=f"Seats Available: {carpool[3]}").pack()
                tk.Label(self.root, text=f"Price: ${carpool[4]}").pack()
                tk.Label(self.root, text=f"Stops: {carpool[5] if carpool[5] else 'None'}").pack()
                tk.Label(self.root, text="").pack()
        else:
            tk.Label(self.root, text="No upcoming carpools found.").pack()

        tk.Button(self.root, text="Back", command=self.display).pack()


    def view_notifications(self):
        self.clear_screen()
        tk.Label(self.root, text="Notifications", font=("Arial", 16)).pack(pady=10)

        db = DatabaseConnection()
        student_id = db.fetch("SELECT user_id FROM users WHERE username = ?", (self.username,))[0][0]
        notifications = db.fetch("SELECT message FROM notifications WHERE user_id = ?", (student_id,))

        if notifications:
            for notification in notifications:
                tk.Label(self.root, text=notification[0]).pack()
        else:
            tk.Label(self.root, text="No notifications.").pack()

        tk.Button(self.root, text="Back", command=self.display).pack()

#CARPOOL CLASS        
class CarpoolObserver:
    def __init__(self, db):
        self.db = db

    def notify_participants(self, carpool_id, message):
        """Notify all participants of the carpool."""
        participants = self.db.fetch("""
            SELECT cr.student_id, u.username
            FROM carpool_requests cr
            JOIN users u ON cr.student_id = u.user_id
            WHERE cr.carpool_id = ? AND cr.status = 'accepted'
        """, (carpool_id,))

        for participant in participants:
            student_id = participant[0]
            self.db.query("""
                INSERT INTO notifications (user_id, message)
                VALUES (?, ?)
            """, (student_id, message))

#EVENTSS
class EventFactory:
    @staticmethod
    def create_event(event_type, name, location, date, time, description, max_participants):
        if event_type == "social":
            return SocialEvent(name, location, date, time, description, max_participants)
        elif event_type == "academic":
            return AcademicEvent(name, location, date, time, description, max_participants)
        elif event_type == "sports":
            return SportsEvent(name, location, date, time, description, max_participants)
        elif event_type == "potluck":
            return PotluckEvent(name, location, date, time, description, max_participants)
        else:
            return OtherEvent(name, location, date, time, description, max_participants)


class CommunityEvent:
    def __init__(self, name, location, date, time, description, max_participants):
        self.name = name
        self.location = location
        self.date = date
        self.time = time
        self.description = description
        self.max_participants = max_participants


class SocialEvent(CommunityEvent):
    pass


class AcademicEvent(CommunityEvent):
    pass


class SportsEvent(CommunityEvent):
    pass


class PotluckEvent(CommunityEvent):
    pass


class OtherEvent(CommunityEvent):
    pass
class EventObserver:
    def __init__(self, db):
        self.db = db

    def notify_participants(self, event_id, message):
        """Notify all participants of an event."""
        participants = self.db.fetch("""
            SELECT ep.student_id
            FROM event_participants ep
            WHERE ep.event_id = ? AND ep.status = 'accepted'
        """, (event_id,))

        for participant in participants:
            student_id = participant[0]
            self.db.query("""
                INSERT INTO notifications (user_id, message)
                VALUES (?, ?)
            """, (student_id, message))


# Application Entry Point
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Housing Management App")
    root.geometry("500x600")
    WelcomeScreen(root).display()
    root.mainloop()

