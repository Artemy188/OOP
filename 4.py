import tkinter as tk
from tkinter import ttk, messagebox
from itertools import permutations, product

def binr(a):
    ans = ''
    while a != 0:
        ans += str(a % 2)
        a //= 2
    return ans[::-1]

class LogicExpressionVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор логических выражений")
        self.root.geometry("900x800")

        self.expression_var = tk.StringVar()
        self.result_var = tk.StringVar(value="1")
        self.current_order = ['x', 'y', 'z', 'w']

        self.create_widgets()
        self.create_partial_table()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        title_label = ttk.Label(
            main_frame,
            text="Калькулятор логических выражений",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        ttk.Label(main_frame, text="Логическое выражение:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )

        expression_entry = ttk.Entry(
            main_frame, textvariable=self.expression_var, width=50
        )
        expression_entry.grid(
            row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0)
        )

        ttk.Label(main_frame, text="Показать строки, где результат:").grid(
            row=4, column=0, sticky=tk.W, pady=5
        )

        result_frame = ttk.Frame(main_frame)
        result_frame.grid(row=4, column=1, sticky=tk.W, pady=5)

        ttk.Radiobutton(
            result_frame, text="Истина (1)", variable=self.result_var,
            value="1", command=self.evaluate_expression
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            result_frame, text="Ложь (0)", variable=self.result_var,
            value="0", command=self.evaluate_expression
        ).pack(side=tk.LEFT, padx=(20, 0))
        ttk.Radiobutton(
            result_frame, text="Все", variable=self.result_var,
            value="2", command=self.evaluate_expression
        ).pack(side=tk.LEFT, padx=(20, 0))

        ttk.Button(
            main_frame, text="Вычислить", command=self.evaluate_expression
        ).grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Label(
            main_frame, text="Таблица истинности (порядок: xyzw):",
            font=("Arial", 10, "bold")
        ).grid(row=6, column=0, columnspan=3, sticky=tk.W, pady=(20, 10))

        columns = ("col1", "col2", "col3", "col4", "result")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=12)

        self.tree.heading("col1", text="X")
        self.tree.heading("col2", text="Y")
        self.tree.heading("col3", text="Z")
        self.tree.heading("col4", text="W")
        self.tree.heading("result", text="Результат")

        self.tree.column("col1", width=80, anchor=tk.CENTER)
        self.tree.column("col2", width=80, anchor=tk.CENTER)
        self.tree.column("col3", width=80, anchor=tk.CENTER)
        self.tree.column("col4", width=80, anchor=tk.CENTER)
        self.tree.column("result", width=120, anchor=tk.CENTER)

        self.tree.grid(
            row=7, column=0, columnspan=3,
            sticky=(tk.W, tk.E, tk.N, tk.S), pady=5
        )

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=7, column=3, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)

        main_frame.rowconfigure(7, weight=1)

    def create_partial_table(self):
        main_frame = self.root.grid_slaves(row=0, column=0)[0]

        ttk.Label(
            main_frame, text="Частичная таблица истинности (порядок неизвестен):",
            font=("Arial", 10, "bold")
        ).grid(row=8, column=0, columnspan=5, sticky=tk.W, pady=(20, 10))

        self.partial_table_frame = ttk.Frame(main_frame)
        self.partial_table_frame.grid(row=9, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=5)

        columns = ["?", "?", "?", "?", "res"]
        for col, text in enumerate(columns):
            label = ttk.Label(self.partial_table_frame, text=text, width=8, anchor=tk.CENTER)
            label.grid(row=0, column=col, padx=2, pady=2)

        self.partial_buttons = []
        for row in range(3):
            row_buttons = []
            for col in range(5):
                btn = tk.Button(
                    self.partial_table_frame, text="", width=8, height=1,
                    command=lambda r=row, c=col: self.toggle_partial_cell(r, c)
                )
                btn.grid(row=row + 1, column=col, padx=2, pady=2)
                row_buttons.append(btn)
            self.partial_buttons.append(row_buttons)

        ttk.Button(
            main_frame, text="Определить порядок переменных",
            command=self.determine_variable_order
        ).grid(row=10, column=0, columnspan=2, pady=10)

        self.order_var = tk.StringVar(value="Порядок переменных: неизвестен")
        order_label = ttk.Label(main_frame, textvariable=self.order_var, font=("Arial", 10))
        order_label.grid(row=10, column=2, columnspan=3, sticky=tk.W, pady=10)

    def toggle_partial_cell(self, row, col):
        btn = self.partial_buttons[row][col]
        current_text = btn.cget("text")

        if current_text == "":
            btn.config(text="0")
        elif current_text == "0":
            btn.config(text="1")
        else:
            btn.config(text="")

    def get_partial_table_data(self):
        data = []
        for row in range(3):
            row_data = []
            for col in range(5):
                value = self.partial_buttons[row][col].cget("text")
                if value == "":
                    row_data.append(None)
                else:
                    row_data.append(int(value))
            data.append(row_data)
        return data

    def check_row_with_partial_data(self, expression, order, data):
        t = []
        for a in range(16):
            a1 = binr(a)
            while len(a1) < 4:
                a1 = "0" + a1
            for b in range(16):
                b1 = binr(b)
                while len(b1) < 4:
                    b1 = "0" + b1
                for c in range(16):
                    t = []
                    c1 = binr(c)
                    while len(c1) < 4:
                        c1 = "0" + c1
                    curr = []
                    for i in range(4):
                        if data[0][1][i] is None:
                            curr.append(int(a1[i]))
                        else:
                            curr.append(data[0][1][i])
                    t.append(tuple(curr))
                    curr = []
                    for i in range(4):
                        if data[1][1][i] is None:
                            curr.append(int(b1[i]))
                        else:
                            curr.append(data[1][1][i])
                    t.append(tuple(curr))
                    curr = []
                    for i in range(4):
                        if data[2][1][i] is None:
                            curr.append(int(c1[i]))
                        else:
                            curr.append(data[2][1][i])
                    t.append(tuple(curr))
                    mark = True
                    if len(set(t)) == len(t):
                        for j in range(3):
                            if  self.safe_eval_with_dict(expression, dict(zip(order, t[j]))) != bool(data[j][1][4]):
                                mark = False
                                break
                        if mark:
                            return True
        return False


    def determine_variable_order(self):
        expression = self.expression_var.get().strip()
        if not expression:
            messagebox.showwarning("Ошибка", "Введите логическое выражение")
            return

        partial_data = self.get_partial_table_data()

        constraints = []
        for row_idx, row in enumerate(partial_data):
            if any(cell is not None for cell in row):
                constraints.append((row_idx, row))

        if not constraints:
            messagebox.showwarning("Ошибка", "Заполните хотя бы одну ячейку в частичной таблице")
            return

        variables = ['x', 'y', 'z', 'w']
        possible_orders = []
        used = []
        for order in permutations(variables):
            valid = True

            if not self.check_row_with_partial_data(expression, order, constraints):
                valid = False

            if valid:
                possible_orders.append(order)

        if possible_orders:
            best_order = possible_orders[0]
            self.current_order = best_order
            self.order_var.set(f"Порядок переменных: {''.join(best_order)}")

            if len(possible_orders) > 1:
                orders_text = ", ".join([''.join(order) for order in possible_orders])
                messagebox.showinfo("Информация",
                                    f"Найдено {len(possible_orders)} возможных порядков: {orders_text}")
        else:
            self.order_var.set("Порядок переменных: не найден")

    def safe_eval_with_dict(self, expression, eval_dict):
        try:
            expr = expression.lower()
            expr = expr.replace('and', ' and ')
            expr = expr.replace('or', ' or ')
            expr = expr.replace('not', ' not ')
            expr = expr.replace('xor', ' ^ ')

            for var, value in eval_dict.items():
                expr = expr.replace(var, str(value))

            result = eval(expr)
            return bool(result)
        except Exception as e:
            raise ValueError(f"Ошибка в выражении: {e}")

    def safe_eval(self, expression, x, y, z, w):
        try:
            expr = expression.lower()
            expr = expr.replace('and', ' and ')
            expr = expr.replace('or', ' or ')
            expr = expr.replace('not', ' not ')
            expr = expr.replace('xor', ' ^ ')

            expr = expr.replace('x', str(x))
            expr = expr.replace('y', str(y))
            expr = expr.replace('z', str(z))
            expr = expr.replace('w', str(w))

            result = eval(expr)
            return bool(result)
        except Exception as e:
            raise ValueError(f"Ошибка в выражении: {e}")

    def evaluate_expression(self):
        expression = self.expression_var.get().strip()

        if not expression:
            messagebox.showwarning("Ошибка", "Введите логическое выражение")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            if self.result_var.get() == "2":
                target_result = 2
            else:
                target_result = self.result_var.get() == "1"
            found_count = 0

            for x in [False, True]:
                for y in [False, True]:
                    for z in [False, True]:
                        for w in [False, True]:
                            result = self.safe_eval(expression, x, y, z, w)

                            if result == target_result or target_result == 2:
                                found_count += 1
                                self.tree.insert("", tk.END, values=(
                                    "1" if x else "0",
                                    "1" if y else "0",
                                    "1" if z else "0",
                                    "1" if w else "0",
                                    "Истина" if result else "Ложь"
                                ))

            if found_count == 0:
                messagebox.showinfo("Результат", "Нет комбинаций")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception:
            messagebox.showerror("Ошибка", "Неизвестная ошибка")


def main():
    root = tk.Tk()
    app = LogicExpressionVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
