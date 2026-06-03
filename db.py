import sqlite3
import os
from utils import get_app_root


# =============================================================================
# ΛΙΣΤΕΣ ΔΕΔΟΜΕΝΩΝ DROPDOWNS ΤΟΥ ΠΡΟΓΡΑΜΜΑΤΟΣ
# =============================================================================

INITIAL_CATEGORIES = [
    "Ορεκτικά", "Σαλάτες", "Σούπες", "Κυρίως Πιάτα", "Ζυμαρικά", "Ρύζι", "Λαδερά",
    "Φαγητά φούρνου", "Ψητά", "Τηγανητά", "Μαγειρευτά", "Κρεατικά", "Κοτόπουλο",
    "Ψάρια & Θαλασσινά", "Χορτοφαγικά", "Vegetarian", "Vegan", "Πίτες", "Αλμυρές πίτες",
    "Γλυκές πίτες", "Αρτοσκευάσματα", "Ψωμιά", "Πρωινό", "Σνακ", "Γλυκά", "Επιδόρπια",
    "Παγωτά", "Ροφήματα", "Ποτά", "Σάλτσες", "Ντιπ", "Μαρμελάδες & Γλυκά κουταλιού",
    "Κονσέρβες", "Ζυμωτά", "Παραδοσιακά", "Νηστίσιμα", "Κατοικίδιων"
]

INITIAL_INGREDIENTS = [
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

INITIAL_UNITS = [
    "kg", "g", "mg", "L", "ml", "κουταλιά/ες σούπας", "κουταλιά/ες γλυκού",
    "τεμάχιο/α", "κούπα/ες", "πρέζα/ες", "φλιτζάνι/α", "ποτήρι/α", "ματσάκι/α",
    "φέτα/ες", "ράβδος/οι", "συσκευασία/ες", "κουτί/α", "μπουκάλι/α", "σταγόνα/ες"
]

INITIAL_STEPS = [
    "Προετοιμασία", "Κόψιμο", "Σοτάρισμα", "Βράσιμο", 
    "Ψήσιμο", "Τηγάνισμα", "Ανάμειξη", "Μαρινάρισμα", "Σερβίρισμα"
]


class DatabaseConn:
    def __init__(self, db_name):
        self.db_path = os.path.join(get_app_root(), db_name)
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.cursor.execute("PRAGMA group_concat_max_len = 10000000")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type is None:
                self.conn.commit()
            self.conn.close()

    def execute(self, query, params=()):
        return self.cursor.execute(query, params)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()
    
    @staticmethod
    def initialize_database(db_name="recipe_database.db"):
        with DatabaseConn(db_name) as db:
            db.execute("CREATE TABLE IF NOT EXISTS categories_list(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
            db.execute("CREATE TABLE IF NOT EXISTS ingredient_list(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
            db.execute("CREATE TABLE IF NOT EXISTS unit_list(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)")
            db.execute("CREATE TABLE IF NOT EXISTS images(id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT UNIQUE)")
            
            db.execute("""
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    difficulty TEXT,
                    total_time_minutes INTEGER,
                    category_id INTEGER REFERENCES categories_list(id),
                    image_id INTEGER REFERENCES images(id)
                )
            """)
            
            db.execute("""
                CREATE TABLE IF NOT EXISTS ingredients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipe_id INTEGER REFERENCES recipes(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    quantity REAL,
                    unit TEXT,
                    notes TEXT
                )
            """)
            
            db.execute("""
                CREATE TABLE IF NOT EXISTS steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipe_id INTEGER REFERENCES recipes(id) ON DELETE CASCADE,
                    step_name TEXT,
                    step_text TEXT,
                    duration_in_minutes INTEGER,
                    sequence_order INTEGER
                )
            """)
            
            db.execute("""
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
            
            for cat in INITIAL_CATEGORIES:
                try:
                    db.execute("INSERT OR IGNORE INTO categories_list (name) VALUES (?)", (cat,))
                except:
                    pass
            
            
            for ing in INITIAL_INGREDIENTS:
                try:
                    db.execute("INSERT OR IGNORE INTO ingredient_list (name) VALUES (?)", (ing,))
                except:
                    pass

            
            for unit in INITIAL_UNITS:
                try:
                    db.execute("INSERT OR IGNORE INTO unit_list (name) VALUES (?)", (unit,))
                except:
                    pass