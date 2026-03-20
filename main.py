# βημα 1ο
# Δημιουργία κλάσεων για Υλικά - Βήματα - Συνταγές

#Κλάση Υλικών
class Ingredient:
    ''' Κλάση για ένα απλό υλικό'''
    def __init__ (self, name):
        self.name = name # μοναδική παράμετρος το όνομα


class Step:
    '''κλάση για τα βήματα της καθε συνταγής'''
    def __init__ (self, sequence_order, title, description, hours, minutes) :
        self.sequence_order = sequence_order # 1o βημα, 2ο βημα κλπ 
        self.title = title # τίτλος βήματος πχ βράσιμο ζυμαρικών κλπ
        self.description = description # τι κανουμε στο βήμα αυτό αναλυτικά πχ πλένω τα λαχανικά για 10 λεπτά, κόβω πατάτες κλπ
        # λόγω εκφώνησης (χρονική διάρκεια του βήματος σε ώρες και λεπτά) χρησιμοποίησα 2 παράμετρους hours/minutes αντί μιας total_time
        self.hours = hours # διάρκεια σε ώρες
        self. minutes = minutes # διάρκεια σε λεπτά
        print(f"Δημιουργήθηκε το βήμα {self.sequence_order} : {self.title}")


class Recipe:
    '''κλάση για τη συνταγή'''
    def __init__ (self, name, category, difficulty, total_time_minutes):
        '''αρχικοποίηση'''
        self.name = name # όνομα συνταγής
        self.category = category # πχ ζυμαρικά
        self.difficulty = difficulty # δυσκολία (εύκολη μέτρια δύσκολη)
        self.total_time_minutes = total_time_minutes # συνολικός χρόνος (εδώ δεν το υπολογίζω ξεχωριστά σε ώρες/λεπτά όπως στα steps, λόγω εκφώνησης)

        # Βήμα 2ο
        # Δημιουργία 2 κενών λιστών για να αποθηκεύσω σε αυτές τα υλικά και τα βήματα που θα ανήκουν στην ίδια συνταγή

        # αυτη η λίστα θα αποθηκεύθει αντικείμενα της κλάσης Ingredient
        # εδώ αποθηκεύω ένα ένα τα υλικά
        # ξεκινάει άδεια γιατί κάθε συνταγή έχει διαφορετικό αριθμό υλικών
        self.ingredients_list = []

        # Αυτή η λίστα αποθηκεύει αντικείμενα της κλάσης Step
        # εδώ αποθηκεύω τα βήματα, επίσης η χρήση λίστας στην περίπτωση αυτή είναι ιδανική
        # γιατί μπορώ να έχω αρίθμιση των αντικειμένων της δλδ κρατάει τη σειρά (1ο-2ο-3ο κλπ)
        self.steps_list = []

        #   Βήμα 3ο
        #   Δημιουργία 3 συναρτήσεων μέσα στην κλάση recipe, που θα κανουν τα παρακατω:
        #   1)  add_ingredient_to_recipe : τοποθετηση του υλικού μέσα στη λιστα της συνταγής (ingredients_list)
        #   2)  add_step_to_recipe : δημιουργία νέου βήματος και τοποθέτησή του στη λίστα βημάτων της συνταγής (steps_list)
        #   3)  calculate_progress : Υπολογίζει το ποσοστό % ολοκλήρωσης της συνταγής μέχρι το βήμα που βρίσκεται ο χρήστης.  

    def add_ingredient_to_recipe(self, ingredient_object):
        '''Παίρνω ένα υλικό και το τοποθετώ στη λίστα της συνταγής'''
        #   1)  Ενημερώνω τι θα γίνει
        print(f"--- Διαδικασία προσθήκης υλικού στη συνταγή {self.name}---")

        #   2)  παιρνω το υλικό
        print(f"Πήραμε το υλικό {ingredient_object.name}") 

        #   3)  Αποθήκευση στη λίστα
        self.ingredients_list.append(ingredient_object)

        #   4)  Επιβεβαίωση ότι η λίστα μεγάλωσε
        print(f"Το υλικό {ingredient_object.name} προστέθηκε στη λίστα της συνταγής {self.name}!")
        print(f"Τώρα η συνταγή έχει {len(self.ingredients_list)} υλικά")
        print("--- Τέλος Προσθήκης ---")

    def add_step_to_recipe(self, sequence_order, title, description, hours, minutes):
        ''' Αυτή η Συνάρτηση δημιουργεί ένα βήμα και το βάζει στη λίστα steps_list '''
        #   1)  Ενημερώνω τι θα γίνει
        print(f"--- Προσθήκη βήματος {sequence_order} ---") 

        #   2)  Καλώ την κλάση Steps
        new_step = Step(sequence_order, title, description, hours, minutes)

        #   3)  Τοποθέτηση στη λίστα steps_list
        self.steps_list.append(new_step)

        #   4)  Επιβαιβέωση τοποθέτησης
        print(f"To βήμα {title} προστέθηκε επιτυχώς!")
        print(f"Συνολικά βήματα συνταγής {self.name} : {len(self.steps_list)}")
        print("--- Τέλος Προσθήκης ---")


    def calculate_progress(self, current_step_index):
        '''Υπολογίζει το ποσοστό % ολοκλήρωσης της συνταγής μέχρι το βήμα που βρίσκεται ο χρήστης.
        Το 'current_step_index' είναι η θέση του βήματος στη λίστα (0, 1, 2...)'''
        
        total_minutes_completed = 0 # αρχικοποίηση τοπικής μεταβλητής που μετράει πόσα λεπτά έχει αφιερώσει στη συνταγή ο χρήστης 
        
       # επανάληψη από το 1ο βήμα έως το βήμα που βρίσκεται ο χρήστης (current_step_index + 1)
        for i in range(current_step_index + 1): 
            # Παίρνουμε το συγκεκριμένο βήμα από τη λίστα steps_list χρησιμοποιώντας τη θέση i
            step = self.steps_list[i]
            # Μετατρέπουμε τις ώρες του βήματος σε λεπτά και προσθέτουμε τα λεπτά
            step_total_minutes = (step.hours * 60) + step.minutes
            # Προσθέτουμε τη διάρκεια αυτού του βήματος στο συνολικό άθροισμα
            total_minutes_completed = total_minutes_completed + step_total_minutes
            # Χρησιμοποιούμε try-except για να διαχειριστούμε την περίπτωση που ο χρόνος είναι μηδέν
        try:
            # Δοκιμάζουμε να κάνουμε τη διαίρεση
            percentage = (total_minutes_completed / self.total_time_minutes) * 100
            # Αν η διαίρεση γίνει κανονικά, επιστρέφουμε το αποτέλεσμα 
            return percentage
            
        except ZeroDivisionError:
            print(f"\n[ΠΡΟΣΟΧΗ]: Αδυναμία υπολογισμού προόδου στη συνταγή '{self.name}'.")
            print(f"Αιτία: Ο συνολικός χρόνος της συνταγής έχει οριστεί ως 0 λεπτά.")
            return 0