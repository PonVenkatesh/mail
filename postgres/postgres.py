import psycopg2

from global_constants import DB_NAME, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD


def get_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn


def insert_json_data(conn, table, primary_key, **kwargs):
    with conn.cursor() as cursor:
        for key, value in kwargs.items():
            if value is None:
                kwargs[key] = 'null'
            elif isinstance(value, str):
                kwargs[key] = f"'{value}'"

        placeholders = ', '.join(["{}"] * len(kwargs))
        columns = ", ".join(kwargs.keys())
        values = list(kwargs.values())
        sql = """INSERT INTO "%s" ( %s ) VALUES ( %s )
                        ON CONFLICT (%s) DO NOTHING""" % (table, columns, placeholders, primary_key)
        sql = sql.format(*values)
        cursor.execute(sql)


def push_data_to_postgres(gmail):
    # Connect to PostgreSQL
    conn = get_connection()

    try:

        print(" Inserting user data")
        for user in gmail.user_data:
            insert_json_data(conn, "user", "user_id", **user)

        print(" Inserting email data")
        for mail in gmail.mail_data:
            insert_json_data(conn, "email", "email_id", **mail)

        print(" Inserting attachment data")
        for attachment in gmail.attachment_data:
            insert_json_data(conn, "attachment", "attachment_id", **attachment)

        print(" Inserting label data")
        for label in gmail.label_data:
            insert_json_data(conn, "label", "id", **label)

        # Commit the transaction
        conn.commit()

        print("Data inserted into postgres successfully.")

    except Exception as e:
        # Rollback the transaction in case of an error
        conn.rollback()
        print(f"Error: {e}")

    finally:
        # Close the database connection
        conn.close()


def fetch_data_from_postgres():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # SQL query
        query = """
            SELECT e.email_id, e.sender_id, e.subject, e.body, e.received_at, u.user_id, a.attachment_id, a.filename, ARRAY_AGG(l.label_id) AS label_ids
            FROM email e
            JOIN public.user u ON e.sender_id = u.user_id
            LEFT JOIN attachment a ON e.email_id = a.email_id
            LEFT JOIN label l ON e.email_id = l.email_id
            GROUP BY e.email_id, u.user_id, a.attachment_id;
        """
        cursor.execute(query)

        # Fetch the results
        results = cursor.fetchall()

        # Process and store the data in a list of dictionaries
        email_data_list = []
        for row in results:
            email_data = {
                'email_id': row[0],
                'sender_id': row[1],
                'subject': row[2],
                'body': row[3],
                'received_at': row[4],
                'user_id': row[5],
                'attachment_id': row[6],
                'filename': row[7],
                'label_ids': row[8],
            }
            email_data_list.append(email_data)

        return email_data_list

    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()
