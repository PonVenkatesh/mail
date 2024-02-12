import psycopg2

from global_constants import DB_NAME, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD


def create_gmail_schema():
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    try:
        # Create a cursor object to interact with the database
        cursor = conn.cursor()

        # Create User table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "User" (
    user_id VARCHAR(255) PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL
);

        """)

        # Create Email table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Email (
                email_id VARCHAR(255) PRIMARY KEY,
                subject VARCHAR(255),
                body TEXT,
                sender_id VARCHAR(255) REFERENCES "User"(user_id),
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create Attachment table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Attachment (
                attachment_id TEXT PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                data BYTEA NOT NULL,
                email_id VARCHAR(255) REFERENCES Email(email_id)
            )
        """)

        # Create Email_Label table
        cursor.execute("""
           CREATE TABLE IF NOT EXISTS Email_Label (
                id SERIAL PRIMARY KEY,
                email_id VARCHAR(255) REFERENCES Email(email_id),
                label_id VARCHAR(255)
            )
        """)

        # Commit the transaction
        conn.commit()

        print("Gmail API schema created successfully.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the database connection
        cursor.close()
        conn.close()


if __name__ == "__main__":
    create_gmail_schema()
