import tkinter as tk
from tkinter import ttk, messagebox
from utils import helpers


class CustomerStatementFrame:
    def __init__(self, parent, customer, dbmanager):
        self.parent = parent
        self.customer = customer
        self.dbmanager = dbmanager

        customer_statement_frame = tk.Frame(parent)
        customer_statement_frame.grid(row=0, column=0)

        tk.Label(customer_statement_frame, text=f"গ্রাহকের নাম: {customer.name}",
                 font=("Arial", 15)).grid(row=0, column=0, sticky=tk.W)
        tk.Label(customer_statement_frame, text=f"গ্রাহকের মোবাইল: {customer.phone}",
                 font=("Arial", 15), ).grid(row=0, column=1, sticky=tk.W)
        tk.Label(customer_statement_frame, text=f"গ্রাহকের ঠিকানা: {customer.address}",
                 font=("Arial", 15), ).grid(
            row=1, column=0, sticky=tk.W)
        tk.Label(customer_statement_frame, text=f"বর্তমান ব্যালেন্স: {customer.balance}",
                 font=("Arial", 15), ).grid(row=1, column=1, sticky=tk.W)
        columns = ("তারিখ", "সময়", "বিবরণ", "টাকা", "ব্যালেন্স")
        statement_style = ttk.Style(customer_statement_frame)
        statement_style.configure("Treeview",
                                  font=("Segoe UI", 12),
                                  rowheight=30,
                                  borderwidth=0,
                                  highlightthickness=0)
        statement_style.configure("Treeview.Heading",
                                  background="#e0e0e0",
                                  foreground="black",
                                  font=("Segoe UI", 12, "bold"))

        self.statement_treeview = ttk.Treeview(customer_statement_frame,
                                               columns=columns,
                                               show="headings",
                                               height=10,
                                               style="Treeview")
        self.statement_treeview.tag_configure("evenrow", background="#f0f0f0")
        self.statement_treeview.tag_configure("oddrow", background="#FFFFFF")

        for col in columns:
            self.statement_treeview.heading(col, text=col)
        self.statement_treeview.column("তারিখ", width=120, stretch=False, )
        self.statement_treeview.column("সময়", width=120, stretch=False, )
        self.statement_treeview.column("বিবরণ", width=350, stretch=False, )
        self.statement_treeview.column("টাকা", width=150, stretch=False, )
        self.statement_treeview.column("ব্যালেন্স", width=150, stretch=False, )

        self.statement_treeview.grid(row=2, column=0, columnspan=2, pady=20)

        scrollbar = ttk.Scrollbar(customer_statement_frame, orient=tk.VERTICAL,
                                  command=self.statement_treeview.yview)
        scrollbar.grid(row=2, column=3, sticky=tk.NS, pady=20)
        self.statement_treeview.configure(yscrollcommand=scrollbar.set)

        self.load_customer_statement()

    def load_customer_statement(self):
        for i, statement in enumerate(self.customer.statements):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.statement_treeview.insert("", tk.END, values=(statement.date,
                                                               statement.time.strftime("%I: %M %p"),
                                                               statement.description, statement.amount,
                                                               statement.balance), tags=tag)


class CustomersFrame(tk.Frame):
    def __init__(self, parent, dbms):
        super().__init__(parent)
        self.dbmanager = dbms

        columns = ("গ্রাহকের নাম", "মোবাইল নম্বর", "ঠিকানা", "ব্যালেন্স")
        self.customer_details_treeview = ttk.Treeview(self, columns=columns, show="headings", height=21)

        for col in columns:
            self.customer_details_treeview.heading(col, text=col)

        self.customer_details_treeview.column("গ্রাহকের নাম", width=240, stretch=False)
        self.customer_details_treeview.column("মোবাইল নম্বর", width=124, stretch=False)
        self.customer_details_treeview.column("ঠিকানা", width=340, stretch=False)
        self.customer_details_treeview.column("ব্যালেন্স", width=120, stretch=False)
        self.customer_details_treeview.grid(row=0, column=0, padx=(20, 0), pady=20)

        # Menu Options for Treeview
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="রিফ্রেশ", command=self.refresh)
        self.menu.add_command(label="ব্যালেন্স জমা", command=self.deposit_balance)
        self.menu.add_command(label="লেনেদেনের বিবরণ", command=self.statement_description)
        self.customer_details_treeview.bind("<Button-3>", self.show_menu)

        self.customer_details_treeview.tag_configure("evenrow", background="#f0f0f0")
        self.customer_details_treeview.tag_configure("oddrow", background="#FFFFFF")

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.customer_details_treeview.yview)
        scrollbar.grid(row=0, column=1, pady=20, sticky=tk.NS)
        self.customer_details_treeview.config(yscrollcommand=scrollbar.set)

        # New Customer Entry
        new_customer_entry_frame = tk.Frame(self, highlightbackground="#2c3e50", highlightthickness=2)
        new_customer_entry_frame.grid(row=0, column=2, padx=20, pady=20, sticky=tk.N)

        tk.Label(new_customer_entry_frame,
                 text="নতুন গ্রাহক যোগ করুন",
                 fg="white",
                 bg="#2c3e50",
                 width=19,
                 font=("Segoe UI", 18)).grid(row=0, column=0, pady=(0, 20), sticky=tk.NSEW)

        tk.Label(new_customer_entry_frame,
                 text="গ্রাহকের নাম",
                 bg="#2c3e50",
                 width=25,
                 fg="white", font=("Segoe UI", 12), ).grid(row=1, column=0, padx=5, sticky=tk.NSEW)
        self.customer_name_entry = tk.Entry(new_customer_entry_frame, font=("Segoe UI", 12))
        self.customer_name_entry.grid(row=2, column=0, pady=(0, 10), padx=5, sticky=tk.EW)

        tk.Label(new_customer_entry_frame,
                 text="গ্রাহকের মোবাইল নম্বর",
                 bg="#2c3e50",
                 fg="white",
                 font=("Segoe UI", 12)).grid(row=3, column=0, padx=5, sticky=tk.NSEW)
        self.customer_phone_entry = tk.Entry(new_customer_entry_frame, validate="key",
                                             validatecommand=(self.register(helpers.validate_phone_number), "%P"),
                                             font=("Segoe UI", 12))
        self.customer_phone_entry.grid(row=4, column=0, pady=(0, 10), padx=5, sticky=tk.EW)

        tk.Label(new_customer_entry_frame,
                 text="গ্রাহকের ঠিকানা",
                 fg="white",
                 bg="#2c3e50",
                 font=("Segoe UI", 12)).grid(row=5, column=0, padx=5, sticky=tk.NSEW)
        self.customer_address_entry = tk.Entry(new_customer_entry_frame, font=("Segoe UI", 12))
        self.customer_address_entry.grid(row=6, column=0, padx=5, pady=(0, 10), sticky=tk.EW)

        ttk.Button(new_customer_entry_frame,
                   text="গ্রাহক যোগ করুন", command=self.add_customer,
                   ).grid(row=7, column=0, padx=5, pady=(0, 10), sticky=tk.NSEW)

        self.refresh()

    def add_customer(self):
        customer = self.dbmanager.Customer(name=self.customer_name_entry.get(),
                                           phone=self.customer_phone_entry.get(),
                                           address=self.customer_address_entry.get()
                                           )
        does_exist = bool(self.dbmanager.get_customer_by_phone(customer.phone))
        if does_exist:
            messagebox.showerror(
                title="ডুপ্লিকেট",
                message="গ্রাহক ইতিমধ্যেই বিদ্যমান !"
            )
            return

        if not all([customer.name, customer.phone, customer.address]):
            messagebox.showerror(
                title="অসম্পূর্ণ তথ্য",
                message="গ্রাহকের নাম, মোবাইল নম্বর ও ঠিকানা সবই পূরণ করতে হবে !"
            )
            return

        self.dbmanager.add_customer(customer)
        self.refresh()

    def deposit_balance(self):
        def update_customer_with_new_balance():
            received_amount = float(payment_received_entry.get())
            customer.balance += received_amount
            received_amount_copy = received_amount

            due_invoices = [invoice for invoice in customer.purchases if invoice.due > 0]
            paid_invoices_list = []
            for invoice in due_invoices:
                if received_amount == 0:
                    break

                payable = min(received_amount, invoice.due)

                invoice.paid += payable
                invoice.due -= payable
                paid_invoices_list.append(invoice.id)
                received_amount -= payable

                customer_due_payment_history = self.dbmanager.CustomerDuePayment(amount=payable)
                invoice.payment_history.append(customer_due_payment_history)

            statement = self.dbmanager.CustomerStatement(customer_id=customer.id,
                                                         description=f"জমা (বাকী পরিশোধঃ বিক্রয় চালান - {paid_invoices_list})",
                                                         amount=received_amount_copy, balance=customer.balance)
            customer.statements.append(statement)
            self.dbmanager.update_changes()
            deposit_win.destroy()
            self.refresh()

        customer_iid = self.customer_details_treeview.selection()[0]
        customer_phone = self.customer_details_treeview.item(customer_iid, "values")[1]
        customer = self.dbmanager.get_customer_by_phone(customer_phone)

        deposit_win = tk.Toplevel(self)
        deposit_win.title("ব্যালেন্স জমা")
        deposit_win.config(padx=20, pady=20)

        self.center_window(deposit_win, 215, 450)

        # Invoice No
        tk.Label(deposit_win, text=f"গ্রাহকের নাম", font=("Segoe UI", 12, "bold"),
                 anchor=tk.W, ).grid(row=0, column=0, sticky=tk.W)
        tk.Label(deposit_win, text=":", font=("Segoe UI", 12, "bold"),
                 anchor=tk.W, ).grid(row=0, column=1, sticky=tk.W)
        tk.Label(deposit_win, text=f"{customer.name}", font=("Segoe UI", 12, "bold"),
                 anchor=tk.W, ).grid(row=0, column=2, sticky=tk.W)

        # Total Payable
        tk.Label(deposit_win, text=f"গ্রাহকের মোবাইল", font=("Segoe UI", 12, "bold"),
                 anchor=tk.W, ).grid(row=1, column=0, sticky=tk.W)
        tk.Label(deposit_win, text=":", font=("Segoe UI", 12, "bold"),
                 anchor=tk.W, ).grid(row=1, column=1, sticky=tk.W)
        tk.Label(deposit_win, text=f"{customer.phone}", font=("Segoe UI", 12, "bold"),
                 anchor=tk.W, ).grid(row=1, column=2, sticky=tk.W)

        # Total Payable
        tk.Label(deposit_win, text=f"গ্রাহকের ঠিকানা", font=("Segoe UI", 12, "bold"),
                 anchor=tk.W, ).grid(row=2, column=0, sticky=tk.W)
        tk.Label(deposit_win, text=":", font=("Segoe UI", 12, "bold"),
                 anchor=tk.W, ).grid(row=2, column=1, sticky=tk.W)
        tk.Label(deposit_win, text=f"{customer.address}", font=("Segoe UI", 12, "bold"),
                 anchor=tk.W, ).grid(row=2, column=2, sticky=tk.W)

        # Due
        tk.Label(deposit_win, text=f"বর্তমান ব্যালেন্স", fg="red", font=("Segoe UI", 12, "bold"),
                 anchor=tk.W, ).grid(row=3, column=0, sticky=tk.W)
        tk.Label(deposit_win, text=":", fg="red", font=("Segoe UI", 12, "bold"),
                 anchor=tk.W, ).grid(row=3, column=1, sticky=tk.W)
        tk.Label(deposit_win, text=f"{customer.balance}", fg="red", font=("Segoe UI", 12, "bold"),
                 anchor=tk.W, ).grid(row=3, column=2, sticky=tk.W)

        tk.Label(deposit_win, text="ব্যালেন্স জমা",
                 font=("Segoe UI", 12, "bold"), anchor=tk.W).grid(row=4, column=0, sticky=tk.W)
        tk.Label(deposit_win, text=":", font=("Segoe UI", 12, "bold"),
                 anchor=tk.W).grid(row=4, column=1, sticky=tk.W)

        payment_received_entry = tk.Entry(deposit_win, width=10, font=("Segoe UI", 12))
        payment_received_entry.focus_set()
        payment_received_entry.grid(row=4, column=2)

        tk.Button(deposit_win, text="নিশ্চিত করুন",
                  command=update_customer_with_new_balance).grid(row=5, column=1, columnspan=2, pady=10, sticky=tk.NSEW)

        deposit_win.transient()
        deposit_win.grab_set()  # modal behavior
        deposit_win.resizable(False, False)

    def statement_description(self):
        customer_iid = self.customer_details_treeview.selection()[0]
        customer_phone = self.customer_details_treeview.item(customer_iid, "values")[1]
        customer = self.dbmanager.get_customer_by_phone(customer_phone)

        customer_statement_window = tk.Toplevel(self)
        customer_statement_window.title("গ্রাহকের লেনদেনের বিবরণ")
        customer_statement_window.config(padx=20, pady=20)
        self.center_window(customer_statement_window, 500, 955)
        customer_statement_window.transient()
        customer_statement_window.grab_set()  # modal behavior
        customer_statement_window.resizable(False, False)

        CustomerStatementFrame(customer_statement_window, customer, self.dbmanager)

    def refresh(self):
        self.customer_details_treeview.delete(*self.customer_details_treeview.get_children())
        for i, customer in enumerate(self.dbmanager.get_all_customers()):
            tag = "evenrow" if i % 2 == 0 else "oddrow"

            self.customer_details_treeview.insert("", tk.END,
                                                  values=(customer.name, customer.phone, customer.address,
                                                          customer.balance), tags=tag)
        self.customer_name_entry.delete(0, tk.END)
        self.customer_phone_entry.delete(0, tk.END)
        self.customer_address_entry.delete(0, tk.END)

    def show_menu(self, event):
        iid = self.customer_details_treeview.identify_row(event.y)
        if iid:
            self.customer_details_treeview.selection_set(iid)
            self.menu.tk_popup(event.x_root, event.y_root)

    def center_window(self, win, custom_height, custom_width):
        win.update_idletasks()
        width = custom_width
        height = custom_height
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")
