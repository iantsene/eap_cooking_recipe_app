# Εισαγωγή των απαραίτητων βιβλιοθηκών
from db import DatabaseConn  # Εισαγωγή της κλάσης για σύνδεση με τη βάση δεδομένων
from models import Recipe, Ingredient, Step  # Εισαγωγή των μοντέλων δεδομένων
import tkinter as tk  # Βιβλιοθήκη για τη δημιουργία γραφικού περιβάλλοντος
from tkinter import ttk, messagebox  # Επιπλέον widgets και μηνύματα ειδοποίησης

# Δημιουργία των πινάκων της βάσης δεδομένων αν δεν υπάρχουν
# Χρήση context manager (with) για αυτόματο κλείσιμο της σύνδεσης
with DatabaseConn("recipe_database.db") as rcp_db:
    # SQL εντολή για δημιουργία πίνακα recipes (συνταγές)
    create_recipe_table = """CREATE TABLE IF NOT EXISTS recipes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        difficulty TEXT,
        total_time_minutes INTEGER
    )"""
    # Επεξήγηση των παραπάνω πεδίων create_recipe_table
    # Μοναδικό αναγνωριστικό, αυτόματη αρίθμηση
    # Όνομα συνταγής
    # Κατηγορία (π.χ. ορεκτικό, κυρίως πιάτο)
    # Βαθμός δυσκολίας (Easy, Medium, Hard)
    # Συνολικός χρόνος σε λεπτά
    
    # SQL εντολή για δημιουργία πίνακα ingredients (συστατικά)
    create_ingredients_table = """CREATE TABLE IF NOT EXISTS ingredients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipe_id INTEGER,
        name TEXT,
        quantity REAL,
        unit TEXT,
        notes TEXT,
        FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
    )"""
    # Επεξήγηση των παραπάνω πεδίων create_ingredients_table
    # Μοναδικό αναγνωριστικό
    # Αναφορά στη συνταγή (foreign key)
    # Όνομα συστατικού
    # Ποσότητα (δεκαδικός αριθμός)
    # Μονάδα μέτρησης (π.χ. kg, κουταλιές)
    # Σημειώσεις (π.χ. προαιρετικό, προτίμηση)
    # Αν διαγραφεί η συνταγή, διαγράφονται και τα συστατικά
    
    # SQL εντολή για δημιουργία πίνακα steps (βήματα εκτέλεσης)
    create_steps_table = """CREATE TABLE IF NOT EXISTS steps(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipe_id INTEGER,
        step_name TEXT,
        sequence_order INTEGER,
        step_text TEXT,
        duration_in_minutes INTEGER,
        FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
    )"""
    # Επεξήγηση των παραπάνω πεδίων create_steps_table
    # Μοναδικό αναγνωριστικό
    # Αναφορά στη συνταγή
    # Τίτλος βήματος
    # Σειρά εκτέλεσης (1ο, 2ο, κλπ)
    # Περιγραφή του βήματος
    # Διάρκεια του βήματος σε λεπτά
    
    # Εκτέλεση των SQL εντολών για δημιουργία των πινάκων
    rcp_db.execute(create_recipe_table)
    rcp_db.execute(create_ingredients_table)
    rcp_db.execute(create_steps_table)


# Κλάση για τη φόρμα προσθήκης/επεξεργασίας συστατικού
class IngredientFormPage:
    def __init__(self, parent_form, index=None, ingredient=None):
        """
        Αρχικοποίηση της φόρμας συστατικού
        parent_form: η γονική φόρμα (RecipeFormPage)
        index: αν υπάρχει, σημαίνει ότι είμαστε σε λειτουργία επεξεργασίας
        ingredient: το συστατικό προς επεξεργασία (αν υπάρχει)
        """
        self.parent_form = parent_form  # Αποθήκευση αναφοράς στη γονική φόρμα
        self.index = index              # None = προσθήκη, int = επεξεργασία

        # Δημιουργία νέου παραθύρου (Toplevel)
        self.window = tk.Toplevel()
        self.window.title("Επεξεργασία Συστατικού" if index is not None else "Προσθήκη Συστατικού")

        # Δημιουργία πεδίων εισαγωγής δεδομένων
        # Πεδίο για το όνομα του συστατικού
        ttk.Label(self.window, text="Όνομα:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(self.window, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Πεδίο για την ποσότητα
        ttk.Label(self.window, text="Ποσότητα:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.quantity_entry = ttk.Entry(self.window, width=30)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        # Πεδίο για τη μονάδα μέτρησης
        ttk.Label(self.window, text="Μονάδα:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.unit_entry = ttk.Entry(self.window, width=30)
        self.unit_entry.grid(row=2, column=1, padx=5, pady=5)

        # Πεδίο για σημειώσεις
        ttk.Label(self.window, text="Σημειώσεις:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.notes_entry = ttk.Entry(self.window, width=30)
        self.notes_entry.grid(row=3, column=1, padx=5, pady=5)

        # Κουμπί αποθήκευσης (το κείμενο αλλάζει ανάλογα με τη λειτουργία)
        label = "Αποθήκευση Αλλαγών" if index is not None else "Προσθήκη Συστατικού"
        ttk.Button(self.window, text=label, command=self.save).grid(
            row=4, column=0, columnspan=2, pady=10
        )

        # Αν είμαστε σε λειτουργία επεξεργασίας, συμπληρώνουμε τα πεδία με τα υπάρχοντα δεδομένα
        if ingredient:
            self.name_entry.insert(0, ingredient.name or "")
            self.quantity_entry.insert(0, ingredient.quantity or "")
            self.unit_entry.insert(0, ingredient.unit or "")
            self.notes_entry.insert(0, ingredient.notes or "")

    def save(self):
        """Αποθήκευση ή ενημέρωση του συστατικού"""
        # Λήψη και καθαρισμός των τιμών από τα πεδία
        name = self.name_entry.get().strip()
        notes = self.notes_entry.get().strip() or None  # Αν κενό, αποθηκεύουμε None
        unit = self.unit_entry.get().strip() or None

        # Έλεγχος εγκυρότητας: το όνομα είναι υποχρεωτικό
        if not name:
            print("Το όνομα του συστατικού είναι υποχρεωτικό.")
            return
        
        # Έλεγχος εγκυρότητας: η ποσότητα πρέπει να είναι θετικός αριθμός
        try:
            quantity = float(self.quantity_entry.get())
            if quantity <= 0:
                print("Η ποσότητα πρέπει να είναι θετική.")
                return
        except ValueError:
            print("Παρακαλώ εισάγετε έναν έγκυρο αριθμό για την ποσότητα.")
            return

        # Δημιουργία νέου αντικειμένου Ingredient
        ingredient = Ingredient(name=name, quantity=quantity, unit=unit, notes=notes)

        # Ενημέρωση της λίστας στη γονική φόρμα
        if self.index is not None:
            self.parent_form.ingredients[self.index] = ingredient  # Αντικατάσταση υπάρχοντος
        else:
            self.parent_form.ingredients.append(ingredient)        # Προσθήκη νέου

        # Ανανέωση της λίστας εμφάνισης στη γονική φόρμα
        self.parent_form.refresh_ingredients_list()
        # Κλείσιμο του παραθύρου
        self.window.destroy()


# Κλάση για τη φόρμα προσθήκης/επεξεργασίας βήματος
class StepFormPage:
    def __init__(self, parent_form, index=None, step=None):
        """
        Αρχικοποίηση της φόρμας βήματος
        parent_form: η γονική φόρμα (RecipeFormPage)
        index: αν υπάρχει, σημαίνει ότι είμαστε σε λειτουργία επεξεργασίας
        step: το βήμα προς επεξεργασία (αν υπάρχει)
        """
        self.parent_form = parent_form
        self.index = index

        self.window = tk.Toplevel()
        self.window.title("Επεξεργασία Βήματος" if index is not None else "Προσθήκη Βήματος")

        # Υπολογισμός του αριθμού βήματος για εμφάνιση
        step_number = (index + 1) if index is not None else len(self.parent_form.steps) + 1
        ttk.Label(self.window, text=f"Βήμα {step_number}", font=("", 10, "bold")).grid(
            row=0, column=0, columnspan=2, pady=5
        )

        # Πεδίο για τον τίτλο του βήματος
        ttk.Label(self.window, text="Τίτλος Βήματος:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.step_name_entry = ttk.Entry(self.window, width=30)
        self.step_name_entry.grid(row=1, column=1, padx=5, pady=5)

        # Πεδίο για την περιγραφή του βήματος
        ttk.Label(self.window, text="Περιγραφή:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.step_text_entry = ttk.Entry(self.window, width=30)
        self.step_text_entry.grid(row=2, column=1, padx=5, pady=5)

        # Πεδίο για τη διάρκεια του βήματος
        ttk.Label(self.window, text="Διάρκεια (λεπτά):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.duration_entry = ttk.Entry(self.window, width=30)
        self.duration_entry.grid(row=3, column=1, padx=5, pady=5)

        # Κουμπί αποθήκευσης
        label = "Αποθήκευση Αλλαγών" if index is not None else "Προσθήκη Βήματος"
        ttk.Button(self.window, text=label, command=self.save).grid(
            row=4, column=0, columnspan=2, pady=10
        )

        # Συμπλήρωση πεδίων αν είμαστε σε λειτουργία επεξεργασίας
        if step:
            self.step_name_entry.insert(0, step.step_name or "")
            self.step_text_entry.insert(0, step.step_text or "")
            self.duration_entry.insert(0, step.duration_in_minutes or "")

    def save(self):
        """Αποθήκευση ή ενημέρωση του βήματος"""
        # Λήψη και καθαρισμός των τιμών
        step_name = self.step_name_entry.get().strip()
        step_text = self.step_text_entry.get().strip()

        # Έλεγχος εγκυρότητας: τίτλος και περιγραφή είναι υποχρεωτικά
        if not step_name or not step_text:
            print("Ο τίτλος και η περιγραφή του βήματος είναι υποχρεωτικά.")
            return
        
        # Έλεγχος εγκυρότητας: η διάρκεια πρέπει να είναι μη αρνητικός ακέραιος
        try:
            duration = int(self.duration_entry.get())
            if duration < 0:
                print("Η διάρκεια δεν μπορεί να είναι αρνητική.")
                return
        except ValueError:
            print("Παρακαλώ εισάγετε έναν έγκυρο ακέραιο αριθμό για τη διάρκεια.")
            return

        # Υπολογισμός της σειράς του βήματος (sequence order)
        sequence_order = (self.index + 1) if self.index is not None else len(self.parent_form.steps) + 1
        
        # Δημιουργία νέου αντικειμένου Step
        step = Step(
            step_name=step_name,
            step_text=step_text,
            duration_in_minutes=duration,
            sequence_order=sequence_order
        )

        # Ενημέρωση της λίστας στη γονική φόρμα
        if self.index is not None:
            self.parent_form.steps[self.index] = step   # Αντικατάσταση υπάρχοντος
        else:
            self.parent_form.steps.append(step)         # Προσθήκη νέου

        # Ανανέωση της λίστας εμφάνισης και κλείσιμο παραθύρου
        self.parent_form.refresh_steps_list()
        self.window.destroy()


# Κλάση για την κύρια φόρμα προσθήκης/επεξεργασίας συνταγής
class RecipeFormPage:
    def __init__(self, parent_app, recipe_id=None):
        """
        Αρχικοποίηση της φόρμας συνταγής
        parent_app: η κύρια εφαρμογή (RecipeApp)
        recipe_id: αν υπάρχει, φορτώνουμε υπάρχουσα συνταγή για επεξεργασία
        """
        self.parent_app = parent_app
        self.recipe_id = recipe_id
        self.ingredients = []   # Λίστα με αντικείμενα Ingredient
        self.steps = []         # Λίστα με αντικείμενα Step

        # Δημιουργία νέου παραθύρου
        self.window = tk.Toplevel()
        self.window.title("Επεξεργασία Συνταγής" if recipe_id else "Προσθήκη Συνταγής")

        # --- Πεδία της συνταγής ---
        # Όνομα συνταγής
        ttk.Label(self.window, text="Όνομα Συνταγής:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(self.window, width=30)
        self.name_entry.grid(row=0, column=1, sticky=tk.E, padx=5, pady=5)

        # Κατηγορία
        ttk.Label(self.window, text="Κατηγορία:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.category_entry = ttk.Entry(self.window, width=30)
        self.category_entry.grid(row=1, column=1, sticky=tk.E, padx=5, pady=5)

        # Βαθμός δυσκολίας - Combobox (dropdown menu) για επιλογή
        ttk.Label(self.window, text="Δυσκολία:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.difficulty_var = tk.StringVar()
        self.difficulty_combo = ttk.Combobox(self.window, textvariable=self.difficulty_var, 
                                             values=["Εύκολη", "Μέτρια", "Δύσκολη"], 
                                             state="readonly", width=27)
        self.difficulty_combo.grid(row=2, column=1, sticky=tk.E, padx=5, pady=5)
        self.difficulty_combo.set("Επιλέξτε δυσκολία...")  # Κείμενο προεπιλογής

        # Συνολικός χρόνος
        ttk.Label(self.window, text="Συνολικός Χρόνος (λεπτά):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.total_time_entry = ttk.Entry(self.window, width=30)
        self.total_time_entry.grid(row=3, column=1, sticky=tk.E, padx=5, pady=5)

        # --- Ενότητα Συστατικών ---
        ttk.Label(self.window, text="Συστατικά:", font=("", 10, "bold")).grid(
            row=4, column=0, sticky=tk.W, padx=5, pady=(10, 0)
        )
        # Κουμπί προσθήκης συστατικού
        ttk.Button(self.window, text="+ Προσθήκη Συστατικού", command=self.open_ingredient_form).grid(
            row=4, column=1, sticky=tk.E, padx=5
        )
        
        # Listbox για εμφάνιση των συστατικών
        self.ingredients_listbox = tk.Listbox(self.window, width=50, height=5)
        self.ingredients_listbox.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        # Κουμπιά επεξεργασίας/διαγραφής για συστατικά
        ing_btn_frame = ttk.Frame(self.window)
        ing_btn_frame.grid(row=6, column=0, columnspan=2)
        ttk.Button(ing_btn_frame, text="Επεξεργασία Συστατικού",   command=self.open_edit_ingredient_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(ing_btn_frame, text="Διαγραφή Συστατικού", command=self.delete_ingredient).pack(side=tk.LEFT, padx=5)

        # --- Ενότητα Βημάτων ---
        ttk.Label(self.window, text="Βήματα:", font=("", 10, "bold")).grid(
            row=7, column=0, sticky=tk.W, padx=5, pady=(10, 0)
        )

        # Κουμπί προσθήκης βήματος
        ttk.Button(self.window, text="+ Προσθήκη Βήματος", command=self.open_step_form).grid(
            row=8, column=1, sticky=tk.E, padx=5
        )
        
        # Listbox για εμφάνιση των βημάτων
        self.steps_listbox = tk.Listbox(self.window, width=50, height=5)
        self.steps_listbox.grid(row=9, column=0, columnspan=2, padx=5, pady=5)

        # Κουμπιά επεξεργασίας/διαγραφής για βήματα
        step_btn_frame = ttk.Frame(self.window)
        step_btn_frame.grid(row=10, column=0, columnspan=2)
        ttk.Button(step_btn_frame, text="Επεξεργασία Βήματος",   command=self.open_edit_step_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(step_btn_frame, text="Διαγραφή Βήματος", command=self.delete_step).pack(side=tk.LEFT, padx=5)

        # --- Κουμπί αποθήκευσης ---
        label = "Αποθήκευση Αλλαγών" if recipe_id else "Προσθήκη Συνταγής"
        ttk.Button(self.window, text=label, command=self.save).grid(
            row=11, column=0, columnspan=2, pady=10
        )

        # Αν έχουμε recipe_id, φορτώνουμε τα δεδομένα της υπάρχουσας συνταγής
        if recipe_id:
            self._prefill(recipe_id)

    def open_ingredient_form(self):
        """Άνοιγμα φόρμας για προσθήκη νέου συστατικού"""
        IngredientFormPage(parent_form=self)

    def open_step_form(self):
        """Άνοιγμα φόρμας για προσθήκη νέου βήματος"""
        StepFormPage(parent_form=self)

    def refresh_ingredients_list(self):
        """Ανανέωση της λίστας εμφάνισης των συστατικών"""
        self.ingredients_listbox.delete(0, tk.END)  # Καθαρισμός υπάρχουσας λίστας
        for ing in self.ingredients:
            self.ingredients_listbox.insert(tk.END, str(ing))  # Χρήση της μεθόδου __str__ του Ingredient

    def refresh_steps_list(self):
        """Ανανέωση της λίστας εμφάνισης των βημάτων"""
        self.steps_listbox.delete(0, tk.END)
        for step in self.steps:
            self.steps_listbox.insert(tk.END, str(step))  # Χρήση της μεθόδου __str__ του Step

    def _prefill(self, recipe_id):
        """Φόρτωση δεδομένων υπάρχουσας συνταγής για επεξεργασία"""
        # Λήψη της συνταγής με όλες τις λεπτομέρειες (συστατικά και βήματα)
        recipe = Recipe.get_recipe_with_details(recipe_id)
        if not recipe:
            return
        
        # Συμπλήρωση των πεδίων της συνταγής
        self.name_entry.insert(0, recipe.name)
        self.category_entry.insert(0, recipe.category)
        
        # Επεξεργασία της δυσκολίας (αν είναι αριθμός, τον μετατρέπουμε σε κείμενο)
        difficulty_value = recipe.difficulty
        if isinstance(difficulty_value, int):
            # Αν η βάση αποθηκεύει αριθμούς 1-5, τους μετατρέπουμε σε κείμενο
            difficulty_map = {1: "Easy", 2: "Easy", 3: "Medium", 4: "Hard", 5: "Hard"}
            difficulty_value = difficulty_map.get(difficulty_value, "Medium")
        
        # Επιλογή της τιμής στο combobox
        if difficulty_value in ["Easy", "Medium", "Hard"]:
            self.difficulty_combo.set(difficulty_value)
        else:
            self.difficulty_combo.set("Medium")  # Προεπιλεγμένη τιμή
        
        # Συμπλήρωση χρόνου και λιστών
        self.total_time_entry.insert(0, recipe.total_time_minutes)
        self.ingredients = recipe.ingredients
        self.steps = recipe.steps
        self.refresh_ingredients_list()
        self.refresh_steps_list()

    def save(self):
        """Αποθήκευση της συνταγής στη βάση δεδομένων"""
        # Έλεγχος εγκυρότητας: όνομα υποχρεωτικό
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Σφάλμα", "Το όνομα της συνταγής είναι υποχρεωτικό.")
            return

        # Έλεγχος εγκυρότητας: επιλογή δυσκολίας
        difficulty = self.difficulty_var.get()
        if difficulty not in ["Ευκολη", "Μέτρια", "Δύσκολη"]:
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε έγκυρο βαθμό δυσκολίας.")
            return

        # Έλεγχος εγκυρότητας: συνολικός χρόνος
        try:
            total_time = int(self.total_time_entry.get().strip())
            if total_time <= 0:
                messagebox.showerror("Σφάλμα", "Ο συνολικός χρόνος πρέπει να είναι θετικός αριθμός.")
                return
        except ValueError:
            messagebox.showerror("Σφάλμα", "Ο συνολικός χρόνος πρέπει να είναι έγκυρος ακέραιος.")
            return

        # Έλεγχος: τουλάχιστον ένα συστατικό και ένα βήμα
        if not self.ingredients:
            messagebox.showerror("Σφάλμα", "Παρακαλώ προσθέστε τουλάχιστον ένα συστατικό.")
            return
            
        if not self.steps:
            messagebox.showerror("Σφάλμα", "Παρακαλώ προσθέστε τουλάχιστον ένα βήμα.")
            return

        # Αποθήκευση στη βάση δεδομένων
        with DatabaseConn("recipe_database.db") as db:
            if self.recipe_id:
                # Ενημέρωση υπάρχουσας συνταγής
                db.execute(
                    "UPDATE recipes SET name=?, category=?, difficulty=?, total_time_minutes=? WHERE id=?",
                    (name, self.category_entry.get(), difficulty, total_time, self.recipe_id)
                )
                # Διαγραφή παλιών συστατικών και βημάτων
                db.execute("DELETE FROM ingredients WHERE recipe_id=?", (self.recipe_id,))
                db.execute("DELETE FROM steps WHERE recipe_id=?", (self.recipe_id,))
                recipe_id = self.recipe_id
            else:
                # Εισαγωγή νέας συνταγής
                db.execute(
                    "INSERT INTO recipes (name, category, difficulty, total_time_minutes) VALUES (?, ?, ?, ?)",
                    (name, self.category_entry.get(), difficulty, total_time)
                )
                recipe_id = db.cursor.lastrowid  # Λήψη του αυτόματα δημιουργημένου ID

            # Αποθήκευση όλων των συστατικών
            for ingredient in self.ingredients:
                ingredient.recipe_id = recipe_id
                ingredient.save_to_db(db)

            # Αποθήκευση όλων των βημάτων
            for step in self.steps:
                step.recipe_id = recipe_id
                step.save_to_db(db)

        # Μήνυμα επιτυχίας και κλείσιμο φόρμας
        messagebox.showinfo("Επιτυχία", f"Η συνταγή '{name}' αποθηκεύτηκε επιτυχώς!")
        self.parent_app.view_recipes()  # Ανανέωση της λίστας συνταγών
        self.window.destroy()

    def open_edit_ingredient_form(self):
        """Άνοιγμα φόρμας για επεξεργασία επιλεγμένου συστατικού"""
        selected = self.ingredients_listbox.curselection()
        if not selected:
            messagebox.showwarning("Προειδοποίηση", "Επιλέξτε ένα συστατικό για επεξεργασία.")
            return
        index = selected[0]
        IngredientFormPage(parent_form=self, index=index, ingredient=self.ingredients[index])

    def delete_ingredient(self):
        """Διαγραφή επιλεγμένου συστατικού"""
        selected = self.ingredients_listbox.curselection()
        if not selected:
            messagebox.showwarning("Προειδοποίηση", "Επιλέξτε ένα συστατικό για διαγραφή.")
            return
        self.ingredients.pop(selected[0])  # Αφαίρεση από τη λίστα
        self.refresh_ingredients_list()    # Ανανέωση εμφάνισης

    def open_edit_step_form(self):
        """Άνοιγμα φόρμας για επεξεργασία επιλεγμένου βήματος"""
        selected = self.steps_listbox.curselection()
        if not selected:
            messagebox.showwarning("Προειδοποίηση", "Επιλέξτε ένα βήμα για επεξεργασία.")
            return
        index = selected[0]
        StepFormPage(parent_form=self, index=index, step=self.steps[index])

    def delete_step(self):
        """Διαγραφή επιλεγμένου βήματος και αναριθμοδότηση των υπόλοιπων"""
        selected = self.steps_listbox.curselection()
        if not selected:
            messagebox.showwarning("Προειδοποίηση", "Επιλέξτε ένα βήμα για διαγραφή.")
            return
        self.steps.pop(selected[0])  # Αφαίρεση από τη λίστα
        
        # Αναριθμοδότηση των sequence_order για τα υπόλοιπα βήματα
        for i, step in enumerate(self.steps):
            step.sequence_order = i + 1
        
        self.refresh_steps_list()    # Ανανέωση εμφάνισης


# Κύρια κλάση της εφαρμογής διαχείρισης συνταγών
class RecipeApp:
    def __init__(self, root):
        """
        Αρχικοποίηση της κύριας εφαρμογής
        root: το κύριο παράθυρο tkinter
        """
        self.root = root

        # Ρύθμιση μεγέθους και κεντραρίσματος του παραθύρου
        width = 600
        height = 300

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Υπολογισμός θέσης ώστε το παράθυρο να εμφανίζεται κεντραρισμένο
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))

        root.geometry(f"{width}x{height}+{x}+{y}")
        root.title("Διαχείριση Συνταγών")

        # Κουμπιά κύριας οθόνης
        ttk.Button(root, text="Προσθήκη Συνταγής",    command=self.open_add_page).grid(row=0, column=0, pady=10, padx=10)
        ttk.Button(root, text="Ενημέρωση Συνταγής", command=self.open_update_page).grid(row=0, column=1, pady=10, padx=10)
        ttk.Button(root, text="Διαγραφή Συνταγής", command=self.delete_recipe).grid(row=0, column=2, pady=10, padx=10)
        ttk.Button(root, text="Εμφάνιση Συνταγών",  command=self.view_recipes).grid(row=0, column=3, pady=10, padx=10)

        # Listbox για εμφάνιση όλων των συνταγών
        self.recipes_listbox = tk.Listbox(root, width=70, height=10)
        self.recipes_listbox.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

        # Αρχική φόρτωση των συνταγών
        self.view_recipes()

    def open_add_page(self):
        """Άνοιγμα φόρμας για προσθήκη νέας συνταγής"""
        RecipeFormPage(parent_app=self)  # Δεν δίνουμε recipe_id = λειτουργία προσθήκης

    def open_update_page(self):
        """Άνοιγμα φόρμας για ενημέρωση επιλεγμένης συνταγής"""
        selected = self.recipes_listbox.curselection()
        if not selected:
            print("Επιλέξτε μια συνταγή για ενημέρωση.")
            return
        # Εξαγωγή του ID από το επιλεγμένο στοιχείο (το ID είναι στην αρχή πριν από ":")
        recipe_id = int(self.recipes_listbox.get(selected[0]).split(":")[0].strip())
        RecipeFormPage(parent_app=self, recipe_id=recipe_id)  # Δίνουμε recipe_id = λειτουργία επεξεργασίας

    def delete_recipe(self):
        """Διαγραφή επιλεγμένης συνταγής από τη βάση"""
        selected = self.recipes_listbox.curselection()
        if selected:
            recipe_id = int(self.recipes_listbox.get(selected[0]).split(":")[0].strip())
            with DatabaseConn("recipe_database.db") as db:
                db.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
            self.view_recipes()  # Ανανέωση της λίστας μετά τη διαγραφή
        else:
            print("Επιλέξτε μια συνταγή για διαγραφή.")

    def view_recipes(self):
        """Φόρτωση και εμφάνιση όλων των συνταγών στη λίστα"""
        self.recipes_listbox.delete(0, tk.END)  # Καθαρισμός υπάρχουσας λίστας
        with DatabaseConn("recipe_database.db") as db:
            # Επιλογή όλων των συνταγών από τη βάση
            db.execute("SELECT id, name, category, difficulty, total_time_minutes FROM recipes")
            rows = db.fetchall()
        
        # Εισαγωγή κάθε συνταγής στη λίστα
        for row in rows:
            self.recipes_listbox.insert(tk.END, f"{row[0]}: {row[1]} - {row[2]} - Δυσκολία {row[3]}")

    def clear_entries(self):
        """Καθαρισμός πεδίων εισαγωγής (δεν χρησιμοποιείται πλέον, αλλά αφήνεται για συμβατότητα)"""
        self.name_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.difficulty_entry.delete(0, tk.END)
        self.total_time_entry.delete(0, tk.END)


# Σημείο εισόδου της εφαρμογής
if __name__ == "__main__":
    root = tk.Tk()              # Δημιουργία του κύριου παραθύρου
    app = RecipeApp(root)       # Δημιουργία της εφαρμογής
    root.mainloop()             # Ε