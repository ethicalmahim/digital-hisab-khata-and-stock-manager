import datetime
import re
import tkinter as tk
from tkinter.font import Font
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from utils import helpers

# New Sale Frame
CODE_COL_INDEX = 0
CATEGORY_COL_INDEX = 1
PRODUCT_COL_INDEX = 2
QTY_COL_INDEX = 3
UNIT_COL_INDEX = 4
BASE_QTY_COL_INDEX = 5
RATE_COL_INDEX = 6
SUBTOTAL_COL_INDEX = 7

# Sales Return Frame
SOLD_QTY_COL_INDEX = 2
RF_RATE_COL_INDEX = 4
RETURN_QTY_P_COL_INDEX = 5
RETURNED_QTY_N_COL_INDEX = 6
REFUND_AMT_COL_INDEX = 7


class NewSaleFrame(tk.Frame):
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

        self.product_name_search_entry = helpers.AutoCompleteEntry(product_selection_frame,
                                                                   db_path="database/database.db", font=("Arial", 15),
                                                                   width=43)
        self.product_name_search_entry.grid(row=0, column=1)

        tk.Label(product_selection_frame, text="পরিমাণ:", font=Font(size=15), ).grid(row=0, column=2)

        self.quantity = tk.Spinbox(product_selection_frame, from_=1, to=100000, font=("Arial", 15), width=7,
                                   validate="key",
                                   validatecommand=(product_selection_frame.register(helpers.is_float), "%P",))
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

        # Menu Options for Treeview
        self.menu = tk.Menu(product_selection_frame, tearoff=0)
        self.menu.add_command(label="মুছুন", command=self.delete_item)
        self.product_entry_treeview.bind("<Button-3>", self.show_menu)
        self.product_entry_treeview.bind("<Double-1>", self.edit_quantity_and_unit_price)
        self.product_entry_treeview.tag_configure("product_entry_row", background="#f0f0f0")

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

        # Invoice Making Frame--------------------------------------------------------------------------------------------
        invoice_frame = tk.Frame(self)
        invoice_frame.grid(row=0, column=1, sticky=tk.N, padx=(20, 0))

        tk.Label(invoice_frame,
                 text="মোট পণ্য",
                 font=("Arial", 16, "bold"),
                 anchor=tk.W
                 ).grid(row=0, column=0, sticky=tk.W)
        tk.Label(invoice_frame,
                 text=":",
                 font=("Arial", 16, "bold"),
                 anchor=tk.W
                 ).grid(row=0, column=1)
        self.total_items = tk.IntVar(value=0)
        tk.Label(invoice_frame,
                 textvariable=self.total_items,
                 fg="white",
                 bg="black",
                 font=("Arial", 16, "bold"),
                 anchor=tk.E, ).grid(row=0, column=2, sticky=tk.NSEW)

        self.mrp_total = tk.DoubleVar(value=0)
        self.total = tk.DoubleVar(value=0)

        # MRP Total
        ttk.Separator(invoice_frame, orient="horizontal").grid(row=1, column=0, columnspan=3, pady=(21, 0),
                                                               sticky=tk.EW)
        tk.Label(invoice_frame,
                 text="সর্বমোট",
                 fg="white",
                 bg="#2c3e50",
                 font=("Segoe UI", 12),
                 anchor=tk.W, ).grid(row=2, column=0, sticky=tk.NSEW)
        tk.Label(invoice_frame,
                 text=":",
                 fg="white",
                 bg="#2c3e50",
                 font=("Segoe UI", 12)).grid(row=2, column=1, sticky=tk.NSEW)

        tk.Label(invoice_frame,
                 textvariable=self.mrp_total,
                 fg="white",
                 bg="#2c3e50",
                 font=("Segoe UI", 12),
                 width=6,
                 anchor=tk.E).grid(row=2, column=2, sticky=tk.NSEW)

        # (-) Discount
        tk.Label(invoice_frame,
                 text="(-) ছাড়",
                 fg="white",
                 bg="#2c3e50",
                 font=("Segoe UI", 12),
                 anchor=tk.W).grid(row=3, column=0, sticky=tk.NSEW)
        tk.Label(invoice_frame,
                 text=":",
                 fg="white",
                 bg="#2c3e50",
                 font=("Segoe UI", 12),
                 ).grid(row=3, column=1, sticky=tk.NSEW)
        self.discount_entry = tk.Entry(invoice_frame,
                                       width=11,
                                       highlightbackground="#2c3e50",
                                       highlightthickness=1,
                                       highlightcolor="#2c3e50",
                                       font=("Segoe UI", 12),
                                       justify=tk.RIGHT)

        self.discount_entry.insert(tk.END, "0")
        self.discount_entry.grid(row=3, column=2, sticky=tk.EW)

        # Total Payable
        ttk.Separator(invoice_frame, orient=tk.HORIZONTAL).grid(row=4, column=0, columnspan=3, sticky=tk.EW)
        tk.Label(invoice_frame,
                 text="মোট প্রদেয়",
                 bg="#2c3e50",
                 font=("Segoe UI", 12, "bold"),
                 anchor=tk.W,
                 fg="white").grid(row=5, column=0, sticky=tk.NSEW)
        tk.Label(invoice_frame,
                 text=":",
                 bg="#2c3e50",
                 font=("Segoe UI", 12),
                 fg="white").grid(row=5, column=1, sticky=tk.NSEW)
        tk.Label(invoice_frame,
                 textvariable=self.total,
                 bg="#2c3e50",
                 font=("Segoe UI", 12, "bold"),
                 anchor=tk.E,
                 width=6,
                 fg="white").grid(row=5, column=2, sticky=tk.NSEW)

        # It has to be here because of self.update_total method.
        # In self.update_total method there is another method called self.calculate_change_due(called inside of self.update_total).
        # In self.calculate change due we referred self.payment_methods_treeview
        self.discount_entry.config(validate="key", validatecommand=(invoice_frame.register(self.update_total), "%P"))

        # Total Paid + Change + Due-------------------------------------------------------------------------------------

        ## Total Paid
        ttk.Separator(invoice_frame, orient="horizontal").grid(row=7, column=0, columnspan=3, sticky=tk.EW)
        tk.Label(invoice_frame,
                 text="পরিশোধিত",
                 bg="#2c3e50",
                 font=("Segoe UI", 12),
                 anchor=tk.W,
                 fg="white").grid(row=8, column=0, sticky=tk.NSEW)
        tk.Label(invoice_frame,
                 text=":",
                 bg="#2c3e50",
                 font=("Segoe UI", 12),
                 fg="white").grid(row=8, column=1, sticky=tk.NSEW)
        self.paid_entry = tk.Entry(invoice_frame,
                                   width=6,
                                   highlightbackground="#2c3e50",
                                   highlightthickness=1,
                                   highlightcolor="#2c3e50",
                                   font=("Segoe UI", 12),
                                   justify=tk.RIGHT)
        self.paid_entry.grid(row=8, column=2, sticky=tk.NSEW)
        self.paid_entry.insert(tk.END, "0")
        self.paid_entry.config(validate="key",
                               validatecommand=(invoice_frame.register(self.calculate_change_due), "%P"))

        ## Change
        tk.Label(invoice_frame,
                 text="ফেরত",
                 fg="white",
                 bg="#2c3e50",
                 font=("Segoe UI", 12),
                 anchor=tk.W).grid(row=9, column=0, sticky=tk.NSEW)
        tk.Label(invoice_frame,
                 text=":",
                 fg="white",
                 bg="#2c3e50",
                 font=("Segoe UI", 12), ).grid(row=9, column=1, sticky=tk.NSEW)
        self.change = tk.DoubleVar(value=0)
        tk.Label(invoice_frame,
                 textvariable=self.change,
                 fg="white",
                 bg="#2c3e50",
                 font=("Segoe UI", 12),
                 anchor=tk.E).grid(row=9, column=2, sticky=tk.NSEW)

        ## Due
        tk.Label(invoice_frame,
                 text="বাকী",
                 fg="white",
                 bg="#2c3e50",
                 font=("Segoe UI", 12),
                 anchor=tk.W, ).grid(row=10, column=0, sticky=tk.NSEW)
        tk.Label(invoice_frame,
                 text=":",
                 bg="#2c3e50", font=("Segoe UI", 12),
                 fg="white").grid(row=10, column=1, sticky=tk.NSEW)
        self.due = tk.DoubleVar(value=0)
        tk.Label(invoice_frame,
                 textvariable=self.due,
                 fg="white",
                 bg="#2c3e50",
                 font=("Segoe UI", 12),
                 anchor=tk.E).grid(row=10, column=2, sticky=tk.NSEW)

        # Customer Details Frame
        customer_details_frame = tk.Frame(invoice_frame)
        customer_details_frame.grid(row=11, column=0, columnspan=3, pady=20, sticky=tk.NSEW)

        tk.Label(customer_details_frame,
                 text="গ্রাহকের মোবাইল নম্বর",
                 fg="white",
                 bg="#2c3e50",
                 font=("Segoe UI", 12), ).grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)

        self.customer_phone_entry = tk.Entry(
            customer_details_frame, validate="key",
            validatecommand=(customer_details_frame.register(helpers.validate_phone_number), "%P",),
            font=("Segoe UI", 12))
        self.customer_phone_entry.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)

        ttk.Button(customer_details_frame,
                   text="খুঁজুন",
                   width=7,
                   command=self.search_customer).grid(row=0, column=2, rowspan=2, padx=(15, 0), sticky=tk.NS)

        tk.Label(customer_details_frame,
                 text="গ্রাহকের নাম",
                 bg="#2c3e50",
                 fg="white",
                 font=("Segoe UI", 12), ).grid(row=2, column=0, columnspan=3, pady=(10, 0), sticky=tk.NSEW)
        self.customer_name_entry = tk.Entry(customer_details_frame, font=("Segoe UI", 12))
        self.customer_name_entry.grid(row=3, column=0, columnspan=3, sticky=tk.EW)

        tk.Label(customer_details_frame,
                 text="গ্রাহকের ঠিকানা",
                 fg="white",
                 bg="#2c3e50",
                 font=("Segoe UI", 12)).grid(row=4, column=0, columnspan=3, pady=(10, 0), sticky=tk.NSEW)
        self.customer_address_entry = tk.Text(customer_details_frame, height=2, width=20, font=("Segoe UI", 12))
        self.customer_address_entry.grid(row=5, column=0, columnspan=3, sticky=tk.EW)

        tk.Label(customer_details_frame,
                 text="গ্রাহকের ব্যালেন্স",
                 bg="#2c3e50",
                 fg="white",
                 font=("Segoe UI", 12), ).grid(row=6, column=0, columnspan=3, pady=(10, 0), sticky=tk.NSEW)
        self.customer_balance_entry = tk.Entry(customer_details_frame, state=tk.DISABLED, font=("Segoe UI", 12))
        self.customer_balance_entry.grid(row=7, column=0, columnspan=3, sticky=tk.EW)

        ttk.Button(customer_details_frame,
                   text="নতুন বিক্রয় তৈরী করুন",
                   command=self.make_sale).grid(row=8, column=0, columnspan=3, pady=(20, 0), sticky=tk.EW)

        call_invoice_frame = tk.Frame(invoice_frame)
        call_invoice_frame.grid(row=12, column=0, columnspan=3, pady=(3, 0), sticky=tk.NSEW)
        tk.Label(call_invoice_frame, text="চালান নং:", fg="white", bg="#2c3e50",
                 font=("Segoe UI", 12)).grid(row=0, column=0, sticky=tk.W)
        self.invoice_call_entry = tk.Entry(call_invoice_frame, width=9, validate="key",
                                           validatecommand=(call_invoice_frame.register(helpers.is_digit), "%P",),
                                           font=("Segoe UI", 14))
        self.invoice_call_entry.grid(row=0, column=1, padx=5, sticky=tk.W)

        ttk.Button(call_invoice_frame, text="কল", command=self.call_invoice).grid(row=0, column=2, sticky=tk.EW)

        ttk.Button(call_invoice_frame, text="চালান আপডেট করুন",
                   command=self.update_invoice).grid(row=1, column=0, columnspan=3, pady=20, sticky=tk.NSEW)

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
            subtotal = float(product.sell_unit_price) * final_quantity
            values = (product.code, product.category, product.name,
                      round(final_quantity, 2), product.sell_unit_type, base_qty,
                      round(product.sell_unit_price, 2), round(subtotal, 2))
        elif product.category == "Pipe":
            final_quantity, base_qty = helpers.calculate_base_stock_for_pipe(product, quantity)
            subtotal = float(product.sell_unit_price) * final_quantity
            values = (product.code, product.category, product.name,
                      round(final_quantity, 2), product.sell_unit_type, base_qty,
                      round(product.sell_unit_price, 2), round(subtotal, 2))

        else:
            subtotal = product.sell_unit_price * quantity
            values = (product.code, product.category, product.name,
                      round(quantity, 2), product.sell_unit_type, "N/A",
                      round(product.sell_unit_price, 2), round(subtotal, 2))

        try:
            self.product_entry_treeview.insert("", tk.END,
                                               iid=product.code,
                                               values=values,
                                               tags="product_entry_row")
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

    def update_calculation(self):
        # Update Total Items
        total_item = len(self.product_entry_treeview.get_children())
        self.total_items.set(total_item)

        # Update MRP Total
        mrp_total_list = [float(self.product_entry_treeview.item(item, "values")[-1]) for item in
                          self.product_entry_treeview.get_children()]
        mrp_total = sum(mrp_total_list)
        self.mrp_total.set(round(mrp_total, 2))

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
        self.total.set(mrp_total - discount)
        self.calculate_change_due(self.paid_entry.get())
        return True

    def calculate_change_due(self, paid_amount):
        if paid_amount == "":
            paid_amount = "0"

        if not helpers.is_float(paid_amount):
            return False

        paid_amount = float(paid_amount)  # Converting str to int
        if self.total.get() < paid_amount:
            self.change.set(paid_amount - self.total.get())
            self.due.set(0)
        else:
            self.due.set(self.total.get() - paid_amount)
            self.change.set(0)

        return True

    def search_customer(self):
        customer_phone = self.customer_phone_entry.get()
        is_valid_phone_number = bool(re.fullmatch(r'^01[3-9]\d{8}$', customer_phone))
        if not is_valid_phone_number:
            messagebox.showerror("ত্রুটি", "অনুগ্রহ করে সঠিক মোবাইল নম্বর প্রদান করুন!")
            return

        if customer_phone:
            customer = self.dbmanager.get_customer_by_phone(customer_phone)
            if customer:
                self.customer_phone_entry.config(bg="green")

                self.customer_name_entry.delete(0, tk.END)  # Removes everything if previously exists anything
                self.customer_name_entry.insert(tk.END, customer.name)

                self.customer_address_entry.delete("1.0", tk.END)
                self.customer_address_entry.insert(tk.END, customer.address)

                self.customer_balance_entry.config(state=tk.NORMAL)
                self.customer_balance_entry.delete(0, tk.END)
                self.customer_balance_entry.insert(tk.END, customer.balance)
                self.customer_balance_entry.config(state=tk.DISABLED)
            else:
                self.customer_phone_entry.config(bg="red")
                self.customer_name_entry.delete(0, tk.END)
                self.customer_address_entry.delete("1.0", tk.END)
                self.customer_balance_entry.config(state=tk.NORMAL)
                self.customer_balance_entry.delete(0, tk.END)
                self.customer_balance_entry.config(state=tk.DISABLED)

    def make_sale(self):
        if not self.product_entry_treeview.get_children():
            messagebox.showerror(title="ত্রুটি", message="নতুন বিক্রয় তৈরী করতে অনুগ্রহ করে পণ্য যোগ করুন !")
            return

        current_customer_phone = self.customer_phone_entry.get()
        if current_customer_phone:
            current_customer = self.dbmanager.get_customer_by_phone(current_customer_phone)
            if not current_customer:
                # Make Customer
                current_customer = self.dbmanager.Customer(
                    name=self.customer_name_entry.get(),
                    phone=self.customer_phone_entry.get(),
                    address=self.customer_address_entry.get("1.0", tk.END),
                )
                # Add Customer
                self.dbmanager.add_customer(current_customer)
        else:
            current_customer = self.dbmanager.get_customer_by_phone("01700000000")

        # Make Sale
        sale = self.dbmanager.Invoice(
            customer_id=current_customer.id,
            mrp_total=self.mrp_total.get(),
            discount=self.discount_entry.get(),
            total_payable=self.total.get(),
            paid=self.paid_entry.get(),
            change=self.change.get(),
            due=self.due.get(),
        )

        # Add products to Sale
        for row_id in self.product_entry_treeview.get_children():
            code, category, product_name, quantity, unit_type, base_qty, unit_price, subtotal = self.product_entry_treeview.item(
                row_id, "values")

            # Male SaleItem for each product
            saleitem = self.dbmanager.SaleItem(
                product_code=int(code),
                product_category=category,
                product_name=product_name,
                quantity=float(quantity),
                unit_type=unit_type,
                base_qty=base_qty,
                unit_price=float(unit_price),
                subtotal=float(subtotal),
            )
            # Add SaleItem to invoice
            sale.items.append(saleitem)
            # Adjust stock while looping over through the TreeView
            self.dbmanager.adjust_stock_of_product(saleitem.product_code, saleitem.quantity)

        self.dbmanager.add_sale(sale)

        # Accoutns Statement Section
        if current_customer.balance > 0 and sale.paid > 0:
            paid = min(sale.paid, current_customer.balance)
            current_customer.balance -= paid
            statement = self.dbmanager.CustomerStatement(customer_id=current_customer.id,
                                                         description=f"ক্রয়ঃ বিক্রয় চালান - {sale.id}",
                                                         amount=-paid, balance=current_customer.balance)
            self.dbmanager.add_statement(statement)
        if sale.due > 0:
            current_customer.balance -= sale.due
            statement = self.dbmanager.CustomerStatement(customer_id=current_customer.id,
                                                         description=f"বাকীঃ বিক্রয় চালান - {sale.id}",
                                                         amount=-sale.due, balance=current_customer.balance)
            self.dbmanager.add_statement(statement)

        should_print_invoice = messagebox.askyesno(title="চালান প্রিন্ট", message="আপনি কি চালান প্রিন্ট করতে চান ?")
        if should_print_invoice:
            ready_invoice = helpers.make_invoice_for_sale(sale)
            helpers.print_out_invoice(ready_invoice)
        self.refresh()

    def call_invoice(self):
        invoice_number = self.invoice_call_entry.get()

        if not invoice_number:
            messagebox.showinfo(title="অসম্পুর্ণ তথ্য", message="চালান কল করতে অনুগ্রহ করে চালান নম্বর দিন !")
            return

        invoice = self.dbmanager.get_invoice(int(invoice_number))
        if not invoice:
            messagebox.showerror(title="ত্রুটি", message="দুঃখিত , উক্ত চালানটি খুঁজে পাওয়া যায়নি !")
            return

        for saleitem in invoice.items:
            for refund in saleitem.refunds:
                if refund:
                    messagebox.showinfo(title="ত্রুটি", message="দুঃখিত, উক্ত চালানটি এডিট করা সম্ভব নয় !")
                    self.invoice_call_entry.delete(0, tk.END)
                    return

        self.product_entry_treeview.delete(*self.product_entry_treeview.get_children())
        for item in invoice.items:
            values = (item.product_code, item.product_category, item.product_name, round(item.quantity, 2),
                      item.unit_type, item.base_qty,
                      round(item.unit_price, 2), round(item.subtotal, 2))
            item.product.current_stock += item.quantity  # Restore Stocks Before Editing
            self.product_entry_treeview.insert("", tk.END, iid=item.product_code, values=values,
                                               tags="product_entry_row")
        self.discount_entry.delete(0, tk.END)
        self.discount_entry.insert(0, invoice.discount)
        self.paid_entry.delete(0, tk.END)
        self.paid_entry.insert(0, invoice.paid)

        self.update_calculation()

        self.customer_phone_entry.delete(0, tk.END)
        self.customer_phone_entry.insert(0, invoice.customer.phone)
        self.customer_name_entry.delete(0, tk.END)
        self.customer_name_entry.insert(0, invoice.customer.name)
        self.customer_address_entry.delete("1.0", tk.END)
        self.customer_address_entry.insert("1.0", invoice.customer.address)
        self.invoice_call_entry.config(state=tk.DISABLED)

    def update_invoice(self):
        invoice_to_update = self.dbmanager.get_invoice(self.invoice_call_entry.get())

        if not invoice_to_update:
            messagebox.showerror(title="ত্রুটি", message="চালান আপডেট করতে অনুগ্রহ করে চালান কল করুন !")
            return

        for saleitem in invoice_to_update.items:
            self.dbmanager.delete_saleitem(saleitem)

        current_customer_phone = self.customer_phone_entry.get()
        if current_customer_phone:
            current_customer = self.dbmanager.get_customer_by_phone(current_customer_phone)
            if not current_customer:
                # Make Customer
                current_customer = self.dbmanager.Customer(
                    name=self.customer_name_entry.get(),
                    phone=self.customer_phone_entry.get(),
                    address=self.customer_address_entry.get("1.0", tk.END),
                )
                # Add Customer
                self.dbmanager.add_customer(current_customer)
        else:
            current_customer = self.dbmanager.get_customer_by_phone("01700000000")

        # Update Invoice
        invoice_to_update.customer_id = current_customer.id
        invoice_to_update.mrp_total = self.mrp_total.get()
        invoice_to_update.discount = self.discount_entry.get()
        invoice_to_update.total_payable = self.total.get()
        invoice_to_update.paid = self.paid_entry.get()
        invoice_to_update.change = self.change.get()
        invoice_to_update.due = self.due.get()

        # Add products to Sale
        for row_id in self.product_entry_treeview.get_children():
            code, category, product_name, quantity, unit_type, base_qty, unit_price, subtotal = self.product_entry_treeview.item(
                row_id, "values")

            # Male SaleItem for each product
            saleitem = self.dbmanager.SaleItem(
                product_code=int(code),
                product_category=category,
                product_name=product_name,
                quantity=float(quantity),
                unit_type=unit_type,
                base_qty=base_qty,
                unit_price=float(unit_price),
                subtotal=float(subtotal),
            )
            # Add SaleItem to invoice
            invoice_to_update.items.append(saleitem)
            # Adjust stock while looping over through the TreeView
            self.dbmanager.adjust_stock_of_product(saleitem.product_code, saleitem.quantity)

        self.dbmanager.update_changes()

        should_print_invoice = messagebox.askyesno(title="চালান প্রিন্ট", message="আপনি কি চালান প্রিন্ট করতে চান ?")
        if should_print_invoice:
            ready_invoice = helpers.make_invoice_for_sale(invoice_to_update)
            helpers.print_out_invoice(ready_invoice)

        self.invoice_call_entry.config(state=tk.NORMAL)  # Make invoice call entry normal before refresh
        self.refresh()

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
        self.paid_entry.delete(0, tk.END)
        self.paid_entry.insert(0, "0")
        self.customer_phone_entry.config(bg="white")
        self.customer_phone_entry.delete(0, tk.END)
        self.customer_name_entry.delete(0, tk.END)
        self.customer_address_entry.delete("1.0", tk.END)
        self.customer_balance_entry.config(state=tk.NORMAL)
        self.customer_balance_entry.delete(0, tk.END)
        self.customer_balance_entry.config(state=tk.DISABLED)
        self.invoice_call_entry.delete(0, tk.END)

    # Helper Methods ---------------------------------------------------------------------------------------------------
    def show_menu(self, event):
        iid = self.product_entry_treeview.identify_row(event.y)
        if iid:
            self.product_entry_treeview.selection_set(iid)
            self.menu.tk_popup(event.x_root, event.y_root)


class DuePaymentHistoryFrame:
    def __init__(self, parent, invoice, dbmanager):
        self.parent = parent
        self.invoice = invoice
        self.dbmanager = dbmanager

        due_payment_history_frame = tk.Frame(parent)
        due_payment_history_frame.grid(row=0, column=0)

        tk.Label(due_payment_history_frame, text=f"চালান: {invoice.id}", font=("Arial", 15), ).grid(row=0, column=0,
                                                                                                    sticky=tk.W)
        tk.Label(due_payment_history_frame, text=f"তারিখ: {invoice.date.strftime("%d-%m-%Y")}",
                 font=("Arial", 15), ).grid(row=1, column=0, sticky=tk.W)
        tk.Label(due_payment_history_frame, text=f"সময়: {invoice.time.strftime("%I:%M %p")}",
                 font=("Arial", 15), ).grid(
            row=1, column=1, sticky=tk.W)
        tk.Label(due_payment_history_frame, text=f"গ্রাহক: {invoice.customer.name}-{invoice.customer.phone}",
                 font=("Arial", 15), ).grid(row=2, column=0, columnspan=2, sticky=tk.W)
        columns = ("তারিখ", "সময়", "টাকা")
        product_entry_treeview_style = ttk.Style(due_payment_history_frame)
        product_entry_treeview_style.configure("Treeview",
                                               font=("Segoe UI", 12),
                                               rowheight=30,
                                               borderwidth=0,
                                               highlightthickness=0)
        product_entry_treeview_style.configure("Treeview.Heading",
                                               background="#e0e0e0",
                                               foreground="black",
                                               font=("Segoe UI", 12, "bold"))

        self.payment_history_treeview = ttk.Treeview(due_payment_history_frame,
                                                     columns=columns,
                                                     show="headings",
                                                     height=10,
                                                     style="Treeview")
        self.payment_history_treeview.tag_configure("evenrow", background="#f0f0f0")
        self.payment_history_treeview.tag_configure("oddrow", background="#FFFFFF")

        for col in columns:
            self.payment_history_treeview.heading(col, text=col)
        self.payment_history_treeview.column("তারিখ", width=200, stretch=False, )
        self.payment_history_treeview.column("সময়", width=100, stretch=False, )
        self.payment_history_treeview.column("টাকা", width=150, stretch=False, )

        self.payment_history_treeview.grid(row=3, column=0, columnspan=2, pady=20)

        scrollbar = ttk.Scrollbar(due_payment_history_frame, orient=tk.VERTICAL,
                                  command=self.payment_history_treeview.yview)
        scrollbar.grid(row=3, column=2, sticky=tk.NS, pady=20)
        self.payment_history_treeview.configure(yscrollcommand=scrollbar.set)

        self.load_payment_history()

    def load_payment_history(self):
        for i, payment_history in enumerate(self.invoice.payment_history):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.payment_history_treeview.insert("", tk.END, values=(payment_history.date.strftime("%d-%m-%Y"),
                                                                     payment_history.time.strftime("%I: %M %p"),
                                                                     payment_history.amount),
                                                 tags=tag)


class RefundFrame:
    def __init__(self, parent, invoice, dbmanager):
        self.parent = parent
        self.invoice = invoice
        self.dbmanager = dbmanager

        product_selection_frame = tk.Frame(parent)
        product_selection_frame.grid(row=1, column=0)

        tk.Label(product_selection_frame, text=f"চালান: {invoice.id}", font=("Arial", 15), ).grid(row=0, column=0,
                                                                                                  sticky=tk.W)
        tk.Label(product_selection_frame, text=f"তারিখ: {invoice.date.strftime("%d-%m-%Y")}",
                 font=("Arial", 15), ).grid(
            row=0, column=1, padx=20)
        tk.Label(product_selection_frame, text=f"সময়: {invoice.time.strftime("%I:%M %p")}", font=("Arial", 15), ).grid(
            row=0, column=2, padx=20)
        tk.Label(product_selection_frame, text=f"গ্রাহক: {invoice.customer.name}-{invoice.customer.phone}",
                 font=("Arial", 15), ).grid(row=0, column=3)
        columns = ("ক্রমিক", "পণ্যের নাম", "বি. পরিমাণ", "একক", "দর", "ফে. পরিমাণ (পূর্ব)", "ফে. পরিমাণ (নতুন)",
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
        self.product_entry_treeview.column("পণ্যের নাম", width=260, stretch=False, )
        self.product_entry_treeview.column("বি. পরিমাণ", width=100, stretch=False, )
        self.product_entry_treeview.column("একক", width=70, stretch=False)
        self.product_entry_treeview.column("দর", width=90, stretch=False)
        self.product_entry_treeview.column("ফে. পরিমাণ (পূর্ব)", width=155, stretch=False, )
        self.product_entry_treeview.column("ফে. পরিমাণ (নতুন)", width=155, stretch=False, )
        self.product_entry_treeview.column("ফে. যোগ্য টাকা", width=130, stretch=False, )

        self.product_entry_treeview.grid(row=1, column=0, columnspan=5, pady=20)

        scrollbar = ttk.Scrollbar(product_selection_frame, orient=tk.VERTICAL,
                                  command=self.product_entry_treeview.yview)
        scrollbar.grid(row=1, column=5, sticky=tk.NS, pady=20)
        self.product_entry_treeview.configure(yscrollcommand=scrollbar.set)

        total_items_frame = tk.Frame(product_selection_frame)
        total_items_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W)

        total_items_frame = tk.Frame(product_selection_frame)
        total_items_frame.grid(row=2, column=2, columnspan=3, sticky=tk.E)
        tk.Label(total_items_frame, text="ফেরতযোগ্য মোট টাকা:", font=("Arial", 16, "bold"), ).grid(row=2, column=0,
                                                                                                   sticky=tk.W)
        self.total_refund_amount = tk.IntVar(value=0)
        tk.Label(total_items_frame, textvariable=self.total_refund_amount, font=("Arial", 16, "bold"), ).grid(row=2,
                                                                                                              column=1,
                                                                                                              sticky=tk.W)

        ttk.Button(product_selection_frame, text="নিশ্চিত করুন", command=self.add_refund_and_update_stock).grid(
            row=3, column=4, pady=(40, 0), sticky=tk.E)
        self.load_products()

    def load_products(self):
        for i, item in enumerate(self.invoice.items):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            previous_returns_of_this_item = sum([refund.refund_quantity for refund in item.refunds])
            self.product_entry_treeview.insert("", tk.END, iid=item.id,
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
        # entry.bind("<FocusOut>", save_edit)

    def add_refund_and_update_stock(self):
        for row_id in self.product_entry_treeview.get_children():
            values = self.product_entry_treeview.item(row_id, "values")

            # Update product stock in the database
            product_code, returned_quantity = values[CODE_COL_INDEX], values[RETURNED_QTY_N_COL_INDEX]
            self.dbmanager.update_stock_of_product(product_code, returned_quantity)

            # Add refund history to the SaleItem
            saleitem = self.dbmanager.get_saleitem(row_id)
            refund_history = self.dbmanager.Refund(
                refund_quantity=returned_quantity,
                refund_amount=saleitem.unit_price * int(returned_quantity),
            )
            saleitem.refunds.append(refund_history)
            self.dbmanager.update_changes()
        self.parent.destroy()


class SalesFrame(tk.Frame):
    def __init__(self, parent, dbmanager):
        super().__init__(parent)
        self.dbmanager = dbmanager
        self.filter_var = tk.StringVar(value="all")
        # Options Frame ------------------------------------------------------------------------------------------------
        options_frame = tk.Frame(self, padx=20, pady=20)
        options_frame.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)

        self.all_radio_button = tk.Radiobutton(options_frame, text="সকল\nবিক্রয়", width=10, fg="white", bg="#3498db",
                                               command=self.all_sales, font=("Arial", 15),
                                               activeforeground="white", activebackground="#1abc9c",
                                               selectcolor="#1abc9c",
                                               variable=self.filter_var, value="all", indicatoron=False, height=3)
        self.all_radio_button.grid(row=0, column=0, sticky=tk.NSEW)

        self.today_radio_button = tk.Radiobutton(options_frame, text="আজকের\nবিক্রয়", width=10,
                                                 fg="white", bg="#3498db", command=self.today_invoices,
                                                 activeforeground="white", font=("Arial", 15),
                                                 activebackground="#1abc9c", selectcolor="#1abc9c",
                                                 variable=self.filter_var,
                                                 value="today", indicatoron=False, height=3)

        self.today_radio_button.grid(row=0, column=1, sticky=tk.NSEW)

        self.due_radio_button = tk.Radiobutton(options_frame, text="বাকী\nবিক্রয়", width=10,
                                               fg="white", bg="#3498db", command=self.due_invoices,
                                               activeforeground="white", font=("Arial", 15),
                                               activebackground="#1abc9c", selectcolor="#1abc9c",
                                               variable=self.filter_var,
                                               value="due", indicatoron=False, height=3)
        self.due_radio_button.grid(row=0, column=2, sticky=tk.NSEW)
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
                                     font=("Segoe UI", 14), )
        self.search_label.grid(row=0, column=0, columnspan=4, sticky=tk.NSEW)
        self.search_by_label = tk.Label(custom_search, text="খোঁজার মাধ্যম:", font=("Segoe UI", 10), )
        self.search_by_label.grid(row=1, column=0, pady=10, sticky=tk.E)

        self.search_filter = tk.StringVar(value="by_invoice")
        self.by_invoice_radiobutton = tk.Radiobutton(custom_search, text="চালান", fg="white", bg="#3498db",
                                                     activeforeground="white", width=8, font=("Segoe UI", 10),
                                                     activebackground="#1abc9c", selectcolor="#1abc9c",
                                                     variable=self.search_filter,
                                                     value="by_invoice", command=self.search_by_invoice,
                                                     indicatoron=False)
        self.by_invoice_radiobutton.grid(row=1, column=1, pady=10, sticky=tk.W)
        self.by_phone_radiobutton = tk.Radiobutton(custom_search, text="ফোন", fg="white", bg="#3498db",
                                                   activeforeground="white", width=8, font=("Segoe UI", 10),
                                                   activebackground="#1abc9c", selectcolor="#1abc9c",
                                                   variable=self.search_filter,
                                                   value="by_phone", command=self.search_by_phone, indicatoron=False)
        self.by_phone_radiobutton.grid(row=1, column=2, pady=10, sticky=tk.W)
        self.by_date_radiobutton = tk.Radiobutton(custom_search, text="তারিখ", fg="white", bg="#3498db",
                                                  activeforeground="white", width=8, font=("Segoe UI", 10),
                                                  activebackground="#1abc9c", selectcolor="#1abc9c",
                                                  variable=self.search_filter,
                                                  value="by_date", command=self.search_by_date_range, indicatoron=False)
        self.by_date_radiobutton.grid(row=1, column=3, pady=10, padx=(0, 8), sticky=tk.W)
        self.option_label = tk.Label(custom_search, text="চালান নং:", width=13, font=("Segoe UI", 10),
                                     anchor=tk.E, )
        self.option_label.grid(row=2, column=0, pady=(0, 10), padx=(7, 0), sticky=tk.E)

        self.invoice_or_phone_entry = tk.Entry(custom_search, width=10, font=("Segoe UI", 10), )
        self.invoice_or_phone_entry.grid(row=2, column=1, columnspan=2, pady=(0, 10), sticky=tk.EW)
        self.date_entry = DateEntry(
            custom_search,
            date_pattern="dd-mm-yyyy",
            width=18,
            showweeknumbers=False,
            background="#2c3e50",
            foreground="white",
            selectbackground="#1a252f",
        )
        self.date_entry.grid(row=2, column=1, pady=(0, 10), columnspan=2)
        self.date_entry.grid_remove()

        self.search_button = tk.Button(custom_search, text="খুঁজুন", font=("Segoe UI", 8),
                                       command=self.get_invoice_by_search)
        self.search_button.grid(row=2, column=3, pady=(0, 10), padx=(0, 8), sticky=tk.EW)

        # Sales Treeview Frame------------------------------------------------------------------------------------------
        self.sales_treeview_frame = tk.Frame(self)
        self.sales_treeview_frame.grid(row=1, column=0, sticky=tk.W)

        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="রিফ্রেশ", command=self.refresh)
        self.menu.add_command(label="চালান মুছুন", command=self.delete_invoice)
        self.menu.add_command(label="বাকী সংগ্রহ", command=self.receive_payment)
        self.menu.add_command(label="বাকী সংগ্রহের বিবরণ", command=self.due_payment_history)
        self.menu.add_command(label="পণ্য ফেরত", command=self.sales_return)

        columns = ("চালান নং", "তারিখ", "সময়", "গ্রাহক", "মোট প্রদেয়", "বাকী")
        self.sales_treeview = ttk.Treeview(self.sales_treeview_frame, columns=columns, show="headings", height=16)

        self.sales_treeview.bind("<<TreeviewSelect>>", self.view_invoice)
        for col in columns:
            self.sales_treeview.heading(col, text=col)
        self.sales_treeview.column("চালান নং", width=90, stretch=False, anchor=tk.W)
        self.sales_treeview.column("তারিখ", width=100, stretch=False, anchor=tk.W)
        self.sales_treeview.column("সময়", width=80, stretch=False, anchor=tk.W)
        self.sales_treeview.column("গ্রাহক", width=295, stretch=False, anchor=tk.W)
        self.sales_treeview.column("মোট প্রদেয়", width=100, stretch=False, anchor=tk.W)
        self.sales_treeview.column("বাকী", width=100, stretch=False, anchor=tk.W)
        self.sales_treeview.tag_configure("evenrow", background="#f0f0f0")
        self.sales_treeview.tag_configure("oddrow", background="#FFFFFF")
        self.sales_treeview.grid(row=0, column=0, padx=(20, 0), sticky=tk.W)

        sales_treeview_scrollbar = ttk.Scrollbar(self.sales_treeview_frame, orient=tk.VERTICAL,
                                                 command=self.sales_treeview.yview)
        sales_treeview_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.sales_treeview.configure(yscrollcommand=sales_treeview_scrollbar.set)
        self.sales_treeview.bind("<Button-3>", self.show_menu)

        invoice_frame = tk.Frame(self)
        invoice_frame.grid(row=1, column=1, sticky=tk.W)

        self.invoice_text = tk.Text(invoice_frame, width=43, height=33, font=("Courier New", 8), bd=2, )
        self.invoice_text.grid(row=0, column=0, padx=(20, 0), sticky=tk.W)
        invoice_scrollbar = ttk.Scrollbar(invoice_frame, orient=tk.VERTICAL, command=self.invoice_text.yview)
        invoice_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.invoice_text.config(yscrollcommand=invoice_scrollbar.set)

        ttk.Button(invoice_frame, text="প্রিন্ট", command=self.print_invoice).grid(row=1, column=0, padx=(20, 0),
                                                                                   pady=(15, 0), sticky=tk.EW)

        self.all_radio_button.invoke()

    def all_sales(self):
        self.disable_search_mechanism()
        self.sales_treeview.delete(*self.sales_treeview.get_children())
        sales = self.dbmanager.get_all_sales()[::-1]
        self.insert_sales_to_treeview(sales)

    def today_invoices(self):
        self.disable_search_mechanism()
        self.sales_treeview.delete(*self.sales_treeview.get_children())
        invoices = self.dbmanager.get_today_sales()[::-1]
        self.insert_sales_to_treeview(invoices)

    def due_invoices(self):
        self.disable_search_mechanism()
        self.sales_treeview.delete(*self.sales_treeview.get_children())
        due_invoices = [invoice for invoice in self.dbmanager.get_all_sales()[::-1] if invoice.due > 0]
        self.insert_sales_to_treeview(due_invoices)

    def custom_search(self):
        self.sales_treeview.delete(*self.sales_treeview.get_children())
        self.enable_search_mechanism()

    def get_invoice_by_search(self):
        filter_option = self.search_filter.get()

        if filter_option == "by_invoice":
            invoice_no = self.invoice_or_phone_entry.get()
            invoice = self.dbmanager.get_invoice(invoice_no)
            if not invoice:
                self.sales_treeview.delete(*self.sales_treeview.get_children())
                messagebox.showerror(title="পাওয়া যায়নি", message="উক্ত চালান নম্বরের চালান পাওয়া যায়নি !")
                return
            self.insert_sales_to_treeview([invoice])

        elif filter_option == "by_phone":
            phone_number = self.invoice_or_phone_entry.get()
            customer = self.dbmanager.get_customer_by_phone(phone_number)
            if not customer:
                self.sales_treeview.delete(*self.sales_treeview.get_children())
                messagebox.showerror(title="পাওয়া যায়নি", message="উক্ত ফোন নম্বরের কোন চালান পাওয়া যায়নি !")
                return
            purchases_of_the_customer = customer.purchases
            self.insert_sales_to_treeview(purchases_of_the_customer[::-1])

        elif filter_option == "by_date":
            date = self.date_entry.get()
            day, month, year = date.split("-")
            date_obj = datetime.date(day=int(day), month=int(month), year=int(year))
            invoices = self.dbmanager.get_invoices_by_date(date_obj)
            if not invoices:
                self.sales_treeview.delete(*self.sales_treeview.get_children())
                messagebox.showerror(title="পাওয়া যায়নি", message="উক্ত তারিখের কোন চালান পাওয়া যায়নি !")
                return
            self.insert_sales_to_treeview(invoices[::-1])

    def enable_search_mechanism(self):
        self.search_label.config(fg="white")
        self.option_label.config(fg="black")
        self.search_by_label.config(fg="black")
        self.by_invoice_radiobutton.config(state=tk.NORMAL)
        self.by_phone_radiobutton.config(state=tk.NORMAL)
        self.by_date_radiobutton.config(state=tk.NORMAL)
        self.invoice_or_phone_entry.config(state=tk.NORMAL)
        self.search_button.config(state=tk.NORMAL)
        self.date_entry.config(state=tk.NORMAL)

    def disable_search_mechanism(self):
        self.search_label.config(fg="gray")
        self.option_label.config(fg="gray")
        self.search_by_label.config(fg="gray")
        self.by_invoice_radiobutton.config(state=tk.DISABLED)
        self.by_phone_radiobutton.config(state=tk.DISABLED)
        self.by_date_radiobutton.config(state=tk.DISABLED)
        self.invoice_or_phone_entry.config(state=tk.DISABLED)
        self.search_button.config(state=tk.DISABLED)
        self.date_entry.config(state=tk.DISABLED, )

    def view_invoice(self, event):
        selected_sale = self.sales_treeview.selection()[0]
        sale_id = self.sales_treeview.item(selected_sale, "values")[0]
        sale = self.dbmanager.get_invoice(sale_id)
        invoice = helpers.make_invoice_for_sale(sale)

        self.invoice_text.config(state=tk.NORMAL)
        self.invoice_text.delete("1.0", tk.END)
        self.invoice_text.insert("1.0", invoice)
        self.invoice_text.config(state=tk.DISABLED)

    def print_invoice(self):
        invoice = self.invoice_text.get("1.0", tk.END)
        if invoice == "\n":
            messagebox.showerror(title="ত্রুটি", message="অনুগ্রহ করে প্রিন্ট করার জন্য একটি চালান নির্বাচন করুন!")
            return

        helpers.print_out_invoice(invoice)

    def insert_sales_to_treeview(self, sales):
        self.sales_treeview.delete(*self.sales_treeview.get_children())
        for i, sale in enumerate(sales):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.sales_treeview.insert(
                "",
                tk.END,
                values=(sale.id, sale.date.strftime("%d-%m-%Y"), sale.time.strftime("%I:%M %p"),
                        f"{sale.customer.name} - {sale.customer.phone}",
                        sale.total_payable, sale.due), tags=tag)

    def receive_payment(self):
        selected_invoice_id = self.sales_treeview.selection()[0]
        selected_invoice = self.sales_treeview.item(selected_invoice_id, "values")
        due_amount = float(selected_invoice[-1])

        if due_amount <= 0:
            messagebox.showinfo(title="বাকী নেই", message="উক্ত চালানের কোন টাকা বাকী নেই !")
            return
        else:
            def update_invoice_with_new_payment():
                if not payment_received_entry.get():
                    messagebox.showerror(title="অসম্পূর্ণ তথ্য", message="অনুগ্রহ করে টাকার পরিমাণ প্রদান করুন !")
                    return

                received_amount = float(payment_received_entry.get())

                if received_amount > invoice.due:
                    messagebox.showinfo(title="অতিরিক্ত টাকা",
                                        message="প্রাপ্ত টাকা বাকী পাওনার চেয়ে অতিরিক্ত। যাচাই করে আবার চেষ্টা করুন !")
                    return
                invoice.paid += received_amount
                invoice.due -= received_amount
                invoice.customer.balance += received_amount
                statement = self.dbmanager.CustomerStatement(customer_id=invoice.customer.id,
                                                             description=f"বাকী পরিশোধঃ বিক্রয় চালান - {invoice.id}",
                                                             amount=received_amount, balance=invoice.customer.balance)
                invoice.customer.statements.append(statement)

                customer_due_payment_history = self.dbmanager.CustomerDuePayment(amount=received_amount)
                invoice.payment_history.append(customer_due_payment_history)

                self.dbmanager.add_customer_due_payment_history(customer_due_payment_history)
                self.dbmanager.update_changes()
                payment_win.destroy()
                self.refresh()

            payment_win = tk.Toplevel(self.sales_treeview_frame)
            payment_win.title("বাকী সংগ্রহ")
            payment_win.config(padx=20, pady=20)

            self.center_window(payment_win, 215, 245)

            invoice_id = selected_invoice[0]
            invoice = self.dbmanager.get_invoice(invoice_id)
            # Invoice No
            tk.Label(payment_win, text=f"চালান নং", font=("Segoe UI", 12, "bold"),
                     anchor=tk.W, ).grid(row=0, column=0, sticky=tk.W)
            tk.Label(payment_win, text=":", font=("Segoe UI", 12, "bold"),
                     anchor=tk.W, ).grid(row=0, column=1, sticky=tk.W)
            tk.Label(payment_win, text=f"{invoice.id}", font=("Segoe UI", 12, "bold"),
                     anchor=tk.W, ).grid(row=0, column=2, sticky=tk.W)

            # Total Payable
            tk.Label(payment_win, text=f"মোট প্রদেয়", font=("Segoe UI", 12, "bold"),
                     anchor=tk.W, ).grid(row=1, column=0, sticky=tk.W)
            tk.Label(payment_win, text=":", font=("Segoe UI", 12, "bold"),
                     anchor=tk.W, ).grid(row=1, column=1, sticky=tk.W)
            tk.Label(payment_win, text=f"{invoice.total_payable}", font=("Segoe UI", 12, "bold"),
                     anchor=tk.W, ).grid(row=1, column=2, sticky=tk.W)

            # Total Payable
            tk.Label(payment_win, text=f"পরিশোধিত", font=("Segoe UI", 12, "bold"),
                     anchor=tk.W, ).grid(row=2, column=0, sticky=tk.W)
            tk.Label(payment_win, text=":", font=("Segoe UI", 12, "bold"),
                     anchor=tk.W, ).grid(row=2, column=1, sticky=tk.W)
            tk.Label(payment_win, text=f"{invoice.paid}", font=("Segoe UI", 12, "bold"),
                     anchor=tk.W, ).grid(row=2, column=2, sticky=tk.W)

            # Due
            tk.Label(payment_win, text=f"বাকী", fg="red", font=("Segoe UI", 12, "bold"),
                     anchor=tk.W, ).grid(row=3, column=0, sticky=tk.W)
            tk.Label(payment_win, text=":", fg="red", font=("Segoe UI", 12, "bold"),
                     anchor=tk.W, ).grid(row=3, column=1, sticky=tk.W)
            tk.Label(payment_win, text=f"{invoice.due}", fg="red", font=("Segoe UI", 12, "bold"),
                     anchor=tk.W, ).grid(row=3, column=2, sticky=tk.W)

            tk.Label(payment_win, text="বাকী সংগ্রহ", font=("Segoe UI", 12, "bold"), anchor=tk.W, ).grid(row=4,
                                                                                                         column=0,
                                                                                                         sticky=tk.W)
            tk.Label(payment_win, text=":", font=("Segoe UI", 12, "bold"), anchor=tk.W, ).grid(row=4, column=1,
                                                                                               sticky=tk.W)
            payment_received_entry = tk.Entry(payment_win, width=10, font=("Segoe UI", 12))
            payment_received_entry.focus_set()
            payment_received_entry.grid(row=4, column=2)
            tk.Button(payment_win, text="নিশ্চিত করুন", command=update_invoice_with_new_payment).grid(row=5, column=1,
                                                                                                      columnspan=2,
                                                                                                      pady=10,
                                                                                                      sticky=tk.NSEW)
            payment_win.transient()
            payment_win.grab_set()  # modal behavior
            payment_win.resizable(False, False)

    def delete_invoice(self):
        selected_invoice_iid = self.sales_treeview.selection()[0]
        invoice_id = self.sales_treeview.item(selected_invoice_iid, "values")[0]
        invoice = self.dbmanager.get_invoice(invoice_id)

        # Check if the invoice has return or not.
        for saleitem in invoice.items:
            for refund in saleitem.refunds:
                if refund:
                    messagebox.showinfo(title="ত্রুটি", message="দুঃখিত, উক্ত চালানটি মুছা সম্ভব নয় !")
                    return

        # Restore Stocks
        for item in invoice.items:
            self.dbmanager.update_stock_of_product(item.product_code, item.quantity)
            self.dbmanager.delete_saleitem(item)

        self.dbmanager.delete_invoice(invoice)
        self.refresh()
        messagebox.showinfo(title="সফল", message="চালানটি সফলভাবে মুছা হয়েছে !")


    def due_payment_history(self):
        selected_invoice_iid = self.sales_treeview.selection()[0]
        invoice_id = self.sales_treeview.item(selected_invoice_iid, "values")[0]
        invoice = self.dbmanager.get_invoice(invoice_id)

        if not invoice.payment_history:
            messagebox.showinfo(title="পাওয়া যায়নি", message="উক্ত চালানের বাকী সংগ্রহের বিবরণ পাওয়া যায়নি !")
            return

        payment_history_window = tk.Toplevel(self.sales_treeview_frame)
        payment_history_window.title("বাকী সংগ্রহের বিবরণ")
        payment_history_window.config(padx=20, pady=20)
        self.center_window(payment_history_window, 485, 510)
        payment_history_window.transient()
        payment_history_window.grab_set()  # modal behavior
        payment_history_window.resizable(False, False)

        DuePaymentHistoryFrame(payment_history_window, invoice, self.dbmanager)

    def center_window(self, win, custom_height, custom_width):
        win.update_idletasks()
        width = custom_width
        height = custom_height
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")

    def sales_return(self):
        sales_return_window = tk.Toplevel(self.sales_treeview_frame)
        sales_return_window.title("পণ্য ফেরত")
        sales_return_window.config(padx=20, pady=20)
        self.center_window(sales_return_window, 550, 1085)
        sales_return_window.transient()
        sales_return_window.grab_set()  # modal behavior
        sales_return_window.resizable(False, False)
        selected_invoice_iid = self.sales_treeview.selection()[0]
        invoice_id = self.sales_treeview.item(selected_invoice_iid, "values")[0]
        invoice = self.dbmanager.get_invoice(invoice_id)
        RefundFrame(sales_return_window, invoice, self.dbmanager)

    def search_by_invoice(self):
        self.option_label.config(text="চালান নং:")
        self.show_invoice_or_phone_entry_search()

    def search_by_phone(self):
        self.option_label.config(text="মোবাইল নম্বর:")
        self.show_invoice_or_phone_entry_search()

    def search_by_date_range(self):
        self.option_label.config(text="তারিখ:")
        self.show_custom_date_search()

    def show_invoice_or_phone_entry_search(self):
        self.date_entry.grid_remove()
        self.invoice_or_phone_entry.grid()

    def show_custom_date_search(self):
        self.invoice_or_phone_entry.grid_remove()
        self.date_entry.grid()

    def refresh(self):
        filter_option = self.filter_var.get()
        if filter_option == "all":
            self.all_radio_button.invoke()
        elif filter_option == "today":
            self.today_radio_button.invoke()
        elif filter_option == "due":
            self.due_radio_button.invoke()
        elif filter_option == "custom_search":
            self.search_button.invoke()

    def show_menu(self, event):
        iid = self.sales_treeview.identify_row(event.y)
        if iid:
            self.sales_treeview.selection_set(iid)
            self.menu.tk_popup(event.x_root, event.y_root)
