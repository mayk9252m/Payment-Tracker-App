# payment_data.py
import json
import os
from sysconfig import get_path

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

    def import_excel(self, target_path):
        """
        Export all stored transactions to an Excel file. at target_path using openpyxl.
        Returns the saved file path on success or raise an exception on failure.
        """
        from openpyxl import Workbook

        # Create a workbook and a sheet
        wb = Workbook()
        ws = wb.active
        ws.title = "Transactions"

        # Header row
        ws.append(["Date", "Type", "Amount", "Description"])

        # Write rows (preserve insertion order as stored)
        for t in self.data.get("transactions", []):
            # Ensure values exist and convert amount to float for numeric cell
            data = t.get("date", "")
            ttype = t.get("type", "")
            # Some legacy records may store amount as string
            try:
                amount = float(t.get("amount", 0))
            except (ValueError, TypeError):
                amount = 0.0
            desc = t.get("description", "")
            ws.append([data, ttype, amount, desc])

        # Auto-adjust column widths
        for col in ws.columns:
            max_length = 0
            col = list(col)
            for cell in col:
                try:
                    val = str(cell.value)
                except Exception:
                    val = ""
                if val and len(val) > max_length:
                    max_length = len(val)
            adjusted_width = (max_length + 2)
            column_letter = col[0].column_letter
            ws.column_dimensions[column_letter].width = adjusted_width

    # Ensure target directory exists, then save
        import os
        directory = os.path.dirname(target_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        wb.save(target_path)
        return target_path