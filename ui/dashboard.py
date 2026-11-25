import tkinter as tk
from tkinter import ttk

CARD_WIDTH = 17


class DashboardFrame(tk.Frame):
    def __init__(self, parent, dbmanager):
        super().__init__(parent)
        self.configure(padx=20, pady=20)
        self.parent = parent
        self.dbmanager = dbmanager

        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="রিফ্রেশ", command=self.refresh)
        self.bind_all("<Button-3>", self.show_menu)

        # Today Data ---------------------------------------------------------------------------------------------------
        today_data = tk.Frame(self)
        today_data.grid(row=0, column=0)

        # Today Sales
        today_sales = tk.Frame(today_data, bg="#2c3e50")
        today_sales.grid(row=0, column=0, padx=(0, 10))

        self.today_sales_count = tk.IntVar(value=0)
        tk.Label(today_sales, text="আজকের\nবিক্রয়সংখ্যা", width=CARD_WIDTH, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold")).grid(row=0, column=0)
        tk.Label(today_sales, textvariable=self.today_sales_count, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold")).grid(row=1, column=0)

        # Today Sales Value
        today_sales_value = tk.Frame(today_data, bg="#2c3e50")
        today_sales_value.grid(row=0, column=1, padx=10)

        self.today_sales_value = tk.DoubleVar(value=0)
        tk.Label(today_sales_value, text="আজকের\nবিক্রয়", width=CARD_WIDTH, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold")).grid(row=0, column=0)
        tk.Label(today_sales_value, textvariable=self.today_sales_value, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold")).grid(row=1, column=0)

        # Today Due Received
        today_due_received = tk.Frame(today_data, bg="#2c3e50")
        today_due_received.grid(row=0, column=2, padx=10)

        self.today_due_received = tk.DoubleVar(value=0)
        tk.Label(today_due_received, text="আজকের বাকী\nসংগ্রহ", width=CARD_WIDTH, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold")).grid(row=0, column=0)
        tk.Label(today_due_received, textvariable=self.today_due_received, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold")).grid(row=1, column=0)

        # Today Due Sales Value
        today_due_sales_value = tk.Frame(today_data, bg="#2c3e50")
        today_due_sales_value.grid(row=0, column=3, padx=10)
        self.today_due_sales_value = tk.DoubleVar(value=0)
        tk.Label(today_due_sales_value, text="আজকের বাকী\nবিক্রয়", width=CARD_WIDTH, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold")).grid(row=0, column=0)
        tk.Label(today_due_sales_value, textvariable=self.today_due_sales_value, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold"), ).grid(row=1, column=0)

        # Today Sales Return Value
        today_sales_return_value = tk.Frame(today_data, bg="#2c3e50")
        today_sales_return_value.grid(row=1, column=0, padx=(0, 10))

        self.today_sales_return_value = tk.DoubleVar(value=0)
        tk.Label(today_sales_return_value, text="আজকের\nপণ্য ফেরত", width=CARD_WIDTH, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold")).grid(row=0, column=0)
        tk.Label(today_sales_return_value, textvariable=self.today_sales_return_value, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold"), ).grid(row=1, column=0)

        # Today Purchases Value
        today_purchases_value = tk.Frame(today_data, bg="#2c3e50")
        today_purchases_value.grid(row=1, column=1, padx=10)

        self.today_purchases_value = tk.DoubleVar(value=0)
        tk.Label(today_purchases_value, text="আজকের\nক্রয়", width=CARD_WIDTH, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold"), ).grid(row=0, column=0)
        tk.Label(today_purchases_value, textvariable=self.today_purchases_value, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold"), ).grid(row=1, column=0)

        # Today Supplier Due Payment
        today_supplier_due_payment = tk.Frame(today_data, bg="#2c3e50")
        today_supplier_due_payment.grid(row=1, column=2, padx=10, pady=20)

        self.today_supplier_due_payment = tk.DoubleVar(value=0)
        tk.Label(today_supplier_due_payment, text="আজকের বাকী\nপরিশোধ", width=CARD_WIDTH, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold")).grid(row=0, column=0)
        tk.Label(today_supplier_due_payment, textvariable=self.today_supplier_due_payment, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold"), ).grid(row=1, column=0)

        # Today Expenses Value
        today_expenses_value = tk.Frame(today_data, bg="#2c3e50")
        today_expenses_value.grid(row=1, column=3, padx=10, pady=20)

        self.today_expenses_value = tk.DoubleVar(value=0)
        tk.Label(today_expenses_value, text="আজকের\nখরচ", width=CARD_WIDTH, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold"), ).grid(row=0, column=0)
        tk.Label(today_expenses_value, textvariable=self.today_expenses_value, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold"), ).grid(row=1, column=0)

        # Today Profit
        today_profit = tk.Frame(today_data, bg="#2c3e50")
        today_profit.grid(row=2, column=0, padx=(0, 10), pady=(0, 20))

        self.today_profit = tk.DoubleVar(value=0)
        tk.Label(today_profit, text="আজকের\nলাভ", width=CARD_WIDTH, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold"), ).grid(row=0, column=0)
        tk.Label(today_profit, textvariable=self.today_profit, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold"), ).grid(row=1, column=0)
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=1, column=0, pady=(0, 10), sticky=tk.EW)

        # Business Data ---------------------------------------------------------------------------------------------------
        business_data = tk.Frame(self)
        business_data.grid(row=2, column=0, sticky=tk.W)

        # Total Valuation
        total_product_valuation = tk.Frame(business_data, bg="#2c3e50")
        total_product_valuation.grid(row=0, column=0, pady=10, padx=(0, 10), sticky=tk.W)

        self.total_product_valuation = tk.DoubleVar(value=0)
        tk.Label(total_product_valuation, text="মজুদকৃত পণ্যের\nমূল্য", width=CARD_WIDTH, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold")).grid(row=0, column=0)
        tk.Label(total_product_valuation, textvariable=self.total_product_valuation, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold")).grid(row=1, column=0)

        # Total Customer Due
        total_customer_due = tk.Frame(business_data, bg="#2c3e50")
        total_customer_due.grid(row=0, column=1, pady=10, padx=(0, 10), sticky=tk.W)

        self.total_customer_due = tk.DoubleVar(value=0)
        tk.Label(total_customer_due, text="গ্রাহকের\nবাকী", width=CARD_WIDTH, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold"), ).grid(row=0, column=0)
        tk.Label(total_customer_due, textvariable=self.total_customer_due, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold"), ).grid(row=1, column=0)

        # Total Supplier Due
        total_supplier_due = tk.Frame(business_data, bg="#2c3e50")
        total_supplier_due.grid(row=0, column=2, pady=10, padx=(0, 10), sticky=tk.W)

        self.total_supplier_due = tk.DoubleVar(value=0)
        tk.Label(total_supplier_due, text="সাপ্লায়ারের\nবাকী", width=CARD_WIDTH, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold")).grid(row=0, column=0)
        tk.Label(total_supplier_due, textvariable=self.total_supplier_due, bg="#2c3e50", fg="white",
                 font=("Arial", 18, "bold")).grid(row=1, column=0)

        self.refresh()

    def refresh(self):
        self.today_sales_count.set(self.get_today_sale_count())
        self.today_sales_value.set(self.get_today_sales_value())
        self.today_due_received.set(self.get_today_due_received())
        self.today_due_sales_value.set(self.get_today_due_sales_value())
        self.today_sales_return_value.set(self.get_today_sales_return_value())
        self.today_purchases_value.set(self.get_today_purchases_value())
        self.today_supplier_due_payment.set(self.get_today_supplier_due_payment())
        self.today_expenses_value.set(self.get_today_expenses_value())
        self.total_product_valuation.set(self.get_total_products_valuation())
        self.total_customer_due.set(self.get_total_customer_due())
        self.total_supplier_due.set(self.get_total_supplier_due())
        self.today_profit.set(self.get_today_profit())

    def get_today_sale_count(self):
        today_sales = self.dbmanager.get_today_sales()
        return len(today_sales)

    def get_today_sales_value(self):
        today_sales_value = 0
        today_sales = self.dbmanager.get_today_sales()
        for today_sale in today_sales:
            today_sales_value += today_sale.total_payable

        return round(today_sales_value, 2)

    def get_today_due_received(self):
        today_due_received_obj = self.dbmanager.today_due_received()
        received_due_payment = 0
        for obj in today_due_received_obj:
            received_due_payment += obj.amount

        return round(received_due_payment, 2)

    def get_today_due_sales_value(self):
        today_due_sales_value = 0
        today_sales = self.dbmanager.get_today_sales()
        for today_sale in today_sales:
            today_due_sales_value += today_sale.due

        return round(today_due_sales_value, 2)

    def get_today_sales_return_value(self):
        refund_amount = 0
        today_sales_returns = self.dbmanager.today_sales_returns()
        for sales_return in today_sales_returns:
            refund_amount += sales_return.refund_amount
        return round(refund_amount, 2)

    def get_today_purchases_value(self):
        purchases_value = 0
        today_purchases = self.dbmanager.today_purchases()
        for today_purchase in today_purchases:
            purchases_value += today_purchase.paid

        return round(purchases_value, 2)

    def get_today_supplier_due_payment(self):
        today_paid = 0
        today_payments = self.dbmanager.today_supplier_payments()
        for today_payment in today_payments:
            today_paid += today_payment.amount

        return round(today_paid, 2)

    def get_today_expenses_value(self):
        today_expenses_amount = 0
        today_expenses_obj = self.dbmanager.today_expenses()
        for today_expense in today_expenses_obj:
            today_expenses_amount += today_expense.amount

        return round(today_expenses_amount, 2)

    def get_total_products_valuation(self):
        products_valuation = 0
        all_products = self.dbmanager.get_all_products()
        for product in all_products:
            product_valuation = product.sell_unit_price * product.current_stock
            products_valuation += product_valuation

        return round(products_valuation, 2)

    def get_total_customer_due(self):
        total_customer_due = 0
        all_sales = self.dbmanager.get_all_sales()
        for sale in all_sales:
            total_customer_due += sale.due

        return round(total_customer_due, 2)

    def get_total_supplier_due(self):
        total_supplier_due = 0
        all_due_purchases = self.dbmanager.get_due_purchases()
        for purchase in all_due_purchases:
            total_supplier_due += purchase.due

        return round(total_supplier_due, 2)

    def get_today_profit(self):
        today_profit = 0
        today_sales = self.dbmanager.get_today_sales()
        for today_sale in today_sales:
            for item in today_sale.items:
                today_profit += (item.unit_price * item.quantity) - (item.product.purchase_rate * item.quantity)
        return round(today_profit, 2)

    def show_menu(self, event):
        widget = event.widget

        # Check whether the clicked widget is inside DashboardFrame
        while widget:
            if widget == self:
                self.menu.tk_popup(event.x_root, event.y_root)
                return

            parent_name = widget.winfo_parent()
            if not parent_name:
                break

            widget = widget.nametowidget(parent_name)
