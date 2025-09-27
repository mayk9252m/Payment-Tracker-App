# main.py
import os
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import mainthread
from kivy.utils import platform
from datetime import datetime

from payment_data import PaymentData

KV = Builder.load_file('payment.kv')

def default_data_path(app):
    # use App.user_data_dir (set by Kivy) for persistent storage
    return os.path.join(app.user_data_dir, 'payment_data.json')

class TransactionRow(BoxLayout):
    # description text (eg., "Groceries" or  "salary")
    desc = StringProperty('')
    # human-reabable amount (eg., "+500.00" or "-120.00")
    amount = StringProperty('')
    # "credit" or "debit"
    ttype = StringProperty('')
    # date-time string (eg., "2025-09-27 11:15")
    date = StringProperty('')

class TrackerUI(BoxLayout):
    balance_text = StringProperty('Rs 0.00')
    transactions = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        data_path = default_data_path(app)
        self.store = PaymentData(data_path)
        self.refresh_view()

    def refresh_view(self):
        # update the balance label at the top
        bal = self.store.get_balance()
        self.balance_text = f"Rs {bal:.2f}"

        # get transactions newest first
        txns = self.store.get_transactions()
        # keep a linghtweight list for any other uses
        formatted = []
        for t in txns:
            sign_amount = f"+{t['amount']:.2f}" if t['type'] =='credit' else f" -{t['amount']:.2f}"
            formatted.append({
                "desc": t.get("description", ""),
                "amount": sign_amount,
                "ttype": t.get("type", ""),
                "date": t.get("date", "")
            })
        self.transactions = formatted

    def add_income(self):
        amt = self.ids.input_amount.text.strip()
        desc = self.ids.input_desc.text.strip() or "Income"
        if not amt:
            self.ids.status.text = "Enter amount"
            return
        try:
            amt_f = float(amt)
            txn = {"type":"credit","amount":amt_f,"description":desc,"date":datetime.now().strftime("%Y-%m-%d %H:%M")}
            # use PaymentData methods
            self.store.add_income(amt_f, desc)
            # ensure date saved as well: append date manually to last txn
            self.store.data["transactions"][-1].update({"date": txn["date"]})
            self.store.save()
            self.ids.input_amount.text = ""
            self.ids.input_desc.text = ""
            self.ids.status.text = "Income added"
            self.refresh_view()
        except Exception as e:
            self.ids.status.text = f"Error: {str(e)}"

    def deduct_expense(self):
        amt = self.ids.input_amount.text.strip()
        desc = self.ids.input_desc.text.strip() or "Expense"
        if not amt:
            self.ids.status.text = "Enter amount"
            return
        try:
            amt_f = float(amt)
            # will raise ValueError if insufficient
            self.store.deduct_expense(amt_f, desc)
            # add date
            self.store.data["transactions"][-1].update({"date": datetime.now().strftime("%Y-%m-%d %H:%M")})
            self.store.save()
            self.ids.input_amount.text = ""
            self.ids.input_desc.text = ""
            self.ids.status.text = "Expense deducted"
            self.refresh_view()
        except ValueError as ve:
            self.ids.status.text = str(ve)
        except Exception as e:
            self.ids.status.text = f"Error: {str(e)}"

    def clear_all(self):
        # reset data
        self.store.data = {"balance": 0.0, "transactions": []}
        self.store.save()
        self.ids.status.text = "All data cleared"
        self.refresh_view()

    def export_data(self):
        # try to export to /sdcard/Download on Android, else to user_data_dir
        target = None
        if platform == 'android':
            # common external path
            external = '/sdcard/Download'
            if os.path.exists(external):
                target = os.path.join(external, f'payment_data_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        if not target:
            target = os.path.join(App.get_running_app().user_data_dir, f'payment_data_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        try:
            path = self.store.export_json(target)
            self.ids.status.text = f"Export saved: {path}"
        except Exception as e:
            self.ids.status.text = f"Export failed: {e}"

class PaymentTrackerApp(App):
    def build(self):
        self.title = "Payment Tracker"
        return TrackerUI()

if __name__ == '__main__':
    PaymentTrackerApp().run()
