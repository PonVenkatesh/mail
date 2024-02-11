# Gmail API Integration

This Python script demonstrates how to interact with the Gmail API using the Google API client library.

## Prerequisites

- Python 3.x
- [Google Cloud Platform (GCP) project](https://console.developers.google.com/)
- Enabled Gmail API and API credentials (client secret JSON file)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/PonVenkatesh/mail.git
   cd mail

2. Install dependencies:

    ```bash
    pip install -r requirements.txt

3. Download the API credentials (client secret JSON file) from the GCP Console. 
   
   Follow the instructions mentioned here : https://developers.google.com/gmail/api/quickstart/python
4. Setup Postgres

#PostgreSQL Installation Guide

This guide provides step-by-step instructions for installing PostgreSQL on different operating systems.

## Windows

1. Download the PostgreSQL installer for Windows from the [official website](https://www.postgresql.org/download/windows/).

   1. Run the installer and follow the on-screen instructions.

   2. During installation, set a password for the PostgreSQL superuser (postgres). Remember this password as it will be needed later.

## macOS

1. Install PostgreSQL using Homebrew:

   ```bash
   brew install postgresql
2. Start the PostgreSQL service:

    ```bash
    brew services start postgresql

3. Start the PostgreSQL service:

    ```bash
    sudo service postgresql start
   
###Accessing PostgreSQL
**Windows:** PostgreSQL command line tools can be accessed through the "pgAdmin" application or the command line.

**macOS/Linux:** Access the PostgreSQL command line using the psql tool
    ```psql -U postgres```

###Create a new database:

```sql
CREATE DATABASE your_database_name;
```

5. update postgres details in _global_constants.py_ and create necessary tables using the _create_tables.py_.
   ```bash
   python create_tables.py
6. Run `python sync_emails.py`