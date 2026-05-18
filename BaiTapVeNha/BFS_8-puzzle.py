import tkinter as tk
from tkinter import messagebox
from collections import deque

# ==========================================
# THUẬT TOÁN BFS (Logic)
# ==========================================
def find_blank(state):
    return state.index(0)

def move(state, blank_idx, target_idx):
    new_state = list(state)
    new_state[blank_idx], new_state[target_idx] = new_state[target_idx], new_state[blank_idx]
    return tuple(new_state)

def get_neighbors(state):
    neighbors = []
    blank_idx = find_blank(state)
    row, col = divmod(blank_idx, 3)

    moves = {
        'Lên': (row - 1, col),
        'Xuống': (row + 1, col),
        'Trái': (row, col - 1),
        'Phải': (row, col + 1)
    }

    for action, (r, c) in moves.items():
        if 0 <= r < 3 and 0 <= c < 3:
            target_idx = r * 3 + c
            new_state = move(state, blank_idx, target_idx)
            neighbors.append((new_state, action))
    return neighbors

def bfs_8_puzzle(start_state, goal_state):
    start_state = tuple(start_state)
    goal_state = tuple(goal_state)
    
    queue = deque([(start_state, [start_state])])
    visited = set()
    visited.add(start_state)

    while queue:
        current_state, path = queue.popleft()

        if current_state == goal_state:
            return path

        for next_state, action in get_neighbors(current_state):
            if next_state not in visited:
                visited.add(next_state)
                queue.append((next_state, path + [next_state]))

    return None

# ==========================================
# GIAO DIỆN ĐỒ HỌA (Tkinter)
# ==========================================
class PuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver (BFS)")
        self.root.geometry("400x550")
        self.root.configure(bg="#2c3e50")

        self.start_state = []
        self.goal_state = []
        self.current_state = []

        # --- KHU VỰC NHẬP LIỆU ---
        input_frame = tk.Frame(self.root, bg="#2c3e50")
        input_frame.pack(pady=15)

        tk.Label(input_frame, text="Bắt đầu (VD: 123405786):", bg="#2c3e50", fg="white", font=("Helvetica", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_start = tk.Entry(input_frame, width=15, font=("Helvetica", 10))
        self.entry_start.insert(0, "123405786")
        self.entry_start.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Đích (VD: 123456780):", bg="#2c3e50", fg="white", font=("Helvetica", 10)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_goal = tk.Entry(input_frame, width=15, font=("Helvetica", 10))
        self.entry_goal.insert(0, "123456780")
        self.entry_goal.grid(row=1, column=1, padx=5, pady=5)

        self.btn_set = tk.Button(input_frame, text="Thiết lập Bảng", bg="#2980b9", fg="white", font=("Helvetica", 10, "bold"), command=self.setup_board)
        self.btn_set.grid(row=2, column=0, columnspan=2, pady=10)

        # --- KHU VỰC BẢNG PUZZLE ---
        self.frame = tk.Frame(self.root, bg="#34495e", bd=5)
        self.frame.pack(pady=5)

        self.tiles = []
        for i in range(9):
            row, col = divmod(i, 3)
            lbl = tk.Label(self.frame, text="", font=("Helvetica", 24, "bold"),
                           width=4, height=2, bg="#ecf0f1", fg="#2c3e50", relief="raised")
            lbl.grid(row=row, column=col, padx=5, pady=5)
            self.tiles.append(lbl)

        # --- KHU VỰC ĐIỀU KHIỂN & THÔNG BÁO ---
        self.status_lbl = tk.Label(self.root, text="Nhập trạng thái và nhấn 'Thiết lập Bảng'", font=("Helvetica", 11), bg="#2c3e50", fg="#f1c40f")
        self.status_lbl.pack(pady=10)

        self.btn_solve = tk.Button(self.root, text="Giải (BFS)", font=("Helvetica", 12, "bold"),
                                   bg="#27ae60", fg="white", command=self.solve_puzzle, state=tk.DISABLED)
        self.btn_solve.pack(pady=5)

        # Thiết lập bảng ngay lần đầu chạy với giá trị mặc định
        self.setup_board()

    def is_valid_input(self, text):
        """Kiểm tra xem chuỗi nhập vào có đúng 9 số từ 0-8 và không trùng nhau không"""
        if len(text) != 9 or not text.isdigit():
            return False
        if set(text) != set("012345678"):
            return False
        return True

    def setup_board(self):
        start_str = self.entry_start.get().strip()
        goal_str = self.entry_goal.get().strip()

        if not self.is_valid_input(start_str) or not self.is_valid_input(goal_str):
            messagebox.showerror("Lỗi nhập liệu", "Vui lòng nhập đúng 9 chữ số từ 0 đến 8, không trùng lặp!\n(Số 0 đại diện cho ô trống)")
            return

        # Chuyển chuỗi thành mảng số nguyên
        self.start_state = [int(x) for x in start_str]
        self.goal_state = [int(x) for x in goal_str]
        self.current_state = list(self.start_state)
        
        self.draw_board(self.current_state)
        self.status_lbl.config(text="Sẵn sàng giải!", fg="#2ecc71")
        self.btn_solve.config(state=tk.NORMAL)

    def draw_board(self, state):
        for i in range(9):
            val = state[i]
            if val == 0:
                self.tiles[i].config(text="", bg="#95a5a6")
            else:
                self.tiles[i].config(text=str(val), bg="#ecf0f1")

    def solve_puzzle(self):
        self.btn_solve.config(state=tk.DISABLED)
        self.btn_set.config(state=tk.DISABLED)
        self.status_lbl.config(text="Đang tìm kiếm đường đi (có thể mất vài giây)...", fg="#f39c12")
        self.root.update()

        path = bfs_8_puzzle(self.start_state, self.goal_state)

        if path:
            self.status_lbl.config(text=f"Tìm thấy đường đi! Tổng cộng: {len(path)-1} bước.", fg="#2ecc71")
            self.animate_solution(path, 0)
        else:
            self.status_lbl.config(text="Không thể giải! (Lỗi Parity Inversion)", fg="#e74c3c")
            messagebox.showerror("Thất bại", "Trạng thái này không thể giải quyết do vi phạm tính chẵn lẻ của bài toán 8-Puzzle.")
            self.btn_solve.config(state=tk.NORMAL)
            self.btn_set.config(state=tk.NORMAL)

    def animate_solution(self, path, step):
        if step < len(path):
            self.draw_board(path[step])
            self.root.after(400, self.animate_solution, path, step + 1)
        else:
            self.status_lbl.config(text="Hoàn thành!", fg="#3498db")
            self.btn_solve.config(state=tk.NORMAL)
            self.btn_set.config(state=tk.NORMAL)

# ==========================================
# KHỞI CHẠY ỨNG DỤNG
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.mainloop()
