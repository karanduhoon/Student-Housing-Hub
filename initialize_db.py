import sqlite3

class DatabaseInitializer:
    def __init__(self, db_name="housing_app.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def initialize(self):
        """Initialize the database schema."""
        # Users table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL, 
                role TEXT NOT NULL,
                phone_number TEXT NOT NULL
            );
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                property_id INTEGER PRIMARY KEY AUTOINCREMENT,
                homeowner_id INTEGER NOT NULL,
                address TEXT NOT NULL,
                bedrooms INTEGER NOT NULL,
                kitchens INTEGER NOT NULL,
                bathrooms INTEGER NOT NULL,
                description TEXT,
                state TEXT NOT NULL,
                city TEXT,
                zipcode TEXT,
                photo_path TEXT,
                rooms_available INTEGER NOT NULL DEFAULT 0,
                visible INTEGER NOT NULL DEFAULT 1,  -- New column for visibility
                FOREIGN KEY(homeowner_id) REFERENCES users(user_id)
            );
        """)




        # Property visits table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS property_visits (
                visit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                homeowner_id INTEGER NOT NULL,
                visit_type TEXT NOT NULL CHECK(visit_type IN ('virtual', 'in_person')),
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'accepted', 'rejected')),
                note TEXT,
                FOREIGN KEY(property_id) REFERENCES properties(property_id),
                FOREIGN KEY(student_id) REFERENCES users(user_id),
                FOREIGN KEY(homeowner_id) REFERENCES users(user_id)
            );
        """)
        
                # Maintenance Requests table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_requests (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                tenant_id INTEGER NOT NULL,
                description TEXT NOT NULL,
                location TEXT,
                date TEXT NOT NULL,
                resolution_date TEXT,
                status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'resolved')),
                FOREIGN KEY(property_id) REFERENCES properties(property_id),
                FOREIGN KEY(tenant_id) REFERENCES users(user_id)
            );
        """)


        # Bookmarks table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookmarks (
                bookmark_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                property_id INTEGER NOT NULL,
                FOREIGN KEY(student_id) REFERENCES users(user_id),
                FOREIGN KEY(property_id) REFERENCES properties(property_id)
            );
        """)

        # Notifications table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                status TEXT DEFAULT 'unread',
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            );
        """)

        # Carpools table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS carpools (
                carpool_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                start_point TEXT NOT NULL,
                destination TEXT NOT NULL,
                seats INTEGER NOT NULL,
                price REAL NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                stops TEXT,
                FOREIGN KEY(student_id) REFERENCES users(user_id)
            );
        """)

        # Carpool Requests table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS carpool_requests (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                carpool_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY(carpool_id) REFERENCES carpools(carpool_id),
                FOREIGN KEY(student_id) REFERENCES users(user_id)
            );
        """)

        # Community Events table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS community_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                organizer_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                max_participants INTEGER NOT NULL,
                description TEXT,
                event_type TEXT NOT NULL,
                FOREIGN KEY(organizer_id) REFERENCES users(user_id)
            );
        """)

        # Event Participants table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_participants (
                participant_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                response TEXT,
                status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'accepted', 'rejected')),
                FOREIGN KEY(event_id) REFERENCES community_events(event_id),
                FOREIGN KEY(student_id) REFERENCES users(user_id)
            );
        """)

        # Event Responses table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_responses (
                response_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                response TEXT,
                status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'accepted', 'rejected')),
                FOREIGN KEY(event_id) REFERENCES community_events(event_id),
                FOREIGN KEY(student_id) REFERENCES users(user_id)
            );
        """)

        # Leases table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS leases (
                lease_id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                tenant_id INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                rent_amount REAL NOT NULL,
                status TEXT DEFAULT 'active' CHECK(status IN ('active', 'terminated')),
                FOREIGN KEY(property_id) REFERENCES properties(property_id),
                FOREIGN KEY(tenant_id) REFERENCES users(user_id)
            );
        """)

        self.connection.commit()
        self.connection.close()
        print("Database initialized successfully.")


if __name__ == "__main__":
    initializer = DatabaseInitializer()
    initializer.initialize()
