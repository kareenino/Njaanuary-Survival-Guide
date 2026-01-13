import json
import os

class Table:
    def __init__(self, name, schema):
        self.name = name
        self.schema = schema 
        self.filename = f"{name}.json"
        self.rows = self._load()

    def _load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                data = json.load(f)
                # Unique lookups via ID
                return {str(row['id']): row for row in data}
        return {}

    def _save(self):
        with open(self.filename, 'w') as f:
            json.dump(list(self.rows.values()), f, indent=4)

    def insert(self, record):
        # auto increment
        if 'id' not in record or record['id'] is None:
            if not self.rows:
                record['id'] = 1
            else:
                # Find the current max ID and add 1
                max_id = max(int(k) for k in self.rows.keys())
                record['id'] = max_id + 1
        
        pk = str(record['id'])
        
        # Unique Key Constraint Check
        if pk in self.rows:
            print(f"❌ Error: Primary Key {pk} already exists.")
            return False
            
        # Data Type Validation
        for column, expected_type in self.schema.items():
            if not isinstance(record.get(column), expected_type):
                print(f"❌ Type Error: {column} must be {expected_type.__name__}")
                return False
        
        self.rows[pk] = record
        self._save()
        return record['id']

    def get_all(self):
        return list(self.rows.values())

    def update(self, pk, updates):
        pk = str(pk)
        if pk in self.rows:
            self.rows[pk].update(updates)
            self._save()
            return True
        return False

    def delete(self, pk):
        pk = str(pk)
        if pk in self.rows:
            del self.rows[pk]
            self._save()
            return True
        return False

class NjaanuaryGuard:
    def __init__(self):
        self.pocket_money = 10000
        # Support for declaring tables with data types
        self.expense_table = Table("expenses", {'id': int, 'item': str, 'amount': float, 'cat_id': int})
        self.category_table = Table("categories", {'id': int, 'name': str})
        
        # Seed categories for Relational JOIN support
        if not self.category_table.get_all():
            self.category_table.insert({'id': 1, 'name': 'Food'})
            self.category_table.insert({'id': 2, 'name': 'Fare'})
            self.category_table.insert({'id': 3, 'name': 'Others'})

    def get_total_spent(self):
        return sum(exp['amount'] for exp in self.expense_table.get_all())
    
    def get_budget_status(self):
        spent = self.get_total_spent()
        percent_used = (spent / self.pocket_money) * 100
        
        if percent_used < 40:
            return "✅ SAFE ZONE: You're doing great. Keep the discipline."
        elif percent_used < 70:
            return "⚠️ MBOGA ZONE: Time to switch to managu."
        elif percent_used < 90:
            return "🚨 WUEH!: You are officially in the Omena and Strong tea zone."
        else:
            return "💀 KIMEKURAMBA"
    
    def show_joined_history(self):
        """Joins Expenses with Categories based on cat_id"""
        expenses = self.expense_table.get_all()
        categories = self.category_table.rows
        
        print("\n" + "="*55)
        print(f"{'ID':<4} | {'Item':<15} | {'Price':<8} | {'Category'}")
        print("-" * 55)
        for exp in expenses:
            # The 'Join' happens here
            cat_info = categories.get(str(exp['cat_id']), {"name": "General"})
            print(f"{exp['id']:<4} | {exp['item']:<15} | {exp['amount']:<8.2f} | {cat_info['name']}")
        print("="*55 + "\n")

# --- USER INTERFACE ---
if __name__ == "__main__":
    db = NjaanuaryGuard()
    
    while True:
        print("🏦 NJAANUARI SURVIVAL GUIDE")
        print("1. Log Expense")
        print("2. View History")
        print("3. Check Balance")
        print("4. Edit/Delete")
        print("5. Exit")
        
        cmd = input("\nAction: ")

        if cmd == '1':
            try:
                item = input("What did you buy? ")
                amt = float(input("Amount: "))
                print("1:Food, 2:Fare, 3:Others")
                cid = int(input("Category ID: "))
                
                remaining = db.pocket_money - db.get_total_spent()
                if amt > remaining:
                    print(f"\n❌ DENIED: Balance is only {remaining} KES!")
                else:
                    new_id = db.expense_table.insert({'item': item, 'amount': amt, 'cat_id': cid})
                    print(f"✅ Success! Logged with ID: {new_id}")
            except ValueError: 
                print("❌ Invalid input! Please use numbers for amount and category.")

        elif cmd == '2':
            db.show_joined_history()

        elif cmd == '3':
            spent = db.get_total_spent()
            remaining = db.pocket_money - spent
            status = db.get_budget_status()
            print(f"\n Total Spent: {spent} KES")
            print(f" Remaining: {remaining} KES")
            print(f"STATUS: {status}\n")

        elif cmd == '4':
            sub = input("Type 'U' to update price or 'D' to delete: ").upper()
            eid = input("Enter record ID: ")
            if sub == 'U':
                try:
                    new_amt = float(input("Enter new price: "))
                    if db.expense_table.update(eid, {'amount': new_amt}):
                        print("✅ Price updated.")
                    else:
                        print("ID not found.")
                except ValueError: print("❌ Invalid price.")
            elif sub == 'D':
                if db.expense_table.delete(eid):
                    print("Record deleted.")
                else:
                    print("ID not found.")

        elif cmd == '5':
            print("Keep grinding! Hii mwezi itaisha tu")
            break