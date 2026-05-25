import tkinter as tk
from tkinter import messagebox
import heapq

# --- CẤU TRÚC DỮ LIỆU ---
class Node:
    def __init__(self, state, parent=None, action=None, cost=0):
        self.state = state
        self.parent = parent
        self.action = action 
        self.cost = cost 

    def __lt__(self, other):
        return self.cost < other.cost

def get_successors(node):
    successors = []
    index = node.state.index(0)
    row, col = divmod(index, 3)
    
    moves = [('Lên', -1, 0), ('Xuống', 1, 0), ('Trái', 0, -1), ('Phải', 0, 1)]
    
    for action, dr, dc in moves:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_index = new_row * 3 + new_col
            new_state = list(node.state)
            new_state[index], new_state[new_index] = new_state[new_index], new_state[index]
            successors.append(Node(tuple(new_state), node, action, node.cost + 1))
            
    return successors

def get_path(node):
    path = []
    while node:
        path.append((node.state, node.action))
        node = node.parent
    return path[::-1]

# --- THUẬT TOÁN UCS ---
def ucs_search(start_state, goal_state):
    start_node = Node(start_state)
    frontier = []
    heapq.heappush(frontier, start_node)
    explored = set()

    while frontier:
        node = heapq.heappop(frontier)

        if node.state == goal_state:
            return get_path(node)

        if node.state not in explored:
            explored.add(node.state)
            for child in get_successors(node):
                if child.state not in explored:
                    heapq.heappush(frontier, child)
    return None

# --- THUẬT TOÁN IDS ---
def dls(node, limit, goal_state):
    if node.state == goal_state:
        return node
    elif limit == 0:
        return 'cutoff'
    
    cutoff_occurred = False
    for child in get_successors(node):
        result = dls(child, limit - 1, goal_state)
        if result == 'cutoff':
            cutoff_occurred = True
        elif result is not None:
            return result
    return 'cutoff' if cutoff_occurred else None

def ids_search(start_state, goal_state, max_depth=30):
    start_node = Node(start_state)
    for depth in range(max_depth):
        result = dls(start_node, depth, goal_state)
        if result != 'cutoff' and result is not None:
            return get_path(result)
    return None

# --- GIAO DIỆN GUI (TKINTER) ---
class PuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver: Tùy chỉnh trạng thái")
        self.root.geometry("650x550") 
        
        self.current_state = (1, 2, 3, 4, 0, 5, 7, 8, 6)
        self.goal_state = (1, 2, 3, 4, 5, 6, 7, 8, 0)
        self.tiles = []
        self.is_animating = False # Cờ chặn thao tác khi đang chạy animation
        
        self.create_widgets()
        self.update_board(self.current_state)

    def create_widgets(self):
        # --- KHUNG NHẬP LIỆU (TOP) ---
        input_frame = tk.Frame(self.root, pady=10)
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=20)

        tk.Label(input_frame, text="Trạng thái ban đầu:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.start_entry = tk.Entry(input_frame, width=20, font=('Arial', 10))
        self.start_entry.insert(0, "1 2 3 4 0 5 7 8 6")
        self.start_entry.grid(row=0, column=1, padx=10)

        tk.Label(input_frame, text="Trạng thái mục tiêu:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.goal_entry = tk.Entry(input_frame, width=20, font=('Arial', 10))
        self.goal_entry.insert(0, "1 2 3 4 5 6 7 8 0")
        self.goal_entry.grid(row=1, column=1, padx=10)

        tk.Button(input_frame, text="Cập nhật / Reset", font=('Arial', 10, 'bold'), bg="lightblue",
                  command=self.apply_inputs).grid(row=0, column=2, rowspan=2, padx=10, ipady=5)

        tk.Label(input_frame, text="(Nhập 9 số từ 0-8 cách nhau bởi dấu cách)", fg="gray", font=('Arial', 8)).grid(row=2, column=0, columnspan=2, sticky=tk.W)

        # --- KHUNG MAIN (Bàn cờ & Panel Lịch sử) ---
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))

        # --- BÊN TRÁI: BÀN CỜ & NÚT BẤM ---
        self.board_frame = tk.Frame(left_frame, bg="gray")
        self.board_frame.pack(pady=10)
        
        for i in range(9):
            lbl = tk.Label(self.board_frame, text="", font=('Arial', 24, 'bold'), 
                           width=4, height=2, bg="white", relief="raised")
            row, col = divmod(i, 3)
            lbl.grid(row=row, column=col, padx=2, pady=2)
            self.tiles.append(lbl)
            
        self.btn_ucs = tk.Button(left_frame, text="Giải bằng UCS", font=('Arial', 12), width=15, command=lambda: self.solve('ucs'))
        self.btn_ucs.pack(pady=5)
        
        self.btn_ids = tk.Button(left_frame, text="Giải bằng IDS", font=('Arial', 12), width=15, command=lambda: self.solve('ids'))
        self.btn_ids.pack(pady=5)
        
        self.status_lbl = tk.Label(left_frame, text="Sẵn sàng", font=('Arial', 10), fg="blue")
        self.status_lbl.pack(pady=10)

        # --- BÊN PHẢI: PANEL LỊCH SỬ ---
        tk.Label(right_frame, text="Lịch sử di chuyển", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        list_frame = tk.Frame(right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.move_listbox = tk.Listbox(list_frame, font=('Arial', 11), yscrollcommand=scrollbar.set)
        
        scrollbar.config(command=self.move_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.move_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def parse_input(self, text):
        text = text.replace(" ", "").replace(",", "")
        if len(text) != 9 or not text.isdigit():
            return None
        tup = tuple(int(c) for c in text)
        if set(tup) != set(range(9)):
            return None
        return tup

    def apply_inputs(self):
        if self.is_animating:
            return # Khóa nút nếu đang chạy animation

        start_tup = self.parse_input(self.start_entry.get())
        goal_tup = self.parse_input(self.goal_entry.get())

        if not start_tup or not goal_tup:
            messagebox.showerror("Lỗi nhập liệu", "Vui lòng nhập đủ 9 số từ 0 đến 8, không trùng lặp.")
            return

        self.current_state = start_tup
        self.goal_state = goal_tup
        self.update_board(self.current_state)
        self.move_listbox.delete(0, tk.END)
        self.status_lbl.config(text="Đã cập nhật trạng thái mới", fg="blue")

    def update_board(self, state):
        for i, val in enumerate(state):
            if val == 0:
                self.tiles[i].config(text="", bg="lightgray")
            else:
                self.tiles[i].config(text=str(val), bg="white")

    def toggle_buttons(self, state):
        btn_state = tk.NORMAL if state else tk.DISABLED
        self.btn_ucs.config(state=btn_state)
        self.btn_ids.config(state=btn_state)

    def animate_solution(self, path, step=0):
        if step < len(path):
            state, action = path[step]
            self.update_board(state)
            
            if action is None:
                log_text = "Bắt đầu: Trạng thái gốc"
            else:
                log_text = f"Bước {step}: Ô trống sang {action}"
                
            self.move_listbox.insert(tk.END, log_text)
            self.move_listbox.see(tk.END) 
            
            self.status_lbl.config(text=f"Bước: {step}/{len(path)-1}")
            self.root.after(500, self.animate_solution, path, step + 1)
        else:
            self.status_lbl.config(text=f"Hoàn thành trong {len(path)-1} bước!", fg="green")
            self.move_listbox.insert(tk.END, "--- THÀNH CÔNG ---")
            self.move_listbox.see(tk.END)
            self.is_animating = False
            self.toggle_buttons(True) # Mở khóa nút

    def solve(self, algo):
        if self.is_animating:
            return
            
        self.status_lbl.config(text="Đang tính toán (có thể mất vài giây)...", fg="red")
        self.move_listbox.delete(0, tk.END) 
        self.is_animating = True
        self.toggle_buttons(False) # Khóa nút bấm khi đang giải/hoạt hình
        self.root.update() 
        
        if algo == 'ucs':
            path = ucs_search(self.current_state, self.goal_state)
        else:
            path = ids_search(self.current_state, self.goal_state)
            
        if path:
            self.animate_solution(path)
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy đường đi hoặc vượt quá độ sâu/trạng thái lỗi!")
            self.status_lbl.config(text="Thất bại", fg="red")
            self.is_animating = False
            self.toggle_buttons(True)

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.mainloop()