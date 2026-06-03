from db import DatabaseConn
from models import Recipe, Ingredient, Step, ImageModel, Category, Unit
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
import ctypes
import datetime
import shutil
from PIL import Image
from fpdf import FPDF
from fractions import Fraction
from utils import (
    resource_path, center_and_size_window, set_window_icon,
    setup_treeview_scroll, greek_sort_key, enable_right_click_menu, get_alloc_val, 
    format_quantity, set_readonly_entry, make_fast_scrollable, get_app_root, SelectableListDialog, ToolTip
)
from db import INITIAL_STEPS

# =============================================================================
# --- 1. ΑΡΧΙΚΟΠΟΙΗΣΗ ΜΟΝΟΠΑΤΙΩΝ ΦΑΚΕΛΩΝ ΚΑΙ ΤΗΣ ΒΑΣΗΣ ΔΕΔΟΜΕΝΩΝ ---
# =============================================================================

APPLICATION_PATH = get_app_root()

IMG_FOLDER = os.path.join(get_app_root(), "recipe_images")

if not os.path.exists(IMG_FOLDER):
    os.makedirs(IMG_FOLDER)


DatabaseConn.initialize_database("recipe_database.db")

ctk.set_default_color_theme("dark-blue")

# =============================================================================
# --- 2. ΚΛΑΣΕΙΣ ΦΟΡΜΩΝ ---
# =============================================================================

class IngredientFormPage:
    def open_ingredient_dialog(self):
        SelectableListDialog(
            parent=self.window,
            title="Επιλογή Υλικού",
            items=Ingredient.get_all(),
            on_select_callback=lambda ing: set_readonly_entry(self.name_entry, ing)
        ).show()
    def open_unit_dialog(self):
        SelectableListDialog(
            parent=self.window,
            title="Επιλογή Μονάδας",
            items=Unit.get_all(),
            on_select_callback=lambda unit: set_readonly_entry(self.unit_entry, unit)
        ).show()
    def __init__(self, parent_form, index=None, ingredient=None):
        self.parent_form = parent_form
        self.index = index
        self.window = ctk.CTkToplevel()
        self.window.title("Επεξεργασία Συστατικού" if index is not None else "Προσθήκη Συστατικού")
        center_and_size_window(self.window, 550, 500)
        set_window_icon(self.window)
        self.window.transient(self.parent_form.window)
        self.window.grab_set()
        
        scroll = ctk.CTkScrollableFrame(self.window, fg_color="transparent")
        scroll.pack(fill=tk.BOTH, expand=True)

        ing_name_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        ing_name_frame.pack(pady=(15,0), padx=20, fill=tk.X)
        
        ctk.CTkLabel(ing_name_frame, text="Όνομα Συστατικού:", font=("Segoe UI", 13)).pack(anchor="w")
        
        name_combo_frame = ctk.CTkFrame(ing_name_frame, fg_color="transparent")
        name_combo_frame.pack(fill=tk.X, pady=5)
        
        self.name_entry = ctk.CTkEntry(name_combo_frame, width=270, font=("Segoe UI", 14))
        self.name_entry.pack(side=tk.LEFT, padx=(0, 5))

        if ingredient and ingredient.name:
            self.name_entry.insert(0, ingredient.name)
        else:
            self.name_entry.insert(0, "Επιλέξτε απο το κουμπί δίπλα...")
        self.name_entry.configure(state="readonly")
        
        ctk.CTkButton(name_combo_frame, text="▼", width=35, height=35,
                     command=self.open_ingredient_dialog, cursor="hand2",
                     fg_color="#1f538d", hover_color="#2a72c1",
                     font=("Segoe UI", 14)).pack(side=tk.LEFT, padx=(0, 5))
        
        ctk.CTkButton(name_combo_frame, text="Διαχείριση Υλικών 🥕", width=40, height=35,
              command=lambda: Ingredient.manage(self.window),
              fg_color="#C01E1E", hover_color="#d35400",
              cursor="hand2", font=("Segoe UI", 16)).pack(side=tk.LEFT)

        ctk.CTkLabel(scroll, text="Ποσότητα:", font=("Segoe UI", 13)).pack(padx=20, anchor="w")
        self.quantity_entry = ctk.CTkEntry(scroll, width=150, font=("Segoe UI", 14))
        self.quantity_entry.pack(pady=5, padx=20, anchor="w")
        if ingredient and ingredient.quantity: 
            self.quantity_entry.insert(0, format_quantity(ingredient.quantity))
        enable_right_click_menu(self.quantity_entry)
        
        unit_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        unit_frame.pack(fill=tk.X, pady=5, padx=20)
        
        ctk.CTkLabel(unit_frame, text="Μονάδα:", font=("Segoe UI", 13), anchor="w").pack(anchor="w")
        
        unit_select_frame = ctk.CTkFrame(unit_frame, fg_color="transparent")
        unit_select_frame.pack(fill=tk.X, pady=5)
        
        self.unit_entry = ctk.CTkEntry(unit_select_frame, width=210, font=("Segoe UI", 14))
        self.unit_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        if ingredient and ingredient.unit:
            self.unit_entry.insert(0, ingredient.unit)
        else:
            self.unit_entry.insert(0, "Επιλέξτε απο το κουμπί δίπλα...")
        self.unit_entry.configure(state="readonly")
        
        
        ctk.CTkButton(unit_select_frame, text="▼", width=35, height=35,
                     command=self.open_unit_dialog, cursor="hand2",
                     fg_color="#1f538d", hover_color="#2a72c1",
                     font=("Segoe UI", 14)).pack(side=tk.LEFT, padx=(0, 5))
        
        ctk.CTkButton(unit_select_frame, text="📏 Διαχείριση Μονάδων", width=100, height=35,
                     command=lambda: Unit.manage(self.window),
                     fg_color="#cc5500", hover_color="#d35400",
                     font=("Segoe UI", 13)).pack(side=tk.LEFT)
        
        ctk.CTkLabel(scroll, text="Σημειώσεις:", font=("Segoe UI", 13)).pack(padx=20, anchor="w")
        self.notes_entry = ctk.CTkEntry(scroll, width=350, font=("Segoe UI", 14))
        self.notes_entry.pack(pady=5, padx=20, anchor="w")
        if ingredient and ingredient.notes: 
            self.notes_entry.insert(0, ingredient.notes)
        enable_right_click_menu(self.notes_entry)
        
        ctk.CTkButton(scroll, text="Αποθήκευση", command=self.save, font=("Segoe UI", 14, "bold"), height=40, cursor="hand2").pack(pady=30)


    def save(self):
        name = self.name_entry.get().strip()
        if not name or name.startswith("Επιλέξτε"): 
            return messagebox.showerror("Σφάλμα", "Το όνομα είναι υποχρεωτικό.")
        try:
            input_text = self.quantity_entry.get().strip().replace(',', '.')
            if ' ' in input_text and '/' in input_text:
                parts = input_text.split()
                whole = Fraction(parts[0])
                frac = Fraction(parts[1])
                qty_value = float(whole + frac)
            else:
                qty_value = float(Fraction(input_text))
            
            if qty_value is None or qty_value <= 0:
                return messagebox.showerror("Σφάλμα", "Εισάγετε έγκυρη ποσότητα (π.χ. 1.5, 1/2, 2 1/2)")
            qty = qty_value         
            unit_val = self.unit_entry.get().strip()
            if unit_val == "Επιλέξτε απο το κουμπί δίπλα...": 
                unit_val = ""
                
            ing = Ingredient(name=name, quantity=qty, unit=unit_val, notes=self.notes_entry.get().strip())
            
            if self.index is not None:
                old_ing = self.parent_form.ingredients[self.index]
                if hasattr(old_ing, 'id'): 
                    ing.id = old_ing.id
                self.parent_form.ingredients[self.index] = ing
            else:
                found = False
                for existing in self.parent_form.ingredients:
                    if existing.name == name and existing.unit == unit_val and existing.notes == ing.notes:
                        existing.quantity = round(existing.quantity + qty, 5)
                        found = True
                        break
                
                if not found:
                    self.parent_form.ingredients.append(ing)
            
            self.parent_form.ingredients.sort(key=lambda x: greek_sort_key(x.name))
            self.parent_form.refresh_ingredients_list()
            self.window.destroy()
        except ValueError: 
            messagebox.showerror("Σφάλμα", "Εισάγετε έγκυρο αριθμό στο πεδίο ποσότητας.")

class StepFormPage:
    def __init__(self, parent_form, index=None, step=None):
        self.parent_form = parent_form
        self.index = index
        self.step_allocations = []
        
        self.window = ctk.CTkToplevel()
        self.window.title("Επεξεργασία Βήματος" if index is not None else "Προσθήκη Βήματος")
        center_and_size_window(self.window, 750, 700)
        set_window_icon(self.window)
        self.window.transient(self.parent_form.window)
        self.window.grab_set()

        if hasattr(self.parent_form, 'unlock_btn'):
            self.parent_form.unlock_btn.configure(state=tk.DISABLED)
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        scroll = ctk.CTkScrollableFrame(self.window, fg_color="transparent")
        scroll.pack(fill=tk.BOTH, expand=True)

        step_names = INITIAL_STEPS.copy()

        step_names = sorted(list(set(step_names)), key=greek_sort_key)

        ctk.CTkLabel(scroll, text="Τίτλος Βήματος:", font=("Segoe UI", 13)).pack(pady=(15,0), padx=20, anchor="w")
        self.step_name_combo = ctk.CTkComboBox(scroll, values=step_names, width=400, font=("Segoe UI", 14))
        self.step_name_combo.pack(pady=5, padx=20, anchor="w")
        
        if step and step.step_name:
            self.step_name_combo.set(step.step_name)
        else:
            self.step_name_combo.set("Επιλέξτε ή πληκτρολογήστε...")
        
        enable_right_click_menu(self.step_name_combo)
        
        def on_step_focus_in(event):
            if self.step_name_combo.get() == "Επιλέξτε ή πληκτρολογήστε...":
                self.step_name_combo.set("")
        
        def on_step_focus_out(event):
            if self.step_name_combo.get() == "":
                self.step_name_combo.set("Επιλέξτε ή πληκτρολογήστε...")
        
        self.step_name_combo._entry.bind("<FocusIn>", on_step_focus_in)
        self.step_name_combo._entry.bind("<FocusOut>", on_step_focus_out)

        ctk.CTkLabel(scroll, text="Περιγραφή:", font=("Segoe UI", 13)).pack(padx=20, anchor="w")
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
        
        ctk.CTkButton(h_f, text="+ Προσθήκη Όλων", command=self.add_all_ingredients, width=130, cursor="hand2", fg_color="#e67e22", hover_color="#d35400").pack(side=tk.RIGHT, padx=(10, 0))
        
        ctk.CTkButton(h_f, text="+ Προσθήκη Υλικού", command=self.add_ingredient_from_existing, width=150, cursor="hand2").pack(side=tk.RIGHT)

        self.ingredients_tree = ttk.Treeview(scroll, columns=('Όνομα', 'Ποσότητα', 'Μονάδα'), show='headings', height=5)
        for col in self.ingredients_tree['columns']: 
            self.ingredients_tree.heading(col, text=col)
            self.ingredients_tree.column(col, anchor='center')
        self.ingredients_tree.pack(fill=tk.X, padx=20, pady=10)
        setup_treeview_scroll(self.ingredients_tree)

        ctk.CTkButton(scroll, text="Αφαίρεση Επιλεγμένου", fg_color="#8b0000", hover_color="#ff1a1a", command=self.remove_selected_ingredient, cursor="hand2").pack(pady=5)
        ctk.CTkButton(scroll, text="Αποθήκευση Βήματος", command=self.save, font=("Segoe UI", 15, "bold"), height=45, fg_color="#1f538d", cursor="hand2").pack(pady=30)

        if step:
            if step.step_text: 
                self.step_text_entry.insert("1.0", step.step_text)
            if step.duration_in_minutes: 
                self.duration_entry.insert(0, str(step.duration_in_minutes))
            self.step_allocations = getattr(step, 'allocations', getattr(step, 'step_ingredients', [])).copy()
            
            self.refresh_ingredients_list()

    def on_close(self):
        if hasattr(self.parent_form, 'unlock_btn'):
            if self.parent_form.ingredients_locked:
                self.parent_form.unlock_btn.configure(state=tk.NORMAL)
            else:
                self.parent_form.unlock_btn.configure(state=tk.DISABLED)
        self.window.destroy()

    def add_ingredient_from_existing(self):
        if not self.parent_form.ingredients: 
            return messagebox.showwarning("!", "Προσθέστε πρώτα υλικά στη συνταγή.")
        
        dialog = ctk.CTkToplevel(self.window)
        center_and_size_window(dialog, 500, 550)
        set_window_icon(dialog)
        dialog.title("Επιλογή Υλικού")
        dialog.transient(self.window)
        dialog.grab_set()
        
        ing_data_list = []
        for idx, ing in enumerate(self.parent_form.ingredients):
            used = 0
            for i, st in enumerate(self.parent_form.steps):
                if self.index is not None and i == self.index:
                    continue
                allocs = getattr(st, 'allocations', getattr(st, 'step_ingredients', []))
                for alloc in allocs:
                    if get_alloc_val(alloc, 'notes') == "Στάδιο Προετοιμασίας":
                        continue
                    if (get_alloc_val(alloc, 'temp_id') == idx or 
                        (get_alloc_val(alloc, 'ingredient_name') == ing.name and 
                        get_alloc_val(alloc, 'unit') == ing.unit)):
                        used += get_alloc_val(alloc, 'quantity', 0)
            
            for alloc in self.step_allocations:
                if get_alloc_val(alloc, 'notes') == "Στάδιο Προετοιμασίας":
                    continue
                if (get_alloc_val(alloc, 'temp_id') == idx or 
                    (get_alloc_val(alloc, 'ingredient_name') == ing.name and 
                    get_alloc_val(alloc, 'unit') == ing.unit)):
                    used += get_alloc_val(alloc, 'quantity', 0)
            
            avail = round(ing.quantity - used, 5)
            if avail > 0:
                ing_data_list.append({
                    'display': f"{ing.name} (Διαθέσιμο: {avail} {ing.unit or ''})",
                    'data': {'temp_id': idx, 'name': ing.name, 'avail': avail, 'unit': ing.unit}
                })
        
        if not ing_data_list: 
            messagebox.showinfo("!", "Έχετε καταναλώσει όλο το απόθεμα υλικών στα προηγούμενα βήματα.")
            dialog.destroy()
            return
        
        ing_data_list.sort(key=lambda x: greek_sort_key(x['display']))
        ing_list = [item['display'] for item in ing_data_list]
        ing_data = [item['data'] for item in ing_data_list]
        
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text="Επιλέξτε Υλικό:", font=("Segoe UI", 14)).pack(anchor="w")
        combo = ctk.CTkComboBox(main_frame, values=ing_list, width=350, font=("Segoe UI", 14))
        combo.pack(pady=10)
        combo.set(ing_list[0] if ing_list else "")

        def on_combo_select(selected):
            nonlocal current_avail
            try:
                idx = ing_list.index(selected)
                current_avail = ing_data[idx]['avail']
            except (ValueError, IndexError):
                pass

        combo.bind("<<ComboboxSelected>>", lambda e: on_combo_select(combo.get()))

        qty_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        qty_frame.pack(fill=tk.X, pady=5)

        ctk.CTkLabel(qty_frame, text="Ποσότητα:", font=("Segoe UI", 14), anchor="w").pack(anchor="w")

        qty_input_frame = ctk.CTkFrame(qty_frame, fg_color="transparent")
        qty_input_frame.pack(fill=tk.X, pady=(5, 0))

        qty_ent = ctk.CTkEntry(qty_input_frame, placeholder_text="Π.χ. 500", font=("Segoe UI", 14), width=150)
        qty_ent.pack(side=tk.LEFT, padx=(0, 10))

        current_avail = 0

        def set_max_quantity():
            selected_display = combo.get()
            if selected_display:
                try:
                    idx = ing_list.index(selected_display)
                    current_max = ing_data[idx]['avail']
                    if current_max > 0:
                        qty_ent.delete(0, tk.END)
                        qty_ent.insert(0, str(current_max))
                        qty_ent.select_range(0, tk.END)
                        qty_ent.focus()
                except (ValueError, IndexError):
                    pass

        max_btn = ctk.CTkButton(qty_input_frame, text="Max", width=60, height=32,
                                command=set_max_quantity, cursor="hand2",
                                fg_color="#e67e22", hover_color="#d35400",
                                font=("Segoe UI", 13, "bold"))
        max_btn.pack(side=tk.LEFT)

        enable_right_click_menu(qty_ent)

        prep_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(main_frame, text="Στάδιο Προετοιμασίας (Δεν μειώνει το απόθεμα)", 
                    variable=prep_var, font=("Segoe UI", 13)).pack(pady=15)
        
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        def confirm():
            try:
                selected_display = combo.get()
                if not selected_display:
                    messagebox.showerror("Λάθος", "Επιλέξτε ένα υλικό.")
                    return
                
                sel = ing_data[ing_list.index(selected_display)]
                
                nonlocal current_avail
                current_avail = sel['avail']
                
                qty_text = qty_ent.get().strip().replace(',', '.')
                if not qty_text:
                    messagebox.showerror("Λάθος", "Εισάγετε ποσότητα.")
                    return
                
                try:
                    if ' ' in qty_text and '/' in qty_text:
                        parts = qty_text.split()
                        whole = Fraction(parts[0])
                        frac = Fraction(parts[1])
                        val = float(whole + frac)
                    else:
                        val = float(Fraction(qty_text))
                except:
                    messagebox.showerror("Λάθος", "Εισάγετε έγκυρη ποσότητα (π.χ. 1.5, 1/2, 2 1/2)")
                    return
                
                if prep_var.get():
                    if val <= 0:
                        messagebox.showerror("Λάθος", "Η ποσότητα πρέπει να είναι θετική.")
                        return
                else:
                    if val <= 0:
                        messagebox.showerror("Λάθος", "Η ποσότητα πρέπει να είναι θετική.")
                        return
                    if val > sel['avail'] + 0.001:
                        messagebox.showerror("Λάθος", f"Μη έγκυρη ποσότητα. Το διαθέσιμο απόθεμα είναι {sel['avail']}.")
                        return
                
                notes_val = "Στάδιο Προετοιμασίας" if prep_var.get() else ""
                
                found = False
                for existing in self.step_allocations:
                    if (existing.get('temp_id') == sel['temp_id'] or 
                        (existing.get('ingredient_name') == sel['name'] and 
                        existing.get('unit') == sel['unit'] and
                        existing.get('notes') == notes_val)):
                        existing['quantity'] = round(existing['quantity'] + val, 5)
                        found = True
                        break
                
                if not found:
                    self.step_allocations.append({
                        'temp_id': sel['temp_id'], 
                        'ingredient_name': sel['name'], 
                        'quantity': val, 
                        'unit': sel['unit'],
                        'notes': notes_val
                    })
                
                self.step_allocations.sort(key=lambda x: greek_sort_key(x['ingredient_name']))
                self.refresh_ingredients_list()
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Λάθος", "Εισάγετε έγκυρο αριθμό στο πεδίο Ποσότητα.")
            except Exception as e:
                messagebox.showerror("Λάθος", f"Σφάλμα: {str(e)}")

        ctk.CTkButton(btn_frame, text="Προσθήκη", command=confirm, cursor="hand2", 
                     fg_color="#28a745", hover_color="#218838", width=120).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="Ακύρωση", command=dialog.destroy, cursor="hand2",
                     fg_color="#8b0000", hover_color="#ff1a1a", width=120).pack(side=tk.LEFT, padx=5)
        
        qty_ent.bind('<Return>', lambda e: confirm())

    def add_all_ingredients(self):
        if not self.parent_form.ingredients: 
            return messagebox.showwarning("!", "Προσθέστε πρώτα υλικά στη συνταγή.")
            
        added_count = 0
        for idx, ing in enumerate(self.parent_form.ingredients):
            used = 0
            for i, st in enumerate(self.parent_form.steps):
                if self.index is not None and i == self.index: continue
                allocs = getattr(st, 'allocations', getattr(st, 'step_ingredients', []))
                for alloc in allocs:
                    if get_alloc_val(alloc, 'notes') == "Στάδιο Προετοιμασίας": continue
                    if get_alloc_val(alloc, 'temp_id') == idx or get_alloc_val(alloc, 'ingredient_name') == ing.name:
                        used += get_alloc_val(alloc, 'quantity', 0)
                        
            for alloc in self.step_allocations:
                if get_alloc_val(alloc, 'notes') == "Στάδιο Προετοιμασίας": continue
                if get_alloc_val(alloc, 'temp_id') == idx or get_alloc_val(alloc, 'ingredient_name') == ing.name:
                    used += get_alloc_val(alloc, 'quantity', 0)
                    
            avail = round(ing.quantity - used, 5)
            
            if avail > 0:
                self.step_allocations.append({
                    'temp_id': idx, 
                    'ingredient_name': ing.name, 
                    'quantity': avail, 
                    'unit': ing.unit,
                    'notes': ""
                })
                added_count += 1
                
        if added_count > 0:
            self.step_allocations.sort(key=lambda x: greek_sort_key(x['ingredient_name']))
            self.refresh_ingredients_list()
            messagebox.showinfo("Επιτυχία", f"Προστέθηκαν αυτόματα {added_count} υλικά.")
        else:
            messagebox.showinfo("!", "Δεν υπάρχουν διαθέσιμα υλικά (τα έχετε ήδη καταναλώσει όλα).")
    
    def refresh_ingredients_list(self):
        for i in self.ingredients_tree.get_children(): 
            self.ingredients_tree.delete(i)
        
        for i, a in enumerate(self.step_allocations): 
            tag = 'even' if i % 2 == 0 else 'odd'
            name = get_alloc_val(a, 'ingredient_name', '')
            notes = get_alloc_val(a, 'notes', '')
            if notes == "Στάδιο Προετοιμασίας":
                name += " (Προετ.)"
            self.ingredients_tree.insert('', 'end', values=(
                name, 
                get_alloc_val(a, 'quantity', ''), 
                get_alloc_val(a, 'unit', '')
            ), tags=(tag,))

    def remove_selected_ingredient(self):
        sel = self.ingredients_tree.selection()
        if sel: 
            idx = self.ingredients_tree.get_children().index(sel[0])
            self.step_allocations.pop(idx)
            self.refresh_ingredients_list()

    def save(self):
        name = self.step_name_combo.get().strip()
        text = self.step_text_entry.get("1.0", "end-1c").strip() 
        if not name or name.startswith("Επιλέξτε") or not text: 
            return messagebox.showerror("!", "Συμπληρώστε τον Τίτλο και την Περιγραφή.")
        try:
            dur_str = self.duration_entry.get().strip()
            dur = int(float(dur_str.replace(',', '.'))) if dur_str else 0
            
            step = Step(step_name=name, step_text=text, duration_in_minutes=dur, sequence_order=(self.index+1 if self.index is not None else len(self.parent_form.steps)+1))
            
            clean_allocations = []
            for a in self.step_allocations:
                clean_allocations.append({
                    'temp_id': a.get('temp_id'),
                    'ingredient_name': a.get('ingredient_name', ''),
                    'quantity': a.get('quantity', 0),
                    'unit': a.get('unit', ''),
                    'notes': a.get('notes', '')
                })
            
            step.allocations = clean_allocations
            step.step_ingredients = clean_allocations
            
            if self.index is not None: 
                self.parent_form.steps[self.index] = step
            else: 
                self.parent_form.steps.append(step)
                
            self.parent_form.refresh_steps_list()

            if hasattr(self.parent_form, 'unlock_btn'):
                if self.parent_form.ingredients_locked:
                    self.parent_form.unlock_btn.configure(state=tk.NORMAL)
                else:
                    self.parent_form.unlock_btn.configure(state=tk.DISABLED)
            
            self.window.destroy()
        except ValueError: 
            messagebox.showerror("!", "Η διάρκεια πρέπει να είναι αριθμός.")

class RecipeFormPage:
    def open_category_dialog(self):
        SelectableListDialog(
            parent=self.window,
            title="Επιλογή Κατηγορίας",
            items=Category.get_all(),
            on_select_callback=lambda cat: set_readonly_entry(self.category_entry, cat)
        ).show()

    def __init__(self, parent_app, recipe_id=None):
        self.parent_app = parent_app
        self.recipe_id = recipe_id
        self.ingredients = []
        self.steps = []
        self.selected_image_path = None
        self.selected_image_id = None
        self.image_to_delete = None
        self.ingredients_locked = False
        self.preview_img_obj = None 
        self.window = ctk.CTkToplevel()
        self.window.title("Φόρμα Συνταγής")
        center_and_size_window(self.window, 950, 850)
        set_window_icon(self.window)
        self.window.transient(self.parent_app.root)
        self.window.grab_set()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.scroll = ctk.CTkScrollableFrame(self.window, fg_color="transparent")
        self.scroll.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        make_fast_scrollable(self.scroll, self.window, speed=150)
        self.img_frame = ctk.CTkFrame(self.scroll, width=250, height=180, fg_color="#333")
        self.img_frame.pack(pady=10)
        self.img_frame.pack_propagate(False)
        self.img_preview_label = ctk.CTkLabel(self.img_frame, text="Δεν υπάρχει εικόνα\n(Max 1MB, 600x400)", text_color="#ffffff")
        self.img_preview_label.pack(expand=True, fill="both")
        
        img_btn_f = ctk.CTkFrame(self.scroll, fg_color="transparent")
        img_btn_f.pack(pady=5)
        
        ctk.CTkButton(img_btn_f, text="📷 Επιλογή", command=self.pick_image, font=("Segoe UI", 13, "bold"), width=10, cursor="hand2").pack(side=tk.LEFT, padx=0)
        ctk.CTkButton(img_btn_f, text="❌ Αφαίρεση", fg_color="#8b0000", hover_color="#ff1a1a", width=100,
                      command=self.remove_image, font=("Segoe UI", 13, "bold"), cursor="hand2").pack(side=tk.LEFT, padx=5)

        info_frame = ctk.CTkFrame(self.scroll)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        name_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        name_row.pack(fill=tk.X, pady=5)
        ctk.CTkLabel(name_row, text="Όνομα Συνταγής:", font=("Segoe UI", 14), width=120, anchor="w").pack(side=tk.LEFT, padx=(15, 10))
        self.name_entry = ctk.CTkEntry(name_row, width=200, font=("Segoe UI", 14))
        if recipe_id is None:
            self.name_entry.insert(0, "Πληκτρολογήστε όνομα...")
        self.name_entry.pack(side=tk.LEFT)
        enable_right_click_menu(self.name_entry)

        def on_name_focus_in(event):
            if self.name_entry.get() == "Πληκτρολογήστε όνομα...":
                self.name_entry.delete(0, tk.END)

        def on_name_focus_out(event):
            if self.name_entry.get().strip() == "" and recipe_id is None:
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, "Πληκτρολογήστε όνομα...")

        self.name_entry.bind("<FocusIn>", on_name_focus_in)
        self.name_entry.bind("<FocusOut>", on_name_focus_out)

        cat_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        cat_row.pack(fill=tk.X, pady=10)
        ctk.CTkLabel(cat_row, text="Κατηγορία:", font=("Segoe UI", 14), width=120, anchor="w").pack(side=tk.LEFT, padx=(15, 10))

        all_cats = Category.get_all()
        all_cats = sorted(all_cats, key=greek_sort_key)

        self.cat_input_frame = ctk.CTkFrame(cat_row, fg_color="transparent")
        self.cat_input_frame.pack(side=tk.LEFT)

        self.category_entry = ctk.CTkEntry(self.cat_input_frame, width=250, font=("Segoe UI", 14))
        self.category_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.category_entry.insert(0, "Επιλέξτε απο το κουμπί δίπλα...")
        self.category_entry.configure(state="readonly")

        ctk.CTkButton(self.cat_input_frame, text="▼", width=35, height=35,
                     command=self.open_category_dialog, cursor="hand2",
                     fg_color="#1f538d", hover_color="#2a72c1",
                     font=("Segoe UI", 14)).pack(side=tk.LEFT, padx=(0, 5))

        ctk.CTkButton(self.cat_input_frame, text="Διαχείριση Κατηγοριών ⚙️", width=35, height=35,
                     command=lambda: Category.manage(self.window, callback_on_change=self.refresh_categories_list),
                     fg_color="#9b59b6", hover_color="#8e44ad",
                     font=("Segoe UI", 14)).pack(side=tk.LEFT)

        details_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        details_row.pack(fill=tk.X, pady=10)

        ctk.CTkLabel(details_row, text="Δυσκολία:", font=("Segoe UI", 14), width=120, anchor="w").pack(side=tk.LEFT, padx=(15, 10))
        self.difficulty_combo = ctk.CTkComboBox(details_row, values=["Εύκολη", "Μέτρια", "Δύσκολη"], width=120, font=("Segoe UI", 14), state="readonly")
        self.difficulty_combo.pack(side=tk.LEFT, padx=(0, 30))
        self.difficulty_combo.set("Μέτρια")

        ctk.CTkLabel(details_row, text="Χρόνος:", font=("Segoe UI", 14)).pack(side=tk.LEFT)
        self.total_time_entry = ctk.CTkEntry(details_row, width=80, font=("Segoe UI", 14))
        self.total_time_entry.pack(side=tk.LEFT, padx=(10, 5))
        ctk.CTkLabel(details_row, text="λεπτά", font=("Segoe UI", 14)).pack(side=tk.LEFT)
        enable_right_click_menu(self.total_time_entry)

        ing_title_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        ing_title_frame.pack(fill=tk.X, pady=(20, 10))
        
        ctk.CTkLabel(ing_title_frame, text="Λίστα Συστατικών", font=("Segoe UI", 18, "bold")).pack(anchor="center")
        
        ing_tree_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        ing_tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tree_container = ttk.Frame(ing_tree_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        ing_scrollbar = ttk.Scrollbar(tree_container)
        ing_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.ing_tree = ttk.Treeview(tree_container, columns=('Όνομα', 'Ποσότητα', 'Μονάδα', 'Σημειώσεις'), 
                                      show='headings', height=8, yscrollcommand=ing_scrollbar.set)
        for col in self.ing_tree['columns']: 
            self.ing_tree.heading(col, text=col)
            self.ing_tree.column(col, anchor='center')
        self.ing_tree.column('Όνομα', width=200)
        self.ing_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ing_scrollbar.config(command=self.ing_tree.yview)

        setup_treeview_scroll(self.ing_tree)

        btn_row1 = ctk.CTkFrame(self.scroll, fg_color="transparent")
        btn_row1.pack(pady=5)
        
        self.add_ing_btn = ctk.CTkButton(btn_row1, text="➕ Προσθήκη", command=lambda: IngredientFormPage(self), cursor="hand2")
        self.add_ing_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_ing_btn = ctk.CTkButton(btn_row1, text="✏️ Επεξεργασία", command=self.edit_ingredient, cursor="hand2")
        self.edit_ing_btn.pack(side=tk.LEFT, padx=5)
        
        self.del_ing_btn = ctk.CTkButton(btn_row1, text="❌ Διαγραφή", fg_color="#8b0000", hover_color="#ff1a1a", command=self.delete_ingredient, cursor="hand2")
        self.del_ing_btn.pack(side=tk.LEFT, padx=5)

        btn_row2 = ctk.CTkFrame(self.scroll, fg_color="transparent")
        btn_row2.pack(pady=10)
        
        self.confirm_btn = ctk.CTkButton(btn_row2, text="✓ Επιβεβαίωση Υλικών", fg_color="#28a745", hover_color="#218838", command=self.confirm_ingredients, font=("Segoe UI", 13, "bold"), height=35, cursor="hand2")
        self.confirm_btn.pack(side=tk.LEFT, padx=5)
        
        self.unlock_btn = ctk.CTkButton(btn_row2, text="✎ Ξεκλείδωμα", fg_color="gray", state=tk.DISABLED, command=self.unlock_ingredients, cursor="hand2", height=35)
        self.unlock_btn.pack(side=tk.LEFT, padx=5)
        
        self.manage_ing_btn = ctk.CTkButton(btn_row2, text="Διαχείριση Υλικών 🥕", 
                                    command=lambda: Ingredient.manage(self.window),
                                    fg_color="#C01E1E", hover_color="#d35400", 
                                    cursor="hand2", width=40, height=35)
        self.manage_ing_btn.pack(side=tk.LEFT, padx=5)

        steps_title_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        steps_title_frame.pack(fill=tk.X, pady=(25, 10))

        title_container = ctk.CTkFrame(steps_title_frame, fg_color="transparent")
        title_container.pack(anchor="center")

        self.steps_label = ctk.CTkLabel(title_container, text="Βήματα Εκτέλεσης", font=("Segoe UI", 18, "bold"))
        self.steps_label.pack(side=tk.LEFT)

        info_btn = ctk.CTkButton(
            title_container, 
            text="ⓘ", 
            width=30, 
            height=30,
            fg_color="#a9a9a9",
            hover_color="#3a7ebf",
            font=("Segoe UI", 14, "bold"),
            cursor="hand2"
        )
        info_btn.pack(side=tk.LEFT, padx=5)

        ToolTip(info_btn, "Τα βήματα επιδέχονται τα δικά τους υλικά για να βοηθήσουν στην οργάνωση κάθε μαγειρικής ενότητας.\n\n" \
                "Αφού προστεθούν τα υλικά των βημάτων δεν φαίνονται στον πίνακα λόγω περιορισμένου χώρου. Για να τα δείτε κάντε διπλό κλικ επάνω στο βήμα.")

        steps_tree_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        steps_tree_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tree_frame = ttk.Frame(steps_tree_container)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        steps_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
        steps_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.steps_tree = ttk.Treeview(
            tree_frame, 
            columns=('Αρ.', 'Τίτλος', 'Περιγραφή', 'Διάρκεια'), 
            show='headings', 
            height=6,
            yscrollcommand=steps_scroll_y.set
        )

        self.steps_tree.column('Αρ.', width=60, anchor='center')
        self.steps_tree.column('Τίτλος', width=200, anchor='w')
        self.steps_tree.column('Περιγραφή', width=400, anchor='w')
        self.steps_tree.column('Διάρκεια', width=100, anchor='center')

        self.steps_tree.heading('Αρ.', text='#')
        self.steps_tree.heading('Τίτλος', text='Τίτλος Βήματος')
        self.steps_tree.heading('Περιγραφή', text='Περιγραφή')
        self.steps_tree.heading('Διάρκεια', text='Διάρκεια')

        steps_scroll_y.config(command=self.steps_tree.yview)

        self.steps_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        setup_treeview_scroll(self.steps_tree)

        self.steps_tree.bind('<<TreeviewSelect>>', self.on_step_select)
        self.steps_tree.bind("<Double-1>", lambda e: self.view_step())

        step_btn_row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        step_btn_row.pack(pady=10)

        self.add_step_btn = ctk.CTkButton(step_btn_row, text="➕ Προσθήκη Βήματος", command=lambda: StepFormPage(self), state=tk.DISABLED, cursor="hand2")
        self.add_step_btn.pack(side=tk.LEFT, padx=5)

        self.edit_step_btn = ctk.CTkButton(step_btn_row, text="✏️ Επεξεργασία", state=tk.DISABLED, command=self.edit_step, cursor="hand2")
        self.edit_step_btn.pack(side=tk.LEFT, padx=5)

        self.del_step_btn = ctk.CTkButton(step_btn_row, text="❌ Διαγραφή", state=tk.DISABLED, fg_color="#8b0000", hover_color="#ff1a1a", command=self.delete_step, cursor="hand2")
        self.del_step_btn.pack(side=tk.LEFT, padx=5)

        self.view_step_btn = ctk.CTkButton(step_btn_row, text="📋 Προβολή Βήματος", state=tk.DISABLED, command=self.view_step, cursor="hand2")
        self.view_step_btn.pack(side=tk.LEFT, padx=5)

        self.save_btn = ctk.CTkButton(self.scroll, text="ΑΠΟΘΗΚΕΥΣΗ ΣΥΝΤΑΓΗΣ", height=50, font=("Segoe UI", 16, "bold"), fg_color="#28a745", hover_color="#218838", command=self.save_recipe, cursor="hand2")
        self.save_btn.pack(pady=40)

        if recipe_id: 
            self._prefill_data(recipe_id)

    def on_close(self):
        if getattr(self, 'selected_image_path', None) and "temp_" in self.selected_image_path:
            try: 
                if os.path.exists(self.selected_image_path):
                    os.remove(self.selected_image_path)
            except Exception:
                pass
        self.window.destroy()

    def update_image_preview(self, path):
        if path and os.path.exists(path):
            try:
                with Image.open(path) as raw_img:
                    img_copy = raw_img.copy()
                img_copy.thumbnail((230, 160))
                self.preview_img_obj = ctk.CTkImage(img_copy, size=(230, 160))
                self.img_preview_label.destroy()
                self.img_preview_label = ctk.CTkLabel(self.img_frame, text="", image=self.preview_img_obj)
                self.img_preview_label.pack(expand=True, fill="both")
            except Exception as e:
                print(f"Error loading image: {e}")
                self.preview_img_obj = None
                self.img_preview_label.destroy()
                self.img_preview_label = ctk.CTkLabel(
                    self.img_frame, 
                    text="Σφάλμα φόρτωσης", 
                    text_color="#ffffff"
                )
                self.img_preview_label.pack(expand=True, fill="both")
        else:
            self.preview_img_obj = None
            self.img_preview_label.destroy()
            self.img_preview_label = ctk.CTkLabel(
                self.img_frame, 
                text="Δεν υπάρχει εικόνα\n(Max 1MB, 600x400)", 
                text_color="#ffffff"
            )
            self.img_preview_label.pack(expand=True, fill="both")

    def pick_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
        if not path: return
        if os.path.getsize(path) > 1024 * 1024: 
            return messagebox.showerror("Σφάλμα", "Η εικόνα είναι πολύ μεγάλη (>1MB).")
        
        with Image.open(path) as img:
            img.thumbnail((600, 400))
            clean_name = os.path.basename(path).replace("temp_preview_", "").replace("temp_", "")
            temp_path = os.path.join(IMG_FOLDER, "temp_" + clean_name)
            img.save(temp_path)

        if getattr(self, 'selected_image_path', None) and "temp_" in self.selected_image_path:
            try:
                if os.path.exists(self.selected_image_path):
                    os.remove(self.selected_image_path)
            except Exception:
                pass

        self.selected_image_path = temp_path
        self.selected_image_id = None
        self.update_image_preview(temp_path)

    def remove_image(self):
        if getattr(self, 'selected_image_path', None):
            if "temp_" in self.selected_image_path:
                try: 
                    if os.path.exists(self.selected_image_path):
                        os.remove(self.selected_image_path)
                except Exception as e:
                    print(f"Error removing temp image: {e}")
        
        if hasattr(self, 'selected_image_id') and self.selected_image_id:
            self.image_to_delete = self.selected_image_id
        else:
            self.image_to_delete = None
        
        self.selected_image_path = None
        self.selected_image_id = None
        self.preview_img_obj = None
        
        self.img_preview_label.destroy()
        self.img_preview_label = ctk.CTkLabel(
            self.img_frame, 
            text="Δεν υπάρχει εικόνα\n(Max 1MB, 600x400)", 
            text_color="#ffffff"
        )
        self.img_preview_label.pack(expand=True, fill="both")

    def view_step(self):
        sel = self.steps_tree.selection()
        if not sel:
            return
        
        idx = self.steps_tree.get_children().index(sel[0])
        step = self.steps[idx]
        
        view_window = ctk.CTkToplevel(self.window)
        view_window.title(f"Βήμα {idx + 1}: {step.step_name}")
        center_and_size_window(view_window, 600, 500)
        set_window_icon(view_window)
        view_window.transient(self.window)
        view_window.grab_set()
        
        main_frame = ctk.CTkScrollableFrame(view_window, fg_color="transparent")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text=f"Βήμα {idx + 1}: {step.step_name}", 
                    font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0, 15))
        
        ctk.CTkLabel(main_frame, text=f"⏱️ Διάρκεια: {step.duration_in_minutes} λεπτά", 
                    font=("Segoe UI", 14)).pack(anchor="w", pady=(0, 10))
        
        ctk.CTkLabel(main_frame, text="📝 Περιγραφή:", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(10, 5))
        desc_frame = ctk.CTkFrame(main_frame, corner_radius=10, border_width=1, border_color="gray")
        desc_frame.pack(fill=tk.X, pady=(0, 10))
        
        desc_label = ctk.CTkLabel(desc_frame, text=step.step_text, font=("Segoe UI", 14), 
                                  wraplength=540, justify=tk.LEFT, anchor="nw")
        desc_label.pack(padx=10, pady=10)
        
        ctk.CTkLabel(main_frame, text="🥕 Υλικά Βήματος:", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(10, 5))
        
        allocs = getattr(step, 'allocations', getattr(step, 'step_ingredients', []))
        valid_allocs = [a for a in allocs if get_alloc_val(a, 'ingredient_name', '')]
        
        if valid_allocs:
            ing_frame = ctk.CTkFrame(main_frame, corner_radius=10, border_width=1, border_color="gray")
            ing_frame.pack(fill=tk.X, pady=(0, 10))
            
            for a in allocs:
                name = get_alloc_val(a, 'ingredient_name', '')
                if name:
                    qty = get_alloc_val(a, 'quantity', '')
                    unit = get_alloc_val(a, 'unit', '')
                    notes = get_alloc_val(a, 'notes', '')
                
                prep_text = " (Στάδιο Προετοιμασίας)" if notes == "Στάδιο Προετοιμασίας" else ""
                ing_text = f"• {qty} {unit} {name}{prep_text}"
                ctk.CTkLabel(ing_frame, text=ing_text, font=("Segoe UI", 13), anchor="w").pack(fill=tk.X, padx=10, pady=5)
        else:
            ctk.CTkLabel(main_frame, text="Δεν υπάρχουν υλικά για αυτό το βήμα", 
                        font=("Segoe UI", 13), text_color="gray").pack(anchor="w")
        
        ctk.CTkButton(view_window, text="Κλείσιμο", command=view_window.destroy,
                     fg_color="#1f538d", hover_color="#2a72c1", cursor="hand2",
                     width=150, height=40).pack(pady=20)
        
    def on_step_select(self, event):
        if self.ingredients_locked and self.steps_tree.selection():
            self.view_step_btn.configure(state=tk.NORMAL)
            self.edit_step_btn.configure(state=tk.NORMAL)
            self.del_step_btn.configure(state=tk.NORMAL)
        elif not self.steps_tree.selection():
            self.view_step_btn.configure(state=tk.DISABLED)
            self.edit_step_btn.configure(state=tk.DISABLED)
            self.del_step_btn.configure(state=tk.DISABLED)
        
    def refresh_categories_list(self):
        all_cats = Category.get_all()
        all_cats = sorted(all_cats, key=greek_sort_key)

    def _validate_recipe_form(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Σφάλμα", "Το όνομα της συνταγής είναι υποχρεωτικό.")
            return False, None
        
        cat_val = self.category_entry.get().strip()
        if not cat_val or cat_val.startswith("Επιλέξτε"):
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε μια κατηγορία.")
            return False, None
        
        difficulty = self.difficulty_combo.get()
        if not difficulty:
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε επίπεδο δυσκολίας.")
            return False, None
        
        time_str = self.total_time_entry.get().strip()
        if not time_str:
            messagebox.showerror("Σφάλμα", "Παρακαλώ εισάγετε τον συνολικό χρόνο παρασκευής.")
            return False, None
        
        try:
            normalized = time_str.replace(',', '.')
            minutes_as_float = float(normalized)
            t = int(minutes_as_float)
            if t <= 0:
                messagebox.showerror("Σφάλμα", "Ο χρόνος πρέπει να είναι θετικός αριθμός.")
                return False, None
        except ValueError:
            messagebox.showerror("Σφάλμα", "Εισάγετε έγκυρο αριθμό στο πεδίο χρόνου.")
            return False, None
        
        # Ingredients and steps validation
        if not self.ingredients:
            messagebox.showerror("Σφάλμα", "Προσθέστε τουλάχιστον ένα υλικό στη συνταγή.")
            return False, None
        
        if not self.steps:
            messagebox.showerror("Σφάλμα", "Προσθέστε τουλάχιστον ένα βήμα εκτέλεσης.")
            return False, None
        
        if not self.ingredients_locked:
            messagebox.showerror("Σφάλμα", "Παρακαλώ επιβεβαιώστε τα υλικά πατώντας '✓ Επιβεβαίωση Υλικών'.")
            return False, None
        
        return True, (name, cat_val, difficulty, t)

    def _check_unused_ingredients(self):
        unused_ingredients = self.find_unused_ingredients()
        if not unused_ingredients:
            return True
        
        unused_text = "\n".join([f"• {ing.name} ({format_quantity(ing.quantity)} {ing.unit or ''})" for ing in unused_ingredients[:10]])
        if len(unused_ingredients) > 10:
            unused_text += f"\n... και {len(unused_ingredients) - 10} ακόμα"
        
        result = messagebox.askyesno(
            "Αχρησιμοποίητα Υλικά",
            f"Τα παρακάτω υλικά ΔΕΝ χρησιμοποιούνται σε κανένα βήμα:\n\n{unused_text}\n\n"
            "Θέλετε να αποθηκεύσετε τη συνταγή έτσι κι αλλιώς;\n\n"
            "⚠️ Αν αποθηκεύσετε, αυτά τα υλικά θα παραμείνουν στη λίστα αλλά δε θα καταναλωθούν ποτέ.",
            icon='warning'
        )
        return result

    def _handle_recipe_image(self, recipe):
        if hasattr(self, 'image_to_delete') and self.image_to_delete:
            recipe.image_id = None
        if getattr(self, 'selected_image_path', None) and self.selected_image_path:
            if "temp_" in self.selected_image_path:
                clean_name = os.path.basename(self.selected_image_path).replace("temp_preview_", "").replace("temp_", "")
                final_path = os.path.join(IMG_FOLDER, f"{int(datetime.datetime.now().timestamp())}_{clean_name}")
                
                if os.path.exists(self.selected_image_path):
                    shutil.copy(self.selected_image_path, final_path)
                    try: 
                        os.remove(self.selected_image_path)
                    except Exception: 
                        pass
                    
                recipe.image_id = ImageModel.save_image(final_path)
            else:
                recipe.image_id = self.selected_image_id
    
    def _build_recipe_object(self):
        name = self.name_entry.get().strip()
        cat_val = self.category_entry.get().strip()
        difficulty = self.difficulty_combo.get()
        time_str = self.total_time_entry.get().strip()
        t = int(float(time_str.replace(',', '.')))
        
        rec = Recipe(id=self.recipe_id, name=name, difficulty=difficulty, total_time_minutes=t)
        rec.category_id = Category.get_or_create(cat_val)
        self._handle_recipe_image(rec)
        rec.ingredients = self.ingredients
        rec.steps = self.steps
        rec.mark_ingredients_dirty()
        rec.mark_steps_dirty()
        return rec

    def edit_ingredient(self):
        sel = self.ing_tree.selection()
        if sel: 
            idx = self.ing_tree.get_children().index(sel[0])
            IngredientFormPage(parent_form=self, index=idx, ingredient=self.ingredients[idx])

    def edit_step(self):
        sel = self.steps_tree.selection()
        if sel: 
            idx = self.steps_tree.get_children().index(sel[0])
            StepFormPage(parent_form=self, index=idx, step=self.steps[idx])

    def refresh_ingredients_list(self):
        for i in self.ing_tree.get_children(): 
            self.ing_tree.delete(i)
        
        unused_set = set()
        if self.ingredients_locked:
            unused = self.find_unused_ingredients()
            unused_set = {(ing.name, ing.unit or '') for ing in unused}
        
        if ctk.get_appearance_mode() == "Dark":
            self.ing_tree.tag_configure('even', background='#2a2d2e')
            self.ing_tree.tag_configure('odd', background='#343638')
            self.ing_tree.tag_configure('unused', background='#5a2a2a')  # Dark red for unused
        else:
            self.ing_tree.tag_configure('even', background='#f2f2f2')
            self.ing_tree.tag_configure('odd', background='#ffffff')
            self.ing_tree.tag_configure('unused', background='#ffe0e0')  # Light red for unused
        
        for i, ing in enumerate(self.ingredients):
            is_unused = (ing.name, ing.unit or '') in unused_set
            
            if is_unused and self.ingredients_locked:
                tag = 'unused'
            else:
                tag = 'even' if i % 2 == 0 else 'odd'
            
            display_quantity = format_quantity(ing.quantity)
            self.ing_tree.insert('', 'end', values=(ing.name, display_quantity, ing.unit or "", ing.notes or ""), tags=(tag,))

    def refresh_steps_list(self):
        for i in self.steps_tree.get_children(): 
            self.steps_tree.delete(i)
        for i, st in enumerate(self.steps, 1): 
            self.steps_tree.insert('', 'end', values=(i, st.step_name, st.step_text, f"{st.duration_in_minutes} min"))

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
            for i, st in enumerate(self.steps): 
                st.sequence_order = i + 1
            self.refresh_steps_list()

    def confirm_ingredients(self):
        if not self.ingredients: 
            return messagebox.showwarning("Προσοχή", "Προσθέστε τουλάχιστον ένα υλικό.")
        
        if self.steps:
            issues = self.validate_steps_against_ingredients()
            if issues:
                result = messagebox.askyesno(
                    "Προσοχή - Υπέρβαση Υλικών",
                    "Τα βήματα που έχετε δημιουργήσει χρησιμοποιούν περισσότερο υλικό από αυτό που υπάρχει:\n\n"
                    + "\n".join(issues) +
                    "\n\nΘέλετε να συνεχίσετε και να κλειδώσετε τα υλικά ΠΑΡΑ ΤΑΥΤΑ;\n"
                    "⚠️ Αν συνεχίσετε, η εκτέλεση της συνταγής μπορεί να ζητήσει υλικά που δεν έχετε.\n\n"
                    "Επιλέξτε 'Ναι' για να κλειδώσετε έτσι κι αλλιώς, ή 'Όχι' για να διορθώσετε πρώτα τα υλικά."
                )
                if not result:
                    return
        
        result = messagebox.askyesno(
            "Επιβεβαίωση Υλικών", 
            f"Έχετε προσθέσει {len(self.ingredients)} υλικό/ά.\n\n"
            "Είστε σίγουροι ότι τα έχετε προσθέσει όλα;\n\n"
            "⚠️ ΣΗΜΑΝΤΙΚΟ: Μετά την επιβεβαίωση, δεν θα μπορείτε να προσθέσετε, να επεξεργαστείτε ή να διαγράψετε υλικά, "
            "εκτός αν πατήσετε το κουμπί 'Ξεκλείδωμα' (το οποίο θα σας επιτρέψει να επεξεργαστείτε ξανά τα υλικά, "
            "αλλά τα υλικά που έχετε ήδη κατανέμει στα βήματα θα σβηστούν - θα χρειαστεί να τα επαναπροσθέσετε)."
        )
        if not result:
            return
        
        self.ingredients_locked = True
        self.refresh_ingredients_list()

        self.add_step_btn.configure(state=tk.NORMAL)
        self.edit_step_btn.configure(state=tk.NORMAL)
        self.del_step_btn.configure(state=tk.NORMAL)
        self.view_step_btn.configure(state=tk.NORMAL)

        self.add_ing_btn.configure(state=tk.DISABLED)
        self.edit_ing_btn.configure(state=tk.DISABLED)
        self.del_ing_btn.configure(state=tk.DISABLED)

        if hasattr(self, 'manage_ing_btn'):
            self.manage_ing_btn.configure(state=tk.DISABLED)

        self.confirm_btn.configure(state=tk.DISABLED, fg_color="gray")
        self.unlock_btn.configure(state=tk.NORMAL, fg_color="#e67e22")

        self.steps_label.configure(text="Βήματα Εκτέλεσης")
        if ctk.get_appearance_mode() == "Dark":
            self.steps_label.configure(text_color="white")
        else:
            self.steps_label.configure(text_color="#2b2b2b")

    def unlock_ingredients(self):
        if not self.steps:
            self.ingredients_locked = False
            self.add_ing_btn.configure(state=tk.NORMAL)
            self.edit_ing_btn.configure(state=tk.NORMAL)
            self.del_ing_btn.configure(state=tk.NORMAL)
            if hasattr(self, 'manage_ing_btn'):
                self.manage_ing_btn.configure(state=tk.NORMAL)
            self.confirm_btn.configure(state=tk.NORMAL, fg_color="#28a745")
            self.unlock_btn.configure(state=tk.DISABLED, fg_color="gray")
            return
        
        if not messagebox.askyesno(
            "Ξεκλείδωμα Υλικών",
            f"Υπάρχουν {len(self.steps)} βήματα που περιέχουν υλικά.\n\n"
            "Το ξεκλείδωμα θα:\n"
            "✓ Σας επιτρέψει να επεξεργαστείτε τα υλικά\n"
            "✓ Διαγράψει ΟΛΑ τα υλικά από τα βήματα (θα παραμείνουν οι τίτλοι, οι περιγραφές και οι διάρκειες)\n"
            "✓ Απαιτήσει να ξαναπροσθέσετε χειροκίνητα τα υλικά σε κάθε βήμα\n\n"
            "Θέλετε να συνεχίσετε;"
        ):
            return
        
        for step in self.steps:
            step.allocations = []
            step.step_ingredients = []
        
        self.refresh_steps_list()
        
        self.ingredients_locked = False
        
        self.add_ing_btn.configure(state=tk.NORMAL)
        self.edit_ing_btn.configure(state=tk.NORMAL)
        self.del_ing_btn.configure(state=tk.NORMAL)
        if hasattr(self, 'manage_ing_btn'):
            self.manage_ing_btn.configure(state=tk.NORMAL)
        
        self.add_step_btn.configure(state=tk.NORMAL)
        self.edit_step_btn.configure(state=tk.NORMAL)
        self.del_step_btn.configure(state=tk.NORMAL)
        self.view_step_btn.configure(state=tk.NORMAL)
        
        self.confirm_btn.configure(state=tk.NORMAL, fg_color="#28a745")
        self.unlock_btn.configure(state=tk.DISABLED, fg_color="gray")
        
        self.steps_label.configure(text="Βήματα Εκτέλεσης (⚠️ τα υλικά διαγράφηκαν - προσθέστε τα ξανά)")
        if ctk.get_appearance_mode() == "Dark":
            self.steps_label.configure(text_color="orange")
        else:
            self.steps_label.configure(text_color="#d35400")
        
        messagebox.showinfo(
            "Ενημέρωση",
            "Τα υλικά αφαιρέθηκαν από όλα τα βήματα.\n\n"
            "Μπορείτε τώρα να επεξεργαστείτε τα υλικά και στη συνέχεια να ξαναπροσθέσετε τα υλικά σε κάθε βήμα."
        )

    def validate_steps_against_ingredients(self):
        issues = []
        remaining = {}
        for idx, ing in enumerate(self.ingredients):
            remaining[idx] = {
                'name': ing.name,
                'quantity': ing.quantity,
                'unit': ing.unit,
                'used': 0
            }
        
        for step in self.steps:
            allocs = getattr(step, 'allocations', getattr(step, 'step_ingredients', []))
            for alloc in allocs:
                if get_alloc_val(alloc, 'notes') == "Στάδιο Προετοιμασίας":
                    continue
                
                ing_name = get_alloc_val(alloc, 'ingredient_name', '')
                qty = get_alloc_val(alloc, 'quantity', 0)
                unit = get_alloc_val(alloc, 'unit', '')
                
                for idx, ing in enumerate(self.ingredients):
                    if ing.name == ing_name and ing.unit == unit:
                        remaining[idx]['used'] += qty
                        break
        
        for idx, data in remaining.items():
            if data['used'] > data['quantity'] + 0.001:  # Small tolerance for float errors
                issues.append(f"• {data['name']}: Χρησιμοποιούνται {data['used']:.2f} {data['unit']} "
                            f"αλλά υπάρχουν {data['quantity']:.2f} {data['unit']}")
        
        return issues
    
    def find_unused_ingredients(self):
        if not self.steps:
            return self.ingredients.copy() if self.ingredients else []
        
        used_ingredients = set()
        
        for step in self.steps:
            allocs = getattr(step, 'allocations', getattr(step, 'step_ingredients', []))
            for alloc in allocs:
                if get_alloc_val(alloc, 'notes') == "Στάδιο Προετοιμασίας":
                    continue
                
                ing_name = get_alloc_val(alloc, 'ingredient_name', '')
                unit = get_alloc_val(alloc, 'unit', '')
                
                if ing_name:
                    used_ingredients.add(f"{ing_name}|{unit}")
        
        unused = []
        for ing in self.ingredients:
            key = f"{ing.name}|{ing.unit or ''}"
            if key not in used_ingredients:
                unused.append(ing)
        
        return unused

    def _prefill_data(self, rid):      
        recipe = Recipe.get_recipe_by_id(rid)
        if not recipe:
            messagebox.showerror("Σφάλμα", "Δεν βρέθηκε η συνταγή")
            return
        
        self.name_entry.insert(0, recipe.name)
        
        category_display = recipe.category if recipe.category and recipe.category.strip() else "Επιλέξτε απο το κουμπί δίπλα..."
        set_readonly_entry(self.category_entry, category_display)
        
        self.difficulty_combo.set(recipe.difficulty if recipe.difficulty else "Μέτρια")
        self.total_time_entry.insert(0, str(recipe.total_time_minutes if recipe.total_time_minutes else 0))
        
        self.ingredients = sorted(recipe.ingredients, key=lambda x: greek_sort_key(x.name)) if recipe.ingredients else []
        self.steps = recipe.steps if recipe.steps else []

        self.image_to_delete = None
        
        image_path = recipe.get_image_path() if hasattr(recipe, 'get_image_path') else None
        if image_path and os.path.exists(image_path):
            self.selected_image_path = image_path
            self.selected_image_id = recipe.image_id
            self.update_image_preview(image_path)
        else:
            self.selected_image_path = None
            self.selected_image_id = None
        
        self.refresh_ingredients_list()
        self.refresh_steps_list()
        
        if self.ingredients and self.steps:
            self.ingredients_locked = True
            
            self.add_ing_btn.configure(state=tk.DISABLED)
            self.edit_ing_btn.configure(state=tk.DISABLED)
            self.del_ing_btn.configure(state=tk.DISABLED)
            if hasattr(self, 'manage_ing_btn'):
                self.manage_ing_btn.configure(state=tk.DISABLED)
            
            self.add_step_btn.configure(state=tk.NORMAL)
            self.edit_step_btn.configure(state=tk.NORMAL)
            self.del_step_btn.configure(state=tk.NORMAL)
            self.view_step_btn.configure(state=tk.NORMAL)
            
            self.confirm_btn.configure(state=tk.DISABLED, fg_color="gray")
            self.unlock_btn.configure(state=tk.NORMAL, fg_color="#e67e22")
            
            self.steps_label.configure(text="Βήματα Εκτέλεσης")
            if ctk.get_appearance_mode() == "Dark":
                self.steps_label.configure(text_color="white")
            else:
                self.steps_label.configure(text_color="#2b2b2b")
            
            self.refresh_ingredients_list()

    def save_recipe(self):
        is_valid, _ = self._validate_recipe_form()
        if not is_valid:
            return
        
        if not self._check_unused_ingredients():
            return
        
        try:
            name = self.name_entry.get().strip()
            cat_val = self.category_entry.get().strip()
            difficulty = self.difficulty_combo.get()
            time_str = self.total_time_entry.get().strip()
            t = int(float(time_str.replace(',', '.')))
            
            rec = Recipe(id=self.recipe_id, name=name, difficulty=difficulty, total_time_minutes=t)
            rec.category_id = Category.get_or_create(cat_val)
            
            old_image_id = self.image_to_delete if hasattr(self, 'image_to_delete') else None
            
            self._handle_recipe_image(rec)
            
            rec.ingredients = self.ingredients
            rec.steps = self.steps
            
            rec.mark_ingredients_dirty()
            rec.mark_steps_dirty()
            
            rec.save()
            
            if old_image_id:
                with DatabaseConn("recipe_database.db") as db:
                    db.execute("SELECT COUNT(*) FROM recipes WHERE image_id = ?", (old_image_id,))
                    count = db.fetchone()[0]
                    if count == 0:
                        ImageModel.delete_image(old_image_id)
                self.image_to_delete = None
            
            messagebox.showinfo("Επιτυχία", f"Η συνταγή '{rec.name}' αποθηκεύτηκε!")
            self.parent_app.load_recipes_from_db()
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Σφάλμα Αποθήκευσης", f"Κάτι πήγε στραβά:\n{str(e)}")


# =============================================================================
# --- 3. ΣΕΛΙΔΑ ΕΚΤΕΛΕΣΗΣ (COOKING MODE) ---
# =============================================================================

class RecipeExecutePage:
    def __init__(self, recipe_id, parent):
        self.parent = parent
        self.recipe = Recipe.get_recipe_by_id(recipe_id)
        self.steps = self.recipe.steps
        self.current_index = -1 
        self.timer_seconds = 0
        self.timer_running = False
        self.is_paused = False 
        self.timer_job = None
        self.window = ctk.CTkToplevel()
        self.window.title("Cooking Mode")
        center_and_size_window(self.window, 950, 800)
        self.window.resizable(True, True)              
        set_window_icon(self.window)
        self.window.grab_set()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.main_container = ctk.CTkFrame(self.window, fg_color="transparent")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        image_path = self.recipe.get_image_path() if hasattr(self.recipe, 'get_image_path') else None
        if image_path and os.path.exists(image_path):
            try:
                img = ctk.CTkImage(Image.open(image_path), size=(240, 160))
                ctk.CTkLabel(self.main_container, text="", image=img).pack(pady=10)
            except Exception as e:
                print(f"Could not load image: {e}")

        ctk.CTkLabel(self.main_container, text=self.recipe.name, font=("Segoe UI", 30, "bold"), text_color="#2a72c1").pack(pady=5)
        
        self.prog_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.prog_frame.pack(pady=10)
        
        self.prog_bar = ctk.CTkProgressBar(self.prog_frame, width=500)
        self.prog_bar.set(0)
        self.prog_bar.pack(side=tk.LEFT, padx=(0, 15))
        
        self.prog_pct_lbl = ctk.CTkLabel(self.prog_frame, text="0%", font=("Segoe UI", 18, "bold"))
        self.prog_pct_lbl.pack(side=tk.LEFT)

        self.countdown_lbl = ctk.CTkLabel(self.prog_frame, text="", font=("Consolas", 20, "bold"), text_color="#e67e22")
        self.countdown_lbl.pack(side=tk.LEFT, padx=(35, 0))

        btn_f = ctk.CTkFrame(self.main_container, fg_color="transparent")
        btn_f.pack(side=tk.BOTTOM, pady=10)
        
        self.prev_btn = ctk.CTkButton(btn_f, text="⏮ Πίσω", width=140, height=45, font=("Segoe UI", 14), command=self.previous, cursor="hand2")
        self.prev_btn.pack(side=tk.LEFT, padx=10)
        
        self.start_btn = ctk.CTkButton(btn_f, text="▶ Έναρξη", fg_color="#1f538d", width=140, height=45, font=("Segoe UI", 14), command=self.start_timer, cursor="hand2")
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.pause_btn = ctk.CTkButton(btn_f, text="⏸ Παύση", width=140, height=45, font=("Segoe UI", 14), command=self.toggle_pause, state=tk.DISABLED, cursor="hand2")
        self.pause_btn.pack(side=tk.LEFT, padx=10)
        
        self.next_btn = ctk.CTkButton(btn_f, text="Επόμενο ⏭", fg_color="#28a745", hover_color="#218838", width=140, height=45, font=("Segoe UI", 15, "bold"), command=self.next, cursor="hand2")
        self.next_btn.pack(side=tk.LEFT, padx=10)

        self.step_frame = ctk.CTkFrame(self.main_container, corner_radius=15)
        self.step_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.num_lbl = ctk.CTkLabel(self.step_frame, text="", font=("Segoe UI", 24, "bold"), text_color="#e67e22")
        self.num_lbl.pack(pady=10)
        self.title_lbl = ctk.CTkLabel(self.step_frame, text="", font=("Segoe UI", 22, "bold"))
        self.title_lbl.pack(pady=5)
        
        desc_frame = ctk.CTkFrame(self.step_frame, fg_color="transparent")
        desc_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 15))
        
        self.desc_text = tk.Text(desc_frame, font=("Segoe UI", 17), wrap=tk.WORD,
                                  relief="flat", padx=15, pady=15)
        
        if ctk.get_appearance_mode() == "Dark":
            self.desc_text.configure(bg="#2b2b2b", fg="white")
        else:
            self.desc_text.configure(bg="#ffffff", fg="black")
        
        desc_scrollbar = tk.Scrollbar(desc_frame, orient="vertical", command=self.desc_text.yview)
        self.desc_text.configure(yscrollcommand=desc_scrollbar.set)
        
        self.desc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.desc_text.configure(state=tk.DISABLED)

        self.show_step()

    def show_step(self):
        self.stop_timer()
        self.is_paused = False
        self.pause_btn.configure(state=tk.DISABLED, text="⏸ Παύση")
        
        if self.current_index == -1:
            self.num_lbl.configure(text="Βήμα 0: Προετοιμασία")
            self.title_lbl.configure(text="Mise en Place")
            sorted_ings = sorted(self.recipe.ingredients, key=lambda x: greek_sort_key(x.name))
            ings = "\n".join([f"• {format_quantity(i.quantity)} {i.unit or ''} {i.name}" for i in sorted_ings])
            self.desc_text.configure(state=tk.NORMAL)
            self.desc_text.delete("1.0", tk.END)
            self.desc_text.insert("1.0", f"Συγκεντρώστε στον πάγκο σας:\n\n{ings}")
            self.desc_text.configure(state=tk.DISABLED)
            
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
            
            allocs = getattr(s, 'allocations', getattr(s, 'step_ingredients', []))
            ing_texts = []
            for a in allocs:
                name = get_alloc_val(a, 'ingredient_name', '')
                qty = get_alloc_val(a, 'quantity', '')
                unit = get_alloc_val(a, 'unit', '')
                notes = get_alloc_val(a, 'notes', '')
                
                prep_mark = " (Στάδιο Προετοιμασίας)" if notes == "Στάδιο Προετοιμασίας" else ""
                if name: 
                    display_qty = format_quantity(qty)
                    ing_texts.append(f"• {display_qty} {unit} {name}{prep_mark}")
            
            ing_str = "\n".join(ing_texts)
            desc_text = s.step_text
            if ing_str: 
                desc_text += f"\n\nΥλικά Βήματος:\n{ing_str}"
            
            self.desc_text.configure(state=tk.NORMAL)
            self.desc_text.delete("1.0", tk.END)
            self.desc_text.insert("1.0", desc_text)
            self.desc_text.configure(state=tk.DISABLED)

            total_steps = len(self.steps)
            progress = (self.current_index + 1) / total_steps if total_steps > 0 else 1
            self.prog_bar.set(progress)
            self.prog_pct_lbl.configure(text=f"{int(progress * 100)}%")
            
            self.prev_btn.configure(state=tk.NORMAL)
            if s.duration_in_minutes > 0: 
                self.start_btn.configure(state=tk.NORMAL, text="▶ Έναρξη")
                self.countdown_lbl.configure(text=f"⏱ {s.duration_in_minutes:02d}:00")
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
            self.countdown_lbl.configure(text=f"⏱ {m:02d}:{s:02d}")
            self.timer_seconds -= 1
            self.timer_job = self.window.after(1000, self._tick)
        else: 
            self.countdown_lbl.configure(text="⏱ ΧΡΟΝΟΣ!")
            self.timer_running = False
            self.pause_btn.configure(state=tk.DISABLED)
            self.window.bell()
            messagebox.showinfo("ChefMaster", "Ολοκληρώθηκε το βήμα!")

    def stop_timer(self):
        self.timer_running = False
        if getattr(self, 'timer_job', None): 
            self.window.after_cancel(self.timer_job)
            self.timer_job = None

    def previous(self): 
        self.current_index -= 1
        self.show_step()
        
    def next(self):
        if self.current_index < len(self.steps) - 1: 
            self.current_index += 1
            self.show_step()
        else: 
            messagebox.showinfo("Μπράβο!", "Η συνταγή ολοκληρώθηκε!")
            self.window.destroy()
            
    def on_close(self): 
        self.stop_timer()
        self.window.destroy()
# =============================================================================
# --- 3.5 ΣΕΛΙΔΑ ΠΡΟΒΟΛΗΣ ΣΥΝΤΑΓΗΣ (READ-ONLY) ---
# =============================================================================

class RecipeViewPage:
    def __init__(self, recipe_id, parent):
        self.parent = parent
        self.recipe = Recipe.get_recipe_by_id(recipe_id)
        
        if not self.recipe:
            messagebox.showerror("Σφάλμα", "Δεν βρέθηκε η συνταγή.")
            return
        
        self.window = ctk.CTkToplevel()
        self.window.title(f"Προβολή Συνταγής: {self.recipe.name}")
        center_and_size_window(self.window, 900, 750)
        set_window_icon(self.window)
        self.window.grab_set()
        
        main_frame = ctk.CTkScrollableFrame(self.window, fg_color="transparent")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ctk.CTkLabel(header_frame, text=self.recipe.name, font=("Segoe UI", 28, "bold"), 
                    text_color="#2a72c1").pack(anchor="center", pady=(0, 10))
        
        image_path = self.recipe.get_image_path() if hasattr(self.recipe, 'get_image_path') else None
        if image_path and os.path.exists(image_path):
            try:
                img = ctk.CTkImage(Image.open(image_path), size=(200, 150))
                ctk.CTkLabel(header_frame, text="", image=img).pack(pady=5)
            except Exception as e:
                print(f"Could not load image: {e}")
        
        info_row = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_row.pack(pady=10)
        
        cat_frame = ctk.CTkFrame(info_row, corner_radius=10, border_width=1, border_color="#1f538d")
        cat_frame.pack(side=tk.LEFT, padx=10)
        ctk.CTkLabel(cat_frame, text=f"📁 {self.recipe.category or 'Χωρίς κατηγορία'}", 
                    font=("Segoe UI", 13)).pack(padx=15, pady=5)
        
        diff_colors = {"Εύκολη": "#28a745", "Μέτρια": "#ff9800", "Δύσκολη": "#f44336"}
        diff_color = diff_colors.get(self.recipe.difficulty, "#1f538d")
        diff_frame = ctk.CTkFrame(info_row, corner_radius=10, border_width=1, border_color=diff_color)
        diff_frame.pack(side=tk.LEFT, padx=10)
        ctk.CTkLabel(diff_frame, text=f"⭐ {self.recipe.difficulty or 'Μέτρια'}", 
                    font=("Segoe UI", 13), text_color=diff_color).pack(padx=15, pady=5)
        
        time_frame = ctk.CTkFrame(info_row, corner_radius=10, border_width=1, border_color="#1f538d")
        time_frame.pack(side=tk.LEFT, padx=10)
        ctk.CTkLabel(time_frame, text=f"⏱️ {self.recipe.total_time_minutes or 0} λεπτά", 
                    font=("Segoe UI", 13)).pack(padx=15, pady=5)
        
        ingredients_frame = ctk.CTkFrame(main_frame)
        ingredients_frame.pack(fill=tk.X, pady=(0, 20))
        
        ctk.CTkLabel(ingredients_frame, text="📝 Συστατικά", font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0, 10))
        
        ing_grid = ctk.CTkFrame(ingredients_frame, fg_color="transparent")
        ing_grid.pack(fill=tk.X)
        
        ctk.CTkLabel(ing_grid, text="Όνομα", font=("Segoe UI", 14, "bold"), width=250, anchor="w").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(ing_grid, text="Ποσότητα", font=("Segoe UI", 14, "bold"), width=100, anchor="w").grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(ing_grid, text="Μονάδα", font=("Segoe UI", 14, "bold"), width=100, anchor="w").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(ing_grid, text="Σημειώσεις", font=("Segoe UI", 14, "bold"), width=200, anchor="w").grid(row=0, column=3, padx=10, pady=5, sticky="w")
        
        ctk.CTkFrame(ing_grid, height=2, fg_color="gray").grid(row=1, column=0, columnspan=4, sticky="ew", padx=10, pady=5)
        
        row = 2
        for ing in sorted(self.recipe.ingredients, key=lambda x: greek_sort_key(x.name)):
            ctk.CTkLabel(ing_grid, text=ing.name, anchor="w", font=("Segoe UI", 13)).grid(row=row, column=0, padx=10, pady=3, sticky="w")
            display_quantity = format_quantity(ing.quantity)
            ctk.CTkLabel(ing_grid, text=display_quantity, anchor="w", font=("Segoe UI", 13)).grid(row=row, column=1, padx=10, pady=3, sticky="w")
            ctk.CTkLabel(ing_grid, text=ing.unit or "-", anchor="w", font=("Segoe UI", 13)).grid(row=row, column=2, padx=10, pady=3, sticky="w")
            ctk.CTkLabel(ing_grid, text=ing.notes or "-", anchor="w", font=("Segoe UI", 13)).grid(row=row, column=3, padx=10, pady=3, sticky="w")
            row += 1
        
        steps_frame = ctk.CTkFrame(main_frame)
        steps_frame.pack(fill=tk.BOTH, expand=True)
        
        ctk.CTkLabel(steps_frame, text="👨‍🍳 Βήματα Εκτέλεσης", font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0, 10))
        
        for idx, step in enumerate(self.recipe.steps, 1):
            step_card = ctk.CTkFrame(steps_frame, corner_radius=10, border_width=1, border_color="#3a7ebf")
            step_card.pack(fill=tk.X, pady=10)
            
            step_header = ctk.CTkFrame(step_card, fg_color="transparent")
            step_header.pack(fill=tk.X, padx=15, pady=10)
            
            ctk.CTkLabel(step_header, text=f"Βήμα {idx}: {step.step_name}", 
                        font=("Segoe UI", 16, "bold"), text_color="#2a72c1").pack(side=tk.LEFT)
            
            if step.duration_in_minutes > 0:
                ctk.CTkLabel(step_header, text=f"⏱️ {step.duration_in_minutes} λεπτά", 
                            font=("Segoe UI", 13), text_color="gray").pack(side=tk.RIGHT)
            
            if step.step_text:
                desc_frame = ctk.CTkFrame(step_card, fg_color="transparent")
                desc_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
                ctk.CTkLabel(desc_frame, text=step.step_text, font=("Segoe UI", 13), 
                            wraplength=800, justify=tk.LEFT, anchor="w").pack(anchor="w")
            
            allocs = getattr(step, 'allocations', getattr(step, 'step_ingredients', []))
            valid_allocs = [a for a in allocs if get_alloc_val(a, 'ingredient_name', '')]
            if valid_allocs:
                ing_frame = ctk.CTkFrame(step_card, fg_color="transparent")
                ing_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
                
                ctk.CTkLabel(ing_frame, text="Υλικά βήματος:", font=("Segoe UI", 13, "bold")).pack(anchor="w")
                
                ing_list_frame = ctk.CTkFrame(ing_frame, fg_color="transparent")
                ing_list_frame.pack(anchor="w", padx=20)
                
                for a in allocs:
                    name = get_alloc_val(a, 'ingredient_name', '')
                    if name:
                        qty = get_alloc_val(a, 'quantity', '')
                        unit = get_alloc_val(a, 'unit', '')
                        notes = get_alloc_val(a, 'notes', '')
                    
                    prep_mark = " (Προετοιμασία)" if notes == "Στάδιο Προετοιμασίας" else ""
                    ing_text = f"• {qty} {unit} {name}{prep_mark}"
                    ctk.CTkLabel(ing_list_frame, text=ing_text, font=("Segoe UI", 12)).pack(anchor="w")
        
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill=tk.X, pady=20)
        
        ctk.CTkButton(btn_frame, text="Κλείσιμο", command=self.window.destroy,
                     fg_color="#1f538d", hover_color="#2a72c1", cursor="hand2",
                     width=150, height=40).pack()

# =============================================================================
# --- 4. ΚΕΝΤΡΙΚΗ ΕΦΑΡΜΟΓΗ (DASHBOARD) ---
# =============================================================================

class RecipeApp:
    def __init__(self, root):
        self.root = root
        set_window_icon(self.root)
        self.root.title("ChefMaster Pro - Dashboard")
        self.root.geometry("1250x850")
        self._build_menu_bar()
        self.style = ttk.Style()
        self.style.theme_use("default")
        
        self.current_filter_category = "Όλες οι Κατηγορίες"
        self.current_filter_difficulty = "Όλες"
        self.current_filter_time = "Όλοι οι Χρόνοι"
        self.current_filter_aa = ""      
        self.current_filter_name = ""    
        self.master_recipe_list = []
        
        self.current_theme_setting = "System" 
        self.auto_theme_job = None

        self.sidebar = ctk.CTkFrame(self.root, width=240, corner_radius=0)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        ctk.CTkLabel(self.sidebar, text="ChefMaster", font=("Segoe UI", 28, "bold")).pack(pady=40)
        
        btn_opts = {"height": 40, "font": ("Segoe UI", 14), "fg_color": "#1f538d", "hover_color": "#2a72c1", "cursor": "hand2"}
        ctk.CTkButton(self.sidebar, text="➕ Νέα Συνταγή", command=lambda: RecipeFormPage(self), **btn_opts).pack(pady=8, padx=20, fill=tk.X)
        ctk.CTkButton(self.sidebar, text="👨‍🍳 Εκτέλεση", command=self.recipe_launch, fg_color="#e67e22", hover_color="#d35400", font=("Segoe UI", 14, "bold"), cursor="hand2", height=40).pack(pady=8, padx=20, fill=tk.X)
        ctk.CTkButton(self.sidebar, text="✏️ Ενημέρωση", command=self.open_update, **btn_opts).pack(pady=8, padx=20, fill=tk.X)
        ctk.CTkButton(self.sidebar, text="🔍 Προβολή", command=lambda: self.open_update(view_only=True), fg_color="#9b59b6", hover_color="#8e44ad", cursor="hand2", height=40, font=("Segoe UI", 14)).pack(pady=8, padx=20, fill=tk.X)
        ctk.CTkButton(self.sidebar, text="❌ Διαγραφή", fg_color="#8b0000", hover_color="#ff1a1a", command=self.delete_recipe, cursor="hand2", height=40, font=("Segoe UI", 14)).pack(pady=8, padx=20, fill=tk.X)
        ctk.CTkButton(self.sidebar, text="📤 Εξαγωγή...", fg_color="#28a745", hover_color="#218838", command=self.open_export, cursor="hand2", height=40, font=("Segoe UI", 14)).pack(pady=30, padx=20, fill=tk.X)

        theme_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        theme_frame.pack(side=tk.BOTTOM, pady=20, padx=20)
        ctk.CTkLabel(theme_frame, text="Θέμα Εφαρμογής:", font=("Segoe UI", 12)).pack(anchor="w")
        self.theme_menu = ctk.CTkOptionMenu(theme_frame, values=["Dark", "Light", "System"], command=self.user_changed_theme, cursor="hand2")
        self.theme_menu.pack(pady=5)
        self.theme_menu.set("Dark")

        self.main_area = ctk.CTkFrame(self.root, corner_radius=15)
        self.main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        search_f = ctk.CTkFrame(self.main_area, fg_color="transparent")
        search_f.pack(fill=tk.X, padx=30, pady=25)
        
        ctk.CTkLabel(search_f, text="🔍 Αναζήτηση:", font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT, padx=10)
        self.search_ent = ctk.CTkEntry(search_f, placeholder_text="Όνομα, Κατηγορία, Χρόνος...", height=40, font=("Segoe UI", 14))
        self.search_ent.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_ent.bind("<KeyRelease>", self.perform_search)
        enable_right_click_menu(self.search_ent)

        self.filter_btn = ctk.CTkButton(search_f, text="⚙️ Προηγμένα Φίλτρα", font=("Segoe UI", 14, "bold"), height=40, command=self.open_filters_dialog, cursor="hand2")
        self.filter_btn.pack(side=tk.LEFT, padx=10)

        dash_f = ctk.CTkFrame(self.main_area, fg_color="transparent")
        dash_f.pack(fill=tk.X, padx=30, pady=10)
        self.card_total = self.create_card(dash_f, "Σύνολο Συνταγών", "#1f538d")
        self.card_pop = self.create_card(dash_f, "Δημοφιλέστερη Κατηγορία", "#e67e22")

        table_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=15)
        
        self.table_scroll = ttk.Scrollbar(table_frame)
        self.table_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.table = ttk.Treeview(table_frame, columns=('aa', 'name', 'category', 'difficulty', 'time'), displaycolumns=('aa', 'name', 'category', 'difficulty', 'time'), show='headings', yscrollcommand=self.table_scroll.set)
        
        self.table.heading('aa', text='Α/Α')
        self.table.heading('name', text='🍲 Όνομα Συνταγής')
        self.table.heading('category', text='🏷️ Κατηγορία')
        self.table.heading('difficulty', text='⭐ Δυσκολία')
        self.table.heading('time', text='⏱️ Χρόνος')
        
        self.table.column('aa', width=50, anchor='center')
        self.table.column('name', width=400, anchor='center')
        self.table.column('category', width=180, anchor='center')
        self.table.column('difficulty', width=130, anchor='center')
        self.table.column('time', width=120, anchor='center')
        
        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.table_scroll.config(command=self.table.yview)
        
        self.table.bind("<Double-1>", lambda e: self.open_update(view_only=True))
        self.table.bind("<Motion>", self.on_tree_motion)

        self.apply_theme()
        self.load_recipes_from_db()

    def _build_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        menu_kwargs = dict(
            tearoff=0,
            font=("Segoe UI", 11),
            bg="#2a2d2e",
            fg="white",
            activebackground="#1f538d",
            activeforeground="white",
        )

        actions_menu = tk.Menu(menubar, **menu_kwargs)
        menubar.add_cascade(label="📋 Ενέργειες", menu=actions_menu)

        actions_menu.add_command(
            label="Νέα Συνταγή",
            command=lambda: RecipeFormPage(self),
        )
        actions_menu.add_command(
            label="Προβολή Συνταγής",
            command=lambda: self.open_update(view_only=True),
        )
        actions_menu.add_command(
            label="Εκτέλεση Συνταγής",
            command=self.recipe_launch,
        )
        actions_menu.add_command(
            label="Ενημέρωση Συνταγής",
            command=self.open_update,
        )
        actions_menu.add_separator()
        actions_menu.add_command(
            label="Διαγραφή Συνταγής",
            command=self.delete_recipe,
        )
        actions_menu.add_separator()
        actions_menu.add_command(
            label="Προηγμένα Φίλτρα",
            command=self.open_filters_dialog,
        )
        actions_menu.add_command(
            label="Εξαγωγή Δεδομένων…",
            command=self.open_export,
        )
        actions_menu.add_separator()
        actions_menu.add_command(
            label="Έξοδος",
            command=self.root.destroy,
        )

        theme_menu = tk.Menu(menubar, **menu_kwargs)
        menubar.add_cascade(label="🎨 Θέμα", menu=theme_menu)
        theme_menu.add_command(
            label="Σκούρο (Dark)",
            command=lambda: self._set_theme_from_menu("Dark"),
        )
        theme_menu.add_command(
            label="Φωτεινό (Light)",
            command=lambda: self._set_theme_from_menu("Light"),
        )
        theme_menu.add_command(
            label="Σύστημα (Auto)",
            command=lambda: self._set_theme_from_menu("System"),
        )
    
    def _set_theme_from_menu(self, mode):
        try:
            self.theme_menu.set(mode)
        except Exception:
            pass
        self.user_changed_theme(mode)    

    def create_card(self, parent, title, color):
        f = ctk.CTkFrame(parent, corner_radius=12, border_width=2, border_color=color)
        f.pack(side=tk.LEFT, padx=10, expand=True, fill="both")
        ctk.CTkLabel(f, text=title, font=("Segoe UI", 13)).pack(pady=(10, 0))
        lbl = ctk.CTkLabel(f, text="-", font=("Segoe UI", 24, "bold"), text_color=color)
        lbl.pack(pady=(0, 10))
        return lbl
    

    def on_tree_motion(self, event):
        row = self.table.identify_row(event.y)
        if row:
            self.table.configure(cursor="hand2")
        else:
            self.table.configure(cursor="")    

    def load_recipes_from_db(self):
        self.master_recipe_list = Recipe.get_all_recipes()
        self.perform_search()

    def perform_search(self, event=None):
        q = self.search_ent.get().strip()
        q_normalized = greek_sort_key(q) if q else ""
        
        for i in self.table.get_children():
            self.table.delete(i)
        
        results = []
        for index, r in enumerate(self.master_recipe_list):
            aa = str(index + 1)
            
            name_normalized = greek_sort_key(r[1])
            cat_normalized = greek_sort_key(r[2]) if r[2] else ""
            diff_normalized = greek_sort_key(r[3]) if r[3] else ""
            time_str = str(r[4]) if r[4] else ""
            
            match_text = (not q_normalized) or (
                q_normalized in aa or 
                q_normalized in name_normalized or 
                q_normalized in cat_normalized or 
                q_normalized in diff_normalized or 
                q_normalized in time_str
            )
            
            match_cat = (self.current_filter_category == "Όλες οι Κατηγορίες") or (r[2] == self.current_filter_category)
            match_diff = (self.current_filter_difficulty == "Όλες") or (r[3] == self.current_filter_difficulty)
            
            t = r[4] or 0
            if self.current_filter_time == "Έως 15 λεπτά":
                match_time = t <= 15
            elif self.current_filter_time == "Έως 30 λεπτά":
                match_time = t <= 30
            elif self.current_filter_time == "Έως 60 λεπτά":
                match_time = t <= 60
            elif self.current_filter_time == "Πάνω από 60 λεπτά":
                match_time = t > 60
            else:
                match_time = True
            
            match_aa = (not self.current_filter_aa) or (self.current_filter_aa == aa)
            match_name_filter = (not self.current_filter_name) or (self.current_filter_name.lower() in r[1].lower())
            
            if match_text and match_cat and match_diff and match_time and match_aa and match_name_filter:
                results.append((aa, r))
        
        cats_for_stats = []
        for i, (aa, r) in enumerate(results):
            tag = (str(r[0]), 'even' if i % 2 == 0 else 'odd', r[3])
            self.table.insert('', 'end', values=(aa, r[1], r[2] or "", r[3], f"{r[4]} λεπτά"), tags=tag)
            if r[2]:
                cats_for_stats.append(r[2])
        
        self.card_total.configure(text=str(len(results)))
        
        if cats_for_stats:
            freq = {}
            for cat in cats_for_stats:
                freq[cat] = freq.get(cat, 0) + 1
            max_count = max(freq.values())
            most_popular = [cat for cat, count in freq.items() if count == max_count]
            self.card_pop.configure(text=most_popular[0] if len(most_popular) == 1 else "Δεν υπάρχει")
        else:
            self.card_pop.configure(text="-")

    def open_filters_dialog(self):
        d = ctk.CTkToplevel(self.root)
        d.title("Προηγμένα Φίλτρα Αναζήτησης")
        center_and_size_window(d, 450, 650)
        set_window_icon(d)
        d.grab_set() 
        
        scroll = ctk.CTkScrollableFrame(d, fg_color="transparent")
        scroll.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ctk.CTkLabel(scroll, text="Α/Α Συνταγής:", font=("Segoe UI", 14, "bold")).pack(pady=(10,5))
        aa_entry = ctk.CTkEntry(scroll, font=("Segoe UI", 14), width=250, placeholder_text="Αύξων Αριθμός Συνταγών...", 
                                fg_color="#1f538d", border_color="#1f538d", text_color="white", placeholder_text_color="#a0a0a0")
        aa_entry.pack(pady=5)
        aa_entry.insert(0, self.current_filter_aa)

        ctk.CTkLabel(scroll, text="Όνομα Συνταγής:", font=("Segoe UI", 14, "bold")).pack(pady=(15,5))
        name_entry = ctk.CTkEntry(scroll, font=("Segoe UI", 14), width=250, placeholder_text="Όλες οι Συνταγές...", 
                                  fg_color="#1f538d", border_color="#1f538d", text_color="white", placeholder_text_color="#a0a0a0")
        name_entry.pack(pady=5)
        name_entry.insert(0, self.current_filter_name)

        ctk.CTkLabel(scroll, text="Κατηγορία Συνταγής:", font=("Segoe UI", 14, "bold")).pack(pady=(15,5))
        
        cat_combo_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        cat_combo_frame.pack(pady=5)
        
        cat_entry = ctk.CTkEntry(cat_combo_frame, font=("Segoe UI", 14), width=210, fg_color="#1f538d", border_color="#1f538d", text_color="white")
        cat_entry.pack(side=tk.LEFT, padx=(0, 5))
        cat_entry.insert(0, self.current_filter_category)
        cat_entry.configure(state="readonly")
        
        def open_filter_cat_dialog():
            cats = ["Όλες οι Κατηγορίες"] + sorted(Category.get_all(), key=greek_sort_key)
            SelectableListDialog(
                parent=d,
                title="Επιλογή Κατηγορίας",
                items=cats,
                on_select_callback=lambda c: set_readonly_entry(cat_entry, c)
            ).show()
            
        ctk.CTkButton(cat_combo_frame, text="▼", width=35, height=35,
                     command=open_filter_cat_dialog, cursor="hand2",
                     fg_color="#1f538d", hover_color="#2a72c1",
                     font=("Segoe UI", 14)).pack(side=tk.LEFT)

        ctk.CTkLabel(scroll, text="Επίπεδο Δυσκολίας:", font=("Segoe UI", 14, "bold")).pack(pady=(15,5))
        diff_combo = ctk.CTkOptionMenu(scroll, values=["Όλες", "Εύκολη", "Μέτρια", "Δύσκολη"], font=("Segoe UI", 14), width=250)
        diff_combo.pack(pady=5)
        diff_combo.set(self.current_filter_difficulty)

        ctk.CTkLabel(scroll, text="Χρόνος Προετοιμασίας:", font=("Segoe UI", 14, "bold")).pack(pady=(15,5))
        time_combo = ctk.CTkOptionMenu(scroll, values=["Όλοι οι Χρόνοι", "Έως 15 λεπτά", "Έως 30 λεπτά", "Έως 60 λεπτά", "Πάνω από 60 λεπτά"], font=("Segoe UI", 14), width=250)
        time_combo.pack(pady=5)
        time_combo.set(self.current_filter_time)

        def apply_filters():
            self.current_filter_aa = aa_entry.get().strip()
            self.current_filter_name = name_entry.get().strip()
            self.current_filter_category = cat_entry.get().strip()
            self.current_filter_difficulty = diff_combo.get()
            self.current_filter_time = time_combo.get()
            
            if (self.current_filter_category != "Όλες οι Κατηγορίες" or 
                self.current_filter_difficulty != "Όλες" or 
                self.current_filter_time != "Όλοι οι Χρόνοι" or
                self.current_filter_aa != "" or
                self.current_filter_name != ""):
                self.filter_btn.configure(text="⚙️ Φίλτρα (Ενεργά)", fg_color="#e67e22", hover_color="#d35400")
            else:
                self.filter_btn.configure(text="⚙️ Προηγμένα Φίλτρα", fg_color=["#3a7ebf", "#1f538d"], hover_color=["#325882", "#14375e"])
            
            self.perform_search()
            d.destroy()

        def clear_filters():
            aa_entry.delete(0, tk.END)
            name_entry.delete(0, tk.END)
            set_readonly_entry(cat_entry, "Όλες οι Κατηγορίες")
            diff_combo.set("Όλες")
            time_combo.set("Όλοι οι Χρόνοι")
        
        btn_f = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_f.pack(pady=35)
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
            if getattr(self, 'auto_theme_job', None):
                self.root.after_cancel(self.auto_theme_job)
            self.auto_theme_job = self.root.after(60000, self.apply_theme)
        else:
            if getattr(self, 'auto_theme_job', None):
                self.root.after_cancel(self.auto_theme_job)
                self.auto_theme_job = None

    def delete_recipe(self):
        sel = self.table.selection()
        if sel:
            rid = int(self.table.item(sel[0], 'tags')[0]) 
            name = self.table.item(sel[0])['values'][1] 
            if messagebox.askyesno("Διαγραφή", f"Θέλετε να διαγράψετε τη συνταγή '{name}';"):
                Recipe.delete_by_id(rid)
                self.load_recipes_from_db()

    def recipe_launch(self):
        sel = self.table.selection()
        if not sel: 
            return messagebox.showwarning("Προσοχή", "Επιλέξτε μια συνταγή για εκτέλεση.")
        try:
            rid = int(self.table.item(sel[0], 'tags')[0]) 
            recipe = Recipe.get_recipe_by_id(rid)
            if not recipe or not recipe.steps: 
                return messagebox.showerror("Σφάλμα", "Η συνταγή δεν έχει βήματα.")
            RecipeExecutePage(rid, self.root)
        except Exception as e: 
            messagebox.showerror("Σφάλμα", f"Αποτυχία: {e}")

    def open_update(self, view_only=False):
        sel = self.table.selection()
        if not sel: 
            messagebox.showwarning("Προσοχή", "Επιλέξτε μια συνταγή.")
            return
        
        rid = int(self.table.item(sel[0], 'tags')[0])
        
        if view_only:
            RecipeViewPage(rid, self.root)
        else:
            RecipeFormPage(self, rid)

    def open_export(self):
        d = ctk.CTkToplevel()
        d.title("Εξαγωγή Δεδομένων")
        center_and_size_window(d, 450, 300)
        set_window_icon(d)
        
        def do_excel():
            p = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Excel CSV", "*.csv")])
            if p:
                try:
                    with open(p, 'w', newline='', encoding='utf-8-sig') as f:
                        w = csv.writer(f, delimiter=';')
                        w.writerow(['A/A', 'ID', 'Όνομα', 'Κατηγορία', 'Δυσκολία', 'Χρόνος'])
                        for idx, r in enumerate(self.master_recipe_list): 
                            w.writerow([idx + 1, r[0], r[1], r[2], r[3], r[4]])
                    messagebox.showinfo("OK", "Η εξαγωγή σε Excel ολοκληρώθηκε!")
                    d.destroy()
                except Exception as e:
                    messagebox.showerror("Σφάλμα", f"Αποτυχία: {e}")
                
        def do_pdf():
            sel = self.table.selection()
            if not sel: 
                return messagebox.showerror("Σφάλμα", "Επιλέξτε μια συνταγή για εξαγωγή σε PDF.")
            
            rid = int(self.table.item(sel[0], 'tags')[0])
            r = Recipe.get_recipe_by_id(rid) 
            
            p = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile=f"{r.name}.pdf")
            if p:
                try:
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    
                    font_path = resource_path(os.path.join("fonts", "DejaVuSans.ttf"))
                    
                    if not os.path.exists(font_path):
                        font_path = resource_path(os.path.join("fonts", "OpenSans-Regular.ttf"))
                    
                    if os.path.exists(font_path):
                        pdf.add_font('GreekFont', '', font_path)
                        pdf.add_font('GreekFont', 'B', font_path)
                        pdf.add_font('GreekFont', 'I', font_path)
                    else:
                        messagebox.showerror("Σφάλμα", "Δεν βρέθηκε γραμματοσειρά.")
                        return

                    image_path = r.get_image_path() if hasattr(r, 'get_image_path') else None
                    if image_path and os.path.exists(image_path):
                        try:
                            with Image.open(image_path) as img:
                                img_width, img_height = img.size
                            
                            max_width_mm = 170
                            image_width_mm = min(max_width_mm, 60)
                            
                            aspect_ratio = img_height / img_width
                            image_height_mm = image_width_mm * aspect_ratio
                            
                            image_x_mm = (210 - image_width_mm) / 2
                            
                            pdf.image(image_path, x=image_x_mm, y=15, w=image_width_mm)
                            
                            space_needed = image_height_mm + 10
                            pdf.ln(space_needed)
                            
                        except Exception as img_error:
                            print(f"Could not add image: {img_error}")
                            pdf.ln(10)
                    else:
                        pdf.ln(10)
                    
                    pdf.set_font('GreekFont', 'B', 20)
                    pdf.cell(0, 15, r.name, align='C')
                    pdf.ln(15)
                    pdf.ln(5)
                    
                    pdf.set_font('GreekFont', '', 11)
                    info_text = f"Κατηγορία: {r.category or '-'}  |  Δυσκολία: {r.difficulty or '-'}  |  Χρόνος: {r.total_time_minutes or 0} λεπτά"
                    pdf.cell(0, 8, info_text, align='C')
                    pdf.ln(8)
                    pdf.ln(10)

                    pdf.set_font('GreekFont', 'B', 14)
                    pdf.cell(0, 10, "Υλικά:")
                    pdf.ln(10)
                    pdf.set_font('GreekFont', '', 11)
                    
                    for ing in sorted(r.ingredients, key=lambda x: greek_sort_key(x.name)):
                        ing_text = f"• {format_quantity(ing.quantity)} {ing.unit or ''} {ing.name}"
                        if ing.notes:
                            ing_text += f" ({ing.notes})"
                        pdf.set_x(10)
                        pdf.multi_cell(0, 6, ing_text)
                    
                    pdf.ln(5)
                    
                    pdf.set_font('GreekFont', 'B', 14)
                    pdf.cell(0, 10, "Βήματα Εκτέλεσης:")
                    pdf.ln(10)
                    
                    for i, st in enumerate(r.steps, 1):
                        pdf.set_font('GreekFont', 'B', 12)
                        step_title = f"{i}. {st.step_name}"
                        if st.duration_in_minutes > 0:
                            step_title += f" ({st.duration_in_minutes} λεπτά)"
                        pdf.cell(0, 8, step_title)
                        pdf.ln(8)
                        
                        if st.step_text:
                            pdf.set_font('GreekFont', '', 11)
                            pdf.set_x(15)
                            pdf.multi_cell(0, 6, st.step_text)
                        
                        allocs = getattr(st, 'allocations', getattr(st, 'step_ingredients', []))
                        valid_allocs = [a for a in allocs if get_alloc_val(a, 'ingredient_name', '')]
                        if valid_allocs:
                            pdf.set_font('GreekFont', 'B', 11)
                            pdf.set_x(15)
                            pdf.cell(0, 6, "Υλικά Βήματος:")
                            pdf.ln(6)
                            
                            pdf.set_font('GreekFont', 'B', 10)
                            for a in allocs:
                                name = get_alloc_val(a, 'ingredient_name', '')
                                qty = get_alloc_val(a, 'quantity', '')
                                unit = get_alloc_val(a, 'unit', '')
                                notes = get_alloc_val(a, 'notes', '')
                                prep_mark = " (Προετοιμασία)" if notes == "Στάδιο Προετοιμασίας" else ""
                                pdf.set_x(20)
                                pdf.multi_cell(0, 5, f"• {format_quantity(qty)} {unit} {name}{prep_mark}")
                        
                        pdf.ln(3)
                    
                    pdf.output(p)
                    messagebox.showinfo("Επιτυχία", "Το PDF δημιουργήθηκε!")
                    d.destroy()
                    try: 
                        os.startfile(p)
                    except: 
                        pass
                        
                except Exception as e: 
                    messagebox.showerror("Σφάλμα", f"Αποτυχία δημιουργίας PDF: {str(e)}")
                    
        ctk.CTkButton(d, text="📊 Εξαγωγή ΟΛΩΝ (Excel)", height=50, font=("Segoe UI", 15, "bold"), command=do_excel, cursor="hand2").pack(pady=30, padx=40, fill=tk.X)
        ctk.CTkButton(d, text="🖨️ Εξαγωγή ΕΠΙΛΕΓΜΕΝΗΣ (PDF)", height=50, font=("Segoe UI", 15, "bold"), fg_color="#e67e22", command=do_pdf, cursor="hand2").pack(pady=10, padx=40, fill=tk.X)

# =============================================================================
# --- ΕΚΚΙΝΗΣΗ ΕΦΑΡΜΟΓΗΣ ---
# =============================================================================

if __name__ == "__main__":
    try:
        myappid = 'eap.project11.chefmaster.1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception: 
        pass
        
    root = ctk.CTk()
    app = RecipeApp(root)
    root.mainloop()