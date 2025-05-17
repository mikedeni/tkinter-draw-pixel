import tkinter as tk
from tkinter import filedialog as fd
from tkinter import colorchooser as cc

canvas_width = 1024
canvas_height = 576
cell_size = 4  # ขนาดช่องตาราง
zoom_factor = 1.0
base_cell_size = 4

points = {}  # เก็บสีของแต่ละช่อง {(row, col): color}

paint_color = "#11ff00"
button_font = ("Helvetica", 11)

master = tk.Tk()
master.title("Drawing App with Grid")

canvas = tk.Canvas(master, width=canvas_width, height=canvas_height, bg="white")
canvas.pack()

def draw_crosshair():
    center_x = canvas_width // 2
    center_y = canvas_height // 2
    # วาดเส้นแนวตั้งตรงกลาง
    canvas.create_line(center_x, 0, center_x, canvas_height, fill="red", width=2)
    # วาดเส้นแนวนอนตรงกลาง
    canvas.create_line(0, center_y, canvas_width, center_y, fill="blue", width=2)

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
    col = event.x // cell_size
    row = event.y // cell_size
    if 0 <= col < canvas_width // cell_size and 0 <= row < canvas_height // cell_size:
        x1 = col * cell_size
        y1 = row * cell_size
        x2 = x1 + cell_size
        y2 = y1 + cell_size

        # วาดสี่เหลี่ยมสีในช่องนั้น (ลบสีเก่า)
        rect_id = canvas.create_rectangle(x1, y1, x2, y2, fill=paint_color, outline="")
        points[(row, col)] = (rect_id, paint_color) # id color

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
                canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")
                points[(row, col)] = (id, color)

def choose_color():
    global paint_color
    color_code = cc.askcolor(title="เลือกสี")
    if color_code[1] is not None:
        paint_color = color_code[1]
        color_display.config(bg=paint_color)

def erase(event):
    col = event.x // cell_size
    row = event.y // cell_size
    if (row, col) in points:
        # delete canvas by point id
        rect_id, _ = points[(row, col)]
        canvas.delete(rect_id)
        del points[(row, col)]

def redraw_all():
    canvas.delete("all")
    draw_grid()
    for (row, col), (rect_id, color) in points.items():
        x1 = col * cell_size
        y1 = row * cell_size
        x2 = x1 + cell_size
        y2 = y1 + cell_size
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

def zoom(event):
    global zoom_factor, cell_size
    # ปรับ zoom_factor ตามทิศทาง scroll
    if event.delta > 0:
        zoom_factor *= 1.1
    else:
        zoom_factor /= 1.1
    # จำกัด zoom_factor ให้อยู่ในช่วงที่เหมาะสม
    zoom_factor = max(0.5, min(zoom_factor, 10))
    cell_size = int(base_cell_size * zoom_factor)
    # ปรับ scrollregion
    canvas.config(scrollregion=(0, 0, canvas_width * zoom_factor, canvas_height * zoom_factor))
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
# canvas.bind("<MouseWheel>", zoom)

master.mainloop()