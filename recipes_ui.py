import tkinter as tk
import db

# Συνάρτηση που καλείται όταν πατηθεί το κουμπί
def on_save():
    name       = entry_name.get().strip()      # διαβάζουμε τι έγραψε ο χρήστης
    category   = entry_category.get().strip()
    difficulty = int(entry_difficulty.get())
    time_mins  = int(entry_time.get())
    db.add_recipe(name, category, difficulty, time_mins)  # αποθηκεύουμε στη βάση
    print(f"Αποθηκεύτηκε: {name}")

# Δημιουργία παραθύρου
window = tk.Tk()
window.title("Συνταγές")

# Τίτλος
tk.Label(window, text="Διαχείριση Συνταγών",
         font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

# Πεδία φόρμας — κάθε γραμμή: Label αριστερά, Entry δεξιά
tk.Label(window, text="Όνομα:").grid(row=1, column=0, sticky="e", padx=8, pady=4)
entry_name = tk.Entry(window, width=30)
entry_name.grid(row=1, column=1, padx=8, pady=4)

tk.Label(window, text="Κατηγορία:").grid(row=2, column=0, sticky="e", padx=8, pady=4)
entry_category = tk.Entry(window, width=30)
entry_category.grid(row=2, column=1, padx=8, pady=4)

tk.Label(window, text="Δυσκολία (1-10):").grid(row=3, column=0, sticky="e", padx=8, pady=4)
entry_difficulty = tk.Entry(window, width=30)
entry_difficulty.grid(row=3, column=1, padx=8, pady=4)

tk.Label(window, text="Χρόνος (λεπτά):").grid(row=4, column=0, sticky="e", padx=8, pady=4)
entry_time = tk.Entry(window, width=30)
entry_time.grid(row=4, column=1, padx=8, pady=4)

# Κουμπί — το command= συνδέει το κλικ με τη συνάρτηση on_save
tk.Button(window, text="Αποθήκευση", command=on_save,
          bg="#4CAF50", fg="white").grid(row=5, column=0, columnspan=2, pady=10)

# Εκκίνηση — κρατάει το παράθυρο ανοιχτό
window.mainloop()