import sqlite3

def remove_column_from_tickets(db_path='tickets.db'):
    # Connect to SQLite
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Step 1: Create a new table without the 'product_id' column
    c.execute('''
        CREATE TABLE tickets_new (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Step 2: Copy data from the old table to the new table
    c.execute('''
        INSERT INTO tickets_new (ticket_id, user_id, message, status, created_at)
        SELECT ticket_id, user_id, message, status, created_at
        FROM tickets
    ''')

    # Step 3: Drop the old table
    c.execute('DROP TABLE tickets')

    # Step 4: Rename the new table to the original table name
    c.execute('ALTER TABLE tickets_new RENAME TO tickets')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Call the function
remove_column_from_tickets()
