import tkinter as tk
import db

# Συνάρτηση που καλείται όταν πατηθεί το κουμπί
def open_add_recipe(parent_window, on_close_callback):
    """
    Ανοίγει τη φόρμα προσθήκης ως popup πάνω στο κεντρικό παράθυρο.
    - parent_window: το κεντρικό παράθυρο (main_window)
    - on_close_callback: συνάρτηση που καλείται μετά το κλείσιμο
      ώστε να ανανεωθεί ο πίνακας αυτόματα
    """

    # Toplevel = νέο παράθυρο που "ανήκει" στο κεντρικό
    # (αντί για tk.Tk() που θα έφτιαχνε εντελώς ανεξάρτητο παράθυρο)
    popup = tk.Toplevel(parent_window)
    popup.title("Προσθήκη Συνταγής")
    popup.resizable(False, False)

    def on_save():
        name       = entry_name.get().strip()
        category   = entry_category.get().strip()

        try:
            difficulty = int(entry_difficulty.get())
            time_mins  = int(entry_time.get())
        except ValueError:
            tk.messagebox.showerror("Σφάλμα", "Η δυσκολία και ο χρόνος πρέπει να είναι αριθμοί!")
            return

        db.add_recipe(name, category, difficulty, time_mins)
        print(f"Αποθηκεύτηκε: {name}")

        popup.destroy()        # κλείνει το popup
        on_close_callback()    # ανανεώνει τον πίνακα στο κεντρικό παράθυρο

    # Τίτλος
    tk.Label(popup, text="Προσθήκη Συνταγής",
             font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

    # Πεδία φόρμας — κάθε γραμμή: Label αριστερά, Entry δεξιά
    tk.Label(popup, text="Όνομα:").grid(row=1, column=0, sticky="e", padx=8, pady=4)
    entry_name = tk.Entry(popup, width=30)
    entry_name.grid(row=1, column=1, padx=8, pady=4)

    tk.Label(popup, text="Κατηγορία:").grid(row=2, column=0, sticky="e", padx=8, pady=4)
    entry_category = tk.Entry(popup, width=30)
    entry_category.grid(row=2, column=1, padx=8, pady=4)

    tk.Label(popup, text="Δυσκολία (1-10):").grid(row=3, column=0, sticky="e", padx=8, pady=4)
    entry_difficulty = tk.Entry(popup, width=30)
    entry_difficulty.grid(row=3, column=1, padx=8, pady=4)

    tk.Label(popup, text="Χρόνος (λεπτά):").grid(row=4, column=0, sticky="e", padx=8, pady=4)
    entry_time = tk.Entry(popup, width=30)
    entry_time.grid(row=4, column=1, padx=8, pady=4)

    # Κουμπί — το command= συνδέει το κλικ με τη συνάρτηση on_save
    tk.Button(popup, text="Αποθήκευση", command=on_save,
              bg="#4CAF50", fg="white").grid(row=5, column=0, columnspan=2, pady=10)