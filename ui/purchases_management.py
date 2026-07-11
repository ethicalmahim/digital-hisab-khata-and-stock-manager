import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from utils.helpers import AutoCompleteEntry, AutoCompleteEntryForSuppliers
from tkinter.font import Font
from utils import helpers

# NewPurchase
CODE_COL_INDEX = 0
CATEGORY_COL_INDEX = 1
PRODUCT_COL_INDEX = 2
QTY_COL_INDEX = 3
UNIT_COL_INDEX = 4
BASE_QTY_COL_INDEX = 5
RATE_COL_INDEX = 6
SUBTOTAL_COL_INDEX = 7

# PurchasesFrame
DUE_AMT_INDEX = 6
DEFAULT_PURCHASE_STATUS = "অগৃহীত"

# Purchase Return Frame
SOLD_QTY_COL_INDEX = 2
RF_RATE_COL_INDEX = 4
RETURN_QTY_P_COL_INDEX = 5
RETURNED_QTY_N_COL_INDEX = 6
REFUND_AMT_COL_INDEX = 7


class NewPurchase(tk.Frame):
    def __init__(self, parent, dbmanager):
        super().__init__(parent)
        self.configure(padx=20, pady=20)
        self.parent = parent
        self.dbmanager = dbmanager

        # Product Selection Frame--------------------------------------------------------------------------------------------
        ## Upper Part
        product_selection_frame = tk.Frame(self)
        product_selection_frame.grid(row=0, column=0)

        tk.Label(product_selection_frame, text="পণ্য:", font=("Arial", 15), ).grid(row=0, column=0, sticky=tk.W)
        self.product_name_search_entry = AutoCompleteEntry(product_selection_frame, db_path="database/database.db",
                                                           font=("Arial", 15), width=43)
        self.product_name_search_entry.grid(row=0, column=1, sticky=tk.EW)

        tk.Label(product_selection_frame, text="পরিমাণ:", font=Font(size=15), ).grid(row=0, column=2)
        self.quantity = tk.Spinbox(
            product_selection_frame, from_=1, to=100000, font=("Arial", 15), width=7,
            validate="key", validatecommand=(product_selection_frame.register(helpers.is_float), "%P",)
        )
        self.quantity.grid(row=0, column=3)

        ttk.Button(product_selection_frame, text="যোগ করুন", command=self.add_item).grid(row=0, column=4)

        ## Lower Part
        treeview_style = ttk.Style(product_selection_frame)
        treeview_style.configure("Treeview",
                                 font=("Segoe UI", 12),
                                 rowheight=30,
                                 borderwidth=0,
                                 highlightthickness=0)
        treeview_style.configure("Treeview.Heading",
                                 background="#e0e0e0",
                                 foreground="black",
                                 font=("Segoe UI", 12, "bold"))

        columns = ("ক্রমিক", "শ্রেণি", "পণ্যের নাম", "পরিমাণ", "একক", "মজুদ", "দর", "মোট")
        self.product_entry_treeview = ttk.Treeview(product_selection_frame,
                                                   columns=columns,
                                                   show="headings",
                                                   height=19,
                                                   style="Treeview")

        for col in columns:
            self.product_entry_treeview.heading(col, text=col)

        self.product_entry_treeview.column("ক্রমিক", width=75, stretch=False, )
        self.product_entry_treeview.column("শ্রেণি", width=80, stretch=False, )
        self.product_entry_treeview.column("পণ্যের নাম", width=280, stretch=False, )
        self.product_entry_treeview.column("পরিমাণ", width=70, stretch=False, anchor=tk.E)
        self.product_entry_treeview.column("একক", width=55, stretch=False)
        self.product_entry_treeview.column("মজুদ", width=80, stretch=False, anchor=tk.CENTER)
        self.product_entry_treeview.column("দর", width=75, stretch=False, anchor=tk.CENTER)
        self.product_entry_treeview.column("মোট", width=100, stretch=False, anchor=tk.CENTER)

        self.product_entry_treeview.grid(row=1, column=0, columnspan=5, pady=20)

        scrollbar = ttk.Scrollbar(product_selection_frame, orient=tk.VERTICAL,
                                  command=self.product_entry_treeview.yview)
        scrollbar.grid(row=1, column=5, sticky=tk.NS, pady=20)
        self.product_entry_treeview.configure(yscrollcommand=scrollbar.set)

        # Menu ---------------------------------------------------------------------------------------------------------
        self.menu = tk.Menu(product_selection_frame, tearoff=0)
        self.menu.add_command(label="মুছুন", command=self.delete_item)
        self.product_entry_treeview.bind("<Button-3>", self.show_menu)
        self.product_entry_treeview.bind("<Double-1>", self.edit_quantity_and_unit_price)
        self.product_entry_treeview.tag_configure("product_entry_row", background="#f0f0f0")

        # Invoice Making Frame------------------------------------------------------------------------------------------
        purchase_invoice_frame = tk.Frame(self)
        purchase_invoice_frame.grid(row=0, column=1, sticky=tk.N, padx=(20, 0))

        tk.Label(purchase_invoice_frame,
                 text="মোট পণ্য",
                 font=("Arial", 16, "bold"),
                 anchor=tk.W
                 ).grid(row=0, column=0, sticky=tk.W)
        tk.Label(purchase_invoice_frame,
                 text=":",
                 font=("Arial", 16, "bold"),
                 anchor=tk.W
                 ).grid(row=0, column=1)
        self.total_items = tk.IntVar(value=0)

        tk.Label(purchase_invoice_frame,
                 textvariable=self.total_items,
                 fg="white",
                 bg="black",
                 font=("Arial", 16, "bold"),
                 anchor=tk.E, ).grid(row=0, column=2, sticky=tk.NSEW)

        self.mrp_total = tk.DoubleVar(value=0.00)
        self.total = tk.DoubleVar(value=0.00)

        # MRP Total
        ttk.Separator(purchase_invoice_frame, orient="horizontal").grid(row=1, column=0, columnspan=3, pady=(21, 0),
                                                                        sticky=tk.EW)
        tk.Label(purchase_invoice_frame,
                 text="সর্বমোট",
                 fg="white",
                 bg="#2c3e50",
                 font=("Segoe UI", 12),
                 anchor=tk.W, ).grid(row=2, column=0, sticky=tk.NSEW)
        tk.Label(purchase_invoice_frame,
                 text=":",
                 fg="white",
                 bg="#2c3e50",
                 font=("Segoe UI", 12)).grid(row=2, column=1, sticky=tk.NSEW)

        tk.Label(purchase_invoice_frame,
                 textvariable=self.mrp_total,
                 fg="white",
                 bg="#2c3e50",
                 font=("Segoe UI", 12),
                 width=6,
                 anchor=tk.E).grid(row=2, column=2, sticky=tk.NSEW)

        # (-) Discount
        tk.Label(purchase_invoice_frame,
                 text="(-) ছাড়",
                 fg="white",
                 bg="#2c3e50",
                 font=("Segoe UI", 12),
                 anchor=tk.W).grid(row=3, column=0, sticky=tk.NSEW)
        tk.Label(purchase_invoice_frame,
                 text=":",
                 fg="white",
                 bg="#2c3e50",
                 font=("Segoe UI", 12),
                 ).grid(row=3, column=1, sticky=tk.NSEW)

        self.discount_entry = tk.Entry(purchase_invoice_frame,
                                       width=11,
                                       highlightbackground="#2c3e50",
                                       highlightthickness=1,
                                       highlightcolor="#2c3e50",
                                       font=("Segoe UI", 12),
                                       justify=tk.RIGHT,
                                       )

        self.discount_entry.insert(tk.END, "0")
        self.discount_entry.grid(row=3, column=2, sticky=tk.EW)
        self.discount_entry.config(validate="key",
                                   validatecommand=(purchase_invoice_frame.register(self.update_total), "%P"))

        # Total Payable
        ttk.Separator(purchase_invoice_frame, orient=tk.HORIZONTAL).grid(row=4, column=0, columnspan=3, sticky=tk.EW)
        tk.Label(purchase_invoice_frame,
                 text="মোট প্রদেয়",
                 bg="#2c3e50",
                 font=("Segoe UI", 12, "bold"),
                 anchor=tk.W,
                 fg="white").grid(row=5, column=0, sticky=tk.NSEW)
        tk.Label(purchase_invoice_frame,
                 text=":",
                 bg="#2c3e50",
                 font=("Segoe UI", 12),
                 fg="white").grid(row=5, column=1, sticky=tk.NSEW)
        tk.Label(purchase_invoice_frame,
                 textvariable=self.total,
                 bg="#2c3e50",
                 font=("Segoe UI", 12, "bold"),
                 anchor=tk.E,
                 width=6,
                 fg="white").grid(row=5, column=2, sticky=tk.NSEW)

        # Total Paid + Due-------------------------------------------------------------------------------------
        ## Total Paid
        ttk.Separator(purchase_invoice_frame, orient=tk.HORIZONTAL).grid(row=7, column=0, columnspan=3, sticky=tk.EW)
        tk.Label(purchase_invoice_frame,
                 text="পরিশোধিত",
                 bg="#2c3e50",
                 font=("Segoe UI", 12),
                 anchor=tk.W,
                 fg="white").grid(row=8, column=0, sticky=tk.NSEW)
        tk.Label(purchase_invoice_frame,
                 text=":",
                 bg="#2c3e50",
                 font=("Segoe UI", 12),
                 fg="white").grid(row=8, column=1, sticky=tk.NSEW)
        self.paid_amount_entry = tk.Entry(purchase_invoice_frame, width=6,
                                          highlightbackground="#2c3e50",
                                          highlightthickness=1,
                                          highlightcolor="#2c3e50",
                                          font=("Segoe UI", 12),
                                          justify=tk.RIGHT, )
        self.paid_amount_entry.grid(row=8, column=2, sticky=tk.NSEW)
        self.paid_amount_entry.insert(0, "0")
        self.paid_amount_entry.config(validate="key",
                                      validatecommand=(purchase_invoice_frame.register(self.calculate_due), "%P"))

        ## Due
        tk.Label(purchase_invoice_frame,
                 text="বাকী",
                 fg="white",
                 bg="#2c3e50",
                 font=("Segoe UI", 12),
                 anchor=tk.W, ).grid(row=10, column=0, sticky=tk.NSEW)
        tk.Label(purchase_invoice_frame,
                 text=":",
                 bg="#2c3e50", font=("Segoe UI", 12),
                 fg="white").grid(
            row=10, column=1, sticky=tk.NSEW)
        self.due = tk.DoubleVar(value=0.00)
        tk.Label(purchase_invoice_frame,
                 textvariable=self.due,
                 fg="white",
                 bg="#2c3e50",
                 font=("Segoe UI", 12),
                 anchor=tk.E).grid(row=10, column=2, sticky=tk.NSEW)

        # Customer Details Frame
        supplier_details_frame = tk.Frame(purchase_invoice_frame)
        supplier_details_frame.grid(row=11, column=0, columnspan=3, pady=20, sticky=tk.NSEW)

        tk.Label(supplier_details_frame,
                 text="সাপ্লায়ার",
                 bg="#2c3e50",
                 fg="white",
                 font=("Segoe UI", 12), ).grid(row=0, column=0, sticky=tk.NSEW)
        self.supplier_name_entry = AutoCompleteEntryForSuppliers(supplier_details_frame, db_path="database/database.db",
                                                                 width=28, font=("Segoe UI", 12))
        self.supplier_name_entry.grid(row=1, column=0, sticky=tk.EW)

        tk.Label(supplier_details_frame,
                 text="সম্ভাব্য ডেলিভারির তারিখ",
                 fg="white",
                 bg="#2c3e50",
                 font=("Segoe UI", 12), ).grid(row=2, column=0, pady=(10, 0), sticky=tk.NSEW)

        self.purchase_delivery_date_entry = DateEntry(
            supplier_details_frame,
            date_pattern="dd-mm-yyyy",
            width=40,
            showweeknumbers=False,
            background="#2c3e50",
            foreground="white",
            selectbackground="#1a252f",
        )
        self.purchase_delivery_date_entry.grid(row=3, column=0)

        ttk.Button(supplier_details_frame,
                   text="নতুন ক্রয় তৈরী করুন",
                   command=self.make_purchase).grid(row=4, column=0, pady=(32, 0), sticky=tk.EW)

        self.refresh()

    # Main Methods -----------------------------------------------------------------------------------------------------
    def add_item(self):
        product_name_with_code = self.product_name_search_entry.get()

        if not product_name_with_code:
            messagebox.showerror("পণ্য নির্বাচন", "অনুগ্রহ করে পণ্য নির্বাচন করুন !")
            return

        if "-" in product_name_with_code:
            product_code = product_name_with_code.split("-")[0].strip()
        else:
            messagebox.showerror("ভুল পণ্য", "উক্ত পণ্য খুঁজে পাওয়া যায়নি !")
            return

        product = self.dbmanager.get_product_by_code(product_code)
        if not product:
            messagebox.showerror("ভুল পণ্য", "উক্ত পণ্য খুঁজে পাওয়া যায়নি !")
            return

        if self.quantity.get():
            quantity = float(self.quantity.get())
        else:
            messagebox.showerror("পরিমাণ নির্ধারণ", "অনুগ্রহ করে পরিমাণ নির্ধারণ করুন !")
            return

        if product.category == "Tiles":
            final_quantity, base_qty = helpers.calculate_base_stock_for_tiles(product, quantity)
            subtotal = float(product.purchase_rate) * final_quantity
            values = (product.code, product.category, product.name,
                      round(final_quantity, 2), product.sell_unit_type, base_qty,
                      round(product.purchase_rate, 2), round(subtotal, 2))
        elif product.category == "Pipe":
            final_quantity, base_qty = helpers.calculate_base_stock_for_pipe(product, quantity)
            subtotal = float(product.purchase_rate) * final_quantity
            values = (product.code, product.category, product.name,
                      round(final_quantity, 2), product.sell_unit_type, base_qty,
                      round(product.purchase_rate, 2), round(subtotal, 2))

        else:
            subtotal = product.purchase_rate * quantity
            values = (product.code, product.category, product.name,
                      round(quantity, 2), product.sell_unit_type, "N/A",
                      round(product.purchase_rate, 2), round(subtotal, 2))

        try:
            self.product_entry_treeview.insert("", tk.END, iid=product.code, values=values, tags="product_entry_row")
        except tk.TclError:
            messagebox.showinfo("ডুপ্লিকেট পণ্য", f"{product.name} ইতিমধ্যে তালিকায় রয়েছে !")

        self.update_calculation()
        self.product_name_search_entry.delete(0, tk.END)
        self.quantity.delete(0, tk.END)
        self.quantity.insert(tk.END, "1")

    def edit_quantity_and_unit_price(self, event):
        # Detect row and column
        region = self.product_entry_treeview.identify("region", event.x, event.y)
        if region != "cell":
            return
        row_id = self.product_entry_treeview.identify_row(event.y)
        column = self.product_entry_treeview.identify_column(event.x)

        # Column index
        col_index = int(column.replace("#", "")) - 1
        # Return, if column is not Qty or Rate Column
        if col_index != QTY_COL_INDEX:
            if col_index != RATE_COL_INDEX:
                return

        x, y, width, height = self.product_entry_treeview.bbox(row_id, column)

        # Current value
        value = self.product_entry_treeview.item(row_id, "values")[col_index]

        # Overlay Entry widget
        entry = tk.Entry(self.product_entry_treeview, font=("Segoe UI", 12), justify=tk.CENTER)

        if col_index == QTY_COL_INDEX:  # For Quantity Entry Only
            entry.config(justify=tk.RIGHT)

        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, value)
        entry.focus()

        def save_edit():
            new_val = entry.get()
            values = list(self.product_entry_treeview.item(row_id, "values"))

            if values[CATEGORY_COL_INDEX] == "Tiles" and col_index == QTY_COL_INDEX:
                product = self.dbmanager.get_product_by_code(values[CODE_COL_INDEX])
                final_quantity, base_qty = helpers.calculate_base_stock_for_tiles(product, new_val)
                values[col_index], values[BASE_QTY_COL_INDEX] = final_quantity, base_qty


            elif values[CATEGORY_COL_INDEX] == "Pipe" and col_index == QTY_COL_INDEX:
                product = self.dbmanager.get_product_by_code(values[CODE_COL_INDEX])
                final_quantity, base_qty = helpers.calculate_base_stock_for_pipe(product, new_val)
                values[col_index], values[BASE_QTY_COL_INDEX] = final_quantity, base_qty
            else:
                values[col_index] = new_val

            values[SUBTOTAL_COL_INDEX] = str(float(values[QTY_COL_INDEX]) * float(values[RATE_COL_INDEX]))
            self.product_entry_treeview.item(row_id, values=values)
            entry.destroy()
            self.update_calculation()

        entry.bind("<Return>", lambda e: save_edit())
        entry.bind("<FocusOut>", lambda e: save_edit())

    def delete_item(self, items=None):
        selected = items or self.product_entry_treeview.selection()
        if not selected:
            return

        for item in selected:
            self.product_entry_treeview.delete(item)

        # Update calculation after deleting an item
        self.update_calculation()

    def make_purchase(self):
        if not self.product_entry_treeview.get_children():
            messagebox.showerror(title="ত্রুটি", message="নতুন ক্রয় তৈরী করতে অনুগ্রহ করে পণ্য যোগ করুন !")
            return  # If no product selected

        supplier_name = self.supplier_name_entry.get().replace(" ", "-")

        if supplier_name:
            supplier = self.dbmanager.get_supplier_by_name(supplier_name)
            if not supplier:
                # Make Supplier
                supplier = self.dbmanager.Supplier(
                    name=supplier_name,
                )
                # Add Supplier
                self.dbmanager.add_supplier(supplier)

        else:
            messagebox.showerror("ত্রুটি", "অনুগ্রহ করে সাপ্লায়ারের নাম প্রদান করুন ।")
            return

        # Taking Delivery Date for the Purchase
        date = self.purchase_delivery_date_entry.get()
        day, month, year = date.split("-")
        date_obj = datetime.date(day=int(day), month=int(month), year=int(year))
        # Make Purchase
        purchase = self.dbmanager.Purchase(
            supplier_id=supplier.id,
            total_payable=self.total.get(),
            paid=float(self.paid_amount_entry.get()),
            due=self.due.get(),
            delivery_date=date_obj,
            status=DEFAULT_PURCHASE_STATUS  # Default Status -> Pending
        )
        for row_id in self.product_entry_treeview.get_children():
            code, category, product_name, quantity, unit, base_qty, rate, subtotal = self.product_entry_treeview.item(
                row_id,
                "values")

            # Male SaleItem for each product
            purchase_item = self.dbmanager.PurchaseItem(
                product_code=code,
                product_category=category,
                product_name=product_name,
                quantity=float(quantity),
                unit_type=unit,
                base_qty=base_qty,
                unit_price=float(rate),
                subtotal=float(subtotal),
            )
            # Add PurchaseItem to Purchase
            purchase.items.append(purchase_item)

        self.dbmanager.add_purchase(purchase)

        if supplier.balance > 0 and purchase.paid > 0:
            paid = min(purchase.paid, supplier.balance)
            supplier.balance -= paid
            statement = self.dbmanager.SupplierStatement(supplier_id=supplier.id,
                                                         description=f"ক্রয়ঃ ক্রয় চালান - {purchase.id}",
                                                         amount=-paid, balance=supplier.balance)
            self.dbmanager.add_statement(statement)
        if purchase.due > 0:
            supplier.balance -= purchase.due
            statement = self.dbmanager.SupplierStatement(supplier_id=supplier.id,
                                                         description=f"বাকীঃ ক্রয় চালান - {purchase.id}",
                                                         amount=-purchase.due, balance=supplier.balance)
            self.dbmanager.add_statement(statement)
        self.refresh()

    # Helper Methods
    def refresh(self):
        # Clear Search Entry + Set Quantity 1
        self.product_name_search_entry.delete(0, tk.END)
        self.quantity.delete(0, tk.END)
        self.quantity.insert(0, "1")

        # Deletes all item in the Product Entry Treeview
        self.delete_item(self.product_entry_treeview.get_children())

        # Clears all entries
        self.discount_entry.delete(0, tk.END)
        self.discount_entry.insert(0, "0")
        self.paid_amount_entry.delete(0, tk.END)
        self.paid_amount_entry.insert(0, "0")
        self.supplier_name_entry.delete(0, tk.END)

    def update_calculation(self):
        # Update Total Items
        total_items = len(self.product_entry_treeview.get_children())
        self.total_items.set(total_items)

        # Update MRP Total
        mrp_total_list = [float(self.product_entry_treeview.item(item, "values")[-1]) for item in
                          self.product_entry_treeview.get_children()]
        mrp_total = round(sum(mrp_total_list), 2)
        self.mrp_total.set(mrp_total)

        # Update total after subtracting discount
        discount = self.discount_entry.get()
        self.update_total(discount)

    def update_total(self, new_value):
        if new_value == "":
            new_value = "0"

        if not helpers.is_float(new_value):
            return False

        # Update total after subtracting discount
        mrp_total = self.mrp_total.get()
        discount = float(new_value)
        total_payable = round(mrp_total - discount, 2)
        self.total.set(total_payable)
        self.calculate_due(self.paid_amount_entry.get())
        return True

    def calculate_due(self, paid):
        if paid == "":
            paid = "0"

        if not helpers.is_float(paid):
            return False

        paid_amount = float(paid)
        total_payable = self.total.get()
        if paid_amount < total_payable:
            due = round(total_payable - paid_amount, 2)
            self.due.set(due)
        else:
            self.due.set(0)
        return True

    def show_menu(self, event):
        iid = self.product_entry_treeview.identify_row(event.y)
        if iid:
            self.product_entry_treeview.selection_set(iid)
            self.menu.tk_popup(event.x_root, event.y_root)


class RefundFrame:
    def __init__(self, parent, purchase, dbmanager):
        self.parent = parent
        self.purchase = purchase
        self.dbmanager = dbmanager

        product_selection_frame = tk.Frame(parent)
        product_selection_frame.grid(row=1, column=0)

        tk.Label(product_selection_frame, text=f"সাপ্লায়ার: {purchase.supplier.name}", font=("Arial", 15)).grid(row=0,
                                                                                                                column=0)

        tk.Label(product_selection_frame, text=f"তারিখ: {purchase.purchase_date.strftime("%d-%m-%Y")}",
                 font=("Arial", 15), ).grid(row=0, column=1, padx=20)

        columns = ("ক্রমিক", "পণ্যের নাম", "ক্র. পরিমাণ", "একক", "দর", "ফে. পরিমাণ (পূর্ব)", "ফে. পরিমাণ (নতুন)",
                   "ফে. যোগ্য টাকা")
        product_entry_treeview_style = ttk.Style(product_selection_frame)
        product_entry_treeview_style.configure("Treeview",
                                               font=("Segoe UI", 12),
                                               rowheight=30,
                                               borderwidth=0,
                                               highlightthickness=0)
        product_entry_treeview_style.configure("Treeview.Heading",
                                               background="#e0e0e0",
                                               foreground="black",
                                               font=("Segoe UI", 12, "bold"))

        self.product_entry_treeview = ttk.Treeview(product_selection_frame,
                                                   columns=columns,
                                                   show="headings",
                                                   height=10,
                                                   style="Treeview")
        self.product_entry_treeview.bind("<Double-1>", self.edit_cell)
        self.product_entry_treeview.tag_configure("evenrow", background="#f0f0f0")
        self.product_entry_treeview.tag_configure("oddrow", background="#FFFFFF")

        for col in columns:
            self.product_entry_treeview.heading(col, text=col)

        self.product_entry_treeview.column("ক্রমিক", width=65, stretch=False, )
        self.product_entry_treeview.column("পণ্যের নাম", width=250, stretch=False, )
        self.product_entry_treeview.column("ক্র. পরিমাণ", width=100, stretch=False, )
        self.product_entry_treeview.column("একক", width=70, stretch=False)
        self.product_entry_treeview.column("দর", width=100, stretch=False)
        self.product_entry_treeview.column("ফে. পরিমাণ (পূর্ব)", width=155, stretch=False, )
        self.product_entry_treeview.column("ফে. পরিমাণ (নতুন)", width=155, stretch=False, )
        self.product_entry_treeview.column("ফে. যোগ্য টাকা", width=130, stretch=False, )

        self.product_entry_treeview.grid(row=1, column=0, columnspan=5, pady=20)

        scrollbar = ttk.Scrollbar(product_selection_frame, orient=tk.VERTICAL,
                                  command=self.product_entry_treeview.yview)
        scrollbar.grid(row=1, column=5, sticky=tk.NS, pady=20)

        self.product_entry_treeview.configure(yscrollcommand=scrollbar.set)

        total_items_frame = tk.Frame(product_selection_frame)
        total_items_frame.grid(row=2, column=2, columnspan=3, sticky=tk.E)
        tk.Label(total_items_frame, text="ফেরতযোগ্য মোট টাকা:", font=("Arial", 16, "bold")).grid(row=2, column=0,
                                                                                                   sticky=tk.W)
        self.total_refund_amount = tk.IntVar(value=0)
        tk.Label(total_items_frame, textvariable=self.total_refund_amount, font=("Arial", 16, "bold")).grid(row=2,
                                                                                                              column=1,
                                                                                                              sticky=tk.W)

        ttk.Button(product_selection_frame, text="নিশ্চিত করুন", command=self.add_refund_and_update_stock).grid(
            row=3, column=4, pady=(40, 0), sticky=tk.E)

        self.load_products()

    def load_products(self):
        for i, item in enumerate(self.purchase.items):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            previous_returns_of_this_item = sum([refund.refund_quantity for refund in item.refunds])
            self.product_entry_treeview.insert("", tk.END,
                                               iid=item.id,
                                               values=(item.product_code, item.product_name, item.quantity,
                                                       item.unit_type,
                                                       item.unit_price, previous_returns_of_this_item, 0, 0), tags=tag)

    def edit_cell(self, event):
        # Detect row and column
        region = self.product_entry_treeview.identify("region", event.x, event.y)

        if region != "cell":
            return

        row_id = self.product_entry_treeview.identify_row(event.y)
        column = self.product_entry_treeview.identify_column(event.x)

        # Column index
        col_index = int(column.replace("#", "")) - 1

        if not col_index == RETURNED_QTY_N_COL_INDEX:
            return

        x, y, width, height = self.product_entry_treeview.bbox(row_id, column)

        # Current value
        value = self.product_entry_treeview.item(row_id, "values")[col_index]

        # Overlay Entry widget
        entry = tk.Entry(self.product_entry_treeview, font=("Segoe UI", 12))
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, value)
        entry.focus()

        def save_edit(event=None):
            new_val = entry.get()
            values = list(self.product_entry_treeview.item(row_id, "values"))

            available_product_to_return = float(values[SOLD_QTY_COL_INDEX]) - float(values[RETURN_QTY_P_COL_INDEX])
            if float(new_val) > available_product_to_return:
                messagebox.showwarning(title="ফেরত সীমার উর্ধ্বে",
                                       message="ফেরতযোগ্য পরিমাণ বিক্রিত পরিমাণের চেয়ে বেশি হতে পারবে না।")
                return

            values[col_index] = new_val  # Implements Changes

            # Update return subtotal
            values[REFUND_AMT_COL_INDEX] = str(float(values[RF_RATE_COL_INDEX]) * float(values[col_index]))

            # Update Product in the TreeView
            self.product_entry_treeview.item(row_id, values=values)

            # Update total refund
            total_refund = 0
            for item in self.product_entry_treeview.get_children():
                total_refund += float(self.product_entry_treeview.item(item, "values")[REFUND_AMT_COL_INDEX])
            self.total_refund_amount.set(total_refund)

            entry.destroy()

        entry.bind("<Return>", save_edit)

    def add_refund_and_update_stock(self):
        for row_id in self.product_entry_treeview.get_children():
            values = self.product_entry_treeview.item(row_id, "values")

            # Update product stock in the database
            product_code, returned_quantity = values[CODE_COL_INDEX], values[RETURNED_QTY_N_COL_INDEX]
            self.dbmanager.adjust_stock_of_product(product_code, int(returned_quantity))

            # Add refund history to the SaleItem
            purchase_item = self.dbmanager.get_purchaseitem(row_id)
            purchase_refund_history = self.dbmanager.PurchaseRefund(
                refund_quantity=returned_quantity,
                refund_amount=purchase_item.unit_price * int(returned_quantity),
            )
            purchase_item.refunds.append(purchase_refund_history)

            self.dbmanager.update_changes()

        total_refund = self.total_refund_amount.get()
        self.purchase.supplier.balance += total_refund
        self.purchase.paid += total_refund
        self.purchase.due -= total_refund
        statement = self.dbmanager.SupplierStatement(supplier_id=self.purchase.supplier_id,
                                                     description=f"পণ্য ফেরত (ক্রয় চালান - {self.purchase.id})",
                                                     amount=self.total_refund_amount.get(),
                                                     balance=self.purchase.supplier.balance)
        self.dbmanager.add_statement(statement)
        self.parent.destroy()


class PurchasesFrame(tk.Frame):
    def __init__(self, parent, dbmanager):
        super().__init__(parent)
        self.dbmanager = dbmanager
        self.filter_var = tk.StringVar(value="all_purchases")
        # Options Frame ------------------------------------------------------------------------------------------------
        options_frame = tk.Frame(self)
        options_frame.grid(row=0, column=0, padx=20, pady=(20, 0), sticky=tk.NSEW)

        self.all_purchases_radio_button = tk.Radiobutton(options_frame, text="সকল\nক্রয়", width=10, fg="white",
                                                         bg="#3498db",
                                                         command=self.all_purchases, font=("Arial", 15),
                                                         activeforeground="white", activebackground="#1abc9c",
                                                         selectcolor="#1abc9c",
                                                         variable=self.filter_var, value="all_purchases",
                                                         indicatoron=False,
                                                         height=3)
        self.all_purchases_radio_button.grid(row=0, column=0, sticky=tk.NSEW)

        self.today_delivery_radio_button = tk.Radiobutton(options_frame, text="আজকে\nডেলিভারি", width=10,
                                                          fg="white", bg="#3498db", command=self.today_delivery,
                                                          activeforeground="white", font=("Arial", 15),
                                                          activebackground="#1abc9c", selectcolor="#1abc9c",
                                                          variable=self.filter_var,
                                                          value="today_delivery", indicatoron=False, height=3)
        self.today_delivery_radio_button.grid(row=0, column=1, sticky=tk.NSEW)

        self.due_purchases_radio_button = tk.Radiobutton(options_frame, text="বাকী\nক্রয়", width=10,
                                                         fg="white", bg="#3498db", command=self.due_purchases,
                                                         activeforeground="white", font=("Arial", 15),
                                                         activebackground="#1abc9c", selectcolor="#1abc9c",
                                                         variable=self.filter_var,
                                                         value="due_purchases", indicatoron=False, height=3)
        self.due_purchases_radio_button.grid(row=0, column=2, sticky=tk.NSEW)

        self.custom_search_button = tk.Radiobutton(options_frame, text="খুঁজুন", width=10, fg="white",
                                                   bg="#3498db",
                                                   command=self.custom_search, font=("Arial", 15),
                                                   activeforeground="white", activebackground="#1abc9c",
                                                   selectcolor="#1abc9c",
                                                   variable=self.filter_var, value="custom_search", indicatoron=False,
                                                   height=3)
        self.custom_search_button.grid(row=0, column=3, sticky=tk.NSEW)

        custom_search = tk.Frame(options_frame, highlightbackground="#2c3e50", highlightthickness=2)
        custom_search.grid(row=0, column=4, sticky=tk.NSEW)

        self.search_label = tk.Label(custom_search,
                                     text="খুঁজুন",
                                     fg="white",
                                     bg="#2c3e50",
                                     width=15,
                                     font=("Segoe UI", 14))
        self.search_label.grid(row=0, column=0, columnspan=4, sticky=tk.NSEW)
        self.search_by_label = tk.Label(custom_search, text="খোঁজার মাধ্যম:", font=("Segoe UI", 10), )
        self.search_by_label.grid(row=1, column=0, pady=10, sticky=tk.E)

        self.search_filter = tk.StringVar(value="by_supplier")
        self.by_supplier_radiobutton = tk.Radiobutton(custom_search, text="সাপ্লায়ার", fg="white", bg="#3498db",
                                                      activeforeground="white", width=10, font=("Segoe UI", 10),
                                                      activebackground="#1abc9c", selectcolor="#1abc9c",
                                                      variable=self.search_filter,
                                                      value="by_supplier", command=self.search_by_supplier,
                                                      indicatoron=False)
        self.by_supplier_radiobutton.grid(row=1, column=1, pady=10, sticky=tk.W)

        self.by_purchase_date_radiobutton = tk.Radiobutton(custom_search, text="ক্রয়ের তারিখ", fg="white",
                                                           bg="#3498db",
                                                           activeforeground="white", width=12, font=("Segoe UI", 10),
                                                           activebackground="#1abc9c", selectcolor="#1abc9c",
                                                           variable=self.search_filter,
                                                           value="by_purchase_date",
                                                           command=self.search_by_purchase_date, indicatoron=False)
        self.by_purchase_date_radiobutton.grid(row=1, column=2, pady=10, sticky=tk.W)

        self.by_delivery_date_radiobutton = tk.Radiobutton(custom_search, text="ডেলিভারির তারিখ", fg="white",
                                                           bg="#3498db",
                                                           activeforeground="white", width=15, font=("Segoe UI", 10),
                                                           activebackground="#1abc9c", selectcolor="#1abc9c",
                                                           variable=self.search_filter,
                                                           value="by_delivery_date",
                                                           command=self.search_by_delivery_date,
                                                           indicatoron=False)
        self.by_delivery_date_radiobutton.grid(row=1, column=3, pady=10, padx=(0, 8), sticky=tk.W)

        self.option_label = tk.Label(custom_search, text="সাপ্লায়ার:", width=15, font=("Segoe UI", 10), anchor=tk.E)
        self.option_label.grid(row=2, column=0, pady=(0, 10), padx=(7, 0), sticky=tk.E)

        self.supplier_name_entry = AutoCompleteEntryForSuppliers(custom_search, db_path="database/database.db",
                                                                 width=20, font=("Segoe UI", 10), )
        self.supplier_name_entry.grid(row=2, column=1, columnspan=2, pady=(0, 10), sticky=tk.EW)

        self.date_entry = DateEntry(
            custom_search,
            date_pattern="dd-mm-yyyy",
            width=25,
            showweeknumbers=False,
            background="#2c3e50",
            foreground="white",
            selectbackground="#1a252f",
        )
        self.date_entry.grid(row=2, column=1, pady=(0, 10), columnspan=2)
        self.date_entry.grid_remove()

        self.search_button = tk.Button(custom_search, text="খুঁজুন", font=("Segoe UI", 8),
                                       command=self.get_purchases_by_search)
        self.search_button.grid(row=2, column=3, pady=(0, 10), padx=(0, 8), sticky=tk.EW)

        # Purchases Frame----------------------------------------------------------------------------------
        self.purchases_treeview_frame = tk.Frame(self)
        self.purchases_treeview_frame.grid(row=1, column=0, sticky=tk.N)

        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="রিফ্রেশ", command=self.refresh)
        self.menu.add_command(label="পণ্যসমূহ দেখুন", command=self.view_purchases_items)
        self.menu.add_command(label="অর্ডার গ্রহণ করুন", command=self.order_received)
        self.menu.add_command(label="বাকী পরিশোধ", command=self.pay_due_payment)
        self.menu.add_command(label="পণ্য ফেরত", command=self.purchase_return)

        columns = ("ক্রমিক", "সাপ্লায়ার", "ক্রয়ের তারিখ", "ডেলিভারির তারিখ", "মোট প্রদেয়", "পরিশোধিত", "বাকী", "অবস্থা")
        self.purchases_treeview = ttk.Treeview(self.purchases_treeview_frame, columns=columns, show="headings",
                                               height=16)

        for col in columns:
            self.purchases_treeview.heading(col, text=col)

        self.purchases_treeview.column("ক্রমিক", width=90, stretch=False, anchor=tk.W)
        self.purchases_treeview.column("সাপ্লায়ার", width=130, stretch=False, anchor=tk.W)
        self.purchases_treeview.column("ক্রয়ের তারিখ", width=150, stretch=False, anchor=tk.W)
        self.purchases_treeview.column("ডেলিভারির তারিখ", width=170, stretch=False, anchor=tk.W)
        self.purchases_treeview.column("মোট প্রদেয়", width=150, stretch=False, anchor=tk.W)
        self.purchases_treeview.column("পরিশোধিত", width=150, stretch=False, anchor=tk.W)
        self.purchases_treeview.column("বাকী", width=150, stretch=False, anchor=tk.W)
        self.purchases_treeview.column("অবস্থা", width=120, stretch=False, anchor=tk.W)
        self.purchases_treeview.tag_configure("evenrow", background="#f0f0f0")
        self.purchases_treeview.tag_configure("oddrow", background="#FFFFFF")
        self.purchases_treeview.grid(row=0, column=0, padx=(20, 0), pady=20, sticky=tk.N)

        sales_treeview_scrollbar = ttk.Scrollbar(self.purchases_treeview_frame, orient=tk.VERTICAL,
                                                 command=self.purchases_treeview.yview)
        sales_treeview_scrollbar.grid(row=0, column=1, pady=20, sticky=tk.NS)

        self.purchases_treeview.configure(yscrollcommand=sales_treeview_scrollbar.set)
        self.purchases_treeview.bind("<Button-3>", self.show_menu)

        self.all_purchases_radio_button.invoke()

    # Filter Option Methods---------------------------------------------------------------------------------------------
    def all_purchases(self):
        self.disable_search_mechanism()
        all_purchases = self.dbmanager.get_all_purchases()
        self.insert_purchases_to_treeview(all_purchases)

    def today_delivery(self):
        self.disable_search_mechanism()
        today_delivery_purchases = self.dbmanager.get_today_delivery_purchases()
        self.insert_purchases_to_treeview(today_delivery_purchases)

    def due_purchases(self):
        self.disable_search_mechanism()
        due_purchases = self.dbmanager.get_due_purchases()
        self.insert_purchases_to_treeview(due_purchases)

    def custom_search(self):
        self.purchases_treeview.delete(*self.purchases_treeview.get_children())
        self.enable_search_mechanism()

    def get_purchases_by_search(self):
        filter_option = self.search_filter.get()

        if filter_option == "by_supplier":
            supplier_name = self.supplier_name_entry.get()
            supplier = self.dbmanager.get_supplier_by_name(supplier_name)

            # Checks if supplier exists
            if not supplier:
                self.purchases_treeview.delete(*self.purchases_treeview.get_children())
                messagebox.showerror(title="পাওয়া যায়নি", message="সাপ্লায়ার পাওয়া যায়নি !")
                return

            purchases = self.dbmanager.get_purchases_by_supplier_name(supplier.name)
            if not purchases:
                self.purchases_treeview.delete(*self.purchases_treeview.get_children())
                messagebox.showerror(title="পাওয়া যায়নি", message="উক্ত সাপ্লায়ারের ক্রয়ের অর্ডার পাওয়া যায়নি")
                return

            self.insert_purchases_to_treeview(purchases)

        elif filter_option == "by_purchase_date":
            date = self.date_entry.get()
            day, month, year = date.split("-")
            delivery_date_obj = datetime.date(day=int(day), month=int(month), year=int(year))

            purchases = self.dbmanager.get_purchases_by_purchase_date(delivery_date_obj)

            if not purchases:
                self.purchases_treeview.delete(*self.purchases_treeview.get_children())
                messagebox.showerror(title="পাওয়া যায়নি", message="উক্ত তারিখের কোন ক্রয় পাওয়া যায়নি !")
                return
            self.insert_purchases_to_treeview(purchases)

        elif filter_option == "by_delivery_date":
            date = self.date_entry.get()
            day, month, year = date.split("-")
            delivery_date_obj = datetime.date(day=int(day), month=int(month), year=int(year))

            purchases = self.dbmanager.get_purchases_by_delivery_date(delivery_date_obj)

            if not purchases:
                self.purchases_treeview.delete(*self.purchases_treeview.get_children())
                messagebox.showerror(title="পাওয়া যায়নি", message="উক্ত ডেলিভারি তারিখের কোন ক্রয় পাওয়া যায়নি !")
                return

            self.insert_purchases_to_treeview(purchases)

    # Filter Option Helper Methods--------------------------------------------------------------------------------------
    def search_by_supplier(self):
        self.option_label.config(text="সাপ্লায়ার:")
        self.show_search_bar_entry_for_suppliers()

    def search_by_purchase_date(self):
        self.option_label.config(text="ক্রয়ের তারিখ:")
        self.show_custom_date_search()

    def search_by_delivery_date(self):
        self.option_label.config(text="ডেলিভারির তারিখ:")
        self.show_custom_date_search()

    def insert_purchases_to_treeview(self, purchases):
        self.purchases_treeview.delete(*self.purchases_treeview.get_children())

        for i, purchase in enumerate(purchases[::-1]):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.purchases_treeview.insert(
                "",
                tk.END, iid=purchase.id,
                values=(purchase.id, purchase.supplier.name, purchase.purchase_date.strftime("%d-%m-%Y"),
                        purchase.delivery_date.strftime("%d-%m-%Y"),
                        purchase.total_payable, purchase.paid, purchase.due, purchase.status), tags=tag)

    def show_search_bar_entry_for_suppliers(self):
        self.date_entry.grid_remove()
        self.supplier_name_entry.grid()

    def show_custom_date_search(self):
        self.supplier_name_entry.grid_remove()
        self.date_entry.grid()

    def enable_search_mechanism(self):
        self.search_label.config(fg="white")
        self.option_label.config(fg="black")
        self.search_by_label.config(fg="black")
        self.by_supplier_radiobutton.config(state=tk.NORMAL)
        self.by_purchase_date_radiobutton.config(state=tk.NORMAL)
        self.by_delivery_date_radiobutton.config(state=tk.NORMAL)
        self.supplier_name_entry.config(state=tk.NORMAL)
        self.search_button.config(state=tk.NORMAL)
        self.date_entry.config(state=tk.NORMAL)

    def disable_search_mechanism(self):
        self.search_label.config(fg="gray")
        self.option_label.config(fg="gray")
        self.search_by_label.config(fg="gray")
        self.by_supplier_radiobutton.config(state=tk.DISABLED)
        self.by_purchase_date_radiobutton.config(state=tk.DISABLED)
        self.by_delivery_date_radiobutton.config(state=tk.DISABLED)
        self.supplier_name_entry.config(state=tk.DISABLED)
        self.search_button.config(state=tk.DISABLED)
        self.date_entry.config(state=tk.DISABLED)

    # Menu item Methods-------------------------------------------------------------------------------------------------
    def view_purchases_items(self):
        # UI
        purchased_products_toplevel = tk.Toplevel(self.purchases_treeview_frame)
        purchased_products_toplevel.resizable(False, False)
        self.center_window(purchased_products_toplevel, 500, 975)
        columns = ("ক্রমিক", "শ্রেণি", "পণ্যের নাম", "পরিমাণ", "একক", "মজুদ পরিমাণ", "দর", "মোট")
        purchased_products_list_treeview = ttk.Treeview(purchased_products_toplevel,
                                                        columns=columns,
                                                        show="headings",
                                                        height=14,
                                                        style="Treeview")

        purchased_products_list_treeview.tag_configure("evenrow", background="#f0f0f0")
        purchased_products_list_treeview.tag_configure("oddrow", background="#FFFFFF")

        for col in columns:
            purchased_products_list_treeview.heading(col, text=col)

        purchased_products_list_treeview.column("ক্রমিক", width=80, stretch=False, )
        purchased_products_list_treeview.column("শ্রেণি", width=80, stretch=False, )
        purchased_products_list_treeview.column("পণ্যের নাম", width=300, stretch=False, )
        purchased_products_list_treeview.column("পরিমাণ", width=80, stretch=False, anchor=tk.E)
        purchased_products_list_treeview.column("একক", width=60, stretch=False)
        purchased_products_list_treeview.column("মজুদ পরিমাণ", width=120, stretch=False, anchor=tk.CENTER)
        purchased_products_list_treeview.column("দর", width=85, stretch=False, anchor=tk.CENTER)
        purchased_products_list_treeview.column("মোট", width=105, stretch=False, anchor=tk.CENTER)

        purchased_products_list_treeview.grid(row=0, column=0, padx=(20, 0), pady=20)

        scrollbar = ttk.Scrollbar(purchased_products_toplevel, orient=tk.VERTICAL,
                                  command=purchased_products_list_treeview.yview)
        scrollbar.grid(row=0, column=1, sticky=tk.NS, padx=(0, 20), pady=20)

        purchased_products_list_treeview.configure(yscrollcommand=scrollbar.set)

        purchase_id = self.purchases_treeview.selection()[0]
        purchase = self.dbmanager.get_purchase_by_id(purchase_id)
        for i, purchase_item in enumerate(purchase.items):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            purchased_products_list_treeview.insert("", tk.END,
                                                    values=(purchase_item.product_code, purchase_item.product_category,
                                                            purchase_item.product_name,
                                                            round(purchase_item.quantity, 2),
                                                            purchase_item.unit_type, purchase_item.base_qty,
                                                            round(purchase_item.unit_price, 2),
                                                            round(purchase_item.subtotal, 2)), tags=tag)

    def order_received(self):
        purchase_id = self.purchases_treeview.selection()[0]
        purchase = self.dbmanager.get_purchase_by_id(purchase_id)
        if purchase.status == "গৃহীত":
            messagebox.showinfo(title="ইতিমধ্যে গৃহীত", message="এই অর্ডারটি ইতিমধ্যেই গৃহীত !")
            return

        purchase.status = "গৃহীত"
        for item in purchase.items:
            self.dbmanager.update_stock_of_product(item.product_code, item.quantity)
        messagebox.showinfo(title="সফল", message="অর্ডারটি সফলভাবে গৃহীত হয়েছে !")
        self.refresh()

    def pay_due_payment(self):
        selected_purchase_id = self.purchases_treeview.selection()[0]
        selected_invoice_values = self.purchases_treeview.item(selected_purchase_id, "values")
        due_amount = float(selected_invoice_values[DUE_AMT_INDEX])

        if due_amount <= 0:
            messagebox.showinfo(title="বাকী পাওনা নেই", message="উক্ত অর্ডারের কোন বাকী পাওনা নেই !")
            return
        else:
            def update_purchase_with_due_payment():
                received_amount = float(payment_received_entry.get())
                if received_amount > purchase.due:
                    messagebox.showinfo(title="অতিরিক্ত টাকা",
                                        message="প্রদত্ত টাকা বাকী পাওনার চেয়ে অতিরিক্ত। যাচাই করে আবার চেষ্টা করুন !")
                    return

                purchase.paid += received_amount
                purchase.due -= received_amount

                purchase.supplier.balance += received_amount
                statement = self.dbmanager.SupplierStatement(supplier_id=purchase.supplier.id,
                                                             description=f"বাকী পরিশোধঃ ক্রয় চালান - {purchase.id}",
                                                             amount=received_amount, balance=purchase.supplier.balance)
                purchase.supplier.statements.append(statement)

                supplier_due_payment_history = self.dbmanager.SupplierDuePayment(amount=received_amount)
                purchase.payment_history.append(supplier_due_payment_history)

                self.dbmanager.add_supplier_due_payment_history(supplier_due_payment_history)
                self.dbmanager.update_changes()
                due_pay_win.destroy()
                self.refresh()

            due_pay_win = tk.Toplevel(self.purchases_treeview_frame)
            due_pay_win.title("বাকী পরিশোধ")
            due_pay_win.config(padx=20, pady=20)

            self.center_window(due_pay_win, 195, 265)

            purchase_id = selected_purchase_id
            purchase = self.dbmanager.get_purchase_by_id(purchase_id)

            # Total Payable
            tk.Label(due_pay_win, text=f"মোট প্রদেয়", font=("Segoe UI", 12, "bold"),
                     anchor=tk.W, ).grid(row=1, column=0, sticky=tk.W)
            tk.Label(due_pay_win, text=":", font=("Segoe UI", 12, "bold"),
                     anchor=tk.W, ).grid(row=1, column=1, sticky=tk.W)
            tk.Label(due_pay_win, text=f"{purchase.total_payable:.2f}", font=("Segoe UI", 12, "bold"),
                     anchor=tk.W, ).grid(row=1, column=2, sticky=tk.W)

            # Paid
            tk.Label(due_pay_win, text=f"পরিশোধিত", font=("Segoe UI", 12, "bold"),
                     anchor=tk.W, ).grid(row=2, column=0, sticky=tk.W)
            tk.Label(due_pay_win, text=":", font=("Segoe UI", 12, "bold"),
                     anchor=tk.W, ).grid(row=2, column=1, sticky=tk.W)
            tk.Label(due_pay_win, text=f"{purchase.paid:.2f}", font=("Segoe UI", 12, "bold"),
                     anchor=tk.W, ).grid(row=2, column=2, sticky=tk.W)

            # Due
            tk.Label(due_pay_win, text=f"বাকী", fg="red", font=("Segoe UI", 12, "bold"),
                     anchor=tk.W, ).grid(row=3, column=0, sticky=tk.W)
            tk.Label(due_pay_win, text=":", fg="red", font=("Segoe UI", 12, "bold"),
                     anchor=tk.W, ).grid(row=3, column=1, sticky=tk.W)
            tk.Label(due_pay_win, text=f"{purchase.due:.2f}", fg="red", font=("Segoe UI", 12, "bold"),
                     anchor=tk.W, ).grid(row=3, column=2, sticky=tk.W)

            tk.Label(due_pay_win, text="বাকী পরিশোধ", font=("Segoe UI", 12, "bold"), anchor=tk.W, ).grid(row=4,
                                                                                                         column=0,
                                                                                                         sticky=tk.W)
            tk.Label(due_pay_win, text=":", font=("Segoe UI", 12, "bold"), anchor=tk.W, ).grid(row=4, column=1,
                                                                                               sticky=tk.W)
            payment_received_entry = tk.Entry(due_pay_win, width=8, font=("Segoe UI", 12))
            payment_received_entry.focus_set()
            payment_received_entry.grid(row=4, column=2, sticky=tk.EW)
            tk.Button(due_pay_win, text="নিশ্চিত করুন", command=update_purchase_with_due_payment).grid(row=5, column=1,
                                                                                                       columnspan=2,
                                                                                                       pady=10,
                                                                                                       sticky=tk.NSEW)
            due_pay_win.transient()
            due_pay_win.grab_set()  # modal behavior
            due_pay_win.resizable(False, False)

    def purchase_return(self):
        selected_purchase_iid = self.purchases_treeview.selection()[0]
        purchase_id = self.purchases_treeview.item(selected_purchase_iid, "values")[0]
        purhcase = self.dbmanager.get_purchase_by_id(purchase_id)

        if purhcase.status == "গৃহীত":
            purchase_return_window = tk.Toplevel(self.purchases_treeview_frame)
            purchase_return_window.title("পণ্য ফেরত")
            purchase_return_window.config(padx=20, pady=20)
            self.center_window(purchase_return_window, 550, 1085)
            purchase_return_window.transient()
            purchase_return_window.grab_set()  # modal behavior
            purchase_return_window.resizable(False, False)
            RefundFrame(purchase_return_window, purhcase, self.dbmanager)
        else:
            messagebox.showerror(title="ত্রুটি", message="দুঃখিত, উক্ত অর্ডারটি গৃহীত হয়নি !")

    def center_window(self, win, custom_height, custom_width):
        win.update_idletasks()
        width = custom_width
        height = custom_height
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")

    def show_menu(self, event):
        iid = self.purchases_treeview.identify_row(event.y)
        if iid:
            self.purchases_treeview.selection_set(iid)
            self.menu.tk_popup(event.x_root, event.y_root)

    def refresh(self):
        filter_option = self.filter_var.get()
        if filter_option == "all_purchases":
            self.all_purchases_radio_button.invoke()
        elif filter_option == "today_delivery":
            self.today_delivery_radio_button.invoke()
        elif filter_option == "due_purchases":
            self.due_purchases_radio_button.invoke()
        elif filter_option == "custom_search":
            self.search_button.invoke()
