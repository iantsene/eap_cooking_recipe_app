import sqlite3

class DatabaseConn:
    def __init__(self, db_str):
        self.db_str = db_str
        self.connection = None
        self.cursor = None

    def __enter__(self):
        print("Initializing database connection...")
        self.connection = sqlite3.connect(self.db_str)
        self.cursor = self.connection.cursor()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        print("Cleaning up...")
        if exc_type is not None:
            print(f"Exception type: {exc_type}")
            print(f"Exception value: {exc_value}")
            print(f"Traceback: {traceback}")
            self.connection.rollback()
        else:
            self.connection.commit()
        if self.connection:
            self.connection.close()
        return False

    def execute(self, sql, params=None):
        if params:
            return self.cursor.execute(sql, params)
        return self.cursor.execute(sql)
    
    def commit(self):
        if self.connection:
            self.connection.commit()


with DatabaseConn("recipe_database.db") as rcp_db:
    create_recipe_table = """CREATE TABLE IF NOT EXISTS recipes(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, difficulty INTEGER, total_time_minutes INTEGER)"""
    create_ingredients_table = """CREATE TABLE IF NOT EXISTS ingredients(id INTEGER PRIMARY KEY AUTOINCREMENT, recipe_id INTEGER, name TEXT, FOREIGN KEY (recipe_id) REFERENCES recipes(id))"""
    create_recipeSteps_table = """CREATE TABLE IF NOT EXISTS steps(id INTEGER PRIMARY KEY AUTOINCREMENT, recipe_id INTEGER, name TEXT, sequence_order INTEGER, description TEXT, duration_in_minutes INTEGER, FOREIGN KEY (recipe_id) REFERENCES recipes(id))"""
    rcp_db.execute(create_recipe_table)
    rcp_db.execute(create_ingredients_table)
    rcp_db.execute(create_recipeSteps_table)

# Under construction
class Steps:
    def __init__(self, name, sequence_order, description, duration_in_minutes):
        self.name = name
        self.sequence_order = sequence_order
        self.description = description
        self.duration_in_minutes = duration_in_minutes

# Under construction
class Ingredients:
    def __init__(self, name, quantity, unit=None, recipe_id=None):
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.recipe_id = recipe_id
        self.id = None

# Needs adjustments
class Recipe:
    def __init__(self, name, category, difficulty, total_time_minutes):
        self.name = name
        self.category = category
        self.difficulty = difficulty
        self.total_time_minutes = total_time_minutes

    def add_recipe(self):
        print("Enter the recipe name:")
        self.name = input()
        print("Enter the recipe category:")
        self.category = input()
        print("Enter the recipe difficulty level (1-10):")
        self.difficulty = int(input())
        print("Enter the recipe total time of execution in minutes:")
        self.total_time_minutes = int(input())
        with DatabaseConn("recipe_database.db") as conn:
            insert_data_in_recipes = """INSERT INTO recipes(name, category, difficulty, total_time_minutes) VALUES(?, ?, ?, ?)"""
            conn.cursor.execute(insert_data_in_recipes, (self.name, self.category, self.difficulty, self.total_time_minutes))
            conn.commit()
        print("Recipe added successfully!")

    def recipe_search(self):
        with DatabaseConn("recipe_database.db") as conn:
            cursor = conn.cursor()
            sql_str = """SELECT * FROM recipes WHERE name = ?"""
            cursor.execute(sql_str, (self.name,))
            results = cursor.fetchone()
        return results

    def delete_recipe(self):
        with DatabaseConn("recipe_database.db") as conn:
            cursor = conn.cursor()
            sql_str = """DELETE FROM recipes WHERE name = ?"""
            cursor.execute(sql_str, (self.name,))
            conn.commit()
        if cursor.rowcount > 0:
            print(f"{cursor.rowcount} recipe deleted.")
        else:
            print("No such recipe found to be deleted.")

    def launch_recipe(id):
        pass

    def get_all_recipes(self):
        with DatabaseConn("recipe_database.db") as conn:
            cursor = conn.cursor()
            fetch_recipes = """SELECT * FROM recipes"""
            cursor.execute(fetch_recipes)
            results = cursor.fetchall()
            for row in results:
                print(row)
        return

