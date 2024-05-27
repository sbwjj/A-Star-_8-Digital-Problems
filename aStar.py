import heapq  # 导入heapq模块，用于优先队列操作
import random  # 导入random模块，用于生成随机棋盘
import tkinter as tk  # 导入tkinter模块，用于GUI
from tkinter import messagebox  # 从tkinter导入messagebox，用于显示信息
import threading  # 导入threading模块，用于多线程

class PuzzleState:
    def __init__(self, board, parent=None, move="", depth=0, cost=0):
        # 初始化拼图状态
        self.board = board  # 当前棋盘状态
        self.parent = parent  # 父节点状态
        self.move = move  # 移动操作
        self.depth = depth  # 当前深度
        self.cost = cost  # 当前代价

    def __lt__(self, other):
        # 重载小于运算符，用于优先队列比较
        return (self.cost + self.heuristic()) < (other.cost + other.heuristic())

    def heuristic(self):
        # 计算启发式函数（曼哈顿距离）
        distance = 0
        for i in range(3):
            for j in range(3):
                if self.board[i][j] != 0:
                    x, y = divmod(self.board[i][j] - 1, 3)
                    distance += abs(x - i) + abs(y - j)
        return distance

    def is_goal(self):
        # 判断是否为目标状态
        return self.board == goal_board

    def get_neighbors(self):
        # 获取邻居节点
        neighbors = []
        x, y = [(i, j) for i in range(3) for j in range(3) if self.board[i][j] == 0][0]
        directions = {'L': (0, 1), 'R': (0, -1), 'U': (1, 0), 'D': (-1, 0)}
        for move, (dx, dy) in directions.items():
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                new_board = [row[:] for row in self.board]
                new_board[x][y], new_board[nx][ny] = new_board[nx][ny], new_board[x][y]
                neighbors.append(PuzzleState(new_board, self, move, self.depth + 1))
        return neighbors


def a_star_search(initial_state):
    # A* 搜索算法
    open_list = []  # 初始化OPEN表
    closed_list = set()  # 初始化CLOSED表
    open_states = {}  # 存储OPEN表中的状态
    closed_states = {}  # 存储CLOSED表中的状态

    heapq.heappush(open_list, initial_state)  # 将初始状态加入OPEN表
    open_states[tuple(map(tuple, initial_state.board))] = initial_state  # 存储初始状态

    while open_list:
        current = heapq.heappop(open_list)  # 从OPEN表中取出代价最小的节点
        del open_states[tuple(map(tuple, current.board))]
        closed_states[tuple(map(tuple, current.board))] = current

        if current.is_goal():
            return current, open_states, closed_states  # 如果是目标状态，返回结果

        closed_list.add(tuple(map(tuple, current.board)))

        for neighbor in current.get_neighbors():
            if tuple(map(tuple, neighbor.board)) not in closed_list:
                if tuple(map(tuple, neighbor.board)) not in open_states:
                    heapq.heappush(open_list, neighbor)
                    open_states[tuple(map(tuple, neighbor.board))] = neighbor
    return None, open_states, closed_states


def generate_puzzle():
    # 生成随机可解的拼图
    nums = list(range(9))
    while True:
        random.shuffle(nums)
        board = [nums[:3], nums[3:6], nums[6:]]
        if is_solvable(board):
            return board


def is_solvable(board):
    # 判断拼图是否有解
    inversion_count = 0
    nums = [num for row in board for num in row if num != 0]
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] > nums[j]:
                inversion_count += 1
    return inversion_count % 2 == 0


class PuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.initial_state = None
        self.solved_path = []
        self.is_paused = False
        self.steps_taken = 0
        self.open_states = {}
        self.closed_states = {}

        self.frame = tk.Frame(root)
        self.frame.grid(row=1, column=0, padx=10, pady=10)
        self.tiles = [[None for _ in range(3)] for _ in range(3)]

        self.target_frame = tk.Frame(root)
        self.target_frame.grid(row=1, column=1, padx=10, pady=10)
        self.target_tiles = [[None for _ in range(3)] for _ in range(3)]
        self.create_grid(goal_board, self.target_tiles, self.target_frame)

        self.label_initial = tk.Label(root, text="Initial State")
        self.label_initial.grid(row=0, column=0)
        self.label_goal = tk.Label(root, text="Goal State")
        self.label_goal.grid(row=0, column=1)

        self.solve_button = tk.Button(root, text="Solve", command=self.solve_puzzle, state=tk.DISABLED)
        self.solve_button.grid(row=2, column=0, columnspan=2)

        self.pause_button = tk.Button(root, text="Pause", command=self.pause_puzzle, state=tk.DISABLED)
        self.pause_button.grid(row=3, column=0, columnspan=2)

        self.init_button = tk.Button(root, text="Initialize", command=self.initialize)
        self.init_button.grid(row=4, column=0, columnspan=2)

        self.show_button = tk.Button(root, text="Show OPEN/CLOSED", command=self.show_result, state=tk.DISABLED)
        self.show_button.grid(row=5, column=0, columnspan=2)

    def initialize(self):
        # 初始化新的拼图
        initial_board = generate_puzzle()
        self.initial_state = PuzzleState(initial_board)
        self.create_grid(self.initial_state.board)
        self.solve_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.show_button.config(state=tk.DISABLED)

    def create_grid(self, board, tiles=None, frame=None):
        # 创建棋盘网格
        if tiles is None:
            tiles = self.tiles
        if frame is None:
            frame = self.frame
        for i in range(3):
            for j in range(3):
                tile_value = board[i][j]
                tiles[i][j] = tk.Label(frame, text=str(tile_value), font=("Helvetica", 32), width=4, height=2)
                tiles[i][j].grid(row=i, column=j)
                if tile_value == 0:
                    tiles[i][j].config(bg="black")

    def update_grid(self, state):
        # 更新棋盘网格
        for i in range(3):
            for j in range(3):
                tile_value = state.board[i][j]
                self.tiles[i][j].config(text=str(tile_value))
                self.tiles[i][j].config(bg="SystemButtonFace" if tile_value != 0 else "black")
        self.frame.update()

    def solve_puzzle(self):
        # 开始求解拼图
        self.solve_button.config(state=tk.DISABLED)
        self.init_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.show_button.config(state=tk.DISABLED)
        self.steps_taken = 0
        threading.Thread(target=self.solve_puzzle_thread).start()

    def pause_puzzle(self):
        # 暂停或恢复求解
        if self.is_paused:
            self.is_paused = False
            self.pause_button.config(text="Pause")
            self.show_solution(self.solved_path)
        else:
            self.is_paused = True
            self.pause_button.config(text="Resume")

    def solve_puzzle_thread(self):
        # 求解拼图的线程
        solution, open_states, closed_states = a_star_search(self.initial_state)
        if not solution:
            messagebox.showinfo("Result", "No solution found!")
            self.solve_button.config(state=tk.NORMAL)
            self.init_button.config(state=tk.NORMAL)
            return

        path = []
        while solution:
            path.append(solution)
            solution = solution.parent
        path.reverse()

        self.solved_path = path
        self.open_states = open_states
        self.closed_states = closed_states
        self.show_solution(path)

    def show_solution(self, path):
        # 显示求解路径
        if not self.is_paused and path:
            state = path.pop(0)
            self.update_grid(state)
            self.steps_taken += 1
            self.root.after(500, self.show_solution, path)
        elif not path:
            self.show_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.solve_button.config(state=tk.NORMAL)
            self.init_button.config(state=tk.NORMAL)
            self.show_result()

    def show_result(self):
        # 显示结果窗口
        result_window = tk.Toplevel(self.root)
        result_window.title("Result")

        steps_label = tk.Label(result_window, text=f"Puzzle Solved! Total steps taken: {self.steps_taken}")
        steps_label.pack()

        open_label = tk.Label(result_window, text="OPEN List:")
        open_label.pack()
        open_listbox = tk.Listbox(result_window, width=50, height=10, font=("Courier", 12))
        for state in self.open_states.values():
            open_listbox.insert(tk.END, self.board_to_string(state.board))
            open_listbox.insert(tk.END, "-" * 30)
        open_listbox.pack(fill=tk.BOTH, expand=1)

        closed_label = tk.Label(result_window, text="CLOSED List:")
        closed_label.pack()
        closed_listbox = tk.Listbox(result_window, width=50, height=10, font=("Courier", 12))
        for state in self.closed_states.values():
            closed_listbox.insert(tk.END, self.board_to_string(state.board))
            closed_listbox.insert(tk.END, "-" * 30)
        closed_listbox.pack(fill=tk.BOTH, expand=1)

    def board_to_string(self, board):
        # 将棋盘状态转换为字符串
        return "\n".join(
            [" ".join(map(str, row[:3])) + " # " + " ".join(map(str, row[3:6])) + " # " + " ".join(map(str, row[6:]))
             for row in board]).strip(" #")


goal_board = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]  # 目标棋盘状态

root = tk.Tk()
root.title("8-Puzzle Solver")
gui = PuzzleGUI(root)
root.mainloop()
