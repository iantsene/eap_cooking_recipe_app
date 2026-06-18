import os                           # Για τη διαχείριση φακέλων και το μονοπάτι της βάσης
import sqlite3                      # Για την επικοινωνία με τη βάση δεδομένων SQL
import tkinter as tk                # Η κύρια βιβλιοθήκη των γραφικών
from tkinter import messagebox, ttk # popup μηνύματα και σύνθετα widgets (π.χ. Combobox)

# ==============================================================================
# ΜΕΡΟΣ 1ο: Κλάσεις (Η ΛΟΓΙΚΗ ΤΩΝ ΔΕΔΟΜΕΝΩΝ)
# ==============================================================================

class Category:
    """ Αντιπροσωπεύει την κατηγορία (π.χ. Πίτες, Ζυμαρικά) """
    def __init__(self, name):
        # έλεγχος αν το name είναι κενό ή none ή πατήθηκαν μόνο κενά    
        if not name or str(name).strip() == "":
            # Αν κάτι από τα πάνω ισχύει, σταματάμε τη δημιουργία του αντικειμένου    
            raise ValueError("Κενή κατηγορία!")
        self.name = str(name).strip() # Αποθήκευση ονόματος χωρίς κενά γύρω-γύρω

class Ingredient:
    """ Αντιπροσωπεύει ένα υλικό της συνταγής """
    def __init__(self, name, quantity, unit):
        if not name or str(name).strip() == "":
            raise ValueError("Κενό όνομα υλικού!")
        try:
            # Μετατροπή ',' σε '.' για να δέχεται το 0,5 ως 0.5 χωρίς να κρασάσει το πρόγραμμα
            qty = float(str(quantity).replace(',', '.'))
            # έλεγχος λογικής. Δεν μπορεί ο χρήστης να δηλώσει αρνητική ποσότητα
            if qty <= 0: raise ValueError()
        except: raise ValueError(f"Η ποσότητα για το '{name}' πρέπει να είναι αριθμός > 0!")

        self.name = name.strip()    # Αποθηκεύει το όνομα του υλικού και αφαιρει τυχον κενά
        self.quantity = qty         # Αποθηκεύει την ποσότητα
        self.unit = unit.strip()    # Αποθηκεύει τη μονάδα μέτρησης και αφαιρει τυχον κενά

class Step:
    """ Αντιπροσωπεύει ένα βήμα εκτέλεσης με χρόνο και οδηγίες """
    def __init__(self, order, title, description, hours, minutes, step_ingredients):
        # Αν ο χρήστης δεν έγραψε τίτλο ή πάτησε μόνο κενά, σταματάμε
        if not title.strip():
            raise ValueError("Κενός τίτλος βήματος!")
        try:
            h = int(hours) # μετατροπή του hours σε ακέραιο σε περίπτωση που ο χρήστης έχει γράψει κάτι διαφορετικό
            m = int(minutes) # ομοίως για τα minutes
            # έλεγχος εάν ο χρήστης δώσει αρνητικές τιμές ή μηδέν (λογικό λάθος)
            if h < 0 or m < 0 or (h == 0 and m == 0):
                raise ValueError()
        except: raise ValueError("Ο χρόνος πρέπει να είναι έγκυρος αριθμός > 0!")
        
        self.order = order # Αποθηκεύει τον αριθμό της σειράς του βήματος (π.χ. Βήμα 1, Βήμα 2)
        self.title = title.strip() # Αποθηκεύει τον τίτλο, σβήνοντας τυχόν κατά λάθος κενά στην αρχή ή στο τέλος
        self.description = description.strip() # με το .strip αφαιρώ την αλλαγη γραμμής του tkinker για να μην εχω κενες γραμμες
        self.hours = h # Αποθηκεύει τις ώρες
        self.minutes = m # Αποθηκεύει τα λεπτά
        self.step_ingredients = step_ingredients.strip() # Αποθηκεύει τα υλικά που ανήκουν αποκλειστικά σε αυτό το βήμα (αν υπάρχουν)

class Recipe:
    """ Η κεντρική οντότητα που συνδέει όλα τα παραπάνω """
    # δημιουργία της συνταγής
    def __init__(self, name, category_name, difficulty):

        # αμυντικός προγραμματισμός αν το ονομα ειναι κενό
        if not name.strip(): 
            raise ValueError("Κενό όνομα συνταγής!")
        # τα βασικά ορίσματα (ταυτότητα της συνταγής), με αυτές το αντικείμενο παίρνει τις απαραίτητες πληροφορίες
        self.name = name.strip() # Αποθηκεύει το όνομα, καθαρισμένο από περιττά κενά
        self.category = Category(category_name) # Δημιουργεί ένα νέο ΑΝΤΙΚΕΙΜΕΝΟ της κλάσης Category και το "δένει" πάνω στη συνταγή.
        self.difficulty = difficulty # Αποθηκεύει τη δυσκολία, στο γραφικό περιβάλλον έχει επιλογή δυσκολίας 
        # προετοιμασία του αντικειμένου με υποδομές λιστών για να μπορουμε αργότερα να δουλέψουμε
        self.ingredients_list = [] # Φτιάχνει μια άδεια λίστα. Εδώ μέσα θα μαζεύονται ένα-ένα τα υλικά (αντικείμενα Ingredient).
        self.steps_list = [] # Φτιάχνει μια άδεια λίστα. Εδώ μέσα θα μπαίνουν τα βήματα (αντικείμενα Step).
        self.total_time_minutes = 0 # Ξεκινάει το χρονόμετρο της συνταγής από το ΜΗΔΕΝ. Θα αυξάνεται αυτόματα.

    # προσθήκη υλικών
    # λειτουργία: παίρνει τα στοιχεία (name,quantity,unit)
    # φτιάχνει νέο υλικό και το πετάει μέσα στη λίστα υλικών
    def add_ingredient(self, name, quantity, unit):
        self.ingredients_list.append(Ingredient(name, quantity, unit))

    # προσθήκη βήματος
    # παίρνει τα στοιχεία (title, description, hours, minutes, step_ingredients)
    # Μετράει πόσα βήματα έχει ήδη η λίστα (με το len)
    # και προσθέτει +1. Έτσι, το πρώτο βήμα παίρνει το '1', το δεύτερο το '2' κ.ο.κ.
    # Αφού φτιαχτεί το βήμα, το βάζει στη λίστα βημάτων.
    def add_step(self, title, description, hours, minutes, step_ingredients):
        new_s = Step(len(self.steps_list)+1, title, description, hours, minutes, step_ingredients)
        self.steps_list.append(new_s)

        # ΑΥΤΟΜΑΤΟΣ ΥΠΟΛΟΓΙΣΜΟΣ ΧΡΟΝΟΥ:
        # Κάθε φορά που μπαίνει ένα βήμα, παίρνει τις ώρες του, τις κάνει λεπτά (* 60),
        # προσθέτει και τα λεπτά του, και τα βάζει όλα στο γενικό σύνολο (total_time_minutes).
        self.total_time_minutes += (new_s.hours * 60) + new_s.minutes

# ==============================================================================
# ΜΕΡΟΣ 2ο: DATABASE (ΔΙΑΧΕΙΡΙΣΗ ΑΠΟΘΗΚΕΥΣΗΣ)
# ==============================================================================

class DatabaseManager:
    """ Αναλαμβάνει όλη την επικοινωνία (αποθήκευση/ανάγνωση) με το αρχείο της βάσης """
    # αρχικοποίηση 
    def __init__(self, db_name='recipe_manager.db'):
        # Βρίσκει τον φάκελο που εκτελείται το script για να σώσει εκεί τη βάση και να μην τη ψαχνουμε
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, db_name)

    # δημιουργία πινάκων 
    def setup_tables(self):
        """ Δημιουργία των πινάκων αν δεν υπάρχουν """
        # Ανοίγει μια "γραμμή επικοινωνίας" με το αρχείο της βάσης
        conn = sqlite3.connect(self.db_path)
        # δημιουργία (δρομέα). Του δίνουμε εντολές SQL και τις εκτελεί.
        cursor = conn.cursor()
        # ΠΙΝΑΚΑΣ 1: Κατηγορίες. (UNIQUE = δεν μπορείς να έχεις 2 φορές την ίδια κατηγορία πχ "Γλυκά")
        cursor.execute('CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY, name TEXT UNIQUE)')
        # ΠΙΝΑΚΑΣ 2: Συνταγές. Συνδέεται με την κατηγορία (category_id). Το όνομα πρέπει να είναι UNIQUE (μοναδικό).
        cursor.execute('''CREATE TABLE IF NOT EXISTS recipes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL, 
                            category_id INTEGER, difficulty TEXT, total_time INTEGER)''')
        # ΠΙΝΑΚΑΣ 3: Υλικά. Έχει ένα 'recipe_id' για να ξέρουμε σε ποια συνταγή ανήκει το κάθε υλικό.
        cursor.execute('CREATE TABLE IF NOT EXISTS ingredients (id INTEGER PRIMARY KEY, recipe_id INTEGER, name TEXT, quantity REAL, unit TEXT)')
        # ΠΙΝΑΚΑΣ 4: Βήματα. Και αυτό έχει 'recipe_id' για να συνδέεται με τη συνταγή.
        cursor.execute('CREATE TABLE IF NOT EXISTS steps (id INTEGER PRIMARY KEY, recipe_id INTEGER, sequence_order INTEGER, title TEXT, description TEXT, hours INTEGER, minutes INTEGER, step_ingredients TEXT)')
        # Αποθηκεύει (Οριστικοποιεί) τις αλλαγές που μόλις κάναμε.
        conn.commit()
        # Κλείνει την βάση
        conn.close()

    # αποθήκευση συνταγής (τοποθέτηση δεδομένων στους πίνακες)
    def save_recipe(self, recipe):
        """ Αποθήκευση πλήρους αντικειμένου Recipe στη βάση """
        # ανοίγουμε το αρχείο της βάσης μας
        conn = sqlite3.connect(self.db_path)
        # δημιουργούμε τον (δρομέα) μας για να εκτελέσουμε τις εντολές της sql 
        cursor = conn.cursor()
        # αμυντικός προγραμματισμός για να μην σωσουμε συνταγή με το ίδιο όνομα
        try:
            # Σώζουμε την κατηγορία
            # INSERT OR IGNORE: Αν η κατηγορία υπάρχει, την αγνοούμε χωρίς μήνυμα σφάλματος
            cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (recipe.category.name,))
            # Ψάχνουμε να βρούμε ποιο είναι το ID της κατηγορίας
            cursor.execute('SELECT id FROM categories WHERE name = ?', (recipe.category.name,))
            # παίρνουμε το id. Γίνεται σύνδεση της συνταγής με το id και όχι με το όνομα. Γρήγορα αποτελέσματα
            cat_id = cursor.fetchone()[0]
            
            # Αποθήκευση βασικής συνταγής
            # Εδώ χρησιμοποιούμε το id που βρήκαμε μόλις, για να συνδέσουμε τη συνταγή με την κατηγορία της.
            cursor.execute('INSERT INTO recipes (name, category_id, difficulty, total_time) VALUES (?, ?, ?, ?)',
                           (recipe.name, cat_id, recipe.difficulty, recipe.total_time_minutes))
            r_id = cursor.lastrowid # Παίρνουμε το ID της συνταγής που μόλις φτιάχτηκε (π.χ. η συνταγή 42)
            
            # Αποθήκευση υλικών συνδεδεμένων με το r_id
            # το for loop είναι ο τρόπος να πάρουμε τα υλικά ένα ένα απ'ο τη λίστα τους και να τα τοποθετήσουμε στη βάση
            for i in recipe.ingredients_list:
                cursor.execute('INSERT INTO ingredients (recipe_id, name, quantity, unit) VALUES (?, ?, ?, ?)', (r_id, i.name, i.quantity, i.unit))
            
            # Αποθήκευση βημάτων συνδεδεμένων με το r_id
            # ομοίως όπως για τη παραπάνω loop 
            for s in recipe.steps_list:
                cursor.execute('INSERT INTO steps VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)', (r_id, s.order, s.title, s.description, s.hours, s.minutes, s.step_ingredients))
         
         # Αν όλα πήγαν καλά, πατάμε το "Save" (commit)   
            conn.commit()
        # Το IntegrityError συμβαίνει αν παραβιάσουμε τον κανόνα UNIQUE.    
        except sqlite3.IntegrityError:
            raise ValueError("Η συνταγή υπάρχει ήδη στη βάση!")
        # Σιγουρευόμαστε ότι η βάση θα κλείσει με ασφάλεια 
        finally:
            conn.close()

# ==============================================================================
# ΜΕΡΟΣ 3ο: GUI (ΓΡΑΦΙΚΟ ΠΕΡΙΒΑΛΛΟΝ)
# ==============================================================================

class RecipeApp:
    def __init__(self, root):
        self.root = root # κεντρικό παράθυρο
        self.root.title("ChefMaster 2026") #τίτλος παραθύρου
        
        # ΕΥΧΡΗΣΤΙΑ: Ορίζουμε ελάχιστο μέγεθος για να μην "κρύβεται" το παράθυρο
        self.root.minsize(450, 500) # ελάχιστο μέγεθος παραθύρου
        self.root.geometry("450x550") # αρχικό μέγεθος
        
        self.db = DatabaseManager() # αντικείμενο για να καλούμε τις μεθόδους που φτιάξαμε στη βάση
        self.db.setup_tables() # φτιάχνει τους πίνακες αν η εφαρμογή τρέχει 1η φορά

        # Κεντρικό πλαίσιο (Frame) που περιέχει τα πάντα
        main_frame = tk.Frame(root, padx=20, pady=20)
        # expand=True και fill="both": Το frame μεγαλώνει μαζί με το παράθυρο
        main_frame.pack(expand=True, fill="both")

        tk.Label(main_frame, text="🍳 Διαχείριση Συνταγών", font=("Arial", 18, "bold")).pack(pady=30)
        
        # Στυλ κουμπιών για ομοιομορφία
        btn_style = {"width": 25, "font": ("Arial", 11, "bold"), "pady": 10}
        
        tk.Button(main_frame, text="➕ Νέα Συνταγή", command=self.open_add_window, bg="#4CAF50", fg="white", **btn_style).pack(pady=10)
        tk.Button(main_frame, text="❌ Έξοδος", command=root.quit, bg="#757575", fg="white", **btn_style).pack(pady=10)

    def open_add_window(self):
        """ Παράθυρο Καταχώρησης - Υποστηρίζει Resizing και Copy-Paste """
        add_win = tk.Toplevel(self.root) # Δημιουργία νέου επιπέδου (pop-up)
        add_win.title("Προσθήκη Νέας Συνταγής")
        add_win.minsize(500, 700) # Ελάχιστες διαστάσεις για να κουνιέται άνετα
        
        # Κύριο container για τα στοιχεία εισαγωγής
        container = tk.Frame(add_win, padx=25, pady=25)
        container.pack(expand=True, fill="both")

        # --- Βασικά Στοιχεία ---
        tk.Label(container, text="Όνομα Συνταγής:").pack(anchor="w")
        # fill="x": Το κουτάκι Entry πιάνει όλο το πλάτος
        name_ent = tk.Entry(container, font=("Arial", 11)); name_ent.pack(fill="x", pady=5)

        tk.Label(container, text="Κατηγορία:").pack(anchor="w")
        cat_ent = tk.Entry(container, font=("Arial", 11)); cat_ent.pack(fill="x", pady=5)

        tk.Label(container, text="Δυσκολία:").pack(anchor="w")
        diff_cb = ttk.Combobox(container, values=["Εύκολη", "Μέτρια", "Δύσκολη"], state="readonly", font=("Arial", 11))
        diff_cb.set("Εύκολη"); diff_cb.pack(fill="x", pady=5)

        # Λίστες μνήμης για τα δεδομένα που μαζεύουμε πριν το Save
        temp_ingredients = []
        temp_steps = []

        # --- Ενότητα Υλικών ---
        tk.Label(container, text="\n🍎 Λίστα Υλικών:", font=("Arial", 11, "bold")).pack(anchor="w")
        # expand=True: Το listbox μεγαλώνει αν μεγαλώσεις το παράθυρο
        ing_listbox = tk.Listbox(container, height=6, font=("Arial", 10))
        ing_listbox.pack(fill="both", expand=True, pady=5)

        def add_ing_popup():
            """ Pop-up για μεμονωμένο υλικό - Επιτρέπει κίνηση και copy-paste """
            ing_win = tk.Toplevel(add_win)
            ing_win.title("Νέο Υλικό")
            ing_win.minsize(350, 320)
            ing_win.configure(padx=20, pady=20)

            tk.Label(ing_win, text="Όνομα Υλικού:").pack(pady=5)
            e_n = tk.Entry(ing_win, font=("Arial", 11)); e_n.pack(fill="x")
            
            tk.Label(ing_win, text="Ποσότητα (π.χ. 0.5):").pack(pady=5)
            e_q = tk.Entry(ing_win, font=("Arial", 11)); e_q.pack(fill="x")
            
            tk.Label(ing_win, text="Μονάδα:").pack(pady=5)
            e_u = tk.Entry(ing_win, font=("Arial", 11)); e_u.pack(fill="x")
            
            def save_ing():
                try:
                    ing = Ingredient(e_n.get(), e_q.get(), e_u.get())
                    temp_ingredients.append(ing)
                    ing_listbox.insert(tk.END, f"• {ing.name}: {ing.quantity} {ing.unit}")
                    ing_win.destroy()
                except ValueError as err: messagebox.showerror("Λάθος", str(err))

            tk.Button(ing_win, text="Προσθήκη", command=save_ing, bg="#4CAF50", fg="white", pady=5).pack(pady=20)

        tk.Button(container, text="+ Προσθήκη Υλικού", command=add_ing_popup).pack(pady=5)

        # --- Ενότητα Βημάτων ---
        tk.Label(container, text="\n📝 Βήματα Εκτέλεσης:", font=("Arial", 11, "bold")).pack(anchor="w")
        step_listbox = tk.Listbox(container, height=6, font=("Arial", 10))
        step_listbox.pack(fill="both", expand=True, pady=5)

        def add_step_popup():
            """ Pop-up για βήμα - Χρησιμοποιεί Text Widget για μεγάλα κείμενα """
            step_win = tk.Toplevel(add_win)
            step_win.title("Νέο Βήμα")
            step_win.minsize(450, 450)
            step_win.configure(padx=20, pady=20)

            tk.Label(step_win, text="Τίτλος Βήματος:").pack()
            e_t = tk.Entry(step_win, font=("Arial", 11)); e_t.pack(fill="x", pady=5)
            
            tk.Label(step_win, text="Οδηγίες (Κάνε επικόλληση εδώ):").pack()
            # Text Widget: Επιτρέπει πολλές γραμμές και εύκολο Copy-Paste
            e_d = tk.Text(step_win, height=6, font=("Arial", 10)); e_d.pack(fill="both", expand=True, pady=5)
            
            # Πλαίσιο για τον χρόνο (δίπλα-δίπλα)
            time_frame = tk.Frame(step_win)
            time_frame.pack(pady=10)
            tk.Label(time_frame, text="Ώρες:").grid(row=0, column=0)
            e_h = tk.Entry(time_frame, width=5); e_h.insert(0, "0"); e_h.grid(row=0, column=1, padx=5)
            tk.Label(time_frame, text="Λεπτά:").grid(row=0, column=2)
            e_m = tk.Entry(time_frame, width=5); e_m.insert(0, "0"); e_m.grid(row=0, column=3, padx=5)

            def save_step():
                try:
                    # e_d.get("1.0", tk.END): Διαβάζει όλο το περιεχόμενο του Text widget
                    s = Step(len(temp_steps)+1, e_t.get(), e_d.get("1.0", tk.END), e_h.get(), e_m.get(), "")
                    temp_steps.append(s)
                    step_listbox.insert(tk.END, f"{s.order}. {s.title} ({s.hours}ω {s.minutes}λ)")
                    step_win.destroy()
                except ValueError as err: messagebox.showerror("Σφάλμα", str(err))

            tk.Button(step_win, text="Προσθήκη", command=save_step, bg="#4CAF50", fg="white", pady=5).pack(pady=10)

        tk.Button(container, text="+ Προσθήκη Βήματος", command=add_step_popup).pack(pady=5)

        # --- Τελική Αποθήκευση στη Βάση ---
        def final_save():
            try:
                if not temp_ingredients or not temp_steps: raise ValueError("Πρέπει να βάλετε υλικά και βήματα!")
                
                # Δημιουργία τελικού αντικειμένου Recipe
                new_recipe = Recipe(name_ent.get(), cat_ent.get(), diff_cb.get())
                new_recipe.ingredients_list = temp_ingredients
                new_recipe.steps_list = temp_steps
                
                # Αποθήκευση μέσω του DatabaseManager
                self.db.save_recipe(new_recipe)
                messagebox.showinfo("Επιτυχία", f"Η συνταγή '{new_recipe.name}' αποθηκεύτηκε!")
                add_win.destroy()
            except ValueError as err: messagebox.showerror("Σφάλμα", str(err))

        # Μεγάλο κουμπί αποθήκευσης που πιάνει όλο το πλάτος (fill="x")
        tk.Button(container, text="💾 ΑΠΟΘΗΚΕΥΣΗ ΣΥΝΤΑΓΗΣ", command=final_save, 
                  bg="#2E7D32", fg="white", font=("Arial", 12, "bold"), pady=15).pack(pady=20, fill="x")

# --- Εκκίνηση της Εφαρμογής ---
if __name__ == "__main__":
    root = tk.Tk()
    app = RecipeApp(root)
    root.mainloop()