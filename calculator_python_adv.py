import tkinter as tk
import math
import ast
import operator
import logging
from concurrent.futures import ProcessPoolExecutor

# Logging

logger = logging.getLogger("AdvancedCalculator")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("advanced_calculator.log", encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

# Math functions with degrees and rounding for tiny values

def round_small(val, eps=1e-10):
    return 0 if abs(val) < eps else val

def sin_deg(x): return round_small(math.sin(math.radians(x)))
def cos_deg(x): return round_small(math.cos(math.radians(x)))
def tan_deg(x): return round_small(math.tan(math.radians(x)))


# Safe eval

ALLOWED_NAMES = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
ALLOWED_NAMES.update({
    'abs': abs,
    'pow': pow,
    'sin': sin_deg,
    'cos': cos_deg,
    'tan': tan_deg,
    'sinh': math.sinh,
    'cosh': math.cosh,
    'tanh': math.tanh,
    'asinh': math.asinh,
    'acosh': math.acosh,
    'atanh': math.atanh,
})

ALLOWED_OPERATORS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}

def safe_eval(expr):
    tree = ast.parse(expr, mode='eval')
    def _eval(node):
        if isinstance(node, ast.Expression): return _eval(node.body)
        if isinstance(node, ast.Constant): return node.value
        if isinstance(node, ast.BinOp):
            return ALLOWED_OPERATORS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            return ALLOWED_OPERATORS[type(node.op)](_eval(node.operand))
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in ALLOWED_NAMES:
                args = [_eval(a) for a in node.args]
                return ALLOWED_NAMES[node.func.id](*args)
            raise ValueError("Invalid function")
        if isinstance(node, ast.Name) and node.id in ALLOWED_NAMES:
            return ALLOWED_NAMES[node.id]
        raise ValueError("Unsupported expression")
    return _eval(tree.body)


# Calculator Class

class AdvancedCalculator:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Advanced Calculator")
        self.window.geometry("720x720")
        self.window.resizable(False, False)
        self.window.configure(bg='#0D0D0D')

        self.current_input = ""
        self.result_var = tk.StringVar(value="0")
        self.process_executor = ProcessPoolExecutor(max_workers=2)
        self.advanced_visible = False

        self.create_display()
        self.create_buttons()
        self.create_advanced_frame()
        self.window.bind('<Key>', self.key_press)
        self.window.focus_set()


    # Display

    def create_display(self):
        display = tk.Entry(
            self.window, font=('Consolas', 30, 'bold'),
            textvariable=self.result_var, justify='right',
            bg='#0A0A0A', fg='#FFFFFF', bd=0, relief='flat',
            insertbackground='#00BFFF'
        )
        display.pack(padx=20, pady=20, fill=tk.X, ipady=15)


    # Main Buttons

    def create_buttons(self):
        self.frame = tk.Frame(self.window, bg='#0D0D0D')
        self.frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        sci_buttons = [
            ['sin', 'cos', 'tan', '√', 'x²'],
            ['log', 'ln', 'x³', 'π', 'e'],
            ['pow', 'mod', '(', ')', '%']
        ]
        basic_buttons = [
            ['C', '±', '÷', '⌫'],
            ['7', '8', '9', '×'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['0', '.', '=', '^', 'More']
        ]

        # create all buttons
        for i, row in enumerate(sci_buttons + basic_buttons):
            for j, text in enumerate(row):
                self.create_button(self.frame, text, i, j)


    # Button creation with color

    def create_button(self, parent, text, row, col):
        if text in ['+', '-', '×', '÷', '=', '^', 'pow']:
            bg, fg, hover = '#00509E', 'white', '#00BFFF'
        elif text in ['sin', 'cos', 'tan', '√', 'x²', 'x³', 'log', 'ln', 'π', 'e', 'mod']:
            bg, fg, hover = '#003F5C', 'white', '#0077B6'
        elif text in ['C', '⌫', '±']:
            bg, fg, hover = '#002F4B', 'white', '#00509E'
        elif text == 'More':
            bg, fg, hover = '#004080', 'white', '#00BFFF'
        else:
            bg, fg, hover = '#0A0A0A', '#FFFFFF', '#00509E'

        btn = tk.Button(
            parent, text=text, font=('Consolas', 16, 'bold'),
            bg=bg, fg=fg, bd=0, relief='flat',
            activebackground=hover, activeforeground='white',
            command=lambda t=text: self.on_button_click(t)
        )
        btn.grid(row=row, column=col, sticky='nsew', padx=3, pady=3)
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)


    # Advanced frame (side by More)

    def create_advanced_frame(self):
        self.adv_frame = tk.Frame(self.frame, bg='#0D0D0D')
        adv_buttons = [
            ['sinh', 'cosh', 'tanh', 'asinh', 'acosh', 'atanh']
        ]
        for i, row in enumerate(adv_buttons):
            for j, text in enumerate(row):
                self.create_adv_button(self.adv_frame, text, i, j)

    def create_adv_button(self, parent, text, row, col):
        btn = tk.Button(
            parent, text=text, font=('Consolas', 14, 'bold'),
            bg='#004080', fg='white', bd=0, relief='flat',
            activebackground='#00BFFF', activeforeground='white',
            command=lambda t=text: self.on_button_click(t)
        )
        btn.grid(row=row, column=col, sticky='nsew', padx=2, pady=2)
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)

    def toggle_advanced(self):
        if self.advanced_visible:
            self.adv_frame.grid_forget()
        else:
            self.adv_frame.grid(row=8, column=0, columnspan=5, sticky='ew', pady=5)
        self.advanced_visible = not self.advanced_visible


    # Logic

    def on_button_click(self, text):
        if text == 'More':
            self.toggle_advanced()
        elif text == 'C':
            self.current_input = ""
            self.result_var.set("0")
        elif text == '⌫':
            self.current_input = self.current_input[:-1]
            self.result_var.set(self.current_input or "0")
        elif text == '=':
            self.evaluate_expression()
        elif text == '±':
            self.toggle_sign()
        elif text == '√':
            self.apply_unary(lambda x: math.sqrt(x))
        elif text == 'x²':
            self.apply_unary(lambda x: x ** 2)
        elif text == 'x³':
            self.apply_unary(lambda x: x ** 3)
        elif text in ['pow', '^']:
            self.current_input += '^'
            self.result_var.set(self.current_input)
        elif text in ['sin', 'cos', 'tan', 'log', 'ln', 'sinh', 'cosh', 'tanh',
                      'asinh', 'acosh', 'atanh']:
            self.wrap_function(text)
        elif text == 'π':
            self.current_input += str(math.pi)
            self.result_var.set(self.current_input)
        elif text == 'e':
            self.current_input += str(math.e)
            self.result_var.set(self.current_input)
        elif text == 'mod':
            self.current_input += '%'
            self.result_var.set(self.current_input)
        else:
            self.current_input += text
            self.result_var.set(self.current_input)

    def toggle_sign(self):
        if self.current_input.startswith('-'):
            self.current_input = self.current_input[1:]
        else:
            self.current_input = '-' + self.current_input
        self.result_var.set(self.current_input)

    def apply_unary(self, func):
        try:
            value = float(self.current_input or self.result_var.get())
            result = func(value)
            self.result_var.set(str(result))
            self.current_input = str(result)
        except:
            self.result_var.set("Error")
            self.current_input = ""

    def wrap_function(self, func_name):
        if self.current_input:
            self.current_input = f"{func_name}({self.current_input})"
        else:
            self.current_input = f"{func_name}("
        self.result_var.set(self.current_input)

    def evaluate_expression(self):
        expression = self.current_input.replace('×', '*').replace('÷', '/').replace('^', '**').replace('%', '/100')
        try:
            result = safe_eval(expression)
            self.result_var.set(str(result))
            self.current_input = str(result)
        except Exception as e:
            logger.exception("Evaluation error")
            self.result_var.set("Error")
            self.current_input = ""

    def key_press(self, event):
        key = event.char
        if key in '0123456789.+-*/()^':
            self.current_input += key
            self.result_var.set(self.current_input)
        elif key == '\r':
            self.evaluate_expression()
        elif key == '\x08':
            self.on_button_click('⌫')
        elif event.keysym == 'Escape':
            self.on_button_click('C')

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    calc = AdvancedCalculator()
    calc.run()
