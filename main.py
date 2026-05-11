# =============================================================================
# ΠΛΗΡΗΣ ΚΩΔΙΚΑΣ MAIN.PY - CHEFMASTER PRO (FINAL ULTIMATE VERSION)
# =============================================================================

from db import DatabaseConn
from models import Recipe, Ingredient, Step, Category, ImageModel
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
import sys




# =============================================================================
# --- RESOURCE PATH (for PyInstaller) ---
# =============================================================================

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# =============================================================================
# --- ΒΟΗΘΗΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ ---
# =============================================================================




def greek_sort_key(text):
    """Έξυπνη ταξινόμηση Ελληνικών που αγνοεί τους τόνους και τα κεφαλαία/μικρά"""
    if not isinstance(text, str): return ""
    replacements = {'ά':'α', 'έ':'ε', 'ή':'η', 'ί':'ι', 'ό':'ο', 'ύ':'υ', 'ώ':'ω', 'ϊ':'ι', 'ϋ':'υ', 'ΐ':'ι', 'ΰ':'υ'}
    text = text.lower().strip()
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def fraction_to_float(fraction_str):
    """Convert fraction string like '1/2' to float 0.5"""
    if not fraction_str:
        return None
    
    fraction_str = fraction_str.strip().replace(',', '.')
    
    # Check if it's a fraction (contains '/')
    if '/' in fraction_str:
        try:
            parts = fraction_str.split('/')
            if len(parts) == 2:
                numerator = float(parts[0].strip())
                denominator = float(parts[1].strip())
                if denominator != 0:
                    return numerator / denominator
        except ValueError:
            pass
    
    # Check if it's a mixed number like '1 1/2'
    if ' ' in fraction_str:
        parts = fraction_str.split()
        if len(parts) == 2 and '/' in parts[1]:
            try:
                whole = float(parts[0])
                frac_parts = parts[1].split('/')
                if len(frac_parts) == 2:
                    numerator = float(frac_parts[0])
                    denominator = float(frac_parts[1])
                    if denominator != 0:
                        return whole + (numerator / denominator)
            except ValueError:
                pass
    
    # Try to convert to float directly
    try:
        return float(fraction_str)
    except ValueError:
        return None

def float_to_fraction(value):
    """Convert float like 0.5 to fraction string '1/2' for common fractions"""
    if not value:
        return str(value)
    
    # Common fractions mapping
    common_fractions = {
        0.5: "1/2",
        0.25: "1/4",
        0.75: "3/4",
        0.333333333333: "1/3",
        0.666666666666: "2/3",
        0.2: "1/5",
        0.4: "2/5",
        0.6: "3/5",
        0.8: "4/5",
        0.125: "1/8",
        0.375: "3/8",
        0.625: "5/8",
        0.875: "7/8"
    }
    
    # Check for common fractions with tolerance
    for fraction_value, fraction_str in common_fractions.items():
        if abs(value - fraction_value) < 0.001:
            return fraction_str
    
    # Check for whole numbers
    if value.is_integer():
        return str(int(value))
    
    # Return as decimal string
    return str(value).rstrip('0').rstrip('.') if '.' in str(value) else str(value)

def create_scrollable_selector(parent, title, items_list, on_select, width=300, height=200):
    """Δημιουργεί ένα κουμπί που ανοίγει scrollable παράθυρο επιλογής"""
    
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    
    # Entry για εμφάνιση της επιλογής
    entry = ctk.CTkEntry(frame, width=width-40, font=("Segoe UI", 14))
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # Κουμπί για άνοιγμα παραθύρου
    def open_selector():
        dialog = ctk.CTkToplevel(frame)
        dialog.title(title)
        dialog.geometry(f"{width}x{height}")
        dialog.transient(frame.winfo_toplevel())
        dialog.grab_set()
        center_and_size_window(dialog, width, height)
        
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(dialog, width=width-40, height=height-80)
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        def select_item(item):
            entry.delete(0, tk.END)
            entry.insert(0, item)
            if on_select:
                on_select(item)
            dialog.destroy()
        
        # Προσθήκη όλων των items
        for item in sorted(items_list, key=greek_sort_key):
            btn = ctk.CTkButton(scroll_frame, text=item, 
                               command=lambda i=item: select_item(i),
                               font=("Segoe UI", 13), height=40,
                               fg_color="transparent", hover_color="#1f538d",
                               anchor="w", cursor="hand2")
            btn.pack(fill=tk.X, pady=2, padx=5)
        
        # Κουμπί κλεισίματος
        ctk.CTkButton(dialog, text="Κλείσιμο", command=dialog.destroy,
                     fg_color="#8b0000", hover_color="#ff1a1a").pack(pady=10)
    
    btn = ctk.CTkButton(frame, text="▼", width=35, height=35,
                       command=open_selector, cursor="hand2",
                       fg_color="#1f538d", hover_color="#2a72c1")
    btn.pack(side=tk.RIGHT)
    
    return frame, entry

def setup_treeview_scroll(treeview):
    """Setup a treeview to scroll independently without affecting parent"""
    def on_mousewheel(event):
        treeview.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"
    treeview.bind("<MouseWheel>", on_mousewheel)

def set_window_icon(window):
    """Set window icon safely - works both in development and packaged exe"""
    try:
        # Try to get the icon path using resource_path
        icon_path = resource_path("chef.ico")
        
        # Only set if the file exists
        if os.path.exists(icon_path):
            # Use after() to delay the icon setting until window is fully created
            window.after(100, lambda: window.iconbitmap(icon_path))
        else:
            # Icon file not found, just skip silently
            pass
    except Exception:
        # If anything fails, just skip - the app will still work
        pass

def enable_right_click_menu(widget):
    if hasattr(widget, '_textbox'): 
        target = widget._textbox
    elif hasattr(widget, '_entry'): 
        target = widget._entry
    else: 
        target = widget
        
    menu = tk.Menu(target, tearoff=False, font=("Segoe UI", 11), bg="#2a2d2e", fg="white", activebackground="#1f538d")
    
    def cut(event=None): 
        try: target.event_generate("<<Cut>>")
        except: pass
        return "break"
        
    def copy(event=None): 
        try: target.event_generate("<<Copy>>")
        except: pass
        return "break"
        
    def paste(event=None): 
        try: target.event_generate("<<Paste>>")
        except: pass
        return "break"
        
    def select_all(event=None): 
        try: 
            if hasattr(target, 'tag_add'):
                target.tag_add("sel", "1.0", "end")
            else:
                target.select_range(0, "end")
                target.icursor("end")
        except: pass
        return "break"
        
    menu.add_command(label="Αποκοπή    (Ctrl+X)", command=cut)
    menu.add_command(label="Αντιγραφή  (Ctrl+C)", command=copy)
    menu.add_command(label="Επικόλληση (Ctrl+V)", command=paste)
    menu.add_separator()
    menu.add_command(label="Επιλογή όλων (Ctrl+A)", command=select_all)
    
    def show_menu(event):
        target.focus_set()
        menu.tk_popup(event.x_root, event.y_root)
        
    target.bind("<Button-3>", show_menu)
    
    def handle_hardware_shortcuts(event):
        if event.state & 0x0004:  
            if event.keycode == 88: return cut()         
            elif event.keycode == 67: return copy()      
            elif event.keycode == 86: return paste()     
            elif event.keycode == 65: return select_all()

    target.bind("<Key>", handle_hardware_shortcuts)

def center_and_size_window(window, desired_w, desired_h):
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    final_w = min(desired_w, int(screen_w * 0.95))
    final_h = min(desired_h, int(screen_h * 0.90))
    window.geometry(f"{final_w}x{final_h}")
    window.lift()                  
    window.focus_force()           
    window.attributes("-topmost", True)  
    
    # Το ξεκαρφιτσώνει μετά από μισό δευτερόλεπτο (500ms) για να μην μπλοκάρει τον υπολογιστή σου
    window.after(500, lambda: window.attributes("-topmost", False))

def setup_autocomplete(combo_widget, full_list, max_height=150):
    """Έξυπνο autocomplete με scrollable dropdown - ΣΤΑΘΕΡΟ ΥΨΟΣ"""
    
    dropdown_window = None
    listbox = None
    scrollbar = None
    
    def close_dropdown():
        nonlocal dropdown_window, listbox, scrollbar
        if dropdown_window:
            dropdown_window.destroy()
            dropdown_window = None
            listbox = None
            scrollbar = None
    
    def select_item(event=None):
        if listbox and listbox.curselection():
            index = listbox.curselection()[0]
            item = listbox.get(index)
            combo_widget.set(item)
            close_dropdown()
            return "break"
    
    def show_dropdown(filtered_items):
        nonlocal dropdown_window, listbox, scrollbar
        
        close_dropdown()
        
        if not filtered_items:
            return
        
        # Δημιουργία παραθύρου dropdown - ΣΤΑΘΕΡΟ ΥΨΟΣ 150 pixels
        dropdown_window = tk.Toplevel(combo_widget)
        dropdown_window.overrideredirect(True)
        dropdown_window.configure(bg='#2b2b2b')
        
        # Τοποθέτηση κάτω από το combobox
        x = combo_widget.winfo_rootx()
        y = combo_widget.winfo_rooty() + combo_widget.winfo_height()
        width = combo_widget.winfo_width()
        dropdown_window.geometry(f"{width}x{max_height}+{x}+{y}")  # ΣΤΑΘΕΡΟ ΥΨΟΣ!
        
        # Frame για το περιεχόμενο
        frame = tk.Frame(dropdown_window, bg='#2b2b2b')
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox
        listbox = tk.Listbox(frame, font=("Segoe UI", 13), bg="#2b2b2b", fg="white",
                            bd=1, relief="solid", highlightthickness=0,
                            selectbackground="#1f538d", yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Προσθήκη ALL filtered items (όχι περιορισμό)
        for item in filtered_items:
            listbox.insert(tk.END, item)
        
        # Events
        listbox.bind('<ButtonRelease-1>', select_item)
        listbox.bind('<Return>', select_item)
        listbox.bind('<Escape>', lambda e: close_dropdown())
        
        # Κλείσιμο όταν χάνει το focus
        def on_focus_out(event):
            if event.widget not in [dropdown_window, listbox, scrollbar, combo_widget._entry]:
                close_dropdown()
        
        dropdown_window.bind('<FocusOut>', on_focus_out)
        listbox.focus_set()
    
    def on_keyrelease(event):
        if event.keysym in ['Up', 'Down', 'Return', 'Escape', 'Tab']:
            if event.keysym == 'Escape':
                close_dropdown()
            return
        
        typed = combo_widget.get().lower().strip()
        
        if not typed or typed.startswith("επιλέξτε"):
            close_dropdown()
            return
        
        # Φιλτράρισμα - βρίσκει items που ΠΕΡΙΕΧΟΥΝ το typed
        filtered = [item for item in full_list if typed in item.lower()]
        
        if filtered:
            show_dropdown(filtered)
        else:
            close_dropdown()
    
    combo_widget._entry.bind('<KeyRelease>', on_keyrelease)
    combo_widget._entry.bind('<FocusOut>', lambda e: combo_widget.after(500, close_dropdown))

def get_alloc_val(alloc, key, default=None):
    if isinstance(alloc, dict): 
        return alloc.get(key, default)
    return getattr(alloc, key, default)

# =============================================================================
# --- 1. ΑΡΧΙΚΟΠΟΙΗΣΗ ΒΑΣΗΣ & ΦΑΚΕΛΩΝ ---
# =============================================================================

# Βρίσκει τον φάκελο που είναι το main.py (π.χ. τον v5)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Determine the application path (for PyInstaller compatibility)
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    APPLICATION_PATH = os.path.dirname(sys.executable)
else:
    # Running as script
    APPLICATION_PATH = BASE_DIR

# Φτιάχνει τον φάκελο των εικόνων ΠΑΝΤΑ μέσα στον φάκελο της εφαρμογής
IMG_FOLDER = os.path.join(APPLICATION_PATH, "recipe_images")

if not os.path.exists(IMG_FOLDER):
    os.makedirs(IMG_FOLDER)

with DatabaseConn("recipe_database.db") as rcp_db:
    rcp_db.execute("CREATE TABLE IF NOT EXISTS categories_list(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
    rcp_db.execute("CREATE TABLE IF NOT EXISTS ingredient_list(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
    rcp_db.execute("CREATE TABLE IF NOT EXISTS unit_list(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
    rcp_db.execute("CREATE TABLE IF NOT EXISTS images(id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT)")
    
    rcp_db.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            difficulty TEXT,
            total_time_minutes INTEGER,
            image_path TEXT,
            category_id INTEGER REFERENCES categories_list(id),
            image_id INTEGER REFERENCES images(id)
        )
    """)
    
    rcp_db.execute("""
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER REFERENCES recipes(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            quantity REAL,
            unit TEXT,
            notes TEXT
        )
    """)
    
    rcp_db.execute("""
        CREATE TABLE IF NOT EXISTS steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER REFERENCES recipes(id) ON DELETE CASCADE,
            step_name TEXT,
            step_text TEXT,
            duration_in_minutes INTEGER,
            sequence_order INTEGER
        )
    """)
    
    # Πίνακας για τα υλικά μέσα στα βήματα
    rcp_db.execute("""
        CREATE TABLE IF NOT EXISTS step_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            step_id INTEGER REFERENCES steps(id) ON DELETE CASCADE,
            ingredient_id INTEGER REFERENCES ingredients(id) ON DELETE CASCADE,
            ingredient_name TEXT,
            quantity REAL,
            unit TEXT,
            notes TEXT
        )
    """)
    
    # ΠΡΟΦΟΡΤΩΣΗ ΑΡΧΙΚΩΝ ΔΕΔΟΜΕΝΩΝ
    # Προφόρτωση Κατηγοριών
    initial_categories = [
        "Ορεκτικά","Σαλάτες","Σούπες","Κυρίως Πιάτα","Ζυμαρικά","Ρύζι","Λαδερά","Φαγητά φούρνου","Ψητά","Τηγανητά",
        "Μαγειρευτά","Κρεατικά","Κοτόπουλο","Ψάρια & Θαλασσινά","Χορτοφαγικά","Vegetarian","Vegan","Πίτες","Αλμυρές πίτες","Γλυκές πίτες",
        "Αρτοσκευάσματα","Ψωμιά","Πρωινό","Σνακ","Γλυκά","Επιδόρπια","Παγωτά","Ροφήματα","Ποτά","Σάλτσες","Ντιπ","Μαρμελάδες & Γλυκά κουταλιού",
        "Κονσέρβες","Ζυμωτά","Παραδοσιακά","Νηστίσιμα","Κατοικίδιων"
    ]
    
    for cat in initial_categories:
        try:
            rcp_db.execute("INSERT OR IGNORE INTO categories_list (name) VALUES (?)", (cat,))
        except:
            pass
    
    # Προφόρτωση Υλικών
    initial_ingredients = [
        "Αλάτι", "Πιπέρι", "Ελαιόλαδο", "Ηλιέλαιο", "Νερό",
        "Αλεύρι Γ.Ο.Χ.", "Ζάχαρη κρυσταλλική", "Κρεμμύδι ξερό", 
        "Κρεμμύδι φρέσκο", "Σκόρδο", "Ντομάτα", "Πατάτα", 
        "Καρότο", "Πιπεριά", "Αυγό", "Γάλα", "Βούτυρο", 
        "Ρίγανη", "Κανέλα", "Λεμόνι", "Μαϊντανός", "Άνηθος",
        "Δυόσμος", "Θυμάρι", "Ματζουράνα", "Πάπρικα", "Κύμινο",
        "Μαύρο πιπέρι", "Κόκκινο πιπέρι", "Σκόνη σκόρδου",
        "Σκόνη κρεμμυδιού", "Μαγειρική σόδα", "Μπέικιν πάουντερ",
        "Γιαούρτι", "Κρέμα γάλακτος", "Τυρί φέτα", "Τυρί γραβιέρα",
        "Παρμεζάνα", "Μοτσαρέλα", "Ρύζι καρολίνα", "Ρύζι νυχάκι",
        "Ζυμαρικά μακαρόνια", "Ζυμαρικά πένες", "Φακές", "Φασόλια",
        "Ρεβίθια", "Λαχανικά κατεψυγμένα", "Κιμάς μοσχαρίσιος",
        "Κιμάς χοιρινός", "Κοτόπουλο", "Μοσχάρι", "Χοιρινό", "Αρνί"
    ]
    
    for ing in initial_ingredients:
        try:
            rcp_db.execute("INSERT OR IGNORE INTO ingredient_list (name) VALUES (?)", (ing,))
        except:
            pass

        # Προφόρτωση Μονάδων
    initial_units = [
        "kg", "g", "mg", "L", "ml", "κουταλιά/ες σούπας", "κουταλιά/ες γλυκού", 
        "τεμάχιο/α", "κούπα/ες", "πρέζα/ες", "φλιτζάνι/α", "ποτήρι/α", "ματσάκι/α", 
        "φέτα/ες", "ράβδος/οι", "συσκευασία/ες", "κουτί/α", "μπουκάλι/α", "σταγόνα/ες"
    ]
    
    for unit in initial_units:
        try:
            rcp_db.execute("INSERT OR IGNORE INTO unit_list (name) VALUES (?)", (unit,))
        except:
            pass

# --- ΝΕΟ: ΕΞΥΠΝΗ ΗΛΕΚΤΡΙΚΗ ΣΚΟΥΠΑ (ΠΡΟΣΤΑΤΕΥΕΙ ΤΑ ΧΕΙΡΟΚΙΝΗΤΑ ΑΡΧΕΙΑ) ---
def deep_clean_images():
    """Διαγράφει temp αρχεία και παλιές/διαγραμμένες εικόνες, ΑΛΛΑ προστατεύει τα προσωπικά αρχεία του χρήστη"""
    try:
        with DatabaseConn("recipe_database.db") as db:
            # Get ALL image paths from the images table (not just recipes)
            db.execute("SELECT path FROM images WHERE path IS NOT NULL AND path != ''")
            all_image_paths = [row[0] for row in db.fetchall() if row[0]]
            
            # Also get image_path directly from recipes table (for backward compatibility)
            db.execute("SELECT image_path FROM recipes WHERE image_path IS NOT NULL AND image_path != ''")
            recipe_image_paths = [row[0] for row in db.fetchall() if row[0]]
            
            # Combine all valid paths
            valid_paths = set(all_image_paths + recipe_image_paths)
            valid_filenames = {os.path.basename(path) for path in valid_paths if path}

            # Scan the images folder
            if os.path.exists(IMG_FOLDER):
                for filename in os.listdir(IMG_FOLDER):
                    filepath = os.path.normpath(os.path.join(IMG_FOLDER, filename))
                    
                    # Case A: Temp files - always delete
                    if filename.startswith("temp_"):
                        try: 
                            os.remove(filepath)
                            print(f"Deleted temp file: {filename}")
                        except Exception as e: 
                            print(f"Could not delete {filename}: {e}")
                        continue
                    
                    # Case B: App-generated images that are no longer in database
                    parts = filename.split('_', 1)
                    is_app_image = len(parts) == 2 and parts[0].isdigit()
                    
                    if is_app_image and filename not in valid_filenames:
                        try: 
                            os.remove(filepath)
                            print(f"Deleted orphaned image: {filename}")
                        except Exception as e: 
                            print(f"Could not delete {filename}: {e}")
                            
    except Exception as e:
        print(f"Σφάλμα καθαρισμού εικόνων: {e}")

# Τρέχουμε τη σκούπα μία φορά κάθε φορά που ανοίγει η εφαρμογή
deep_clean_images()

ctk.set_default_color_theme("blue")

# =============================================================================
# --- 2. ΚΛΑΣΕΙΣ ΦΟΡΜΩΝ ---
# =============================================================================

class IngredientFormPage:
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

        # --- ΟΝΟΜΑ ΣΥΣΤΑΤΙΚΟΥ με κουμπί διαχείρισης ---
        ing_name_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        ing_name_frame.pack(pady=(15,0), padx=20, fill=tk.X)
        
        ctk.CTkLabel(ing_name_frame, text="Όνομα Συστατικού:", font=("Segoe UI", 13)).pack(anchor="w")
        
        name_combo_frame = ctk.CTkFrame(ing_name_frame, fg_color="transparent")
        name_combo_frame.pack(fill=tk.X, pady=5)
        
        # Entry για εμφάνιση/πληκτρολόγηση
        self.name_entry = ctk.CTkEntry(name_combo_frame, width=270, font=("Segoe UI", 14))
        self.name_entry.pack(side=tk.LEFT, padx=(0, 5))
        enable_right_click_menu(self.name_entry)
        
        # Προσθήκη focus events για το placeholder
        def on_name_focus_in(event):
            if self.name_entry.get() == "Επιλέξτε ή πληκτρολογήστε...":
                self.name_entry.delete(0, tk.END)
        
        def on_name_focus_out(event):
            if self.name_entry.get() == "":
                self.name_entry.insert(0, "Επιλέξτε ή πληκτρολογήστε...")
        
        self.name_entry.bind("<FocusIn>", on_name_focus_in)
        self.name_entry.bind("<FocusOut>", on_name_focus_out)
        
        # Φόρτωση υλικών και ρύθμιση της επιλεγμένης τιμής
        if ingredient and ingredient.name:
            self.name_entry.insert(0, ingredient.name)
        else:
            self.name_entry.insert(0, "Επιλέξτε ή πληκτρολογήστε...")
        
        # Κουμπί dropdown που ανοίγει scrollable παράθυρο
        def open_ingredient_dialog():
            all_ingredients = DatabaseConn.get_all_ingredients()
            if not all_ingredients:
                all_ingredients = ["Αλάτι", "Πιπέρι", "Ελαιόλαδο", "Ηλιέλαιο", "Νερό"]
            all_ingredients = sorted(all_ingredients, key=greek_sort_key)
            
            dialog = ctk.CTkToplevel(name_combo_frame)
            dialog.title("Επιλογή Υλικού")
            center_and_size_window(dialog, 350, 400)
            set_window_icon(dialog)
            dialog.focus_force()
            
            scroll_frame = ctk.CTkScrollableFrame(dialog, width=300, height=350)
            scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            canvas = scroll_frame._parent_canvas
            
            def on_mousewheel(event):
                canvas.yview_scroll(int(-1 * (event.delta / 8)) * 3, "units")
                return "break"
            
            dialog.bind('<MouseWheel>', on_mousewheel)
            canvas.bind('<MouseWheel>', on_mousewheel)
            
            def select_ingredient(ing_name):
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, ing_name)
                dialog.destroy()
            
            for ing in all_ingredients:
                btn = ctk.CTkButton(scroll_frame, text=ing, 
                                   command=lambda i=ing: select_ingredient(i),
                                   font=("Segoe UI", 13), height=35,
                                   fg_color=["#3a7ebf", "#1f538d"],
                                   hover_color=["#325882", "#14375e"],
                                   text_color="white",
                                   anchor="w", cursor="hand2")
                btn.pack(fill=tk.X, pady=2, padx=5)
            
            ctk.CTkButton(dialog, text="Κλείσιμο", command=dialog.destroy,
                         fg_color="#8b0000", hover_color="#ff1a1a",
                         cursor="hand2").pack(pady=10)
        
        ctk.CTkButton(name_combo_frame, text="▼", width=35, height=35,
                     command=open_ingredient_dialog, cursor="hand2",
                     fg_color="#1f538d", hover_color="#2a72c1",
                     font=("Segoe UI", 14)).pack(side=tk.LEFT, padx=(0, 5))
        
        # Κουμπί διαχείρισης υλικών
        ctk.CTkButton(name_combo_frame, text="Διαχείριση Υλικών 🥕", width=40, height=35,
                      command=self.manage_ingredients_from_form,
                      fg_color="#C01E1E", hover_color="#d35400",
                      cursor="hand2", font=("Segoe UI", 16)).pack(side=tk.LEFT)
        

        
        # --- ΠΟΣΟΤΗΤΑ ---
        ctk.CTkLabel(scroll, text="Ποσότητα:", font=("Segoe UI", 13)).pack(padx=20, anchor="w")
        self.quantity_entry = ctk.CTkEntry(scroll, width=150, font=("Segoe UI", 14))
        self.quantity_entry.pack(pady=5, padx=20, anchor="w")
        if ingredient and ingredient.quantity: 
            self.quantity_entry.insert(0, float_to_fraction(ingredient.quantity))
        enable_right_click_menu(self.quantity_entry)
        
        # --- ΜΟΝΑΔΑ με κουμπιά επιλογής και διαχείρισης ---
        unit_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        unit_frame.pack(fill=tk.X, pady=5, padx=20)
        
        ctk.CTkLabel(unit_frame, text="Μονάδα:", font=("Segoe UI", 13), anchor="w").pack(anchor="w")
        
        unit_select_frame = ctk.CTkFrame(unit_frame, fg_color="transparent")
        unit_select_frame.pack(fill=tk.X, pady=5)
        
        # Entry για εμφάνιση/πληκτρολόγηση
        self.unit_entry = ctk.CTkEntry(unit_select_frame, width=210, font=("Segoe UI", 14))
        self.unit_entry.pack(side=tk.LEFT, padx=(0, 5))
        enable_right_click_menu(self.unit_entry)
        
        # Focus events για placeholder
        def on_unit_focus_in(event):
            if self.unit_entry.get() == "Επιλέξτε ή πληκτρολογήστε...":
                self.unit_entry.delete(0, tk.END)
        
        def on_unit_focus_out(event):
            if self.unit_entry.get() == "":
                self.unit_entry.insert(0, "Επιλέξτε ή πληκτρολογήστε...")
        
        self.unit_entry.bind("<FocusIn>", on_unit_focus_in)
        self.unit_entry.bind("<FocusOut>", on_unit_focus_out)
        
        if ingredient and ingredient.unit:
            self.unit_entry.insert(0, ingredient.unit)
        else:
            self.unit_entry.insert(0, "Επιλέξτε ή πληκτρολογήστε...")
        
        # Κουμπί dropdown για επιλογή μονάδας
        def open_unit_dialog():
            all_units = DatabaseConn.get_all_units()
            if not all_units:
                all_units = ["kg", "g", "mg", "L", "ml", "κουταλιά σούπας", "κουταλιά γλυκού", "τεμάχιο", "κούπα", "πρέζα"]
            all_units = sorted(all_units, key=greek_sort_key)
            
            dialog = ctk.CTkToplevel(unit_select_frame)
            dialog.title("Επιλογή Μονάδας")
            center_and_size_window(dialog, 350, 400)
            set_window_icon(dialog)
            dialog.focus_force()
            
            scroll_frame = ctk.CTkScrollableFrame(dialog, width=300, height=350)
            scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            canvas = scroll_frame._parent_canvas
            
            def on_mousewheel(event):
                canvas.yview_scroll(int(-1 * (event.delta / 8)) * 3, "units")
                return "break"
            
            dialog.bind('<MouseWheel>', on_mousewheel)
            canvas.bind('<MouseWheel>', on_mousewheel)
            
            def select_unit(unit_name):
                self.unit_entry.delete(0, tk.END)
                self.unit_entry.insert(0, unit_name)
                dialog.destroy()
            
            for unit in all_units:
                btn = ctk.CTkButton(scroll_frame, text=unit, 
                                   command=lambda u=unit: select_unit(u),
                                   font=("Segoe UI", 13), height=35,
                                   fg_color=["#3a7ebf", "#1f538d"],
                                   hover_color=["#325882", "#14375e"],
                                   text_color="white",
                                   anchor="w", cursor="hand2")
                btn.pack(fill=tk.X, pady=2, padx=5)
            
            ctk.CTkButton(dialog, text="Κλείσιμο", command=dialog.destroy,
                         fg_color="#8b0000", hover_color="#ff1a1a",
                         cursor="hand2").pack(pady=10)
        
        ctk.CTkButton(unit_select_frame, text="▼", width=35, height=35,
                     command=open_unit_dialog, cursor="hand2",
                     fg_color="#1f538d", hover_color="#2a72c1",
                     font=("Segoe UI", 14)).pack(side=tk.LEFT, padx=(0, 5))
        
        # Κουμπί διαχείρισης μονάδων
        def manage_units():
            d = ctk.CTkToplevel(self.window)
            d.title("Διαχείριση Μονάδων")
            center_and_size_window(d, 500, 450)
            set_window_icon(d)
            d.grab_set()
            
            units = DatabaseConn.get_all_units()
            if not units:
                units = ["kg", "g", "mg", "L", "ml", "κουταλιά σούπας", "κουταλιά γλυκού", "τεμάχιο", "κούπα", "πρέζα"]
            units = sorted(units, key=greek_sort_key)
            
            main_frame = ctk.CTkFrame(d)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            ctk.CTkLabel(main_frame, text="Λίστα Μονάδων", font=("Segoe UI", 16, "bold")).pack(pady=(0, 10))
            
            # Scrollable listbox
            list_frame = ctk.CTkFrame(main_frame)
            list_frame.pack(fill=tk.BOTH, expand=True)
            
            listbox_frame = tk.Frame(list_frame)
            listbox_frame.pack(fill=tk.BOTH, expand=True)
            
            scrollbar = tk.Scrollbar(listbox_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            current_theme = ctk.get_appearance_mode()
            if current_theme == "Dark":
                bg_color = "#2b2b2b"
                fg_color = "white"
            else:
                bg_color = "#ffffff"
                fg_color = "black"
            
            listbox = tk.Listbox(listbox_frame, font=("Segoe UI", 13), bg=bg_color, fg=fg_color,
                                selectbackground='#1f538d', selectforeground='white',
                                yscrollcommand=scrollbar.set, bd=1, relief="solid", highlightthickness=0)
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=listbox.yview)
            
            for unit in units:
                listbox.insert(tk.END, unit)
            
            # Πλαίσιο προσθήκης
            add_frame = ctk.CTkFrame(main_frame)
            add_frame.pack(fill=tk.X, pady=15)
            
            new_unit_entry = ctk.CTkEntry(add_frame, placeholder_text="Νέα μονάδα...", font=("Segoe UI", 14), width=250)
            new_unit_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
            
            def add_unit():
                new_unit = new_unit_entry.get().strip()
                if not new_unit:
                    messagebox.showwarning("Προσοχή", "Παρακαλώ εισάγετε μια μονάδα.")
                    return
                
                if DatabaseConn.add_unit(new_unit):
                    current_items = list(listbox.get(0, tk.END))
                    current_items.append(new_unit)
                    current_items.sort(key=greek_sort_key)
                    
                    listbox.delete(0, tk.END)
                    for item in current_items:
                        listbox.insert(tk.END, item)
                    
                    new_unit_entry.delete(0, tk.END)
                    messagebox.showinfo("Επιτυχία", f"Η μονάδα '{new_unit}' προστέθηκε!")
                else:
                    messagebox.showerror("Σφάλμα", "Η μονάδα υπάρχει ήδη")
            
            ctk.CTkButton(add_frame, text="➕ Προσθήκη", command=add_unit, 
                         cursor="hand2", width=100, fg_color="#28a745", hover_color="#218838").pack(side=tk.RIGHT)
            
            # Πλαίσιο διαγραφής
            delete_frame = ctk.CTkFrame(main_frame)
            delete_frame.pack(fill=tk.X, pady=5)
            
            def delete_unit():
                selection = listbox.curselection()
                if not selection:
                    messagebox.showwarning("Προσοχή", "Επιλέξτε μια μονάδα για διαγραφή.")
                    return
                
                unit_name = listbox.get(selection[0])
                
                if not messagebox.askyesno("Επιβεβαίωση", f"Θέλετε να διαγράψετε τη μονάδα '{unit_name}';"):
                    return
                
                if DatabaseConn.delete_unit(unit_name):
                    listbox.delete(selection[0])
                    messagebox.showinfo("Επιτυχία", f"Η μονάδα '{unit_name}' διαγράφηκε!")
                else:
                    messagebox.showerror("Σφάλμα", "Δεν μπορείτε να διαγράψετε μονάδα που χρησιμοποιείται σε συνταγές")
            
            ctk.CTkButton(delete_frame, text="❌ Διαγραφή Επιλεγμένης", command=delete_unit, 
                         fg_color="#8b0000", hover_color="#ff1a1a", cursor="hand2", width=200).pack()
            
            new_unit_entry.bind('<Return>', lambda e: add_unit())
            ctk.CTkButton(main_frame, text="Κλείσιμο", command=d.destroy, 
                         fg_color="#1f538d", hover_color="#2a72c1", cursor="hand2", width=150).pack(pady=15)
        
        ctk.CTkButton(unit_select_frame, text="📏 Διαχείριση", width=100, height=35,
                     command=manage_units, cursor="hand2",
                     fg_color="#e67e22", hover_color="#d35400",
                     font=("Segoe UI", 13)).pack(side=tk.LEFT)
        
        # --- ΣΗΜΕΙΩΣΕΙΣ ---
        ctk.CTkLabel(scroll, text="Σημειώσεις:", font=("Segoe UI", 13)).pack(padx=20, anchor="w")
        self.notes_entry = ctk.CTkEntry(scroll, width=350, font=("Segoe UI", 14))
        self.notes_entry.pack(pady=5, padx=20, anchor="w")
        if ingredient and ingredient.notes: 
            self.notes_entry.insert(0, ingredient.notes)
        enable_right_click_menu(self.notes_entry)
        
        # --- ΚΟΥΜΠΙ ΑΠΟΘΗΚΕΥΣΗΣ ---
        ctk.CTkButton(scroll, text="Αποθήκευση", command=self.save, font=("Segoe UI", 14, "bold"), height=40, cursor="hand2").pack(pady=30)


    def manage_ingredients_from_form(self):
        """Ανοίγει παράθυρο διαχείρισης υλικών"""
        d = ctk.CTkToplevel(self.window)
        d.title("Διαχείριση Υλικών")
        center_and_size_window(d, 500, 450)
        set_window_icon(d)
        d.grab_set()
        
        ingredients = DatabaseConn.get_all_ingredients()
        ingredients = sorted(ingredients, key=greek_sort_key)
        
        # Πλαίσιο για τη λίστα και τα κουμπιά
        main_frame = ctk.CTkFrame(d)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Ετικέτα
        ctk.CTkLabel(main_frame, text="Λίστα Υλικών", font=("Segoe UI", 16, "bold")).pack(pady=(0, 10))
        
        # Scrollable listbox
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
                # Δημιουργία Listbox με scrollbar - σωστά χρώματα ανάλογα με το θέμα
        listbox_frame = tk.Frame(list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Παίρνουμε το τρέχον θέμα ΑΜΕΣΑ από το ctk
        current_theme = ctk.get_appearance_mode()
        
        if current_theme == "Dark":
            bg_color = "#2b2b2b"
            fg_color = "white"
        else:
            bg_color = "#ffffff"
            fg_color = "black"
        
        listbox = tk.Listbox(listbox_frame, font=("Segoe UI", 13), bg=bg_color, fg=fg_color,
                            selectbackground='#1f538d', selectforeground='white',
                            yscrollcommand=scrollbar.set, bd=1, relief="solid", highlightthickness=0)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Προσθήκη υλικών στη λίστα
        for ing in ingredients:
            listbox.insert(tk.END, ing)
        
        # Πλαίσιο για προσθήκη νέου υλικού
        add_frame = ctk.CTkFrame(main_frame)
        add_frame.pack(fill=tk.X, pady=15)
        
        self.new_ing_entry = ctk.CTkEntry(add_frame, placeholder_text="Νέο υλικό...", font=("Segoe UI", 14), width=250)
        self.new_ing_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        def add_ingredient():
            new_ing = self.new_ing_entry.get().strip()
            if not new_ing:
                messagebox.showwarning("Προσοχή", "Παρακαλώ εισάγετε ένα υλικό.")
                return
            
            if DatabaseConn.add_ingredient(new_ing):
                # Προσθήκη στη λίστα με αλφαβητική σειρά
                current_items = list(listbox.get(0, tk.END))
                current_items.append(new_ing)
                current_items.sort(key=greek_sort_key)
                
                listbox.delete(0, tk.END)
                for item in current_items:
                    listbox.insert(tk.END, item)
                
                self.new_ing_entry.delete(0, tk.END)
                messagebox.showinfo("Επιτυχία", f"Το υλικό '{new_ing}' προστέθηκε!")
            else:
                messagebox.showerror("Σφάλμα", "Το υλικό υπάρχει ήδη")
        
        ctk.CTkButton(add_frame, text="➕ Προσθήκη", command=add_ingredient, 
                      cursor="hand2", width=100, fg_color="#28a745", hover_color="#218838").pack(side=tk.RIGHT)
        
        # Πλαίσιο για διαγραφή
        delete_frame = ctk.CTkFrame(main_frame)
        delete_frame.pack(fill=tk.X, pady=5)
        
        def delete_ingredient():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Προσοχή", "Επιλέξτε ένα υλικό για διαγραφή.")
                return
            
            ing_name = listbox.get(selection[0])
            
            if not messagebox.askyesno("Επιβεβαίωση", f"Θέλετε να διαγράψετε το υλικό '{ing_name}';"):
                return
            
            if DatabaseConn.delete_ingredient(ing_name):
                listbox.delete(selection[0])
                messagebox.showinfo("Επιτυχία", f"Το υλικό '{ing_name}' διαγράφηκε!")
            else:
                messagebox.showerror("Σφάλμα", "Δεν μπορείτε να διαγράψετε υλικό που χρησιμοποιείται σε συνταγές")
        
        ctk.CTkButton(delete_frame, text="❌ Διαγραφή Επιλεγμένου", command=delete_ingredient, 
                      fg_color="#8b0000", hover_color="#ff1a1a", cursor="hand2", width=200).pack()
        
        # Επιτρέπει στο Enter να προσθέτει το υλικό
        self.new_ing_entry.bind('<Return>', lambda e: add_ingredient())
        
        # Κουμπί κλεισίματος
        ctk.CTkButton(main_frame, text="Κλείσιμο", command=d.destroy, 
                     fg_color="#1f538d", hover_color="#2a72c1", cursor="hand2", width=150).pack(pady=15)
        

    def save(self):
        name = self.name_entry.get().strip()
        if not name or name.startswith("Επιλέξτε"): 
            return messagebox.showerror("Σφάλμα", "Το όνομα είναι υποχρεωτικό.")
        try:
            qty_value = fraction_to_float(self.quantity_entry.get())
            if qty_value is None:
                return messagebox.showerror("Σφάλμα", "Εισάγετε έγκυρη ποσότητα (π.χ. 1.5, 1/2, 2 1/2)")
            qty = qty_value
            if qty <= 0: 
                return messagebox.showerror("Σφάλμα", "Η ποσότητα πρέπει να είναι θετική.")
            
            unit_val = self.unit_entry.get().strip()
            if unit_val == "Επιλέξτε...": 
                unit_val = ""
                
            ing = Ingredient(name=name, quantity=qty, unit=unit_val, notes=self.notes_entry.get().strip())
            
            if self.index is not None:
                # Επεξεργασία υπάρχοντος υλικού - ΑΝΤΙΚΑΤΑΣΤΑΣΗ
                old_ing = self.parent_form.ingredients[self.index]
                if hasattr(old_ing, 'id'): 
                    ing.id = old_ing.id
                self.parent_form.ingredients[self.index] = ing
            else:
                # Νέο υλικό - ΕΛΕΓΧΟΣ για διπλότυπο
                found = False
                for existing in self.parent_form.ingredients:
                    if existing.name == name and existing.unit == unit_val and existing.notes == ing.notes:
                        # Βρέθηκε ίδιο υλικό - ενώνουμε τις ποσότητες
                        existing.quantity = round(existing.quantity + qty, 5)
                        found = True
                        break
                
                if not found:
                    # Δεν υπάρχει - κανονική προσθήκη
                    self.parent_form.ingredients.append(ing)
            
            # Ταξινόμηση μετά από οποιαδήποτε αλλαγή
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

         # Disable unlock button in parent form while editing
        if hasattr(self.parent_form, 'unlock_btn'):
            self.parent_form.unlock_btn.configure(state=tk.DISABLED)
        
        # Set up close handler to restore unlock button
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        scroll = ctk.CTkScrollableFrame(self.window, fg_color="transparent")
        scroll.pack(fill=tk.BOTH, expand=True)

        existing_step_names = [
            "Προετοιμασία", "Κόψιμο", "Σοτάρισμα", "Βράσιμο", 
            "Ψήσιμο", "Τηγάνισμα", "Ανάμειξη", "Μαρινάρισμα", "Σερβίρισμα"
        ]
        try:
            with DatabaseConn("recipe_database.db") as db:
                db.execute("SELECT DISTINCT step_name FROM steps")
                db_steps = [row[0] for row in db.fetchall() if row[0] and row[0] not in existing_step_names]
                existing_step_names.extend(db_steps)
        except Exception: pass

        existing_step_names = sorted(list(set(existing_step_names)), key=greek_sort_key)

        ctk.CTkLabel(scroll, text="Τίτλος Βήματος:", font=("Segoe UI", 13)).pack(pady=(15,0), padx=20, anchor="w")
        self.step_name_combo = ctk.CTkComboBox(scroll, values=existing_step_names, width=400, font=("Segoe UI", 14))
        self.step_name_combo.pack(pady=5, padx=20, anchor="w")
        
        # Ρύθμιση αρχικής τιμής
        if step and step.step_name:
            self.step_name_combo.set(step.step_name)
        else:
            self.step_name_combo.set("Επιλέξτε ή πληκτρολογήστε...")
        
        enable_right_click_menu(self.step_name_combo)
        setup_autocomplete(self.step_name_combo, existing_step_names)
        
        # Προσθήκη focus events για το placeholder του combobox
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
        
        # Το νέο κουμπί "Προσθήκη Όλων" (πορτοκαλί)
        ctk.CTkButton(h_f, text="+ Προσθήκη Όλων", command=self.add_all_ingredients, width=130, cursor="hand2", fg_color="#e67e22", hover_color="#d35400").pack(side=tk.RIGHT, padx=(10, 0))
        
        # Το υπάρχον κουμπί "Προσθήκη Υλικού" (μπλε)
        ctk.CTkButton(h_f, text="+ Προσθήκη Υλικού", command=self.add_ingredient_from_existing, width=150, cursor="hand2").pack(side=tk.RIGHT)

        self.ingredients_tree = ttk.Treeview(scroll, columns=('Όνομα', 'Ποσότητα', 'Μονάδα'), show='headings', height=5)
        for col in self.ingredients_tree['columns']: 
            self.ingredients_tree.heading(col, text=col)
            self.ingredients_tree.column(col, anchor='center') # <-- ΠΡΟΣΤΕΘΗΚΕ Η ΣΤΟΙΧΙΣΗ
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
        """Called when window is closed via X button"""
        # Restore unlock button in parent form
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
            # Υπολογισμός πόσο έχει καταναλωθεί σε άλλα βήματα
            for i, st in enumerate(self.parent_form.steps):
                if self.index is not None and i == self.index:
                    continue
                allocs = getattr(st, 'allocations', getattr(st, 'step_ingredients', []))
                for alloc in allocs:
                    if get_alloc_val(alloc, 'notes') == "Στάδιο Προετοιμασίας":
                        continue
                    # Check by name AND unit to differentiate
                    if (get_alloc_val(alloc, 'temp_id') == idx or 
                        (get_alloc_val(alloc, 'ingredient_name') == ing.name and 
                        get_alloc_val(alloc, 'unit') == ing.unit)):
                        used += get_alloc_val(alloc, 'quantity', 0)
            
            # Υπολογισμός πόσο έχει ήδη προστεθεί σε αυτό το βήμα
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
        
        # Frame για τα στοιχεία
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
        
        # Ποσότητα with Max button
        qty_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        qty_frame.pack(fill=tk.X, pady=5)

        ctk.CTkLabel(qty_frame, text="Ποσότητα:", font=("Segoe UI", 14), anchor="w").pack(anchor="w")

        qty_input_frame = ctk.CTkFrame(qty_frame, fg_color="transparent")
        qty_input_frame.pack(fill=tk.X, pady=(5, 0))

        qty_ent = ctk.CTkEntry(qty_input_frame, placeholder_text="Π.χ. 500", font=("Segoe UI", 14), width=150)
        qty_ent.pack(side=tk.LEFT, padx=(0, 10))

        # Store reference to current available quantity
        current_avail = 0

        def set_max_quantity():
            """Set the quantity entry to the maximum available amount"""
            # Get the currently selected ingredient
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
        
        # Frame για τα κουμπιά
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        def confirm():
            try:
                selected_display = combo.get()
                if not selected_display:
                    messagebox.showerror("Λάθος", "Επιλέξτε ένα υλικό.")
                    return
                
                sel = ing_data[ing_list.index(selected_display)]
                
                # Update the current available quantity for the Max button
                nonlocal current_avail
                current_avail = sel['avail']
                
                qty_text = qty_ent.get().strip().replace(',', '.')
                if not qty_text:
                    messagebox.showerror("Λάθος", "Εισάγετε ποσότητα.")
                    return
                
                val = fraction_to_float(qty_text)
                if val is None:
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
                
                # ΕΛΕΓΧΟΣ: Αν το υλικό υπάρχει ήδη στο βήμα, το ενώνουμε (check by name AND unit)
                found = False
                for existing in self.step_allocations:
                    # Match by temp_id OR (ingredient_name AND unit)
                    if (existing.get('temp_id') == sel['temp_id'] or 
                        (existing.get('ingredient_name') == sel['name'] and 
                        existing.get('unit') == sel['unit'] and
                        existing.get('notes') == notes_val)):
                        existing['quantity'] = round(existing['quantity'] + val, 5)
                        found = True
                        break
                
                if not found:
                    # Νέο υλικό - προσθήκη
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
        
        # Επιτρέπει στο Enter να προσθέτει
        qty_ent.bind('<Return>', lambda e: confirm())

    def add_all_ingredients(self):
        """Προσθέτει αυτόματα όλα τα υπόλοιπα διαθέσιμα υλικά στο τρέχον βήμα"""
        if not self.parent_form.ingredients: 
            return messagebox.showwarning("!", "Προσθέστε πρώτα υλικά στη συνταγή.")
            
        added_count = 0
        for idx, ing in enumerate(self.parent_form.ingredients):
            used = 0
            # 1. Υπολογισμός πόσο έχουμε ξοδέψει στα ΑΛΛΑ βήματα
            for i, st in enumerate(self.parent_form.steps):
                if self.index is not None and i == self.index: continue
                allocs = getattr(st, 'allocations', getattr(st, 'step_ingredients', []))
                for alloc in allocs:
                    if get_alloc_val(alloc, 'notes') == "Στάδιο Προετοιμασίας": continue
                    if get_alloc_val(alloc, 'temp_id') == idx or get_alloc_val(alloc, 'ingredient_name') == ing.name:
                        used += get_alloc_val(alloc, 'quantity', 0)
                        
            # 2. Υπολογισμός πόσο έχουμε ΉΔΗ βάλει σε ΑΥΤΟ το βήμα
            for alloc in self.step_allocations:
                if get_alloc_val(alloc, 'notes') == "Στάδιο Προετοιμασίας": continue
                if get_alloc_val(alloc, 'temp_id') == idx or get_alloc_val(alloc, 'ingredient_name') == ing.name:
                    used += get_alloc_val(alloc, 'quantity', 0)
                    
            avail = round(ing.quantity - used, 5)
            
            # Αν έχει περισσέψει υλικό, το ρίχνουμε όλο μέσα!
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
        # Clear the treeview
        for i in self.ingredients_tree.get_children(): 
            self.ingredients_tree.delete(i)
        
        # Add each allocation to the treeview
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
            
            # Make a clean copy of allocations with proper names
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
            
            # Restore unlock button in parent form
            if hasattr(self.parent_form, 'unlock_btn'):
                if self.parent_form.ingredients_locked:
                    self.parent_form.unlock_btn.configure(state=tk.NORMAL)
                else:
                    self.parent_form.unlock_btn.configure(state=tk.DISABLED)
            
            self.window.destroy()
        except ValueError: 
            messagebox.showerror("!", "Η διάρκεια πρέπει να είναι αριθμός.")

class RecipeFormPage:
    def __init__(self, parent_app, recipe_id=None):
        self.parent_app = parent_app
        self.recipe_id = recipe_id
        self.ingredients = []
        self.steps = []
        self.selected_image_path = None
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

        # --- ΠΕΡΙΟΧΗ ΕΙΚΟΝΑΣ ---
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

        # --- ΥΠΟΛΟΙΠΗ ΦΟΡΜΑ ---
        info_frame = ctk.CTkFrame(self.scroll)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        # Όνομα Συνταγής
        name_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        name_row.pack(fill=tk.X, pady=5)
        ctk.CTkLabel(name_row, text="Όνομα Συνταγής:", font=("Segoe UI", 14), width=120, anchor="w").pack(side=tk.LEFT, padx=(15, 10))
        self.name_entry = ctk.CTkEntry(name_row, width=200, font=("Segoe UI", 14))
        self.name_entry.pack(side=tk.LEFT)
        enable_right_click_menu(self.name_entry)

        # Κατηγορία
        cat_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        cat_row.pack(fill=tk.X, pady=10)
        ctk.CTkLabel(cat_row, text="Κατηγορία:", font=("Segoe UI", 14), width=120, anchor="w").pack(side=tk.LEFT, padx=(15, 10))

        all_cats = DatabaseConn.get_all_categories()
        if not all_cats:
            all_cats = ["Ορεκτικά","Σαλάτες","Σούπες","Κυρίως Πιάτα","Ζυμαρικά","Ρύζι","Λαδερά","Φαγητά φούρνου","Ψητά","Τηγανητά",
                        "Μαγειρευτά","Κρεατικά","Κοτόπουλο","Ψάρια & Θαλασσινά","Χορτοφαγικά","Vegetarian","Vegan","Πίτες","Αλμυρές πίτες","Γλυκές πίτες",
                        "Αρτοσκευάσματα","Ψωμιά","Πρωινό","Σνακ","Γλυκά","Επιδόρπια","Παγωτά","Ροφήματα","Ποτά","Σάλτσες","Ντιπ","Μαρμελάδες & Γλυκά κουταλιού",
                        "Κονσέρβες","Ζυμωτά","Παραδοσιακά","Νηστίσιμα","Κατοικίδιων"]
        all_cats = sorted(all_cats, key=greek_sort_key)

        cat_input_frame = ctk.CTkFrame(cat_row, fg_color="transparent")
        cat_input_frame.pack(side=tk.LEFT)

        self.category_entry = ctk.CTkEntry(cat_input_frame, width=250, font=("Segoe UI", 14))
        self.category_entry.pack(side=tk.LEFT, padx=(0, 5))
        enable_right_click_menu(self.category_entry)

        def on_category_focus_in(event):
            if self.category_entry.get() == "Επιλέξτε ή πληκτρολογήστε...":
                self.category_entry.delete(0, tk.END)

        def on_category_focus_out(event):
            if self.category_entry.get() == "":
                self.category_entry.insert(0, "Επιλέξτε ή πληκτρολογήστε...")

        self.category_entry.bind("<FocusIn>", on_category_focus_in)
        self.category_entry.bind("<FocusOut>", on_category_focus_out)
        self.category_entry.insert(0, "Επιλέξτε ή πληκτρολογήστε...")

        def open_category_dialog():
            dialog = ctk.CTkToplevel(cat_input_frame)
            dialog.title("Επιλογή Κατηγορίας")
            center_and_size_window(dialog, 350, 400)
            set_window_icon(dialog)
            dialog.focus_force()

            scroll_frame = ctk.CTkScrollableFrame(dialog, width=300, height=350)
            scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            canvas = scroll_frame._parent_canvas

            def on_mousewheel(event):
                canvas.yview_scroll(int(-1 * (event.delta / 8)) * 3, "units")
                return "break"

            dialog.bind('<MouseWheel>', on_mousewheel)
            canvas.bind('<MouseWheel>', on_mousewheel)

            def select_category(cat_name):
                self.category_entry.delete(0, tk.END)
                self.category_entry.insert(0, cat_name)
                dialog.destroy()

            # LOAD CATEGORIES FROM DATABASE EVERY TIME THE DIALOG OPENS
            current_cats = DatabaseConn.get_all_categories()
            if not current_cats:
                current_cats = ["Ορεκτικά","Σαλάτες","Σούπες","Κυρίως Πιάτα","Ζυμαρικά","Ρύζι","Λαδερά","Φαγητά φούρνου","Ψητά","Τηγανητά",
                                "Μαγειρευτά","Κρεατικά","Κοτόπουλο","Ψάρια & Θαλασσινά","Χορτοφαγικά","Vegetarian","Vegan","Πίτες","Αλμυρές πίτες","Γλυκές πίτες",
                                "Αρτοσκευάσματα","Ψωμιά","Πρωινό","Σνακ","Γλυκά","Επιδόρπια","Παγωτά","Ροφήματα","Ποτά","Σάλτσες","Ντιπ","Μαρμελάδες & Γλυκά κουταλιού",
                                "Κονσέρβες","Ζυμωτά","Παραδοσιακά","Νηστίσιμα","Κατοικίδιων"]
            current_cats = sorted(current_cats, key=greek_sort_key)
            
            for cat in current_cats:
                btn = ctk.CTkButton(scroll_frame, text=cat,
                                   command=lambda c=cat: select_category(c),
                                   font=("Segoe UI", 13), height=35,
                                   fg_color=["#3a7ebf", "#1f538d"],
                                   hover_color=["#325882", "#14375e"],
                                   text_color="white",
                                   anchor="w", cursor="hand2")
                btn.pack(fill=tk.X, pady=2, padx=5)

            ctk.CTkButton(dialog, text="Κλείσιμο", command=dialog.destroy,
                         fg_color="#8b0000", hover_color="#ff1a1a",
                         cursor="hand2").pack(pady=10)

        ctk.CTkButton(cat_input_frame, text="▼", width=35, height=35,
                     command=open_category_dialog, cursor="hand2",
                     fg_color="#1f538d", hover_color="#2a72c1",
                     font=("Segoe UI", 14)).pack(side=tk.LEFT, padx=(0, 5))

        ctk.CTkButton(cat_input_frame, text="Διαχείριση Κατηγοριών ⚙️", width=35, height=35,
                     command=self.manage_categories_dialog, cursor="hand2",
                     fg_color="#9b59b6", hover_color="#8e44ad",
                     font=("Segoe UI", 14)).pack(side=tk.LEFT)

        # Δυσκολία και Χρόνος
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

        # --- Λίστα Συστατικών ---
        ing_title_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        ing_title_frame.pack(fill=tk.X, pady=(20, 10))
        
        ctk.CTkLabel(ing_title_frame, text="Λίστα Συστατικών", font=("Segoe UI", 18, "bold")).pack(anchor="center")
        
        # Ingredients Treeview
        ing_tree_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        ing_tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create Treeview with scrollbar
        tree_container = ttk.Frame(ing_tree_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        ing_scrollbar = ttk.Scrollbar(tree_container)
        ing_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview with scrollbar
        self.ing_tree = ttk.Treeview(tree_container, columns=('Όνομα', 'Ποσότητα', 'Μονάδα', 'Σημειώσεις'), 
                                      show='headings', height=8, yscrollcommand=ing_scrollbar.set)
        for col in self.ing_tree['columns']: 
            self.ing_tree.heading(col, text=col)
            self.ing_tree.column(col, anchor='center')
        self.ing_tree.column('Όνομα', width=200)
        self.ing_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ing_scrollbar.config(command=self.ing_tree.yview)

        setup_treeview_scroll(self.ing_tree)

        # Row 1: Add, Edit, Delete buttons
        btn_row1 = ctk.CTkFrame(self.scroll, fg_color="transparent")
        btn_row1.pack(pady=5)
        
        self.add_ing_btn = ctk.CTkButton(btn_row1, text="➕ Προσθήκη", command=lambda: IngredientFormPage(self), cursor="hand2")
        self.add_ing_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_ing_btn = ctk.CTkButton(btn_row1, text="✏️ Επεξεργασία", command=self.edit_ingredient, cursor="hand2")
        self.edit_ing_btn.pack(side=tk.LEFT, padx=5)
        
        self.del_ing_btn = ctk.CTkButton(btn_row1, text="❌ Διαγραφή", fg_color="#8b0000", hover_color="#ff1a1a", command=self.delete_ingredient, cursor="hand2")
        self.del_ing_btn.pack(side=tk.LEFT, padx=5)

        # Row 2: Confirm, Unlock, and Manage buttons
        btn_row2 = ctk.CTkFrame(self.scroll, fg_color="transparent")
        btn_row2.pack(pady=10)
        
        self.confirm_btn = ctk.CTkButton(btn_row2, text="✓ Επιβεβαίωση Υλικών", fg_color="#28a745", hover_color="#218838", command=self.confirm_ingredients, font=("Segoe UI", 13, "bold"), height=35, cursor="hand2")
        self.confirm_btn.pack(side=tk.LEFT, padx=5)
        
        self.unlock_btn = ctk.CTkButton(btn_row2, text="✎ Ξεκλείδωμα", fg_color="gray", state=tk.DISABLED, command=self.unlock_ingredients, cursor="hand2", height=35)
        self.unlock_btn.pack(side=tk.LEFT, padx=5)
        
        self.manage_ing_btn = ctk.CTkButton(btn_row2, text="🥕 Διαχείριση Υλικών", command=self.manage_ingredients_dialog,
                                            fg_color="#e67e22", hover_color="#d35400", cursor="hand2", height=35)
        self.manage_ing_btn.pack(side=tk.LEFT, padx=5)

        # --- Βήματα Εκτέλεσης ---
        steps_title_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        steps_title_frame.pack(fill=tk.X, pady=(25, 10))

        self.steps_label = ctk.CTkLabel(steps_title_frame, text="Βήματα Εκτέλεσης", font=("Segoe UI", 18, "bold"))
        self.steps_label.pack(anchor="center")

        # Steps Treeview with Scrollbar
        steps_tree_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        steps_tree_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Create frame for tree + scrollbar
        tree_frame = ttk.Frame(steps_tree_container)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Vertical scrollbar only
        steps_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
        steps_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview with vertical scrollbar
        self.steps_tree = ttk.Treeview(
            tree_frame, 
            columns=('Αρ.', 'Τίτλος', 'Περιγραφή', 'Διάρκεια'), 
            show='headings', 
            height=6,
            yscrollcommand=steps_scroll_y.set
        )

        # Configure columns
        self.steps_tree.column('Αρ.', width=60, anchor='center')
        self.steps_tree.column('Τίτλος', width=200, anchor='w')
        self.steps_tree.column('Περιγραφή', width=400, anchor='w')
        self.steps_tree.column('Διάρκεια', width=100, anchor='center')

        # Configure headings
        self.steps_tree.heading('Αρ.', text='#')
        self.steps_tree.heading('Τίτλος', text='Τίτλος Βήματος')
        self.steps_tree.heading('Περιγραφή', text='Περιγραφή')
        self.steps_tree.heading('Διάρκεια', text='Διάρκεια')

        # Connect scrollbar
        steps_scroll_y.config(command=self.steps_tree.yview)

        self.steps_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        setup_treeview_scroll(self.steps_tree)

        # Bind events
        self.steps_tree.bind('<<TreeviewSelect>>', self.on_step_select)
        self.steps_tree.bind("<Double-1>", lambda e: self.view_step())

        # Button row: Add, Edit, Delete, View
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

    # --- ΜΕΘΟΔΟΙ ΕΙΚΟΝΑΣ ---
    def on_close(self):
        if getattr(self, 'selected_image_path', None) and "temp_" in self.selected_image_path:
            try: os.remove(self.selected_image_path)
            except Exception: pass
        self.window.destroy()  

    def update_image_preview(self, path):
        if path and os.path.exists(path):
            try:
                with Image.open(path) as raw_img:
                    img_copy = raw_img.copy()
                self.preview_img_obj = ctk.CTkImage(img_copy, size=(230, 160))
                self.img_preview_label.configure(image=self.preview_img_obj, text="")
            except Exception:
                self.preview_img_obj = None
                self.img_preview_label.configure(image="", text="Σφάλμα φόρτωσης", text_color="#ffffff")
        else:
            self.preview_img_obj = None
            self.img_preview_label.configure(image="", text="Δεν υπάρχει εικόνα", text_color="#ffffff")

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
            try: os.remove(self.selected_image_path)
            except Exception: pass

        self.selected_image_path = temp_path
        self.update_image_preview(temp_path)

    def remove_image(self):
        if getattr(self, 'selected_image_path', None) and "temp_" in self.selected_image_path:
            try: os.remove(self.selected_image_path)
            except Exception: pass
        self.selected_image_path = "DELETED"
        self.update_image_preview(None)

    # --- ΜΕΘΟΔΟΙ ΔΙΑΧΕΙΡΙΣΗΣ ΚΑΤΗΓΟΡΙΩΝ, ΒΗΜΑΤΩΝ & ΥΛΙΚΩΝ ---
    def view_step(self):
        """Εμφανίζει πλήρη προβολή του επιλεγμένου βήματος"""
        sel = self.steps_tree.selection()
        if not sel:
            return
        
        idx = self.steps_tree.get_children().index(sel[0])
        step = self.steps[idx]
        
        # Δημιουργία παραθύρου προβολής
        view_window = ctk.CTkToplevel(self.window)
        view_window.title(f"Βήμα {idx + 1}: {step.step_name}")
        center_and_size_window(view_window, 600, 500)
        set_window_icon(view_window)
        view_window.transient(self.window)
        view_window.grab_set()
        
        # Scrollable frame για μεγάλο κείμενο
        main_frame = ctk.CTkScrollableFrame(view_window, fg_color="transparent")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Τίτλος
        ctk.CTkLabel(main_frame, text=f"Βήμα {idx + 1}: {step.step_name}", 
                    font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0, 15))
        
        # Διάρκεια
        ctk.CTkLabel(main_frame, text=f"⏱️ Διάρκεια: {step.duration_in_minutes} λεπτά", 
                    font=("Segoe UI", 14)).pack(anchor="w", pady=(0, 10))
        
        # Περιγραφή
        ctk.CTkLabel(main_frame, text="📝 Περιγραφή:", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(10, 5))
        desc_frame = ctk.CTkFrame(main_frame, corner_radius=10, border_width=1, border_color="gray")
        desc_frame.pack(fill=tk.X, pady=(0, 10))
        
        desc_label = ctk.CTkLabel(desc_frame, text=step.step_text, font=("Segoe UI", 14), 
                                  wraplength=540, justify=tk.LEFT, anchor="nw")
        desc_label.pack(padx=10, pady=10)
        
        # Υλικά βήματος
        ctk.CTkLabel(main_frame, text="🥕 Υλικά Βήματος:", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(10, 5))
        
        allocs = getattr(step, 'allocations', getattr(step, 'step_ingredients', []))
        
        if allocs:
            ing_frame = ctk.CTkFrame(main_frame, corner_radius=10, border_width=1, border_color="gray")
            ing_frame.pack(fill=tk.X, pady=(0, 10))
            
            for a in allocs:
                name = get_alloc_val(a, 'ingredient_name', '')
                qty = get_alloc_val(a, 'quantity', '')
                unit = get_alloc_val(a, 'unit', '')
                notes = get_alloc_val(a, 'notes', '')
                
                prep_text = " (Στάδιο Προετοιμασίας)" if notes == "Στάδιο Προετοιμασίας" else ""
                ing_text = f"• {qty} {unit} {name}{prep_text}"
                ctk.CTkLabel(ing_frame, text=ing_text, font=("Segoe UI", 13), anchor="w").pack(fill=tk.X, padx=10, pady=5)
        else:
            ctk.CTkLabel(main_frame, text="Δεν υπάρχουν υλικά για αυτό το βήμα", 
                        font=("Segoe UI", 13), text_color="gray").pack(anchor="w")
        
        # Κουμπί κλεισίματος
        ctk.CTkButton(view_window, text="Κλείσιμο", command=view_window.destroy,
                     fg_color="#1f538d", hover_color="#2a72c1", cursor="hand2",
                     width=150, height=40).pack(pady=20)
        
    def on_step_select(self, event):
        """Ενεργοποιεί τα κουμπιά βημάτων όταν επιλέγεται ένα βήμα"""
        if self.ingredients_locked and self.steps_tree.selection():
            self.view_step_btn.configure(state=tk.NORMAL)
            self.edit_step_btn.configure(state=tk.NORMAL)
            self.del_step_btn.configure(state=tk.NORMAL)
        elif not self.steps_tree.selection():
            self.view_step_btn.configure(state=tk.DISABLED)
            self.edit_step_btn.configure(state=tk.DISABLED)
            self.del_step_btn.configure(state=tk.DISABLED)
        
    def refresh_categories_list(self):
        all_cats = DatabaseConn.get_all_categories()
        if not all_cats:
            all_cats = ["Ορεκτικά","Σαλάτες","Σούπες","Κυρίως Πιάτα","Ζυμαρικά","Ρύζι","Λαδερά","Φαγητά φούρνου","Ψητά","Τηγανητά",
                        "Μαγειρευτά","Κρεατικά","Κοτόπουλο","Ψάρια & Θαλασσινά","Χορτοφαγικά","Vegetarian","Vegan","Πίτες","Αλμυρές πίτες","Γλυκές πίτες",
                        "Αρτοσκευάσματα","Ψωμιά","Πρωινό","Σνακ","Γλυκά","Επιδόρπια","Παγωτά","Ροφήματα","Ποτά","Σάλτσες","Ντιπ","Μαρμελάδες & Γλυκά κουταλιού",
                        "Κονσέρβες","Ζυμωτά","Παραδοσιακά","Νηστίσιμα","Κατοικίδιων"]
        all_cats = sorted(all_cats, key=greek_sort_key)
        # Η λίστα ανανεώνεται όταν ανοίγει το παράθυρο, οπότε δεν χρειάζεται άλλο

    def manage_categories_dialog(self):
        """Ανοίγει παράθυρο διαχείρισης κατηγοριών"""
        d = ctk.CTkToplevel(self.window)
        d.title("Διαχείριση Κατηγοριών")
        center_and_size_window(d, 500, 450)
        set_window_icon(d)
        d.grab_set()
        
        categories = DatabaseConn.get_all_categories()
        categories = sorted(categories, key=greek_sort_key)
        
        # Πλαίσιο για τη λίστα και τα κουμπιά
        main_frame = ctk.CTkFrame(d)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Ετικέτα
        ctk.CTkLabel(main_frame, text="Λίστα Κατηγοριών", font=("Segoe UI", 16, "bold")).pack(pady=(0, 10))
        
        # Scrollable listbox
        list_frame = ctk.CTkFrame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Δημιουργία Listbox με scrollbar - σωστά χρώματα ανάλογα με το θέμα
        listbox_frame = tk.Frame(list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Παίρνουμε το τρέχον θέμα ΑΜΕΣΑ από το ctk
        current_theme = ctk.get_appearance_mode()

        if current_theme == "Dark":
            bg_color = "#2b2b2b"
            fg_color = "white"
        else:
            bg_color = "#ffffff"
            fg_color = "black"

        
        listbox = tk.Listbox(listbox_frame, font=("Segoe UI", 13), bg=bg_color, fg=fg_color,
                            selectbackground='#1f538d', selectforeground='white',
                            yscrollcommand=scrollbar.set, bd=1, relief="solid", highlightthickness=0)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Προσθήκη κατηγοριών στη λίστα
        for cat in categories:
            listbox.insert(tk.END, cat)
        
        # Πλαίσιο για προσθήκη νέας κατηγορίας
        add_frame = ctk.CTkFrame(main_frame)
        add_frame.pack(fill=tk.X, pady=15)
        
        new_cat_entry = ctk.CTkEntry(add_frame, placeholder_text="Νέα κατηγορία...", font=("Segoe UI", 14), width=250)
        new_cat_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        def add_category():
            new_cat = new_cat_entry.get().strip()
            if not new_cat:
                messagebox.showwarning("Προσοχή", "Παρακαλώ εισάγετε μια κατηγορία.")
                return
            
            if DatabaseConn.add_category(new_cat):
                current_items = list(listbox.get(0, tk.END))
                current_items.append(new_cat)
                current_items.sort(key=greek_sort_key)
                
                listbox.delete(0, tk.END)
                for item in current_items:
                    listbox.insert(tk.END, item)
                
                new_cat_entry.delete(0, tk.END)
                self.refresh_categories_list()
                messagebox.showinfo("Επιτυχία", f"Η κατηγορία '{new_cat}' προστέθηκε!")
            else:
                messagebox.showerror("Σφάλμα", "Η κατηγορία υπάρχει ήδη")
        
        ctk.CTkButton(add_frame, text="➕ Προσθήκη", command=add_category, 
                      cursor="hand2", width=100, fg_color="#28a745", hover_color="#218838").pack(side=tk.RIGHT)
        
        # Πλαίσιο για διαγραφή
        delete_frame = ctk.CTkFrame(main_frame)
        delete_frame.pack(fill=tk.X, pady=5)
        
        def delete_category():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Προσοχή", "Επιλέξτε μια κατηγορία για διαγραφή.")
                return
            
            cat_name = listbox.get(selection[0])
            
            if not messagebox.askyesno("Επιβεβαίωση", f"Θέλετε να διαγράψετε την κατηγορία '{cat_name}';"):
                return
            
            if DatabaseConn.delete_category(cat_name):
                listbox.delete(selection[0])
                self.refresh_categories_list()
                if self.category_entry.get() == cat_name:
                    self.category_entry.delete(0, tk.END)
                    self.category_entry.insert(0, "Επιλέξτε ή πληκτρολογήστε...")
                messagebox.showinfo("Επιτυχία", f"Η κατηγορία '{cat_name}' διαγράφηκε!")
            else:
                messagebox.showerror("Σφάλμα", "Δεν μπορείτε να διαγράψετε κατηγορία που χρησιμοποιείται σε συνταγές")
        
        ctk.CTkButton(delete_frame, text="❌ Διαγραφή Επιλεγμένης", command=delete_category, 
                      fg_color="#8b0000", hover_color="#ff1a1a", cursor="hand2", width=200).pack()
        
        # Επιτρέπει στο Enter να προσθέτει την κατηγορία
        new_cat_entry.bind('<Return>', lambda e: add_category())
        
        # Κουμπί κλεισίματος
        ctk.CTkButton(main_frame, text="Κλείσιμο", command=d.destroy, 
                     fg_color="#1f538d", hover_color="#2a72c1", cursor="hand2", width=150).pack(pady=15)
        
    def manage_ingredients_dialog(self):
        d = ctk.CTkToplevel(self.window)
        d.title("Διαχείριση Υλικών")
        center_and_size_window(d, 500, 450)
        set_window_icon(d)
        d.grab_set()
        
        ingredients = DatabaseConn.get_all_ingredients()
        
        list_frame = ctk.CTkFrame(d)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree_frame = ctk.CTkFrame(list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        tree = ttk.Treeview(tree_frame, columns=('Υλικό',), show='headings', height=10)
        tree.heading('Υλικό', text='Υλικά')
        tree.column('Υλικό', width=400, anchor='center')
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scroll.set)
        
        for i, ing in enumerate(sorted(ingredients, key=greek_sort_key)):
            tag = 'even' if i % 2 == 0 else 'odd'
            tree.insert('', 'end', values=(ing,), tags=(tag,))
        
        if ctk.get_appearance_mode() == "Dark":
            tree.tag_configure('even', background='#2a2d2e')
            tree.tag_configure('odd', background='#343638')
        else:
            tree.tag_configure('even', background='#f2f2f2')
            tree.tag_configure('odd', background='#ffffff')
        
        entry_frame = ctk.CTkFrame(d)
        entry_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ing_entry = ctk.CTkEntry(entry_frame, placeholder_text="Νέο υλικό...", font=("Segoe UI", 14))
        ing_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        def add_ingredient():
            new_ing = ing_entry.get().strip()
            if new_ing:
                if DatabaseConn.add_ingredient(new_ing):
                    current_items = [tree.item(item)['values'][0] for item in tree.get_children()]
                    current_items.append(new_ing)
                    current_items.sort(key=greek_sort_key)
                    
                    for item in tree.get_children():
                        tree.delete(item)
                    for i, ing in enumerate(current_items):
                        tag = 'even' if i % 2 == 0 else 'odd'
                        tree.insert('', 'end', values=(ing,), tags=(tag,))
                    
                    ing_entry.delete(0, tk.END)
                    messagebox.showinfo("Επιτυχία", f"Το υλικό '{new_ing}' προστέθηκε!")
                else:
                    messagebox.showerror("Σφάλμα", "Το υλικό υπάρχει ήδη")
        
        def delete_ingredient():
            selection = tree.selection()
            if selection:
                ing_name = tree.item(selection[0])['values'][0]
                if messagebox.askyesno("Επιβεβαίωση", f"Θέλετε να διαγράψετε το υλικό '{ing_name}';"):
                    if DatabaseConn.delete_ingredient(ing_name):
                        tree.delete(selection[0])
                        messagebox.showinfo("Επιτυχία", f"Το υλικό '{ing_name}' διαγράφηκε!")
                    else:
                        messagebox.showerror("Σφάλμα", "Δεν μπορείτε να διαγράψετε υλικό που χρησιμοποιείται σε συνταγές")
        
        button_frame = ctk.CTkFrame(d)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkButton(button_frame, text="➕ Προσθήκη", command=add_ingredient, 
                      cursor="hand2", width=120).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(button_frame, text="❌ Διαγραφή", command=delete_ingredient, 
                      fg_color="#8b0000", hover_color="#ff1a1a", cursor="hand2", width=120).pack(side=tk.LEFT, padx=5)
        
        ing_entry.bind('<Return>', lambda e: add_ingredient())

    # --- ΜΕΘΟΔΟΙ ΑΠΟΘΗΚΕΥΣΗΣ ---
    def save_recipe(self):
        name = self.name_entry.get().strip()
        if not name: 
            return messagebox.showerror("Σφάλμα", "Το όνομα της συνταγής είναι υποχρεωτικό.")
        
        # Έλεγχος κατηγορίας
        cat_val = self.category_entry.get().strip()
        if not cat_val or cat_val.startswith("Επιλέξτε"):
            return messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε ή πληκτρολογήστε μια κατηγορία.")
        
        # Έλεγχος δυσκολίας
        difficulty = self.difficulty_combo.get()
        if not difficulty:
            return messagebox.showerror("Σφάλμα", "Παρακαλώ επιλέξτε επίπεδο δυσκολίας.")
        
        # Έλεγχος χρόνου
        time_str = self.total_time_entry.get().strip()
        if not time_str:
            return messagebox.showerror("Σφάλμα", "Παρακαλώ εισάγετε τον συνολικό χρόνο παρασκευής.")
        
        try:
            t = int(float(time_str.replace(',', '.')))
            if t <= 0:
                return messagebox.showerror("Σφάλμα", "Ο χρόνος πρέπει να είναι θετικός αριθμός.")
        except ValueError:
            return messagebox.showerror("Σφάλμα", "Εισάγετε έγκυρο αριθμό στο πεδίο χρόνου.")
        
        # Έλεγχος υλικών
        if not self.ingredients:
            return messagebox.showerror("Σφάλμα", "Προσθέστε τουλάχιστον ένα υλικό στη συνταγή.")
        
        # Έλεγχος βημάτων
        if not self.steps:
            return messagebox.showerror("Σφάλμα", "Προσθέστε τουλάχιστον ένα βήμα εκτέλεσης.")
        
        # Έλεγχος ότι τα υλικά έχουν επιβεβαιωθεί (κλειδωθεί)
        if not self.ingredients_locked:
            return messagebox.showerror("Σφάλμα", "Παρακαλώ επιβεβαιώστε τα υλικά πατώντας '✓ Επιβεβαίωση Υλικών'.")
        
        try:
            rec = Recipe(id=self.recipe_id, name=name, difficulty=difficulty, total_time_minutes=t)
            rec.category_id = Category.get_or_create(cat_val)
            
            # Handle image - ONLY ONCE!
            if getattr(self, 'selected_image_path', None) and self.selected_image_path != "DELETED":
                clean_name = os.path.basename(self.selected_image_path).replace("temp_preview_", "").replace("temp_", "")
                final_path = os.path.join(IMG_FOLDER, f"{int(datetime.datetime.now().timestamp())}_{clean_name}")
                
                if os.path.exists(self.selected_image_path):
                    shutil.copy(self.selected_image_path, final_path)
                    try: 
                        os.remove(self.selected_image_path)
                    except Exception: 
                        pass
                    
                rec.image_id = ImageModel.save_image(final_path)
                rec.image_path = final_path  # Store path for display
                
            elif getattr(self, 'selected_image_path', None) == "DELETED" and self.recipe_id:
                rec.image_id = None
                rec.image_path = None
            
            rec.ingredients = self.ingredients
            rec.steps = self.steps
            rec.save()

            messagebox.showinfo("Επιτυχία", f"Η συνταγή '{name}' αποθηκεύτηκε!")
            self.parent_app.load_recipes_from_db()
            self.window.destroy()
            
        except Exception as e: 
            messagebox.showerror("Σφάλμα Αποθήκευσης", f"Κάτι πήγε στραβά:\n{str(e)}")

    # --- ΜΕΘΟΔΟΙ ΔΙΑΧΕΙΡΙΣΗΣ ΣΥΣΤΑΤΙΚΩΝ & ΒΗΜΑΤΩΝ ---
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
        """Refresh the ingredients tree with even/odd coloring"""
        # Clear existing items
        for i in self.ing_tree.get_children(): 
            self.ing_tree.delete(i)
        
        # Configure tags for even/odd rows
        if ctk.get_appearance_mode() == "Dark":
            self.ing_tree.tag_configure('even', background='#2a2d2e')
            self.ing_tree.tag_configure('odd', background='#343638')
        else:
            self.ing_tree.tag_configure('even', background='#f2f2f2')
            self.ing_tree.tag_configure('odd', background='#ffffff')
        
        # Add ingredients with alternating colors
        for i, ing in enumerate(self.ingredients):
            tag = 'even' if i % 2 == 0 else 'odd'
            display_quantity = float_to_fraction(ing.quantity)
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
        
        # Μήνυμα επιβεβαίωσης
        result = messagebox.askyesno(
            "Επιβεβαίωση Υλικών", 
            f"Έχετε προσθέσει {len(self.ingredients)} υλικό/ά.\n\n"
            "Είστε σίγουροι ότι τα έχετε προσθέσει όλα;\n\n"
            "⚠️ ΣΗΜΑΝΤΙΚΟ: Μετά την επιβεβαίωση, δεν θα μπορείτε να προσθέσετε, να επεξεργαστείτε ή να διαγράψετε υλικά, "
            "εκτός αν πατήσετε το κουμπί 'Ξεκλείδωμα' (το οποίο θα διαγράψει τα βήματα που έχετε δημιουργήσει)."
        )
        if not result:
            return
        
        self.ingredients_locked = True
        
        # Ενεργοποίηση κουμπιών βημάτων
        self.add_step_btn.configure(state=tk.NORMAL)
        self.edit_step_btn.configure(state=tk.NORMAL)
        self.del_step_btn.configure(state=tk.NORMAL)
        self.view_step_btn.configure(state=tk.NORMAL)
        
        # Απενεργοποίηση κουμπιών υλικών
        self.add_ing_btn.configure(state=tk.DISABLED)
        self.edit_ing_btn.configure(state=tk.DISABLED)
        self.del_ing_btn.configure(state=tk.DISABLED)
        
        # Απενεργοποίηση του κουμπιού διαχείρισης υλικών
        if hasattr(self, 'manage_ing_btn'):
            self.manage_ing_btn.configure(state=tk.DISABLED)
        
        # Αλλαγή κατάστασης των κουμπιών επιβεβαίωσης
        self.confirm_btn.configure(state=tk.DISABLED, fg_color="gray")
        self.unlock_btn.configure(state=tk.NORMAL, fg_color="#e67e22")
        
        # Αλλαγή χρώματος της ετικέτας βημάτων
        if ctk.get_appearance_mode() == "Dark":
            self.steps_label.configure(text_color="white")
        else:
            self.steps_label.configure(text_color="#2b2b2b")

    def unlock_ingredients(self):
        if self.steps and not messagebox.askyesno("Προσοχή", "Το ξεκλείδωμα θα διαγράψει τα βήματα. Συνέχεια;"): 
            return
        self.steps = []
        self.refresh_steps_list()
        self.ingredients_locked = False
        
        # Απενεργοποίηση κουμπιών βημάτων
        self.add_step_btn.configure(state=tk.DISABLED)
        self.edit_step_btn.configure(state=tk.DISABLED)
        self.del_step_btn.configure(state=tk.DISABLED)
        self.view_step_btn.configure(state=tk.DISABLED)
        
        # Ενεργοποίηση κουμπιών υλικών
        self.add_ing_btn.configure(state=tk.NORMAL)
        self.edit_ing_btn.configure(state=tk.NORMAL)
        self.del_ing_btn.configure(state=tk.NORMAL)
        
        # Ενεργοποίηση του κουμπιού διαχείρισης υλικών (προσθήκη)
        if hasattr(self, 'manage_ing_btn'):
            self.manage_ing_btn.configure(state=tk.NORMAL)
        
        # Αλλαγή κατάστασης των κουμπιών επιβεβαίωσης
        self.confirm_btn.configure(state=tk.NORMAL, fg_color="#28a745")
        self.unlock_btn.configure(state=tk.DISABLED, fg_color="gray")
        
        # Αλλαγή χρώματος της ετικέτας βημάτων
        self.steps_label.configure(text_color="gray")

    def _prefill_data(self, rid):
        recipe = Recipe.get_recipe_by_id(rid)
        if not recipe:
            messagebox.showerror("Σφάλμα", "Δεν βρέθηκε η συνταγή")
            return
        
        # Fill basic info
        self.name_entry.insert(0, recipe.name)
        if recipe.category: 
            self.category_entry.delete(0, tk.END)
            self.category_entry.insert(0, recipe.category)
        else:
            self.category_entry.delete(0, tk.END)
            self.category_entry.insert(0, "Επιλέξτε ή πληκτρολογήστε...")
        
        self.difficulty_combo.set(recipe.difficulty or "Μέτρια")
        self.total_time_entry.insert(0, str(recipe.total_time_minutes))
        
        # Load ingredients
        self.ingredients = sorted(recipe.ingredients, key=lambda x: greek_sort_key(x.name))
        
        # Load steps
        self.steps = recipe.steps
        
        # Load image if exists
        if hasattr(recipe, 'image_path') and recipe.image_path and os.path.exists(recipe.image_path):
            self.selected_image_path = recipe.image_path
            self.update_image_preview(recipe.image_path)
        
        # Refresh displays
        self.refresh_ingredients_list()
        self.refresh_steps_list()
        
        # Auto-lock ingredients for existing recipes
        if self.ingredients:
            self.ingredients_locked = True
            self.add_step_btn.configure(state=tk.NORMAL)
            self.del_step_btn.configure(state=tk.NORMAL)
            self.edit_step_btn.configure(state=tk.NORMAL)
            self.view_step_btn.configure(state=tk.NORMAL)
            
            # Update label color based on theme
            if ctk.get_appearance_mode() == "Dark":
                self.steps_label.configure(text_color="white")
            else:
                self.steps_label.configure(text_color="#2b2b2b")
            
            self.confirm_btn.configure(state=tk.DISABLED, fg_color="gray")
            self.unlock_btn.configure(state=tk.NORMAL, fg_color="#e67e22")
            self.add_ing_btn.configure(state=tk.DISABLED)
            self.del_ing_btn.configure(state=tk.DISABLED)
            self.edit_ing_btn.configure(state=tk.DISABLED)
            
            # Disable manage ingredients button
            if hasattr(self, 'manage_ing_btn'):
                self.manage_ing_btn.configure(state=tk.DISABLED)


# =============================================================================
# --- 3. ΣΕΛΙΔΑ ΕΚΤΕΛΕΣΗΣ (KITCHEN MODE) ---
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
        center_and_size_window(self.window, 850, 750)
        set_window_icon(self.window)
        self.window.transient(parent)
        self.window.grab_set()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        # --- MAKE THE WHOLE WINDOW SCROLLABLE ---
        self.main_scroll = ctk.CTkScrollableFrame(self.window, fg_color="transparent")
        self.main_scroll.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        if getattr(self.recipe, 'image_path', None) and os.path.exists(self.recipe.image_path):
            try:
                img = ctk.CTkImage(Image.open(self.recipe.image_path), size=(200, 130))
                ctk.CTkLabel(self.main_scroll, text="", image=img).pack(pady=10)
            except: pass

        ctk.CTkLabel(self.main_scroll, text=self.recipe.name, font=("Segoe UI", 26, "bold"), text_color="#2a72c1").pack(pady=5)
        
        self.prog_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.prog_frame.pack(pady=5)
        self.prog_bar = ctk.CTkProgressBar(self.prog_frame, width=550)
        self.prog_bar.set(0)
        self.prog_bar.pack(side=tk.LEFT, padx=(0, 15))
        self.prog_pct_lbl = ctk.CTkLabel(self.prog_frame, text="0%", font=("Segoe UI", 16, "bold"))
        self.prog_pct_lbl.pack(side=tk.LEFT)

        self.step_frame = ctk.CTkFrame(self.main_scroll, corner_radius=15)
        self.step_frame.pack(fill=tk.BOTH, expand=True, pady=15)
        
        self.num_lbl = ctk.CTkLabel(self.step_frame, text="", font=("Segoe UI", 22, "bold"), text_color="#e67e22")
        self.num_lbl.pack(pady=10)
        self.title_lbl = ctk.CTkLabel(self.step_frame, text="", font=("Segoe UI", 20, "bold"))
        self.title_lbl.pack(pady=5)
        
        
                # Make description scrollable with scrollbar (only appears when needed)
        desc_frame = ctk.CTkFrame(self.step_frame, fg_color="transparent")
        desc_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        # Create Text widget with dynamic height based on content
        self.desc_text = tk.Text(desc_frame, font=("Segoe UI", 14), wrap=tk.WORD,
                                  relief="flat", padx=15, pady=15, height=10)
        
        # Set colors based on theme
        if ctk.get_appearance_mode() == "Dark":
            self.desc_text.configure(bg="#2b2b2b", fg="white")
        else:
            self.desc_text.configure(bg="#ffffff", fg="black")
        
        # Add scrollbar (only shows when needed)
        desc_scrollbar = tk.Scrollbar(desc_frame, orient="vertical", command=self.desc_text.yview)
        self.desc_text.configure(yscrollcommand=desc_scrollbar.set)
        
        # Pack widgets - the text widget will expand but scrollbar only shows when needed
        self.desc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure scrollbar to only appear when content exceeds height
        def update_scrollbar_visibility(event=None):
            """Show/hide scrollbar based on content height"""
            if self.desc_text.count("1.0", "end-1c", "lines")[0] > self.desc_text.cget("height"):
                desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            else:
                desc_scrollbar.pack_forget()
        
        # Bind to content changes and configure
        self.desc_text.bind("<<Modified>>", update_scrollbar_visibility)
        self.desc_text.bind("<Configure>", update_scrollbar_visibility)
        
        # Make it read-only
        self.desc_text.configure(state=tk.DISABLED)

        self.countdown_lbl = ctk.CTkLabel(self.step_frame, text="", font=("Consolas", 45, "bold"), text_color="#1f538d")
        self.countdown_lbl.pack(pady=10)

        btn_f = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        btn_f.pack(side=tk.BOTTOM, pady=20)
        
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
            sorted_ings = sorted(self.recipe.ingredients, key=lambda x: greek_sort_key(x.name))
            ings = "\n".join([f"• {float_to_fraction(i.quantity)} {i.unit or ''} {i.name}" for i in sorted_ings])
            self.desc_text.configure(state=tk.NORMAL)
            self.desc_text.delete("1.0", tk.END)
            self.desc_text.insert("1.0", f"Συγκεντρώστε στον πάγκο σας:\n\n{ings}")
            self.desc_text.configure(state=tk.DISABLED)
            self.desc_text.configure(height=min(15, self.desc_text.count("1.0", "end-1c", "lines")[0] + 2))
            
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
                    display_qty = float_to_fraction(qty) if isinstance(qty, (int, float)) else qty
                    ing_texts.append(f"• {display_qty} {unit} {name}{prep_mark}")
            
            ing_str = "\n".join(ing_texts)
            desc_text = s.step_text
            if ing_str: 
                desc_text += f"\n\nΥλικά Βήματος:\n{ing_str}"
            
            self.desc_text.configure(state=tk.NORMAL)
            self.desc_text.delete("1.0", tk.END)
            self.desc_text.insert("1.0", desc_text)
            self.desc_text.configure(state=tk.DISABLED)

            line_count = self.desc_text.count("1.0", "end-1c", "lines")[0]
            self.desc_text.configure(height=min(15, line_count + 2))
            
            total_steps = len(self.steps)
            progress = (self.current_index + 1) / total_steps if total_steps > 0 else 1
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
        self.window.transient(parent)
        self.window.grab_set()
        
        # Main container with scrollbar
        main_frame = ctk.CTkScrollableFrame(self.window, fg_color="transparent")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # --- HEADER ---
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Recipe name
        ctk.CTkLabel(header_frame, text=self.recipe.name, font=("Segoe UI", 28, "bold"), 
                    text_color="#2a72c1").pack(anchor="center", pady=(0, 10))
        
        # Recipe image (if exists)
        if getattr(self.recipe, 'image_path', None) and self.recipe.image_path and os.path.exists(self.recipe.image_path):
            try:
                img = ctk.CTkImage(Image.open(self.recipe.image_path), size=(200, 150))
                ctk.CTkLabel(header_frame, text="", image=img).pack(pady=5)
            except:
                pass
        
        # Basic info row
        info_row = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_row.pack(pady=10)
        
        # Category
        cat_frame = ctk.CTkFrame(info_row, corner_radius=10, border_width=1, border_color="#1f538d")
        cat_frame.pack(side=tk.LEFT, padx=10)
        ctk.CTkLabel(cat_frame, text=f"📁 {self.recipe.category or 'Χωρίς κατηγορία'}", 
                    font=("Segoe UI", 13)).pack(padx=15, pady=5)
        
        # Difficulty
        diff_colors = {"Εύκολη": "#28a745", "Μέτρια": "#ff9800", "Δύσκολη": "#f44336"}
        diff_color = diff_colors.get(self.recipe.difficulty, "#1f538d")
        diff_frame = ctk.CTkFrame(info_row, corner_radius=10, border_width=1, border_color=diff_color)
        diff_frame.pack(side=tk.LEFT, padx=10)
        ctk.CTkLabel(diff_frame, text=f"⭐ {self.recipe.difficulty or 'Μέτρια'}", 
                    font=("Segoe UI", 13), text_color=diff_color).pack(padx=15, pady=5)
        
        # Time
        time_frame = ctk.CTkFrame(info_row, corner_radius=10, border_width=1, border_color="#1f538d")
        time_frame.pack(side=tk.LEFT, padx=10)
        ctk.CTkLabel(time_frame, text=f"⏱️ {self.recipe.total_time_minutes or 0} λεπτά", 
                    font=("Segoe UI", 13)).pack(padx=15, pady=5)
        
        # --- INGREDIENTS SECTION ---
        ingredients_frame = ctk.CTkFrame(main_frame)
        ingredients_frame.pack(fill=tk.X, pady=(0, 20))
        
        ctk.CTkLabel(ingredients_frame, text="📝 Συστατικά", font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Ingredients grid
        ing_grid = ctk.CTkFrame(ingredients_frame, fg_color="transparent")
        ing_grid.pack(fill=tk.X)
        
        # Header
        ctk.CTkLabel(ing_grid, text="Όνομα", font=("Segoe UI", 14, "bold"), width=250, anchor="w").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(ing_grid, text="Ποσότητα", font=("Segoe UI", 14, "bold"), width=100, anchor="w").grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(ing_grid, text="Μονάδα", font=("Segoe UI", 14, "bold"), width=100, anchor="w").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(ing_grid, text="Σημειώσεις", font=("Segoe UI", 14, "bold"), width=200, anchor="w").grid(row=0, column=3, padx=10, pady=5, sticky="w")
        
        ctk.CTkFrame(ing_grid, height=2, fg_color="gray").grid(row=1, column=0, columnspan=4, sticky="ew", padx=10, pady=5)
        
        row = 2
        for ing in sorted(self.recipe.ingredients, key=lambda x: greek_sort_key(x.name)):
            ctk.CTkLabel(ing_grid, text=ing.name, anchor="w", font=("Segoe UI", 13)).grid(row=row, column=0, padx=10, pady=3, sticky="w")
            display_quantity = float_to_fraction(ing.quantity)
            ctk.CTkLabel(ing_grid, text=display_quantity, anchor="w", font=("Segoe UI", 13)).grid(row=row, column=1, padx=10, pady=3, sticky="w")
            ctk.CTkLabel(ing_grid, text=ing.unit or "-", anchor="w", font=("Segoe UI", 13)).grid(row=row, column=2, padx=10, pady=3, sticky="w")
            ctk.CTkLabel(ing_grid, text=ing.notes or "-", anchor="w", font=("Segoe UI", 13)).grid(row=row, column=3, padx=10, pady=3, sticky="w")
            row += 1
        
        # --- STEPS SECTION ---
        steps_frame = ctk.CTkFrame(main_frame)
        steps_frame.pack(fill=tk.BOTH, expand=True)
        
        ctk.CTkLabel(steps_frame, text="👨‍🍳 Βήματα Εκτέλεσης", font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0, 10))
        
        for idx, step in enumerate(self.recipe.steps, 1):
            step_card = ctk.CTkFrame(steps_frame, corner_radius=10, border_width=1, border_color="#3a7ebf")
            step_card.pack(fill=tk.X, pady=10)
            
            # Step header
            step_header = ctk.CTkFrame(step_card, fg_color="transparent")
            step_header.pack(fill=tk.X, padx=15, pady=10)
            
            ctk.CTkLabel(step_header, text=f"Βήμα {idx}: {step.step_name}", 
                        font=("Segoe UI", 16, "bold"), text_color="#2a72c1").pack(side=tk.LEFT)
            
            if step.duration_in_minutes > 0:
                ctk.CTkLabel(step_header, text=f"⏱️ {step.duration_in_minutes} λεπτά", 
                            font=("Segoe UI", 13), text_color="gray").pack(side=tk.RIGHT)
            
            # Step description
            if step.step_text:
                desc_frame = ctk.CTkFrame(step_card, fg_color="transparent")
                desc_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
                ctk.CTkLabel(desc_frame, text=step.step_text, font=("Segoe UI", 13), 
                            wraplength=800, justify=tk.LEFT, anchor="w").pack(anchor="w")
            
            # Step ingredients
            allocs = getattr(step, 'allocations', getattr(step, 'step_ingredients', []))
            if allocs:
                ing_frame = ctk.CTkFrame(step_card, fg_color="transparent")
                ing_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
                
                ctk.CTkLabel(ing_frame, text="Υλικά βήματος:", font=("Segoe UI", 13, "bold")).pack(anchor="w")
                
                ing_list_frame = ctk.CTkFrame(ing_frame, fg_color="transparent")
                ing_list_frame.pack(anchor="w", padx=20)
                
                for a in allocs:
                    name = get_alloc_val(a, 'ingredient_name', '')
                    qty = get_alloc_val(a, 'quantity', '')
                    unit = get_alloc_val(a, 'unit', '')
                    notes = get_alloc_val(a, 'notes', '')
                    
                    prep_mark = " (Προετοιμασία)" if notes == "Στάδιο Προετοιμασίας" else ""
                    ing_text = f"• {qty} {unit} {name}{prep_mark}"
                    ctk.CTkLabel(ing_list_frame, text=ing_text, font=("Segoe UI", 12)).pack(anchor="w")
        
        # --- CLOSE BUTTON ---
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
        
        self.current_theme_setting = "Dark" 
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
        self.search_ent = ctk.CTkEntry(search_f, placeholder_text="Όνομα, Χρόνος...", height=40, font=("Segoe UI", 14))
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
        self.dragged_item = None
        self.table.bind("<ButtonPress-1>", self.on_drag_start)
        self.table.bind("<ButtonRelease-1>", self.on_drag_drop)
        self.table.bind("<Motion>", self.on_tree_motion)

        self.apply_theme()
        self.load_recipes_from_db()

    def _build_menu_bar(self):
        """Build the application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Style for dropdowns
        menu_kwargs = dict(
            tearoff=0,
            font=("Segoe UI", 11),
            bg="#2a2d2e",
            fg="white",
            activebackground="#1f538d",
            activeforeground="white",
        )

        # --- Dropdown: Actions (all sidebar buttons) ---
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

        # --- Dropdown: Theme (mirrors CTkOptionMenu) ---
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
        """Sync the CTkOptionMenu in sidebar when theme changes from menu bar"""
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
    
    # --- ΜΗΧΑΝΙΣΜΟΣ DRAG & DROP ---
    def on_drag_start(self, event):
        """Αποθηκεύει τη γραμμή που μόλις πιάσαμε με το κλικ"""
        row = self.table.identify_row(event.y)
        if row:
            self.dragged_item = row

    def on_drag_drop(self, event):
        """Όταν αφήνουμε το κλικ, μετακινεί τη γραμμή στη νέα θέση"""
        if not getattr(self, 'dragged_item', None): return
        
        target_row = self.table.identify_row(event.y)
        if target_row and target_row != self.dragged_item:
            # Βρίσκουμε τη νέα θέση και μετακινούμε τη γραμμή
            target_index = self.table.index(target_row)
            self.table.move(self.dragged_item, '', target_index)
            
            # Διορθώνουμε την αρίθμηση (Α/Α) και τα χρώματα
            self.recalculate_table_order()
            
        self.dragged_item = None

    def on_tree_motion(self, event):
        """Εμφανίζει το 'χεράκι' ΜΟΝΟ όταν το ποντίκι είναι πάνω από συνταγή"""
        row = self.table.identify_row(event.y)
        if row:
            self.table.configure(cursor="hand2")
        else:
            self.table.configure(cursor="")    

    def recalculate_table_order(self):
        """Ενημερώνει τον αριθμό Α/Α και τη διχρωμία (γκρι-λευκό) μετά το σύρσιμο"""
        for index, item in enumerate(self.table.get_children()):
            # Ενημέρωση της στήλης Α/Α (index + 1)
            current_values = list(self.table.item(item, 'values'))
            current_values[0] = str(index + 1)
            self.table.item(item, values=current_values)
            
            # Ενημέρωση των χρωμάτων (odd/even) για να μη χαλάσει το μοτίβο
            current_tags = list(self.table.item(item, 'tags'))
            new_tags = [t for t in current_tags if t not in ('odd', 'even')]
            new_tags.append('even' if index % 2 == 0 else 'odd')
            self.table.item(item, tags=new_tags)
    
    def manage_categories(self):
        """Ανοίγει παράθυρο διαχείρισης κατηγοριών"""
        d = ctk.CTkToplevel(self.root)
        d.title("Διαχείριση Κατηγοριών")
        center_and_size_window(d, 500, 400)
        set_window_icon(d)
        
        # Φόρτωση υπαρχουσών κατηγοριών
        categories = DatabaseConn.get_all_categories()
        
        # Λίστα κατηγοριών
        list_frame = ctk.CTkFrame(d)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(list_frame, columns=('Κατηγορία',), show='headings', height=10)
        tree.heading('Κατηγορία', text='Κατηγορίες')
        tree.column('Κατηγορία', width=400, anchor='center')
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scroll.set)
        
        # Προσθήκη κατηγοριών στη λίστα
        for cat in categories:
            tree.insert('', 'end', values=(cat,))
        
        # Πλαίσιο εισαγωγής νέας κατηγορίας
        entry_frame = ctk.CTkFrame(d)
        entry_frame.pack(fill=tk.X, padx=10, pady=10)
        
        cat_entry = ctk.CTkEntry(entry_frame, placeholder_text="Νέα κατηγορία...", font=("Segoe UI", 14))
        cat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    
        def add_category():
            new_cat = cat_entry.get().strip()
            if new_cat:
                if DatabaseConn.add_category(new_cat):
                    tree.insert('', 'end', values=(new_cat,))
                    cat_entry.delete(0, tk.END)
                    messagebox.showinfo("Επιτυχία", f"Η κατηγορία '{new_cat}' προστέθηκε!")
                else:
                    messagebox.showerror("Σφάλμα", "Η κατηγορία υπάρχει ήδη")
        
        def delete_category():
            selection = tree.selection()
            if selection:
                cat_name = tree.item(selection[0])['values'][0]
                if DatabaseConn.delete_category(cat_name):
                    tree.delete(selection[0])
                    messagebox.showinfo("Επιτυχία", f"Η κατηγορία '{cat_name}' διαγράφηκε!")
                else:
                    messagebox.showerror("Σφάλμα", "Δεν μπορείτε να διαγράψετε κατηγορία που χρησιμοποιείται σε συνταγές")
        
        ctk.CTkButton(entry_frame, text="➕ Προσθήκη", command=add_category, cursor="hand2", width=100).pack(side=tk.RIGHT, padx=5)
        ctk.CTkButton(d, text="❌ Διαγραφή Επιλεγμένης", command=delete_category, fg_color="#8b0000", cursor="hand2").pack(pady=10)

    def manage_ingredients(self):
        """Ανοίγει παράθυρο διαχείρισης υλικών"""
        d = ctk.CTkToplevel(self.root)
        d.title("Διαχείριση Υλικών")
        center_and_size_window(d, 500, 400)
        set_window_icon(d)
        
        # Φόρτωση υπαρχόντων υλικών
        ingredients = DatabaseConn.get_all_ingredients()
        
        # Λίστα υλικών
        list_frame = ctk.CTkFrame(d)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(list_frame, columns=('Υλικό',), show='headings', height=10)
        tree.heading('Υλικό', text='Υλικά')
        tree.column('Υλικό', width=400, anchor='center')
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scroll.set)
        
        # Προσθήκη υλικών στη λίστα
        for ing in ingredients:
            tree.insert('', 'end', values=(ing,))
        
        # Πλαίσιο εισαγωγής νέου υλικού
        entry_frame = ctk.CTkFrame(d)
        entry_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ing_entry = ctk.CTkEntry(entry_frame, placeholder_text="Νέο υλικό...", font=("Segoe UI", 14))
        ing_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    
        def add_ingredient():
            new_ing = ing_entry.get().strip()
            if new_ing:
                if DatabaseConn.add_ingredient(new_ing):
                    tree.insert('', 'end', values=(new_ing,))
                    ing_entry.delete(0, tk.END)
                    messagebox.showinfo("Επιτυχία", f"Το υλικό '{new_ing}' προστέθηκε!")
                else:
                    messagebox.showerror("Σφάλμα", "Το υλικό υπάρχει ήδη")
        
        def delete_ingredient():
            selection = tree.selection()
            if selection:
                ing_name = tree.item(selection[0])['values'][0]
                if DatabaseConn.delete_ingredient(ing_name):
                    tree.delete(selection[0])
                    messagebox.showinfo("Επιτυχία", f"Το υλικό '{ing_name}' διαγράφηκε!")
                else:
                    messagebox.showerror("Σφάλμα", "Δεν μπορείτε να διαγράψετε υλικό που χρησιμοποιείται σε συνταγές")
        
        ctk.CTkButton(entry_frame, text="➕ Προσθήκη", command=add_ingredient, cursor="hand2", width=100).pack(side=tk.RIGHT, padx=5)
        ctk.CTkButton(d, text="❌ Διαγραφή Επιλεγμένου", command=delete_ingredient, fg_color="#8b0000", cursor="hand2").pack(pady=10)

    def load_recipes_from_db(self):
        self.master_recipe_list = Recipe.get_all_recipes()
        self.perform_search()

    def perform_search(self, event=None):
        q = self.search_ent.get().lower().strip()
        for i in self.table.get_children(): 
            self.table.delete(i)
        
        results = []
        for index, r in enumerate(self.master_recipe_list):
            aa = str(index + 1)
            
            # 1. Έλεγχος από την κεντρική μπάρα αναζήτησης
            match_text = (not q) or (q == aa or q in str(r[0]) or q in r[1].lower() or (r[2] and q in r[2].lower()) or (r[3] and q in r[3].lower()) or (r[4] and q in str(r[4])))
            
            # 2. Έλεγχος από τα προηγμένα φίλτρα (Κατηγορία, Δυσκολία, Χρόνος)
            match_cat = (self.current_filter_category == "Όλες οι Κατηγορίες") or (r[2] == self.current_filter_category)
            match_diff = (self.current_filter_difficulty == "Όλες") or (r[3] == self.current_filter_difficulty)
            
            t = r[4] or 0
            if self.current_filter_time == "Έως 15 λεπτά": match_time = t <= 15
            elif self.current_filter_time == "Έως 30 λεπτά": match_time = t <= 30
            elif self.current_filter_time == "Έως 60 λεπτά": match_time = t <= 60
            elif self.current_filter_time == "Πάνω από 60 λεπτά": match_time = t > 60
            else: match_time = True
            
            # 3. ΕΙΔΙΚΟΣ Έλεγχος από τα ΝΕΑ φίλτρα (Α/Α και Όνομα)
            match_aa = (not self.current_filter_aa) or (self.current_filter_aa == aa)
            match_name_filter = (not self.current_filter_name) or (self.current_filter_name.lower() in r[1].lower())
            
            # Αν περνάει όλα τα ενεργά φίλτρα, το δείχνουμε!
            if match_text and match_cat and match_diff and match_time and match_aa and match_name_filter: 
                results.append((aa, r))
        
        cats_for_stats = []
        for i, (aa, r) in enumerate(results): 
            tag = (str(r[0]), 'even' if i % 2 == 0 else 'odd', r[3])
            self.table.insert('', 'end', values=(aa, r[1], r[2] or "", r[3], f"{r[4]} λεπτά"), tags=tag)
            if r[2]: 
                cats_for_stats.append(r[2])
            
        self.card_total.configure(text=str(len(results)))
        
        # Λογική για τη δημοφιλέστερη κατηγορία
        if cats_for_stats:
            freq = {}
            for cat in cats_for_stats:
                freq[cat] = freq.get(cat, 0) + 1
            
            max_count = max(freq.values())
            most_popular = [cat for cat, count in freq.items() if count == max_count]
            
            if len(most_popular) == 1:
                self.card_pop.configure(text=most_popular[0])
            else:
                self.card_pop.configure(text="Δεν υπάρχει")
        else: 
            self.card_pop.configure(text="-")

    def open_filters_dialog(self):
        d = ctk.CTkToplevel(self.root)
        d.title("Προηγμένα Φίλτρα Αναζήτησης")
        # Κάναμε το παράθυρο λίγο πιο ψηλό για να χωρέσουν όλα (450x650)
        center_and_size_window(d, 450, 650)
        set_window_icon(d)
        d.grab_set() 
        
        # Προσθέτουμε Scrollable Frame ώστε αν μικρύνει η οθόνη, να μη χαθούν τα κουμπιά
        scroll = ctk.CTkScrollableFrame(d, fg_color="transparent")
        scroll.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ΠΕΔΙΟ: Α/Α
        ctk.CTkLabel(scroll, text="Α/Α Συνταγής:", font=("Segoe UI", 14, "bold")).pack(pady=(10,5))
        aa_entry = ctk.CTkEntry(scroll, font=("Segoe UI", 14), width=250, placeholder_text="Αύξων Αριθμός Συνταγών...", 
                                fg_color="#1f538d", border_color="#1f538d", text_color="white", placeholder_text_color="#a0a0a0")
        aa_entry.pack(pady=5)
        aa_entry.insert(0, self.current_filter_aa)

        # ΠΕΔΙΟ: Όνομα Συνταγής
        ctk.CTkLabel(scroll, text="Όνομα Συνταγής:", font=("Segoe UI", 14, "bold")).pack(pady=(15,5))
        name_entry = ctk.CTkEntry(scroll, font=("Segoe UI", 14), width=250, placeholder_text="Όλες οι Συνταγές...", 
                                  fg_color="#1f538d", border_color="#1f538d", text_color="white", placeholder_text_color="#a0a0a0")
        name_entry.pack(pady=5)
        name_entry.insert(0, self.current_filter_name)

        # ΠΕΔΙΟ: Κατηγορία Συνταγής
        ctk.CTkLabel(scroll, text="Κατηγορία Συνταγής:", font=("Segoe UI", 14, "bold")).pack(pady=(15,5))
        filter_categories = ["Όλες οι Κατηγορίες"]
        filter_categories.extend(sorted(Category.get_all(), key=greek_sort_key))
        cat_combo = ctk.CTkOptionMenu(scroll, values=filter_categories, font=("Segoe UI", 14), width=250)
        cat_combo.pack(pady=5)
        cat_combo.set(self.current_filter_category)

        # ΠΕΔΙΟ: Επίπεδο Δυσκολίας
        ctk.CTkLabel(scroll, text="Επίπεδο Δυσκολίας:", font=("Segoe UI", 14, "bold")).pack(pady=(15,5))
        diff_combo = ctk.CTkOptionMenu(scroll, values=["Όλες", "Εύκολη", "Μέτρια", "Δύσκολη"], font=("Segoe UI", 14), width=250)
        diff_combo.pack(pady=5)
        diff_combo.set(self.current_filter_difficulty)

        # ΠΕΔΙΟ: Χρόνος Προετοιμασίας
        ctk.CTkLabel(scroll, text="Χρόνος Προετοιμασίας:", font=("Segoe UI", 14, "bold")).pack(pady=(15,5))
        time_combo = ctk.CTkOptionMenu(scroll, values=["Όλοι οι Χρόνοι", "Έως 15 λεπτά", "Έως 30 λεπτά", "Έως 60 λεπτά", "Πάνω από 60 λεπτά"], font=("Segoe UI", 14), width=250)
        time_combo.pack(pady=5)
        time_combo.set(self.current_filter_time)

        def apply_filters():
            self.current_filter_aa = aa_entry.get().strip()
            self.current_filter_name = name_entry.get().strip()
            self.current_filter_category = cat_combo.get()
            self.current_filter_difficulty = diff_combo.get()
            self.current_filter_time = time_combo.get()
            
            # Το κουμπί γίνεται Πορτοκαλί (Ενεργό) αν έστω και ΕΝΑ φίλτρο έχει χρησιμοποιηθεί
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
            cat_combo.set("Όλες οι Κατηγορίες")
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
            # Open read-only view
            RecipeViewPage(rid, self.root)
        else:
            # Open edit form
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
                    from fpdf import FPDF
                    
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    
                    # Load font from fonts folder
                    font_path = resource_path(os.path.join("fonts", "DejaVuSans.ttf"))
                    
                    if not os.path.exists(font_path):
                        font_path = resource_path(os.path.join("fonts", "OpenSans-Regular.ttf"))
                    
                    if os.path.exists(font_path):
                        pdf.add_font('GreekFont', '', font_path, uni=True)
                        pdf.add_font('GreekFont', 'B', font_path, uni=True)
                        pdf.add_font('GreekFont', 'I', font_path, uni=True)
                    else:
                        messagebox.showerror("Σφάλμα", "Δεν βρέθηκε γραμματοσειρά.")
                        return
                    
                    # Title
                    pdf.set_font('GreekFont', 'B', 20)
                    pdf.cell(0, 15, r.name, ln=True, align='C')
                    pdf.ln(5)
                    
                    # Basic info
                    pdf.set_font('GreekFont', '', 11)
                    info_text = f"Κατηγορία: {r.category or '-'}  |  Δυσκολία: {r.difficulty or '-'}  |  Χρόνος: {r.total_time_minutes or 0} λεπτά"
                    pdf.cell(0, 8, info_text, ln=True, align='C')
                    pdf.ln(10)
                    
                    # ========== INGREDIENTS ==========
                    pdf.set_font('GreekFont', 'B', 14)
                    pdf.cell(0, 10, "Υλικά:", ln=True)
                    pdf.set_font('GreekFont', '', 11)
                    
                    for ing in sorted(r.ingredients, key=lambda x: greek_sort_key(x.name)):
                        ing_text = f"• {ing.quantity} {ing.unit or ''} {ing.name}"
                        if ing.notes:
                            ing_text += f" ({ing.notes})"
                        pdf.set_x(10)  # Set left margin to 10
                        pdf.multi_cell(0, 6, ing_text)
                    
                    pdf.ln(5)
                    
                    # ========== STEPS ==========
                    pdf.set_font('GreekFont', 'B', 14)
                    pdf.cell(0, 10, "Βήματα Εκτέλεσης:", ln=True)
                    
                    for i, st in enumerate(r.steps, 1):
                        # Step title
                        pdf.set_font('GreekFont', 'B', 12)
                        step_title = f"{i}. {st.step_name}"
                        if st.duration_in_minutes > 0:
                            step_title += f" ({st.duration_in_minutes} λεπτά)"
                        pdf.cell(0, 8, step_title, ln=True)
                        
                        # Step description
                        if st.step_text:
                            pdf.set_font('GreekFont', '', 11)
                            pdf.set_x(15)  # Indent
                            pdf.multi_cell(0, 6, st.step_text)
                        
                        # Step ingredients
                        allocs = getattr(st, 'allocations', getattr(st, 'step_ingredients', []))
                        if allocs:
                            pdf.set_font('GreekFont', 'I', 10)
                            for a in allocs:
                                name = get_alloc_val(a, 'ingredient_name', '')
                                qty = get_alloc_val(a, 'quantity', '')
                                unit = get_alloc_val(a, 'unit', '')
                                notes = get_alloc_val(a, 'notes', '')
                                prep_mark = " (Προετοιμασία)" if notes == "Στάδιο Προετοιμασίας" else ""
                                pdf.set_x(20)  # Double indent
                                pdf.multi_cell(0, 5, f"• {qty} {unit} {name}{prep_mark}")
                        
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