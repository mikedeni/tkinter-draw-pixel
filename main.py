import tkinter as tk
from tkinter import filedialog as fd
from tkinter import colorchooser as cc

class DrawingApp:
    def __init__(self, master):
        # Initialize attributes
        self.canvas_width = 1024
        self.canvas_height = 576
        self.cell_size = 4
        self.zoom_factor = 1.0
        self.base_cell_size = 4
        self.initial_rows = self.canvas_height // self.base_cell_size
        self.initial_cols = self.canvas_width // self.base_cell_size
        self.points = {}  # เก็บสีของแต่ละช่อง {(row, col): (rect_id, color)}
        self.paint_color = "#11ff00"
        self.button_font = ("Helvetica", 11)
        
        self.master = master
        self.master.title("Drawing App with Grid")
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.geometry("1024x650+100+50")
        
        self.setup_ui()
        self.draw_grid()
        self.setup_color_palette()
        self.bind_events()
    
    def setup_ui(self):
        # สร้าง frame ครอบ canvas กับ scrollbar
        self.canvas_frame = tk.Frame(self.master)
        self.canvas_frame.grid(row=1, column=0, sticky="nsew")

        self.canvas = tk.Canvas(self.canvas_frame, width=self.canvas_width, 
                              height=self.canvas_height, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # สร้าง scrollbar แนวตั้ง
        self.v_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, 
                                       command=self.canvas.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")

        # สร้าง scrollbar แนวนอน
        self.h_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, 
                                       command=self.canvas.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        # เชื่อม scrollbar กับ canvas
        self.canvas.config(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)

        # กำหนดขนาด scrollable area
        self.canvas.config(scrollregion=(0, 0, self.canvas_width, self.canvas_height))

        # ปรับ grid config ให้ canvas_frame ขยายได้
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Message label
        self.message = tk.Label(self.master, text="คลิ๊กซ้ายลงสี, คลิ๊กขวาลบสี", font=("Helvetica", 11))
        self.message.grid(row=0, column=0, sticky="ew")
        
        # Button frame
        self.button_frame = tk.Frame(self.master)
        self.button_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=5)
        
        # ตั้งค่าให้คอลัมน์ในส่วนปุ่มมีน้ำหนักเท่ากัน
        self.button_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        
        # Create buttons
        self.save_button = tk.Button(self.button_frame, text="บันทึกภาพวาด", 
                                   command=self.save_drawing, font=self.button_font)
        self.save_button.grid(row=0, column=0, padx=10, sticky="ew")

        self.load_button = tk.Button(self.button_frame, text="เปิดภาพวาด", 
                                   command=self.load_drawing, font=self.button_font)
        self.load_button.grid(row=0, column=1, padx=10, sticky="ew")

        self.clear_button = tk.Button(self.button_frame, text="ล้างภาพวาด", 
                                    command=self.clear_canvas, font=self.button_font)
        self.clear_button.grid(row=0, column=2, padx=10, sticky="ew")

        self.color_button = tk.Button(self.button_frame, text="เลือกสี", 
                                    command=self.choose_color, font=self.button_font)
        self.color_button.grid(row=0, column=3, padx=10, sticky="ew")

        self.color_display = tk.Label(self.button_frame, bg=self.paint_color, width=2)
        self.color_display.grid(row=0, column=4, padx=5, sticky="ew")

        self.color_entry = tk.Entry(self.button_frame, width=8, font=self.button_font)
        self.color_entry.grid(row=0, column=5, padx=5, sticky="ew")
        self.color_entry.insert(0, self.paint_color)
        self.color_entry.bind("<Return>", self.update_color_from_entry)

    def bind_events(self):
        self.canvas.bind("<Button-1>", self.paint)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<Button-3>", self.erase)
        self.canvas.bind("<B3-Motion>", self.erase)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.master.bind("<Left>", lambda e: self.canvas.xview_scroll(-1, "units"))
        self.master.bind("<Right>", lambda e: self.canvas.xview_scroll(1, "units"))
        self.master.bind("<Up>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.master.bind("<Down>", lambda e: self.canvas.yview_scroll(1, "units"))

    def draw_grid(self):
        rows = self.canvas_height // self.cell_size
        cols = self.canvas_width // self.cell_size
        center_x = self.canvas_width // 2
        center_y = self.canvas_height // 2

        for col in range(cols + 1):
            x = col * self.cell_size
            if x == center_x:
                self.canvas.create_line(x, 0, x, self.canvas_height, fill="blue")
            elif col % 8 == 0:
                self.canvas.create_line(x, 0, x, self.canvas_height, fill="red")
            else:
                self.canvas.create_line(x, 0, x, self.canvas_height, fill="gray")

        for row in range(rows + 1):
            y = row * self.cell_size
            if y == center_y:
                self.canvas.create_line(0, y, self.canvas_width, y, fill="blue")
            elif row % 8 == 0:
                self.canvas.create_line(0, y, self.canvas_width, y, fill="red")
            else:
                self.canvas.create_line(0, y, self.canvas_width, y, fill="gray")

    def paint(self, event):
        # ปรับพิกัดตาม scroll offset
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        col = int(x // self.cell_size)
        row = int(y // self.cell_size)
        if 0 <= col < self.canvas_width // self.cell_size and 0 <= row < self.canvas_height // self.cell_size:
            if (row, col) in self.points:
                rect_id, _ = self.points[(row, col)]
                self.canvas.itemconfig(rect_id, fill=self.paint_color)
                self.points[(row, col)] = (rect_id, self.paint_color)
            else:
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.paint_color, outline="")
                self.points[(row, col)] = (rect_id, self.paint_color)

    def save_drawing(self):
        file_path = fd.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if file_path:
            with open(file_path, "w") as f:
                for (row, col), (id, color) in self.points.items():
                    f.write(f"{row},{col},{id},{color}\n")

    def clear_canvas(self):
        self.canvas.delete("all")
        self.points.clear()
        self.draw_grid()

    def load_drawing(self):
        file_path = fd.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All Files", "*.*")],
        )
        if file_path:
            self.clear_canvas()
            with open(file_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    row, col, id, color = line.split(",")
                    row, col = int(row), int(col)
                    x1 = col * self.cell_size
                    y1 = row * self.cell_size
                    x2 = x1 + self.cell_size
                    y2 = y1 + self.cell_size
                    rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                    self.points[(row, col)] = (id, color)

    def choose_color(self):
        color_code = cc.askcolor(title="เลือกสี")[1]
        if color_code:
            self.paint_color = color_code
            self.color_display.config(bg=self.paint_color)
            self.color_entry.delete(0, tk.END)
            self.color_entry.insert(0, self.paint_color)

    def erase(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        col = int(x // self.cell_size)
        row = int(y // self.cell_size)
        if (row, col) in self.points:
            rect_id, _ = self.points[(row, col)]
            self.canvas.delete(rect_id)
            del self.points[(row, col)]

    def update_canvas_and_cellsize(self, zoom_factor):
        self.cell_size = int(self.base_cell_size * zoom_factor)
        if self.cell_size < 1:
            self.cell_size = 1
        self.canvas_width = self.initial_cols * self.cell_size
        self.canvas_height = self.initial_rows * self.cell_size
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)
        return self.cell_size, self.canvas_width, self.canvas_height

    def redraw_all(self):
        self.canvas.delete("all")
        self.draw_grid()
        for (row, col), (rect_id, color) in list(self.points.items()):
            x1 = col * self.cell_size
            y1 = row * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            new_rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
            self.points[(row, col)] = (new_rect_id, color)

    def zoom(self, event):
        # บันทึกตำแหน่งเดิมก่อนซูม
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # คำนวณอัตราส่วนตำแหน่งเทียบกับขนาด canvas
        x_ratio = x / self.canvas_width
        y_ratio = y / self.canvas_height
        
        # ปรับ zoom factor
        if event.delta > 0:
            self.zoom_factor *= 1.1
        elif event.delta < 0:
            self.zoom_factor /= 1.1
        self.zoom_factor = max(0.2, min(self.zoom_factor, 5))
        
        # ปรับขนาด cell และ canvas
        self.update_canvas_and_cellsize(self.zoom_factor)
        self.redraw_all()
        
        # อัปเดต scrollregion
        self.canvas.config(scrollregion=(0, 0, self.canvas_width, self.canvas_height))
        
        # เลื่อนให้ตำแหน่งที่ซูมอยู่ตรงกลาง
        self.canvas.xview_moveto(x_ratio - 0.5)
        self.canvas.yview_moveto(y_ratio - 0.5)

    def update_color_from_entry(self, event=None):
        color = self.color_entry.get()
        if color.startswith("#") and (len(color) == 7 or len(color) == 4):
            try:
                # ทดสอบสีโดยสร้างสี่เหลี่ยมเล็กๆ
                self.canvas.create_rectangle(0, 0, 1, 1, fill=color)
                self.paint_color = color
                self.color_display.config(bg=self.paint_color)
            except tk.TclError:
                pass  # สีไม่ถูกต้อง ไม่ทำอะไร

    def setup_color_palette(self):
        palette = tk.Frame(self.master)
        palette.grid(row=3, column=0, padx=10, pady=5)

        colors = [
            "#000000",
            "#282828",
            "#505050",
            "#a0a0a0",
            "#d09018",
            "#f8e048",
            "#e84000",
            "#f89840",
            "#d86020",
            "#fb9043",
            "#f8c880",
            "#f8ebce",
            "#4880b0",
            "#887068",
            "#c0b0a8",
            "#e0d8d0",
            "#1840f8",
            "#3bc6f8",
            "#a8e8f8",
            "#dff4f8",
            "#f80000",
            "#f89040",
            "#a00800",
            "#e82810"
        ]

        for i, color in enumerate(colors):
            btn = tk.Button(palette, bg=color, width=2, height=1)
            btn.config(command=lambda c=color: self.select_color(c))
            btn.grid(row=0, column=i, padx=3)

        add_btn = tk.Button(palette, text="+", width=2, command=self.open_color_picker)
        add_btn.grid(row=0, column=len(colors), padx=3)
    
    def select_color(self, color):
        self.paint_color = color
        self.color_display.config(bg=color)
        self.color_entry.delete(0, tk.END)
        self.color_entry.insert(0, color)

    def open_color_picker(self):
        color = cc.askcolor(title="เลือกสี")[1]
        if color:
            self.select_color(color)

def main():
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
