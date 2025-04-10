import requests
import time
import json
import os
from datetime import datetime
import sys

class CurrencyConverter:
    """A class to handle currency conversion operations."""
    
    def __init__(self):
        self.base_url = "https://api.exchangerate.host"
        self.history_file = "conversion_history.json"
        self.available_currencies = None
        self.history = self._load_history()
        self.emoji = self._get_emoji_support()

    def _get_emoji_support(self):
        """Check if the terminal supports emojis."""
        if sys.platform == "win32":
            return False  # Windows doesn't support emojis by default
        return True
    
    def _load_history(self):
        """Load conversion history from file if it exists."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"conversions": []}
        return {"conversions": []}
    
    def _save_history(self):
        """Save conversion history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save history: {e}")
    
    def get_available_currencies(self):
        """Get list of available currencies from the API."""
        if self.available_currencies:
            return self.available_currencies
        
        try:
            print("Fetching available currencies...")
            response = requests.get(f"{self.base_url}/symbols")
            response.raise_for_status()
            data = response.json()
            
            if data.get("success", False) and "symbols" in data:
                self.available_currencies = data["symbols"]
                return self.available_currencies
            else:
                print("Error: Could not retrieve currency list.")
                return None
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return None
    
    def display_available_currencies(self):
        """Display available currencies in a formatted way."""
        currencies = self.get_available_currencies()
        if not currencies:
            return
        
        print("\n=== Available Currencies ===")
        # Print in columns (3 currencies per line)
        count = 0
        for code, data in currencies.items():
            print(f"{code}: {data['description'][:20]:<20}", end="  ")
            count += 1
            if count % 3 == 0:
                print()
        if count % 3 != 0:
            print()
        print("=" * 30)
    
    def validate_currency(self, currency_code):
        """Validate if a currency code exists."""
        currencies = self.get_available_currencies()
        if not currencies:
            return False
        return currency_code in currencies
    
    def get_exchange_rate(self, base_currency, target_currency):
        """Get the exchange rate between two currencies."""
        try:
            print(f"Fetching exchange rate for {base_currency} to {target_currency}...")
            url = f"{self.base_url}/latest?base={base_currency}&symbols={target_currency}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("success", True):  # Some APIs use success flag
                print(f"API Error: {data.get('error', 'Unknown error')}")
                return None
                
            if "rates" in data and target_currency in data['rates']:
                return data['rates'][target_currency]
            else:
                print(f"Could not find rate for {target_currency}")
                return None
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return None
    
    def convert_currency(self, base_currency, target_currencies, amount):
        """Convert from base currency to one or more target currencies."""
        results = []
        
        # Validate currencies first
        base_valid = self.validate_currency(base_currency)
        if not base_valid:
            print(f"Error: '{base_currency}' is not a valid currency code.")
            return results
        
        invalid_targets = [c for c in target_currencies if not self.validate_currency(c)]
        if invalid_targets:
            print(f"Error: Invalid target currency code(s): {', '.join(invalid_targets)}")
            target_currencies = [c for c in target_currencies if c not in invalid_targets]
            if not target_currencies:
                return results
        
        # Perform conversions for each target currency
        for target_currency in target_currencies:
            # Skip if base and target are the same
            if base_currency == target_currency:
                results.append({
                    "base": base_currency,
                    "target": target_currency,
                    "amount": amount,
                    "converted": amount,
                    "rate": 1.0,
                    "timestamp": datetime.now().isoformat()
                })
                print(f"{amount:.2f} {base_currency} = {amount:.2f} {target_currency} (same currency)")
                continue
                
            rate = self.get_exchange_rate(base_currency, target_currency)
            if rate is not None:
                converted_amount = amount * rate
                
                # Create result dictionary
                result = {
                    "base": base_currency,
                    "target": target_currency,
                    "amount": amount,
                    "converted": converted_amount,
                    "rate": rate,
                    "timestamp": datetime.now().isoformat()
                }
                results.append(result)
                
                # Add to history
                self.history["conversions"].append(result)
                # Keep only the last 10 conversions
                if len(self.history["conversions"]) > 10:
                    self.history["conversions"] = self.history["conversions"][-10:]
                self._save_history()
                
                # Display result with proper formatting
                print(f"{amount:.2f} {base_currency} = {converted_amount:.2f} {target_currency} (rate: {rate:.6f})")
        
        return results
    
    def show_history(self):
        """Display recent conversion history."""
        conversions = self.history["conversions"]
        if not conversions:
            print("No conversion history available.")
            return
        
        print("\n=== Recent Conversions ===")
        for i, conv in enumerate(reversed(conversions), 1):
            base = conv["base"]
            target = conv["target"]
            amount = conv["amount"]
            converted = conv["converted"]
            timestamp = conv["timestamp"].split("T")[0]  # Just get the date part
            print(f"{i}. {timestamp}: {amount:.2f} {base} → {converted:.2f} {target}")
        print("=" * 30)

def main():
    """Main function for the currency converter application."""
    converter = CurrencyConverter()
    
    # Use emojis if supported by terminal
    print(f"{'💱' if converter.emoji else ''} Enhanced Currency Converter {'💱' if converter.emoji else ''}")
    print("Type 'exit' at any prompt to quit")
    print("Type 'currencies' to see available currencies")
    print("Type 'history' to see your recent conversions")
    
    while True:
        print("\nWhat would you like to do?")
        choice = input("1. Convert currencies\n2. Show available currencies\n3. View history\n4. Exit\nEnter choice (1-4): ")
        
        if choice == '4' or choice.lower() == 'exit':
            print("Thank you for using the Currency Converter!")
            break
            
        elif choice == '2' or choice.lower() == 'currencies':
            converter.display_available_currencies()
            
        elif choice == '3' or choice.lower() == 'history':
            converter.show_history()
            
        elif choice == '1':
            base = input("Enter base currency (e.g., USD): ").upper()
            if base.lower() == 'exit':
                break
            if base.lower() == 'currencies':
                converter.display_available_currencies()
                continue
            if base.lower() == 'history':
                converter.show_history()
                continue
                
            target_input = input("Enter target currency/currencies (e.g., EUR,GBP,JPY): ").upper()
            if target_input.lower() == 'exit':
                break
            if target_input.lower() == 'currencies':
                converter.display_available_currencies()
                continue
            if target_input.lower() == 'history':
                converter.show_history()
                continue
                
            target_currencies = [c.strip() for c in target_input.split(',')]
            
            try:
                amount_input = input("Enter amount:  ")
                if amount_input.lower() == 'exit':
                    break
                amount = float(amount_input)
                if amount < 0:
                    print("Please enter a positive number.")
                    continue
                    
                converter.convert_currency(base, target_currencies, amount)
                
            except ValueError:
                print("Please enter a valid number.")
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
