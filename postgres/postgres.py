import psycopg2

from global_constants import DB_NAME, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD


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
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

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
