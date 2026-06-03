import os
import sys
import tkinter as tk
from fractions import Fraction
import customtkinter as ctk

# =============================================================================
# ΒΟΗΘΗΤΙΚΕΣ ΚΛΑΣΕΙΣ - COMPONENTS
# =============================================================================

class SelectableListDialog:
    def __init__(self, parent, title, items, on_select_callback, width=350, height=500):
        self.parent = parent
        self.title = title
        self.items = sorted(items, key=greek_sort_key)
        self.on_select_callback = on_select_callback
        self.width = width
        self.height = height
        self.dialog = None
        self.search_entry = None
        self.scroll_frame = None
        
    def show(self):
        if self.parent and self.parent.winfo_exists():
            self.parent.grab_release()
            
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title(self.title)
        center_and_size_window(self.dialog, self.width, self.height)
        set_window_icon(self.dialog)
        
        # 2. ΚΛΕΙΔΩΝΟΥΜΕ το τρέχον παραθυράκι της λίστας
        self.dialog.grab_set()
        self.dialog.focus_force()
        
        original_destroy = self.dialog.destroy
        def safe_close():
            original_destroy()
            if self.parent and self.parent.winfo_exists():
                self.parent.grab_set()
                
        self.dialog.destroy = safe_close
        self.dialog.protocol("WM_DELETE_WINDOW", safe_close)
        
        self.search_entry = ctk.CTkEntry(
            self.dialog, 
            placeholder_text="Αναζήτηση...", 
            font=("Segoe UI", 13)
        )
        self.search_entry.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.dialog, 
            width=self.width - 20,
            height=self.height - 120
        )
        self.scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 10))
        
        canvas = self.scroll_frame._parent_canvas
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 8)) * 3, "units")
            return "break"
        
        self.dialog.bind('<MouseWheel>', on_mousewheel)
        canvas.bind('<MouseWheel>', on_mousewheel)
        
        self._render_items()
        
        self.search_entry.bind('<KeyRelease>', lambda e: self._render_items())
        
        ctk.CTkButton(
            self.dialog, 
            text="Κλείσιμο", 
            command=self.dialog.destroy,
            fg_color="#8b0000", 
            hover_color="#ff1a1a",
            cursor="hand2",
            height=40
        ).pack(pady=(0, 10))
        
    def _render_items(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        
        filter_text = self.search_entry.get().strip().lower()
        
        MIN_SEARCH_CHARS = 2
        LARGE_LIST_THRESHOLD = 500
        
        if len(filter_text) < MIN_SEARCH_CHARS and len(self.items) > LARGE_LIST_THRESHOLD:
            info_label = ctk.CTkLabel(
                self.scroll_frame, 
                text=f"🔍 Πληκτρολογήστε τουλάχιστον {MIN_SEARCH_CHARS} χαρακτήρες για αναζήτηση\n(Σύνολο: {len(self.items)} items)",
                font=("Segoe UI", 13),
                text_color="orange"
            )
            info_label.pack(pady=20)
            return
        
        ft = greek_sort_key(filter_text) if filter_text else ""
        
        if not ft:
            filtered = self.items.copy()
        else:
            filtered = []
            for item in self.items:
                if ft in greek_sort_key(item):
                    filtered.append(item)
        
        filtered.sort(key=greek_sort_key)
        
        if not filtered:
            no_results_label = ctk.CTkLabel(
                self.scroll_frame, 
                text="😕 Δεν βρέθηκαν αποτελέσματα",
                font=("Segoe UI", 14),
                text_color="gray"
            )
            no_results_label.pack(pady=20)
            return
        
        if len(filtered) > 100:
            count_label = ctk.CTkLabel(
                self.scroll_frame,
                text=f"📋 {len(filtered)} αποτελέσματα",
                font=("Segoe UI", 11),
                text_color="gray"
            )
            count_label.pack(pady=(0, 5))
        
        MAX_VISIBLE = 200
        display_items = filtered[:MAX_VISIBLE] if len(filtered) > MAX_VISIBLE else filtered
        
        for item in display_items:
            btn = ctk.CTkButton(
                self.scroll_frame, 
                text=item, 
                command=lambda i=item: self._on_item_selected(i),
                font=("Segoe UI", 13), 
                height=35,
                fg_color=["#3a7ebf", "#1f538d"],
                hover_color=["#325882", "#14375e"],
                text_color="white",
                anchor="w", 
                cursor="hand2"
            )
            btn.pack(fill=tk.X, pady=2, padx=5)
        
        if len(filtered) > MAX_VISIBLE:
            truncate_label = ctk.CTkLabel(
                self.scroll_frame,
                text=f"⚠️ Εμφανίζονται {MAX_VISIBLE} από {len(filtered)} αποτελέσματα.\nΠληκτρολογήστε περισσότερους χαρακτήρες για καλύτερη αναζήτηση.",
                font=("Segoe UI", 10),
                text_color="orange"
            )
            truncate_label.pack(pady=5)
    
    def _on_item_selected(self, item):
        self.on_select_callback(item)
        self.dialog.destroy()


# =============================================================================
# REUSABLE TOOLTIP COMPONENT
# =============================================================================

class ToolTip:
    def __init__(self, widget, text, delay=500, bg_color=None, fg_color=None):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.tooltip_window = None
        self.after_id = None
        
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Motion>", self.on_motion)
    
    def on_enter(self, event=None):
        self.after_id = self.widget.after(self.delay, self.show_tooltip)
    
    def on_leave(self, event=None):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        self.hide_tooltip()
    
    def on_motion(self, event=None):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = self.widget.after(self.delay, self.show_tooltip)
    
    def show_tooltip(self):
        if self.tooltip_window:
            return
        
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 5
        y = self.widget.winfo_rooty()
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        if self.bg_color is None:
            current_theme = ctk.get_appearance_mode()
            if current_theme == "Dark":
                self.bg_color = "#3a3a3a"
                self.fg_color = "#ffffff"
            else:
                self.bg_color = "#ffffe0"
                self.fg_color = "#000000"
        
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            justify=tk.LEFT,
            background=self.bg_color,
            foreground=self.fg_color,
            relief=tk.SOLID,
            borderwidth=1,
            font=("Segoe UI", 10),
            padx=8,
            pady=4,
            wraplength=300
        )
        label.pack()
    
    def hide_tooltip(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


# =============================================================================
# ΒΟΗΘΗΤΙΚΕΣ ΣΥΝΑΡΤΗΣΕΙΣ
# =============================================================================

def get_app_root():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)



# =============================================================================
# ΣΥΝΑΡΤΗΣΗ ΠΡΟΣΑΡΜΟΓΗΣ ΠΑΡΑΘΥΡΟΥ ΣΤΟ ΚΕΝΤΡΟ ΚΑΙ ΟΡΙΣΜΑ ΜΕΓΕΘΟΥΣ ΠΑΡΑΘΥΡΟΥ
# =============================================================================

def center_and_size_window(window, desired_w, desired_h):
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    final_w = min(desired_w, int(screen_w * 0.95))
    final_h = min(desired_h, int(screen_h * 0.90))
    window.geometry(f"{final_w}x{final_h}")
    window.lift()
    window.focus_force()
    window.attributes("-topmost", True)
    window.after(500, lambda: window.attributes("-topmost", False))


def set_window_icon(window):
    try:
        icon_path = resource_path("chef.ico")
        
        if os.path.exists(icon_path):
            def apply_icon():
                try:
                    window.iconbitmap(icon_path)
                    
                    if window.__class__.__name__ == "CTk":
                        window.iconbitmap(default=icon_path)
                except Exception as e:
                    print(f"Σφάλμα κατά την τοποθέτηση του εικονιδίου: {e}")
                    
            window.after(200, apply_icon)
        else:
            print(f"ΠΡΟΣΟΧΗ: Το αρχείο chef.ico δεν βρέθηκε στη διαδρομή: {icon_path}")
    except Exception:
        pass

# =============================================================================
# ΔΙΑΧΕΙΡΙΣΗ ΤΑΧΥΤΗΤΑΣ ΜΠΑΡΑΣ ΚΥΛΙΣΜΑΤΟΣ ΣΕ TREEVIEW
# =============================================================================
def setup_treeview_scroll(treeview):
    def on_mousewheel(event):
        treeview.yview_scroll(int(-3 * (event.delta / 120)), "units")
        return "break"
    treeview.bind("<MouseWheel>", on_mousewheel)

# =============================================================================
# ΔΙΑΧΕΙΡΙΣΗ ΤΑΧΥΤΗΤΑΣ ΜΠΑΡΑΣ ΚΥΛΙΣΜΑΤΟΣ ΣΕ ΦΟΡΜΕΣ
# =============================================================================
def make_fast_scrollable(scrollable_frame, parent_window=None, speed=150):
    def fast_scroll(event):
        canvas = scrollable_frame._parent_canvas
        canvas.yview_scroll(int(-speed * (event.delta / 120)), "units")
        return "break"
    
    scrollable_frame._parent_canvas.bind("<MouseWheel>", fast_scroll)
    if parent_window:
        parent_window.bind("<MouseWheel>", fast_scroll)
    return fast_scroll



# =============================================================================
# ΔΙΑΧΕΙΡΙΣΗ ΕΛΛΗΝΙΚΩΝ ΧΑΡΑΚΤΗΡΩΝ ΓΙΑ ΜΗ ΠΡΟΒΛΗΜΑΤΙΚΗ ΚΑΤΑΧΩΡΗΣΗ ΣΤΗ ΒΑΣΗ
# =============================================================================

def greek_sort_key(text):
    if not isinstance(text, str):
        return ""
    replacements = {
        'ά': 'α', 'έ': 'ε', 'ή': 'η', 'ί': 'ι', 'ό': 'ο', 'ύ': 'υ', 'ώ': 'ω',
        'ϊ': 'ι', 'ϋ': 'υ', 'ΐ': 'ι', 'ΰ': 'υ'
    }
    text = text.lower().strip()
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


# =====================================================================================================
# ΣΥΝΑΡΤΗΣΗ ΜΕΤΑΤΡΟΠΗΣ ΚΛΑΣΜΑΤΩΝ ΣΕ ΠΡΑΓΜΑΤΙΚΟΥΣ ΑΡΙΘΜΟΥΣ ΓΙΑ ΕΝΑΡΜΟΝΙΣΗ ΜΕ ΠΙΝΑΚΑ ΒΑΣΗΣ ΔΕΔΟΜΕΝΩΝ
# =====================================================================================================

def format_quantity(value):
    if value is None:
        return ""
    try:
        frac = Fraction(str(value)).limit_denominator(100)
        if frac.denominator == 1:
            return str(frac.numerator)
        return str(frac)
    except:
        return str(value)

# =============================================================================
# ΜΕΝΟΥ (COPY/PASTE) ΜΕ ΔΕΞΙ ΚΛΙΚ
# =============================================================================

def enable_right_click_menu(widget):
    if hasattr(widget, '_textbox'):
        target = widget._textbox
    elif hasattr(widget, '_entry'):
        target = widget._entry
    else:
        target = widget

    menu = tk.Menu(target, tearoff=False, font=("Segoe UI", 11),
                   bg="#2a2d2e", fg="white", activebackground="#1f538d")

    def cut(event=None):
        try:
            target.event_generate("<<Cut>>")
        except:
            pass
        return "break"

    def copy(event=None):
        try:
            target.event_generate("<<Copy>>")
        except:
            pass
        return "break"

    def paste(event=None):
        try:
            target.event_generate("<<Paste>>")
        except:
            pass
        return "break"

    def select_all(event=None):
        try:
            if hasattr(target, 'tag_add'):
                target.tag_add("sel", "1.0", "end")
            else:
                target.select_range(0, "end")
                target.icursor("end")
        except:
            pass
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
        if event.state & 0x0004:  # Ctrl key
            if event.keycode == 88:
                return cut()
            elif event.keycode == 67:
                return copy()
            elif event.keycode == 86:
                return paste()
            elif event.keycode == 65:
                return select_all()

    target.bind("<Key>", handle_hardware_shortcuts)


# =============================================================================
# ΣΥΝΑΡΤΗΣΗ ΑΣΦΑΛΟΥΣ ΕΞΑΓΩΓΗΣ ΚΕΙΜΕΝΟΥ ΑΠΟ ΛΕΞΙΚΟ Η ΑΝΤΙΚΕΙΜΕΝΟ
# =============================================================================

def get_alloc_val(alloc, key, default=None):
    if isinstance(alloc, dict):
        return alloc.get(key, default)
    return getattr(alloc, key, default)

# =============================================================================
# ΣΥΝΑΡΤΗΣΗ ΠΟΥ ΚΑΝΕΙ ΕΝΑ ΠΛΑΙΣΙΟ ΚΕΙΜΕΝΟΥ READ-ONLY
# =============================================================================

def set_readonly_entry(entry, value):
    entry.configure(state="normal")
    entry.delete(0, tk.END)
    entry.insert(0, value)
    entry.configure(state="readonly")