import sqlite3
# Η python εχει ενσωμματωμένη την sqlite3 οποτε μπορούμε να την κάνουμε import κατευθείαν

conn = sqlite3.connect('recipe_database.db')
# Το πρώτο βήμα για να στήσουμε μια βάση δεδομένων είναι να φτιαξουμε μια μεταβλητη και να την εξισώσουμε με το ονομα της βάσης δεδομένων μας. Αν υπάρχει η βάση ήδη η python θα συνδεθεί σε αυτήν. Αν δεν υπάρχει θα την δημιουγήσει

cursor = conn.cursor()
# Το δευτερο βήμα είναι να δημιουργήσουμε εναν κέρσορα. Αυτός χρειάζεται για να αλληλεπιδράσουμε με τη βάση μας μέσω εντολών SQL. Αυτό θα μας επιτρέψει να δημιουργήσουμε και να τροποποιήσουμε πίνακες μέσα στη βάση μας.

create_recipe_table = """CREATE TABLE IF NOT EXISTS
recipes(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, difficulty INTEGER, total_time_minutes INTEGER)"""
# Δημιουργούμε μια εντολή SQL που θα δημιουργήσει εναν πίνακα ονόματι "recipes" αν αυτός δεν υπάρχει. Ορίζουμε ενα id οπου θα μετράει τις εισαγωγές δεδομένων σε κάθε σειρά/γραμμή του πίνακα και του δίνουμε τύπο δεδομένων INTEGER και του δίνουμε την ιδιότητα PRIMARY KEY για να ορίσουμε οτι θα είναι το κύριο στοιχείο του πίνακα οπου θα χρησιμοποιούμε για να αναφερθούμε στην συγκεκριμένη καταχώρηση που θέλουμε να τροποποιήσουμε στο μέλλον. Βάζουμε AUTOINCREMENT για να δίνεται αυτόματα αυξοντας σειράς ID κάθε φορά που κάνουμε καταχώρηση μέσα στον πίνακα χωρίς να το κάνουμε εμείς χειροκίνητα. Τα υπόλοιπα στοιχεία του πίνακα πρέπει να αντικατοπτρίζουν τα δεδομένα που θα εισάγουμε σε κάθε καταχώρηση απο το πρόγραμμα μας ώστε να έχουμε όλη την πληροφορία εκεί για επεξεργασία απο το πρόγραμμα μας.

cursor.execute(create_recipe_table)
# Τρέχει τον κώδικα της SQL στη μνήμη του υπολογιστή
conn.commit()
# Ενσωμματώνει τις άλλαγές που έχουν γίνει στη μνήμη με το execute επίσημα πια στη βάση.
conn.close()
# Κλείνει τη σύνδεση με τη βάση ωστε να μην γίνονται πιά αλλαγές

def add_recipe():
    print("Enter the recipe name:")
    name = input()
    print("Enter the recipe category:")
    category = input()
    print("Enter the recipe difficulty level (1-10):")
    difficulty = int(input())
    print("Enter the recipe total time of execution in minutes:")
    total_time_minutes = int(input())
    with sqlite3.connect('recipe_database.db') as conn:
        cursor = conn.cursor()
        insert_data_in_recipes = """INSERT INTO recipes(name, category, difficulty, total_time_minutes) VALUES(?, ?, ?, ?)"""
        cursor.execute(insert_data_in_recipes, (name, category, difficulty, total_time_minutes))
        conn.commit()
    print("Recipe added successfully!")

def recipe_search(id):
    with sqlite3.connect('recipe_database.db') as conn:
        cursor = conn.cursor()
        sql_str = """SELECT * FROM recipes WHERE id = ?"""
        cursor.execute(sql_str, (id,))
        results = cursor.fetchone()
    return results

def update_recipe(id): # Needs work to get the fields towards updating from the user/frontend
    with sqlite3.connect('recipe_database.db') as conn:
        cursor = conn.cursor()
        sql_str = """UPDATE recipes SET FIELD1 = ?, FIELD2 = ?, FIELD3 = ? WHERE id = ?"""
        cursor.execute(sql_str, (id,))
        conn.commit()
    pass

def delete_recipe(id):
    with sqlite3.connect('recipe_database.db') as conn:
        cursor = conn.cursor()
        sql_str = """DELETE FROM recipes WHERE id = ?"""
        cursor.execute(sql_str, (id,))
        conn.commit()
    if cursor.rowcount > 0:
        print(f"{cursor.rowcount} recipe deleted.")
    else:
        print("No such recipe found to be deleted.")

def launch_recipe(id):
    pass

def get_all_recipes():
    with sqlite3.connect('recipe_database.db') as conn:
        cursor = conn.cursor()
        fetch_recipes = """SELECT * FROM recipes"""
        cursor.execute(fetch_recipes)
        results = cursor.fetchall()
        for row in results:
            print(row)
    return

# add_recipe()
# recipe_to_search = recipe_search(1)
# print(recipe_to_search)
recipe_to_delete = delete_recipe(1)
recipes = get_all_recipes()
print(recipes)
