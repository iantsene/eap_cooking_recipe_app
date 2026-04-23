# Εισαγωγή των απαραίτητων βιβλιοθηκών
from db import DatabaseConn  # Εισαγωγή της κλάσης για σύνδεση με τη βάση δεδομένων
from models import Recipe, Ingredient, Step  # Εισαγωγή των μοντέλων δεδομένων
import tkinter as tk  # Βιβλιοθήκη για τη δημιουργία γραφικού περιβάλλοντος
from tkinter import ttk, messagebox, simpledialog  # Επιπλέον widgets και μηνύματα ειδοποίησης

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

    create_ingredients_to_steps_table = """CREATE TABLE IF NOT EXISTS step_ingredients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ingredient_id INTEGER,
        step_id INTEGER,
        quantity REAL,
        unit TEXT,
        notes TEXT,
        FOREIGN KEY (step_id) REFERENCES steps(id) ON DELETE CASCADE,
        FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
    )"""
    # Επεξήγηση των παραπάνω πεδίων create_ingredients_to_steps_table
    # Μοναδικό αναγνωριστικό
    # Αναφορά στο υλικό
    # Αναφορά στο βήμα
    # Ποσότητα (δεκαδικός αριθμός)
    # Μονάδα μέτρησης (π.χ. kg, κουταλιές)
    # Σημειώσεις (π.χ. προαιρετικό, προτίμηση)
    # Κλειδί σύνδεσης με πίνακα steps
    # Κλειδί σύνδεσης με πίνακα ingredients
    
    # Εκτέλεση των παραπάνω SQL εντολών για δημιουργία των πινάκων
    rcp_db.execute(create_recipe_table)
    rcp_db.execute(create_ingredients_table)
    rcp_db.execute(create_steps_table)
    rcp_db.execute(create_ingredients_to_steps_table)


# Κλάση για τη φόρμα προσθήκης/επεξεργασίας συστατικού
class IngredientFormPage:
    def __init__(self, parent_form, index=None, ingredient=None):
        """
        Αρχικοποίηση της φόρμας συστατικού
        parent_form: η γονική φόρμα (RecipeFormPage)
        index: αν υπάρχει, σημαίνει ότι είμαστε σε λειτουργία επεξεργασίας
        ingredient: το συστατικό προς επεξεργασία (αν υπάρχει)
        """
        self.parent_form = parent_form
        self.index = index

        # Δημιουργία νέου παραθύρου
        self.window = tk.Toplevel()
        self.window.title("Επεξεργασία Συστατικού" if index is not None else "Προσθήκη Συστατικού")
        self.window.geometry("500x350")
        self.window.transient()
        self.window.grab_set()

        # Common units list
        self.common_units = [
            "Προσθήκη νέας μονάδας...",
            "kg", "g", "mg",
            "L", "ml",
            "κουταλιά σούπας", "κουταλιά γλυκού", "κουταλάκι",
            "φλιτζάνι", "ποτήρι",
            "τεμάχιο", "φέτα", "κομμάτι",
            "πρέζα", "σταγόνα",
            "συσκευασία", "κονσέρβα"            
        ]
        
        # StringVar for unit
        self.unit_var = tk.StringVar()
        
        row = 0
        
        # Όνομα συστατικού
        ttk.Label(self.window, text="Όνομα:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=10)
        self.name_entry = ttk.Entry(self.window, width=40)
        self.name_entry.grid(row=row, column=1, columnspan=2, padx=10, pady=10)
        row += 1
        
        # Ποσότητα
        ttk.Label(self.window, text="Ποσότητα:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=10)
        self.quantity_entry = ttk.Entry(self.window, width=15)
        self.quantity_entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=10)
        row += 1
        
        # Μονάδα μέτρησης - Dropdown with option to add new unit
        ttk.Label(self.window, text="Μονάδα μέτρησης:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=10)
        self.unit_combo = ttk.Combobox(self.window, textvariable=self.unit_var, 
                                       values=self.common_units, width=30)
        self.unit_combo.grid(row=row, column=1, columnspan=2, sticky=tk.W, padx=5, pady=10)
        self.unit_combo.set("Επιλέξτε μονάδα...")
        
        # Frame for new unit entry (hidden initially)
        self.new_unit_frame = tk.Frame(self.window)
        self.new_unit_frame.grid(row=row+1, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(self.new_unit_frame, text="Νέα μονάδα:").pack(side=tk.LEFT, padx=5)
        self.new_unit_entry = ttk.Entry(self.new_unit_frame, width=25)
        self.new_unit_entry.pack(side=tk.LEFT, padx=5)
        
        # Hide new unit frame initially
        self.new_unit_frame.grid_remove()
        
        # Bind event to show/hide new unit entry
        self.unit_combo.bind("<<ComboboxSelected>>", self.on_unit_selected)
        row += 2
        
        # Σημειώσεις
        ttk.Label(self.window, text="Σημειώσεις (προαιρετικά):").grid(row=row, column=0, sticky=tk.W, padx=10, pady=10)
        self.notes_entry = ttk.Entry(self.window, width=40)
        self.notes_entry.grid(row=row, column=1, columnspan=2, padx=10, pady=10)
        row += 1
        
        # Κουμπί αποθήκευσης
        label = "Αποθήκευση Αλλαγών" if index is not None else "Προσθήκη Συστατικού"
        ttk.Button(self.window, text=label, command=self.save).grid(
            row=row, column=0, columnspan=3, pady=20
        )
        
        # Αν είμαστε σε λειτουργία επεξεργασίας, συμπληρώνουμε τα πεδία
        if ingredient:
            self.name_entry.insert(0, ingredient.name or "")
            self.quantity_entry.insert(0, ingredient.quantity or "")
            
            # Check if ingredient.unit exists in common_units
            if ingredient.unit and ingredient.unit in self.common_units:
                self.unit_combo.set(ingredient.unit)
            elif ingredient.unit:
                # Custom unit - show new unit frame
                self.unit_combo.set("Προσθήκη νέας μονάδας...")
                self.show_new_unit_frame()
                self.new_unit_entry.insert(0, ingredient.unit)
            
            self.notes_entry.insert(0, ingredient.notes or "")
    
    def on_unit_selected(self, event):
        """Handle unit dropdown selection"""
        selected = self.unit_combo.get()
        if selected == "Προσθήκη νέας μονάδας...":
            self.show_new_unit_frame()
        else:
            self.hide_new_unit_frame()
    
    def show_new_unit_frame(self):
        """Show the new unit entry frame"""
        self.new_unit_frame.grid()
        self.new_unit_entry.focus()
    
    def hide_new_unit_frame(self):
        """Hide the new unit entry frame"""
        self.new_unit_frame.grid_remove()
        self.new_unit_entry.delete(0, tk.END)
    
    def get_selected_unit(self):
        """Return the selected unit (either from dropdown or new unit entry)"""
        selected = self.unit_combo.get()
        if selected == "Προσθήκη νέας μονάδας...":
            new_unit = self.new_unit_entry.get().strip()
            if new_unit:
                return new_unit
            else:
                return None
        elif selected and selected != "Επιλέξτε μονάδα...":
            return selected
        return None

    def save(self):
        """Αποθήκευση ή ενημέρωση του συστατικού"""
        # Λήψη και καθαρισμός των τιμών
        name = self.name_entry.get().strip()
        notes = self.notes_entry.get().strip() or None
        
        # Έλεγχος εγκυρότητας: το όνομα είναι υποχρεωτικό
        if not name:
            messagebox.showerror("Σφάλμα", "Το όνομα του συστατικού είναι υποχρεωτικό.")
            return
        
        # Έλεγχος εγκυρότητας: η ποσότητα πρέπει να είναι θετικός αριθμός
        try:
            quantity = float(self.quantity_entry.get())
            if quantity <= 0:
                messagebox.showerror("Σφάλμα", "Η ποσότητα πρέπει να είναι θετική.")
                return
        except ValueError:
            messagebox.showerror("Σφάλμα", "Παρακαλώ εισάγετε έναν έγκυρο αριθμό για την ποσότητα.")
            return
        
        # Get unit from dropdown or new unit entry
        unit = self.get_selected_unit()

        # Δημιουργία νέου αντικειμένου Ingredient
        ingredient = Ingredient(name=name, quantity=quantity, unit=unit, notes=notes)

        # Ενημέρωση της λίστας στη γονική φόρμα
        if self.index is not None:
            self.parent_form.ingredients[self.index] = ingredient
        else:
            self.parent_form.ingredients.append(ingredient)

        # Ανανέωση της λίστας εμφάνισης
        self.parent_form.refresh_ingredients_list()
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
        self.step_allocations = []  # Track allocations for this step

        self.window = tk.Toplevel()
        self.window.title("Επεξεργασία Βήματος" if index is not None else "Προσθήκη Βήματος")
        self.window.geometry("650x550")

        # Υπολογισμός του αριθμού βήματος για εμφάνιση
        step_number = (index + 1) if index is not None else len(self.parent_form.steps) + 1
        ttk.Label(self.window, text=f"Βήμα {step_number}", font=("", 10, "bold")).grid(
            row=0, column=0, columnspan=2, pady=5
        )

        # Πεδίο για τον τίτλο του βήματος
        ttk.Label(self.window, text="Τίτλος Βήματος:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.step_name_entry = ttk.Entry(self.window, width=40)
        self.step_name_entry.grid(row=1, column=1, padx=5, pady=5)

        # Πεδίο για την περιγραφή του βήματος
        ttk.Label(self.window, text="Περιγραφή:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.step_text_entry = ttk.Entry(self.window, width=40)
        self.step_text_entry.grid(row=2, column=1, padx=5, pady=5)

        # Πεδίο για τη διάρκεια του βήματος
        ttk.Label(self.window, text="Διάρκεια (λεπτά):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.duration_entry = ttk.Entry(self.window, width=40)
        self.duration_entry.grid(row=3, column=1, padx=5, pady=5)

        # --- Ενότητα Συστατικών ---
        ttk.Label(self.window, text=f"Συστατικά βήματος {step_number}:", font=("", 10, "bold")).grid(
            row=4, column=0, sticky=tk.W, padx=5, pady=(10, 0)
        )
        
        # Κουμπί προσθήκης συστατικού
        ttk.Button(self.window, text="+ Προσθήκη Συστατικού", command=self.add_ingredient_from_existing).grid(
            row=4, column=1, sticky=tk.E, padx=5
        )

        # Treeview για εμφάνιση των συστατικών
        columns = ('Όνομα', 'Ποσότητα', 'Μονάδα', 'Σημειώσεις')
        self.ingredients_tree = ttk.Treeview(self.window, columns=columns, show='headings', height=5)
        
        self.ingredients_tree.heading('Όνομα', text='Όνομα')
        self.ingredients_tree.heading('Ποσότητα', text='Ποσότητα')
        self.ingredients_tree.heading('Μονάδα', text='Μονάδα')
        self.ingredients_tree.heading('Σημειώσεις', text='Σημειώσεις')
        
        self.ingredients_tree.column('Όνομα', width=150)
        self.ingredients_tree.column('Ποσότητα', width=100)
        self.ingredients_tree.column('Μονάδα', width=100)
        self.ingredients_tree.column('Σημειώσεις', width=150)
        
        self.ingredients_tree.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=self.ingredients_tree.yview)
        scrollbar.grid(row=5, column=2, sticky='ns', padx=(0, 5))
        self.ingredients_tree.configure(yscrollcommand=scrollbar.set)

        # Delete ingredient button
        ttk.Button(self.window, text="Αφαίρεση Συστατικού", command=self.remove_selected_ingredient).grid(
            row=6, column=0, columnspan=2, pady=5
        )

        # Κουμπί αποθήκευσης
        label = "Αποθήκευση Αλλαγών" if index is not None else "Προσθήκη Βήματος"
        ttk.Button(self.window, text=label, command=self.save).grid(
            row=7, column=0, columnspan=2, pady=10
        )

        # Συμπλήρωση πεδίων αν είμαστε σε λειτουργία επεξεργασίας
        if step:
            self.step_name_entry.insert(0, step.step_name or "")
            self.step_text_entry.insert(0, step.step_text or "")
            self.duration_entry.insert(0, step.duration_in_minutes or "")
            if hasattr(step, 'allocations'):
                self.step_allocations = step.allocations.copy()
                self.refresh_ingredients_list()

    def add_ingredient_from_existing(self):
        """Open dialog to add an existing ingredient to this step"""
        
        # Check if there are any ingredients in the parent recipe
        if not self.parent_form.ingredients:
            messagebox.showwarning("Προειδοποίηση", 
                "Δεν υπάρχουν συστατικά στη συνταγή. Προσθέστε συστατικά πρώτα.")
            return
        
        # Create dialog
        dialog = tk.Toplevel()
        dialog.title("Προσθήκη Συστατικού στο Βήμα")
        dialog.geometry("550x500")
        dialog.transient(self.window)
        dialog.grab_set()
        
        row = 0
        
        tk.Label(dialog, text="Επιλέξτε συστατικό από τη συνταγή:", 
                font=("", 10, "bold")).grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        
        # Function to refresh available ingredients using temp_id (index)
        def refresh_available_ingredients():
            ingredient_list = []
            ingredient_data = []
            
            for idx, ing in enumerate(self.parent_form.ingredients):
                # Calculate used quantity from ALL steps (excluding current step if editing)
                used_quantity = 0
                
                # Check other steps (already saved steps)
                for step in self.parent_form.steps:
                    if hasattr(step, 'allocations'):
                        # If editing, skip the current step to avoid double counting
                        if self.index is not None and step == self.parent_form.steps[self.index]:
                            continue
                        for alloc in step.allocations:
                            # Match by temp_id OR real ingredient_id
                            if alloc.get('temp_id') == idx:
                                used_quantity += alloc.get('quantity', 0)
                            # Also check real ID for already-saved ingredients
                            elif alloc.get('ingredient_id') is not None and alloc.get('ingredient_id') == ing.id:
                                used_quantity += alloc.get('quantity', 0)

                for alloc in self.step_allocations:
                    if alloc.get('temp_id') == idx:
                        used_quantity += alloc.get('quantity', 0)
                    elif alloc.get('ingredient_id') is not None and alloc.get('ingredient_id') == ing.id:
                        used_quantity += alloc.get('quantity', 0)
                
                available = round(ing.quantity - used_quantity, 5)
                if available > 0.001:
                    ingredient_list.append(f"{ing.name} (διαθέσιμο: {available} {ing.unit or ''})")
                    ingredient_data.append({
                        'temp_id': idx,
                        'id': ing.id,
                        'name': ing.name,
                        'available': available,
                        'unit': ing.unit
                    })
            
            return ingredient_list, ingredient_data
        
        # Initial refresh
        ingredient_list, ingredient_data = refresh_available_ingredients()
        
        if not ingredient_list:
            tk.Label(dialog, text="Δεν υπάρχουν διαθέσιμα συστατικά", 
                    fg="red").grid(row=row, column=0, columnspan=2, pady=10)
            tk.Button(dialog, text="Κλείσιμο", command=dialog.destroy).grid(row=row+1, column=0, columnspan=2, pady=10)
            return
        
        # Ingredient dropdown
        tk.Label(dialog, text="Συστατικό:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        ingredient_var = tk.StringVar()
        ingredient_combo = ttk.Combobox(dialog, textvariable=ingredient_var, values=ingredient_list, 
                                        width=40, state="readonly")
        ingredient_combo.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        # Quantity input
        tk.Label(dialog, text="Ποσότητα που θα χρησιμοποιηθεί:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        quantity_entry = ttk.Entry(dialog, width=20)
        quantity_entry.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
        row += 1
        
        # Unit display
        unit_label = tk.Label(dialog, text="")
        unit_label.grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
        row += 1
        
        # Notes
        tk.Label(dialog, text="Σημειώσεις (προαιρετικά):").grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)
        notes_entry = ttk.Entry(dialog, width=40)
        notes_entry.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        # Remaining preview
        remaining_label = tk.Label(dialog, text="", fg="blue")
        remaining_label.grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        
        def update_preview(*args):
            try:
                selected_idx = ingredient_combo.current()
                if selected_idx >= 0 and selected_idx < len(ingredient_data):
                    selected = ingredient_data[selected_idx]
                    unit_label.config(text=f"Μονάδα: {selected['unit'] or 'τεμάχια'}")
                    
                    qty_text = quantity_entry.get()
                    if qty_text:
                        qty = float(qty_text)
                        remaining = selected['available'] - qty
                        if remaining >= 0:
                            remaining_label.config(text=f"Θα απομένουν: {remaining} {selected['unit'] or ''}", fg="green")
                        else:
                            remaining_label.config(text=f"Υπέρβαση! Διαθέσιμο: {selected['available']}", fg="red")
                    else:
                        remaining_label.config(text=f"Διαθέσιμο: {selected['available']} {selected['unit'] or ''}")
            except ValueError:
                remaining_label.config(text="Εισάγετε έγκυρο αριθμό", fg="red")
        
        def save_allocation():
            try:
                selected_idx = ingredient_combo.current()
                if selected_idx < 0:
                    messagebox.showerror("Σφάλμα", "Επιλέξτε συστατικό")
                    return
                
                selected = ingredient_data[selected_idx]
                quantity = float(quantity_entry.get())
                
                if quantity <= 0:
                    messagebox.showerror("Σφάλμα", "Η ποσότητα πρέπει να είναι θετική")
                    return
                
                if quantity > selected['available'] + 0.001:
                    messagebox.showerror("Σφάλμα", 
                        f"Δεν υπάρχει αρκετό {selected['name']}! "
                        f"Διαθέσιμο: {selected['available']} {selected['unit'] or ''}")
                    return
                
                # Add allocation with both temp_id and real id
                allocation = {
                    'temp_id': selected['temp_id'],
                    'ingredient_id': selected['id'],
                    'ingredient_name': selected['name'],
                    'quantity': quantity,
                    'unit': selected['unit'],
                    'notes': notes_entry.get().strip()
                }
                
                self.step_allocations.append(allocation)
                self.refresh_ingredients_list()
                
                # Close dialog
                dialog.destroy()
                
                # Ask if user wants to add another ingredient
                if messagebox.askyesno("Επιτυχία", 
                    f"Το {selected['name']} προστέθηκε στο βήμα.\n\n"
                    "Θέλετε να προσθέσετε άλλο συστατικό στο ίδιο βήμα;"):
                    self.add_ingredient_from_existing()
                
            except ValueError:
                messagebox.showerror("Σφάλμα", "Εισάγετε έγκυρο αριθμό για την ποσότητα")
        
        ingredient_combo.bind('<<ComboboxSelected>>', update_preview)
        quantity_entry.bind('<KeyRelease>', update_preview)
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        tk.Button(button_frame, text="Προσθήκη", command=save_allocation, 
                 bg="green", fg="white", padx=20).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Ακύρωση", command=dialog.destroy, 
                 bg="gray", fg="white", padx=20).pack(side=tk.LEFT, padx=10)
        
        update_preview()
    
    def remove_selected_ingredient(self):
        """Remove selected ingredient from current step"""
        selected = self.ingredients_tree.selection()
        if not selected:
            messagebox.showwarning("Προειδοποίηση", "Επιλέξτε ένα συστατικό για αφαίρεση")
            return
        
        all_items = self.ingredients_tree.get_children()
        index = all_items.index(selected[0])
        
        removed = self.step_allocations.pop(index)
        self.refresh_ingredients_list()
        
        messagebox.showinfo("Επιτυχία", f"Το συστατικό {removed['ingredient_name']} αφαιρέθηκε")
    
    def refresh_ingredients_list(self):
        """Refresh the treeview with current step allocations"""
        for item in self.ingredients_tree.get_children():
            self.ingredients_tree.delete(item)
        
        for alloc in self.step_allocations:
            self.ingredients_tree.insert('', 'end', values=(
                alloc['ingredient_name'],
                alloc['quantity'],
                alloc['unit'] or "",
                alloc.get('notes', '')
            ))

    def save(self):
        """Αποθήκευση ή ενημέρωση του βήματος"""
        step_name = self.step_name_entry.get().strip()
        step_text = self.step_text_entry.get().strip()

        if not step_name or not step_text:
            messagebox.showerror("Σφάλμα", "Ο τίτλος και η περιγραφή του βήματος είναι υποχρεωτικά.")
            return
        
        try:
            duration = int(self.duration_entry.get())
            if duration < 0:
                messagebox.showerror("Σφάλμα", "Η διάρκεια δεν μπορεί να είναι αρνητική.")
                return
        except ValueError:
            messagebox.showerror("Σφάλμα", "Παρακαλώ εισάγετε έναν έγκυρο ακέραιο αριθμό για τη διάρκεια.")
            return

        sequence_order = (self.index + 1) if self.index is not None else len(self.parent_form.steps) + 1
        
        step = Step(
            step_name=step_name,
            step_text=step_text,
            duration_in_minutes=duration,
            sequence_order=sequence_order
        )
        
        step.allocations = self.step_allocations

        if self.index is not None:
            self.parent_form.steps[self.index] = step
        else:
            self.parent_form.steps.append(step)

        # Store allocations in parent form for tracking
        if not hasattr(self.parent_form, 'step_allocations'):
            self.parent_form.step_allocations = []
        
        # Remove old allocations for this step if editing
        if self.index is not None:
            self.parent_form.step_allocations = [
                alloc for alloc in self.parent_form.step_allocations 
                if alloc.get('step_index') != self.index
            ]
        
        # Add current allocations
        for alloc in self.step_allocations:
            self.parent_form.step_allocations.append({
                'step_index': sequence_order - 1,
                'step_name': step_name,
                **alloc
            })

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
        self.ingredients_locked = False
        self.ingredients = []
        self.steps = []

        self.common_categories = [
            "Προσθήκη νέας κατηγορίας...",
            "Ορεκτικά",
            "Σαλάτες",
            "Σούπες",
            "Κυρίως Πιάτα",
            "Ζυμαρικά",
            "Ρύζι",
            "Λαδερά",
            "Φαγητά φούρνου",
            "Ψητά",
            "Τηγανητά",
            "Μαγειρευτά",
            "Κρεατικά",
            "Κοτόπουλο",
            "Ψάρια & Θαλασσινά",
            "Χορτοφαγικά",
            "Vegetarian",
            "Vegan",
            "Πίτες",
            "Αλμυρές πίτες",
            "Γλυκές πίτες",
            "Αρτοσκευάσματα",
            "Ψωμιά",
            "Πρωινό",
            "Σνακ",
            "Γλυκά",
            "Επιδόρπια",
            "Παγωτά",
            "Ροφήματα",
            "Ποτά",
            "Σάλτσες",
            "Ντιπ",
            "Μαρμελάδες & Γλυκά κουταλιού",
            "Κονσέρβες",
            "Ζυμωτά",
            "Παραδοσιακά",
            "Νηστίσιμα",
            "Κατοικίδιων"
        ]

        self.window = tk.Toplevel()
        self.window.title("Επεξεργασία Συνταγής" if recipe_id else "Προσθήκη Συνταγής")
        self.window.geometry("750x700")

        row = 0

        # Όνομα συνταγής
        ttk.Label(self.window, text="Όνομα Συνταγής:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = ttk.Entry(self.window, width=40)
        self.name_entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1

        # Κατηγορία
        ttk.Label(self.window, text="Κατηγορία:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(self.window, textvariable=self.category_var,
                                           values=self.common_categories,
                                           state="normal", width=37)
        self.category_combo.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        self.category_combo.set("Επιλέξτε κατηγορία...")
        self.category_combo.bind("<<ComboboxSelected>>", self.on_category_selected)
        row += 1

        # New category frame (always visible but disabled)
        self.new_category_frame = tk.Frame(self.window)
        self.new_category_frame.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(self.new_category_frame, text="Νέα κατηγορία:").pack(side=tk.LEFT, padx=5)
        self.new_category_entry = ttk.Entry(self.new_category_frame, width=25)
        self.new_category_entry.pack(side=tk.LEFT, padx=5)
        self.new_category_entry.config(state=tk.DISABLED)
        row += 1

        # Δυσκολία
        ttk.Label(self.window, text="Δυσκολία:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.difficulty_var = tk.StringVar()
        self.difficulty_combo = ttk.Combobox(self.window, textvariable=self.difficulty_var,
                                             values=["Εύκολη", "Μέτρια", "Δύσκολη"],
                                             state="readonly", width=37)
        self.difficulty_combo.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        self.difficulty_combo.set("Επιλέξτε δυσκολία...")
        row += 1

        # Συνολικός χρόνος
        ttk.Label(self.window, text="Συνολικός Χρόνος (λεπτά):").grid(row=row, column=0, sticky=tk.W, padx=5, pady=5)
        self.total_time_entry = ttk.Entry(self.window, width=40)
        self.total_time_entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=5)
        row += 1

        # Συστατικά
        ttk.Label(self.window, text="Συστατικά:", font=("", 10, "bold")).grid(
            row=row, column=0, sticky=tk.W, padx=5, pady=(10, 0)
        )
        self.add_ingredient_button = ttk.Button(self.window, text="+ Προσθήκη Συστατικού", command=self.open_ingredient_form)
        self.add_ingredient_button.grid(row=row, column=1, sticky=tk.E, padx=5)
        row += 1

        # Ingredients Treeview
        columns = ('Όνομα', 'Ποσότητα', 'Μονάδα', 'Σημειώσεις')
        self.ingredients_tree = ttk.Treeview(self.window, columns=columns, show='headings', height=5)
        self.ingredients_tree.heading('Όνομα', text='Όνομα')
        self.ingredients_tree.heading('Ποσότητα', text='Ποσότητα')
        self.ingredients_tree.heading('Μονάδα', text='Μονάδα')
        self.ingredients_tree.heading('Σημειώσεις', text='Σημειώσεις')
        self.ingredients_tree.column('Όνομα', width=150)
        self.ingredients_tree.column('Ποσότητα', width=80)
        self.ingredients_tree.column('Μονάδα', width=80)
        self.ingredients_tree.column('Σημειώσεις', width=200)
        self.ingredients_tree.grid(row=row, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        ing_scrollbar = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=self.ingredients_tree.yview)
        ing_scrollbar.grid(row=row, column=2, sticky='ns', padx=(0, 5))
        self.ingredients_tree.configure(yscrollcommand=ing_scrollbar.set)
        row += 1

        # Ingredient buttons
        self.ing_btn_frame = ttk.Frame(self.window)
        self.ing_btn_frame.grid(row=row, column=0, columnspan=2, pady=5)
        self.edit_ingredient_btn = ttk.Button(self.ing_btn_frame, text="Επεξεργασία Συστατικού", command=self.open_edit_ingredient_form)
        self.edit_ingredient_btn.pack(side=tk.LEFT, padx=5)
        self.delete_ingredient_btn = ttk.Button(self.ing_btn_frame, text="Διαγραφή Συστατικού", command=self.delete_ingredient)
        self.delete_ingredient_btn.pack(side=tk.LEFT, padx=5)
        row += 1

        # Confirm buttons
        confirm_frame = ttk.Frame(self.window)
        confirm_frame.grid(row=row, column=0, columnspan=2, pady=5)
        self.confirm_button = ttk.Button(confirm_frame, text="✓ Επιβεβαίωση Συστατικών", command=self.confirm_ingredients)
        self.confirm_button.pack(side=tk.LEFT, padx=5)
        self.edit_ingredients_button = ttk.Button(confirm_frame, text="✎ Επεξεργασία Συστατικών", command=self.unlock_ingredients, state=tk.DISABLED)
        self.edit_ingredients_button.pack(side=tk.LEFT, padx=5)
        row += 1

        # Βήματα
        self.steps_label = ttk.Label(self.window, text="Βήματα:", font=("", 10, "bold"))
        self.steps_label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=(10, 0))
        self.add_step_button = ttk.Button(self.window, text="+ Προσθήκη Βήματος", command=self.open_step_form)
        self.add_step_button.grid(row=row, column=1, sticky=tk.E, padx=5)
        row += 1

        # Steps Treeview
        step_columns = ('Αρ.', 'Τίτλος', 'Περιγραφή', 'Διάρκεια (λεπτά)')
        self.steps_tree = ttk.Treeview(self.window, columns=step_columns, show='headings', height=5)
        self.steps_tree.heading('Αρ.', text='Αρ.')
        self.steps_tree.heading('Τίτλος', text='Τίτλος')
        self.steps_tree.heading('Περιγραφή', text='Περιγραφή')
        self.steps_tree.heading('Διάρκεια (λεπτά)', text='Διάρκεια (λεπτά)')
        self.steps_tree.column('Αρ.', width=50)
        self.steps_tree.column('Τίτλος', width=200)
        self.steps_tree.column('Περιγραφή', width=250)
        self.steps_tree.column('Διάρκεια (λεπτά)', width=100)
        self.steps_tree.grid(row=row, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        step_scrollbar = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=self.steps_tree.yview)
        step_scrollbar.grid(row=row, column=2, sticky='ns', padx=(0, 5))
        self.steps_tree.configure(yscrollcommand=step_scrollbar.set)
        row += 1

        # Step buttons
        self.step_btn_frame = ttk.Frame(self.window)
        self.step_btn_frame.grid(row=row, column=0, columnspan=2, pady=5)
        self.edit_step_btn = ttk.Button(self.step_btn_frame, text="Επεξεργασία Βήματος", command=self.open_edit_step_form)
        self.edit_step_btn.pack(side=tk.LEFT, padx=5)
        self.delete_step_btn = ttk.Button(self.step_btn_frame, text="Διαγραφή Βήματος", command=self.delete_step)
        self.delete_step_btn.pack(side=tk.LEFT, padx=5)
        row += 1

        # Hint label
        self.steps_hint_label = ttk.Label(self.window, text="※ Πρώτα επιβεβαιώστε τα συστατικά για να ενεργοποιηθούν τα βήματα", foreground="gray", font=("", 9, "italic"))
        self.steps_hint_label.grid(row=row, column=0, columnspan=2, pady=5)
        self.steps_hint_label.grid_remove()
        row += 1

        # Save button
        label = "Αποθήκευση Αλλαγών" if recipe_id else "Προσθήκη Συνταγής"
        self.save_button = ttk.Button(self.window, text=label, command=self.save)
        self.save_button.grid(row=row, column=0, columnspan=2, pady=10)

        self.steps_section_enabled(False)

        if recipe_id:
            self._prefill(recipe_id)

    def on_category_selected(self, event):
        selected = self.category_combo.get()
        if selected == "Προσθήκη νέας κατηγορίας...":
            self.new_category_entry.config(state=tk.NORMAL)
            self.new_category_entry.focus()
        else:
            self.new_category_entry.config(state=tk.DISABLED)
            self.new_category_entry.delete(0, tk.END)

    def get_selected_category(self):
        selected = self.category_combo.get()
        if selected == "Προσθήκη νέας κατηγορίας...":
            new_category = self.new_category_entry.get().strip()
            return new_category if new_category else None
        elif selected and selected != "Επιλέξτε κατηγορία...":
            return selected
        return None

    def open_ingredient_form(self):
        IngredientFormPage(parent_form=self)

    def open_step_form(self):
        if not self.ingredients_locked:
            messagebox.showwarning("Προειδοποίηση", "Πρέπει πρώτα να επιβεβαιώσετε τα συστατικά πριν προσθέσετε βήματα.")
            return
        StepFormPage(parent_form=self)

    def refresh_ingredients_list(self):
        for item in self.ingredients_tree.get_children():
            self.ingredients_tree.delete(item)
        for ing in self.ingredients:
            self.ingredients_tree.insert('', 'end', values=(ing.name or "", ing.quantity or "", ing.unit or "", ing.notes or ""))

    def refresh_steps_list(self):
        for item in self.steps_tree.get_children():
            self.steps_tree.delete(item)
        for i, step in enumerate(self.steps, 1):
            self.steps_tree.insert('', 'end', values=(i, step.step_name or "", step.step_text or "", step.duration_in_minutes or ""))
        if not self.ingredients_locked:
            for item in self.steps_tree.get_children():
                self.steps_tree.item(item, tags=('disabled',))
            self.steps_tree.tag_configure('disabled', foreground='gray')

    def _prefill(self, recipe_id):
        recipe = Recipe.get_recipe_by_id(recipe_id)
        if not recipe:
            return

        self.name_entry.insert(0, recipe.name)

        if recipe.category and recipe.category in self.common_categories:
            self.category_combo.set(recipe.category)
        elif recipe.category:
            self.category_combo.set("Προσθήκη νέας κατηγορίας...")
            self.new_category_entry.config(state=tk.NORMAL)
            self.new_category_entry.insert(0, recipe.category)
        else:
            self.category_combo.set("Επιλέξτε κατηγορία...")

        gr_map = {"Easy": "Εύκολη", "Medium": "Μέτρια", "Hard": "Δύσκολη"}
        if recipe.difficulty in gr_map:
            self.difficulty_combo.set(gr_map[recipe.difficulty])
        elif recipe.difficulty in ["Εύκολη", "Μέτρια", "Δύσκολη"]:
            self.difficulty_combo.set(recipe.difficulty)
        else:
            self.difficulty_combo.set("Μέτρια")

        self.total_time_entry.insert(0, recipe.total_time_minutes)
        self.ingredients = recipe.ingredients
        self.steps = recipe.steps

        self.refresh_ingredients_list()
        self.refresh_steps_list()

        if self.ingredients:
            self.ingredients_locked = True
            self.steps_section_enabled(True)
            self.confirm_button.config(state=tk.DISABLED)
            self.edit_ingredients_button.config(state=tk.NORMAL)
            self.add_ingredient_button.config(state=tk.DISABLED)
            for child in self.ing_btn_frame.winfo_children():
                child.config(state=tk.DISABLED)

    def save(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Σφάλμα", "Το όνομα της συνταγής είναι υποχρεωτικό.")
            return

        category = self.get_selected_category()
        if not category:
            messagebox.showerror("Σφάλμα", "Η κατηγορία της συνταγής είναι υποχρεωτική.")
            return

        difficulty = self.difficulty_var.get()
        if difficulty not in ["Εύκολη", "Μέτρια", "Δύσκολη"]:
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε έγκυρο βαθμό δυσκολίας.")
            return

        try:
            total_time = int(self.total_time_entry.get().strip())
            if total_time <= 0:
                messagebox.showerror("Σφάλμα", "Ο συνολικός χρόνος πρέπει να είναι θετικός αριθμός.")
                return
        except ValueError:
            messagebox.showerror("Σφάλμα", "Ο συνολικός χρόνος πρέπει να είναι έγκυρος ακέραιος.")
            return

        if not self.ingredients:
            messagebox.showerror("Σφάλμα", "Παρακαλώ προσθέστε τουλάχιστον ένα συστατικό.")
            return

        if not self.steps:
            messagebox.showerror("Σφάλμα", "Παρακαλώ προσθέστε τουλάχιστον ένα βήμα.")
            return

        recipe = Recipe(name=name, category=category, difficulty=difficulty, total_time_minutes=total_time)
        recipe.ingredients = self.ingredients
        recipe.steps = self.steps

        if self.recipe_id:
            recipe.id = self.recipe_id
            recipe.update()
        else:
            recipe.save()

        messagebox.showinfo("Επιτυχία", f"Η συνταγή '{name}' αποθηκεύτηκε επιτυχώς!")
        self.parent_app.view_recipes()
        self.window.destroy()

    def open_edit_ingredient_form(self):
        selected = self.ingredients_tree.selection()
        if not selected:
            messagebox.showwarning("Προειδοποίηση", "Επιλέξτε ένα συστατικό για επεξεργασία.")
            return
        all_items = self.ingredients_tree.get_children()
        index = all_items.index(selected[0])
        IngredientFormPage(parent_form=self, index=index, ingredient=self.ingredients[index])

    def delete_ingredient(self):
        selected = self.ingredients_tree.selection()
        if not selected:
            messagebox.showwarning("Προειδοποίηση", "Επιλέξτε ένα συστατικό για διαγραφή.")
            return
        all_items = self.ingredients_tree.get_children()
        index = all_items.index(selected[0])
        self.ingredients.pop(index)
        self.refresh_ingredients_list()

    def open_edit_step_form(self):
        if not self.ingredients_locked:
            messagebox.showwarning("Προειδοποίηση", "Πρέπει πρώτα να επιβεβαιώσετε τα συστατικά.")
            return
        selected = self.steps_tree.selection()
        if not selected:
            messagebox.showwarning("Προειδοποίηση", "Επιλέξτε ένα βήμα για επεξεργασία.")
            return
        all_items = self.steps_tree.get_children()
        index = all_items.index(selected[0])
        step = self.steps[index]
        if not hasattr(step, 'allocations'):
            step.allocations = []
        StepFormPage(parent_form=self, index=index, step=step)

    def delete_step(self):
        selected = self.steps_tree.selection()
        if not selected:
            messagebox.showwarning("Προειδοποίηση", "Επιλέξτε ένα βήμα για διαγραφή.")
            return
        all_items = self.steps_tree.get_children()
        index = all_items.index(selected[0])
        self.steps.pop(index)
        for i, step in enumerate(self.steps):
            step.sequence_order = i + 1
        self.refresh_steps_list()

    def confirm_ingredients(self):
        if not self.ingredients:
            messagebox.showwarning("Προειδοποίηση", "Δεν υπάρχουν συστατικά. Προσθέστε τουλάχιστον ένα συστατικό πρώτα.")
            return

        invalid_ingredients = [ing for ing in self.ingredients if ing.quantity <= 0]
        if invalid_ingredients:
            messagebox.showerror("Σφάλμα", f"Τα παρακάτω συστατικά έχουν μη έγκυρη ποσότητα:\n{', '.join([ing.name for ing in invalid_ingredients])}")
            return

        self.ingredients_locked = True
        self.steps_section_enabled(True)

        self.confirm_button.config(state=tk.DISABLED)
        self.edit_ingredients_button.config(state=tk.NORMAL)

        for child in self.ing_btn_frame.winfo_children():
            child.config(state=tk.DISABLED)

        self.add_ingredient_button.config(state=tk.DISABLED)

        messagebox.showinfo("Επιτυχία", "Τα συστατικά επιβεβαιώθηκαν! Μπορείτε τώρα να προσθέσετε βήματα.\n\nΓια να αλλάξετε τα συστατικά, πατήστε 'Επεξεργασία Συστατικών'.")

    def unlock_ingredients(self):
        if self.steps:
            if not messagebox.askyesno("Προειδοποίηση", "Η επεξεργασία των συστατικών θα διαγράψει όλα τα υπάρχοντα βήματα γιατί τα υλικά στα βήματα θα γίνουν μη έγκυρα.\n\nΘέλετε να συνεχίσετε;"):
                return
            self.steps = []
            self.refresh_steps_list()

        self.ingredients_locked = False
        self.steps_section_enabled(False)

        self.confirm_button.config(state=tk.NORMAL)
        self.edit_ingredients_button.config(state=tk.DISABLED)

        for child in self.ing_btn_frame.winfo_children():
            child.config(state=tk.NORMAL)

        self.add_ingredient_button.config(state=tk.NORMAL)

    def steps_section_enabled(self, enabled):
        state = tk.NORMAL if enabled else tk.DISABLED
        fg_color = "black" if enabled else "gray"

        self.steps_label.config(foreground=fg_color)
        self.add_step_button.config(state=state)

        for child in self.step_btn_frame.winfo_children():
            child.config(state=state)

        if enabled:
            self.steps_tree.config(selectmode='browse')
            for item in self.steps_tree.get_children():
                self.steps_tree.item(item, tags=())
            self.steps_hint_label.grid_remove()
        else:
            self.steps_tree.config(selectmode='none')
            for item in self.steps_tree.get_children():
                self.steps_tree.item(item, tags=('disabled',))
            self.steps_tree.tag_configure('disabled', foreground='gray')
            self.steps_hint_label.grid()


class RecipeExecutePage:
    def __init__(self, recipe_id):
        # Φόρτωση συνταγής από τη βάση
        self.recipe = Recipe.get_recipe_by_id(recipe_id)
        if not self.recipe or not self.recipe.steps:
            messagebox.showerror("Σφάλμα", "Δεν βρέθηκαν βήματα για αυτή τη συνταγή.")
            return

        self.steps = self.recipe.steps      # Λίστα βημάτων
        self.current_index = 0              # Τρέχον βήμα — ξεκινά από 0
        self.timer_seconds = 0              # Δευτερόλεπτα αντίστροφης μέτρησης
        self.timer_running = False          # True=τρέχει, False=σταμάτησε
        self.timer_job = None               # Αναφορά στο after() για ακύρωση αν χρειαστεί

        # Συνολικός χρόνος για υπολογισμό ποσοστού
        self.total_time = sum((s.duration_in_minutes or 0) for s in self.steps)
        if self.total_time == 0:
            self.total_time = 1             # Αποφυγή διαίρεσης με μηδέν

        # Δημιουργία παραθύρου
        self.window = tk.Toplevel()
        self.window.title(f"Εκτέλεση: {self.recipe.name}")
        self.window.geometry("520x560")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)  # X → on_close() αντί για άμεσο κλείσιμο

        # Όνομα συνταγής
        ttk.Label(self.window, text=self.recipe.name, font=("", 14, "bold")).pack(pady=(15, 5))

        # Progress bar ολοκλήρωσης
        pct_frame = ttk.Frame(self.window)
        pct_frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(pct_frame, text="Ολοκλήρωση:").pack(side=tk.LEFT)
        self.progress_var = tk.DoubleVar(value=0)   # Μεταβλητή που ελέγχει το progress bar
        ttk.Progressbar(pct_frame, variable=self.progress_var, maximum=100, length=280).pack(side=tk.LEFT, padx=8)
        self.pct_label = ttk.Label(pct_frame, text="0%")
        self.pct_label.pack(side=tk.LEFT)

        ttk.Separator(self.window, orient="horizontal").pack(fill=tk.X, padx=10, pady=8)

        # Λίστα υλικών συνταγής
        ttk.Label(self.window, text="Υλικά Συνταγής:", font=("", 10, "bold")).pack(anchor=tk.W, padx=20)
        ing_frame = ttk.Frame(self.window)
        ing_frame.pack(fill=tk.X, padx=20, pady=5)
        ing_list = tk.Listbox(ing_frame, height=4, width=60)
        ing_list.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ing_scroll = ttk.Scrollbar(ing_frame, orient=tk.VERTICAL, command=ing_list.yview)
        ing_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        ing_list.configure(yscrollcommand=ing_scroll.set)
        for ing in self.recipe.ingredients:
            ing_list.insert(tk.END, f"  {ing.quantity or ''} {ing.unit or ''} {ing.name or ''}")

        ttk.Separator(self.window, orient="horizontal").pack(fill=tk.X, padx=10, pady=8)

        # Κουμπί Εκκίνησης — κρύβεται μόλις πατηθεί
        self.start_button = ttk.Button(self.window, text="Εκκίνηση", command=self.start_recipe)
        self.start_button.pack(pady=5)

        # Περιοχή βήματος — κρυμμένη αρχικά, εμφανίζεται μετά την Εκκίνηση
        self.step_frame = ttk.LabelFrame(self.window, text="Τρέχον Βήμα", padding=10)

        self.step_num_label = ttk.Label(self.step_frame, text="", font=("", 10, "bold"))
        self.step_num_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))

        ttk.Label(self.step_frame, text="Τίτλος:").grid(row=1, column=0, sticky=tk.W)
        self.step_title_label = ttk.Label(self.step_frame, text="", width=40)
        self.step_title_label.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5)

        ttk.Label(self.step_frame, text="Περιγραφή:").grid(row=2, column=0, sticky=tk.NW, pady=5)
        self.step_text_label = ttk.Label(self.step_frame, text="", wraplength=340, justify=tk.LEFT)
        self.step_text_label.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=5)

        ttk.Label(self.step_frame, text="Χρόνος:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.step_time_label = ttk.Label(self.step_frame, text="", foreground="gray")
        self.step_time_label.grid(row=3, column=1, sticky=tk.W, padx=5)
        self.countdown_label = ttk.Label(self.step_frame, text="", foreground="red", font=("", 11, "bold"))
        self.countdown_label.grid(row=3, column=2, sticky=tk.W, padx=10)

        # Κουμπιά βήματος
        btn_frame = ttk.Frame(self.step_frame)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        self.step_start_btn = ttk.Button(btn_frame, text="Εκκίνηση Βήματος", command=self.start_timer)
        self.step_start_btn.pack(side=tk.LEFT, padx=5)
        self.pause_btn = ttk.Button(btn_frame, text="Pause", command=self.toggle_pause, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        self.previous_btn = ttk.Button(btn_frame, text="Προηγούμενο Βήμα", command=self.previous_step, state=tk.DISABLED)
        self.previous_btn.pack(side=tk.LEFT, padx=5)
        self.next_btn = ttk.Button(btn_frame, text="Επόμενο Βήμα", command=self.next_step)
        self.next_btn.pack(side=tk.LEFT, padx=5)

    def start_recipe(self):
        # Κρύβει το κουμπί Εκκίνηση και εμφανίζει την περιοχή βήματος
        self.start_button.pack_forget()
        self.step_frame.pack(fill=tk.X, padx=20, pady=5)
        self.show_step()

    def show_step(self):
        # Εμφανίζει το τρέχον βήμα — καλείται κάθε φορά που αλλάζει βήμα
        self.stop_timer()
        step = self.steps[self.current_index]

        self.step_num_label.config(text=f"Βήμα {self.current_index + 1} από {len(self.steps)}")
        self.step_title_label.config(text=step.step_name or "")
        self.step_text_label.config(text=step.step_text or "")
        self.step_time_label.config(text=f"{step.duration_in_minutes or 0} λεπτά")
        self.countdown_label.config(text="")

        # Ποσοστό = χρόνος βημάτων που ΤΕΛΕΙΩΣΑΝ / συνολικός χρόνος
        completed_time = sum((self.steps[i].duration_in_minutes or 0) for i in range(self.current_index))
        pct = (completed_time / self.total_time) * 100
        self.progress_var.set(pct)
        self.pct_label.config(text=f"{int(pct)}%")

        self.step_start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(text="Pause", state=tk.DISABLED)

        if self.current_index == 0:
            self.previous_btn.config(state=tk.DISABLED)
        else:
            self.previous_btn.config(state=tk.NORMAL)

        # Αν είναι το τελευταίο βήμα, αλλάζει σε "Ολοκλήρωση"
        if self.current_index == len(self.steps) - 1:
            self.next_btn.config(text="Ολοκλήρωση", command=self.finish)
        else:
            self.next_btn.config(text="Επόμενο Βήμα", command=self.next_step)

    def start_timer(self):
        # Μετατρέπει λεπτά σε δευτερόλεπτα και ξεκινάει την αντίστροφη μέτρηση
        step = self.steps[self.current_index]
        self.timer_seconds = (step.duration_in_minutes or 0) * 60
        self.timer_running = True
        self.step_start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self._tick()

    def _tick(self):
        # Εκτελείται κάθε 1 δευτερόλεπτο — η καρδιά της αντίστροφης μέτρησης
        if not self.timer_running:
            return
        if self.timer_seconds > 0:
            mins, secs = divmod(self.timer_seconds, 60)     # Μετατροπή σε MM:SS
            self.countdown_label.config(text=f"{mins:02d}:{secs:02d}")
            self.timer_seconds -= 1
            self.timer_job = self.window.after(1000, self._tick)  # Επόμενο tick σε 1 δευτερόλεπτο
        else:
            self.countdown_label.config(text="Τελος!")
            self.timer_running = False
            messagebox.showinfo("Χρόνος!", "Ο χρόνος του βήματος ολοκληρώθηκε!")

    def toggle_pause(self):
        # Εναλλάσσει Pause/Resume
        if self.timer_running:
            self.timer_running = False
            if self.timer_job:
                self.window.after_cancel(self.timer_job)
            self.pause_btn.config(text="Resume")
        else:
            self.timer_running = True
            self.pause_btn.config(text="Pause")
            self._tick()

    def stop_timer(self):
        # Σταματάει πλήρως τον χρονομετρητή — σημαντικό για αποφυγή crash
        self.timer_running = False
        if self.timer_job:
            self.window.after_cancel(self.timer_job)
            self.timer_job = None

    def previous_step(self):
        if self.current_index > 0:
            self.stop_timer()
            self.current_index -= 1
            self.show_step()

    def next_step(self):
        self.current_index += 1
        self.show_step()

    def finish(self):
        self.stop_timer()
        self.progress_var.set(100)
        self.pct_label.config(text="100%")
        messagebox.showinfo("Ολοκλήρωση!", f"Η συνταγή '{self.recipe.name}' ολοκληρώθηκε!")
        self.window.destroy()

    def on_close(self):
        # ΠΡΩΤΑ σταμάτα τον χρονομετρητή — αλλιώς crash από pending after()
        self.stop_timer()
        self.window.destroy()

# Κύρια κλάση της εφαρμογής διαχείρισης συνταγών
class RecipeApp:
    def __init__(self, root):
        """
        Αρχικοποίηση της κύριας εφαρμογής
        root: το κύριο παράθυρο tkinter
        """
        self.root = root

        # Ρύθμιση μεγέθους και κεντραρίσματος του παραθύρου
        width = 700
        height = 500

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Υπολογισμός θέσης ώστε το παράθυρο να εμφανίζεται κεντραρισμένο
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))

        root.geometry(f"{width}x{height}+{x}+{y}")
        root.title("Διαχείριση Συνταγών")

        # Κουμπιά κύριας οθόνης
        ttk.Button(root, text="Προσθήκη Συνταγής", command=self.open_add_page).grid(row=0, column=0, pady=10, padx=10)
        ttk.Button(root, text="Ενημέρωση Συνταγής", command=self.open_update_page).grid(row=0, column=1, pady=10, padx=10)
        ttk.Button(root, text="Διαγραφή Συνταγής", command=self.delete_recipe).grid(row=0, column=2, pady=10, padx=10)
        ttk.Button(root, text="Εμφάνιση Συνταγών", command=self.view_recipes).grid(row=0, column=3, pady=10, padx=10)
        ttk.Button(root, text="Εμφάνιση Συνταγης", command=self.view_recipe).grid(row=1, column=1, pady=10, padx=10)
        ttk.Button(root, text="Αναζήτηση Συνταγής", command=self.recipe_lookup).grid(row=1, column=2, pady=10, padx=10)
        ttk.Button(root, text="Εκτέλεση Συνταγής", command=self.recipe_launch).grid(row=1, column=3, pady=10, padx=10)

        # Listbox για εμφάνιση όλων των συνταγών
        self.recipes_table = ttk.Treeview(root, columns=('Αριθμός', 'Όνομα', 'Κατηγορία', 'Δυσκολία', 'Χρόνος Εκτέλεσης'), show='headings')
        self.recipes_table.heading('Αριθμός', text='Αριθμός')
        self.recipes_table.heading('Όνομα', text='Όνομα Συνταγής')
        self.recipes_table.heading('Κατηγορία', text='Κατηγορία')
        self.recipes_table.heading('Δυσκολία', text='Δυσκολία')
        self.recipes_table.heading('Χρόνος Εκτέλεσης', text='Χρόνος Εκτέλεσης')

        # Ρύθμιση πλάτους στηλών (προαιρετικά)
        self.recipes_table.column('Αριθμός', width=55)
        self.recipes_table.column('Όνομα', width=200)
        self.recipes_table.column('Κατηγορία', width=100)
        self.recipes_table.column('Δυσκολία', width=100)
        self.recipes_table.column('Χρόνος Εκτέλεσης', width=150)

        self.recipes_table.grid(row=2, column=0, columnspan=4, padx=5, pady=15)


    def open_add_page(self):
        """Open form to add new recipe"""
        RecipeFormPage(parent_app=self)

    def open_update_page(self):
        """Open form to update selected recipe"""
        selected = self.recipes_table.selection()
        if not selected:
            messagebox.showwarning("Προειδοποίηση", "Επιλέξτε μια συνταγή για ενημέρωση.")
            return
        
        real_id = int(self.recipes_table.item(selected[0], 'tags')[0])
        RecipeFormPage(parent_app=self, recipe_id=real_id)

    def delete_recipe(self):
        """Delete selected recipe"""
        selected = self.recipes_table.selection()
        if not selected:
            messagebox.showwarning("Προειδοποίηση", "Επιλέξτε μια συνταγή για διαγραφή.")
            return
        
        values = self.recipes_table.item(selected[0])['values']
        recipe_id = values[0]
        recipe_name = values[1]
        
        if messagebox.askyesno("Επιβεβαίωση", f"Θέλετε να διαγράψετε τη συνταγή '{recipe_name}';"):
            Recipe.delete_by_id(recipe_id)
            self.view_recipes()
            messagebox.showinfo("Επιτυχία", "Η συνταγή διαγράφηκε!")

    def view_recipe(self):
        """Display selected recipe details in a new window"""
        selected = self.recipes_table.selection()
        if not selected:
            messagebox.showerror("Σφάλμα", "Επιλέξτε μια συνταγή για εμφάνιση")
            return
        
        values = self.recipes_table.item(selected[0])['values']
        recipe_id = values[0]
        
        # Get complete recipe from model
        recipe = Recipe.get_recipe_by_id(recipe_id)
        if not recipe:
            messagebox.showerror("Σφάλμα", "Δεν βρέθηκε η συνταγή")
            return
        
        # Create dialog window
        dialog = tk.Toplevel()
        dialog.title(f"Συνταγή: {recipe.name}")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create main frame with scrollbar
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas and scrollbar for scrolling
        canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        row = 0
        
        # Section 1: Recipe Header
        tk.Label(scrollable_frame, text=recipe.name, font=("Arial", 14, "bold")).grid(
            row=row, column=0, columnspan=2, pady=10)
        row += 1
        
        tk.Label(scrollable_frame, text=f"Κατηγορία: {recipe.category}").grid(
            row=row, column=0, sticky="w", padx=20, pady=2)
        tk.Label(scrollable_frame, text=f"Δυσκολία: {recipe.difficulty}").grid(
            row=row, column=1, sticky="w", padx=20, pady=2)
        row += 1
        
        tk.Label(scrollable_frame, text=f"Συνολικός Χρόνος: {recipe.total_time_minutes} λεπτά").grid(
            row=row, column=0, columnspan=2, sticky="w", padx=20, pady=2)
        row += 2
        
        # Section 2: Ingredients
        tk.Label(scrollable_frame, text="Συστατικά:", font=("Arial", 11, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=20, pady=(10,5))
        row += 1
        
        if recipe.ingredients:
            for ing in recipe.ingredients:
                ing_text = f"• {ing.name} - {ing.quantity}"
                if ing.unit:
                    ing_text += f" {ing.unit}"
                if ing.notes:
                    ing_text += f" ({ing.notes})"
                tk.Label(scrollable_frame, text=ing_text, wraplength=500, justify=tk.LEFT).grid(
                    row=row, column=0, columnspan=2, sticky="w", padx=40, pady=2)
                row += 1
        else:
            tk.Label(scrollable_frame, text="Δεν υπάρχουν συστατικά", font=("Arial", 10, "italic")).grid(
                row=row, column=0, columnspan=2, sticky="w", padx=40, pady=2)
            row += 1
        
        row += 1
        
        # Section 3: Steps
        tk.Label(scrollable_frame, text="Βήματα Εκτέλεσης:", font=("Arial", 11, "bold")).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=20, pady=(10,5))
        row += 1
        
        if recipe.steps:
            for i, step in enumerate(recipe.steps, 1):
                step_text = f"{i}. {step.step_name}"
                if step.step_text:
                    step_text += f": {step.step_text}"
                if step.duration_in_minutes:
                    step_text += f" ({step.duration_in_minutes} λεπτά)"
                tk.Label(scrollable_frame, text=step_text, wraplength=500, justify=tk.LEFT).grid(
                    row=row, column=0, columnspan=2, sticky="w", padx=40, pady=5)
                row += 1
        else:
            tk.Label(scrollable_frame, text="Δεν υπάρχουν βήματα", font=("Arial", 10, "italic")).grid(
                row=row, column=0, columnspan=2, sticky="w", padx=40, pady=2)
            row += 1
        
        row += 1
        
        # Close button
        tk.Button(scrollable_frame, text="Κλείσιμο", command=dialog.destroy, 
                bg="gray", fg="white", padx=20, pady=5).grid(
                row=row, column=0, columnspan=2, pady=20)

    def view_recipes(self):
        for item in self.recipes_table.get_children():
            self.recipes_table.delete(item)
        
        recipes_data = Recipe.get_all_recipes()  # ← Call model
        
        for counter, row in enumerate(recipes_data, 1):  # Start from 1
            self.recipes_table.insert('', 'end', values=(
                counter,           # ← Sequential number, not database ID
                row[1],            # name
                row[2],            # category
                row[3],            # difficulty
                f"{row[4]} λεπτά"  # time
            ), tags=(str(row[0]),))


    def recipe_lookup(self):
        search_term = simpledialog.askstring("Αναζήτηση", "Εισάγετε όνομα συνταγής:")
        if search_term:
            recipes_data = Recipe.search_by_name(search_term)  # ← Call model
            
            # Clear and display results
            for item in self.recipes_table.get_children():
                self.recipes_table.delete(item)
            
            for counter, row in enumerate(recipes_data, 1):
                # Store the real database ID as a hidden value using 'tags' or 'values'
                self.recipes_table.insert('', 'end', values=(
                    counter,           # Display sequential number
                    row[1],            # name
                    row[2],            # category
                    row[3],            # difficulty
                    f"{row[4]} λεπτά"  # time
                ), tags=(str(row[0]),))  # Store real ID in tags

    def recipe_launch(self):
        """Launch the recipe execution mode"""
        selected = self.recipes_table.selection()
        if not selected:
            messagebox.showerror("Σφάλμα", "Επιλέξτε μια συνταγή για εκτέλεση.")
            return
        
        # Get the real recipe ID from tags (stored during view_recipes)
        real_id = int(self.recipes_table.item(selected[0], 'tags')[0])
        
        # Pass the recipe_id to RecipeExecutePage
        RecipeExecutePage(recipe_id=real_id)
    

# Σημείο εισόδου της εφαρμογής
if __name__ == "__main__":
    root = tk.Tk()              # Δημιουργία του κύριου παραθύρου
    app = RecipeApp(root)       # Δημιουργία της εφαρμογής
    root.mainloop()             # Ε