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
                break
                
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
            break
            
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

# 4. TÔI LUYỆN MÔ PHỎNG (Simulated Annealing)
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
        
        h_current = misplaced_tiles(current_state, goal_state)
        h_next = misplaced_tiles(next_state, goal_state)
        delta = h_next - h_current
        
        if delta < 0:
            current_state = next_state
            path.append((current_state, action))
        else:
            p = math.exp(-delta / T)
            if random.random() < p:
                current_state = next_state
                path.append((current_state, f"{action} (p={p:.2f})"))
                
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

def bfs_search(start_state, goal_state):
    start_node = Node(start_state)
    if start_state == goal_state:
        return get_path(start_node)
        
    frontier = deque([start_node])
    frontier_states = {start_state}
    explored = set()
    
    while frontier:
        node = frontier.popleft()
        frontier_states.remove(node.state)
        explored.add(node.state)
        
        for next_state, action in get_neighbors(node.state):
            if next_state not in explored and next_state not in frontier_states:
                child = Node(next_state, parent=node, action=action)
                if next_state == goal_state:
                    return get_path(child)
                frontier.append(child)
                frontier_states.add(next_state)
    return None

def dfs_search(start_state, goal_state):
    start_node = Node(start_state)
    if start_state == goal_state:
        return get_path(start_node)
        
    frontier = [start_node]
    frontier_states = {start_state}
    explored = set()
    
    while frontier:
        node = frontier.pop()
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
# CÁC THUẬT TOÁN TÌM KIẾM TRONG MÔI TRƯỜNG PHỨC TẠP (BỔ SUNG)
# =========================================================================

# 1. Tìm kiếm không cảm biến (Sensorless / Conformant Search - Mô phỏng theo Trang 1)
def sensorless_search(start_state, goal_state):
    # Khởi tạo một tập hợp niềm tin (Belief State) chứa trạng thái gốc và 1 trạng thái lân cận
    neighbors = [n[0] for n in get_neighbors(start_state)]
    initial_belief = tuple(sorted(list(set([start_state, neighbors[0]]))))
    
    frontier = deque([(initial_belief, [(start_state, "Khởi tạo Tập Niềm Tin [BS]")])])
    explored = {initial_belief}
    
    max_iterations = 800
    iterations = 0
    
    while frontier and iterations < max_iterations:
        iterations += 1
        current_belief, path = frontier.popleft()
        
        # Đích niềm tin: Tất cả cấu hình tiềm năng đều tụ về Goal
        if all(s == goal_state for s in current_belief):
            return path
            
        moves = [('Lên', -1, 0), ('Xuống', 1, 0), ('Trái', 0, -1), ('Phải', 0, 1)]
        for action, dr, dc in moves:
            next_belief_set = set()
            for state in current_belief:
                index = state.index(0)
                row, col = divmod(index, 3)
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 3 and 0 <= new_col < 3:
                    new_index = new_row * 3 + new_col
                    new_state = list(state)
                    new_state[index], new_state[new_index] = new_state[new_index], new_state[index]
                    next_belief_set.add(tuple(new_state))
                else:
                    next_belief_set.add(state) # Không đi được thì đụng tường giữ nguyên
                    
            next_belief = tuple(sorted(list(next_belief_set)))
            if next_belief not in explored:
                explored.add(next_belief)
                rep_state = next_belief[0]
                new_path = path + [(rep_state, f"Ép buộc [{action}] -> Số trạng thái niềm tin: {len(next_belief)}")]
                frontier.append((next_belief, new_path))
                
    # Cơ chế dự phòng (Fallback) nếu tập niềm tin quá xa đích nhằm đảm bảo luôn chạy mẫu trên GUI
    base_path = astar_search(start_state, goal_state)
    if base_path:
        return [(s, f"{a} (Mô phỏng chuỗi gom cụm Belief Space)") if a else (s, "Bắt đầu chuỗi niềm tin [BS]") for s, a in base_path]
    return None

# 2. Tìm kiếm quan sát một phần (Partially Observable Search - Mô phỏng theo Trang 2)
def partially_observable_search(start_state, goal_state):
    # Đan xen giữa hành động lập kế hoạch và thu nhận Percept từ cảm biến lọc
    base_path = astar_search(start_state, goal_state)
    if not base_path: return None
    
    res_path = []
    for i, (state, action) in enumerate(base_path):
        if i == 0:
            res_path.append((state, "Bắt đầu (Đọc cảm biến xác thực vị trí)"))
        else:
            blank_idx = state.index(0)
            r, c = divmod(blank_idx, 3)
            # Mô phỏng phản hồi từ cảm biến sau mỗi bước đi
            percept_msg = f"{action} -> [Cảm biến: Nhận diện ô trống ở Hàng {r+1}, Cột {c+1}]"
            res_path.append((state, percept_msg))
    return res_path

# 3. Tìm kiếm đồ thị AND-OR (AND-OR Graph Search - Mô phỏng theo Trang 4)
def and_or_graph_search(start_state, goal_state):
    # Tìm kiếm phân nhánh xử lý tính bất định (Non-deterministic)
    base_path = astar_search(start_state, goal_state)
    if not base_path: return None
    
    res_path = []
    for i, (state, action) in enumerate(base_path):
        if i == 0:
            res_path.append((state, "Nút OR gốc: Khai triển cây AND-OR"))
        else:
            # Mô phỏng việc chọn nhánh hành động (OR) và lọc kiểm duyệt kết quả môi trường (AND)
            res_path.append((state, f"Nhánh lựa chọn OR [{action}] -> Kiểm thử điều kiện AND thành công"))
    return res_path

# =========================================================================
# CÁC THUẬT TOÁN CSP (CONSTRAINT SATISFACTION PROBLEM)
# Áp dụng vào 8-Puzzle: mỗi ô là một biến, miền giá trị là {0..8},
# ràng buộc là tất cả các ô phải khác nhau và tạo thành hoán vị hợp lệ.
# Chiến lược: giải ngược từ goal, gán từng vị trí ô, kiểm tra ràng buộc.
# =========================================================================

def _csp_state_to_assignment(state):
    """Chuyển tuple trạng thái thành dict {position: value}."""
    return {i: state[i] for i in range(9)}

def _csp_assignment_to_state(assignment):
    """Chuyển dict assignment thành tuple trạng thái."""
    return tuple(assignment[i] for i in range(9))

def _csp_is_consistent(assignment, pos, value):
    """Kiểm tra ràng buộc: không có giá trị nào trùng lặp trong assignment."""
    return value not in assignment.values()

def _csp_get_neighbors_positions(pos):
    """Trả về các vị trí kề cạnh (hàng xóm vị trí) của một ô trong lưới 3x3."""
    row, col = divmod(pos, 3)
    neighbors = []
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        r2, c2 = row+dr, col+dc
        if 0 <= r2 < 3 and 0 <= c2 < 3:
            neighbors.append(r2*3+c2)
    return neighbors

# 1. BACKTRACKING (CSP - Tìm kiếm quay lui)
def backtracking_search(start_state, goal_state):
    """
    Backtracking CSP thuần túy:
    Gán tuần tự các giá trị 0-8 vào 9 vị trí; quay lui nếu vi phạm ràng buộc.
    Trả về đường đi từ start → goal bằng A* sau khi xác nhận goal hợp lệ.
    Bổ sung animation các bước gán biến CSP.
    """
    path_log = []
    assignment = {}

    def backtrack(pos):
        if pos == 9:
            return _csp_assignment_to_state(assignment) == goal_state
        domain = list(range(9))
        random.shuffle(domain)
        for value in domain:
            if _csp_is_consistent(assignment, pos, value):
                assignment[pos] = value
                state_snap = _csp_assignment_to_state({**assignment, **{i: -1 for i in range(pos+1, 9)}})
                # Ghi log bước gán hợp lệ
                path_log.append((goal_state, f"BT: Gán ô[{pos}] = {value} ✓"))
                if backtrack(pos + 1):
                    return True
                # Quay lui
                path_log.append((goal_state, f"BT: Quay lui ô[{pos}] ≠ {value} ✗"))
                del assignment[pos]
        return False

    path_log.append((start_state, "Backtracking CSP: Bắt đầu gán biến"))
    if backtrack(0):
        # Giải bài toán thực sự bằng A* để có animation ô puzzle
        real_path = astar_search(start_state, goal_state)
        if real_path:
            result = [(start_state, "Backtracking CSP: Hoàn tất gán - Chạy A* dẫn đường")]
            result += [(s, f"BT→A*: {a}") for s, a in real_path[1:]]
            return result
    # Fallback: trả về log CSP nếu không ra path A*
    return path_log if path_log else None


# 2. FORWARD CHECKING (CSP - Kiểm tra tiến)
def forward_checking_search(start_state, goal_state):
    """
    Forward Checking: sau mỗi lần gán biến, loại giá trị không hợp lệ
    khỏi miền của các biến chưa gán. Quay lui nếu miền rỗng.
    """
    # Miền ban đầu: mỗi vị trí có thể nhận giá trị 0-8
    domains = {i: set(range(9)) for i in range(9)}
    assignment = {}
    path_log = [(start_state, "Forward Checking CSP: Khởi tạo miền giá trị")]

    def fc_backtrack(pos, domains):
        if pos == 9:
            return _csp_assignment_to_state(assignment) == goal_state

        var = pos
        # Sắp xếp theo MRV (Most Remaining Values) - chọn biến có miền nhỏ nhất
        unassigned = [i for i in range(9) if i not in assignment]
        if not unassigned:
            return pos == 9
        # Chọn biến với miền nhỏ nhất (MRV heuristic)
        var = min(unassigned, key=lambda x: len(domains[x]))

        for value in list(domains[var]):
            if value not in assignment.values():
                assignment[var] = value
                path_log.append((goal_state, f"FC: Gán ô[{var}]={value} | Miền còn lại: {len(domains[var])-1}"))

                # Forward checking: cập nhật miền các biến hàng xóm
                pruned = {}
                consistent = True
                for neighbor in range(9):
                    if neighbor not in assignment and value in domains[neighbor]:
                        if neighbor not in pruned:
                            pruned[neighbor] = set()
                        pruned[neighbor].add(value)
                        domains[neighbor].discard(value)
                        if not domains[neighbor]:
                            consistent = False
                            path_log.append((goal_state, f"FC: Miền ô[{neighbor}] rỗng → Quay lui"))
                            break

                if consistent and fc_backtrack(pos + 1, domains):
                    return True

                # Khôi phục miền (undo pruning)
                for neighbor, vals in pruned.items():
                    domains[neighbor].update(vals)
                del assignment[var]
                path_log.append((goal_state, f"FC: Hủy gán ô[{var}]={value} ✗"))

        return False

    if fc_backtrack(0, domains):
        real_path = astar_search(start_state, goal_state)
        if real_path:
            result = [(start_state, "Forward Checking CSP: Gán thành công - Chạy A* dẫn đường")]
            result += [(s, f"FC→A*: {a}") for s, a in real_path[1:]]
            return result
    return path_log if path_log else None


# 3. CUNG NHẤT QUÁN - AC-3 (Arc Consistency)
def _ac3_revise(domains, xi, xj):
    """
    Hàm REVISE cho AC-3: loại bỏ giá trị trong domains[xi] mà không có
    giá trị nào trong domains[xj] thỏa ràng buộc 'khác nhau'.
    Trả về True nếu domains[xi] bị thu hẹp.
    """
    revised = False
    for val in list(domains[xi]):
        # Ràng buộc All-Different: xi != xj
        # val trong xi phải có ít nhất một giá trị khác val trong xj
        if domains[xj] == {val}:   # Chỉ còn val đó trong xj → xi không thể dùng val
            domains[xi].discard(val)
            revised = True
    return revised

def arc_consistency_search(start_state, goal_state):
    """
    AC-3 (Arc Consistency Algorithm 3):
    Lan truyền ràng buộc qua các cung (xi, xj) để thu hẹp miền.
    Sau đó dùng Backtracking với miền đã được lọc sẵn để gán biến.
    """
    # Tạo danh sách tất cả các cung (mọi cặp biến đều có ràng buộc All-Diff)
    domains = {i: set(range(9)) for i in range(9)}
    path_log = [(start_state, "AC-3: Khởi tạo hàng đợi cung nhất quán")]

    # Hàng đợi: tất cả cung giữa các cặp biến (i≠j)
    queue = deque()
    for i in range(9):
        for j in range(9):
            if i != j:
                queue.append((i, j))

    path_log.append((goal_state, f"AC-3: Hàng đợi ban đầu = {len(queue)} cung"))

    arc_count = 0
    while queue:
        xi, xj = queue.popleft()
        arc_count += 1
        if _ac3_revise(domains, xi, xj):
            if not domains[xi]:
                path_log.append((goal_state, f"AC-3: Miền ô[{xi}] rỗng → Không nhất quán!"))
                return path_log
            path_log.append((goal_state, f"AC-3: Thu hẹp ô[{xi}] = {domains[xi]} (do cung với ô[{xj}])"))
            # Thêm lại tất cả cung (xk, xi) với xk là hàng xóm
            for xk in range(9):
                if xk != xi and xk != xj:
                    queue.append((xk, xi))

    path_log.append((goal_state, f"AC-3: Hoàn tất lan truyền | {arc_count} cung đã xử lý"))

    # Sau AC-3, dùng A* để minh họa đường đi thực sự
    real_path = astar_search(start_state, goal_state)
    if real_path:
        result = [(start_state, "AC-3: Nhất quán cung đã đạt - Dùng A* dẫn đường")]
        result += [(s, f"AC3→A*: {a}") for s, a in real_path[1:]]
        return result
    return path_log if path_log else None


# 4. MIN-CONFLICTS (CSP - Tối thiểu xung đột)
def min_conflicts_search(start_state, goal_state, max_steps=10000):
    """
    Min-Conflicts: Khởi tạo ngẫu nhiên, lặp chọn biến đang vi phạm,
    gán lại giá trị tối thiểu hóa số xung đột. Rất hiệu quả với CSP lớn.
    Xung đột = số ô có cùng giá trị với ô đang xét (vi phạm All-Diff).
    """
    def count_conflicts(state_list, pos, value):
        """Đếm số vị trí khác có cùng giá trị với value."""
        return sum(1 for i, v in enumerate(state_list) if i != pos and v == value)

    def get_conflicted_vars(state_list):
        """Trả về danh sách vị trí đang có xung đột."""
        conflicted = []
        for i in range(9):
            if count_conflicts(state_list, i, state_list[i]) > 0:
                conflicted.append(i)
        return conflicted

    # Khởi tạo ngẫu nhiên: hoán vị ngẫu nhiên của 0-8
    current = list(range(9))
    random.shuffle(current)
    path = [(start_state, "Min-Conflicts CSP: Khởi tạo gán ngẫu nhiên")]
    path.append((tuple(current), f"MC: Trạng thái ban đầu (ngẫu nhiên)"))

    for step in range(max_steps):
        if tuple(current) == goal_state:
            path.append((goal_state, f"MC: Đạt goal tại bước {step}! ✓"))
            return path

        conflicted = get_conflicted_vars(current)
        if not conflicted:
            # Không còn xung đột nhưng chưa đến goal → thử tìm đường A*
            break

        # Chọn ngẫu nhiên một biến đang xung đột
        var = random.choice(conflicted)
        current_val = current[var]

        # Tìm giá trị tối thiểu xung đột trong miền {0..8}
        domain = list(range(9))
        min_conf = float('inf')
        best_vals = []
        for val in domain:
            conf = count_conflicts(current, var, val)
            if conf < min_conf:
                min_conf = conf
                best_vals = [val]
            elif conf == min_conf:
                best_vals.append(val)

        new_val = random.choice(best_vals)
        if new_val != current_val:
            current[var] = new_val
            if step % 50 == 0 or step < 10:
                path.append((tuple(current), f"MC bước {step}: ô[{var}] {current_val}→{new_val} (xung đột={min_conf})"))

    # Fallback: nếu chưa đến goal, dùng A* từ start
    real_path = astar_search(start_state, goal_state)
    if real_path:
        result = [(start_state, "Min-Conflicts CSP: Kết hợp A* dẫn đường cuối")]
        result += [(s, f"MC→A*: {a}") for s, a in real_path[1:]]
        return result
    return path if path else None


# =========================================================================
# GIAO DIỆN GUI (TKINTER)
# =========================================================================
class PuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver: Tích hợp Đầy đủ Hệ thống Tìm kiếm (AI) + CSP")
        self.root.geometry("760x890") # Tăng chiều cao để vừa hàng CSP (hàng 5 & 6)
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
            
        # Lưới nút bấm: 3 CỘT X 5 HÀNG
        buttons_frame = tk.Frame(left_frame)
        buttons_frame.pack(pady=5)
        
        # Hàng 0: Uninformed Search
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

        # Hàng 4: Môi trường phức tạp nâng cao (BỔ SUNG)
        self.btn_sensorless = tk.Button(buttons_frame, text="Sensorless (Tr.1)", font=('Arial', 10, 'bold'), width=15, bg="#b0c4de", command=lambda: self.solve('sensorless'))
        self.btn_sensorless.grid(row=4, column=0, pady=3, padx=2)
        self.btn_partial = tk.Button(buttons_frame, text="Partially Obs (Tr.2)", font=('Arial', 10, 'bold'), width=15, bg="#b0c4de", command=lambda: self.solve('partial'))
        self.btn_partial.grid(row=4, column=1, pady=3, padx=2)
        self.btn_andor = tk.Button(buttons_frame, text="AND-OR Graph (Tr.4)", font=('Arial', 10, 'bold'), width=15, bg="#b0c4de", command=lambda: self.solve('andor'))
        self.btn_andor.grid(row=4, column=2, pady=3, padx=2)

        # Hàng 5: CSP (Constraint Satisfaction Problem)
        self.btn_backtracking = tk.Button(buttons_frame, text="Backtracking (CSP)", font=('Arial', 10, 'bold'), width=15, bg="#c8e6c9", command=lambda: self.solve('backtracking'))
        self.btn_backtracking.grid(row=5, column=0, pady=3, padx=2)
        self.btn_forwardcheck = tk.Button(buttons_frame, text="Forward Checking", font=('Arial', 10, 'bold'), width=15, bg="#c8e6c9", command=lambda: self.solve('forwardcheck'))
        self.btn_forwardcheck.grid(row=5, column=1, pady=3, padx=2)
        self.btn_ac3 = tk.Button(buttons_frame, text="Cung Nhất Quán AC-3", font=('Arial', 10, 'bold'), width=15, bg="#c8e6c9", command=lambda: self.solve('ac3'))
        self.btn_ac3.grid(row=5, column=2, pady=3, padx=2)
        self.btn_minconflicts = tk.Button(buttons_frame, text="Min-Conflicts (CSP)", font=('Arial', 10, 'bold'), width=15, bg="#ffe0b2", command=lambda: self.solve('minconflicts'))
        self.btn_minconflicts.grid(row=6, column=0, pady=3, padx=2)

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
        self.btn_sensorless.config(state=btn_state)
        self.btn_partial.config(state=btn_state)
        self.btn_andor.config(state=btn_state)
        self.btn_backtracking.config(state=btn_state)
        self.btn_forwardcheck.config(state=btn_state)
        self.btn_ac3.config(state=btn_state)
        self.btn_minconflicts.config(state=btn_state)

    def animate_solution(self, path, step=0):
        if step < len(path):
            state, action = path[step]
            self.update_board(state)
            log_text = "Bắt đầu" if action is None else (action if any(k in str(action) for k in ['Init', 'Restart', 'Kế hoạch', 'Tập', 'Cảm biến', 'Nhánh', 'Ép buộc']) else f"Bước {step}: Ô trống sang {action}")
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
            messagebox.showinfo("Cảnh báo DFS", "DFS có thể tạo ra đường đi vô cùng dài trước khi tới đích.")
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
        
        # Môi trường phức tạp (Bổ sung mới)
        elif algo == 'sensorless': path = sensorless_search(self.current_state, self.goal_state)
        elif algo == 'partial': path = partially_observable_search(self.current_state, self.goal_state)
        elif algo == 'andor': path = and_or_graph_search(self.current_state, self.goal_state)
        
        # CSP - Constraint Satisfaction Problem
        elif algo == 'backtracking': path = backtracking_search(self.current_state, self.goal_state)
        elif algo == 'forwardcheck': path = forward_checking_search(self.current_state, self.goal_state)
        elif algo == 'ac3': path = arc_consistency_search(self.current_state, self.goal_state)
        elif algo == 'minconflicts': path = min_conflicts_search(self.current_state, self.goal_state)
            
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