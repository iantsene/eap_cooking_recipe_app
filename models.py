from db import DatabaseConn
import os

class ListManager:
    TABLE_NAME = None
    ITEM_NAME = None
    WINDOW_TITLE = None
    
    @classmethod
    def get_all(cls):
        with DatabaseConn("recipe_database.db") as db:
            db.execute(f"SELECT name FROM {cls.TABLE_NAME} ORDER BY name COLLATE NOCASE")
            return [row[0] for row in db.fetchall()]
    
    @classmethod
    def add(cls, name):
        if not name or not name.strip():
            return False
        try:
            with DatabaseConn("recipe_database.db") as db:
                db.execute(f"INSERT INTO {cls.TABLE_NAME} (name) VALUES (?)", (name.strip(),))
                return True
        except Exception:
            return False
    
    @classmethod
    def manage(cls, parent_window=None, callback_on_change=None):
        import customtkinter as ctk
        import tkinter as tk
        from tkinter import messagebox
        from utils import center_and_size_window, set_window_icon, greek_sort_key
        
        d = ctk.CTkToplevel(parent_window) if parent_window else ctk.CTkToplevel()
        d.title(cls.WINDOW_TITLE)
        center_and_size_window(d, 500, 450)
        set_window_icon(d)
        d.grab_set()
        
        items = cls.get_all()
        items = sorted(items, key=greek_sort_key)
        
        main_frame = ctk.CTkFrame(d)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(main_frame, text=f"Λίστα {cls.ITEM_NAME}", font=("Segoe UI", 16, "bold")).pack(pady=(0, 10))
        
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        listbox_frame = tk.Frame(list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        current_theme = ctk.get_appearance_mode()
        bg_color = "#2b2b2b" if current_theme == "Dark" else "#ffffff"
        fg_color = "white" if current_theme == "Dark" else "black"
        
        listbox = tk.Listbox(listbox_frame, font=("Segoe UI", 13), bg=bg_color, fg=fg_color,
                            selectbackground='#1f538d', selectforeground='white',
                            yscrollcommand=scrollbar.set, bd=1, relief="solid", highlightthickness=0)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        for item in items:
            listbox.insert(tk.END, item)
        
        add_frame = ctk.CTkFrame(main_frame)
        add_frame.pack(fill=tk.X, pady=15)
        
        new_entry = ctk.CTkEntry(add_frame, placeholder_text=f"Νέο/α {cls.ITEM_NAME}...", font=("Segoe UI", 14), width=250)
        new_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        def add_item():
            new_name = new_entry.get().strip()
            if not new_name:
                messagebox.showwarning("Προσοχή", f"Παρακαλώ εισάγετε {cls.ITEM_NAME}.")
                return
            
            if cls.add(new_name):
                current_items = list(listbox.get(0, tk.END))
                current_items.append(new_name)
                current_items.sort(key=greek_sort_key)
                
                listbox.delete(0, tk.END)
                for item in current_items:
                    listbox.insert(tk.END, item)
                
                new_entry.delete(0, tk.END)
                if callback_on_change:
                    callback_on_change()
                
                msg = f"Το {cls.ITEM_NAME} '{new_name}' προστέθηκε!" if cls.ITEM_NAME == "Υλικό" else f"Η {cls.ITEM_NAME} '{new_name}' προστέθηκε!"
                messagebox.showinfo("Επιτυχία", msg)
            else:
                messagebox.showerror("Σφάλμα", f"Το/Η {cls.ITEM_NAME} υπάρχει ήδη")
        
        ctk.CTkButton(add_frame, text="➕ Προσθήκη", command=add_item, 
                     cursor="hand2", width=100, fg_color="#28a745", hover_color="#218838").pack(side=tk.RIGHT)
        
        delete_frame = ctk.CTkFrame(main_frame)
        delete_frame.pack(fill=tk.X, pady=5)
        
        def delete_item():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Προσοχή", f"Επιλέξτε {cls.ITEM_NAME} για διαγραφή.")
                return
            
            item_name = listbox.get(selection[0])
            
            if not messagebox.askyesno("Επιβεβαίωση", f"Θέλετε να διαγράψετε το/η {cls.ITEM_NAME} '{item_name}';"):
                return
            
            if cls.delete(item_name):
                listbox.delete(selection[0])
                if callback_on_change:
                    callback_on_change()
                messagebox.showinfo("Επιτυχία", f"Το/Η {cls.ITEM_NAME} '{item_name}' διαγράφηκε!")
            else:
                messagebox.showerror("Σφάλμα", f"Δεν μπορείτε να διαγράψετε {cls.ITEM_NAME} που χρησιμοποιείται σε συνταγές")
        
        ctk.CTkButton(delete_frame, text="❌ Διαγραφή Επιλεγμένου/ης", command=delete_item, 
                     fg_color="#8b0000", hover_color="#ff1a1a", cursor="hand2", width=200).pack()
        
        new_entry.bind('<Return>', lambda e: add_item())
        
        def filter_items(event=None):
            typed = new_entry.get().strip().lower()
            listbox.delete(0, tk.END)
            for i in sorted(cls.get_all(), key=greek_sort_key):
                if not typed or typed in i.lower():
                    listbox.insert(tk.END, i)
        
        new_entry.bind('<KeyRelease>', filter_items)
        
        ctk.CTkButton(main_frame, text="Κλείσιμο", command=d.destroy, 
                     fg_color="#1f538d", hover_color="#2a72c1", cursor="hand2", width=150).pack(pady=15)
        
        return d

class Category(ListManager):
    TABLE_NAME = "categories_list"
    ITEM_NAME = "Κατηγοριών"
    WINDOW_TITLE = "Διαχείριση Κατηγοριών"
    
    @staticmethod
    def get_or_create(name):
        if not name or not name.strip():
            raise ValueError("Category name cannot be empty")
        with DatabaseConn("recipe_database.db") as db:
            db.execute("SELECT id FROM categories_list WHERE name = ?", (name,))
            res = db.fetchone()
            if res:
                return res[0]
            db.execute("INSERT INTO categories_list (name) VALUES (?)", (name,))
            return db.cursor.lastrowid
    
    @classmethod
    def delete(cls, name):
        with DatabaseConn("recipe_database.db") as db:
            db.execute("SELECT id FROM categories_list WHERE name = ?", (name,))
            cat_row = db.fetchone()
            if not cat_row:
                return False
            
            category_id = cat_row[0]
            db.execute("SELECT COUNT(*) FROM recipes WHERE category_id = ?", (category_id,))
            count = db.fetchone()[0]
            
            if count > 0:
                return False
            
            db.execute("DELETE FROM categories_list WHERE id = ?", (category_id,))
            return True

class Unit(ListManager):
    TABLE_NAME = "unit_list"
    ITEM_NAME = "Μονάδων"
    WINDOW_TITLE = "Διαχείριση Μονάδων"
    
    @classmethod
    def delete(cls, name):
        with DatabaseConn("recipe_database.db") as db:
            db.execute("SELECT COUNT(*) FROM ingredients WHERE unit = ?", (name,))
            count = db.fetchone()[0]
            
            if count > 0:
                return False
            
            db.execute("DELETE FROM unit_list WHERE name = ?", (name,))
            return True

class Ingredient(ListManager):
    TABLE_NAME = "ingredient_list"
    ITEM_NAME = "Υλικών"
    WINDOW_TITLE = "Διαχείριση Υλικών"
    
    def __init__(self, id=None, recipe_id=None, name="", quantity=0, unit="", notes=""):
        self.id = id
        self.recipe_id = recipe_id
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.notes = notes
        self.temp_id = None
    
    @classmethod
    def delete(cls, name):
        with DatabaseConn("recipe_database.db") as db:
            db.execute("SELECT COUNT(*) FROM ingredients WHERE name = ?", (name,))
            count = db.fetchone()[0]
            
            if count > 0:
                return False
            
            db.execute(f"DELETE FROM {cls.TABLE_NAME} WHERE name = ?", (name,))
            return True

class Step:
    def __init__(self, id=None, recipe_id=None, step_name="", sequence_order=0, step_text="", duration_in_minutes=0):
        self.id = id
        self.recipe_id = recipe_id
        self.step_name = step_name
        self.sequence_order = sequence_order
        self.step_text = step_text
        self.duration_in_minutes = duration_in_minutes
        self.allocations = []

class ImageModel:
    def __init__(self, id=None, path=None):
        self.id = id
        self.path = path

    @staticmethod
    def save_image(path):
        if not path:
            return None
        with DatabaseConn("recipe_database.db") as db:
            db.execute("SELECT id FROM images WHERE path = ?", (path,))
            existing = db.fetchone()
            if existing:
                return existing[0]
            
            db.execute("INSERT INTO images (path) VALUES (?)", (path,))
            return db.cursor.lastrowid
    
    @staticmethod
    def get_path_by_id(image_id):
        if not image_id:
            return None
        with DatabaseConn("recipe_database.db") as db:
            db.execute("SELECT path FROM images WHERE id = ?", (image_id,))
            result = db.fetchone()
            return result[0] if result else None
    
    @staticmethod
    def delete_image(image_id):
        if not image_id:
            return False
        
        with DatabaseConn("recipe_database.db") as db:
            db.execute("SELECT path FROM images WHERE id = ?", (image_id,))
            result = db.fetchone()
            path = result[0] if result else None
            
            db.execute("DELETE FROM images WHERE id = ?", (image_id,))
            
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    return True
                except Exception as e:
                    print(f"Could not delete image file: {e}")
            return True


class Recipe:
    def __init__(self, id=None, name="", category="", difficulty="", total_time_minutes=0):
        self.id = id
        self.name = name
        self.category = category
        self.category_id = None
        self.difficulty = difficulty
        self.total_time_minutes = total_time_minutes
        self.image_id = None
        self.ingredients = []
        self.steps = []
        self._dirty = False
        self._ingredients_dirty = False
        self._steps_dirty = False
    
    def get_image_path(self):
        if self.image_id:
            return ImageModel.get_path_by_id(self.image_id)
        return None
    
    def mark_dirty(self):
        self._dirty = True
    
    def mark_ingredients_dirty(self):
        self._ingredients_dirty = True
        self._steps_dirty = True
        self._dirty = True
    
    def mark_steps_dirty(self):
        self._steps_dirty = True
        self._dirty = True

    def save(self):
        with DatabaseConn("recipe_database.db") as db:
            is_new = self.id is None
            
            if is_new:
                db.execute("""INSERT INTO recipes (name, category_id, difficulty, total_time_minutes, image_id) 
                            VALUES (?, ?, ?, ?, ?)""", 
                        (self.name, self.category_id, self.difficulty, self.total_time_minutes, self.image_id))
                self.id = db.cursor.lastrowid
                self._ingredients_dirty = True
                self._steps_dirty = True
            else:
                db.execute("SELECT name, category_id, difficulty, total_time_minutes, image_id FROM recipes WHERE id = ?", (self.id,))
                old = db.fetchone()
                
                if (old[0] != self.name or old[1] != self.category_id or old[2] != self.difficulty or 
                    old[3] != self.total_time_minutes or old[4] != self.image_id):
                    db.execute("""UPDATE recipes 
                                SET name=?, category_id=?, difficulty=?, total_time_minutes=?, image_id=? 
                                WHERE id=?""", 
                            (self.name, self.category_id, self.difficulty, self.total_time_minutes, self.image_id, self.id))
            
            if self._ingredients_dirty or is_new:
                if not is_new:
                    db.execute("DELETE FROM ingredients WHERE recipe_id=?", (self.id,))
                
                for ing in self.ingredients:
                    db.execute("INSERT INTO ingredients (recipe_id, name, quantity, unit, notes) VALUES (?,?,?,?,?)", 
                            (self.id, ing.name, ing.quantity, ing.unit, getattr(ing, 'notes', '')))
                    ing.id = db.cursor.lastrowid
                    
                    try:
                        db.execute("INSERT OR IGNORE INTO ingredient_list (name) VALUES (?)", (ing.name,))
                    except:
                        pass
                
                self._ingredients_dirty = False
            
            if self._steps_dirty or is_new:
                if not is_new:
                    db.execute("DELETE FROM steps WHERE recipe_id=?", (self.id,))
                
                for idx, st in enumerate(self.steps, 1):
                    st.sequence_order = idx
                    db.execute("""INSERT INTO steps (recipe_id, step_name, sequence_order, step_text, duration_in_minutes) 
                                VALUES (?,?,?,?,?)""",
                            (self.id, st.step_name, st.sequence_order, st.step_text, st.duration_in_minutes))
                    st.id = db.cursor.lastrowid
                    
                    for a in getattr(st, 'allocations', []):
                        ing_id = None
                        ingredient_name = a.get('ingredient_name', '')
                        
                        for ing in self.ingredients:
                            if ing.name == ingredient_name:
                                ing_id = ing.id
                                break
                        
                        if not ing_id:
                            for ing in self.ingredients:
                                if hasattr(ing, 'temp_id') and ing.temp_id == a.get('temp_id'):
                                    ing_id = ing.id
                                    break
                        
                        if ing_id:
                            db.execute("""INSERT INTO step_ingredients (ingredient_id, step_id, ingredient_name, quantity, unit, notes) 
                                    VALUES (?,?,?,?,?,?)""",
                                    (ing_id, st.id, a.get('ingredient_name'), a.get('quantity'), a.get('unit'), a.get('notes', '')))
                
                self._steps_dirty = False
            
            self._dirty = False

    @staticmethod
    def get_all_recipes():
        with DatabaseConn("recipe_database.db") as db:
            db.execute("""SELECT r.id, r.name, c.name, r.difficulty, r.total_time_minutes, i.path 
                          FROM recipes r 
                          LEFT JOIN categories_list c ON r.category_id = c.id
                          LEFT JOIN images i ON r.image_id = i.id
                          ORDER BY r.name COLLATE NOCASE""")
            return db.fetchall()

    @staticmethod
    def get_recipe_by_id(recipe_id):
        with DatabaseConn("recipe_database.db") as db:
            db.execute("""SELECT r.id, r.name, c.name, r.difficulty, r.total_time_minutes, i.path, r.image_id
                        FROM recipes r 
                        LEFT JOIN categories_list c ON r.category_id = c.id
                        LEFT JOIN images i ON r.image_id = i.id 
                        WHERE r.id = ?""", (recipe_id,))
            row = db.fetchone()
            if not row: 
                return None
            
            category_name = row[2] if row[2] is not None else ""
            
            recipe = Recipe(id=row[0], name=row[1], category=category_name, 
                          difficulty=row[3] if row[3] else "Μέτρια", 
                          total_time_minutes=row[4] if row[4] else 0)
            recipe.image_id = row[6] if len(row) > 6 else None
            
            db.execute("SELECT id, name, quantity, unit, notes FROM ingredients WHERE recipe_id = ?", (recipe_id,))
            recipe.ingredients = [Ingredient(r[0], recipe_id, r[1], r[2] if r[2] else 0, r[3] if r[3] else "", r[4] if r[4] else "") for r in db.fetchall()]
            
            db.execute("""
                SELECT s.id, s.step_name, s.sequence_order, s.step_text, s.duration_in_minutes,
                    GROUP_CONCAT(
                        COALESCE(si.ingredient_id, '') || '|' || 
                        COALESCE(i.name, '') || '|' || 
                        COALESCE(si.quantity, '') || '|' || 
                        COALESCE(si.unit, '') || '|' || 
                        COALESCE(si.notes, '')
                    ) as allocations
                FROM steps s
                LEFT JOIN step_ingredients si ON si.step_id = s.id
                LEFT JOIN ingredients i ON si.ingredient_id = i.id
                WHERE s.recipe_id = ?
                GROUP BY s.id
                ORDER BY s.sequence_order
            """, (recipe_id,))

            for s_row in db.fetchall():
                st = Step(s_row[0], recipe_id, s_row[1] if s_row[1] else "", s_row[2], 
                         s_row[3] if s_row[3] else "", s_row[4] if s_row[4] else 0)
                st.allocations = []
                
                if s_row[5]:
                    for alloc_str in s_row[5].split(','):
                        parts = alloc_str.split('|')
                        if len(parts) >= 5:
                            st.allocations.append({
                                'ingredient_id': int(parts[0]) if parts[0] and parts[0] != '' else None,
                                'ingredient_name': parts[1] if parts[1] != '' else '',
                                'quantity': float(parts[2]) if parts[2] and parts[2] != '' else 0,
                                'unit': parts[3] if parts[3] != '' else '',
                                'notes': parts[4] if parts[4] != '' and parts[4] != 'None' else ''
                            })
                
                st.step_ingredients = st.allocations
                recipe.steps.append(st)
            
            return recipe

    @classmethod
    def delete_by_id(cls, recipe_id):
        image_id = None
        with DatabaseConn("recipe_database.db") as db:
            db.execute("SELECT image_id FROM recipes WHERE id = ?", (recipe_id,))
            result = db.fetchone()
            image_id = result[0] if result else None
            
            db.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        
        if image_id:
            with DatabaseConn("recipe_database.db") as db:
                db.execute("SELECT COUNT(*) FROM recipes WHERE image_id = ?", (image_id,))
                count = db.fetchone()[0]
                if count == 0:
                    ImageModel.delete_image(image_id)
        return True

    @staticmethod
    def search_recipes(search_term=""):
        with DatabaseConn("recipe_database.db") as db:
            if search_term:
                term = f"%{search_term}%"
                db.execute("""
                    SELECT r.id, r.name, c.name, r.difficulty, r.total_time_minutes, i.path
                    FROM recipes r 
                    LEFT JOIN categories_list c ON r.category_id = c.id
                    LEFT JOIN images i ON r.image_id = i.id
                    WHERE r.name LIKE ? OR c.name LIKE ? OR r.difficulty LIKE ?
                    ORDER BY r.name COLLATE NOCASE
                """, (term, term, term))
            else:
                db.execute("""
                    SELECT r.id, r.name, c.name, r.difficulty, r.total_time_minutes, i.path
                    FROM recipes r 
                    LEFT JOIN categories_list c ON r.category_id = c.id
                    LEFT JOIN images i ON r.image_id = i.id
                    ORDER BY r.name COLLATE NOCASE
                """)
            return db.fetchall()
