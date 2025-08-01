import tkinter as tk
from tkinter import messagebox
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Calculator:
    def __init__(self):
        self.root = tk.Tk()
        self.entry = tk.Entry(self.root)
        self.button_frame = tk.Frame(self.root)

        # Create buttons for digits 0-9
        for i in range(10):
            button = tk.Button(self.button_frame, text=str(i), command=lambda x=i: self.append_to_entry(x))
            button.pack(side=tk.LEFT)

        # Create buttons for basic arithmetic operations
        operation_buttons = [
            ('+', self.add),
            ('-', self.subtract),
            ('*', self.multiply),
            ('/', self.divide)
        ]

        for label, func in operation_buttons:
            tk.Button(self.button_frame, text=label, command=func).pack(side=tk.LEFT)

        # Create equals button
        tk.Button(self.button_frame, text='=', command=self.calculate).pack(side=tk.LEFT)

        # Pack widgets
        self.entry.pack()
        self.button_frame.pack()

    def append_to_entry(self, value):
        try:
            current_value = float(self.entry.get())
            new_value = current_value * 10 + value
            self.entry.delete(0, tk.END)
            self.entry.insert(0, str(new_value))
        except ValueError:
            logging.warning("Invalid input")

    def add(self):
        try:
            current_value = float(self.entry.get())
            new_value = current_value + 1
            self.entry.delete(0, tk.END)
            self.entry.insert(0, str(new_value))
        except ValueError:
            logging.warning("Invalid input")

    def subtract(self):
        try:
            current_value = float(self.entry.get())
            new_value = current_value - 1
            self.entry.delete(0, tk.END)
            self.entry.insert(0, str(new_value))
        except ValueError:
            logging.warning("Invalid input")

    def multiply(self):
        try:
            current_value = float(self.entry.get())
            new_value = current_value * 2
            self.entry.delete(0, tk.END)
            self.entry.insert(0, str(new_value))
        except ValueError:
            logging.warning("Invalid input")

    def divide(self):
        try:
            current_value = float(self.entry.get())
            if current_value == 0:
                messagebox.showerror("Error", "Cannot divide by zero")
            else:
                new_value = current_value / 2
                self.entry.delete(0, tk.END)
                self.entry.insert(0, str(new_value))
        except ValueError:
            logging.warning("Invalid input")

    def calculate(self):
        try:
            result = eval(self.entry.get())
            self.entry.delete(0, tk.END)
            self.entry.insert(0, str(result))
        except Exception as e:
            messagebox.showerror("Error", "Invalid calculation")
            logging.error(str(e))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    calculator = Calculator()
    calculator.run()
