import tkinter as tk
from tkinter import filedialog as fd
from tkinter import colorchooser as cc

canvas_width = 1024
canvas_height = 576
cell_size = 4  # ขนาดช่องตาราง
zoom_factor = 1.0
base_cell_size = 4
initial_rows = canvas_height // base_cell_size
initial_cols = canvas_width // base_cell_size

points = {}  # เก็บสีของแต่ละช่อง {(row, col): (rect_id, color)}

paint_color = "#11ff00"
button_font = ("Helvetica", 11)

master = tk.Tk()
master.title("Drawing App with Grid")

# สร้าง frame ครอบ canvas กับ scrollbar
canvas_frame = tk.Frame(master)
canvas_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(canvas_frame, width=canvas_width, height=canvas_height, bg="white")
canvas.grid(row=0, column=0, sticky="nsew")

# สร้าง scrollbar แนวตั้ง
v_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
v_scrollbar.grid(row=0, column=1, sticky="ns")

# สร้าง scrollbar แนวนอน
h_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)
h_scrollbar.grid(row=1, column=0, sticky="ew")

# เชื่อม scrollbar กับ canvas
canvas.config(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

# กำหนดขนาด scrollable area (scrollregion)
canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))

# ปรับ grid config ให้ canvas_frame ขยายได้
canvas_frame.grid_rowconfigure(0, weight=1)
canvas_frame.grid_columnconfigure(0, weight=1)

def draw_grid():
    rows = canvas_height // cell_size
    cols = canvas_width // cell_size
    center_x = canvas_width // 2
    center_y = canvas_height // 2

    for col in range(cols + 1):
        x = col * cell_size
        if x == center_x:
            canvas.create_line(x, 0, x, canvas_height, fill="blue")
        elif col % 8 == 0:
            canvas.create_line(x, 0, x, canvas_height, fill="red")
        else:
            canvas.create_line(x, 0, x, canvas_height, fill="gray")

    for row in range(rows + 1):
        y = row * cell_size
        if y == center_y:
            canvas.create_line(0, y, canvas_width, y, fill="blue")
        elif row % 8 == 0:
            canvas.create_line(0, y, canvas_width, y, fill="red")
        else:
            canvas.create_line(0, y, canvas_width, y, fill="gray")  

draw_grid()

# ฟังก์ชันวาดสีในช่องตาราง
def paint(event):
    # ปรับพิกัดตาม scroll offset
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    col = int(x // cell_size)
    row = int(y // cell_size)
    if 0 <= col < canvas_width // cell_size and 0 <= row < canvas_height // cell_size:
        if (row, col) in points:
            rect_id, _ = points[(row, col)]
            canvas.itemconfig(rect_id, fill=paint_color)
            points[(row, col)] = (rect_id, paint_color)
        else:
            x1 = col * cell_size
            y1 = row * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            rect_id = canvas.create_rectangle(x1, y1, x2, y2, fill=paint_color, outline="")
            points[(row, col)] = (rect_id, paint_color)

def save_drawing():
    file_path = fd.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )
    if file_path:
        with open(file_path, "w") as f:
            for (row, col), (id, color) in points.items():
                f.write(f"{row},{col},{id},{color}\n")

def clear_canvas():
    canvas.delete("all")
    points.clear()
    draw_grid()

def load_drawing():
    file_path = fd.askopenfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All Files", "*.*")],
    )
    if file_path:
        clear_canvas()
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row, col, id, color = line.split(",")
                row, col = int(row), int(col)
                x1 = col * cell_size
                y1 = row * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                points[(row, col)] = (id, color)

def choose_color():
    global paint_color
    color_code = cc.askcolor(title="เลือกสี")
    if color_code[1] is not None:
        paint_color = color_code[1]
        color_display.config(bg=paint_color)

def erase(event):
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    col = int(x // cell_size)
    row = int(y // cell_size)
    if (row, col) in points:
        rect_id, _ = points[(row, col)]
        canvas.delete(rect_id)
        del points[(row, col)]

def update_canvas_and_cellsize(zoom_factor):
    global canvas_width, canvas_height, cell_size
    cell_size = int(base_cell_size * zoom_factor)
    if cell_size < 1:
        cell_size = 1
    canvas_width = initial_cols * cell_size
    canvas_height = initial_rows * cell_size
    canvas.config(width=canvas_width, height=canvas_height)
    return cell_size, canvas_width, canvas_height

def redraw_all():
    canvas.delete("all")
    draw_grid()
    for (row, col), (rect_id, color) in points.items():
        x1 = col * cell_size
        y1 = row * cell_size
        x2 = x1 + cell_size
        y2 = y1 + cell_size
        new_rect_id = canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
        points[(row, col)] = (new_rect_id, color)

def zoom(event):
    global zoom_factor, cell_size
    if event.delta > 0:
        zoom_factor *= 1.1
    elif event.delta < 0:
        zoom_factor /= 1.1
    zoom_factor = max(0.2, min(zoom_factor, 5))
    update_canvas_and_cellsize(zoom_factor)
    redraw_all()

message = tk.Label(master, text="คลิ๊กซ้ายลงสี, คลิ๊กขวาลบสี", font=("Helvetica", 11))
message.pack()

frame = tk.Frame(master)
frame.pack(padx=40, pady=2)

save_button = tk.Button(frame, text="บันทึกภาพวาด", command=save_drawing, font=button_font)
save_button.pack(side=tk.LEFT, padx=20)

load_button = tk.Button(frame, text="เปิดภาพวาด", command=load_drawing, font=button_font)
load_button.pack(side=tk.LEFT, padx=20)

clear_button = tk.Button(frame, text="ล้างภาพวาด", command=clear_canvas, font=button_font)
clear_button.pack(side=tk.LEFT, padx=20)

color_button = tk.Button(frame, text="เลือกสี", command=choose_color, font=button_font)
color_button.pack(side=tk.LEFT, padx=20)

color_display = tk.Label(frame, bg=paint_color, width=2)
color_display.pack(side=tk.LEFT, padx=2)

canvas.bind("<Button-1>", paint)
canvas.bind("<Button-3>", erase)
canvas.bind("<MouseWheel>", zoom)

master.mainloop()