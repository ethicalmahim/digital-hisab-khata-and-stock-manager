import os
import sys

# When running as a PyInstaller exe, use the exe's folder as the working directory
# so database/ and .env are read from (and stored next to) the exe.
if getattr(sys, "frozen", False):
    os.chdir(os.path.dirname(sys.executable))
os.makedirs("database", exist_ok=True)


def resource_path(relative_path):
    """Path to a bundled resource (works for both source and PyInstaller exe)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)


import tkinter as tk
from tkinter import ttk
from ui.dashboard import DashboardFrame
from ui.sales_management import NewSaleFrame, SalesFrame
from ui.purchases_management import NewPurchase, PurchasesFrame
from ui.expenses_management import ExpensesFrame
from ui.product_management import ProductsFrame
from ui.customer_management import CustomersFrame
from utils import database_management as db
from ui.supplier_management import SuppliersFrame

TITLE = "ডিজিটাল হিসাব খাতা ও স্টক ম্যানেজার"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(TITLE)
        self.state('zoomed')

        style = ttk.Style(self)
        style.theme_use("clam")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar_frame = tk.Frame(self, bg="#2c3e50", width=200, height=500)
        self.sidebar_frame.grid(row=0, column=0, sticky=tk.NS)
        self.sidebar_frame.grid_propagate(False)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)

        # Content area
        self.content_frame = tk.Frame(self)
        self.content_frame.grid(row=0, column=1, sticky=tk.NSEW)
        self.content_frame.grid_propagate(False)

        # Sidebar button style
        style.configure("Sidebar.TButton", font=("Arial", 15), foreground="white", background="#2c3e50", borderwidth=0,
                        relief="solid", padding=10)
        style.map("Sidebar.TButton", background=[("active", "#1a252f")], relief=[("pressed", "sunken")])

        # Sidebar Buttons
        ttk.Button(self.sidebar_frame, text="ড্যাশবোর্ড", style="Sidebar.TButton",
                   command=lambda: self.show_frame("dashboard")).grid(row=0, column=0, sticky=tk.EW)
        ttk.Separator(self.sidebar_frame, orient=tk.HORIZONTAL).grid(row=1, column=0, sticky=tk.EW)

        ttk.Button(self.sidebar_frame, text="নতুন বিক্রয়", style="Sidebar.TButton",
                   command=lambda: self.show_frame("new_sale")).grid(row=2, column=0, sticky=tk.EW)
        ttk.Separator(self.sidebar_frame, orient=tk.HORIZONTAL).grid(row=3, column=0, sticky=tk.EW)

        ttk.Button(self.sidebar_frame, text="বিক্রয়সমূহ", style="Sidebar.TButton",
                   command=lambda: self.show_frame("sales")).grid(row=4, column=0, sticky=tk.EW)
        ttk.Separator(self.sidebar_frame, orient=tk.HORIZONTAL).grid(row=5, column=0, sticky=tk.EW)

        ttk.Button(self.sidebar_frame, text="নতুন ক্রয়", style="Sidebar.TButton",
                   command=lambda: self.show_frame("new_purchase")).grid(row=6, column=0, sticky=tk.EW)
        ttk.Separator(self.sidebar_frame, orient=tk.HORIZONTAL).grid(row=7, column=0, sticky=tk.EW)

        ttk.Button(self.sidebar_frame, text="ক্রয়সমূহ", style="Sidebar.TButton",
                   command=lambda: self.show_frame("purchases")).grid(row=8, column=0, sticky=tk.EW)
        ttk.Separator(self.sidebar_frame, orient=tk.HORIZONTAL).grid(row=9, column=0, sticky=tk.EW)

        ttk.Button(self.sidebar_frame, text="খরচসমূহ", style="Sidebar.TButton",
                   command=lambda: self.show_frame("expenses")).grid(row=10, column=0, sticky=tk.EW)
        ttk.Separator(self.sidebar_frame, orient=tk.HORIZONTAL).grid(row=11, column=0, sticky=tk.EW)

        ttk.Button(self.sidebar_frame, text="পণ্যসমূহ", style="Sidebar.TButton",
                   command=lambda: self.show_frame("products")).grid(row=12, column=0, sticky=tk.EW)
        ttk.Separator(self.sidebar_frame, orient=tk.HORIZONTAL).grid(row=13, column=0, sticky=tk.EW)

        ttk.Button(self.sidebar_frame, text="গ্রাহক", style="Sidebar.TButton",
                   command=lambda: self.show_frame("customers")).grid(row=14, column=0, sticky=tk.EW)
        ttk.Separator(self.sidebar_frame, orient="horizontal").grid(row=15, column=0, sticky=tk.EW)

        ttk.Button(self.sidebar_frame,
                   text="সাপ্লায়ার", style="Sidebar.TButton", command=lambda: self.show_frame("suppliers")).grid(row=16,
                                                                                                                 column=0,
                                                                                                                 sticky=tk.EW)
        ttk.Separator(self.sidebar_frame, orient="horizontal").grid(row=17, column=0, sticky=tk.EW)


        # Frames for content
        self.frames = {}
        for name, frame_class in {
            "dashboard": DashboardFrame,
            "new_sale": NewSaleFrame,
            "sales": SalesFrame,
            "new_purchase": NewPurchase,
            "purchases": PurchasesFrame,
            "expenses": ExpensesFrame,
            "products": ProductsFrame,
            "customers": CustomersFrame,
            "suppliers": SuppliersFrame,
        }.items():
            frame = frame_class(self.content_frame, db)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky=tk.NSEW)

        self.show_frame("dashboard")
        self.iconbitmap(resource_path("img/icon.ico"))

    def show_frame(self, name):
        self.frames[name].tkraise()


if __name__ == "__main__":
    app = App()
    app.mainloop()
