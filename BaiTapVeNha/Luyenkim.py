import tkinter as tk
from tkinter import messagebox
import heapq
import random
import math
from collections import deque

# --- CẤU TRÚC DỮ LIỆU NÚT ---
class Node:
    def __init__(self, state, parent=None, action=None, g_cost=0, h_cost=0):
        self.state = state
        self.parent = parent
        self.action = action 
        self.g_cost = g_cost  
        self.h_cost = h_cost  
        self.f_cost = 0       

# --- HÀM HEURISTIC 1: MANHATTAN (Dùng cho Greedy và A*) ---
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

# --- HÀM HEURISTIC 2: MISPLACED TILES (Dùng cho Local Search) ---
def misplaced_tiles(state, goal_state):
    count = 0
    for i in range(9):
        if state[i] != 0 and state[i] != goal_state[i]:
            count += 1
    return count

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

def generate_random_state(start_state, moves=20):
    curr = start_state
    for _ in range(moves):
        neighbors = get_neighbors(curr)
        curr = random.choice(neighbors)[0]
    return curr

# =========================================================================
# CÁC THUẬT TOÁN TÌM KIẾM CỤC BỘ (LOCAL SEARCH)
# =========================================================================

# 1. LEO ĐỒI ĐƠN GIẢN (Simple Hill Climbing / First-Choice)
def simple_hill_climbing(start_state, goal_state):
    current_state = start_state
    path = [(current_state, None)]
    
    while True:
        current_value = -misplaced_tiles(current_state, goal_state)
        found_better = False
        
        for next_state, action in get_neighbors(current_state):
            next_value = -misplaced_tiles(next_state, goal_state)
            if next_value > current_value:
                current_state = next_state
                path.append((current_state, action))
                found_better = True
                break # Lấy ngay trạng thái tốt hơn đầu tiên
                
        if not found_better:
            break 
    return path 

# 2. LEO ĐỒI DỐC NHẤT (Steepest-Ascent Hill Climbing)
def steepest_ascent_hill_climbing(start_state, goal_state):
    current_state = start_state
    path = [(current_state, None)]
    
    while True:
        current_value = -misplaced_tiles(current_state, goal_state)
        best_next_state = None
        best_action = None
        best_value = float('-inf')
        
        # Duyệt TẤT CẢ các trạng thái kề để tìm cực đại
        for next_state, action in get_neighbors(current_state):
            next_value = -misplaced_tiles(next_state, goal_state)
            if next_value > best_value:
                best_value = next_value
                best_next_state = next_state
                best_action = action
                
        if best_value > current_value:
            current_state = best_next_state
            path.append((current_state, best_action))
        else:
            break # Kẹt cực đại cục bộ
            
    return path

# 3. LEO ĐỒI NGẪU NHIÊN (Stochastic Hill Climbing)
def stochastic_hill_climbing(start_state, goal_state):
    current_state = start_state
    path = [(current_state, None)]
    
    while True:
        if current_state == goal_state:
            return path
            
        current_value = -misplaced_tiles(current_state, goal_state)
        better_neighbors = []
        
        for next_state, action in get_neighbors(current_state):
            next_value = -misplaced_tiles(next_state, goal_state)
            if next_value > current_value:
                better_neighbors.append((next_state, action))
                
        if not better_neighbors:
            break 
            
        next_state, action = random.choice(better_neighbors)
        current_state = next_state
        path.append((current_state, action))
        
    return path

# 4. TÔI LUYỆN MÔ PHỎNG (Simulated Annealing - Theo Ảnh 1)
def simulated_annealing(start_state, goal_state, T0=100.0, Tmin=0.01, alpha=0.99):
    current_state = start_state
    path = [(current_state, 'Init SA')]
    T = T0
    
    while T > Tmin:
        if current_state == goal_state:
            return path
            
        neighbors = get_neighbors(current_state)
        if not neighbors:
            break
            
        next_state, action = random.choice(neighbors)
        
        # Heuristic h: số mảnh sai vị trí (Cần tối thiểu hóa h)
        h_current = misplaced_tiles(current_state, goal_state)
        h_next = misplaced_tiles(next_state, goal_state)
        
        # Delta = h(next) - h(current) theo đúng mã giả
        delta = h_next - h_current
        
        if delta < 0:
            current_state = next_state
            path.append((current_state, action))
        else:
            # Nếu next tệ hơn (delta >= 0), tính xác suất chấp nhận
            p = math.exp(-delta / T)
            if random.random() < p:
                current_state = next_state
                path.append((current_state, f"{action} (Xác suất p={p:.2f})"))
                
        T = alpha * T
        
    return path

# 5. RANDOM-RESTART VÀ 6. LOCAL BEAM
def random_restart_hill_climbing(start_state, goal_state, max_restart=10):
    best_path = []
    for i in range(max_restart):
        current_state = start_state if i == 0 else generate_random_state(start_state)
        path = [(current_state, f'Bắt đầu (Restart {i})' if i > 0 else None)]
        while True:
            if current_state == goal_state: return path
            current_value = -misplaced_tiles(current_state, goal_state)
            better_neighbors = [(n_s, a, -misplaced_tiles(n_s, goal_state)) for n_s, a in get_neighbors(current_state) if -misplaced_tiles(n_s, goal_state) > current_value]
            if not better_neighbors: break
            best_next = max(better_neighbors, key=lambda x: x[2])
            current_state = best_next[0]
            path.append((current_state, best_next[1]))
        best_path = path 
    return best_path 

def local_beam_search(start_state, goal_state, k=3):
    current_states_paths = [(start_state, [(start_state, None)])]
    for _ in range(k - 1):
        rand_state = generate_random_state(start_state)
        current_states_paths.append((rand_state, [(rand_state, 'Init Random Beam')]))
        
    while True:
        neighbor_states_pool = []
        for state, path in current_states_paths:
            if state == goal_state: return path 
            for next_state, action in get_neighbors(state):
                new_path = path + [(next_state, action)]
                if next_state == goal_state: return new_path
                value = -misplaced_tiles(next_state, goal_state)
                neighbor_states_pool.append((value, next_state, new_path))
                
        if not neighbor_states_pool: return current_states_paths[0][1] 
        neighbor_states_pool.sort(key=lambda x: x[0], reverse=True)
        
        next_states_paths = []
        seen = set()
        for val, state, path in neighbor_states_pool:
            if state not in seen:
                seen.add(state)
                next_states_paths.append((state, path))
            if len(next_states_paths) == k: break
        current_states_paths = next_states_paths

# =========================================================================
# CÁC THUẬT TOÁN TÌM KIẾM CƠ BẢN (TRUYỀN THỐNG)
# =========================================================================

# BFS (Breadth-First Search) - Theo Ảnh 2
def bfs_search(start_state, goal_state):
    start_node = Node(start_state)
    if start_state == goal_state:
        return get_path(start_node)
        
    frontier = deque([start_node]) # FIFO Queue
    frontier_states = {start_state}
    explored = set()
    
    while frontier:
        node = frontier.popleft() # REMOVE() từ đầu hàng đợi
        frontier_states.remove(node.state)
        explored.add(node.state)
        
        for next_state, action in get_neighbors(node.state):
            if next_state not in explored and next_state not in frontier_states:
                child = Node(next_state, parent=node, action=action)
                if next_state == goal_state: # GOAL-TEST trước khi đưa vào frontier
                    return get_path(child)
                frontier.append(child) # INSERT()
                frontier_states.add(next_state)
    return None

# DFS (Depth-First Search)
def dfs_search(start_state, goal_state):
    start_node = Node(start_state)
    if start_state == goal_state:
        return get_path(start_node)
        
    frontier = [start_node] # LIFO Stack
    frontier_states = {start_state}
    explored = set()
    
    while frontier:
        node = frontier.pop() # Lấy ở đỉnh Stack
        frontier_states.remove(node.state)
        
        if node.state == goal_state:
            return get_path(node)
            
        explored.add(node.state)
        
        for next_state, action in get_neighbors(node.state):
            if next_state not in explored and next_state not in frontier_states:
                child = Node(next_state, parent=node, action=action)
                frontier.append(child)
                frontier_states.add(next_state)
    return None

def greedy_search(start_state, goal_state):
    start_node = Node(start_state, h_cost=manhattan_distance(start_state, goal_state))
    start_node.f_cost = start_node.h_cost
    frontier_heap = [(start_node.f_cost, id(start_node), start_node)]
    frontier_dict = {start_state: start_node}
    reached_set = set()
    
    while frontier_heap:
        _, _, node = heapq.heappop(frontier_heap)
        if node.state not in frontier_dict or frontier_dict[node.state] != node: continue
        if node.state == goal_state: return get_path(node)
        del frontier_dict[node.state]
        reached_set.add(node.state)
        for m_state, action in get_neighbors(node.state):
            if m_state not in frontier_dict and m_state not in reached_set:
                child = Node(m_state, parent=node, action=action)
                child.h_cost = manhattan_distance(m_state, goal_state)
                child.f_cost = child.h_cost
                frontier_dict[m_state] = child
                heapq.heappush(frontier_heap, (child.f_cost, id(child), child))
    return None

def astar_search(start_state, goal_state):
    start_node = Node(start_state, g_cost=0, h_cost=manhattan_distance(start_state, goal_state))
    start_node.f_cost = start_node.g_cost + start_node.h_cost
    frontier_heap = [(start_node.f_cost, id(start_node), start_node)]
    frontier_dict = {start_state: start_node}
    reached_dict = {}
    
    while frontier_heap:
        _, _, node = heapq.heappop(frontier_heap)
        if node.state not in frontier_dict or frontier_dict[node.state] != node: continue
        if node.state == goal_state: return get_path(node)
        del frontier_dict[node.state]
        reached_dict[node.state] = node
        for m_state, action in get_neighbors(node.state):
            g_new = node.g_cost + 1
            in_reached = m_state in reached_dict
            in_frontier = m_state in frontier_dict
            if in_reached:
                if g_new >= reached_dict[m_state].g_cost: continue
                else:
                    del reached_dict[m_state]
                    in_reached = False
            if in_frontier:
                if g_new < frontier_dict[m_state].g_cost:
                    target_node = frontier_dict[m_state]
                    target_node.g_cost = g_new
                    target_node.f_cost = g_new + target_node.h_cost
                    target_node.parent = node
                    target_node.action = action
                    heapq.heappush(frontier_heap, (target_node.f_cost, id(target_node), target_node))
            if not in_frontier and not in_reached:
                child = Node(m_state, parent=node, action=action, g_cost=g_new)
                child.h_cost = manhattan_distance(m_state, goal_state)
                child.f_cost = child.g_cost + child.h_cost
                frontier_dict[m_state] = child
                heapq.heappush(frontier_heap, (child.f_cost, id(child), child))
    return None

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

# =========================================================================
# GIAO DIỆN GUI (TKINTER)
# =========================================================================
class PuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver: Tích hợp Đầy đủ (BFS, DFS, Local Search)")
        self.root.geometry("760x700") # Mở rộng cửa sổ để chứa khung Grid 3 cột nút bấm
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
            
        # Tổ chức lại lưới nút bấm: 3 CỘT X 4 HÀNG
        buttons_frame = tk.Frame(left_frame)
        buttons_frame.pack(pady=5)
        
        # Hàng 0: Uninformed Search (Cơ bản)
        self.btn_bfs = tk.Button(buttons_frame, text="BFS (Chiều rộng)", font=('Arial', 10), width=15, command=lambda: self.solve('bfs'))
        self.btn_bfs.grid(row=0, column=0, pady=3, padx=2)
        self.btn_dfs = tk.Button(buttons_frame, text="DFS (Chiều sâu)", font=('Arial', 10), width=15, command=lambda: self.solve('dfs'))
        self.btn_dfs.grid(row=0, column=1, pady=3, padx=2)
        self.btn_ids = tk.Button(buttons_frame, text="IDS (Sâu lặp)", font=('Arial', 10), width=15, command=lambda: self.solve('ids'))
        self.btn_ids.grid(row=0, column=2, pady=3, padx=2)
        
        # Hàng 1: Optimal & Heuristic 
        self.btn_ucs = tk.Button(buttons_frame, text="UCS Search", font=('Arial', 10), width=15, command=lambda: self.solve('ucs'))
        self.btn_ucs.grid(row=1, column=0, pady=3, padx=2)
        self.btn_greedy = tk.Button(buttons_frame, text="Greedy Search", font=('Arial', 10), width=15, bg="#f0e68c", command=lambda: self.solve('greedy'))
        self.btn_greedy.grid(row=1, column=1, pady=3, padx=2)
        self.btn_astar = tk.Button(buttons_frame, text="A* Search", font=('Arial', 10), width=15, bg="#98fb98", command=lambda: self.solve('astar'))
        self.btn_astar.grid(row=1, column=2, pady=3, padx=2)
        
        # Hàng 2: Local Search (Cơ bản)
        self.btn_hill = tk.Button(buttons_frame, text="Leo Đồi (First)", font=('Arial', 10, 'bold'), width=15, bg="#ffb6c1", command=lambda: self.solve('hill'))
        self.btn_hill.grid(row=2, column=0, pady=3, padx=2)
        self.btn_steepest = tk.Button(buttons_frame, text="Leo Đồi (Dốc nhất)", font=('Arial', 10, 'bold'), width=15, bg="#ffb6c1", command=lambda: self.solve('steepest'))
        self.btn_steepest.grid(row=2, column=1, pady=3, padx=2)
        self.btn_stochastic = tk.Button(buttons_frame, text="Stochastic Hill", font=('Arial', 10, 'bold'), width=15, bg="#ffb6c1", command=lambda: self.solve('stochastic'))
        self.btn_stochastic.grid(row=2, column=2, pady=3, padx=2)
        
        # Hàng 3: Local Search (Nâng cao)
        self.btn_restart = tk.Button(buttons_frame, text="Random-Restart", font=('Arial', 10, 'bold'), width=15, bg="#ffb6c1", command=lambda: self.solve('restart'))
        self.btn_restart.grid(row=3, column=0, pady=3, padx=2)
        self.btn_beam = tk.Button(buttons_frame, text="Local Beam Search", font=('Arial', 10, 'bold'), width=15, bg="#dda0dd", command=lambda: self.solve('beam'))
        self.btn_beam.grid(row=3, column=1, pady=3, padx=2)
        self.btn_sa = tk.Button(buttons_frame, text="Simulated Anneal", font=('Arial', 10, 'bold'), width=15, bg="#dda0dd", command=lambda: self.solve('sa'))
        self.btn_sa.grid(row=3, column=2, pady=3, padx=2)

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
        self.btn_bfs.config(state=btn_state)
        self.btn_dfs.config(state=btn_state)
        self.btn_ucs.config(state=btn_state)
        self.btn_ids.config(state=btn_state)
        self.btn_greedy.config(state=btn_state)
        self.btn_astar.config(state=btn_state)
        self.btn_hill.config(state=btn_state)
        self.btn_steepest.config(state=btn_state)
        self.btn_stochastic.config(state=btn_state)
        self.btn_restart.config(state=btn_state)
        self.btn_beam.config(state=btn_state)
        self.btn_sa.config(state=btn_state)

    def animate_solution(self, path, step=0):
        if step < len(path):
            state, action = path[step]
            self.update_board(state)
            log_text = "Bắt đầu: Trạng thái gốc" if action is None else (action if 'Init' in str(action) or 'Restart' in str(action) else f"Bước {step}: Ô trống sang {action}")
            self.move_listbox.insert(tk.END, log_text)
            self.move_listbox.see(tk.END) 
            self.status_lbl.config(text=f"Bước: {step}/{len(path)-1}")
            self.root.after(400, self.animate_solution, path, step + 1)
        else:
            if path[-1][0] == self.goal_state:
                self.status_lbl.config(text=f"Hoàn thành trong {len(path)-1} bước!", fg="green")
                self.move_listbox.insert(tk.END, "--- THÀNH CÔNG ---")
            else:
                self.status_lbl.config(text="Dừng tại Cực đại cục bộ (Kẹt)!", fg="orange")
                self.move_listbox.insert(tk.END, "--- KẸT / THẤT BẠI ---")
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
        
        if algo == 'bfs': path = bfs_search(self.current_state, self.goal_state)
        elif algo == 'dfs': 
            messagebox.showinfo("Cảnh báo DFS", "DFS có thể tạo ra đường đi vô cùng dài (hàng nghìn bước) trước khi tới đích, thời gian chạy có thể lâu nếu nhánh cây xấu.")
            path = dfs_search(self.current_state, self.goal_state)
        elif algo == 'ucs': path = ucs_search(self.current_state, self.goal_state)
        elif algo == 'ids': path = ids_search(self.current_state, self.goal_state)
        elif algo == 'greedy': path = greedy_search(self.current_state, self.goal_state)
        elif algo == 'astar': path = astar_search(self.current_state, self.goal_state)
        
        # Local Search
        elif algo == 'hill': path = simple_hill_climbing(self.current_state, self.goal_state)
        elif algo == 'steepest': path = steepest_ascent_hill_climbing(self.current_state, self.goal_state)
        elif algo == 'stochastic': path = stochastic_hill_climbing(self.current_state, self.goal_state)
        elif algo == 'restart': path = random_restart_hill_climbing(self.current_state, self.goal_state)
        elif algo == 'beam': path = local_beam_search(self.current_state, self.goal_state)
        elif algo == 'sa': path = simulated_annealing(self.current_state, self.goal_state)
            
        if path: self.animate_solution(path)
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy đường đi hoặc thuật toán bị kẹt ngay từ đầu!")
            self.status_lbl.config(text="Thất bại", fg="red")
            self.is_animating = False
            self.toggle_buttons(True)

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.mainloop()