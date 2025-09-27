import tkinter as tk
from tkinter import ttk, messagebox


class LogicExpressionVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор логических выражений")
        self.root.geometry("900x700")


        self.expression_var = tk.StringVar()
        self.result_var = tk.StringVar(value="1")


        self.create_widgets()

    def create_widgets(self):

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))


        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)


        title_label = ttk.Label(main_frame, text="Визуализатор логических выражений",
                                font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))


        ttk.Label(main_frame, text="Логическое выражение:").grid(row=1, column=0, sticky=tk.W, pady=5)

        expression_entry = ttk.Entry(main_frame, textvariable=self.expression_var, width=50)
        expression_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))


        ttk.Label(main_frame, text="Показать строки, где результат:").grid(row=4, column=0, sticky=tk.W, pady=5)

        result_frame = ttk.Frame(main_frame)
        result_frame.grid(row=4, column=1, sticky=tk.W, pady=5)

        ttk.Radiobutton(result_frame, text="Истина (1)", variable=self.result_var,
                        value="1", command=self.evaluate_expression).pack(side=tk.LEFT)
        ttk.Radiobutton(result_frame, text="Ложь (0)", variable=self.result_var,
                        value="0", command=self.evaluate_expression).pack(side=tk.LEFT, padx=(20, 0))
        ttk.Radiobutton(result_frame, text="Все", variable=self.result_var,
                        value="2", command=self.evaluate_expression).pack(side=tk.LEFT, padx=(20, 0))


        ttk.Button(main_frame, text="Вычислить", command=self.evaluate_expression).grid(row=5, column=0, columnspan=2,
                                                                                        pady=10)


        ttk.Label(main_frame, text="Таблица истинности:", font=("Arial", 10, "bold")).grid(row=6, column=0,
                                                                                           columnspan=3, sticky=tk.W,
                                                                                           pady=(20, 10))


        columns = ("x", "y", "z", "w", "result")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=12)

        self.tree.heading("x", text="X")
        self.tree.heading("y", text="Y")
        self.tree.heading("z", text="Z")
        self.tree.heading("w", text="W")
        self.tree.heading("result", text="Результат")

        self.tree.column("x", width=80, anchor=tk.CENTER)
        self.tree.column("y", width=80, anchor=tk.CENTER)
        self.tree.column("z", width=80, anchor=tk.CENTER)
        self.tree.column("w", width=80, anchor=tk.CENTER)
        self.tree.column("result", width=120, anchor=tk.CENTER)

        self.tree.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)


        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=7, column=3, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)





        main_frame.rowconfigure(7, weight=1)

    def safe_eval(self, expression, x, y, z, w):

        try:

            expression = expression.lower()
            expression = expression.replace('and', ' and ')
            expression = expression.replace('or', ' or ')
            expression = expression.replace('not', ' not ')
            expression = expression.replace('xor', ' ^ ')


            expression = expression.replace('x', str(x))
            expression = expression.replace('y', str(y))
            expression = expression.replace('z', str(z))
            expression = expression.replace('w', str(w))


            result = eval(expression)
            return bool(result)
        except Exception as e:
            raise ValueError(f"Ошибка в выражении: {e}")

    def evaluate_expression(self):

        expression = self.expression_var.get().strip()

        if not expression:
            messagebox.showwarning("Введите логическое выражение")
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


            result_text = "истина" if target_result else "ложь"


            if found_count == 0:
                messagebox.showinfo("Нет комбинаций")
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

        except Exception as e:
            messagebox.showerror("Ошибка")
def main():
    root = tk.Tk()
    app = LogicExpressionVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()