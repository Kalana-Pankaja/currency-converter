import tkinter as tk
from tkinter import ttk, messagebox
import requests

class CurrencyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter 💱")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        self.base_currency_var = tk.StringVar()
        self.target_currency_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.result_var = tk.StringVar()

        self.symbols = self.fetch_symbols()
        if not self.symbols:
            messagebox.showerror("Error", "Failed to load currencies. Check your internet connection or API.")
            root.destroy()
            return

        self.create_widgets()

    def fetch_symbols(self):
        try:
            print("Fetching available currencies...")
            response = requests.get("https://api.exchangerate.host/symbols", timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("success") and "symbols" in data:
                return sorted(data["symbols"].keys())
            return None
        except Exception as e:
            print("Error fetching symbols:", e)
            return None

    def create_widgets(self):
        ttk.Label(self.root, text="Base Currency:").pack(pady=5)
        base_menu = ttk.Combobox(self.root, textvariable=self.base_currency_var, values=self.symbols)
        base_menu.pack()

        ttk.Label(self.root, text="Target Currency:").pack(pady=5)
        target_menu = ttk.Combobox(self.root, textvariable=self.target_currency_var, values=self.symbols)
        target_menu.pack()

        ttk.Label(self.root, text="Amount:").pack(pady=5)
        ttk.Entry(self.root, textvariable=self.amount_var).pack()

        ttk.Button(self.root, text="Convert", command=self.convert_currency).pack(pady=15)
        ttk.Label(self.root, textvariable=self.result_var, font=("Arial", 12)).pack(pady=10)

    def convert_currency(self):
        base = self.base_currency_var.get()
        target = self.target_currency_var.get()
        amount_str = self.amount_var.get()

        if not base or not target or not amount_str:
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number.")
            return

        url = f"https://api.exchangerate.host/convert?from={base}&to={target}&amount={amount}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("success"):
                result = data["result"]
                self.result_var.set(f"{amount:.2f} {base} = {result:.2f} {target}")
            else:
                messagebox.showerror("Conversion Error", "Failed to convert currencies.")
        except Exception as e:
            messagebox.showerror("Error", f"Conversion failed:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyApp(root)
    root.mainloop()
