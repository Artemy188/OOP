import tkinter as tk
from tkinter import ttk, messagebox
import string
from itertools import permutations


class Backend:
    def __init__(self):
        self.letters = list(string.ascii_uppercase)

    def get_adjacency_matrix(self, table, num_vertices):
        matrix = [[0 for _ in range(num_vertices)] for _ in range(num_vertices)]

        for i in range(num_vertices):
            for j in range(num_vertices):
                if i != j and table[i][j] is not None and table[i][j].get() == "*":
                    matrix[i][j] = 1
        return matrix

    def matrices_are_equal(self, mat1, mat2, permutation):
        n = len(mat1)
        for i in range(n):
            for j in range(n):
                if mat1[i][j] != mat2[permutation[i]][permutation[j]]:
                    return False
        return True

    def find_isomorphism(self, digital_table, letter_table, num_vertices):
        digital_matrix = self.get_adjacency_matrix(digital_table, num_vertices)
        letter_matrix = self.get_adjacency_matrix(letter_table, num_vertices)

        found = False
        results = []

        for perm in permutations(range(num_vertices)):
            if self.matrices_are_equal(digital_matrix, letter_matrix, perm):
                found = True
                mapping = {str(i + 1): self.letters[perm[i]] for i in range(num_vertices)}
                results.append(mapping)

        return found, results


class Frontend:
    def __init__(self, root):
        self.root = root
        self.root.title("Сопоставление графов - калькулятор")
        self.root.geometry("900x700")

        self.backend = Backend()
        self.num_vertices = 4

        self.tables_frame = None
        self.digital_frame = None
        self.letter_frame = None
        self.org = tk.BooleanVar(value=True);
        self.create_widgets()
        self.create_tables()

    def create_widgets(self):
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10)

        ttk.Label(control_frame, text="Количество вершин:").grid(row=0, column=0, padx=5)
        self.vertices_var = tk.StringVar(value=str(self.num_vertices))
        vertices_entry = ttk.Entry(control_frame, textvariable=self.vertices_var, width=5)
        vertices_entry.grid(row=0, column=1, padx=5)

        ttk.Button(control_frame, text="Создать таблицы",
                   command=self.update_tables).grid(row=0, column=2, padx=5)
        ttk.Button(control_frame, text="Найти соответствие",
                   command=self.find_isomorphism).grid(row=0, column=3, padx=5)
        ttk.Button(control_frame, text="Очистить",
                   command=self.clear_tables).grid(row=0, column=4, padx=5)
        ttk.Checkbutton(control_frame, text="Неориентированный", variable=self.org
                  ).grid(row=1, column=2, padx=5)

    def clear_old_tables(self):
        if self.tables_frame:
            self.tables_frame.destroy()
            self.tables_frame = None
            self.digital_frame = None
            self.letter_frame = None
            self.org = True;
            self.digital_table = []
            self.letter_table = []

    def create_tables(self):
        self.clear_old_tables()

        self.tables_frame = ttk.Frame(self.root)
        self.tables_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.tables_frame)

        self.v_scrollbar = ttk.Scrollbar(self.tables_frame, orient="vertical", command=self.canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(self.tables_frame, orient="horizontal", command=self.canvas.xview)

        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.tables_frame.grid_rowconfigure(0, weight=1)
        self.tables_frame.grid_columnconfigure(0, weight=1)

        tables_container = ttk.Frame(self.scrollable_frame)
        tables_container.pack(pady=10, fill=tk.BOTH, expand=True)

        self.digital_frame = ttk.LabelFrame(tables_container, text="Граф с цифровыми вершинами")
        self.digital_frame.pack(side="left", padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.letter_frame = ttk.LabelFrame(tables_container, text="Граф с буквенными вершинами")
        self.letter_frame.pack(side="right", padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.digital_table = []
        self.letter_table = []

        self.create_digital_table(self.digital_frame)
        self.create_letter_table(self.letter_frame)

        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)
        self.digital_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.digital_frame.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)
        self.letter_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.letter_frame.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_shift_mousewheel(self, event):
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_digital_table(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        self.digital_table = []
        n = self.num_vertices

        table_frame = ttk.Frame(parent)
        table_frame.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        for j in range(n + 1):
            if j == 0:
                label = ttk.Label(table_frame, text="", width=4)
                label.grid(row=0, column=j, padx=1, pady=1)
            else:
                label = ttk.Label(table_frame, text=str(j), width=4, anchor="center")
                label.grid(row=0, column=j, padx=1, pady=1)

        for i in range(1, n + 1):
            label = ttk.Label(table_frame, text=str(i), width=4, anchor="center")
            label.grid(row=i, column=0, padx=1, pady=1)

            row = []
            for j in range(1, n + 1):
                if i == j:
                    label = ttk.Label(table_frame, text="×", width=4, background="lightgray", anchor="center")
                    label.grid(row=i, column=j, padx=1, pady=1)
                    row.append(None)
                else:
                    var = tk.StringVar(value="")
                    label = ttk.Label(table_frame, textvariable=var, width=4,
                                      relief="solid", background="white", anchor="center")
                    label.grid(row=i, column=j, padx=1, pady=1)
                    label.bind("<Button-1>", lambda e, row_idx=i - 1, col_idx=j - 1:
                    self.toggle_digital_cell(row_idx, col_idx))
                    row.append(var)
            self.digital_table.append(row)

    def create_letter_table(self, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        self.letter_table = []
        n = self.num_vertices

        table_frame = ttk.Frame(parent)
        table_frame.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        for j in range(n + 1):
            if j == 0:
                label = ttk.Label(table_frame, text="", width=4)
                label.grid(row=0, column=j, padx=1, pady=1)
            else:
                label = ttk.Label(table_frame, text=self.backend.letters[j - 1], width=4, anchor="center")
                label.grid(row=0, column=j, padx=1, pady=1)

        for i in range(1, n + 1):
            label = ttk.Label(table_frame, text=self.backend.letters[i - 1], width=4, anchor="center")
            label.grid(row=i, column=0, padx=1, pady=1)

            row = []
            for j in range(1, n + 1):
                if i == j:
                    label = ttk.Label(table_frame, text="×", width=4, background="lightgray", anchor="center")
                    label.grid(row=i, column=j, padx=1, pady=1)
                    row.append(None)
                else:
                    var = tk.StringVar(value="")
                    label = ttk.Label(table_frame, textvariable=var, width=4,
                                      relief="solid", background="white", anchor="center")
                    label.grid(row=i, column=j, padx=1, pady=1)
                    label.bind("<Button-1>", lambda e, row_idx=i - 1, col_idx=j - 1:
                    self.toggle_letter_cell(row_idx, col_idx))
                    row.append(var)
            self.letter_table.append(row)

    def toggle_digital_cell(self, row, col):
        if row != col:
            current = self.digital_table[row][col].get()
            if current == "":
                self.digital_table[row][col].set("*")
                if self.org.get():
                    self.digital_table[col][row].set("*")
            else:
                self.digital_table[row][col].set("")
                if self.org.get():
                    self.digital_table[col][row].set("")

    def toggle_letter_cell(self, row, col):
        if row != col:
            current = self.letter_table[row][col].get()
            if current == "":
                self.letter_table[row][col].set("*")
                if self.org.get():
                    self.letter_table[col][row].set("*")
            else:
                self.letter_table[row][col].set("")
                if self.org.get():
                    self.letter_table[col][row].set("")

    def update_tables(self):
        try:
            new_num = int(self.vertices_var.get())
            if new_num < 2 or new_num > 20:
                messagebox.showerror("Ошибка", "Количество вершин должно быть от 2 до 20")
                return
            self.num_vertices = new_num
            self.create_tables()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число")

    def clear_tables(self):
        for i in range(self.num_vertices):
            for j in range(self.num_vertices):
                if i != j and self.digital_table[i][j] is not None:
                    self.digital_table[i][j].set("")
                if i != j and self.letter_table[i][j] is not None:
                    self.letter_table[i][j].set("")

    def find_isomorphism(self):
        found, results = self.backend.find_isomorphism(self.digital_table, self.letter_table, self.num_vertices)

        if found:
            result_text = "Найдены соответствия:\n\n"
            for i, mapping in enumerate(results, 1):
                result_text += f"Вариант {i}:\n"
                for digital, letter in sorted(mapping.items()):
                    result_text += f"  {digital} → {letter}\n"
                result_text += "\n"

            result_window = tk.Toplevel(self.root)
            result_window.title("Результаты сопоставления")
            result_window.geometry("300x400")

            result_frame = ttk.Frame(result_window)
            result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            text_scrollbar = ttk.Scrollbar(result_frame)
            text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            text_widget = tk.Text(result_frame, wrap=tk.WORD, yscrollcommand=text_scrollbar.set)
            text_widget.insert(tk.END, result_text)
            text_widget.config(state=tk.DISABLED)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            text_scrollbar.config(command=text_widget.yview)

            ttk.Button(result_window, text="Закрыть",
                       command=result_window.destroy).pack(pady=5)
        else:
            messagebox.showinfo("Результат", "Соответствие не найдено")


def main():
    root = tk.Tk()
    app = Frontend(root)
    root.mainloop()


if __name__ == "__main__":
    main()