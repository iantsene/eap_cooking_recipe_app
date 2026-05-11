import sqlite3
import os
import sys

# Βρίσκει τη διαδρομή του φακέλου στον οποίο βρίσκεται το παρόν αρχείο (db.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class DatabaseConn:
    def __init__(self, db_name):
        # Ενώνει τον φάκελο του project με το όνομα της βάσης
        # Έτσι η διαδρομή γίνεται "απόλυτη" 
        # Get the directory where the executable is located (for packaged app)
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            application_path = os.path.dirname(sys.executable)
        else:
            # Running as script
            application_path = BASE_DIR

        self.db_path = os.path.join(application_path, db_name)
        self.conn = None
        self.cursor = None

    def __enter__(self):
        # Σύνδεση στη βάση χρησιμοποιώντας την πλήρη διαδρομή
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            self.conn.close()

    # Βοηθητικές μέθοδοι 
    def execute(self, query, params=()):
        return self.cursor.execute(query, params)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()
    
    # Νέες μέθοδοι για διαχείριση λιστών κατηγοριών, μονάδων και υλικών
    @staticmethod
    def get_all_categories():
        """Επιστρέφει όλες τις κατηγορίες από τη λίστα"""
        with DatabaseConn("recipe_database.db") as db:
            db.execute("SELECT name FROM categories_list ORDER BY name COLLATE NOCASE")
            return [row[0] for row in db.fetchall()]
    
    @staticmethod
    def add_category(category_name):
        """Προσθέτει νέα κατηγορία στη λίστα"""
        if not category_name or not category_name.strip():
            return False
        try:
            with DatabaseConn("recipe_database.db") as db:
                db.execute("INSERT INTO categories_list (name) VALUES (?)", (category_name.strip(),))
                return True
        except sqlite3.IntegrityError:
            return False  # Η κατηγορία υπάρχει ήδη
    
    @staticmethod
    def delete_category(category_name):
        """Διαγράφει κατηγορία από τη λίστα (μόνο αν δεν χρησιμοποιείται)"""
        with DatabaseConn("recipe_database.db") as db:
            # Πρώτα βρίσκουμε το ID της κατηγορίας
            db.execute("SELECT id FROM categories_list WHERE name = ?", (category_name,))
            cat_row = db.fetchone()
            if not cat_row:
                return False  # Η κατηγορία δεν υπάρχει
            
            category_id = cat_row[0]
            
            # Ελέγχουμε αν υπάρχει συνταγή με αυτό το category_id
            db.execute("SELECT COUNT(*) FROM recipes WHERE category_id = ?", (category_id,))
            count = db.fetchone()[0]
            
            if count > 0:
                return False  # Η κατηγορία χρησιμοποιείται
            
            # Διαγραφή της κατηγορίας
            db.execute("DELETE FROM categories_list WHERE id = ?", (category_id,))
            return True
        
    @staticmethod
    def get_all_units():
        """Επιστρέφει όλες τις μονάδες από τη λίστα"""
        with DatabaseConn("recipe_database.db") as db:
            db.execute("SELECT name FROM unit_list ORDER BY name COLLATE NOCASE")
            return [row[0] for row in db.fetchall()]
    
    @staticmethod
    def add_unit(unit_name):
        """Προσθέτει νέα μονάδα στη λίστα"""
        if not unit_name or not unit_name.strip():
            return False
        try:
            with DatabaseConn("recipe_database.db") as db:
                db.execute("INSERT INTO unit_list (name) VALUES (?)", (unit_name.strip(),))
                return True
        except sqlite3.IntegrityError:
            return False
    
    @staticmethod
    def delete_unit(unit_name):
        """Διαγράφει μονάδα από τη λίστα (μόνο αν δεν χρησιμοδείται)"""
        with DatabaseConn("recipe_database.db") as db:
            # Ελέγχουμε αν υπάρχει υλικό που χρησιμοποιεί αυτή τη μονάδα
            db.execute("SELECT COUNT(*) FROM ingredients WHERE unit = ?", (unit_name,))
            count = db.fetchone()[0]
            
            if count > 0:
                return False  # Η μονάδα χρησιμοποιείται
            
            # Διαγραφή της μονάδας
            db.execute("DELETE FROM unit_list WHERE name = ?", (unit_name,))
            return True
    
    @staticmethod
    def get_all_ingredients():
        """Επιστρέφει όλα τα υλικά από τη λίστα"""
        with DatabaseConn("recipe_database.db") as db:
            db.execute("SELECT name FROM ingredient_list ORDER BY name COLLATE NOCASE")
            return [row[0] for row in db.fetchall()]
    
    @staticmethod
    def add_ingredient(ingredient_name):
        """Προσθέτει νέο υλικό στη λίστα"""
        if not ingredient_name or not ingredient_name.strip():
            return False
        try:
            with DatabaseConn("recipe_database.db") as db:
                db.execute("INSERT INTO ingredient_list (name) VALUES (?)", (ingredient_name.strip(),))
                return True
        except sqlite3.IntegrityError:
            return False  # Το υλικό υπάρχει ήδη
    
    @staticmethod
    def delete_ingredient(ingredient_name):
        """Διαγράφει υλικό από τη λίστα (μόνο αν δεν χρησιμοποιείται)"""
        with DatabaseConn("recipe_database.db") as db:
            # Πρώτα βρίσκουμε αν υπάρχει συνταγή που χρησιμοποιεί αυτό το υλικό
            db.execute("SELECT COUNT(*) FROM ingredients WHERE name = ?", (ingredient_name,))
            count = db.fetchone()[0]
            
            if count > 0:
                return False  # Το υλικό χρησιμοποιείται
            
            # Διαγραφή του υλικού
            db.execute("DELETE FROM ingredient_list WHERE name = ?", (ingredient_name,))
            return True