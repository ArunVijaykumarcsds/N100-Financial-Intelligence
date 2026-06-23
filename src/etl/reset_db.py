from db_utils import get_connection


def reset_database():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("DELETE FROM profit_loss")
    cursor.execute("DELETE FROM balance_sheet")
    cursor.execute("DELETE FROM companies")

    conn.commit()
    conn.close()

    print("Database reset completed.")


if __name__ == "__main__":
    reset_database()