#Banking App Using Python and MySQL
import mysql.connector
from mysql.connector import pooling
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk

commission_fee = 30.00 #Public variable for commission fee

#Database Connection Pool
connection_pool = pooling.MySQLConnectionPool(
    pool_name="bank_pool",
    pool_size=5,
    host="localhost",
    user="root",
    password="",
    database="banking_app"
)

def get_connection():
    return connection_pool.get_connection()

#Check whether user account is valid or not
def get_user(account_no, password):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE account_no = %s AND password = %s", (account_no, password))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    return user

def get_balance(account_no):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT balance FROM users WHERE account_no = %s", (account_no,))
    balance = cursor.fetchone()
    cursor.close()
    db.close()
    return balance[0] if balance else 0.0

def update_balance(account_no, amount, is_add=True):
    db = get_connection()
    cursor = db.cursor()
    if is_add:
        cursor.execute("UPDATE users SET balance = balance + %s WHERE account_no = %s", (amount, account_no))
        cursor.execute("INSERT INTO transactions (account_no, type, amount) VALUES (%s, %s, %s)", (account_no, 'Deposit', amount))
    else:
        cursor.execute("UPDATE users SET balance = balance - %s WHERE account_no = %s", (amount, account_no))
        cursor.execute("INSERT INTO transactions (account_no, type, amount) VALUES (%s, %s, %s)", (account_no, 'Withdraw', amount))
    db.commit()
    cursor.close()
    db.close()

def update_transfer_balance(account_no, amount, username, is_add=True):
    db = get_connection()
    cursor = db.cursor()
    if is_add:
        cursor.execute("UPDATE users SET balance = balance + %s WHERE account_no = %s", (amount, account_no))
        cursor.execute("INSERT INTO transactions (account_no, type, amount) VALUES (%s, %s, %s)", (account_no, 'Transferred by '+username, amount))
    else:
        cursor.execute("UPDATE users SET balance = balance - %s WHERE account_no = %s", (amount, account_no))
        cursor.execute("INSERT INTO transactions (account_no, type, amount) VALUES (%s, %s, %s)", (account_no, 'Transferred to '+username, amount-commission_fee))
        cursor.execute("INSERT INTO transactions (account_no, type, amount) VALUES (%s, %s, %s)", (account_no, 'Commission Fee', commission_fee))
    db.commit()
    cursor.close()
    db.close()

#Check whether receiver account is valid or not
def get_transfer_user(transfer_account_no):
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE account_no = %s", (transfer_account_no,))
    transfer_user = cursor.fetchone()
    cursor.close()
    db.close()
    return transfer_user

class BankingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Banking App")

        #Load image as favicon
        favicon = Image.open("assets/logo.png")
        self.favicon = ImageTk.PhotoImage(favicon)
        self.root.iconphoto(True, self.favicon)
        
        #Load background image
        self.bg_image = Image.open("assets/background_image.png")
        self.bg_image = self.bg_image.resize((800, 600))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.current_user = None
        self.create_login_interface()
    
    def create_login_interface(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        #Display Background Image
        self.bg_label = tk.Label(self.root, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)

        #Center the frame
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        #Frame for login form
        frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        frame.grid(row=0, column=0)

        #Load and display logo image
        image = Image.open("assets/logo.png")
        image = image.resize((150, 150))
        self.logo = ImageTk.PhotoImage(image)
        tk.Label(frame, image=self.logo, bg="#f0f0f0").grid(row=0, column=0, columnspan=2, pady=(10,0))

        #Login Label
        tk.Label(frame, text="Login", bg="#f0f0f0", font=("Arial", 20, "bold")).grid(row=1, column=0, columnspan=2, pady=(0,10))

        #Account number field
        tk.Label(frame, text="Account Number", bg="#f0f0f0", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.account_entry = tk.Entry(frame, font=("Arial", 12))
        self.account_entry.grid(row=2, column=1, padx=10, pady=5)

        #Password field
        tk.Label(frame, text="Password", bg="#f0f0f0", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.password_entry = tk.Entry(frame, show="*", font=("Arial", 12))
        self.password_entry.grid(row=3, column=1, padx=10, pady=5)

        #Login button
        tk.Button(frame, text="Login", command=self.login, font=("Arial", 12, "bold"), bg="#4a7ef7", fg="white", width=15).grid(row=4, column=0, columnspan=2, pady=20)
    
    def login(self):
        account_no = self.account_entry.get()
        password = self.password_entry.get()
        user = get_user(account_no, password)
        if user:
            self.current_user = user
            self.create_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid account number or password!")
    
    def create_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        #Display Background Image
        self.bg_label = tk.Label(self.root, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)

        #Center the frame
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        #Frame for dashboard
        frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        frame.grid(row=0, column=0)
        
        balance = get_balance(self.current_user['account_no'])
        
        #Display Username
        tk.Label(frame, text=f"Welcome, {self.current_user['username']}", fg="#4a7ef7", font=("Arial", 20, "bold")).grid(row=0, column=0, columnspan=3, pady=(10,0))

        #Show balance label
        tk.Label(frame, text=f"Balance: Rs. {balance:.2f}", bg="#000000", fg="white", font=("Arial", 16, "bold"), width=38, height=3).grid(row=1, column=0, columnspan=3, pady=(5,5))

        #Buttons to navigate to each page of the Dashboard
        tk.Button(frame, text="View All Transactions", width=20, command=self.create_view_all_transactions_interface, font=("Arial", 12, "bold"), bg="#4a7ef7", fg="white").grid(row=2, column=0, columnspan=3, pady=(0,30))
        tk.Button(frame, text="Deposit", width=15, height=5, command=self.create_deposit_interface, font=("Arial", 12, "bold"), bg="#273f66", fg="white").grid(row=3, column=0, padx=10)
        tk.Button(frame, text="Withdraw", width=15, height=5, command=self.create_withdraw_interface, font=("Arial", 12, "bold"), bg="#9615b3", fg="white").grid(row=3, column=1)
        tk.Button(frame, text="Transfer \nMoney", width=15, height=5, command=self.create_transfer_interface, font=("Arial", 12, "bold"), bg="#6115b3", fg="white").grid(row=3, column=2, padx=10)

        #Button to navigate to login page
        tk.Button(frame, text="Logout", command=self.create_login_interface, font=("Arial", 12, "bold"), bg="#000000", fg="white", width=15).grid(row=4, column=0, columnspan=3, pady=30)
    
    def create_deposit_interface(self):
        self.create_transaction_interface("Deposit", True)
    
    def create_withdraw_interface(self):
        self.create_transaction_interface("Withdraw", False)
    
    #Interface for deposit and withdraw
    def create_transaction_interface(self, action, is_deposit):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        #Display Background Image
        self.bg_label = tk.Label(self.root, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)

        #Center the frame
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        #Frame for deposit and withdraw ui
        frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        frame.grid(row=0, column=0)
        
        tk.Label(frame, text=f"{action}", bg="#f0f0f0", font=("Arial", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        #Amount Field
        tk.Label(frame, text=f"{action} Amount", bg="#f0f0f0", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.amount_entry = tk.Entry(frame, font=("Arial", 12))
        self.amount_entry.grid(row=1, column=1, padx=10, pady=5)

        #Buttons to submit the process or discard the process
        tk.Button(frame, text=action, command=lambda: self.process_transaction(is_deposit), font=("Arial", 12, "bold"), bg="#4a7ef7", fg="white", width=15).grid(row=2, column=0, padx=10, pady=20)
        tk.Button(frame, text="Back", command=self.create_dashboard, font=("Arial", 12, "bold"), bg="#000000", fg="white", width=15).grid(row=2, column=1, padx=10, pady=20)
    
    #Check whether deposit or withdraw amount is valid or not
    def process_transaction(self, is_deposit):
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError("Invalid amount!")
            
            if not is_deposit:
                balance = get_balance(self.current_user['account_no'])
                if amount > balance:
                    messagebox.showerror("Error", "Insufficient funds!")
                    return
                
            update_balance(self.current_user['account_no'], amount, is_deposit)
            messagebox.showinfo("Success", f"Transaction successful! Rs. {amount:.2f} {'deposited' if is_deposit else 'withdrawn'}.")
            self.create_dashboard()
        except ValueError:
            messagebox.showerror("Error", "Invalid amount!")
    
    #Interface to transfer money
    def create_transfer_interface(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        #Display Background Image
        self.bg_label = tk.Label(self.root, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)

        #Center the frame
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        #Frame for transfer money ui
        frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        frame.grid(row=0, column=0)
        
        tk.Label(frame, text="Transfer Money", bg="#f0f0f0", font=("Arial", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=(10,0))
        tk.Label(frame, text=f"Commission Fee to Transfer Money is Rs. {commission_fee:.2f}", bg="#f0f0f0", fg="#FF0000", font=("Arial", 16)).grid(row=1, column=0, columnspan=2, pady=(5,20))

        #Receiver account no field
        tk.Label(frame, text="Recipient's Account Number", bg="#f0f0f0", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.recipient_entry = tk.Entry(frame, font=("Arial", 12))
        self.recipient_entry.grid(row=2, column=1, padx=10, pady=5)
        
        #Amount to transfer
        tk.Label(frame, text="Amount to Transfer", bg="#f0f0f0", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.amount_entry = tk.Entry(frame, font=("Arial", 12))
        self.amount_entry.grid(row=3, column=1, padx=10, pady=5)
        
        #Buttons to submit the process or discard the process
        tk.Button(frame, text="Transfer", command=self.transfer_money, font=("Arial", 12, "bold"), bg="#4a7ef7", fg="white", width=15).grid(row=4, column=0, padx=10, pady=20)
        tk.Button(frame, text="Back", command=self.create_dashboard, font=("Arial", 12, "bold"), bg="#000000", fg="white", width=15).grid(row=4, column=1, padx=10, pady=20)
    
    #Check whether transfer amount is valid or not
    def transfer_money(self):
        try:
            recipient_no = self.recipient_entry.get()
            amount = float(self.amount_entry.get())
            total_amount = amount + commission_fee
            
            if amount <= 0:
                raise ValueError("Invalid amount!")
            
            recipient = get_transfer_user(recipient_no)
            if not recipient:
                messagebox.showerror("Error", "Recipient not found!")
                return

            #Check whether sender's account no and recipient's account no are same or not
            if recipient['account_no'] == self.current_user['account_no']:
                messagebox.showerror("Error", "Cannot transfer money to your own account")
                return
            
            balance = get_balance(self.current_user['account_no'])
            if total_amount > balance:
                messagebox.showerror("Error", "Insufficient funds!")
                return
            
            update_transfer_balance(self.current_user['account_no'], total_amount, recipient['username'], False)
            update_transfer_balance(recipient_no, amount, self.current_user['username'], True)
            messagebox.showinfo("Success", f"Rs. {amount:.2f} transferred to {recipient['username']}. \nCommission Fee: Rs. {commission_fee:.2f}")
            self.create_dashboard()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid amount!")

    #Interface to view all transactions
    def create_view_all_transactions_interface(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        #Display Background Image
        self.bg_label = tk.Label(self.root, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)

        #Center the frame
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        #Frame for view all transactions UI
        frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        frame.grid(row=0, column=0)

        tk.Label(frame, text="Transaction History", bg="#f0f0f0", font=("Arial", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        #Fetch transactions
        db = get_connection()
        cursor = db.cursor()
        cursor.execute("SELECT date, type, amount FROM transactions WHERE account_no=%s ORDER BY date DESC", (self.current_user['account_no'],))
        transactions = cursor.fetchall()
        db.close()

        #Table Frame
        table_frame = tk.Frame(frame)
        table_frame.grid(row=1, column=0, columnspan=2)

        #Scrollbar
        tree_scroll = ttk.Scrollbar(table_frame)
        tree_scroll.pack(side="right", fill="y")

        #Define Treeview Style
        style = ttk.Style()
        style.configure("Bold.Treeview", font=("Arial", 12))
        style.configure("Bold.Treeview.Heading", font=("Arial", 14, "bold"))

        #Treeview Table
        columns = ("Date", "Type", "Amount")
        transaction_table = ttk.Treeview(table_frame, columns=columns, show="headings", yscrollcommand=tree_scroll.set, height=10, style="Bold.Treeview")
        
        #Define Column Headings
        transaction_table.heading("Date", text="Date")
        transaction_table.heading("Type", text="Type")
        transaction_table.heading("Amount", text="Amount")

        #Adjust Column Width
        transaction_table.column("Date", anchor="center", width=180)
        transaction_table.column("Type", anchor="w", width=300)
        transaction_table.column("Amount", anchor="e", width=120)

        transaction_table.pack()
        tree_scroll.config(command=transaction_table.yview)

        #Insert Transactions into Table
        for t in transactions:
            transaction_table.insert("", "end", values=t)

        #Back Button
        tk.Button(frame, text="Back", command=self.create_dashboard, font=("Arial", 12, "bold"), bg="#000000", fg="white", width=15).grid(row=2, column=0, columnspan=2, pady=20)

root = tk.Tk()
app = BankingApp(root)
root.mainloop()
