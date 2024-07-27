import pygame

cols = 11
rows = 6

pygame.init()
screen = pygame.display.set_mode((cols * 55, rows * 60))
fps = pygame.time.Clock()
running = True
dt = 0

# Initialize font
pygame.font.init()
font = pygame.font.Font(None, 20)

black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)
purple = pygame.Color(128, 0, 128)
gray = pygame.Color(128, 128, 128)

BARRIER = 1
EMPTY = 0
PLAYER = 2
DESTINATION = 3
CURRENT = 4
CLOSED = 5

game_grid = [[0 for i in range(cols)] for j in range(rows)]

barriers = [
    [1, 3],
    [2, 3],
    [2, 4],
    [2, 5],
    [2, 6],
    [2, 7],
]

player_pos = [4, 7]
current_pos = player_pos.copy()
destination = [1, 4]

for barrier in barriers:
    game_grid[barrier[0]][barrier[1]] = BARRIER

game_grid[player_pos[0]][player_pos[1]] = PLAYER
game_grid[destination[0]][destination[1]] = DESTINATION

open_list = []
closed_list = []

# Dictionary to store G, H, and F scores for each node
node_scores = {}

def move_player(direction):
    global current_pos, game_grid
    new_pos = current_pos.copy()

    if direction == "UP":
        new_pos[0] -= 1
    elif direction == "DOWN":
        new_pos[0] += 1
    elif direction == "LEFT":
        new_pos[1] -= 1
    elif direction == "RIGHT":
        new_pos[1] += 1
    elif direction == "UP_LEFT":
        new_pos[0] -= 1
        new_pos[1] -= 1
    elif direction == "UP_RIGHT":
        new_pos[0] -= 1
        new_pos[1] += 1
    elif direction == "DOWN_LEFT":
        new_pos[0] += 1
        new_pos[1] -= 1
    elif direction == "DOWN_RIGHT":
        new_pos[0] += 1
        new_pos[1] += 1

    if new_pos[0] < 0 or new_pos[0] >= rows or new_pos[1] < 0 or new_pos[1] >= cols:
        return

    if game_grid[new_pos[0]][new_pos[1]] == BARRIER:
        return

    game_grid[current_pos[0]][current_pos[1]] = EMPTY
    current_pos = new_pos
    game_grid[current_pos[0]][current_pos[1]] = CURRENT

def reset_game():
    global player_pos, current_pos, game_grid, open_list, closed_list, node_scores
    game_grid = [[0 for i in range(cols)] for j in range(rows)]
    player_pos = [4, 7]
    current_pos = player_pos.copy()
    game_grid[player_pos[0]][player_pos[1]] = PLAYER
    game_grid[destination[0]][destination[1]] = DESTINATION
    for barrier in barriers:
        game_grid[barrier[0]][barrier[1]] = BARRIER
    open_list = []
    closed_list = []
    node_scores = {}

def calculate_distance(start, end):
    row_diff = abs(start[0] - end[0])
    col_diff = abs(start[1] - end[1])
    diagonal_steps = min(row_diff, col_diff)
    straight_steps = abs(row_diff - col_diff)
    distance = diagonal_steps * 14 + straight_steps * 10
    return distance

def update_open_list():
    global open_list, closed_list, node_scores
    new_open_list = []
    for row in range(current_pos[0] - 1, current_pos[0] + 2):
        for col in range(current_pos[1] - 1, current_pos[1] + 2):
            if 0 <= row < rows and 0 <= col < cols and game_grid[row][col] != BARRIER:
                if [row, col] != current_pos and [row, col] not in closed_list:
                    new_open_list.append([row, col])
    open_list.extend([pos for pos in new_open_list if pos not in open_list])
    if current_pos not in closed_list:
        closed_list.append(current_pos)
        game_grid[current_pos[0]][current_pos[1]] = CLOSED

    for pos in closed_list:
        if pos in open_list:
            open_list.remove(pos)
        
    for pos in open_list:
        g_score = calculate_distance(pos, player_pos)
        h_score = calculate_distance(pos, destination)
        f_score = g_score + h_score
        node_scores[tuple(pos)] = (g_score, h_score, f_score)
        
    for pos in closed_list:
        g_score = calculate_distance(pos, player_pos)
        h_score = calculate_distance(pos, destination)
        f_score = g_score + h_score
        node_scores[tuple(pos)] = (g_score, h_score, f_score)

def draw_game_grid():
    screen.fill("black")

    for row in range(len(game_grid)):
        for col in range(len(game_grid[row])):
            rect = pygame.Rect(col * 50, row * 50, 50, 50)
            if game_grid[row][col] == BARRIER:
                pygame.draw.rect(screen, red, rect)
            elif game_grid[row][col] == CURRENT:
                pygame.draw.rect(screen, purple, rect)
            elif game_grid[row][col] == PLAYER:
                pygame.draw.rect(screen, white, rect)
            elif game_grid[row][col] == DESTINATION:
                pygame.draw.rect(screen, green, rect)
            elif game_grid[row][col] == CLOSED:
                pygame.draw.rect(screen, blue, rect)
            else:
                pygame.draw.rect(screen, black, rect)
                
            if col == player_pos[1] and row == player_pos[0]:
                text = font.render("P", True, white)
                pygame.draw.rect(screen, blue, rect)
                screen.blit(text, (col * 50 + 20, row * 50 + 20))
                
            if (row, col) in node_scores:
                g_score, h_score, f_score = node_scores[(row, col)]
                g_text_surface = font.render(str(g_score), True, purple)
                h_text_surface = font.render(str(h_score), True, purple)
                f_text_surface = font.render(str(f_score), True, purple)
                
                screen.blit(g_text_surface, (rect.x + 5, rect.y + 5))
                screen.blit(h_text_surface, (rect.x + rect.width - 20, rect.y + 5))
                screen.blit(f_text_surface, (rect.x + rect.width // 2 - 10, rect.y + rect.height // 2 + 5))
                
            if [row, col] in closed_list:
                g_score, h_score, f_score = node_scores[(row, col)]
                g_text_surface = font.render(str(g_score), True, blue)
                h_text_surface = font.render(str(h_score), True, blue)
                f_text_surface = font.render(str(f_score), True, blue)
                
                screen.blit(g_text_surface, (rect.x + 5, rect.y + 5))
                screen.blit(h_text_surface, (rect.x + rect.width - 20, rect.y + 5))
                screen.blit(f_text_surface, (rect.x + rect.width // 2 - 10, rect.y + rect.height // 2 + 5))
                
    # draw the borders of the grid
    for i in range(cols + 1):
        pygame.draw.line(screen, white, (i * 50, 0), (i * 50, rows * 50))
    for i in range(rows + 1):
        pygame.draw.line(screen, white, (0, i * 50), (cols * 50, i * 50))

update_open_list()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_r:
                reset_game()
            elif event.key == pygame.K_w:
                move_player("UP")
            elif event.key == pygame.K_x:
                move_player("DOWN")
            elif event.key == pygame.K_a:
                move_player("LEFT")
            elif event.key == pygame.K_d:
                move_player("RIGHT")
            elif event.key == pygame.K_q:
                move_player("UP_LEFT")
            elif event.key == pygame.K_e:
                move_player("UP_RIGHT")
            elif event.key == pygame.K_z:
                move_player("DOWN_LEFT")
            elif event.key == pygame.K_c:
                move_player("DOWN_RIGHT")

    update_open_list()
    draw_game_grid()

    # flip() the display to put your work on screen
    pygame.display.flip()
    
    # limits FPS to 60
    dt = fps.tick(60) / 1000

pygame.quit()
