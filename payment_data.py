# payment_data.py
import json
import os

class PaymentData:
    def __init__(self, filepath):
        self.filepath = filepath
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.filepath):
            self.data = {"balance": 0.0, "transactions": []}
            self.save()
        else:
            self.load()

    def load(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {"balance": 0.0, "transactions": []}
            self.save()

    def save(self):
        directory = os.path.dirname(self.filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4)

    def add_income(self, amount, description="Income"):
        amount = float(amount)
        self.data["balance"] += amount
        self.data["transactions"].append({
            "type": "credit",
            "amount": amount,
            "description": description
        })
        self.save()

    def deduct_expense(self, amount, description="Expense"):
        amount = float(amount)
        if amount > self.data["balance"]:
            raise ValueError("Insufficient balance")
        self.data["balance"] -= amount
        self.data["transactions"].append({
            "type": "debit",
            "amount": amount,
            "description": description
        })
        self.save()

    def get_balance(self):
        return self.data.get("balance", 0.0)

    def get_transactions(self):
        return list(reversed(self.data.get("transactions", [])))  # newest first

    def export_json(self, target_path):
        # copy the saved JSON to a new target path (for backup/export)
        with open(self.filepath, 'r', encoding='utf-8') as src:
            content = src.read()
        directory = os.path.dirname(target_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        with open(target_path, 'w', encoding='utf-8') as dst:
            dst.write(content)
        return target_path
