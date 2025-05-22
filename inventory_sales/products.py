import csv
import os
import re
from db_config import database_connection

class Product:
    def __init__(self):
        self.conn = database_connection()
        print("Connected to database")

    
    def is_valid_name(self, name):
        pattern = r'^[A-Za-z\s]+$'
        if isinstance(name, str) and name.strip() != "":
            if re.match(pattern, name.strip()):
                return True
            else:
                return False
        return False   

    def is_product_exists(self, product_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Products WHERE Product_id = ?", (product_id,))
            result = cursor.fetchone()[0]
            return result > 0 
        except Exception as e:
            print(f"Error checking product existence: {e}")
            return False

    def generate_product_id(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT MAX(product_id) FROM products")
            result = cursor.fetchone()

            if result[0] is None:
                next_id = 1
            else:
                max_id = int(result[0][4:])
                next_id = max_id + 1

            return f"PROD{next_id:04}"
        except Exception as e:
            print(f"Error generating customer ID: {e}")
            return None

    def add_product(self, name, category, price, quantity):

        try:
            product_id = self.generate_product_id()
            if product_id is None:
                return
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO Products (Product_id, Name, category, price, quantity)
                VALUES (?, ?, ?, ?, ?)
            """, (product_id, name, category, price, quantity))
            self.conn.commit()
            print(f"Product {name} added successfully with {product_id}.")
        except Exception as e:
            print(f"Error adding product: {e}")

    def view_products(self, page=1, page_size=10):
        try:
            cursor = self.conn.cursor()
            offset = (page - 1) * page_size
            cursor.execute("SELECT * FROM Products ORDER BY product_id OFFSET ? ROWS FETCH NEXT ? ROWS ONLY", (offset, page_size))
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    print(row)
            else:
                print("No products on this page.")
        except Exception as e:
            print(f"Error viewing products: {e}")
    
    def update_product_details(self, product_id, name=None, category=None, price=None, quantity=None):
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("SELECT Name, Category, Price, Quantity FROM Products WHERE Product_id=?", (product_id,))
            result = cursor.fetchone()

            if not result:
                print("Product not found.")
                return
            current_name, current_category, current_price, current_quantity = result

            new_name = name if name else current_name
            new_category = category if category else current_category
            new_price = price if price  else current_price
            new_quantity = quantity if quantity  else current_quantity

            if name is not None and (not isinstance(name, str) or not name.strip()):
                print("Name must be a non-empty string.")
                return
        
            if category is not None and (not isinstance(category, str) or not category.strip()):
                print("Category must be a non-empty string.")
                return

            if price is not None and (not isinstance(price, (int, float)) or price <= 0):
                print("Price must be a positive number.")
                return

            if quantity is not None and (not isinstance(quantity, int) or quantity < 0):
                print("Quantity must be a non-negative integer.")
                return

            cursor.execute("""
                UPDATE Products
                SET Name = ?, Category = ?, Price = ?, Quantity = ?
                WHERE Product_id = ?
            """, (new_name, new_category, new_price, new_quantity, product_id))

            self.conn.commit()

        except Exception as e:
            print(f"Error updating product: {e}")


    def delete_product(self, product_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM Products WHERE product_id=?", (product_id,))
            self.conn.commit()
        except Exception as e:
            print(f"Error deleting product: {e}")

    def search_product(self, keyword):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM Products
                WHERE Name LIKE ? OR category LIKE ?
            """, (f"%{keyword}%", f"%{keyword}%"))
            results = cursor.fetchall()
            if results:
                for row in results:
                    print(row)
            else:
                print("No matching products found.")
        except Exception as e:
            print(f"Error searching product: {e}")

    def export_products_csv(self):
        try:
            data_folder = r"C:\Users\nimmakayala.charan\Desktop\inventory_sales\data"

            if not os.path.exists(data_folder):
                os.makedirs(data_folder)

            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM Products")
            rows = cursor.fetchall()

            file_path = os.path.join(data_folder, "products.csv")

            with open(file_path, "w", newline='') as file:
                writer = csv.writer(file)
                writer.writerow([column[0] for column in cursor.description])
                writer.writerows(rows)
            print(f"Products exported to {file_path}.")
        except Exception as e:
            print(f"Error exporting products CSV: {e}")

    def import_products_csv(self, filename):
        try:
            data_folder = r"C:\Users\nimmakayala.charan\Desktop\inventory_sales\data"

            if not os.path.exists(data_folder):
                os.makedirs(data_folder)

            file_path = os.path.join(data_folder, filename)

            cursor = self.conn.cursor()
            with open(file_path, newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    cursor.execute("""
                        INSERT INTO Products (product_id, Name, category, quantity, price)
                        VALUES (?, ?, ?, ?, ?)
                    """, (row['product_id'], row['Name'], row['category'], int(row['quantity']), float(row['price'])))
            self.conn.commit()
            print(f"Products imported from {file_path}.")
        except Exception as e:
            print(f"Error importing products from CSV: {e}")


    

