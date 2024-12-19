import sqlite3

class DatabaseConnection:
    _instance = None     # Singleton instance

    def __new__(cls, db_name="housing_app.db"):         # Create a new instance if one doesn't already exist
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connection = sqlite3.connect(db_name)
            cls._instance.cursor = cls._instance.connection.cursor()
        return cls._instance

    def query(self, sql, parameters=()):
        self.cursor.execute(sql, parameters)
        self.connection.commit()

    def fetch(self, sql, parameters=()):      ## Execute a SQL query and fetch all results
        self.cursor.execute(sql, parameters)
        return self.cursor.fetchall()

    def close(self):       # Close the database connection and reset the singleton instance
        self.connection.close()
        DatabaseConnection._instance = None


