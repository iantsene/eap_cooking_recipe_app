from db import DatabaseConn 
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class Recipe:
    def __init__(self, name=None, category=None, difficulty=None, total_time_minutes=None):
        self.name = name
        self.category = category
        self.difficulty = difficulty
        self.total_time_minutes = total_time_minutes
        self.id = None
        self.ingredients = []
        self.steps = []

    def add_recipe(self):
        """GUI-based method to add a recipe using dropdown menus"""
        
        # Create main dialog window
        dialog = tk.Toplevel()
        dialog.title("Add New Recipe")
        dialog.geometry("500x600")
        dialog.transient()  # Make it modal
        dialog.grab_set()   # Make it modal
        
        # Variables to store input
        name_var = tk.StringVar()
        category_var = tk.StringVar()
        difficulty_var = tk.StringVar()
        time_var = tk.StringVar()
        
        # Create form fields
        row = 0
        
        # Recipe Name
        tk.Label(dialog, text="Recipe Name:", font=("Arial", 10, "bold")).grid(row=row, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(dialog, textvariable=name_var, width=40).grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        # Recipe Category
        tk.Label(dialog, text="Recipe Category:", font=("Arial", 10, "bold")).grid(row=row, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(dialog, textvariable=category_var, width=40).grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        # Recipe Difficulty - DROPDOWN
        tk.Label(dialog, text="Difficulty Level:", font=("Arial", 10, "bold")).grid(row=row, column=0, padx=10, pady=5, sticky="w")
        difficulty_options = ["Εύκολη", "Μέτρια", "Δύσκολη"]
        difficulty_combo = ttk.Combobox(dialog, textvariable=difficulty_var, values=difficulty_options, state="readonly", width=37)
        difficulty_combo.grid(row=row, column=1, padx=10, pady=5)
        difficulty_combo.set("Select difficulty...")
        row += 1
        
        # Total Time
        tk.Label(dialog, text="Total Time (minutes):", font=("Arial", 10, "bold")).grid(row=row, column=0, padx=10, pady=5, sticky="w")
        tk.Entry(dialog, textvariable=time_var, width=40).grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        # Separator
        ttk.Separator(dialog, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky="ew", pady=10)
        row += 1
        
        # Ingredients Listbox
        tk.Label(dialog, text="Ingredients:", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        ingredients_frame = tk.Frame(dialog)
        ingredients_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=5)
        
        ingredients_listbox = tk.Listbox(ingredients_frame, height=5, width=50)
        ingredients_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ingredients_scrollbar = tk.Scrollbar(ingredients_frame, orient="vertical", command=ingredients_listbox.yview)
        ingredients_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        ingredients_listbox.config(yscrollcommand=ingredients_scrollbar.set)
        row += 1
        
        # Ingredients buttons
        ingredients_btn_frame = tk.Frame(dialog)
        ingredients_btn_frame.grid(row=row, column=0, columnspan=2, pady=5)
        
        def add_ingredient():
            ingredient = Ingredient()
            ingredient.add_ingredient()  # This should be GUI-based too
            self.ingredients.append(ingredient)
            ingredients_listbox.insert(tk.END, f"{ingredient.name} - {ingredient.quantity} {ingredient.unit}")
        
        def remove_ingredient():
            selection = ingredients_listbox.curselection()
            if selection:
                index = selection[0]
                ingredients_listbox.delete(index)
                del self.ingredients[index]
        
        tk.Button(ingredients_btn_frame, text="Add Ingredient", command=add_ingredient).pack(side=tk.LEFT, padx=5)
        tk.Button(ingredients_btn_frame, text="Remove Ingredient", command=remove_ingredient).pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Separator
        ttk.Separator(dialog, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky="ew", pady=10)
        row += 1
        
        # Steps Listbox
        tk.Label(dialog, text="Steps:", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, pady=5)
        row += 1
        
        steps_frame = tk.Frame(dialog)
        steps_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=5)
        
        steps_listbox = tk.Listbox(steps_frame, height=5, width=50)
        steps_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        steps_scrollbar = tk.Scrollbar(steps_frame, orient="vertical", command=steps_listbox.yview)
        steps_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        steps_listbox.config(yscrollcommand=steps_scrollbar.set)
        row += 1
        
        # Steps buttons
        steps_btn_frame = tk.Frame(dialog)
        steps_btn_frame.grid(row=row, column=0, columnspan=2, pady=5)
        
        def add_step():
            step_num = len(self.steps) + 1
            step = Step()
            step.add_step(step_num)  # This should be GUI-based too
            self.steps.append(step)
            steps_listbox.insert(tk.END, f"Step {step_num}: {step.step_text[:50]}...")
        
        def remove_step():
            selection = steps_listbox.curselection()
            if selection:
                index = selection[0]
                steps_listbox.delete(index)
                del self.steps[index]
                # Re-number remaining steps
                for i, step in enumerate(self.steps, 1):
                    step.sequence_order = i
        
        tk.Button(steps_btn_frame, text="Add Step", command=add_step).pack(side=tk.LEFT, padx=5)
        tk.Button(steps_btn_frame, text="Remove Step", command=remove_step).pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Separator
        ttk.Separator(dialog, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky="ew", pady=10)
        row += 1
        
        # Submit button
        def submit_recipe():
            # Validate inputs
            if not name_var.get().strip():
                messagebox.showerror("Error", "Please enter a recipe name")
                return
            
            if not category_var.get().strip():
                messagebox.showerror("Error", "Please enter a recipe category")
                return
            
            if difficulty_var.get() not in difficulty_options:
                messagebox.showerror("Error", "Please select a difficulty level")
                return
            
            try:
                time_minutes = int(time_var.get().strip())
                if time_minutes <= 0:
                    messagebox.showerror("Error", "Please enter a positive number for total time")
                    return
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid integer for total time")
                return
            
            if not self.ingredients:
                messagebox.showerror("Error", "Please add at least one ingredient")
                return
            
            if not self.steps:
                messagebox.showerror("Error", "Please add at least one step")
                return
            
            # Set recipe attributes
            self.name = name_var.get().strip()
            self.category = category_var.get().strip()
            self.difficulty = difficulty_var.get()
            self.total_time_minutes = time_minutes
            
            # Save to database
            try:
                with DatabaseConn("recipe_database.db") as conn:
                    # Insert recipe
                    insert_recipe = """INSERT INTO recipes(name, category, difficulty, total_time_minutes) 
                                      VALUES(?, ?, ?, ?)"""
                    conn.execute(insert_recipe, (self.name, self.category, 
                                                self.difficulty, self.total_time_minutes))
                    self.id = conn.cursor.lastrowid
                    
                    # Insert ingredients
                    for ingredient in self.ingredients:
                        ingredient.recipe_id = self.id
                        ingredient.save_to_db(conn)
                    
                    # Insert steps
                    for step in self.steps:
                        step.recipe_id = self.id
                        step.save_to_db(conn)
                
                messagebox.showinfo("Success", f"Recipe '{self.name}' added successfully with ID: {self.id}!\nAdded {len(self.ingredients)} ingredients and {len(self.steps)} steps.")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to save recipe: {str(e)}")
        
        # Buttons frame
        button_frame = tk.Frame(dialog)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        tk.Button(button_frame, text="Save Recipe", command=submit_recipe, bg="green", fg="white", padx=20).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy, bg="red", fg="white", padx=20).pack(side=tk.LEFT, padx=10)
        
        # Wait for dialog to close
        dialog.wait_window()

    @staticmethod
    def get_recipe_with_details(recipe_id):
        with DatabaseConn("recipe_database.db") as conn:
            # Get recipe
            conn.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
            recipe_data = conn.cursor.fetchone()
            
            if not recipe_data:
                print(f"No recipe found with ID: {recipe_id}")
                return None
            
            # Get ingredients
            conn.execute("SELECT * FROM ingredients WHERE recipe_id = ?", (recipe_id,))
            ingredients_data = conn.cursor.fetchall()
            
            # Get steps
            conn.execute("SELECT * FROM steps WHERE recipe_id = ? ORDER BY sequence_order", (recipe_id,))
            steps_data = conn.cursor.fetchall()
            
            # Create recipe object
            recipe = Recipe(
                name=recipe_data[1],
                category=recipe_data[2],
                difficulty=recipe_data[3],
                total_time_minutes=recipe_data[4]
            )
            recipe.id = recipe_data[0]
            
            # Create ingredient objects
            recipe.ingredients = [
                Ingredient(
                    name=ing[2],
                    quantity=ing[3],
                    unit=ing[4],
                    notes=ing[5]
                ) for ing in ingredients_data
            ]
            
            # Create step objects
            recipe.steps = [
                Step(
                    step_name=step[2],
                    sequence_order=step[3],
                    step_text=step[4],
                    duration_in_minutes=step[5]
                ) for step in steps_data
            ]
            
            return recipe


class Ingredient:
    def __init__(self, name=None, quantity=None, unit=None, notes=None, recipe_id=None):
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.notes = notes
        self.recipe_id = recipe_id
        self.id = None
    
    def add_ingredient(self):
        print("\nEnter ingredient name:")
        self.name = input().strip()
        
        print("Enter quantity (e.g., 2, 0.5, 1.5):")
        while True:
            try:
                self.quantity = float(input())
                if self.quantity > 0:
                    break
                else:
                    print("Please enter a positive number.")
            except ValueError:
                print("Please enter a valid number.")
        
        print("Enter unit (e.g., cups, tbsp, grams, pieces) or press Enter to skip:")
        self.unit = input().strip()
        if not self.unit:
            self.unit = None
        
        print("Enter any notes (e.g., chopped, fresh, optional) or press Enter to skip:")
        self.notes = input().strip()
        if not self.notes:
            self.notes = None
    
    def save_to_db(self, conn):
        """Save ingredient to database"""
        insert_ingredient = """INSERT INTO ingredients(
            recipe_id, name, quantity, unit, notes
        ) VALUES(?, ?, ?, ?, ?)"""
        conn.execute(insert_ingredient, (
            self.recipe_id, self.name, self.quantity, 
            self.unit, self.notes
        ))
        self.id = conn.cursor.lastrowid
    
    def __str__(self):
        """String representation of ingredient"""
        parts = [str(self.quantity)]
        if self.unit:
            parts.append(self.unit)
        parts.append(self.name)
        if self.notes:
            parts.append(f"({self.notes})")
        return " ".join(parts)


class Step:
    def __init__(self, step_name=None, sequence_order=None, step_text=None, duration_in_minutes=None, recipe_id=None):
        self.step_name = step_name
        self.sequence_order = sequence_order
        self.step_text = step_text
        self.duration_in_minutes = duration_in_minutes
        self.recipe_id = recipe_id
        self.id = None
    
    def add_step(self, step_number):
        """Prompt user for step details"""
        print(f"\nStep {step_number}:")
        
        print("Enter step name (e.g., 'Prepare vegetables'):")
        self.step_name = input().strip()
        
        print("Enter step description:")
        self.step_text = input().strip()
        
        print("Enter duration in minutes:")
        while True:
            try:
                self.duration_in_minutes = int(input())
                if self.duration_in_minutes >= 0:
                    break
                else:
                    print("Please enter a non-negative number.")
            except ValueError:
                print("Please enter a valid integer.")
        
        self.sequence_order = step_number
    
    def save_to_db(self, conn):
        """Save step to database"""
        insert_step = """INSERT INTO steps(
            recipe_id, step_name, sequence_order, step_text, duration_in_minutes
        ) VALUES(?, ?, ?, ?, ?)"""
        conn.execute(insert_step, (
            self.recipe_id, self.step_name, self.sequence_order,
            self.step_text, self.duration_in_minutes
        ))
        self.id = conn.cursor.lastrowid
    
    def __str__(self):
        """String representation of step"""
        return f"{self.sequence_order}. {self.step_name}: {self.step_text} ({self.duration_in_minutes} mins)"
