import pygame
import heapq
import random
import time

# Difficulty levels and corresponding maze sizes
maze_sizes = {'easy': 20, 'medium': 40, 'hard': 50}

# Function to choose difficulty level
def select_difficulty():
    print("Select difficulty level: ")
    print("1. Easy")
    print("2. Medium")
    print("3. Hard")
    choice = input("Enter your choice (1-3): ")

    if choice == '1':
        return maze_sizes['easy']
    elif choice == '2':
        return maze_sizes['medium']
    elif choice == '3':
        return maze_sizes['hard']
    else:
        print("Invalid choice! Defaulting to Easy level.")
        return maze_sizes['easy']

# Set maze size based on difficulty selection
maze_size = select_difficulty()

# Maze setup
maze = [[1] * maze_size for _ in range(maze_size)]

# Prim's algorithm for maze generation
def generate_maze():
    start_x, start_y = random.randint(0, maze_size - 1), random.randint(0, maze_size - 1)
    maze[start_x][start_y] = 0
    walls = [(start_x, start_y + 1), (start_x + 1, start_y), (start_x, start_y - 1), (start_x - 1, start_y)]

    while walls:
        x, y = random.choice(walls)
        walls.remove((x, y))

        if 0 <= x < maze_size and 0 <= y < maze_size and maze[x][y] == 1:
            neighbors = 0
            if x > 0 and maze[x - 1][y] == 0:
                neighbors += 1
            if x < maze_size - 1 and maze[x + 1][y] == 0:
                neighbors += 1
            if y > 0 and maze[x][y - 1] == 0:
                neighbors += 1
            if y < maze_size - 1 and maze[x][y + 1] == 0:
                neighbors += 1

            if neighbors == 1:
                maze[x][y] = 0
                walls.append((x, y + 1))
                walls.append((x + 1, y))
                walls.append((x, y - 1))
                walls.append((x - 1, y))

# A* algorithm for pathfinding
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(start, end):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        if current == end:
            return reconstruct_path(came_from, current)
        
        x, y = current
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (x + dx, y + dy)
            if (0 <= neighbor[0] < maze_size and 0 <= neighbor[1] < maze_size and maze[neighbor[0]][neighbor[1]] == 0):
                tentative_g_score = g_score[current] + 1
                
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    return []

def reconstruct_path(came_from, current):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

# Enemy class for AI enemies
class Enemy:
    def __init__(self, pos):
        self.pos = list(pos)

    def move_toward_player(self, player_pos):
        path = a_star(tuple(self.pos), tuple(player_pos))
        if path:
            self.pos = list(path[0])

# Choose game mode
def select_game_mode():
    print("Select game mode: ")
    print("1. Manual Mode")
    print("2. AI Mode")
    choice = input("Enter your choice (1-2): ")
    
    if choice == '1':
        return "manual"
    elif choice == '2':
        return "ai"
    else:
        print("Invalid choice! Defaulting to Manual Mode.")
        return "manual"

game_mode = select_game_mode()

# Generate maze and set start/end points
generate_maze()
start = (0, 0)
end = (maze_size - 1, maze_size - 1)
maze[0][0] = 0
maze[maze_size - 1][maze_size - 1] = 0

# Set up AI enemies
num_enemies = 1
enemies = [Enemy((random.randint(0, maze_size - 1), random.randint(0, maze_size - 1))) for _ in range(num_enemies)]

# Pygame Initialization
pygame.init()
tile_size = 15
window_size = (maze_size * tile_size, maze_size * tile_size)
screen = pygame.display.set_mode(window_size, pygame.RESIZABLE | pygame.NOFRAME)
pygame.display.set_caption("Maze Game with AI Enemies")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Draw maze function
def draw_maze():
    for x in range(len(maze)):
        for y in range(len(maze[0])):
            color = WHITE if maze[x][y] == 0 else BLACK
            pygame.draw.rect(screen, color, (y * tile_size, x * tile_size, tile_size, tile_size))
    pygame.draw.rect(screen, GREEN, (start[1] * tile_size, start[0] * tile_size, tile_size, tile_size))
    pygame.draw.rect(screen, RED, (end[1] * tile_size, end[0] * tile_size, tile_size, tile_size))

# Main Game Loop
player_pos = list(start)
hit_count = 0
invincibility_cooldown = 3  # cooldown in seconds
last_hit_time = 0  # track the time of the last hit
enemy_move_timer = time.time()
running = True

# Start the game timer
game_start_time = time.time()

# Define the path for AI mode
ai_path = a_star(start, end) if game_mode == "ai" else []

# Time interval for AI movement
ai_move_timer = time.time()

while running:
    screen.fill(BLACK)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            new_pos = list(player_pos)
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                new_pos[1] -= 1  # Move left
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                new_pos[1] += 1  # Move right
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                new_pos[0] -= 1  # Move up
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                new_pos[0] += 1  # Move down
            
            # Ensure the new position is within bounds and not a wall
            if 0 <= new_pos[0] < maze_size and 0 <= new_pos[1] < maze_size and maze[new_pos[0]][new_pos[1]] == 0:
                player_pos = new_pos  # Update player position

    # AI Mode: Move the AI player every 1 second along the calculated path
    if game_mode == "ai" and time.time() - ai_move_timer > 1:
        if ai_path:
            next_step = ai_path.pop(0)
            player_pos = list(next_step)
            ai_move_timer = time.time()
        else:
            print("AI has reached the end.")
            running = False

    # Move enemies every 2 seconds
    if time.time() - enemy_move_timer > 2:
        for enemy in enemies:
            enemy.move_toward_player(tuple(player_pos))
        enemy_move_timer = time.time()

    # Draw the maze and player
    draw_maze()
    pygame.draw.rect(screen, BLUE, (player_pos[1] * tile_size, player_pos[0] * tile_size, tile_size, tile_size))  # Draw player

    # Draw enemies
    for enemy in enemies:
        pygame.draw.rect(screen, YELLOW, (enemy.pos[1] * tile_size, enemy.pos[0] * tile_size, tile_size, tile_size))
    
    # Update screen
    pygame.display.flip()

    # Check for collisions with enemies (invincibility logic)
    for enemy in enemies:
        if player_pos == enemy.pos:
            current_time = time.time()
            if current_time - last_hit_time > invincibility_cooldown:
                last_hit_time = current_time
                hit_count += 1
                print(f"Player hit by enemy! Total hits: {hit_count}")

    # End game condition: player reaches the end or hit count exceeds
    if tuple(player_pos) == end:
        print("Player reached the end!")
        game_end_time = time.time()
        print(f"Time taken: {game_end_time - game_start_time:.2f} seconds")
        running = False
    elif hit_count > 3:
        print("Player has been hit too many times!")
        running = False

    # Delay to control game speed
    time.sleep(0.1)

pygame.quit()
