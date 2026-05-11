from db import DatabaseConn  # Εισαγωγή της κλάσης για τη σύνδεση με τη βάση SQLite

# --- ΚΛΑΣΗ: ΚΑΤΗΓΟΡΙΕΣ ---
class Category:
    def __init__(self, id=None, name=None):
        self.id = id  # ID κατηγορίας
        self.name = name  # Όνομα κατηγορίας

    @staticmethod
    def get_or_create(name):  # Εύρεση ID ή δημιουργία νέας κατηγορίας
        if not name: return None  # Επιστροφή None αν δεν υπάρχει όνομα
        with DatabaseConn("recipe_database.db") as db:  # Σύνδεση με τη βάση
            db.execute("SELECT id FROM categories_list WHERE name = ?", (name,))  # Αναζήτηση ονόματος
            res = db.fetchone()  # Λήψη αποτελέσματος
            if res: return res[0]  # Αν υπάρχει, επιστροφή του ID
            
            # Δημιουργία νέας κατηγορίας
            db.execute("INSERT INTO categories_list (name) VALUES (?)", (name,))  # Αν όχι, δημιουργία νέας
            category_id = db.cursor.lastrowid
            return category_id

    @staticmethod
    def get_all():  # Λήψη όλων των ονομάτων κατηγοριών
        with DatabaseConn("recipe_database.db") as db:
            db.execute("SELECT name FROM categories_list")
            return [row[0] for row in db.fetchall()]

# --- ΚΛΑΣΗ: ΕΙΚΟΝΕΣ ---
class ImageModel:
    def __init__(self, id=None, path=None):
        self.id = id  # ID εικόνας
        self.path = path  # Διαδρομή αρχείου

    @staticmethod
    def save_image(path):  # Αποθήκευση διαδρομής εικόνας στη βάση
        if not path: return None  # Επιστροφή None αν δεν δόθηκε path
        with DatabaseConn("recipe_database.db") as db:
            db.execute("INSERT INTO images (path) VALUES (?)", (path,))  # Εισαγωγή στη βάση
            return db.cursor.lastrowid  # Επιστροφή του ID της εικόνας

# --- ΚΛΑΣΗ: ΥΛΙΚΑ ---
class Ingredient:
    def __init__(self, id=None, recipe_id=None, name="", quantity=0, unit="", notes=""):
        self.id = id  # ID υλικού
        self.recipe_id = recipe_id  # ID συνταγής
        self.name = name  # Όνομα υλικού
        self.quantity = quantity  # Ποσότητα
        self.unit = unit  # Μονάδα (π.χ. kg, ml)
        self.notes = notes  # Σημειώσεις (π.χ. "Στάδιο Προετοιμασίας")
        self.temp_id = None  # Για προσωρινή αποθήκευση

# --- ΚΛΑΣΗ: ΒΗΜΑΤΑ ---
class Step:
    def __init__(self, id=None, recipe_id=None, step_name="", sequence_order=0, step_text="", duration_in_minutes=0):
        self.id = id  # ID βήματος
        self.recipe_id = recipe_id  # ID συνταγής
        self.step_name = step_name  # Τίτλος βήματος
        self.sequence_order = sequence_order  # Σειρά εκτέλεσης
        self.step_text = step_text  # Περιγραφή βήματος
        self.duration_in_minutes = duration_in_minutes  # Χρόνος βήματος
        self.allocations = []  # Λίστα υλικών που χρησιμοποιεί το βήμα

# --- ΚΛΑΣΗ: ΣΥΝΤΑΓΗ ---
class Recipe:
    def __init__(self, id=None, name="", category="", difficulty="", total_time_minutes=0, image_path=None):
        self.id = id  # ID συνταγής
        self.name = name  # Όνομα συνταγής
        self.category = category  # Όνομα κατηγορίας (κείμενο)
        self.category_id = None  # ID κατηγορίας (για αποθήκευση)
        self.difficulty = difficulty  # Δυσκολία
        self.total_time_minutes = total_time_minutes  # Συνολικός χρόνος
        self.image_path = image_path  # Διαδρομή εικόνας
        self.image_id = None  # ID εικόνας (για αποθήκευση)
        self.ingredients = []  # Λίστα αντικειμένων Ingredient
        self.steps = []  # Λίστα αντικειμένων Step

    def save(self):
        with DatabaseConn("recipe_database.db") as db:
            if self.id:  # Update existing recipe
                # ALSO update the image_path column for direct access
                db.execute("""UPDATE recipes 
                            SET name=?, category_id=?, difficulty=?, total_time_minutes=?, image_id=?, image_path=? 
                            WHERE id=?""", 
                        (self.name, self.category_id, self.difficulty, self.total_time_minutes, self.image_id, self.image_path, self.id))
                db.execute("DELETE FROM ingredients WHERE recipe_id=?", (self.id,))
                db.execute("DELETE FROM steps WHERE recipe_id=?", (self.id,))
            else:  # Insert new recipe
                db.execute("""INSERT INTO recipes (name, category_id, difficulty, total_time_minutes, image_id, image_path) 
                            VALUES (?, ?, ?, ?, ?, ?)""", 
                        (self.name, self.category_id, self.difficulty, self.total_time_minutes, self.image_id, self.image_path))
                self.id = db.cursor.lastrowid

            # Save ingredients
            for ing in self.ingredients:
                db.execute("INSERT INTO ingredients (recipe_id, name, quantity, unit, notes) VALUES (?,?,?,?,?)", 
                        (self.id, ing.name, ing.quantity, ing.unit, getattr(ing, 'notes', '')))
                ing.id = db.cursor.lastrowid
                
                try:
                    db.execute("INSERT OR IGNORE INTO ingredient_list (name) VALUES (?)", (ing.name,))
                except:
                    pass
                
            # Save steps
            for idx, st in enumerate(self.steps, 1):
                st.sequence_order = idx
                db.execute("""INSERT INTO steps (recipe_id, step_name, sequence_order, step_text, duration_in_minutes) 
                            VALUES (?,?,?,?,?)""",
                        (self.id, st.step_name, st.sequence_order, st.step_text, st.duration_in_minutes))
                st.id = db.cursor.lastrowid
                
                # Save step ingredients
                for a in getattr(st, 'allocations', []):
                    ing_id = None
                    ingredient_name = a.get('ingredient_name', '')
                    
                    # Try to find by name first (more reliable than temp_id)
                    for ing in self.ingredients:
                        if ing.name == ingredient_name:
                            ing_id = ing.id
                            break
                    
                    # If not found by name, try by temp_id (fallback)
                    if not ing_id:
                        for ing in self.ingredients:
                            if hasattr(ing, 'temp_id') and ing.temp_id == a.get('temp_id'):
                                ing_id = ing.id
                                break
                    
                    if ing_id:
                        db.execute("""INSERT INTO step_ingredients (ingredient_id, step_id, ingredient_name, quantity, unit, notes) 
                                VALUES (?,?,?,?,?,?)""",
                                (ing_id, st.id, a.get('ingredient_name'), a.get('quantity'), a.get('unit'), a.get('notes', '')))

    @staticmethod
    def get_all_recipes():  # Λήψη όλων των συνταγών με JOIN για κατηγορία/εικόνα
        with DatabaseConn("recipe_database.db") as db:
            db.execute("""SELECT r.id, r.name, c.name, r.difficulty, r.total_time_minutes, i.path 
                          FROM recipes r LEFT JOIN categories_list c ON r.category_id = c.id
                          LEFT JOIN images i ON r.image_id = i.id""")
            return db.fetchall()  # Επιστροφή λίστας αποτελεσμάτων


    @staticmethod
    def get_recipe_by_id(recipe_id):
        with DatabaseConn("recipe_database.db") as db:
            # Include image_path from recipes table as fallback
            db.execute("""SELECT r.id, r.name, c.name, r.difficulty, r.total_time_minutes, 
                                COALESCE(i.path, r.image_path) as image_path
                        FROM recipes r 
                        LEFT JOIN categories_list c ON r.category_id = c.id
                        LEFT JOIN images i ON r.image_id = i.id 
                        WHERE r.id = ?""", (recipe_id,))
            row = db.fetchone()
            if not row: 
                return None
            
            recipe = Recipe(
                id=row[0], 
                name=row[1], 
                category=row[2], 
                difficulty=row[3], 
                total_time_minutes=row[4]
            )
            
            # Set the image path from either source
            recipe.image_path = row[5]
            
            # Load ingredients
            db.execute("SELECT id, name, quantity, unit, notes FROM ingredients WHERE recipe_id = ?", (recipe_id,))
            recipe.ingredients = [Ingredient(r[0], recipe_id, r[1], r[2], r[3], r[4]) for r in db.fetchall()]
            
            # Load steps
            db.execute("SELECT id, step_name, sequence_order, step_text, duration_in_minutes FROM steps WHERE recipe_id = ? ORDER BY sequence_order", (recipe_id,))
            for s_row in db.fetchall():
                st = Step(s_row[0], recipe_id, s_row[1], s_row[2], s_row[3], s_row[4])
                db.execute("""SELECT si.ingredient_id, i.name, si.quantity, si.unit, si.notes 
                            FROM step_ingredients si 
                            JOIN ingredients i ON si.ingredient_id = i.id 
                            WHERE si.step_id = ?""", (st.id,))
                st.allocations = [{'ingredient_id': ir[0], 'ingredient_name': ir[1], 'quantity': ir[2], 'unit': ir[3], 'notes': ir[4]} for ir in db.fetchall()]
                st.step_ingredients = st.allocations
                recipe.steps.append(st)
            
            return recipe

    @staticmethod
    def delete_by_id(recipe_id):  # Διαγραφή συνταγής
        with DatabaseConn("recipe_database.db") as db:
            db.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))  # Διαγραφή (τα υπόλοιπα διαγράφονται μέσω CASCADE)
            return db.cursor.rowcount > 0