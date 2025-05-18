import tkinter as tk
from tkinter import filedialog as fd
import os
import glob
from pathlib import Path
import re

canvas_width = 1024
canvas_height = 576
cell_size = 4  # ขนาดช่องตาราง

class AnimationPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Animation Player")
        self.root.geometry("1024x650+100+50")
        
        # ตัวแปรสำหรับอนิเมชัน
        self.frames = []  # เก็บข้อมูลเฟรม
        self.current_frame = 0
        self.is_playing = False
        self.animation_id = None
        self.animation_speed = 100  # มิลลิวินาที
        
        # ตั้งค่า UI
        self.setup_ui()
        
    def setup_ui(self):
        # จัดวางหน้าต่างหลัก
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # ข้อความด้านบน
        message = tk.Label(self.root, text="โปรแกรมเล่นอนิเมชัน", font=("Helvetica", 11))
        message.grid(row=0, column=0, sticky="ew")
        
        # กรอบแคนวาส
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.grid(row=1, column=0, sticky="nsew")
        
        self.canvas = tk.Canvas(self.canvas_frame, width=canvas_width, height=canvas_height, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar
        self.v_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.h_scrollbar = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.canvas.config(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)
        self.canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))
        
        # กรอบปุ่มควบคุม
        self.control_frame = tk.Frame(self.root)
        self.control_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=5)
        
        # ปุ่มควบคุม
        self.control_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        
        self.load_folder_btn = tk.Button(self.control_frame, text="เลือกโฟลเดอร์", command=self.load_folder, font=("Helvetica", 11))
        self.load_folder_btn.grid(row=0, column=0, padx=10, sticky="ew")
        
        self.play_btn = tk.Button(self.control_frame, text="เล่น", command=self.play_animation, font=("Helvetica", 11))
        self.play_btn.grid(row=0, column=1, padx=10, sticky="ew")
        
        self.stop_btn = tk.Button(self.control_frame, text="หยุด", command=self.stop_animation, font=("Helvetica", 11))
        self.stop_btn.grid(row=0, column=2, padx=10, sticky="ew")
        
        self.frame_label = tk.Label(self.control_frame, text="เฟรม: 0/0", font=("Helvetica", 11))
        self.frame_label.grid(row=0, column=3, padx=10, sticky="ew")
        
        # ควบคุมความเร็ว
        self.speed_label = tk.Label(self.control_frame, text="ความเร็ว (ms):", font=("Helvetica", 11))
        self.speed_label.grid(row=0, column=4, padx=5, sticky="e")
        
        self.speed_scale = tk.Scale(self.control_frame, from_=10, to=500, orient=tk.HORIZONTAL, length=150)
        self.speed_scale.set(self.animation_speed)
        self.speed_scale.grid(row=0, column=5, padx=5, sticky="ew")
    
    def load_folder(self):
        folder_path = fd.askdirectory(title="เลือกโฟลเดอร์ที่มีเฟรมอนิเมชัน")
        if not folder_path:
            return
            
        # ล้างเฟรมปัจจุบัน
        self.frames = []
        self.stop_animation()
        
        # ดึงไฟล์ .txt ทั้งหมดจากโฟลเดอร์
        txt_files = glob.glob(os.path.join(folder_path, "*.txt"))

        # แก้ไข path ให้ใช้ / แทน \ เพื่อให้ pathlib ทำงานถูกต้อง
        txt_files = [path.replace('\\', '/') for path in txt_files]

        # ดึงชื่อไฟล์ออกมา
        file_names = [Path(path).name for path in txt_files]

        # สร้างคู่ (ชื่อไฟล์, path) เพื่อเรียงลำดับตามเลขในชื่อไฟล์
        def extract_number(filename):
            # สมมติชื่อไฟล์เป็นรูปแบบเลข.txt เช่น 1.txt, 10.txt
            match = re.search(r'(\d+)', filename)
            return int(match.group(1)) if match else -1
        
        # จับคู่ชื่อไฟล์กับ path
        files_with_names = list(zip(file_names, txt_files))

        # เรียงลำดับตามเลขในชื่อไฟล์
        files_with_names.sort(key=lambda x: extract_number(x[0]))

        # แยกชื่อไฟล์และ path ที่เรียงแล้ว
        sorted_file_names, sorted_paths = zip(*files_with_names)

        print("เรียงชื่อไฟล์:", sorted_file_names)
            
        # โหลดทุกเฟรม
        for file_path in sorted_paths:
            frame_data = {}
            try:
                with open(file_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        row, col, id, color = line.split(",")
                        frame_data[(int(row), int(col))] = color
                self.frames.append(frame_data)
            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการโหลดไฟล์ {file_path}: {e}")
                
        self.current_frame = 0
        self.frame_label.config(text=f"เฟรม: {self.current_frame + 1}/{len(self.frames)}")
        self.display_frame(self.current_frame)
        
    def display_frame(self, frame_index):
        # ล้างแคนวาส
        self.canvas.delete("all")
        
        # แสดงเฟรมปัจจุบัน
        if 0 <= frame_index < len(self.frames):
            frame_data = self.frames[frame_index]
            for (row, col), color in frame_data.items():
                x1 = col * cell_size
                y1 = row * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
    
    def play_animation(self):
        if not self.frames:
            return
        
        if self.is_playing:
            self.pause_animation()
            return
            
        self.is_playing = True
        self.play_btn.config(text="หยุดชั่วคราว")
        self.animate_next_frame()
    
    def pause_animation(self):
        self.is_playing = False
        self.play_btn.config(text="เล่น")
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
    
    def stop_animation(self):
        self.pause_animation()
        self.current_frame = 0
        if self.frames:
            self.display_frame(self.current_frame)
            self.frame_label.config(text=f"เฟรม: {self.current_frame + 1}/{len(self.frames)}")
    
    def animate_next_frame(self):
        if not self.is_playing:
            return
            
        # แสดงเฟรมปัจจุบัน
        self.display_frame(self.current_frame)
        self.frame_label.config(text=f"เฟรม: {self.current_frame + 1}/{len(self.frames)}")
        
        # ไปยังเฟรมถัดไป (วนกลับไปเริ่มต้นถ้าจำเป็น)
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        
        # กำหนดเวลาเฟรมถัดไป
        speed = self.speed_scale.get()
        self.animation_id = self.root.after(speed, self.animate_next_frame)

# เริ่มแอปพลิเคชัน
if __name__ == "__main__":
    root = tk.Tk()
    app = AnimationPlayer(root)
    root.mainloop()
