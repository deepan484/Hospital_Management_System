from database import get_db_connection

def fetch_table_info():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all table names
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
    """)
    tables = cursor.fetchall()

    table_info = {}

    # Fetch columns and relationships for each table
    for (table_name,) in tables:
        cursor.execute(f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
        """)
        columns = cursor.fetchall()
        
        cursor.execute(f"""
            SELECT kcu.column_name, ccu.table_name AS foreign_table, ccu.column_name AS foreign_column
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            WHERE constraint_type = 'FOREIGN KEY' AND kcu.table_name='{table_name}';
        """)
        foreign_keys = cursor.fetchall()

        # Store column info and relationships
        table_info[table_name] = {
            'columns': {col[0]: col[1] for col in columns},
            'foreign_keys': foreign_keys
        }

    cursor.close()
    conn.close()

    return table_info

def print_table_info(table_info):
    for table, info in table_info.items():
        print(f"Table: {table}")
        print("Columns:")
        for col, data_type in info['columns'].items():
            print(f"  {col}: {data_type}")
        print("Foreign Keys:")
        for fk in info['foreign_keys']:
            print(f"  {fk[0]} references {fk[1]}({fk[2]})")
        print("\n")

if __name__ == "__main__":
    table_info = fetch_table_info()
    print_table_info(table_info)