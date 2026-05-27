import tkinter as tk
from tkinter import messagebox
import heapq

# --- CẤU TRÚC DỮ LIỆU NÚT ---
class Node:
    def __init__(self, state, parent=None, action=None, g_cost=0, h_cost=0):
        self.state = state
        self.parent = parent
        self.action = action 
        self.g_cost = g_cost  # Chi phí thực tế g(n)
        self.h_cost = h_cost  # Chi phí ước lượng h(n)
        self.f_cost = 0       # f(n) dùng để sắp xếp hàng đợi ưu tiên

# --- HÀM HEURISTIC (MANHATTAN DISTANCE) ---
def manhattan_distance(state, goal_state):
    distance = 0
    for i in range(9):
        val = state[i]
        if val != 0: 
            goal_index = goal_state.index(val)
            current_row, current_col = divmod(i, 3)
            goal_row, goal_col = divmod(goal_index, 3)
            distance += abs(current_row - goal_row) + abs(current_col - goal_col)
    return distance

# --- HÀM SINH TRẠNG THÁI KỀ (HÀNG XÓM) ---
def get_neighbors(state):
    neighbors = []
    index = state.index(0)
    row, col = divmod(index, 3)
    moves = [('Lên', -1, 0), ('Xuống', 1, 0), ('Trái', 0, -1), ('Phải', 0, 1)]
    
    for action, dr, dc in moves:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_index = new_row * 3 + new_col
            new_state = list(state)
            new_state[index], new_state[new_index] = new_state[new_index], new_state[index]
            neighbors.append((tuple(new_state), action))
    return neighbors

def get_path(node):
    path = []
    while node:
        path.append((node.state, node.action))
        node = node.parent
    return path[::-1]

# =========================================================================
# ĐOẠN 1: THUẬT TOÁN GREEDY SEARCH (Theo chính xác mã giả Hình 1)
# =========================================================================
def greedy_search(start_state, goal_state):
    # 1. Khởi tạo tập FRONTIER = {Start}. Tính hàm đánh giá h(Start)
    start_node = Node(start_state)
    start_node.h_cost = manhattan_distance(start_state, goal_state)
    start_node.f_cost = start_node.h_cost  # Sắp xếp theo h(n)
    
    # Dùng heap để lấy min, kết hợp dict để kiểm tra m có trong FRONTIER không
    frontier_heap = [(start_node.f_cost, id(start_node), start_node)]
    frontier_dict = {start_state: start_node}
    
    # 2. Khởi tạo tập REACHED = {}
    reached_set = set()
    
    # 3. TRONG KHI (FRONTIER không rỗng):
    while frontier_heap:
        # a. Chọn trạng thái n từ FRONTIER có h(n) nhỏ nhất
        _, _, node = heapq.heappop(frontier_heap)
        if node.state not in frontier_dict or frontier_dict[node.state] != node:
            continue  # Bỏ qua các nút trùng lặp cũ trong heap
            
        # b. NẾU n == Goal: TRẢ VỀ "Thành công"
        if node.state == goal_state:
            return get_path(node)
            
        # c. Loại bỏ n khỏi FRONTIER và thêm n vào REACHED
        del frontier_dict[node.state]
        reached_set.add(node.state)
        
        # d. Với mỗi trạng thái m kề với n:
        for m_state, action in get_neighbors(node.state):
            
            # i. NẾU m chưa có trong cả FRONTIER và REACHED:
            if m_state not in frontier_dict and m_state not in reached_set:
                child = Node(m_state, parent=node, action=action) # Gán cha là n
                child.h_cost = manhattan_distance(m_state, goal_state) # Tính heuristic
                child.f_cost = child.h_cost
                
                # Thêm m vào FRONTIER
                frontier_dict[m_state] = child
                heapq.heappush(frontier_heap, (child.f_cost, id(child), child))
                
            # ii. NẾU m đã có trong FRONTIER hoặc REACHED: Bỏ qua m
            else:
                continue
                
    return None # 4. TRẢ VỀ "Thất bại"

# =========================================================================
# ĐOẠN 2: THUẬT TOÁN A* SEARCH (Theo chính xác mã giả Hình 2)
# =========================================================================
def astar_search(start_state, goal_state):
    # 1. Khởi tạo tập FRONTIER = {Start} với f(Start) = 0 + h(Start)
    start_node = Node(start_state, g_cost=0)
    start_node.h_cost = manhattan_distance(start_state, goal_state)
    start_node.f_cost = start_node.g_cost + start_node.h_cost
    
    frontier_heap = [(start_node.f_cost, id(start_node), start_node)]
    frontier_dict = {start_state: start_node}
    
    # 2. Khởi tạo tập REACHED = {} (Lưu dưới dạng dict để tra cứu g_cost)
    reached_dict = {}
    
    # 3. TRONG KHI (FRONTIER không rỗng):
    while frontier_heap:
        # a. Chọn trạng thái n từ FRONTIER có giá trị f(n) nhỏ nhất
        _, _, node = heapq.heappop(frontier_heap)
        if node.state not in frontier_dict or frontier_dict[node.state] != node:
            continue
            
        # b. NẾU n == Goal: TRẢ VỀ "Thành công"
        if node.state == goal_state:
            return get_path(node)
            
        # c. Loại bỏ n khỏi FRONTIER và thêm n vào REACHED
        del frontier_dict[node.state]
        reached_dict[node.state] = node
        
        # d. Với mỗi trạng thái m kề với n:
        for m_state, action in get_neighbors(node.state):
            # i. Tính toán chi phí thực tế mới: g_new(m) = g(n) + cost(m)
            g_new = node.g_cost + 1  # Trong 8-puzzle, mỗi bước dịch chuyển tính giá trị là 1
            
            in_reached = m_state in reached_dict
            in_frontier = m_state in frontier_dict
            
            # ii. NẾU m đã nằm trong REACHED:
            if in_reached:
                if g_new >= reached_dict[m_state].g_cost:
                    continue # Bỏ qua trạng thái m (tệ hơn)
                else:
                    # Xóa m khỏi REACHED và cập nhật lại g(m) = g_new(m)
                    del reached_dict[m_state]
                    in_reached = False # Đánh dấu để rơi xuống điều kiện iv kế tiếp
            
            # iii. NẾU m đã nằm trong FRONTIER:
            if in_frontier:
                if g_new < frontier_dict[m_state].g_cost:
                    # Cập nhật lại g(m), f(m) và đỉnh cha là n
                    target_node = frontier_dict[m_state]
                    target_node.g_cost = g_new
                    target_node.f_cost = g_new + target_node.h_cost
                    target_node.parent = node
                    target_node.action = action
                    # Đẩy cập nhật mới vào heap
                    heapq.heappush(frontier_heap, (target_node.f_cost, id(target_node), target_node))
            
            # iv. NẾU m chưa có mặt trong FRONTIER và REACHED:
            if not in_frontier and not in_reached:
                child = Node(m_state, parent=node, action=action, g_cost=g_new)
                child.h_cost = manhattan_distance(m_state, goal_state)
                child.f_cost = child.g_cost + child.h_cost
                
                # Thêm m vào FRONTIER
                frontier_dict[m_state] = child
                heapq.heappush(frontier_heap, (child.f_cost, id(child), child))
                
    return None # 4. TRẢ VỀ "Thất bại"

# --- PHẦN GIỮ NGUYÊN ĐỂ KHÔNG LỖI HỆ THỐNG GIAO DIỆN ---
def ucs_search(start_state, goal_state):
    start_node = Node(start_state, g_cost=0)
    start_node.f_cost = start_node.g_cost
    frontier = [(start_node.f_cost, id(start_node), start_node)]
    explored = set()
    while frontier:
        _, _, node = heapq.heappop(frontier)
        if node.state == goal_state: return get_path(node)
        if node.state not in explored:
            explored.add(node.state)
            for m_state, action in get_neighbors(node.state):
                if m_state not in explored:
                    child = Node(m_state, parent=node, action=action, g_cost=node.g_cost + 1)
                    child.f_cost = child.g_cost
                    heapq.heappush(frontier, (child.f_cost, id(child), child))
    return None

def dls(node, limit, goal_state):
    if node.state == goal_state: return node
    elif limit == 0: return 'cutoff'
    cutoff_occurred = False
    for m_state, action in get_neighbors(node.state):
        child = Node(m_state, parent=node, action=action)
        result = dls(child, limit - 1, goal_state)
        if result == 'cutoff': cutoff_occurred = True
        elif result is not None: return result
    return 'cutoff' if cutoff_occurred else None

def ids_search(start_state, goal_state, max_depth=30):
    for depth in range(max_depth):
        result = dls(Node(start_state), depth, goal_state)
        if result != 'cutoff' and result is not None: return get_path(result)
    return None

# --- GIAO DIỆN GUI (TKINTER) ---
class PuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver: Khớp thuật toán với Slide")
        self.root.geometry("680x580")
        self.current_state = (1, 2, 3, 4, 0, 5, 7, 8, 6)
        self.goal_state = (1, 2, 3, 4, 5, 6, 7, 8, 0)
        self.tiles = []
        self.is_animating = False 
        self.create_widgets()
        self.update_board(self.current_state)

    def create_widgets(self):
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
        tk.Button(input_frame, text="Cập nhật / Reset", font=('Arial', 10, 'bold'), bg="lightblue", command=self.apply_inputs).grid(row=0, column=2, rowspan=2, padx=10, ipady=5)

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))

        self.board_frame = tk.Frame(left_frame, bg="gray")
        self.board_frame.pack(pady=10)
        for i in range(9):
            lbl = tk.Label(self.board_frame, text="", font=('Arial', 24, 'bold'), width=4, height=2, bg="white", relief="raised")
            row, col = divmod(i, 3)
            lbl.grid(row=row, column=col, padx=2, pady=2)
            self.tiles.append(lbl)
            
        buttons_frame = tk.Frame(left_frame)
        buttons_frame.pack(pady=5)
        self.btn_ids = tk.Button(buttons_frame, text="Giải bằng IDS", font=('Arial', 11), width=15, command=lambda: self.solve('ids'))
        self.btn_ids.grid(row=0, column=0, pady=3, padx=3)
        self.btn_ucs = tk.Button(buttons_frame, text="Giải bằng UCS", font=('Arial', 11), width=15, command=lambda: self.solve('ucs'))
        self.btn_ucs.grid(row=1, column=0, pady=3, padx=3)
        self.btn_greedy = tk.Button(buttons_frame, text="Giải bằng Greedy", font=('Arial', 11), width=15, bg="#f0e68c", command=lambda: self.solve('greedy'))
        self.btn_greedy.grid(row=0, column=1, pady=3, padx=3)
        self.btn_astar = tk.Button(buttons_frame, text="Giải bằng A*", font=('Arial', 11), width=15, bg="#98fb98", command=lambda: self.solve('astar'))
        self.btn_astar.grid(row=1, column=1, pady=3, padx=3)
        
        self.status_lbl = tk.Label(left_frame, text="Sẵn sàng", font=('Arial', 10), fg="blue")
        self.status_lbl.pack(pady=10)

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
        if len(text) != 9 or not text.isdigit(): return None
        tup = tuple(int(c) for c in text)
        if set(tup) != set(range(9)): return None
        return tup

    def apply_inputs(self):
        if self.is_animating: return
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
            self.tiles[i].config(text="" if val == 0 else str(val), bg="lightgray" if val == 0 else "white")

    def toggle_buttons(self, state):
        btn_state = tk.NORMAL if state else tk.DISABLED
        self.btn_ucs.config(state=btn_state)
        self.btn_ids.config(state=btn_state)
        self.btn_greedy.config(state=btn_state)
        self.btn_astar.config(state=btn_state)

    def animate_solution(self, path, step=0):
        if step < len(path):
            state, action = path[step]
            self.update_board(state)
            log_text = "Bắt đầu: Trạng thái gốc" if action is None else f"Bước {step}: Ô trống sang {action}"
            self.move_listbox.insert(tk.END, log_text)
            self.move_listbox.see(tk.END) 
            self.status_lbl.config(text=f"Bước: {step}/{len(path)-1}")
            self.root.after(400, self.animate_solution, path, step + 1)
        else:
            self.status_lbl.config(text=f"Hoàn thành trong {len(path)-1} bước!", fg="green")
            self.move_listbox.insert(tk.END, "--- THÀNH CÔNG ---")
            self.move_listbox.see(tk.END)
            self.is_animating = False
            self.toggle_buttons(True)

    def solve(self, algo):
        if self.is_animating: return
        self.status_lbl.config(text=f"Đang tính toán {algo.upper()}...", fg="red")
        self.move_listbox.delete(0, tk.END) 
        self.is_animating = True
        self.toggle_buttons(False)
        self.root.update() 
        
        if algo == 'ucs': path = ucs_search(self.current_state, self.goal_state)
        elif algo == 'ids': path = ids_search(self.current_state, self.goal_state)
        elif algo == 'greedy': path = greedy_search(self.current_state, self.goal_state)
        elif algo == 'astar': path = astar_search(self.current_state, self.goal_state)
            
        if path: self.animate_solution(path)
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy đường đi!")
            self.status_lbl.config(text="Thất bại", fg="red")
            self.is_animating = False
            self.toggle_buttons(True)

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.mainloop()