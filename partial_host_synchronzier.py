import os

import psycopg2


def main():
    con = psycopg2.connect(
        database=os.getenv("INVENTORY_DB_NAME"),
        user=os.getenv("INVENTORY_DB_USER"),
        password=os.getenv("INVENTORY_DB_PASS"),
        host="localhost",
        port=os.getenv("INVENTORY_DB_PORT"),
    )
    cursor_obj = con.cursor()
    # cursor_obj.execute("SELECT * FROM Hosts")
    for i in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, "a", "b", "c", "d", "e", "f"]:
        cursor_obj.execute(
            f"SELECT COUNT(*) \
            FROM hosts \
            WHERE LEFT(id::text, 1) = '{i}'"
        )
        result = cursor_obj.fetchall()
        print(f"Number of hosts with id starting with {i}: {result[0][0]}")


if __name__ == "__main__":
    main()
