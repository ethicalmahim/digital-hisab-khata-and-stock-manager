import tkinter as tk
from tkinter import ttk, messagebox
from utils import helpers
from utils.dbmodels import Supplier


class SupplierStatementFrame:
    def __init__(self, parent, supplier, dbmanager):
        self.parent = parent
        self.supplier = supplier
        self.dbmanager = dbmanager

        supplier_statement_frame = tk.Frame(parent)
        supplier_statement_frame.grid(row=0, column=0)

        tk.Label(supplier_statement_frame, text=f"সাপ্লায়ারের নাম: {supplier.name}", font=("Arial", 15), ).grid(row=0,
                                                                                                             column=0,
                                                                                                             sticky=tk.W)
        tk.Label(supplier_statement_frame, text=f"বর্তমান ব্যালেন্স: {supplier.balance}",
                 font=("Arial", 15), ).grid(row=1, column=0, sticky=tk.W)
        columns = ("তারিখ", "সময়", "বিবরণ", "টাকা", "ব্যালেন্স")
        statement_style = ttk.Style(supplier_statement_frame)
        statement_style.configure("Treeview",
                                  font=("Segoe UI", 12),
                                  rowheight=30,
                                  borderwidth=0,
                                  highlightthickness=0)
        statement_style.configure("Treeview.Heading",
                                  background="#e0e0e0",
                                  foreground="black",
                                  font=("Segoe UI", 12, "bold"))

        self.statement_treeview = ttk.Treeview(supplier_statement_frame,
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

        scrollbar = ttk.Scrollbar(supplier_statement_frame, orient=tk.VERTICAL,
                                  command=self.statement_treeview.yview)
        scrollbar.grid(row=2, column=3, sticky=tk.NS, pady=20)
        self.statement_treeview.configure(yscrollcommand=scrollbar.set)

        self.load_customer_statement()

    def load_customer_statement(self):
        for i, statement in enumerate(self.supplier.statements):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.statement_treeview.insert("", tk.END, values=(statement.date,
                                                               statement.time.strftime("%I: %M %p"),
                                                               statement.description, statement.amount,
                                                               statement.balance), tags=tag)


class SuppliersFrame(tk.Frame):
    def __init__(self, parent, dbms):
        super().__init__(parent)
        self.dbmanager = dbms

        columns = ("সাপ্লায়ারের নাম", "ব্যালেন্স")
        self.supplier_details_treeview = ttk.Treeview(self, columns=columns, show="headings", height=21)
        for col in columns:
            self.supplier_details_treeview.heading(col, text=col)

        self.supplier_details_treeview.column("সাপ্লায়ারের নাম", width=624, stretch=False)
        self.supplier_details_treeview.column("ব্যালেন্স", width=200, stretch=False)
        self.supplier_details_treeview.grid(row=0, column=0, padx=(20, 0), pady=20)

        # Menu Options for Treeview
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="রিফ্রেশ", command=self.refresh)
        self.menu.add_command(label="ব্যালেন্স জমা", command=self.deposit_balance)
        self.menu.add_command(label="লেনেদেনের বিবরণ", command=self.statement_description)
        self.supplier_details_treeview.bind("<Button-3>", self.show_menu)

        self.supplier_details_treeview.tag_configure("evenrow", background="#f0f0f0")
        self.supplier_details_treeview.tag_configure("oddrow", background="#FFFFFF")

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.supplier_details_treeview.yview)
        scrollbar.grid(row=0, column=1, pady=20, sticky=tk.NS)
        self.supplier_details_treeview.config(yscrollcommand=scrollbar.set)

        # New Customer Entry
        new_supplier_entry_frame = tk.Frame(self, highlightbackground="#2c3e50", highlightthickness=2)
        new_supplier_entry_frame.grid(row=0, column=2, padx=20, pady=20, sticky=tk.N)

        tk.Label(new_supplier_entry_frame,
                 text="নতুন সাপ্লায়ার যোগ",
                 fg="white",
                 bg="#2c3e50",
                 width=19,
                 font=("Segoe UI", 18)).grid(row=0, column=0, pady=(0, 20), sticky=tk.NSEW)

        tk.Label(new_supplier_entry_frame,
                 text="সাপ্লায়ারের নাম",
                 bg="#2c3e50",
                 width=25,
                 fg="white", font=("Segoe UI", 12), ).grid(row=1, column=0, padx=5, sticky=tk.NSEW)
        self.supplier_name_entry = tk.Entry(new_supplier_entry_frame, font=("Segoe UI", 12))
        self.supplier_name_entry.grid(row=2, column=0, pady=(0, 10), padx=5, sticky=tk.EW)

        ttk.Button(new_supplier_entry_frame,
                   text="যোগ করুন", command=self.add_supplier,
                   ).grid(row=7, column=0, padx=5, pady=(0, 10), sticky=tk.NSEW)

        self.refresh()

    def add_supplier(self):
        supplier = self.dbmanager.Supplier(name=self.supplier_name_entry.get())
        does_exist = bool(self.dbmanager.get_supplier_by_name(supplier.name))

        if does_exist:
            messagebox.showerror(
                title="ডুপ্লিকেট",
                message="সাপ্লায়ার ইতিমধ্যেই বিদ্যমান !"
            )
            return

        if not supplier.name:
            messagebox.showerror(
                title="অসম্পূর্ণ তথ্য",
                message="সাপ্লায়ারের নাম পূরণ করতে হবে !"
            )
            return

        self.dbmanager.add_supplier(supplier)
        self.refresh()

    def deposit_balance(self):
        def update_supplier_with_new_balance():
            received_amount = float(payment_received_entry.get())
            supplier.balance += received_amount
            received_amount_copy = received_amount

            due_purchases = [purchase for purchase in supplier.orders if purchase.due > 0]
            paid_purchases_list = []
            for purchase in due_purchases:
                if received_amount == 0:
                    break

                payable = min(received_amount, purchase.due)

                purchase.paid += payable
                purchase.due -= payable
                paid_purchases_list.append(purchase.id)
                received_amount -= payable

                supplier_due_payment_history = self.dbmanager.SupplierDuePayment(amount=payable)
                purchase.payment_history.append(supplier_due_payment_history)

            statement = self.dbmanager.SupplierStatement(supplier_id=supplier.id,
                                                         description=f"জমা (বাকী পরিশোধঃ ক্রয় চালান - {paid_purchases_list})",
                                                         amount=received_amount_copy, balance=supplier.balance)
            supplier.statements.append(statement)
            self.dbmanager.update_changes()
            deposit_win.destroy()
            self.refresh()

        supplier_iid = self.supplier_details_treeview.selection()[0]
        supplier_name = self.supplier_details_treeview.item(supplier_iid, "values")[0]
        supplier = self.dbmanager.get_supplier_by_name(supplier_name)

        deposit_win = tk.Toplevel(self)
        deposit_win.title("ব্যালেন্স জমা")
        deposit_win.config(padx=20, pady=20)

        self.center_window(deposit_win, 180, 290)

        # Invoice No
        tk.Label(deposit_win, text=f"সাপ্লায়ারের নাম", font=("Segoe UI", 12, "bold"),
                 anchor=tk.W, ).grid(row=0, column=0, sticky=tk.W)
        tk.Label(deposit_win, text=":", font=("Segoe UI", 12, "bold"),
                 anchor=tk.W, ).grid(row=0, column=1, sticky=tk.W)
        tk.Label(deposit_win, text=f"{supplier.name}", font=("Segoe UI", 12, "bold"),
                 anchor=tk.W, ).grid(row=0, column=2, sticky=tk.W)

        # Due
        tk.Label(deposit_win, text=f"বর্তমান ব্যালেন্স", fg="red", font=("Segoe UI", 12, "bold"),
                 anchor=tk.W, ).grid(row=1, column=0, sticky=tk.W)
        tk.Label(deposit_win, text=":", fg="red", font=("Segoe UI", 12, "bold"),
                 anchor=tk.W, ).grid(row=1, column=1, sticky=tk.W)
        tk.Label(deposit_win, text=f"{supplier.balance}", fg="red", font=("Segoe UI", 12, "bold"),
                 anchor=tk.W, ).grid(row=1, column=2, sticky=tk.W)

        tk.Label(deposit_win, text="ব্যালেন্স জমা", font=("Segoe UI", 12, "bold"), anchor=tk.W, ).grid(row=2,
                                                                                                       column=0,
                                                                                                       sticky=tk.W)
        tk.Label(deposit_win, text=":", font=("Segoe UI", 12, "bold"), anchor=tk.W, ).grid(row=2, column=1,
                                                                                           sticky=tk.W)
        payment_received_entry = tk.Entry(deposit_win, width=10, font=("Segoe UI", 12))
        payment_received_entry.focus_set()
        payment_received_entry.grid(row=2, column=2)
        tk.Button(deposit_win, text="নিশ্চিত করুন", command=update_supplier_with_new_balance).grid(row=3, column=1,
                                                                                                   columnspan=2,
                                                                                                   pady=10,
                                                                                                   sticky=tk.NSEW)
        deposit_win.transient()
        deposit_win.grab_set()  # modal behavior
        deposit_win.resizable(False, False)

    def statement_description(self):
        supplier_iid = self.supplier_details_treeview.selection()[0]
        supplier_name = self.supplier_details_treeview.item(supplier_iid, "values")[0]
        supplier = self.dbmanager.get_supplier_by_name(supplier_name)

        supplier_statement_window = tk.Toplevel(self)
        supplier_statement_window.title("সাপ্লায়ারের লেনদেনের বিবরণ")
        supplier_statement_window.config(padx=20, pady=20)
        self.center_window(supplier_statement_window, 500, 955)
        supplier_statement_window.transient()
        supplier_statement_window.grab_set()  # modal behavior
        supplier_statement_window.resizable(False, False)

        SupplierStatementFrame(supplier_statement_window, supplier, self.dbmanager)

    def refresh(self):
        self.supplier_details_treeview.delete(*self.supplier_details_treeview.get_children())
        for i, supplier in enumerate(self.dbmanager.get_all_suppliers()):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.supplier_details_treeview.insert("", tk.END,
                                                  values=(supplier.name, supplier.balance),
                                                  tags=tag)
        self.supplier_name_entry.delete(0, tk.END)

    def show_menu(self, event):
        iid = self.supplier_details_treeview.identify_row(event.y)
        if iid:
            self.supplier_details_treeview.selection_set(iid)
            self.menu.tk_popup(event.x_root, event.y_root)

    def center_window(self, win, custom_height, custom_width):
        win.update_idletasks()
        width = custom_width
        height = custom_height
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")
