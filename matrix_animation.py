import tkinter as tk
from tkinter import ttk
import tensorflow as tf
import threading
import queue
import time

ROWS = 100
COLS = 100
THREAD_COUNT = 4

matrix_a = tf.random.uniform(
    [ROWS, COLS], minval=1, maxval=10, dtype=tf.float32
)

matrix_b = tf.random.uniform(
    [ROWS, COLS], minval=1, maxval=10, dtype=tf.float32
)

matrix_c = tf.Variable(tf.zeros([ROWS, COLS], dtype=tf.float32))

updates = queue.Queue()

completed = 0
finished = 0
is_running = False
begin_time = 0

def calculate_part(number, first, last):
    """Calculate the rows assigned to one thread."""

    for r in range(first, last):
        row_result = tf.linalg.matvec(
            tf.transpose(matrix_b),
            matrix_a[r]
        )

        updates.put(("row", number, r, row_result.numpy()))
        time.sleep(0.025)

    updates.put(("done", number))

class MatrixWindow:

    def __init__(self, window):
        self.window = window

        self.window.title("Threaded Matrix Calculator")
        self.window.geometry("980x720")
        self.window.configure(bg="#eef2f7")
        self.window.resizable(False, False)

        self.thread_text = []
        self.thread_progress = []

        self.build_header()
        self.build_controls()
        self.build_matrices()
        self.build_thread_area()
        self.build_footer()

        self.show_input(matrix_a, self.canvas_a)
        self.show_input(matrix_b, self.canvas_b)
        self.show_result()

    def build_header(self):
        heading = tk.Label(
            self.window,
            text="100 × 100 MATRIX MULTIPLICATION",
            font=("Arial", 20, "bold"),
            bg="#eef2f7",
            fg="#1f2937"
        )
        heading.pack(pady=(16, 2))

        info = tk.Label(
            self.window,
            text="Four worker threads • TensorFlow • Row based processing",
            font=("Arial", 10),
            bg="#eef2f7",
            fg="#64748b"
        )
        info.pack()

    def build_controls(self):
        area = tk.Frame(self.window, bg="#eef2f7")
        area.pack(pady=12)

        self.start_button = tk.Button(
            area,
            text="START",
            command=self.start,
            width=12,
            font=("Arial", 10, "bold"),
            bg="#2563eb",
            fg="white",
            relief="flat",
            padx=8,
            pady=5
        )
        self.start_button.grid(row=0, column=0, padx=5)

        reset_button = tk.Button(
            area,
            text="CLEAR",
            command=self.clear,
            width=12,
            font=("Arial", 10, "bold"),
            bg="#475569",
            fg="white",
            relief="flat",
            padx=8,
            pady=5
        )
        reset_button.grid(row=0, column=1, padx=5)

        self.main_status = tk.Label(
            area,
            text="Waiting for start",
            font=("Arial", 10, "bold"),
            bg="#eef2f7",
            fg="#334155"
        )
        self.main_status.grid(row=0, column=2, padx=20)

    def matrix_box(self, parent, title):
        box = tk.Frame(
            parent,
            bg="white",
            bd=1,
            relief="solid",
            padx=8,
            pady=7
        )

        tk.Label(
            box,
            text=title,
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#334155"
        ).pack()

        canvas = tk.Canvas(
            box,
            width=175,
            height=175,
            bg="#f8fafc",
            highlightthickness=0
        )
        canvas.pack(pady=(5, 0))

        return box, canvas

    def build_matrices(self):
        top = tk.Frame(self.window, bg="#eef2f7")
        top.pack()

        left, self.canvas_a = self.matrix_box(top, "MATRIX A  (100 × 100)")
        left.grid(row=0, column=0, padx=18)

        tk.Label(
            top,
            text="×",
            font=("Arial", 24, "bold"),
            bg="#eef2f7",
            fg="#64748b"
        ).grid(row=0, column=1, padx=3)

        right, self.canvas_b = self.matrix_box(top, "MATRIX B  (100 × 100)")
        right.grid(row=0, column=2, padx=18)

        tk.Label(
            self.window,
            text="RESULT C",
            font=("Arial", 11, "bold"),
            bg="#eef2f7",
            fg="#334155"
        ).pack(pady=(9, 3))

        self.result_canvas = tk.Canvas(
            self.window,
            width=470,
            height=85,
            bg="#f8fafc",
            highlightthickness=1,
            highlightbackground="#cbd5e1"
        )
        self.result_canvas.pack()

    def show_input(self, matrix, canvas):
        canvas.delete("all")

        values = matrix.numpy()
        cells = 14
        size = 175 / cells

        for y in range(cells):
            for x in range(cells):
                value = values[y * 7, x * 7]
                level = int(245 - (value / 10) * 140)
                level = max(80, min(245, level))

                fill = f"#{level:02x}{level:02x}ff"

                canvas.create_rectangle(
                    x * size,
                    y * size,
                    (x + 1) * size,
                    (y + 1) * size,
                    fill=fill,
                    outline="white"
                )

    def show_result(self):
        self.result_canvas.delete("all")

        values = matrix_c.numpy()
        rows = 20
        cols = 20

        cell_w = 470 / cols
        cell_h = 85 / rows

        for y in range(rows):
            for x in range(cols):
                value = values[y * 5, x * 5]

                if value == 0:
                    fill = "#e2e8f0"
                else:
                    level = int(250 - min(float(value) / 10000, 1) * 180)
                    level = max(70, level)
                    fill = f"#{level:02x}ff{level:02x}"

                self.result_canvas.create_rectangle(
                    x * cell_w,
                    y * cell_h,
                    (x + 1) * cell_w,
                    (y + 1) * cell_h,
                    fill=fill,
                    outline="white"
                )

    def build_thread_area(self):
        tk.Label(
            self.window,
            text="THREAD WORK AREA",
            font=("Arial", 11, "bold"),
            bg="#eef2f7",
            fg="#334155"
        ).pack(pady=(8, 4))

        holder = tk.Frame(self.window, bg="#eef2f7")
        holder.pack()

        ranges = [
            (0, 25),
            (25, 50),
            (50, 75),
            (75, 100)
        ]

        for i, (start, end) in enumerate(ranges):
            card = tk.Frame(
                holder,
                bg="white",
                bd=1,
                relief="solid",
                padx=7,
                pady=5
            )
            card.grid(row=0, column=i, padx=6)

            tk.Label(
                card,
                text=f"THREAD {i + 1}",
                font=("Arial", 9, "bold"),
                bg="white",
                fg="#334155"
            ).pack()

            tk.Label(
                card,
                text=f"Rows {start} to {end - 1}",
                font=("Arial", 8),
                bg="white",
                fg="#64748b"
            ).pack()

            bar = ttk.Progressbar(
                card,
                length=125,
                maximum=25,
                mode="determinate"
            )
            bar.pack(pady=4)

            state = tk.Label(
                card,
                text="READY",
                font=("Arial", 8, "bold"),
                bg="white",
                fg="#64748b"
            )
            state.pack()

            self.thread_progress.append(bar)
            self.thread_text.append(state)

    def build_footer(self):
        self.total_bar = ttk.Progressbar(
            self.window,
            length=520,
            maximum=100,
            mode="determinate"
        )
        self.total_bar.pack(pady=(10, 2))

        self.percent = tk.Label(
            self.window,
            text="0%",
            font=("Arial", 9, "bold"),
            bg="#eef2f7",
            fg="#334155"
        )
        self.percent.pack()

        self.time_text = tk.Label(
            self.window,
            text="",
            font=("Arial", 9),
            bg="#eef2f7",
            fg="#64748b"
        )
        self.time_text.pack(pady=(1, 4))
    def start(self):
        global completed, finished, is_running, begin_time

        if is_running:
            return

        completed = 0
        finished = 0
        is_running = True
        begin_time = time.time()

        matrix_c.assign(tf.zeros([ROWS, COLS], dtype=tf.float32))
        self.show_result()

        self.total_bar["value"] = 0
        self.percent.config(text="0%")
        self.time_text.config(text="")
        self.main_status.config(
            text="Threads are calculating...",
            fg="#d97706"
        )
        self.start_button.config(state="disabled")

        for bar, label in zip(self.thread_progress, self.thread_text):
            bar["value"] = 0
            label.config(text="RUNNING", fg="#d97706")

        rows_each = ROWS // THREAD_COUNT

        for n in range(THREAD_COUNT):
            first = n * rows_each
            last = first + rows_each

            worker = threading.Thread(
                target=calculate_part,
                args=(n, first, last)
            )
            worker.daemon = True
            worker.start()

        self.window.after(40, self.read_updates)

    def read_updates(self):
        global completed, finished, is_running

        while not updates.empty():
            data = updates.get()

            if data[0] == "row":
                number, row_number, row_values = data[1], data[2], data[3]

                matrix_c[row_number].assign(row_values)
                completed += 1

                thread_done = completed_rows_for_thread(number, row_number)
                self.thread_progress[number - 1]["value"] = thread_done

                percent = completed
                self.total_bar["value"] = percent
                self.percent.config(text=f"{percent}%")

                self.main_status.config(
                    text=f"Thread {number} completed row {row_number}"
                )

                self.show_result()

            elif data[0] == "done":
                number = data[1]
                finished += 1

                self.thread_progress[number - 1]["value"] = 25
                self.thread_text[number - 1].config(
                    text="FINISHED",
                    fg="#16a34a"
                )

        if finished == THREAD_COUNT:
            is_running = False
            elapsed = time.time() - begin_time

            self.total_bar["value"] = 100
            self.percent.config(text="100%")
            self.main_status.config(
                text="Multiplication completed",
                fg="#15803d"
            )
            self.time_text.config(
                text=f"Execution time: {elapsed:.2f} seconds"
            )
            self.start_button.config(state="normal")

            print("\n------------------------------")
            print("Matrix multiplication completed")
            print("Matrix A :", matrix_a.shape)
            print("Matrix B :", matrix_b.shape)
            print("Matrix C :", matrix_c.shape)
            print("Threads  :", THREAD_COUNT)
            print(f"Time     : {elapsed:.2f} seconds")
            print("------------------------------")

            return

        if is_running:
            self.window.after(40, self.read_updates)


    def clear(self):
        global completed, finished, is_running

        if is_running:
            return

        completed = 0
        finished = 0

        matrix_c.assign(tf.zeros([ROWS, COLS], dtype=tf.float32))
        self.show_result()

        self.total_bar["value"] = 0
        self.percent.config(text="0%")
        self.time_text.config(text="")
        self.main_status.config(
            text="Waiting for start",
            fg="#334155"
        )

        for bar, label in zip(self.thread_progress, self.thread_text):
            bar["value"] = 0
            label.config(text="READY", fg="#64748b")


def completed_rows_for_thread(thread_number, row_number):
    """Return progress from 0 to 25 for a particular thread."""
    first_row = (thread_number - 1) * 25
    return row_number - first_row + 1

window = tk.Tk()
app = MatrixWindow(window)
window.mainloop()
