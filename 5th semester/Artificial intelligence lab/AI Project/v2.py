import tkinter as tk
from tkinter import PhotoImage
import random
import time
from collections import deque

from PIL import Image, ImageTk

# Constants
GRID_SIZE = 10  # Default grid size
CELL_SIZE = 50  # Each cell is 50x50 pixels
OBSTACLE_COUNT = 25  # Number of obstacles

# Game variables
player_pos = [0, 0]
goal_pos = [random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)]
obstacles = []
start_time = None
game_mode = "manual"  # Default game mode

# Create main window
window = tk.Tk()
window.title("Treasure Hunting Game")
window.geometry(f"{GRID_SIZE * CELL_SIZE + 200}x{GRID_SIZE * CELL_SIZE + 50}")

# Load and resize images
hunter_img_raw = Image.open("hunter.png").resize((CELL_SIZE, CELL_SIZE), Image.Resampling.LANCZOS)
gold_img_raw = Image.open("gold.png").resize((CELL_SIZE, CELL_SIZE), Image.Resampling.LANCZOS)
obstacle_img_raw = Image.open("rock.png").resize((CELL_SIZE, CELL_SIZE), Image.Resampling.LANCZOS)
# Convert to PhotoImage for Tkinter
hunter_img = ImageTk.PhotoImage(hunter_img_raw)
gold_img = ImageTk.PhotoImage(gold_img_raw)
obstacle_img = ImageTk.PhotoImage(obstacle_img_raw)
# Function to generate obstacles
def generate_obstacles():
    global obstacles
    obstacles = []
    while len(obstacles) < OBSTACLE_COUNT:
        x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
        if [x, y] != player_pos and [x, y] != goal_pos:
            obstacles.append([x, y])

# Function to draw the grid
def draw_grid(canvas):
    canvas.delete("all")
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x1, y1 = col * CELL_SIZE, row * CELL_SIZE
            x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
            if [row, col] == player_pos:
                canvas.create_image(x1 + CELL_SIZE // 2, y1 + CELL_SIZE // 2, image=hunter_img)
            elif [row, col] == goal_pos:
                canvas.create_image(x1 + CELL_SIZE // 2, y1 + CELL_SIZE // 2, image=gold_img)
            elif [row, col] in obstacles:
                canvas.create_image(x1 + CELL_SIZE // 2, y1 + CELL_SIZE // 2, image=obstacle_img)
            else:
                canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")

# BFS pathfinding function
def bfs(start, goal):
    queue = deque([start])
    came_from = {tuple(start): None}
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        current = queue.popleft()
        if current == goal:
            path = []
            while current:
                path.append(current)
                current = came_from[tuple(current)]
            return path[::-1]
        for dx, dy in directions:
            neighbor = [current[0] + dx, current[1] + dy]
            if (0 <= neighbor[0] < GRID_SIZE and 0 <= neighbor[1] < GRID_SIZE and
                neighbor not in obstacles and tuple(neighbor) not in came_from):
                queue.append(neighbor)
                came_from[tuple(neighbor)] = current
    return None  # No path found

# Function to auto-move the player
def auto_move(canvas):
    path = bfs(player_pos, goal_pos)
    if not path:
        print("No path to the goal!")
        return

    def step():
        nonlocal path
        if len(path) > 1:
            next_pos = path.pop(1)
            player_pos[0], player_pos[1] = next_pos
            draw_grid(canvas)
            if player_pos == goal_pos:
                show_victory()
            else:
                window.after(200, step)

    step()

# Handle manual player movement
def move_player(canvas, dx, dy):
    new_x, new_y = player_pos[0] + dx, player_pos[1] + dy
    if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and [new_x, new_y] not in obstacles:
        player_pos[0], player_pos[1] = new_x, new_y
        draw_grid(canvas)
        if player_pos == goal_pos:
            show_victory()

# Show victory screen
def show_victory():
    for widget in window.winfo_children():
        widget.destroy()
    
    victory_frame = tk.Frame(window, bg="green")
    victory_frame.pack(expand=True, fill="both")
    
    elapsed_time = time_elapsed()
    tk.Label(victory_frame, text="You Win!", font=("Arial", 36), bg="green", fg="white").pack(pady=20)
    tk.Label(victory_frame, text=f"Time: {elapsed_time} seconds", font=("Arial", 24), bg="green", fg="white").pack(pady=10)
    
    tk.Button(victory_frame, text="Play Again", font=("Arial", 16), command=lambda: [victory_frame.destroy(), start_game(game_mode)]).pack(pady=10)
    tk.Button(victory_frame, text="Go to Home Screen", font=("Arial", 16), command=lambda: [victory_frame.destroy(), show_start_screen()]).pack(pady=10)

# Start the timer
def start_timer(label):
    global start_time
    start_time = time.time()  # Start time in seconds
    update_timer(label)

# Update the timer
def update_timer(label):
    elapsed = time_elapsed()
    label.config(text=f"Time: {elapsed} seconds")
    window.after(100, update_timer, label)  # Update timer every 100ms

# Calculate elapsed time
def time_elapsed():
    return round(time.time() - start_time)

# Start the game
def start_game(mode):
    global game_mode, player_pos, goal_pos
    game_mode = mode
    player_pos = [0, 0]
    goal_pos = [random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)]
    generate_obstacles()

    # Setup game frame
    for widget in window.winfo_children():
        widget.destroy()
    
    game_frame = tk.Frame(window, bg="black")
    game_frame.pack()
    canvas = tk.Canvas(game_frame, width=GRID_SIZE * CELL_SIZE, height=GRID_SIZE * CELL_SIZE, bg="white")
    canvas.pack()
    draw_grid(canvas)

    # Timer label
    timer_label = tk.Label(game_frame, text="Time: 0 seconds", font=("Arial", 16), bg="black", fg="white")
    timer_label.pack()
    start_timer(timer_label)

    # Bind manual controls
    def key_press(event):
        if game_mode == "manual":
            if event.keysym == "Up":
                move_player(canvas, -1, 0)
            elif event.keysym == "Down":
                move_player(canvas, 1, 0)
            elif event.keysym == "Left":
                move_player(canvas, 0, -1)
            elif event.keysym == "Right":
                move_player(canvas, 0, 1)

    window.bind("<KeyPress>", key_press)

    # Auto-move for AI mode
    if game_mode == "auto":
        auto_move(canvas)

# Show the start screen
def show_start_screen():
    for widget in window.winfo_children():
        widget.destroy()
    
    start_frame = tk.Frame(window, bg="blue")
    start_frame.pack(expand=True, fill="both")
    
    tk.Label(start_frame, text="Treasure Hunting Game", font=("Arial", 36), bg="blue", fg="white").pack(pady=20)
    tk.Button(start_frame, text="Play Manually", font=("Arial", 16), command=lambda: [start_frame.destroy(), start_game("manual")]).pack(pady=10)
    tk.Button(start_frame, text="Auto Play with AI", font=("Arial", 16), command=lambda: [start_frame.destroy(), start_game("auto")]).pack(pady=10)
    tk.Button(start_frame, text="Quit", font=("Arial", 16), command=window.destroy).pack(pady=10)

# Initialize the game
show_start_screen()
window.mainloop()
