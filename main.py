# =============================================================================
# ΠΛΗΡΗΣ ΚΩΔΙΚΑΣ - ΜΕ CTkTextbox ΣΤΑ ΒΗΜΑΤΑ ΚΑΙ ΔΙΟΡΘΩΜΕΝΑ ΧΡΩΜΑΤΑ ΣΤΟΥΣ ΠΙΝΑΚΕΣ
# =============================================================================

from db import DatabaseConn
from models import Recipe, Ingredient, Step
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
import ctypes
import datetime

# --- ΒΟΗΘΗΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ ---

def set_window_icon(window):
    """Βάζει το εικονίδιο chef.ico στο παράθυρο που της δίνουμε."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(current_dir, "chef.ico")
        window.after(200, lambda: window.iconbitmap(icon_path))
    except Exception:
        pass

def enable_right_click_menu(widget):
    """Προσθέτει μενού Δεξιού Κλικ (Αποκοπή/Αντιγραφή/Επικόλληση) με ασφαλή εγγενή τρόπο."""
    if hasattr(widget, '_textbox'): target = widget._textbox
    elif hasattr(widget, '_entry'): target = widget._entry
    else: target = widget
        
    menu = tk.Menu(target, tearoff=False, font=("Segoe UI", 11), bg="#2a2d2e", fg="white", activebackground="#1f538d")
    
    def cut(): 
        try: target.event_generate("<<Cut>>")
        except: pass
    def copy(): 
        try: target.event_generate("<<Copy>>")
        except: pass
    def paste(): 
        try: target.event_generate("<<Paste>>")
        except: pass
        
    menu.add_command(label="Αποκοπή    (Ctrl+X)", command=cut)
    menu.add_command(label="Αντιγραφή  (Ctrl+C)", command=copy)
    menu.add_command(label="Επικόλληση (Ctrl+V)", command=paste)
    
    def show_menu(event):
        target.focus_set()
        menu.tk_popup(event.x_root, event.y_root)
        
    target.bind("<Button-3>", show_menu)

def center_and_size_window(window, desired_w, desired_h):
    """Κεντράρει το παράθυρο και δεν το αφήνει να βγει εκτός οθόνης."""
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    final_w = min(desired_w, int(screen_w * 0.95))
    final_h = min(desired_h, int(screen_h * 0.90))
    window.geometry(f"{final_w}x{final_h}")
    window.attributes("-topmost", True)
    window.after(200, lambda: window.attributes("-topmost", False))

def setup_autocomplete(combo_widget, full_list):
    """ΜΗΧΑΝΙΣΜΟΣ GOOGLE-STYLE AUTOCOMPLETE"""
    listbox = None 

    def close_listbox(event=None):
        nonlocal listbox
        if listbox:
            listbox.destroy()
            listbox = None

    def select_item(event=None):
        if listbox and listbox.curselection():
            index = listbox.curselection()[0]
            item = listbox.get(index)
            combo_widget.set(item) 
            close_listbox()
            combo_widget._entry.focus_set()

    def on_keyrelease(event):
        nonlocal listbox
        if event.keysym in ['Up', 'Down', 'Return', 'Escape', 'Tab']:
            return

        typed = combo_widget.get().lower().strip()
        if not typed or typed == "επιλέξτε..." or typed == "επιλέξτε ή πληκτρολογήστε...":
            close_listbox()
            return

        filtered = [item for item in full_list if item.lower().startswith(typed) and item.lower() != typed][:6]

        if not filtered:
            close_listbox()
            return

        if not listbox:
            mode = ctk.get_appearance_mode()
            bg_color = "#f9f9f9" if mode == "Light" else "#2b2b2b"
            fg_color = "black" if mode == "Light" else "white"
            hl_color = "#3b8ed0" if mode == "Light" else "#1f538d"

            listbox = tk.Listbox(combo_widget.master, font=("Segoe UI", 13), 
                                 bg=bg_color, fg=fg_color, selectbackground=hl_color, 
                                 bd=1, relief="solid", highlightthickness=0)
            listbox.bind("<Double-Button-1>", select_item)
            listbox.bind("<Return>", select_item)
            listbox.bind("<Escape>", close_listbox)
            
            listbox.place(in_=combo_widget, x=0, rely=1, relwidth=1)
            listbox.lift()

        listbox.delete(0, tk.END)
        for item in filtered:
            listbox.insert(tk.END, item)
        
        list_height = len(filtered) * 26
        listbox.place_configure(height=list_height)

    def on_down_arrow(event):
        if listbox and listbox.size() > 0:
            listbox.focus_set()
            listbox.selection_set(0)
            listbox.activate(0)

    def on_return(event):
        if listbox and listbox.size() > 0:
            item = listbox.get(0)
            combo_widget.set(item)
            close_listbox()

    def on_focusout(event):
        combo_widget._entry.after(150, check_focus)
        
    def check_focus():
        try:
            focus_widget = combo_widget.focus_get()
            if focus_widget != listbox and focus_widget != combo_widget._entry:
                close_listbox()
        except: pass

    target = combo_widget._entry
    target.bind('<KeyRelease>', on_keyrelease)
    target.bind('<Down>', on_down_arrow)
    target.bind('<Return>', on_return)
    target.bind('<FocusOut>', on_focusout)


# --- 1. ΔΗΜΙΟΥΡΓΙΑ ΤΗΣ ΒΑΣΗΣ ΔΕΔΟΜΕΝΩΝ ---
with DatabaseConn("recipe_database.db") as rcp_db:
    rcp_db.execute("""CREATE TABLE IF NOT EXISTS recipes(
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, difficulty TEXT, total_time_minutes INTEGER)""")
    rcp_db.execute("""CREATE TABLE IF NOT EXISTS ingredients(
        id INTEGER PRIMARY KEY AUTOINCREMENT, recipe_id INTEGER, name TEXT, quantity REAL, unit TEXT, notes TEXT,
        FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE)""")
    rcp_db.execute("""CREATE TABLE IF NOT EXISTS steps(
        id INTEGER PRIMARY KEY AUTOINCREMENT, recipe_id INTEGER, step_name TEXT, sequence_order INTEGER, 
        step_text TEXT, duration_in_minutes INTEGER, FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE)""")
    rcp_db.execute("""CREATE TABLE IF NOT EXISTS step_ingredients(
        id INTEGER PRIMARY KEY AUTOINCREMENT, ingredient_id INTEGER, step_id INTEGER, quantity REAL, unit TEXT, notes TEXT,
        FOREIGN KEY (step_id) REFERENCES steps(id) ON DELETE CASCADE, FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE)""")

ctk.set_default_color_theme("blue")

# --- 2. ΚΛΑΣΕΙΣ ΦΟΡΜΩΝ ---

class IngredientFormPage:
    def __init__(self, parent_form, index=None, ingredient=None):
        self.parent_form = parent_form
        self.index = index
        self.window = ctk.CTkToplevel()
        self.window.title("Επεξεργασία Συστατικού" if index is not None else "Προσθήκη Συστατικού")
        center_and_size_window(self.window, 550, 500)
        set_window_icon(self.window)
        
        scroll = ctk.CTkScrollableFrame(self.window, fg_color="transparent")
        scroll.pack(fill=tk.BOTH, expand=True)

        base_ingredients = [
            "Αλάτι", "Αλάτι χοντρό", "Πιπέρι", "Πιπέρι μαύρο", "Ελαιόλαδο", "Ηλιέλαιο", "Ξύδι", "Λεμόνι", "Νερό",
            "Αλεύρι Γ.Ο.Χ.", "Αλεύρι που φουσκώνει", "Ζάχαρη κρυσταλλική", "Ζάχαρη άχνη", "Ζάχαρη καστανή",
            "Κρεμμύδι ξερό", "Κρεμμύδι φρέσκο", "Σκόρδο", "Ντομάτα", "Πατάτα", "Καρότο", "Πιπεριά",
            "Αυγό", "Γάλα", "Γάλα εβαπορέ", "Βούτυρο", "Γιαούρτι", "Κρέμα γάλακτος", 
            "Τυρί φέτα", "Τυρί γκούντα", "Ρίγανη", "Θυμάρι", "Μαϊντανός", "Δυόσμος", "Κανέλα"
        ]
        
        try:
            with DatabaseConn("recipe_database.db") as db:
                db.execute("SELECT DISTINCT name FROM ingredients")
                db_ings = [row[0] for row in db.fetchall() if row[0] and row[0] not in base_ingredients]
                base_ingredients.extend(db_ings)
        except Exception: pass

        ctk.CTkLabel(scroll, text="Όνομα Συστατικού:", font=("Segoe UI", 13)).pack(pady=(15,0), padx=20, anchor="w")
        self.name_combo = ctk.CTkComboBox(scroll, values=base_ingredients, width=350, font=("Segoe UI", 14))
        self.name_combo.pack(pady=5, padx=20, anchor="w")
        self.name_combo.set(ingredient.name if ingredient and ingredient.name else "Επιλέξτε ή πληκτρολογήστε...")
        enable_right_click_menu(self.name_combo)
        setup_autocomplete(self.name_combo, base_ingredients)
        
        ctk.CTkLabel(scroll, text="Ποσότητα:", font=("Segoe UI", 13)).pack(padx=20, anchor="w")
        self.quantity_entry = ctk.CTkEntry(scroll, width=150, font=("Segoe UI", 14))
        self.quantity_entry.pack(pady=5, padx=20, anchor="w")
        if ingredient and ingredient.quantity: self.quantity_entry.insert(0, str(ingredient.quantity))
        enable_right_click_menu(self.quantity_entry)
        
        existing_units = ["kg", "g", "mg", "L", "ml", "κουταλιά σούπας", "κουταλιά γλυκού", "τεμάχιο", "κούπα", "πρέζα"]
        try:
            with DatabaseConn("recipe_database.db") as db:
                db.execute("SELECT DISTINCT unit FROM ingredients")
                db_units = [row[0] for row in db.fetchall() if row[0] and row[0] not in existing_units]
                existing_units.extend(db_units)
        except Exception: pass

        ctk.CTkLabel(scroll, text="Μονάδα:", font=("Segoe UI", 13)).pack(padx=20, anchor="w")
        self.unit_combo = ctk.CTkComboBox(scroll, values=existing_units, width=250, font=("Segoe UI", 14))
        self.unit_combo.pack(pady=5, padx=20, anchor="w")
        self.unit_combo.set(ingredient.unit if ingredient and ingredient.unit else "Επιλέξτε...")
        enable_right_click_menu(self.unit_combo)
        setup_autocomplete(self.unit_combo, existing_units)
        
        ctk.CTkLabel(scroll, text="Σημειώσεις:", font=("Segoe UI", 13)).pack(padx=20, anchor="w")
        self.notes_entry = ctk.CTkEntry(scroll, width=350, font=("Segoe UI", 14))
        self.notes_entry.pack(pady=5, padx=20, anchor="w")
        if ingredient and ingredient.notes: self.notes_entry.insert(0, ingredient.notes)
        enable_right_click_menu(self.notes_entry)
        
        ctk.CTkButton(scroll, text="Αποθήκευση", command=self.save, font=("Segoe UI", 14, "bold"), height=40, cursor="hand2").pack(pady=30)

    def save(self):
        name = self.name_combo.get().strip()
        if not name or name == "Επιλέξτε ή πληκτρολογήστε...": return messagebox.showerror("Σφάλμα", "Το όνομα είναι υποχρεωτικό.")
        try:
            qty = float(self.quantity_entry.get().replace(',', '.'))
            if qty <= 0: return messagebox.showerror("Σφάλμα", "Η ποσότητα πρέπει να είναι θετική.")
            
            unit_val = self.unit_combo.get().strip()
            if unit_val == "Επιλέξτε...": unit_val = ""
                
            ingredient = Ingredient(name=name, quantity=qty, unit=unit_val, notes=self.notes_entry.get().strip())
            
            if self.index is not None: self.parent_form.ingredients[self.index] = ingredient
            else: self.parent_form.ingredients.append(ingredient)
            self.parent_form.refresh_ingredients_list()
            self.window.destroy()
        except ValueError: messagebox.showerror("Σφάλμα", "Εισάγετε έγκυρο αριθμό (επιτρέπεται και κόμμα).")

class StepFormPage:
    def __init__(self, parent_form, index=None, step=None):
        self.parent_form = parent_form
        self.index = index
        self.step_allocations = []
        self.window = ctk.CTkToplevel()
        self.window.title("Επεξεργασία Βήματος" if index is not None else "Προσθήκη Βήματος")
        center_and_size_window(self.window, 750, 700)
        set_window_icon(self.window)
        
        scroll = ctk.CTkScrollableFrame(self.window, fg_color="transparent")
        scroll.pack(fill=tk.BOTH, expand=True)

        existing_step_names = [
            "Προετοιμασία", "Κόψιμο", "Σοτάρισμα", "Τσιγάρισμα", "Βράσιμο", 
            "Ψήσιμο", "Τηγάνισμα", "Ανάμειξη", "Ζύμωμα", "Χτύπημα", 
            "Μαρινάρισμα", "Γαρνίρισμα", "Σερβίρισμα"
        ]
        try:
            with DatabaseConn("recipe_database.db") as db:
                db.execute("SELECT DISTINCT step_name FROM steps")
                db_steps = [row[0] for row in db.fetchall() if row[0] and row[0] not in existing_step_names]
                existing_step_names.extend(db_steps)
        except Exception: pass

        ctk.CTkLabel(scroll, text="Τίτλος Βήματος:", font=("Segoe UI", 13)).pack(pady=(15,0), padx=20, anchor="w")
        self.step_name_combo = ctk.CTkComboBox(scroll, values=existing_step_names, width=400, font=("Segoe UI", 14))
        self.step_name_combo.pack(pady=5, padx=20, anchor="w")
        self.step_name_combo.set(step.step_name if step and step.step_name else "Επιλέξτε ή πληκτρολογήστε...")
        enable_right_click_menu(self.step_name_combo)
        setup_autocomplete(self.step_name_combo, existing_step_names)

        ctk.CTkLabel(scroll, text="Περιγραφή:", font=("Segoe UI", 13)).pack(padx=20, anchor="w")
        # --- ΝΕΟ: Αντικατάσταση CTkEntry με CTkTextbox για μεγάλες παραγράφους με scrollbar ---
        self.step_text_entry = ctk.CTkTextbox(scroll, width=500, height=120, font=("Segoe UI", 14))
        self.step_text_entry.pack(pady=5, padx=20, anchor="w")
        enable_right_click_menu(self.step_text_entry)

        ctk.CTkLabel(scroll, text="Διάρκεια (λεπτά):", font=("Segoe UI", 13)).pack(padx=20, anchor="w")
        self.duration_entry = ctk.CTkEntry(scroll, width=100, font=("Segoe UI", 14))
        self.duration_entry.pack(pady=5, padx=20, anchor="w")
        enable_right_click_menu(self.duration_entry)

        h_f = ctk.CTkFrame(scroll, fg_color="transparent")
        h_f.pack(fill=tk.X, padx=20, pady=(20,0))
        ctk.CTkLabel(h_f, text="Υλικά για αυτό το βήμα:", font=("Segoe UI", 15, "bold")).pack(side=tk.LEFT)
        ctk.CTkButton(h_f, text="+ Προσθήκη Υλικού", command=self.add_ingredient_from_existing, width=150, cursor="hand2").pack(side=tk.RIGHT)

        self.ingredients_tree = ttk.Treeview(scroll, columns=('Όνομα', 'Ποσότητα', 'Μονάδα'), show='headings', height=5)
        for col in self.ingredients_tree['columns']: self.ingredients_tree.heading(col, text=col)
        self.ingredients_tree.pack(fill=tk.X, padx=20, pady=10)

        ctk.CTkButton(scroll, text="Αφαίρεση Επιλεγμένου", fg_color="#8b0000", hover_color="#ff1a1a", command=self.remove_selected_ingredient, cursor="hand2").pack(pady=5)
        ctk.CTkButton(scroll, text="Αποθήκευση Βήματος", command=self.save, font=("Segoe UI", 15, "bold"), height=45, fg_color="#1f538d", cursor="hand2").pack(pady=30)

        if step:
            if step.step_text: self.step_text_entry.insert("0.0", step.step_text)
            if step.duration_in_minutes: self.duration_entry.insert(0, str(step.duration_in_minutes))
            if hasattr(step, 'allocations'): 
                self.step_allocations = step.allocations.copy()
                self.refresh_ingredients_list()

    def add_ingredient_from_existing(self):
        if not self.parent_form.ingredients: return messagebox.showwarning("!", "Προσθέστε πρώτα υλικά στη συνταγή.")
        dialog = ctk.CTkToplevel()
        center_and_size_window(dialog, 500, 500)
        set_window_icon(dialog)

        def get_avail():
            ing_list, ing_data = [], []
            for idx, ing in enumerate(self.parent_form.ingredients):
                used = 0
                for i, step in enumerate(self.parent_form.steps):
                    if hasattr(step, 'allocations'):
                        if self.index is not None and i == self.index: continue
                        for alloc in step.allocations:
                            if alloc.get('temp_id') is not None and alloc.get('temp_id') == idx:
                                used += alloc.get('quantity', 0)
                            elif ing.id is not None and alloc.get('ingredient_id') == ing.id:
                                used += alloc.get('quantity', 0)
                                
                for alloc in self.step_allocations:
                    if alloc.get('temp_id') is not None and alloc.get('temp_id') == idx:
                        used += alloc.get('quantity', 0)
                    elif ing.id is not None and alloc.get('ingredient_id') == ing.id:
                        used += alloc.get('quantity', 0)
                        
                avail = round(ing.quantity - used, 5)
                if avail > 0.001:
                    ing_list.append(f"{ing.name} (Διαθέσιμο: {avail} {ing.unit or ''})")
                    ing_data.append({'temp_id': idx, 'id': ing.id, 'name': ing.name, 'avail': avail, 'unit': ing.unit})
            return ing_list, ing_data

        ing_list, ing_data = get_avail()
        if not ing_list: 
            messagebox.showinfo("!", "Δεν υπάρχουν άλλα διαθέσιμα υλικά.")
            dialog.destroy()
            return

        combo = ctk.CTkComboBox(dialog, values=ing_list, width=350); combo.pack(pady=20)
        qty_ent = ctk.CTkEntry(dialog, placeholder_text="Ποσότητα"); qty_ent.pack(pady=10)
        enable_right_click_menu(qty_ent)

        def confirm():
            try:
                sel = ing_data[ing_list.index(combo.get())]
                val = float(qty_ent.get().replace(',', '.'))
                if val <= 0 or val > sel['avail'] + 0.001: return messagebox.showerror("Λάθος", "Μη έγκυρη ποσότητα.")
                self.step_allocations.append({'temp_id': sel['temp_id'], 'ingredient_id': sel['id'], 'ingredient_name': sel['name'], 'quantity': val, 'unit': sel['unit']})
                self.refresh_ingredients_list(); dialog.destroy()
            except ValueError: messagebox.showerror("!", "Εισάγετε αριθμό.")
        
        ctk.CTkButton(dialog, text="Προσθήκη", command=confirm, cursor="hand2").pack(pady=20)

    def refresh_ingredients_list(self):
        for i in self.ingredients_tree.get_children(): self.ingredients_tree.delete(i)
        for i, a in enumerate(self.step_allocations): 
            tag = 'even' if i % 2 == 0 else 'odd'
            self.ingredients_tree.insert('', 'end', values=(a['ingredient_name'], a['quantity'], a['unit'] or ""), tags=(tag,))

    def remove_selected_ingredient(self):
        sel = self.ingredients_tree.selection()
        if sel: idx = self.ingredients_tree.get_children().index(sel[0]); self.step_allocations.pop(idx); self.refresh_ingredients_list()

    def save(self):
        name = self.step_name_combo.get().strip()
        text = self.step_text_entry.get("0.0", "end").strip() # Λήψη κειμένου από το CTkTextbox
        if not name or name == "Επιλέξτε ή πληκτρολογήστε..." or not text: return messagebox.showerror("!", "Συμπληρώστε τα πεδία.")
        try:
            dur = int(float(self.duration_entry.get().replace(',', '.')))
            step = Step(step_name=name, step_text=text, duration_in_minutes=dur, sequence_order=(self.index+1 if self.index is not None else len(self.parent_form.steps)+1))
            step.allocations = self.step_allocations
            if self.index is not None: self.parent_form.steps[self.index] = step
            else: self.parent_form.steps.append(step)
            self.parent_form.refresh_steps_list(); self.window.destroy()
        except ValueError: messagebox.showerror("!", "Η διάρκεια πρέπει να είναι αριθμός.")


class RecipeFormPage:
    def __init__(self, parent_app, recipe_id=None):
        self.parent_app = parent_app
        self.recipe_id = recipe_id
        self.ingredients = []
        self.steps = []
        self.ingredients_locked = False

        self.window = ctk.CTkToplevel()
        self.window.title("Φόρμα Συνταγής")
        center_and_size_window(self.window, 900, 850)
        set_window_icon(self.window)

        self.scroll = ctk.CTkScrollableFrame(self.window, fg_color="transparent")
        self.scroll.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        info_frame = ctk.CTkFrame(self.scroll)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        ctk.CTkLabel(info_frame, text="Όνομα Συνταγής:", font=("Segoe UI", 14)).grid(row=0, column=0, sticky=tk.W, padx=15, pady=10)
        self.name_entry = ctk.CTkEntry(info_frame, width=400, font=("Segoe UI", 14))
        self.name_entry.grid(row=0, column=1, sticky=tk.W, padx=15, pady=10)
        enable_right_click_menu(self.name_entry)

        base_categories = [
            "Ορεκτικά", "Σαλάτες", "Σούπες", "Κυρίως Πιάτα", "Ζυμαρικά", "Ρύζι",
            "Λαδερά", "Φαγητά φούρνου", "Ψητά", "Τηγανητά", "Μαγειρευτά", "Κρεατικά",
            "Κοτόπουλο", "Ψάρια & Θαλασσινά", "Χορτοφαγικά", "Vegetarian", "Vegan",
            "Πίτες", "Αλμυρές πίτες", "Γλυκές πίτες", "Αρτοσκευάσματα", "Ψωμιά",
            "Πρωινό", "Σνακ", "Γλυκά", "Επιδόρπια", "Παγωτά", "Ροφήματα", "Ποτά",
            "Σάλτσες", "Ντιπ", "Μαρμελάδες & Γλυκά κουταλιού", "Κονσέρβες",
            "Ζυμωτά", "Παραδοσιακά", "Νηστίσιμα", "Κατοικίδιων"
        ]
        try:
            db_recipes = Recipe.get_all_recipes()
            for r in db_recipes:
                if r[2] and r[2] not in base_categories: base_categories.append(r[2])
        except Exception: pass

        ctk.CTkLabel(info_frame, text="Κατηγορία:", font=("Segoe UI", 14)).grid(row=1, column=0, sticky=tk.W, padx=15, pady=10)
        self.category_combo = ctk.CTkComboBox(info_frame, values=base_categories, width=400, font=("Segoe UI", 14))
        self.category_combo.grid(row=1, column=1, sticky=tk.W, padx=15, pady=10)
        enable_right_click_menu(self.category_combo)
        setup_autocomplete(self.category_combo, base_categories)

        ctk.CTkLabel(info_frame, text="Δυσκολία:", font=("Segoe UI", 14)).grid(row=2, column=0, sticky=tk.W, padx=15, pady=10)
        self.difficulty_combo = ctk.CTkComboBox(info_frame, values=["Εύκολη", "Μέτρια", "Δύσκολη"], width=200, font=("Segoe UI", 14))
        self.difficulty_combo.grid(row=2, column=1, sticky=tk.W, padx=15, pady=10)

        ctk.CTkLabel(info_frame, text="Συνολικός Χρόνος (λεπτά):", font=("Segoe UI", 14)).grid(row=3, column=0, sticky=tk.W, padx=15, pady=10)
        self.total_time_entry = ctk.CTkEntry(info_frame, width=150, font=("Segoe UI", 14))
        self.total_time_entry.grid(row=3, column=1, sticky=tk.W, padx=15, pady=10)
        enable_right_click_menu(self.total_time_entry)

        ctk.CTkLabel(self.scroll, text="Λίστα Συστατικών", font=("Segoe UI", 17, "bold")).pack(pady=(20, 5))
        self.ing_tree = ttk.Treeview(self.scroll, columns=('Όνομα', 'Ποσότητα', 'Μονάδα', 'Σημειώσεις'), show='headings', height=5)
        for col in self.ing_tree['columns']: self.ing_tree.heading(col, text=col)
        self.ing_tree.pack(fill=tk.X, padx=20, pady=10)

        btn_f = ctk.CTkFrame(self.scroll, fg_color="transparent"); btn_f.pack(pady=5)
        self.add_ing_btn = ctk.CTkButton(btn_f, text="+ Προσθήκη Υλικού", command=self.open_ingredient_form, cursor="hand2")
        self.add_ing_btn.pack(side=tk.LEFT, padx=5)
        self.edit_ing_btn = ctk.CTkButton(btn_f, text="Επεξεργασία Υλικού", command=self.edit_ingredient, cursor="hand2")
        self.edit_ing_btn.pack(side=tk.LEFT, padx=5)
        self.del_ing_btn = ctk.CTkButton(btn_f, text="Διαγραφή Υλικού", fg_color="#8b0000", hover_color="#ff1a1a", command=self.delete_ingredient, cursor="hand2")
        self.del_ing_btn.pack(side=tk.LEFT, padx=5)

        self.confirm_btn = ctk.CTkButton(self.scroll, text="✓ Επιβεβαίωση Υλικών", fg_color="#28a745", hover_color="#218838", command=self.confirm_ingredients, font=("Segoe UI", 13, "bold"), height=35, cursor="hand2")
        self.confirm_btn.pack(pady=15)
        self.unlock_btn = ctk.CTkButton(self.scroll, text="✎ Ξεκλείδωμα Υλικών", fg_color="gray", state=tk.DISABLED, command=self.unlock_ingredients, cursor="hand2")
        self.unlock_btn.pack(pady=5)

        self.steps_label = ctk.CTkLabel(self.scroll, text="Βήματα Εκτέλεσης", font=("Segoe UI", 17, "bold"), text_color="gray")
        self.steps_label.pack(pady=(25, 5))
        
        self.add_step_btn = ctk.CTkButton(self.scroll, text="+ Προσθήκη Βήματος", command=self.open_step_form, state=tk.DISABLED, cursor="hand2")
        self.add_step_btn.pack(pady=10)

        self.steps_tree = ttk.Treeview(self.scroll, columns=('Αρ.', 'Τίτλος', 'Περιγραφή', 'Διάρκεια'), show='headings', height=5)
        for col in self.steps_tree['columns']: self.steps_tree.heading(col, text=col)
        self.steps_tree.column('Αρ.', width=50)
        self.steps_tree.pack(fill=tk.X, padx=20, pady=10)

        step_btn_f = ctk.CTkFrame(self.scroll, fg_color="transparent"); step_btn_f.pack(pady=5)
        self.edit_step_btn = ctk.CTkButton(step_btn_f, text="Επεξεργασία Βήματος", state=tk.DISABLED, command=self.edit_step, cursor="hand2")
        self.edit_step_btn.pack(side=tk.LEFT, padx=5)
        self.del_step_btn = ctk.CTkButton(step_btn_f, text="Διαγραφή Βήματος", state=tk.DISABLED, fg_color="#8b0000", hover_color="#ff1a1a", command=self.delete_step, cursor="hand2")
        self.del_step_btn.pack(side=tk.LEFT, padx=5)

        self.save_btn = ctk.CTkButton(self.scroll, text="ΑΠΟΘΗΚΕΥΣΗ ΣΥΝΤΑΓΗΣ", height=50, font=("Segoe UI", 16, "bold"), fg_color="#28a745", hover_color="#218838", command=self.save_recipe, cursor="hand2")
        self.save_btn.pack(pady=40)

        if recipe_id: self._prefill_data(recipe_id)
        else: self.category_combo.set("Επιλέξτε ή Πληκτρολογήστε...")

    def open_ingredient_form(self): IngredientFormPage(self)
    def open_step_form(self): StepFormPage(self)

    def edit_ingredient(self):
        sel = self.ing_tree.selection()
        if sel:
            idx = self.ing_tree.get_children().index(sel[0])
            IngredientFormPage(parent_form=self, index=idx, ingredient=self.ingredients[idx])

    def edit_step(self):
        sel = self.steps_tree.selection()
        if sel:
            idx = self.steps_tree.get_children().index(sel[0])
            st = self.steps[idx]
            if not hasattr(st, 'allocations'): st.allocations = []
            StepFormPage(parent_form=self, index=idx, step=st)

    def refresh_ingredients_list(self):
        for i in self.ing_tree.get_children(): self.ing_tree.delete(i)
        for i, ing in enumerate(self.ingredients): 
            tag = 'even' if i % 2 == 0 else 'odd'
            self.ing_tree.insert('', 'end', values=(ing.name, ing.quantity, ing.unit or "", ing.notes or ""), tags=(tag,))

    def refresh_steps_list(self):
        for i in self.steps_tree.get_children(): self.steps_tree.delete(i)
        for i, st in enumerate(self.steps, 1): 
            tag = 'even' if (i-1) % 2 == 0 else 'odd'
            self.steps_tree.insert('', 'end', values=(i, st.step_name, st.step_text, f"{st.duration_in_minutes} min"), tags=(tag,))

    def delete_ingredient(self):
        sel = self.ing_tree.selection()
        if sel: 
            idx = self.ing_tree.get_children().index(sel[0])
            self.ingredients.pop(idx)
            self.refresh_ingredients_list()
        
    def delete_step(self):
        sel = self.steps_tree.selection()
        if sel:
            idx = self.steps_tree.get_children().index(sel[0])
            self.steps.pop(idx)
            for i, st in enumerate(self.steps): st.sequence_order = i + 1
            self.refresh_steps_list()

    def confirm_ingredients(self):
        if not self.ingredients: return messagebox.showwarning("Προσοχή", "Προσθέστε τουλάχιστον ένα υλικό.")
        self.ingredients_locked = True
        self.add_step_btn.configure(state=tk.NORMAL); self.del_step_btn.configure(state=tk.NORMAL); self.edit_step_btn.configure(state=tk.NORMAL)
        self.steps_label.configure(text_color="white")
        self.confirm_btn.configure(state=tk.DISABLED, fg_color="gray")
        self.unlock_btn.configure(state=tk.NORMAL, fg_color="#e67e22")
        self.add_ing_btn.configure(state=tk.DISABLED); self.del_ing_btn.configure(state=tk.DISABLED); self.edit_ing_btn.configure(state=tk.DISABLED)

    def unlock_ingredients(self):
        if self.steps and not messagebox.askyesno("Προσοχή", "Το ξεκλείδωμα θα διαγράψει τα βήματα. Συνέχεια;"): return
        self.steps = []
        self.refresh_steps_list()
        self.ingredients_locked = False
        self.add_step_btn.configure(state=tk.DISABLED); self.del_step_btn.configure(state=tk.DISABLED); self.edit_step_btn.configure(state=tk.DISABLED)
        self.steps_label.configure(text_color="gray")
        self.confirm_btn.configure(state=tk.NORMAL, fg_color="#28a745")
        self.unlock_btn.configure(state=tk.DISABLED, fg_color="gray")
        self.add_ing_btn.configure(state=tk.NORMAL); self.del_ing_btn.configure(state=tk.NORMAL); self.edit_ing_btn.configure(state=tk.NORMAL)

    def _prefill_data(self, rid):
        recipe = Recipe.get_recipe_by_id(rid)
        self.name_entry.insert(0, recipe.name)
        if recipe.category: self.category_combo.set(recipe.category)
        self.difficulty_combo.set(recipe.difficulty or "Μέτρια")
        self.total_time_entry.insert(0, str(recipe.total_time_minutes))
        self.ingredients = recipe.ingredients
        self.steps = recipe.steps
        self.refresh_ingredients_list()
        self.refresh_steps_list()
        if self.ingredients: self.confirm_ingredients()

    def save_recipe(self):
        name = self.name_entry.get().strip()
        if not name: return messagebox.showerror("Σφάλμα", "Το όνομα είναι υποχρεωτικό.")
        try:
            t = int(float(self.total_time_entry.get().replace(',', '.'))) if self.total_time_entry.get() else 0
            category_val = self.category_combo.get().strip()
            if category_val == "Επιλέξτε ή Πληκτρολογήστε...": category_val = ""
            recipe = Recipe(name=name, category=category_val, difficulty=self.difficulty_combo.get(), total_time_minutes=t)
            recipe.ingredients, recipe.steps = self.ingredients, self.steps
            
            if self.recipe_id: 
                recipe.id = self.recipe_id
                recipe.update()
            else: 
                recipe.save()
                
            messagebox.showinfo("Επιτυχία", f"Η συνταγή '{name}' αποθηκεύτηκε με επιτυχία!")
            self.parent_app.load_recipes_from_db()
            self.window.destroy()
        except ValueError: messagebox.showerror("Σφάλμα", "Ελέγξτε τα πεδία των χρόνων.")

class RecipeExecutePage:
    def __init__(self, recipe_id):
        self.recipe = Recipe.get_recipe_by_id(recipe_id)
        self.steps = self.recipe.steps
        self.current_index = -1 
        self.timer_seconds = 0
        self.timer_running = False
        self.is_paused = False 
        self.timer_job = None

        self.window = ctk.CTkToplevel()
        self.window.title("Kitchen Mode")
        center_and_size_window(self.window, 850, 700)
        set_window_icon(self.window)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        ctk.CTkLabel(self.window, text=self.recipe.name, font=("Segoe UI", 26, "bold"), text_color="#2a72c1").pack(pady=15)
        
        self.prog_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.prog_frame.pack(pady=10)
        
        self.prog_bar = ctk.CTkProgressBar(self.prog_frame, width=550)
        self.prog_bar.set(0)
        self.prog_bar.pack(side=tk.LEFT, padx=(0, 15))
        
        self.prog_pct_lbl = ctk.CTkLabel(self.prog_frame, text="0%", font=("Segoe UI", 16, "bold"))
        self.prog_pct_lbl.pack(side=tk.LEFT)

        self.step_frame = ctk.CTkFrame(self.window, corner_radius=15)
        self.step_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        self.num_lbl = ctk.CTkLabel(self.step_frame, text="", font=("Segoe UI", 22, "bold"), text_color="#e67e22")
        self.num_lbl.pack(pady=15)
        self.title_lbl = ctk.CTkLabel(self.step_frame, text="", font=("Segoe UI", 20, "bold"))
        self.title_lbl.pack(pady=5)
        self.desc_lbl = ctk.CTkLabel(self.step_frame, text="", font=("Segoe UI", 18), wraplength=700, justify=tk.CENTER)
        self.desc_lbl.pack(pady=30, expand=True)

        self.countdown_lbl = ctk.CTkLabel(self.step_frame, text="", font=("Consolas", 45, "bold"), text_color="#1f538d")
        self.countdown_lbl.pack(pady=10)

        btn_f = ctk.CTkFrame(self.step_frame, fg_color="transparent")
        btn_f.pack(side=tk.BOTTOM, pady=30)
        self.prev_btn = ctk.CTkButton(btn_f, text="⏮ Πίσω", width=120, height=45, font=("Segoe UI", 14), command=self.previous, cursor="hand2")
        self.prev_btn.pack(side=tk.LEFT, padx=10)
        
        self.start_btn = ctk.CTkButton(btn_f, text="▶ Έναρξη", fg_color="#1f538d", height=45, font=("Segoe UI", 14), command=self.start_timer, cursor="hand2")
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.pause_btn = ctk.CTkButton(btn_f, text="⏸ Παύση", width=120, height=45, font=("Segoe UI", 14), command=self.toggle_pause, state=tk.DISABLED, cursor="hand2")
        self.pause_btn.pack(side=tk.LEFT, padx=10)
        
        self.next_btn = ctk.CTkButton(btn_f, text="Επόμενο ⏭", fg_color="#28a745", height=45, font=("Segoe UI", 15, "bold"), command=self.next, cursor="hand2")
        self.next_btn.pack(side=tk.LEFT, padx=10)

        self.show_step()

    def show_step(self):
        self.stop_timer()
        self.is_paused = False
        self.pause_btn.configure(state=tk.DISABLED, text="⏸ Παύση")
        
        if self.current_index == -1:
            self.num_lbl.configure(text="Βήμα 0: Προετοιμασία")
            self.title_lbl.configure(text="Mise en Place")
            ings = "\n".join([f"• {i.quantity} {i.unit or ''} {i.name}" for i in self.recipe.ingredients])
            self.desc_lbl.configure(text=f"Συγκεντρώστε στον πάγκο σας:\n\n{ings}")
            
            self.prog_bar.set(0)
            self.prog_pct_lbl.configure(text="0%")
            
            self.prev_btn.configure(state=tk.DISABLED)
            self.start_btn.configure(state=tk.DISABLED)
            self.countdown_lbl.configure(text="")
            self.next_btn.configure(text="Ξεκινάμε ⏭", fg_color="#28a745")
        else:
            s = self.steps[self.current_index]
            self.num_lbl.configure(text=f"Βήμα {self.current_index + 1} / {len(self.steps)}")
            self.title_lbl.configure(text=s.step_name)
            self.desc_lbl.configure(text=s.step_text)
            
            progress = (self.current_index + 1) / len(self.steps)
            self.prog_bar.set(progress)
            self.prog_pct_lbl.configure(text=f"{int(progress * 100)}%")
            
            self.prev_btn.configure(state=tk.NORMAL)
            if s.duration_in_minutes > 0: 
                self.start_btn.configure(state=tk.NORMAL, text="▶ Έναρξη")
                self.countdown_lbl.configure(text=f"{s.duration_in_minutes:02d}:00")
            else: 
                self.start_btn.configure(state=tk.DISABLED, text="▶ Έναρξη")
                self.countdown_lbl.configure(text="")
            self.next_btn.configure(text="Τέλος ✅" if self.current_index == len(self.steps)-1 else "Επόμενο ⏭", fg_color="#1f538d")

    def start_timer(self):
        if not self.is_paused:
            self.timer_seconds = self.steps[self.current_index].duration_in_minutes * 60
            
        self.timer_running = True
        self.is_paused = False
        
        self.start_btn.configure(state=tk.DISABLED)
        self.pause_btn.configure(state=tk.NORMAL, text="⏸ Παύση")
        self._tick()

    def toggle_pause(self):
        if self.timer_running:
            self.timer_running = False
            self.is_paused = True
            if self.timer_job: 
                self.window.after_cancel(self.timer_job)
                self.timer_job = None
            self.pause_btn.configure(text="▶ Συνέχεια")
        else:
            self.start_timer()

    def _tick(self):
        if not self.timer_running: return
        if self.timer_seconds > 0:
            m, s = divmod(self.timer_seconds, 60)
            self.countdown_lbl.configure(text=f"{m:02d}:{s:02d}")
            self.timer_seconds -= 1
            self.timer_job = self.window.after(1000, self._tick)
        else: 
            self.countdown_lbl.configure(text="ΧΡΟΝΟΣ!")
            self.timer_running = False
            self.pause_btn.configure(state=tk.DISABLED)
            self.window.bell()
            messagebox.showinfo("ChefMaster", "Ολοκληρώθηκε το βήμα!")

    def stop_timer(self):
        self.timer_running = False
        if self.timer_job: 
            self.window.after_cancel(self.timer_job)
            self.timer_job = None

    def previous(self): self.current_index -= 1; self.show_step()
    def next(self):
        if self.current_index < len(self.steps) - 1: 
            self.current_index += 1; self.show_step()
        else: 
            messagebox.showinfo("Μπράβο!", "Η συνταγή ολοκληρώθηκε!")
            self.window.destroy()
    def on_close(self): self.stop_timer(); self.window.destroy()

class RecipeApp:
    def __init__(self, root):
        self.root = root
        set_window_icon(self.root)

        self.root.title("ChefMaster Pro - Dashboard")
        self.root.geometry("1250x850")

        self.style = ttk.Style()
        self.style.theme_use("default")
        
        self.current_filter_aa = ""
        self.current_filter_category = "Όλες οι Κατηγορίες"
        self.current_filter_difficulty = "Όλες"
        self.current_filter_time = "Όλοι οι Χρόνοι"
        
        self.master_recipe_list = []

        self.current_theme_setting = "Dark" 
        self.auto_theme_job = None

        self.sidebar = ctk.CTkFrame(self.root, width=240, corner_radius=0)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        ctk.CTkLabel(self.sidebar, text="ChefMaster", font=("Segoe UI", 28, "bold")).pack(pady=40)
        
        btn_opts = {"height": 45, "font": ("Segoe UI", 15), "fg_color": "#1f538d", "hover_color": "#2a72c1", "cursor": "hand2"}
        ctk.CTkButton(self.sidebar, text="➕ Νέα Συνταγή", command=lambda: RecipeFormPage(self), **btn_opts).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="📖 Προβολή", command=self.view_recipe, **btn_opts).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="👨‍🍳 Εκτέλεση", command=self.recipe_launch, fg_color="#e67e22", hover_color="#d35400", font=("", 15, "bold"), cursor="hand2").pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="✏️ Ενημέρωση", command=self.open_update, **btn_opts).pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="❌ Διαγραφή", fg_color="#8b0000", hover_color="#ff1a1a", command=self.delete_recipe, cursor="hand2").pack(pady=10, padx=20)
        ctk.CTkButton(self.sidebar, text="📤 Εξαγωγή...", fg_color="#28a745", hover_color="#218838", command=self.open_export, cursor="hand2").pack(pady=40, padx=20)

        theme_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        theme_frame.pack(side=tk.BOTTOM, pady=20, padx=20)
        ctk.CTkLabel(theme_frame, text="Χρώμα Εφαρμογής:", font=("Segoe UI", 12)).pack(anchor="w")
        self.theme_menu = ctk.CTkOptionMenu(theme_frame, values=["Dark", "Light", "System"], command=self.user_changed_theme, cursor="hand2")
        self.theme_menu.pack(pady=5)
        self.theme_menu.set("Dark")

        self.main_area = ctk.CTkFrame(self.root, corner_radius=15)
        self.main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        search_f = ctk.CTkFrame(self.main_area, fg_color="transparent")
        search_f.pack(fill=tk.X, padx=30, pady=25)
        
        ctk.CTkLabel(search_f, text="🔍 Αναζήτηση:", font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT, padx=10)
        self.search_ent = ctk.CTkEntry(search_f, placeholder_text="Α/Α, Όνομα, ID, Χρόνος...", height=40, font=("Segoe UI", 14))
        self.search_ent.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_ent.bind("<KeyRelease>", self.perform_search)
        enable_right_click_menu(self.search_ent)

        self.filter_btn = ctk.CTkButton(search_f, text="⚙️ Προηγμένα Φίλτρα", font=("Segoe UI", 14, "bold"), height=40, command=self.open_filters_dialog, cursor="hand2")
        self.filter_btn.pack(side=tk.LEFT, padx=10)

        dash_f = ctk.CTkFrame(self.main_area, fg_color="transparent")
        dash_f.pack(fill=tk.X, padx=30, pady=10)
        self.card1 = self.create_card(dash_f, "Σύνολο Συνταγών", "#1f538d")
        self.card2 = self.create_card(dash_f, "Δημοφιλέστερη Κατηγορία", "#e67e22")

        table_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=15)
        
        self.table_scroll = ttk.Scrollbar(table_frame)
        self.table_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.table = ttk.Treeview(table_frame, columns=('aa', 'id', 'name', 'category', 'difficulty', 'time'), show='headings', yscrollcommand=self.table_scroll.set)
        self.table.heading('aa', text='Α/Α', anchor='center')
        self.table.heading('id', text='📋 ID', anchor='center')
        self.table.heading('name', text='🍲 Όνομα Συνταγής', anchor='w')
        self.table.heading('category', text='🏷️ Κατηγορία', anchor='w')
        self.table.heading('difficulty', text='⭐ Δυσκολία', anchor='center')
        self.table.heading('time', text='⏱️ Χρόνος', anchor='center')
        
        self.table.column('aa', width=50, anchor='center')
        self.table.column('id', width=70, anchor='center')
        self.table.column('name', width=350, anchor='w')
        self.table.column('category', width=180, anchor='w')
        self.table.column('difficulty', width=130, anchor='center')
        self.table.column('time', width=120, anchor='center')
        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.table_scroll.config(command=self.table.yview)

        self.apply_theme()

        self._drag_item = None
        self.table.bind("<ButtonPress-1>", self.on_drag_start)
        self.table.bind("<B1-Motion>", self.on_drag_motion)
        self.table.bind("<ButtonRelease-1>", self.on_drag_drop)
        self.table.bind("<Double-1>", lambda e: self.view_recipe())
        
        self.execute_window = None
        self.load_recipes_from_db()

    def load_recipes_from_db(self):
        db_recipes = Recipe.get_all_recipes()
        db_dict = {r[0]: r for r in db_recipes}
        
        new_master = []
        for old_r in self.master_recipe_list:
            if old_r[0] in db_dict:
                new_master.append(db_dict[old_r[0]]) 
                del db_dict[old_r[0]]
                
        for r_id, r in db_dict.items():
            new_master.append(r)
            
        self.master_recipe_list = new_master
        self.perform_search()

    def open_filters_dialog(self):
        d = ctk.CTkToplevel(self.root)
        d.title("Προηγμένα Φίλτρα Αναζήτησης")
        center_and_size_window(d, 400, 520)
        set_window_icon(d)
        d.grab_set() 
        
        ctk.CTkLabel(d, text="Α/Α Συνταγής:", font=("Segoe UI", 14, "bold")).pack(pady=(20,5))
        aa_entry = ctk.CTkEntry(d, font=("Segoe UI", 14), width=250, placeholder_text="Ακριβής Α/Α (π.χ. 3)")
        aa_entry.pack(pady=5)
        if self.current_filter_aa:
            aa_entry.insert(0, self.current_filter_aa)

        ctk.CTkLabel(d, text="Κατηγορία Συνταγής:", font=("Segoe UI", 14, "bold")).pack(pady=(20,5))
        filter_categories = ["Όλες οι Κατηγορίες"]
        try:
            with DatabaseConn("recipe_database.db") as db:
                db.execute("SELECT DISTINCT category FROM recipes WHERE category IS NOT NULL AND category != ''")
                filter_categories.extend([row[0] for row in db.fetchall()])
        except Exception: pass
        
        cat_combo = ctk.CTkOptionMenu(d, values=filter_categories, font=("Segoe UI", 14), width=250)
        cat_combo.pack(pady=5)
        cat_combo.set(self.current_filter_category)

        ctk.CTkLabel(d, text="Επίπεδο Δυσκολίας:", font=("Segoe UI", 14, "bold")).pack(pady=(20,5))
        diff_combo = ctk.CTkOptionMenu(d, values=["Όλες", "Εύκολη", "Μέτρια", "Δύσκολη"], font=("Segoe UI", 14), width=250)
        diff_combo.pack(pady=5)
        diff_combo.set(self.current_filter_difficulty)

        ctk.CTkLabel(d, text="Χρόνος Προετοιμασίας:", font=("Segoe UI", 14, "bold")).pack(pady=(20,5))
        time_combo = ctk.CTkOptionMenu(d, values=["Όλοι οι Χρόνοι", "Έως 15 λεπτά", "Έως 30 λεπτά", "Έως 60 λεπτά", "Πάνω από 60 λεπτά"], font=("Segoe UI", 14), width=250)
        time_combo.pack(pady=5)
        time_combo.set(self.current_filter_time)

        def apply_filters():
            self.current_filter_aa = aa_entry.get().strip()
            self.current_filter_category = cat_combo.get()
            self.current_filter_difficulty = diff_combo.get()
            self.current_filter_time = time_combo.get()
            
            if self.current_filter_aa or self.current_filter_category != "Όλες οι Κατηγορίες" or self.current_filter_difficulty != "Όλες" or self.current_filter_time != "Όλοι οι Χρόνοι":
                self.filter_btn.configure(text="⚙️ Φίλτρα (Ενεργά)", fg_color="#e67e22", hover_color="#d35400")
            else:
                self.filter_btn.configure(text="⚙️ Προηγμένα Φίλτρα", fg_color=["#3a7ebf", "#1f538d"], hover_color=["#325882", "#14375e"])
            self.perform_search()
            d.destroy()

        def clear_filters():
            aa_entry.delete(0, tk.END)
            cat_combo.set("Όλες οι Κατηγορίες")
            diff_combo.set("Όλες")
            time_combo.set("Όλοι οι Χρόνοι")
        
        btn_f = ctk.CTkFrame(d, fg_color="transparent"); btn_f.pack(pady=35)
        ctk.CTkButton(btn_f, text="Καθαρισμός", fg_color="gray", command=clear_filters, cursor="hand2").pack(side=tk.LEFT, padx=10)
        ctk.CTkButton(btn_f, text="✓ Εφαρμογή", fg_color="#28a745", hover_color="#218838", font=("Segoe UI", 14, "bold"), command=apply_filters, cursor="hand2").pack(side=tk.LEFT, padx=10)

    def user_changed_theme(self, new_mode):
        self.current_theme_setting = new_mode
        self.apply_theme()

    def apply_theme(self):
        mode_to_apply = self.current_theme_setting
        
        if mode_to_apply == "System":
            hour = datetime.datetime.now().hour
            if 7 <= hour < 19:
                mode_to_apply = "Light"
            else:
                mode_to_apply = "Dark"
                
        ctk.set_appearance_mode(mode_to_apply)
        
        # Εφαρμογή χρωμάτων για ΌΛΟΥΣ τους πίνακες της εφαρμογής
        if mode_to_apply == "Light":
            self.style.configure("Treeview", background="#ffffff", foreground="black", fieldbackground="#ffffff", borderwidth=0, font=("Segoe UI", 14), rowheight=35)
            self.style.configure("Treeview.Heading", background="#d9d9d9", foreground="black", font=("Segoe UI", 15, "bold"))
            self.style.map('Treeview', background=[('selected', '#3b8ed0')], foreground=[('selected', 'white')])
            self.table.tag_configure('even', background='#f2f2f2')
            self.table.tag_configure('odd', background='#ffffff')
            
            self.table.tag_configure('Εύκολη', foreground='#28a745') 
            self.table.tag_configure('Μέτρια', foreground='#d35400')
            self.table.tag_configure('Δύσκολη', foreground='#dc3545')
        else:
            self.style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0, font=("Segoe UI", 14), rowheight=35)
            self.style.configure("Treeview.Heading", background="#1f538d", foreground="white", font=("Segoe UI", 15, "bold"))
            self.style.map('Treeview', background=[('selected', '#14375e')], foreground=[('selected', 'white')])
            self.table.tag_configure('even', background='#2a2d2e')
            self.table.tag_configure('odd', background='#343638')
            
            self.table.tag_configure('Εύκολη', foreground='#4caf50')
            self.table.tag_configure('Μέτρια', foreground='#ff9800')
            self.table.tag_configure('Δύσκολη', foreground='#f44336')

        if self.current_theme_setting == "System":
            if self.auto_theme_job:
                self.root.after_cancel(self.auto_theme_job)
            self.auto_theme_job = self.root.after(60000, self.apply_theme)
        else:
            if self.auto_theme_job:
                self.root.after_cancel(self.auto_theme_job)
                self.auto_theme_job = None

    def create_card(self, p, t, c):
        f = ctk.CTkFrame(p, corner_radius=12, border_width=2, border_color=c)
        f.pack(side=tk.LEFT, padx=10, expand=True, fill="both")
        ctk.CTkLabel(f, text=t, font=("Segoe UI", 13)).pack(pady=(10, 0))
        l = ctk.CTkLabel(f, text="-", font=("Segoe UI", 24, "bold"), text_color=c)
        l.pack(pady=(0, 10))
        return l

    def on_drag_start(self, event): self._drag_item = self.table.identify_row(event.y)
    def on_drag_motion(self, event):
        item = self.table.identify_row(event.y)
        if item and self._drag_item and item != self._drag_item: 
            self.table.move(self._drag_item, '', self.table.index(item))
            
    def on_drag_drop(self, event): 
        self._drag_item = None
        
        is_filtered = bool(self.search_ent.get().strip()) or bool(self.current_filter_aa) or \
                      self.current_filter_category != "Όλες οι Κατηγορίες" or \
                      self.current_filter_difficulty != "Όλες" or \
                      self.current_filter_time != "Όλοι οι Χρόνοι"
                      
        if not is_filtered:
            new_master = []
            for i, item in enumerate(self.table.get_children()):
                current_values = list(self.table.item(item, 'values'))
                current_values[0] = i + 1 
                
                diff = current_values[4] 
                r_id = int(current_values[1])
                for r in self.master_recipe_list:
                    if r[0] == r_id:
                        new_master.append(r)
                        break
                        
                tags = ('even' if i % 2 == 0 else 'odd', diff)
                self.table.item(item, values=current_values, tags=tags)
                
            self.master_recipe_list = new_master
        else:
            for i, item in enumerate(self.table.get_children()):
                current_values = list(self.table.item(item, 'values'))
                diff = current_values[4]
                tags = ('even' if i % 2 == 0 else 'odd', diff)
                self.table.item(item, tags=tags)

    def perform_search(self, event=None):
        q = self.search_ent.get().lower().strip()
        for i in self.table.get_children(): self.table.delete(i)
        
        results = []
        for index, r in enumerate(self.master_recipe_list):
            aa = str(index + 1)
            
            match_text = (not q) or (q == aa or q in str(r[0]) or q in r[1].lower() or (r[2] and q in r[2].lower()) or (r[3] and q in r[3].lower()) or (r[4] and q in str(r[4])))
            
            match_aa = (not self.current_filter_aa) or (aa == self.current_filter_aa)
            match_cat = (self.current_filter_category == "Όλες οι Κατηγορίες") or (r[2] == self.current_filter_category)
            match_diff = (self.current_filter_difficulty == "Όλες") or (r[3] == self.current_filter_difficulty)
            
            t = r[4] or 0
            if self.current_filter_time == "Έως 15 λεπτά": match_time = t <= 15
            elif self.current_filter_time == "Έως 30 λεπτά": match_time = t <= 30
            elif self.current_filter_time == "Έως 60 λεπτά": match_time = t <= 60
            elif self.current_filter_time == "Πάνω από 60 λεπτά": match_time = t > 60
            else: match_time = True
            
            if match_text and match_aa and match_cat and match_diff and match_time: 
                results.append((aa, r))
        
        for i, (aa, r) in enumerate(results): 
            tag = ('even' if i % 2 == 0 else 'odd', r[3])
            self.table.insert('', 'end', values=(aa, r[0], r[1], r[2], r[3], f"{r[4]} λεπτά"), tags=tag)
            
        self.card1.configure(text=str(len(results)))
        cats = [r[2] for _, r in results if r[2]]
        if cats:
            freq = {c: cats.count(c) for c in set(cats)}
            m = max(freq.values())
            self.card2.configure(text=", ".join([k for k, v in freq.items() if v == m]))
        else: self.card2.configure(text="-")
    
    def delete_recipe(self):
        sel = self.table.selection()
        if sel:
            rid = int(self.table.item(sel[0])['values'][1]) 
            name = self.table.item(sel[0])['values'][2] 
            if messagebox.askyesno("Διαγραφή", f"Θέλετε να διαγράψετε τη συνταγή '{name}';"): 
                Recipe.delete_by_id(rid)
                self.load_recipes_from_db()

    def recipe_launch(self):
        sel = self.table.selection()
        if not sel: return messagebox.showwarning("Προσοχή", "Επιλέξτε μια συνταγή για εκτέλεση.")
        try:
            rid = int(self.table.item(sel[0])['values'][1]) 
            recipe = Recipe.get_recipe_by_id(rid)
            if not recipe or not recipe.steps: return messagebox.showerror("Σφάλμα", "Η συνταγή δεν έχει βήματα.")
            self.execute_window = RecipeExecutePage(rid)
        except Exception as e: messagebox.showerror("Σφάλμα", f"Αποτυχία: {e}")

    def open_update(self):
        sel = self.table.selection()
        if sel: RecipeFormPage(self, int(self.table.item(sel[0])['values'][1])) 
        else: messagebox.showwarning("Προσοχή", "Επιλέξτε μια συνταγή.")

    def view_recipe(self):
        sel = self.table.selection()
        if not sel: return
        r = Recipe.get_recipe_by_id(int(self.table.item(sel[0])['values'][1])) 
        d = ctk.CTkToplevel(); center_and_size_window(d, 700, 650); set_window_icon(d)
        sc = ctk.CTkScrollableFrame(d, fg_color="transparent"); sc.pack(fill=tk.BOTH, expand=True)
        ctk.CTkLabel(sc, text=r.name, font=("Segoe UI", 26, "bold"), text_color="#2a72c1").pack(pady=20)
        ctk.CTkLabel(sc, text="🛒 Υλικά:", font=("Segoe UI", 18, "bold")).pack(anchor=tk.W, padx=40)
        for i in r.ingredients: ctk.CTkLabel(sc, text=f"• {i.quantity} {i.unit or ''} {i.name}", font=("Segoe UI", 15)).pack(anchor=tk.W, padx=60, pady=2)
        ctk.CTkLabel(sc, text="👨‍🍳 Βήματα:", font=("Segoe UI", 18, "bold")).pack(anchor=tk.W, padx=40, pady=(25, 10))
        for i, st in enumerate(r.steps, 1):
            ctk.CTkLabel(sc, text=f"{i}. {st.step_name}", font=("Segoe UI", 15, "bold")).pack(anchor=tk.W, padx=60, pady=(10, 0))
            ctk.CTkLabel(sc, text=st.step_text, wraplength=550, justify=tk.LEFT, font=("Segoe UI", 14)).pack(anchor=tk.W, padx=80)

    def open_export(self):
        d = ctk.CTkToplevel(); d.title("Εξαγωγή Δεδομένων"); center_and_size_window(d, 450, 300); set_window_icon(d)
        def do_excel():
            p = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Excel CSV", "*.csv")])
            if p:
                with open(p, 'w', newline='', encoding='utf-8-sig') as f:
                    w = csv.writer(f, delimiter=';'); w.writerow(['A/A', 'ID', 'Όνομα', 'Κατηγορία', 'Δυσκολία', 'Χρόνος'])
                    for idx, r in enumerate(self.master_recipe_list): 
                        w.writerow([idx + 1, r[0], r[1], r[2], r[3], r[4]])
                messagebox.showinfo("OK", "Η εξαγωγή σε Excel ολοκληρώθηκε!"); d.destroy()
                
        def do_pdf():
            sel = self.table.selection()
            if not sel: return messagebox.showerror("Σφάλμα", "Επιλέξτε μια συνταγή.")
            rid = int(self.table.item(sel[0])['values'][1]); r = Recipe.get_recipe_by_id(rid) 
            p = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile=f"{r.name}.pdf")
            if p:
                try:
                    from fpdf import FPDF
                    pdf = FPDF(); pdf.add_page()
                    font_path = "C:\\Windows\\Fonts\\arial.ttf"; bold_font_path = "C:\\Windows\\Fonts\\arialbd.ttf"
                    if os.path.exists(font_path):
                        pdf.add_font("ArialGR", "", font_path)
                        if os.path.exists(bold_font_path): pdf.add_font("ArialGR", "B", bold_font_path)
                        pdf.set_font("ArialGR", "B" if os.path.exists(bold_font_path) else "", 18)
                    else: pdf.set_font("helvetica", "B", 18)
                    pdf.cell(0, 10, r.name, ln=True, align='C')
                    pdf.set_font("ArialGR" if os.path.exists(font_path) else "helvetica", "", 12)
                    pdf.cell(0, 10, f"Κατηγορία: {r.category} | Δυσκολία: {r.difficulty}", ln=True)
                    pdf.ln(10); pdf.set_font("ArialGR" if os.path.exists(font_path) else "helvetica", "B", 14)
                    pdf.cell(0, 10, "Υλικά:", ln=True)
                    pdf.set_font("ArialGR" if os.path.exists(font_path) else "helvetica", "", 12)
                    for ing in r.ingredients: pdf.cell(0, 8, f"- {ing.quantity} {ing.unit or ''} {ing.name}", ln=True)
                    pdf.ln(10); pdf.set_font("ArialGR" if os.path.exists(font_path) else "helvetica", "B", 14)
                    pdf.cell(0, 10, "Βήματα Εκτέλεσης:", ln=True)
                    pdf.set_font("ArialGR" if os.path.exists(font_path) else "helvetica", "", 12)
                    for i, st in enumerate(r.steps, 1): pdf.multi_cell(0, 8, f"{i}. {st.step_name}\n    {st.step_text}"); pdf.ln(3)
                    pdf.output(p); messagebox.showinfo("Επιτυχία", "Το PDF δημιουργήθηκε!"); d.destroy()
                    try: os.startfile(p)
                    except: pass
                except Exception as e: messagebox.showerror("Σφάλμα", f"Αποτυχία: {e}")
        ctk.CTkButton(d, text="📊 Εξαγωγή ΟΛΩΝ (Excel)", height=50, font=("Segoe UI", 15, "bold"), command=do_excel, cursor="hand2").pack(pady=25, padx=40, fill=tk.X)
        ctk.CTkButton(d, text="🖨️ Εξαγωγή ΕΠΙΛΕΓΜΕΝΗΣ (PDF)", height=50, font=("Segoe UI", 15, "bold"), fg_color="#e67e22", command=do_pdf, cursor="hand2").pack(pady=10, padx=40, fill=tk.X)

if __name__ == "__main__":
    try:
        myappid = 'eap.project11.chefmaster.1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception: pass
    root = ctk.CTk()
    app = RecipeApp(root)
    root.mainloop()