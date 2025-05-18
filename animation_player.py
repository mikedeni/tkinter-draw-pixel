import tkinter as tk
from pathlib import Path
import re

CANVAS_WIDTH = 1024
CANVAS_HEIGHT = 576
CELL_SIZE = 4  # ขนาดช่องตาราง

class AnimationPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Animation Player")
        self.root.geometry("1024x650+100+50")
        
        # ตัวแปรสำหรับอนิเมชัน
        self.frames = []  # เก็บข้อมูลเฟรม
        self.current_frame_index = 0
        self.play_end_frame_index = 0
        self.is_playing = False
        self.animation_after_id = None
        self.animation_folder_path = Path("./naruto_frame")
        self.is_idle = True
        self.idle_frame_index = 0
        self.idle_frame_indices = [0, 1] # Frame 1 and 2
        
        # ตั้งค่า UI
        self.setup_ui()
        self.load_folder()
        
    def setup_ui(self):
        # จัดวางหน้าต่างหลัก
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # ข้อความด้านบน
        message = tk.Label(self.root, text="โปรแกรมเล่นอนิเมชัน", font=("Helvetica", 11))
        message.grid(row=0, column=0, sticky="ew")
        
        # กรอบแคนวาส
        self.canvas_container = tk.Frame(self.root)
        self.canvas_container.grid(row=1, column=0, sticky="nsew")
        
        self.canvas = tk.Canvas(self.canvas_container, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # กรอบปุ่มควบคุม
        self.control_panel = tk.Frame(self.root)
        self.control_panel.grid(row=2, column=0, sticky="ew", padx=40, pady=5)
        
        # ปุ่มควบคุม
        self.control_panel.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.skill1_button = tk.Button(self.control_panel, text="Skill 1", command=lambda:self.play_animation(3, 10), font=("Helvetica", 11))
        self.skill1_button.grid(row=0, column=0, padx=10, sticky="ew")
        
        self.skill2_button = tk.Button(self.control_panel, text="Skill 2", command=lambda:self.play_animation(11, 19), font=("Helvetica", 11))
        self.skill2_button.grid(row=0, column=1, padx=10, sticky="ew")
        
        self.skill3_button = tk.Button(self.control_panel, text="Skill 3", command=lambda:self.play_animation(20, 29), font=("Helvetica", 11))
        self.skill3_button.grid(row=0, column=2, padx=10, sticky="ew")
    
    def load_folder(self):
        if not self.animation_folder_path.is_dir():
            print(f"animation โฟลเดอร์ไม่ถูกต้อง")
            return

        def extract_number(file_path):
            # สมมติชื่อไฟล์เป็นรูปแบบเลข.txt เช่น 1.txt, 10.txt
            match = re.search(r'(\d+)', file_path.stem)
            return int(match.group(1)) if match else -1
        
        txt_files = sorted(self.animation_folder_path.glob("*.txt"), key=extract_number)
            
        # โหลดข้อมูลแต่ละเฟรมจากไฟล์ txt แล้วเก็บตำแหน่งและสีลงใน frames
        for file_path in txt_files:
            frame_data = {}
            try:
                with open(file_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        row, col, _, color = line.split(",")
                        frame_data[(int(row), int(col))] = color
                self.frames.append(frame_data)
            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการโหลดไฟล์ {file_path}: {e}")
        
        self.run_idle_animation()
        
    def display_frame(self, frame_index):
        # ล้างแคนวาส
        self.canvas.delete("all")
        
        # แสดงเฟรมปัจจุบัน
        if 0 <= frame_index < len(self.frames):
            frame_data = self.frames[frame_index]
            for (row, col), color in frame_data.items():
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
    
    def play_animation(self, start, end):
        self.is_idle = False
        start -= 1
        end -= 1

        if not self.frames:
            return
        
        if start < 0 or end >= len(self.frames) or start > end:
            print("ช่วงเฟรมที่ต้องการเล่นไม่ถูกต้อง")
            return
        
        self.play_end_frame_index = end
        self.current_frame_index = start
        self.is_playing = True
        self.animate_next_frame()
    
    def stop_animation(self):
        self.is_playing = False
        if self.animation_after_id:
            self.root.after_cancel(self.animation_after_id)
            self.animation_after_id = None
        self.is_idle = True
        self.idle_frame_index = 0
        self.root.after(500, self.run_idle_animation)
    
    def animate_next_frame(self):
        if not self.is_playing:
            return
        
        self.display_frame(self.current_frame_index)
        
        if self.current_frame_index >= self.play_end_frame_index:
            self.stop_animation()
            return
            
        self.current_frame_index +=1
        
        self.animation_after_id = self.root.after(250, self.animate_next_frame)

    def run_idle_animation(self):
        if not self.is_idle or not self.frames:
            return
        self.display_frame(self.idle_frame_indices[self.idle_frame_index])
        self.idle_frame_index = (self.idle_frame_index + 1) % len(self.idle_frame_indices)
        self.root.after(500, self.run_idle_animation)

# เริ่มแอปพลิเคชัน
if __name__ == "__main__":
    root = tk.Tk()
    app = AnimationPlayer(root)
    root.mainloop()
