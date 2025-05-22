import csv
import os
import re
from db_config import database_connection

class Customer:
    def __init__(self):
        self.conn = database_connection()
        print("Connected to database")


    def generate_customer_id(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT MAX(customer_id) FROM Customers")
            result = cursor.fetchone()

            if result[0] is None:
                next_id = 1
            else:
                max_id = int(result[0][4:])
                next_id = max_id + 1

            return f"CUST{next_id:04}"
        except Exception as e:
            print(f"Error generating customer ID: {e}")
            return None
        
        
    def is_valid_name(self, name):
        if isinstance(name, str) and name.strip() != "":
            if re.search(r'\d', name): 
                return False
            return True
        return False

    def is_valid_phone(self, phone):
        phone = phone.strip().replace(" ", "")
        if phone.startswith("+91"):
            phone = phone[3:]
        return phone.isdigit() and len(phone) == 10
    
    def format_phone(self, phone):
        phone = phone.strip().replace(" ", "")
        if phone.startswith("+91"):
            return "+91" + phone[3:]
        else:
            return "+91" + phone

    def add_customer(self, name, phone):

        if not self.is_valid_name(name):
            print("Name must be a non-empty string.")
            return
        if not self.is_valid_phone(phone):
            print("Phone number must be a valid 10-digit number.")
            return
        
        phone = self.format_phone(phone)
        try:
            customer_id = self.generate_customer_id()
            if customer_id is None:
                return
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO Customers (customer_id, name, phone) VALUES (?, ?, ?)",
                           (customer_id, name, phone))
            self.conn.commit()
            print(f"Customer with ID {customer_id} added successfully.")
        except Exception as e:
            if '23000' in str(e):  # SQL Server duplicate key error code
                print(f"Error adding customer: Customer ID {customer_id} already exists.")
            else:
                print(f"Error adding customer: {e}")
    

    def view_customers(self, page=1, page_size=10):
        try:
            cursor = self.conn.cursor()
            offset = (page - 1) * page_size
            cursor.execute("SELECT * FROM customers ORDER BY customer_id OFFSET ? ROWS FETCH NEXT ? ROWS ONLY", (offset, page_size))
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    print(row)
            else:
                print("No products on this page.")
        except Exception as e:
            print(f"Error viewing products: {e}")

    def update_customer(self, customer_id, name=None, phone=None):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name, phone FROM Customers WHERE customer_id=?", (customer_id))
            result = cursor.fetchone()
            if not result:
                print("Customer not found.")
                return
            
            current_name, current_phone = result
            new_name = name if name else current_name
            new_phone = phone if phone else current_phone

            if name is not None and (not isinstance(name, str) or not name.strip()):
                print("Name must be a non-empty string.")
                return

            if phone is not None and not self.is_valid_phone(phone):
                print("Phone number must be a valid 10-digit number.")
                return

            if phone:
                new_phone = self.format_phone(new_phone)

            cursor.execute("""
                UPDATE Customers
                SET name = ?, phone = ?
                WHERE customer_id = ?
            """, (new_name, new_phone, customer_id))
            self.conn.commit()
            print("Customer updated.")
        except Exception as e:
            print(f"Error updating customer: {e}")    

    def delete_customer(self, customer_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM Customers WHERE customer_id=?", (customer_id,))
            self.conn.commit()
            print("Customer deleted.")
        except Exception as e:
            print(f"Error deleting customer: {e}")

    def search_customer(self, keyword):
        try:
            cursor = self.conn.cursor()
            search_term = f"%{keyword}%"
            cursor.execute("""
                SELECT * FROM Customers
                WHERE customer_id LIKE ? OR name LIKE ? OR phone LIKE ?
            """, (search_term, search_term, search_term))
            results = cursor.fetchall()
            if results:
                for row in results:
                    print(row)
            else:
                print("No customers found.")
        except Exception as e:
            print(f"Error searching customer: {e}")

    def export_customers_csv(self):
        try:
            data_folder = r"C:\Users\nimmakayala.charan\Desktop\inventory_sales\data"

            if not os.path.exists(data_folder):
                os.makedirs(data_folder)

            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM Customers")
            rows = cursor.fetchall()

            file_path = os.path.join(data_folder, "customers.csv")

            with open(file_path, "w", newline='') as file:
                writer = csv.writer(file)
                writer.writerow([column[0] for column in cursor.description])  # headers
                writer.writerows(rows)
            print(f"Customers exported to {file_path}.")
        except Exception as e:
            print(f"Error exporting customers CSV: {e}")

    def import_customers_csv(self, filename):
        try:
            data_folder = r"C:\Users\nimmakayala.charan\Desktop\inventory_sales\data"

            if not os.path.exists(data_folder):
                os.makedirs(data_folder)

            file_path = os.path.join(data_folder, filename)

            cursor = self.conn.cursor()
            with open(file_path, newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    customer_id = row['customer_id']
                    name = row['name']
                    phone = row['phone']

                    if not self.is_valid_phone(phone):
                        print(f"Invalid phone number format for {name}. Skipping row.")
                        continue
                    cursor.execute("SELECT COUNT(*) FROM Customers WHERE customer_id = ?", (customer_id,))
                    if cursor.fetchone()[0] > 0:
                        print(f"Customer ID {customer_id} already exists. Skipping.")
                        continue

                    cursor.execute("""
                        INSERT INTO Customers (customer_id, name, phone)
                        VALUES (?, ?, ?)
                    """, (customer_id, name, phone))

            self.conn.commit()
            print(f"Customers imported from {file_path}.")
        except Exception as e:
            print(f"Error importing customers from CSV: {e}")

    
