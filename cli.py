import psycopg2
import signal
import sys
import getpass

# ---------------- DATABASE SETTINGS ---------------- #
DB_NAME = "car_project"
DB_USER = getpass.getuser()
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_PORT = "5432"

conn = None


# ---------------- SAFE EXIT ---------------- #
def safe_exit(signum, frame):
    global conn
    print("\n\nEXIT ENCOUNTERED... EXITING SAFELY\n")
    try:
        if conn is not None and conn.closed == 0:
            conn.rollback()
            conn.close()
    except Exception:
        pass
    sys.exit()


signal.signal(signal.SIGTERM, safe_exit)
signal.signal(signal.SIGINT, safe_exit)


# ---------------- TABLE PRINTING ---------------- #
def print_table(title, descs, rows):
    print()
    sep = 25
    colamt = len(descs)
    halfway = int(sep * (colamt / 2))

    print(f"{' ' * halfway}{title.upper()}")

    def demarcate():
        for _ in range(colamt):
            print(f"|{'=' * sep}", end="")
        print("|")

    demarcate()

    for desc in descs:
        print(f"|{desc.name:<{sep}}", end="")
    print("|")

    demarcate()

    if not rows:
        print("|" + f"{'No records found.':<{sep * colamt + colamt - 1}}" + "|")
        demarcate()
    else:
        for row in rows:
            for col in row:
                print(f"|{str(col):<{sep}}", end="")
            print("|")
            demarcate()

    input("(Enter any button to continue)...")
    return


# ---------------- DATABASE CONNECTION ---------------- #
def connect_db():
    global DB_USER

    print(f"\nDefault DB user: {DB_USER}")
    entered_user = input("Enter DB User (empty for default): ").strip()

    if entered_user != "":
        DB_USER = entered_user

    entered_password = input("Enter DB Password (empty for no password/default): ")
    password_to_use = entered_password if entered_password != "" else DB_PASSWORD

    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=password_to_use,
        host=DB_HOST,
        port=DB_PORT
    )


def get_conn():
    global conn

    if conn is None or conn.closed != 0:
        conn = connect_db()
    else:
        try:
            conn.rollback()
        except Exception:
            pass

    return conn


# ---------------- INVENTORY FUNCTIONS ---------------- #
def view_inventory():
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                i.inventory_id,
                i.dealer_id,
                d.dealer_name,
                i.vin,
                b.brand_name,
                m.model_name,
                m.body_style,
                i.date_received,
                i.date_sold,
                i.price
            FROM inventory i
            JOIN dealer d ON i.dealer_id = d.dealer_id
            JOIN vehicle v ON i.vin = v.vin
            JOIN model m ON v.model_id = m.model_id
            JOIN brand b ON m.brand_id = b.brand_id
            ORDER BY i.inventory_id;
        """)

        print_table("Inventory", cur.description, cur.fetchall())

    except Exception as e:
        conn.rollback()
        print("Error viewing inventory:", e)

    finally:
        cur.close()


def search_vehicle():
    conn = get_conn()
    cur = conn.cursor()

    vin = input("Enter VIN: ").strip()

    try:
        cur.execute("""
            SELECT
                v.vin,
                b.brand_name,
                m.model_name,
                m.body_style,
                v.manufacture_date,
                v.status,
                p.plant_name
            FROM vehicle v
            JOIN model m ON v.model_id = m.model_id
            JOIN brand b ON m.brand_id = b.brand_id
            LEFT JOIN plant p ON v.plant_id = p.plant_id
            WHERE v.vin = %s;
        """, (vin,))

        print_table("Vehicle Search Result", cur.description, cur.fetchall())

    except Exception as e:
        conn.rollback()
        print("Error searching vehicle:", e)

    finally:
        cur.close()


def add_vehicle_to_inventory():
    conn = get_conn()
    cur = conn.cursor()

    try:
        dealer_id = input("Enter Dealer ID: ").strip()
        vin = input("Enter Existing VIN: ").strip()
        price = input("Enter Price: ").strip()
        date_received = input("Enter Date Received (YYYY-MM-DD): ").strip()

        cur.execute("""
            INSERT INTO inventory (dealer_id, vin, date_received, price)
            VALUES (%s, %s, %s, %s);
        """, (dealer_id, vin, date_received, price))

        conn.commit()
        print("Vehicle added to inventory successfully.")

    except Exception as e:
        conn.rollback()
        print("Error adding vehicle to inventory:", e)

    finally:
        cur.close()


def remove_vehicle_from_inventory():
    conn = get_conn()
    cur = conn.cursor()

    try:
        inventory_id = input("Enter Inventory ID to remove: ").strip()

        cur.execute("""
            DELETE FROM inventory
            WHERE inventory_id = %s;
        """, (inventory_id,))

        conn.commit()
        print("Vehicle removed from inventory successfully.")

    except Exception as e:
        conn.rollback()
        print("Error removing vehicle from inventory:", e)

    finally:
        cur.close()


# ---------------- SALES FUNCTIONS ---------------- #
def view_sales():
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                s.sale_id,
                s.inventory_id,
                i.vin,
                b.brand_name,
                m.model_name,
                s.sale_date,
                s.sale_price,
                c.customer_id,
                c.first_name,
                c.last_name
            FROM sale s
            JOIN inventory i ON s.inventory_id = i.inventory_id
            JOIN vehicle v ON i.vin = v.vin
            JOIN model m ON v.model_id = m.model_id
            JOIN brand b ON m.brand_id = b.brand_id
            LEFT JOIN customer c ON s.customer_id = c.customer_id
            ORDER BY s.sale_id;
        """)

        print_table("Sales", cur.description, cur.fetchall())

    except Exception as e:
        conn.rollback()
        print("Error viewing sales:", e)

    finally:
        cur.close()


def record_sale():
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                i.inventory_id,
                i.vin,
                b.brand_name,
                m.model_name,
                i.price
            FROM inventory i
            JOIN vehicle v ON i.vin = v.vin
            JOIN model m ON v.model_id = m.model_id
            JOIN brand b ON m.brand_id = b.brand_id
            WHERE i.date_sold IS NULL
            ORDER BY i.inventory_id;
        """)

        print_table("Available Inventory", cur.description, cur.fetchall())

        inventory_id = input("Enter Inventory ID: ").strip()
        customer_id = input("Enter Customer ID: ").strip()
        sale_date = input("Enter Sale Date (YYYY-MM-DD): ").strip()
        sale_price = input("Enter Sale Price: ").strip()

        cur.execute("""
            INSERT INTO sale (inventory_id, customer_id, sale_date, sale_price)
            VALUES (%s, %s, %s, %s);
        """, (inventory_id, customer_id, sale_date, sale_price))

        cur.execute("""
            UPDATE inventory
            SET date_sold = %s
            WHERE inventory_id = %s;
        """, (sale_date, inventory_id))

        cur.execute("""
            UPDATE vehicle
            SET status = 'sold'
            WHERE vin = (
                SELECT vin
                FROM inventory
                WHERE inventory_id = %s
            );
        """, (inventory_id,))

        conn.commit()
        print("Sale recorded successfully.")

    except Exception as e:
        conn.rollback()
        print("Error recording sale:", e)

    finally:
        cur.close()


# ---------------- CUSTOMER FUNCTIONS ---------------- #
def view_customers():
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT customer_id, first_name, last_name, gender, income, phone, address
            FROM customer
            ORDER BY customer_id;
        """)

        print_table("Customers", cur.description, cur.fetchall())

    except Exception as e:
        conn.rollback()
        print("Error viewing customers:", e)

    finally:
        cur.close()


def search_customer():
    conn = get_conn()
    cur = conn.cursor()

    customer_id = input("Enter Customer ID: ").strip()

    try:
        cur.execute("""
            SELECT customer_id, first_name, last_name, gender, income, phone, address
            FROM customer
            WHERE customer_id = %s;
        """, (customer_id,))

        print_table("Customer Search Result", cur.description, cur.fetchall())

    except Exception as e:
        conn.rollback()
        print("Error searching customer:", e)

    finally:
        cur.close()


def add_customer():
    conn = get_conn()
    cur = conn.cursor()

    try:
        first_name = input("Enter First Name: ").strip()
        last_name = input("Enter Last Name: ").strip()
        gender = input("Enter Gender (M/F/O): ").strip()
        income = input("Enter Income: ").strip()
        phone = input("Enter Phone: ").strip()
        address = input("Enter Address: ").strip()

        cur.execute("""
            INSERT INTO customer (first_name, last_name, gender, income, phone, address)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (first_name, last_name, gender, income, phone, address))

        conn.commit()
        print("Customer added successfully.")

    except Exception as e:
        conn.rollback()
        print("Error adding customer:", e)

    finally:
        cur.close()


def update_customer():
    conn = get_conn()
    cur = conn.cursor()

    try:
        customer_id = input("Enter Customer ID to update: ").strip()

        cur.execute("""
            SELECT customer_id, first_name, last_name, gender, income, phone, address
            FROM customer
            WHERE customer_id = %s;
        """, (customer_id,))

        result = cur.fetchone()

        if not result:
            print("Customer not found.")
            return

        print("\nLeave blank to keep old value.")

        first_name = input(f"First Name ({result[1]}): ").strip()
        last_name = input(f"Last Name ({result[2]}): ").strip()
        gender = input(f"Gender ({result[3]}): ").strip()
        income = input(f"Income ({result[4]}): ").strip()
        phone = input(f"Phone ({result[5]}): ").strip()
        address = input(f"Address ({result[6]}): ").strip()

        first_name = result[1] if first_name == "" else first_name
        last_name = result[2] if last_name == "" else last_name
        gender = result[3] if gender == "" else gender
        income = result[4] if income == "" else income
        phone = result[5] if phone == "" else phone
        address = result[6] if address == "" else address

        cur.execute("""
            UPDATE customer
            SET first_name = %s,
                last_name = %s,
                gender = %s,
                income = %s,
                phone = %s,
                address = %s
            WHERE customer_id = %s;
        """, (first_name, last_name, gender, income, phone, address, customer_id))

        conn.commit()
        print("Customer updated successfully.")

    except Exception as e:
        conn.rollback()
        print("Error updating customer:", e)

    finally:
        cur.close()


def delete_customer():
    conn = get_conn()
    cur = conn.cursor()

    try:
        customer_id = input("Enter Customer ID to delete: ").strip()

        cur.execute("""
            DELETE FROM customer
            WHERE customer_id = %s;
        """, (customer_id,))

        conn.commit()
        print("Customer deleted successfully.")

    except Exception as e:
        conn.rollback()
        print("Error deleting customer:", e)

    finally:
        cur.close()


# ---------------- DEALER FUNCTIONS ---------------- #
def view_dealers():
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT dealer_id, dealer_name, address, city, dealer_state, phone
            FROM dealer
            ORDER BY dealer_id;
        """)

        print_table("Dealers", cur.description, cur.fetchall())

    except Exception as e:
        conn.rollback()
        print("Error viewing dealers:", e)

    finally:
        cur.close()


def search_dealer():
    conn = get_conn()
    cur = conn.cursor()

    dealer_id = input("Enter Dealer ID: ").strip()

    try:
        cur.execute("""
            SELECT dealer_id, dealer_name, address, city, dealer_state, phone
            FROM dealer
            WHERE dealer_id = %s;
        """, (dealer_id,))

        print_table("Dealer Search Result", cur.description, cur.fetchall())

    except Exception as e:
        conn.rollback()
        print("Error searching dealer:", e)

    finally:
        cur.close()


def add_dealer():
    conn = get_conn()
    cur = conn.cursor()

    try:
        dealer_name = input("Enter Dealer Name: ").strip()
        address = input("Enter Address: ").strip()
        city = input("Enter City: ").strip()
        dealer_state = input("Enter State: ").strip()
        phone = input("Enter Phone: ").strip()

        cur.execute("""
            INSERT INTO dealer (dealer_name, address, city, dealer_state, phone)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING dealer_id;
        """, (dealer_name, address, city, dealer_state, phone))

        new_id = cur.fetchone()[0]
        conn.commit()

        print(f"Dealer added successfully. New Dealer ID: {new_id}")

    except Exception as e:
        conn.rollback()
        print("Error adding dealer:", e)

    finally:
        cur.close()


def update_dealer():
    conn = get_conn()
    cur = conn.cursor()

    try:
        dealer_id = input("Enter Dealer ID to update: ").strip()

        cur.execute("""
            SELECT dealer_id, dealer_name, address, city, dealer_state, phone
            FROM dealer
            WHERE dealer_id = %s;
        """, (dealer_id,))

        result = cur.fetchone()

        if not result:
            print("Dealer not found.")
            return

        print("\nLeave blank to keep old value.")

        dealer_name = input(f"Dealer Name ({result[1]}): ").strip()
        address = input(f"Address ({result[2]}): ").strip()
        city = input(f"City ({result[3]}): ").strip()
        dealer_state = input(f"State ({result[4]}): ").strip()
        phone = input(f"Phone ({result[5]}): ").strip()

        dealer_name = result[1] if dealer_name == "" else dealer_name
        address = result[2] if address == "" else address
        city = result[3] if city == "" else city
        dealer_state = result[4] if dealer_state == "" else dealer_state
        phone = result[5] if phone == "" else phone

        cur.execute("""
            UPDATE dealer
            SET dealer_name = %s,
                address = %s,
                city = %s,
                dealer_state = %s,
                phone = %s
            WHERE dealer_id = %s;
        """, (dealer_name, address, city, dealer_state, phone, dealer_id))

        conn.commit()
        print("Dealer updated successfully.")

    except Exception as e:
        conn.rollback()
        print("Error updating dealer:", e)

    finally:
        cur.close()


def delete_dealer():
    conn = get_conn()
    cur = conn.cursor()

    try:
        dealer_id = input("Enter Dealer ID to delete: ").strip()

        cur.execute("""
            SELECT COUNT(*)
            FROM inventory
            WHERE dealer_id = %s;
        """, (dealer_id,))

        inventory_count = cur.fetchone()[0]

        if inventory_count > 0:
            print("This dealer still has inventory records. Delete inventory first.")
            return

        cur.execute("""
            DELETE FROM dealer
            WHERE dealer_id = %s;
        """, (dealer_id,))

        conn.commit()
        print("Dealer deleted successfully.")

    except Exception as e:
        conn.rollback()
        print("Error deleting dealer:", e)

    finally:
        cur.close()


# ---------------- REPORTS / ANALYTICS FUNCTIONS ---------------- #
def sales_trends_report():
    conn = get_conn()
    cur = conn.cursor()

    try:
        for period in ["YEAR", "MONTH", "WEEK"]:
            query = f"""
                SELECT
                    b.brand_name AS brand,
                    EXTRACT({period} FROM s.sale_date) AS {period.lower()},
                    c.gender AS buyer_gender,
                    CASE
                        WHEN c.income IS NULL THEN 'Unknown'
                        WHEN c.income < 50000 THEN 'Below 50k'
                        WHEN c.income BETWEEN 50000 AND 99999 THEN '50k-99k'
                        WHEN c.income BETWEEN 100000 AND 149999 THEN '100k-149k'
                        ELSE '150k+'
                    END AS income_range,
                    COUNT(*) AS total_units_sold,
                    SUM(s.sale_price) AS total_revenue
                FROM sale s
                JOIN inventory i ON s.inventory_id = i.inventory_id
                JOIN vehicle v ON i.vin = v.vin
                JOIN model m ON v.model_id = m.model_id
                JOIN brand b ON m.brand_id = b.brand_id
                JOIN customer c ON s.customer_id = c.customer_id
                WHERE s.sale_date >= CURRENT_DATE - INTERVAL '3 years'
                GROUP BY
                    b.brand_name,
                    EXTRACT({period} FROM s.sale_date),
                    c.gender,
                    income_range
                ORDER BY
                    EXTRACT({period} FROM s.sale_date),
                    b.brand_name,
                    c.gender,
                    income_range;
            """

            cur.execute(query)
            print_table(f"Sales Trends by {period}", cur.description, cur.fetchall())

    except Exception as e:
        conn.rollback()
        print("Error generating sales trends report:", e)

    finally:
        cur.close()


def defective_getrag_transmission_report():
    conn = get_conn()
    cur = conn.cursor()

    start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    end_date = input("Enter end date (YYYY-MM-DD): ").strip()
    plant_name = input("Enter plant name filter (empty for all plants): ").strip()

    try:
        if plant_name == "":
            cur.execute("""
                SELECT DISTINCT
                    v.vin,
                    b.brand_name,
                    m.model_name,
                    p.plant_name,
                    v.manufacture_date,
                    c.customer_id,
                    c.first_name,
                    c.last_name,
                    s.sale_date
                FROM supplier sup
                JOIN part part ON sup.supplier_id = part.supplier_id
                JOIN part_models pm ON part.part_id = pm.part_id
                JOIN model m ON pm.model_id = m.model_id
                JOIN brand b ON m.brand_id = b.brand_id
                JOIN vehicle v ON m.model_id = v.model_id
                JOIN plant p ON v.plant_id = p.plant_id
                JOIN inventory i ON v.vin = i.vin
                JOIN sale s ON i.inventory_id = s.inventory_id
                JOIN customer c ON s.customer_id = c.customer_id
                WHERE sup.supplier_name ILIKE 'Getrag'
                  AND part.part_name ILIKE '%%transmission%%'
                  AND v.manufacture_date BETWEEN %s AND %s
                ORDER BY v.vin;
            """, (start_date, end_date))
        else:
            cur.execute("""
                SELECT DISTINCT
                    v.vin,
                    b.brand_name,
                    m.model_name,
                    p.plant_name,
                    v.manufacture_date,
                    c.customer_id,
                    c.first_name,
                    c.last_name,
                    s.sale_date
                FROM supplier sup
                JOIN part part ON sup.supplier_id = part.supplier_id
                JOIN part_models pm ON part.part_id = pm.part_id
                JOIN model m ON pm.model_id = m.model_id
                JOIN brand b ON m.brand_id = b.brand_id
                JOIN vehicle v ON m.model_id = v.model_id
                JOIN plant p ON v.plant_id = p.plant_id
                JOIN inventory i ON v.vin = i.vin
                JOIN sale s ON i.inventory_id = s.inventory_id
                JOIN customer c ON s.customer_id = c.customer_id
                WHERE sup.supplier_name ILIKE 'Getrag'
                  AND part.part_name ILIKE '%%transmission%%'
                  AND v.manufacture_date BETWEEN %s AND %s
                  AND p.plant_name ILIKE %s
                ORDER BY v.vin;
            """, (start_date, end_date, f"%{plant_name}%"))

        print_table("Defective Getrag Transmissions", cur.description, cur.fetchall())

    except Exception as e:
        conn.rollback()
        print("Error generating defective transmission report:", e)

    finally:
        cur.close()


def top_2_brands_by_revenue():
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                b.brand_name,
                SUM(s.sale_price) AS total_revenue
            FROM sale s
            JOIN inventory i ON s.inventory_id = i.inventory_id
            JOIN vehicle v ON i.vin = v.vin
            JOIN model m ON v.model_id = m.model_id
            JOIN brand b ON m.brand_id = b.brand_id
            WHERE s.sale_date >= CURRENT_DATE - INTERVAL '1 year'
            GROUP BY b.brand_name
            ORDER BY total_revenue DESC
            LIMIT 2;
        """)

        print_table("Top 2 Brands by Revenue", cur.description, cur.fetchall())

    except Exception as e:
        conn.rollback()
        print("Error generating top revenue report:", e)

    finally:
        cur.close()


def top_2_brands_by_units():
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                b.brand_name,
                COUNT(*) AS units_sold
            FROM sale s
            JOIN inventory i ON s.inventory_id = i.inventory_id
            JOIN vehicle v ON i.vin = v.vin
            JOIN model m ON v.model_id = m.model_id
            JOIN brand b ON m.brand_id = b.brand_id
            WHERE s.sale_date >= CURRENT_DATE - INTERVAL '1 year'
            GROUP BY b.brand_name
            ORDER BY units_sold DESC
            LIMIT 2;
        """)

        print_table("Top 2 Brands by Units Sold", cur.description, cur.fetchall())

    except Exception as e:
        conn.rollback()
        print("Error generating top units report:", e)

    finally:
        cur.close()


def convertible_best_months():
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            WITH monthly_sales AS (
                SELECT
                    TO_CHAR(s.sale_date, 'Month') AS month_name,
                    EXTRACT(MONTH FROM s.sale_date) AS month_number,
                    COUNT(*) AS convertible_sales
                FROM sale s
                JOIN inventory i ON s.inventory_id = i.inventory_id
                JOIN vehicle v ON i.vin = v.vin
                JOIN model m ON v.model_id = m.model_id
                WHERE m.body_style ILIKE '%%convertible%%'
                GROUP BY month_name, month_number
            ),
            max_sales AS (
                SELECT MAX(convertible_sales) AS max_count
                FROM monthly_sales
            )
            SELECT
                month_name,
                convertible_sales
            FROM monthly_sales, max_sales
            WHERE convertible_sales = max_count
            ORDER BY month_number;
        """)

        print_table("Best Month(s) for Convertibles", cur.description, cur.fetchall())

    except Exception as e:
        conn.rollback()
        print("Error generating convertible report:", e)

    finally:
        cur.close()


def dealer_longest_inventory_duration():
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                d.dealer_id,
                d.dealer_name,
                ROUND(AVG(COALESCE(i.date_sold, CURRENT_DATE) - i.date_received), 2) AS avg_days_in_inventory,
                COUNT(*) AS vehicle_count
            FROM dealer d
            JOIN inventory i ON d.dealer_id = i.dealer_id
            GROUP BY d.dealer_id, d.dealer_name
            ORDER BY avg_days_in_inventory DESC;
        """)

        print_table("Dealers with Longest Avg Inventory Time", cur.description, cur.fetchall())

    except Exception as e:
        conn.rollback()
        print("Error generating inventory duration report:", e)

    finally:
        cur.close()


# ---------------- MENUS ---------------- #
def inventory_menu():
    while True:
        print("\n==== Inventory Menu ====")
        print("1. View Inventory")
        print("2. Search Vehicle by VIN")
        print("3. Add Vehicle to Inventory")
        print("4. Remove Vehicle from Inventory")
        print("5. Back to Main Menu")

        choice = input("Select option: ").strip()

        if choice == "1":
            view_inventory()
        elif choice == "2":
            search_vehicle()
        elif choice == "3":
            add_vehicle_to_inventory()
        elif choice == "4":
            remove_vehicle_from_inventory()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")


def sales_menu():
    while True:
        print("\n==== Sales Menu ====")
        print("1. View Sales")
        print("2. Record Sale")
        print("3. Back to Main Menu")

        choice = input("Select option: ").strip()

        if choice == "1":
            view_sales()
        elif choice == "2":
            record_sale()
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")


def customer_menu():
    while True:
        print("\n==== Customer Menu ====")
        print("1. View Customers")
        print("2. Search Customer by ID")
        print("3. Add Customer")
        print("4. Update Customer")
        print("5. Delete Customer")
        print("6. Back to Main Menu")

        choice = input("Select option: ").strip()

        if choice == "1":
            view_customers()
        elif choice == "2":
            search_customer()
        elif choice == "3":
            add_customer()
        elif choice == "4":
            update_customer()
        elif choice == "5":
            delete_customer()
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please try again.")


def dealer_menu():
    while True:
        print("\n==== Dealer Menu ====")
        print("1. View Dealers")
        print("2. Search Dealer by ID")
        print("3. Add Dealer")
        print("4. Update Dealer")
        print("5. Delete Dealer")
        print("6. Back to Main Menu")

        choice = input("Select option: ").strip()

        if choice == "1":
            view_dealers()
        elif choice == "2":
            search_dealer()
        elif choice == "3":
            add_dealer()
        elif choice == "4":
            update_dealer()
        elif choice == "5":
            delete_dealer()
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please try again.")


def reports_menu():
    while True:
        print("\n==== Reports / Analytics Menu ====")
        print("1. Sales Trends by Brand, Year, Month, Week, Gender, Income Range")
        print("2. Defective Getrag Transmission Report")
        print("3. Top 2 Brands by Dollar Amount Sold in Past Year")
        print("4. Top 2 Brands by Unit Sales in Past Year")
        print("5. Best Month(s) for Convertible Sales")
        print("6. Dealers with Longest Average Inventory Time")
        print("7. Back to Main Menu")

        choice = input("Select option: ").strip()

        if choice == "1":
            sales_trends_report()
        elif choice == "2":
            defective_getrag_transmission_report()
        elif choice == "3":
            top_2_brands_by_revenue()
        elif choice == "4":
            top_2_brands_by_units()
        elif choice == "5":
            convertible_best_months()
        elif choice == "6":
            dealer_longest_inventory_duration()
        elif choice == "7":
            break
        else:
            print("Invalid choice. Please try again.")


def main():
    global conn

    try:
        get_conn()
    except Exception as e:
        print("\nDatabase connection failed.")
        print("Error:", e)
        return

    while True:
        print("\n==== Car Dealership CLI ====")
        print("1. Open Inventory Menu")
        print("2. Open Sales Menu")
        print("3. Open Customer Menu")
        print("4. Open Dealer Menu")
        print("5. Open Reports / Analytics Menu")
        print("0. Close CLI")

        choice = input("Select option: ").strip()

        if choice == "1":
            inventory_menu()
        elif choice == "2":
            sales_menu()
        elif choice == "3":
            customer_menu()
        elif choice == "4":
            dealer_menu()
        elif choice == "5":
            reports_menu()
        elif choice == "0":
            print("\nExiting CLI.")
            break
        else:
            print("Invalid choice. Please try again.")

    if conn is not None and conn.closed == 0:
        conn.close()


if __name__ == "__main__":
    main()
