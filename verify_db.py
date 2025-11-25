import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root', 
    'password': 'Rahil@MySQL',
    'database': 'dbms3'
}

try:
    print("Connecting to database...")
    conn = mysql.connector.connect(**db_config)
    print("Connected!")
    
    cursor = conn.cursor(dictionary=True)
    
    print("\nChecking Admin table:")
    cursor.execute("SELECT * FROM Admin")
    admins = cursor.fetchall()
    for admin in admins:
        print(admin)
        
    print("\nChecking Host table:")
    cursor.execute("SELECT * FROM Host LIMIT 5")
    hosts = cursor.fetchall()
    for host in hosts:
        print(host)

    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
