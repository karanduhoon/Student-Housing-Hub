# Student-Housing-Hub

Here’s the updated **README** for your project named **Student Housing Hub**:

---

# Student Housing Hub

## Overview

**Student Housing Hub** is a Python-based application designed to streamline the housing search and management process for students. The system provides features to connect landlords, tenants, and students while facilitating property management, community engagement, and transportation options. The backend leverages an SQLite database to manage all interactions and data.

## Features

### Core Functionality
- **User Management**:  
  Support for multiple roles (homeowners, tenants, students).  
  Users can register, log in, and manage their profiles.

- **Property Listings**:  
  Add, edit, and manage housing properties, including availability and visibility settings.

- **Maintenance Requests**:  
  Log maintenance issues, track their status, and record resolution dates.

- **Visit Scheduling**:  
  Schedule property visits, either virtual or in-person, with status tracking.

- **Lease Management**:  
  Handle lease agreements, including rent details and lease termination.

### Additional Features
- **Bookmarks**:  
  Students can bookmark properties for future reference.

- **Notifications**:  
  Notify users about important updates or events.

- **Carpools**:  
  Create and join carpools to facilitate transportation among users.

- **Community Events**:  
  Organize and participate in events with descriptions, limits, and RSVP status.

## Database Structure

The application uses an SQLite database with the following tables:

1. **`users`**: Manages user information, roles, and contact details.  
2. **`properties`**: Stores property details like address, bedrooms, availability, and visibility.  
3. **`property_visits`**: Tracks property visit requests and statuses.  
4. **`maintenance_requests`**: Logs and manages property maintenance issues.  
5. **`bookmarks`**: Links students with their bookmarked properties.  
6. **`notifications`**: Stores user notifications and their status (read/unread).  
7. **`carpools`**: Manages carpool routes, seats, and costs.  
8. **`carpool_requests`**: Tracks requests to join carpools.  
9. **`community_events`**: Stores event details like location, participants, and type.  
10. **`event_participants`**: Tracks participation in community events.  
11. **`leases`**: Manages lease agreements, including start and end dates.  

## How to Set Up

### Prerequisites
- Python 3.7 or later.
- SQLite (comes pre-installed with Python).

### Steps to Initialize
1. Clone or download this repository.
2. Ensure the `DatabaseInitializer` class is in the project folder.
3. Run the script to initialize the database schema:
   ```bash
   python db_initializer.py
   ```
4. A database file named `housing_app.db` will be created in the project directory.

### Integration
- Use this database as the backend for your housing management system.
- Extend the application by writing scripts to interact with the database (e.g., user authentication, property management).

### Testing
- Test database functionality using Python or SQLite tools.
- Ensure all relationships and constraints are working correctly.

## Technologies Used

- **Programming Language**: Python
- **Database**: SQLite
- **Libraries**: `sqlite3`

