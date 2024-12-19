import tkinter as tk
from tkinter import PhotoImage
import random
import time
from PIL import Image, ImageTk
from heapq import heappush, heappop

# Constants
GRID_SIZE = 10  # Default grid size
CELL_SIZE = 50  # Each cell is 50x50 pixels
OBSTACLE_COUNT = 25  # Number of obstacles
TIME_LIMIT = 60  # Time limit in seconds

# Game variables
player_pos = [0, 0]
goal_pos = [random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)]
obstacles = []
start_time = None
game_mode = "manual"  # Default game mode
game_over = False  # Flag to track if the game is over

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

# A* pathfinding function
def astar(start, goal):
    open_list = []
    heappush(open_list, (0, start))  # (priority, position)
    came_from = {tuple(start): None}
    g_score = {tuple(start): 0}  # Cost from start to current node

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance

    while open_list:
        _, current = heappop(open_list)

        if current == goal:
            path = []
            while current:
                path.append(current)
                current = came_from[tuple(current)]
            return path[::-1]

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            neighbor = [current[0] + dx, current[1] + dy]
            if 0 <= neighbor[0] < GRID_SIZE and 0 <= neighbor[1] < GRID_SIZE and neighbor not in obstacles:
                tentative_g_score = g_score[tuple(current)] + 1

                if tuple(neighbor) not in g_score or tentative_g_score < g_score[tuple(neighbor)]:
                    g_score[tuple(neighbor)] = tentative_g_score
                    f_score = tentative_g_score + heuristic(neighbor, goal)
                    heappush(open_list, (f_score, neighbor))
                    came_from[tuple(neighbor)] = current

    return None  # No path found

# Function to auto-move the player
def auto_move(canvas):
    path = astar(player_pos, goal_pos)
    if not path:
        show_nopath()
        return

    def step():
        nonlocal path
        if len(path) > 1:
            next_pos = path.pop(1)
            player_pos[0], player_pos[1] = next_pos
            draw_grid(canvas)
            if player_pos == goal_pos:
                show_victory()
            elif game_over:
                return  # Stop moving if game is over
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
    global game_over
    game_over = True
    for widget in window.winfo_children():
        widget.destroy()

    victory_frame = tk.Frame(window, bg="green")
    victory_frame.pack(expand=True, fill="both")

    elapsed_time = time_elapsed()
    tk.Label(victory_frame, text="You Win!", font=("Arial", 36), bg="green", fg="white").pack(pady=20)
    tk.Label(victory_frame, text=f"Time: {elapsed_time} seconds", font=("Arial", 24), bg="green", fg="white").pack(pady=10)

    tk.Button(victory_frame, text="Play Again", font=("Arial", 16), command=lambda: [victory_frame.destroy(), start_game(game_mode)]).pack(pady=10)
    tk.Button(victory_frame, text="Go to Home Screen", font=("Arial", 16), command=lambda: [victory_frame.destroy(), show_start_screen()]).pack(pady=10)

# Show no path screen
def show_nopath():
    global game_over
    game_over = True
    for widget in window.winfo_children():
        widget.destroy()

    loss_frame = tk.Frame(window, bg="red")
    loss_frame.pack(expand=True, fill="both")

    tk.Label(loss_frame, text="NO Path Found!", font=("Arial", 36), bg="red", fg="white").pack(pady=20)

    tk.Button(loss_frame, text="Play Again", font=("Arial", 16), command=lambda: [loss_frame.destroy(), start_game(game_mode)]).pack(pady=10)
    tk.Button(loss_frame, text="Go to Home Screen", font=("Arial", 16), command=lambda: [loss_frame.destroy(), show_start_screen()]).pack(pady=10)

# Timer functions
def start_timer(label):
    global start_time
    start_time = time.time()
    update_timer(label)

def update_timer(label):
    elapsed = time_elapsed()
    label.config(text=f"Time: {elapsed} seconds")

    if elapsed >= TIME_LIMIT:
        show_loss()
        return

    window.after(100, update_timer, label)

def time_elapsed():
    return round(time.time() - start_time)

# Start the game
def start_game(mode):
    global game_mode, player_pos, goal_pos, game_over
    game_mode = mode
    player_pos = [0, 0]
    goal_pos = [random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)]
    generate_obstacles()
    game_over = False

    for widget in window.winfo_children():
        widget.destroy()

    game_frame = tk.Frame(window, bg="black")
    game_frame.pack()
    canvas = tk.Canvas(game_frame, width=GRID_SIZE * CELL_SIZE, height=GRID_SIZE * CELL_SIZE, bg="white")
    canvas.pack()
    draw_grid(canvas)

    timer_label = tk.Label(game_frame, text="Time: 0 seconds", font=("Arial", 16), bg="black", fg="white")
    timer_label.pack()
    start_timer(timer_label)

    def key_press(event):
        if game_mode == "manual" and not game_over:
            if event.keysym == "Up":
                move_player(canvas, -1, 0)
            elif event.keysym == "Down":
                move_player(canvas, 1, 0)
            elif event.keysym == "Left":
                move_player(canvas, 0, -1)
            elif event.keysym == "Right":
                move_player(canvas, 0, 1)

    window.bind("<KeyPress>", key_press)

    if game_mode == "auto" and not game_over:
        auto_move(canvas)

def show_start_screen():
    for widget in window.winfo_children():
        widget.destroy()

    start_frame = tk.Frame(window)
    start_frame.pack(expand=True, fill="both")

    background_image = PhotoImage(file="background.png")
    background_image_resized = background_image.subsample(2, 2)
    background_label = tk.Label(start_frame, image=background_image_resized)
    background_label.place(relwidth=1, relheight=1)

    tk.Label(start_frame, text="Treasure Hunting Game", font=("Arial", 36), bg="#FDE7A1", fg="red").pack(pady=20)

    tk.Button(start_frame, text="Play Manually", font=("Arial", 16), bg="#3EB603", fg="white", command=lambda: [start_frame.destroy(), start_game("manual")]).pack(pady=10)
    tk.Button(start_frame, text="Auto Play with AI", font=("Arial", 16), bg="#21B8F3", fg="white", command=lambda: [start_frame.destroy(), start_game("auto")]).pack(pady=10)

    tk.Button(start_frame, text="Quit", font=("Arial", 16), bg="#E0422C", fg="white", command=window.destroy).pack(pady=10)

    developer_label = tk.Label(start_frame, text="Developed by Zahid, Rubel, Abir, Shanin", font=("Arial", 12), bg="blue", fg="white")
    developer_label.pack(side="bottom", pady=10)

    background_label.image = background_image_resized

window.geometry("800x600") 
show_start_screen()
window.mainloop()
