from db import DatabaseConn 
import tkinter as tk
from tkinter import ttk, messagebox


class Recipe:
    def __init__(self, name=None, category=None, difficulty=None, total_time_minutes=None):
        self.name = name
        self.category = category
        self.difficulty = difficulty
        self.total_time_minutes = total_time_minutes
        self.id = None
        self.ingredients = []
        self.steps = []

    @classmethod
    def get_all_recipes(cls):
        """Return list of all recipes as Recipe objects (or tuples)"""
        with DatabaseConn("recipe_database.db") as db:
            db.execute("SELECT id, name, category, difficulty, total_time_minutes FROM recipes")
            return db.fetchall()  # or convert to Recipe objects
        
    @classmethod
    def get_recipe_by_id(cls, recipe_id):
        """Fetch a single recipe by ID with all its ingredients and steps"""
        with DatabaseConn("recipe_database.db") as db:
            # Get recipe
            db.execute("SELECT id, name, category, difficulty, total_time_minutes FROM recipes WHERE id = ?", (recipe_id,))
            row = db.fetchone()
            
            if not row:
                return None
            
            # Create recipe object
            recipe = cls(
                name=row[1],
                category=row[2],
                difficulty=row[3],
                total_time_minutes=row[4]
            )
            recipe.id = row[0]
            
            # Get ingredients
            db.execute("SELECT id, name, quantity, unit, notes FROM ingredients WHERE recipe_id = ?", (recipe_id,))
            ingredient_rows = db.fetchall()
            for ing_row in ingredient_rows:
                ingredient = Ingredient(
                    id=ing_row[0],
                    name=ing_row[1],
                    quantity=ing_row[2],
                    unit=ing_row[3],
                    notes=ing_row[4],
                    recipe_id=recipe_id
                )
                recipe.ingredients.append(ingredient)
            
            # Get steps with their allocations
            db.execute("""SELECT id, step_name, sequence_order, step_text, duration_in_minutes 
                        FROM steps WHERE recipe_id = ? ORDER BY sequence_order""", (recipe_id,))
            step_rows = db.fetchall()
            for step_row in step_rows:
                step = Step(
                    id=step_row[0],
                    step_name=step_row[1],
                    sequence_order=step_row[2],
                    step_text=step_row[3],
                    duration_in_minutes=step_row[4],
                    recipe_id=recipe_id
                )
                
                # 🔧 CRITICAL: Load allocations for this step
                db.execute("""
                    SELECT si.ingredient_id, i.name, si.quantity, si.unit, si.notes
                    FROM step_ingredients si
                    JOIN ingredients i ON si.ingredient_id = i.id
                    WHERE si.step_id = ?
                """, (step.id,))
                alloc_rows = db.fetchall()
                
                step.allocations = []
                for alloc_row in alloc_rows:
                    step.allocations.append({
                        'ingredient_id': alloc_row[0],
                        'ingredient_name': alloc_row[1],
                        'quantity': alloc_row[2],
                        'unit': alloc_row[3],
                        'notes': alloc_row[4]
                    })
                
                recipe.steps.append(step)
            
            return recipe
    
    @classmethod
    def search_by_name(cls, search_term):
        """Return recipes matching search term (data retrieval only)"""
        with DatabaseConn("recipe_database.db") as db:
            db.execute(
                "SELECT id, name, category, difficulty, total_time_minutes FROM recipes WHERE name LIKE ?",
                (f'%{search_term}%',)
            )
            return db.fetchall()

    def update(self):
        """Update this recipe in the database"""
        if not self.id:
            raise ValueError("Cannot update recipe without an ID")
        
        with DatabaseConn("recipe_database.db") as db:
            # Update recipe basic info
            db.execute("""
                UPDATE recipes 
                SET name=?, category=?, difficulty=?, total_time_minutes=?
                WHERE id=?
            """, (self.name, self.category, self.difficulty, self.total_time_minutes, self.id))
            
            # Delete old ingredients, steps, and step_ingredients
            db.execute("DELETE FROM step_ingredients WHERE step_id IN (SELECT id FROM steps WHERE recipe_id=?)", (self.id,))
            db.execute("DELETE FROM ingredients WHERE recipe_id = ?", (self.id,))
            db.execute("DELETE FROM steps WHERE recipe_id = ?", (self.id,))
            
            # Save current ingredients and steps
            for ingredient in self.ingredients:
                ingredient.recipe_id = self.id
                ingredient.save_to_db(db)
            
            for step in self.steps:
                step.recipe_id = self.id
                step.save_to_db(db)  # This now also saves allocations
            
            return db.cursor.rowcount > 0

    @classmethod
    def delete_by_id(cls, recipe_id):
        """Delete recipe by ID (class method - use when you don't have a Recipe object)"""
        with DatabaseConn("recipe_database.db") as db:
            db.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
            return db.cursor.rowcount > 0

    def delete(self):
        """Delete this recipe instance"""
        if not self.id:
            return False
        return self.__class__.delete_by_id(self.id)
    
    def save(self):
        """Insert new recipe into database"""
        with DatabaseConn("recipe_database.db") as db:
            db.execute("""
                INSERT INTO recipes (name, category, difficulty, total_time_minutes)
                VALUES (?, ?, ?, ?)
            """, (self.name, self.category, self.difficulty, self.total_time_minutes))
            self.id = db.cursor.lastrowid
            
            # Save ingredients and steps
            for ingredient in self.ingredients:
                ingredient.recipe_id = self.id
                ingredient.save_to_db(db)
            
            for step in self.steps:
                step.recipe_id = self.id
                step.save_to_db(db)
            
            return True


class Ingredient:
    def __init__(self, id=None, name=None, quantity=None, unit=None, notes=None, recipe_id=None):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.notes = notes
        self.recipe_id = recipe_id
    
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
    def __init__(self, id=None, step_name=None, sequence_order=None, 
                 step_text=None, duration_in_minutes=None, recipe_id=None):
        self.id = id
        self.step_name = step_name
        self.sequence_order = sequence_order
        self.step_text = step_text
        self.duration_in_minutes = duration_in_minutes
        self.recipe_id = recipe_id
        self.allocations = []  # List of ingredient allocations for this step
    
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
        
        # 🔧 FIX: Save step-ingredient relationships
        for allocation in self.allocations:
            step_ingredient = StepIngredient(
                step_id=self.id,
                ingredient_id=allocation.get('ingredient_id'),
                quantity=allocation.get('quantity'),
                unit=allocation.get('unit'),
                notes=allocation.get('notes', '')
            )
            step_ingredient.save_to_db(conn)
    
    def load_allocations(self, conn):
        """Load ingredient allocations for this step from database"""
        conn.execute("""
            SELECT si.ingredient_id, i.name, si.quantity, si.unit, si.notes
            FROM step_ingredients si
            JOIN ingredients i ON si.ingredient_id = i.id
            WHERE si.step_id = ?
        """, (self.id,))
        rows = conn.fetchall()
        
        self.allocations = []
        for row in rows:
            self.allocations.append({
                'ingredient_id': row[0],
                'ingredient_name': row[1],
                'quantity': row[2],
                'unit': row[3],
                'notes': row[4]
            })
        return self.allocations
    
    def __str__(self):
        return f"{self.sequence_order}. {self.step_name}: {self.step_text} ({self.duration_in_minutes} mins)"


class StepIngredient:
    """Junction table model for step-ingredient relationships"""
    def __init__(self, id=None, step_id=None, ingredient_id=None, 
                 quantity=None, unit=None, notes=None):
        self.id = id
        self.step_id = step_id
        self.ingredient_id = ingredient_id
        self.quantity = quantity
        self.unit = unit
        self.notes = notes
    
    def save_to_db(self, conn):
        """Save step-ingredient relationship to database"""
        insert_sql = """INSERT INTO step_ingredients(
            step_id, ingredient_id, quantity, unit, notes
        ) VALUES(?, ?, ?, ?, ?)"""
        conn.execute(insert_sql, (
            self.step_id, self.ingredient_id, 
            self.quantity, self.unit, self.notes
        ))
        self.id = conn.cursor.lastrowid