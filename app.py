import ast
import pygame
import heapq
import math


BARRIER_IMAGE = pygame.image.load("sprites/barrier1.png")
SQUARE_SIZE = 50
BORDER_RADIUS = 5
COLS = 20
ROWS = 15


# to make a chess like grid
def get_tile_color(x, y):
    return (0, 0, 0) if (x + y) % 2 == 0 else (25, 25, 25)


# get a rect a little smaller than the square
def get_rect(x, y):
    return pygame.Rect(
        x * SQUARE_SIZE + 5, y * SQUARE_SIZE + 5, SQUARE_SIZE - 10, SQUARE_SIZE - 10
    )


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("A* Pathfinding")
        self.screen = pygame.display.set_mode((COLS * SQUARE_SIZE, ROWS * SQUARE_SIZE))
        self.running = True
        self.clock = pygame.time.Clock()
        self.square_size = 50
        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.barriers = [
            (5, 6),
            (4, 6),
            (3, 6),
            (2, 6),
            (1, 6),
            (0, 6),
            (6, 6),
            (7, 6),
            (8, 6),
            (9, 6),
            (12, 6),
            (10, 6),
            (11, 6),
            (13, 6),
            (14, 6),
            (15, 6),
            (16, 6),
            (17, 6),
            (18, 6),
            (19, 6),
            (2, 0),
            (2, 1),
            (3, 1),
            (4, 1),
            (4, 2),
            (5, 4),
            (4, 3),
            (6, 4),
            (8, 4),
            (7, 4),
            (9, 4),
            (10, 4),
            (11, 4),
            (12, 4),
            (4, 4),
            (13, 4),
            (14, 4),
            (15, 4),
            (16, 4),
            (17, 4),
            (18, 4),
            (7, 0),
            (7, 1),
            (7, 2),
            (10, 3),
            (10, 2),
            (10, 1),
            (13, 0),
            (13, 1),
            (13, 2),
            (16, 3),
            (16, 2),
            (16, 1),
        ]

        self.player = (0, 0)
        self.enemy = (7, 7)
        self.destination = (9, 9)
        self.power_up = (3, 0)
        self.open_list = []
        self.closed_list = []
        self.path = []
        self.distances = {}
        self.prev_nodes = {}
        self.time = 0
        self.objective = self.destination
        self.has_power_up = False
        self.is_game_started = False
        self.selected_tool = "barrier"

        self.load_map()
        self.initialize_distances()

    # save the current state of the map to a txt file
    def update_map(self):
        with open("map.txt", "w") as f:
            f.write(f"{self.player}\n")
            f.write(f"{self.enemy}\n")
            f.write(f"{self.destination}\n")
            f.write(f"{self.power_up}\n")
            f.write(f"{self.barriers}\n")

    # check if the map file exists
    def load_map(self):
        try:
            with open("map.txt", "r") as f:
                self.player = ast.literal_eval(f.readline().strip())
                self.enemy = ast.literal_eval(f.readline().strip())
                self.destination = ast.literal_eval(f.readline().strip())
                self.power_up = ast.literal_eval(f.readline().strip())
                self.barriers = ast.literal_eval(f.readline().strip())
        except FileNotFoundError:
            # if the file does not exist, create it with the default values
            self.update_map()
        except (SyntaxError, ValueError) as e:
            print(f"Error reading map.txt: {e}")
            # if there is an error reading the file, create it with the default values
            self.update_map()

    # heuristic function to calculate the distance between two nodes
    def heuristic(self, a, b):
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    # get the neighbors of a node
    def get_neighbors(self, node):
        directions = [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (1, 1),
            (1, -1),
            (-1, 1),
            (-1, -1),
        ]
        neighbors = []
        for direction in directions:
            neighbor = (node[0] + direction[0], node[1] + direction[1])
            if 0 <= neighbor[0] < COLS and 0 <= neighbor[1] < ROWS:
                neighbors.append(neighbor)
            else:
                print(f"Neighbor {neighbor} out of bounds")
        return neighbors

    # initialize the distances dictionary with all the nodes in the grid
    def initialize_distances(self):
        for x in range(COLS):
            for y in range(ROWS):
                self.distances[(x, y)] = float("inf")
        self.distances[self.player] = 0

    # reconstruct the path from the destination to the initial position
    def reconstruct_path(self, end_node):
        print("Reconstructing path")
        path = []
        while end_node in self.prev_nodes:
            path.append(end_node)
            end_node = self.prev_nodes[end_node]
        print(path)
        self.path = path
        self.closed_list = []
        self.open_list = []

    # each tick of the game
    def move_player_with_a_star(self):
        if self.path:
            print("Moving player")
            self.player = self.path.pop(-1)
            self.path = []
            self.open_list = []
            self.closed_list = []
            self.distances = {}
            self.prev_nodes = {}
            self.initialize_distances()
            self.move_enemy()
            if self.player == self.power_up:
                self.has_power_up = True
            return

        print("Calculating path")

        priority_queue = []
        heapq.heappush(priority_queue, (0, self.player))

        while priority_queue:
            current_node = heapq.heappop(priority_queue)[1]

            if current_node == self.objective:
                print("Path found")
                self.reconstruct_path(current_node)
                break

            if current_node in self.closed_list:
                continue

            self.closed_list.append(current_node)
            neighbors = self.get_neighbors(current_node)

            for neighbor in neighbors:
                if (
                    neighbor in self.closed_list
                    or (neighbor in self.barriers and not self.has_power_up)
                    or neighbor in self.open_list
                    or neighbor == self.enemy
                ):
                    continue

                g_cost = self.heuristic(current_node, neighbor)
                h_cost = self.heuristic(neighbor, self.objective)
                f_cost = g_cost + h_cost

                if f_cost < self.distances[neighbor]:
                    self.distances[neighbor] = f_cost
                    self.prev_nodes[neighbor] = current_node
                    heapq.heappush(priority_queue, (f_cost, neighbor))

            self.open_list = [node for _, node in priority_queue]
            pygame.display.flip()

        if not self.path:
            print("No path found")
            # if no path found, try to found a path to the power up that unlock the power to destroy barriers
            if self.objective == self.destination:
                self.objective = self.power_up
            else:
                self.objective = self.destination
            self.open_list = []
            self.closed_list = []
            self.distances = {}
            self.prev_nodes = {}
            self.initialize_distances()

    def draw_grid(self):
        self.screen.fill((0, 0, 0))
        for i in range(COLS):
            for j in range(ROWS):
                if (i, j) in self.barriers and not self.has_power_up:

                    self.screen.blit(
                        BARRIER_IMAGE,
                        get_rect(i, j),
                    )

                elif (i, j) == self.player:
                    pygame.draw.rect(
                        self.screen,
                        (0, 255, 0),
                        get_rect(i, j),
                        0,
                        BORDER_RADIUS,
                    )

                elif (i, j) == self.enemy:
                    pygame.draw.rect(
                        self.screen,
                        (255, 0, 0),
                        get_rect(i, j),
                        0,
                        BORDER_RADIUS,
                    )

                elif (i, j) == self.destination:
                    pygame.draw.rect(
                        self.screen,
                        (0, 0, 255),
                        get_rect(i, j),
                        0,
                        BORDER_RADIUS,
                    )

                elif (i, j) == self.power_up and not self.has_power_up:
                    pygame.draw.rect(
                        self.screen,
                        (255, 255, 255),
                        get_rect(i, j),
                        0,
                        BORDER_RADIUS,
                    )

                elif (i, j) in self.path:
                    pygame.draw.rect(
                        self.screen,
                        (0, 255, 255),
                        get_rect(i, j),
                        0,
                        BORDER_RADIUS,
                    )

                elif (i, j) in self.open_list:
                    pygame.draw.rect(
                        self.screen,
                        (255, 255, 0),
                        get_rect(i, j),
                        0,
                        BORDER_RADIUS,
                    )

                elif (i, j) in self.closed_list:
                    pygame.draw.rect(
                        self.screen,
                        (255, 0, 255),
                        get_rect(i, j),
                        0,
                        BORDER_RADIUS,
                    )

                else:
                    pygame.draw.rect(
                        self.screen,
                        get_tile_color(i, j),
                        (i * SQUARE_SIZE, j * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
                        0,
                    )

    def move_enemy(self):
        enemyY = -1 if self.enemy[1] % 2 == 0 else 1
        self.enemy = (self.enemy[0], self.enemy[1] + enemyY)

    def reset(self):
        self.player = (0, 0)
        self.enemy = (7, 7)
        self.destination = (9, 9)
        self.power_up = (3, 0)
        self.open_list = []
        self.closed_list = []
        self.path = []
        self.distances = {}
        self.prev_nodes = {}
        self.time = 0
        self.objective = self.destination
        self.has_power_up = False
        self.is_game_started = False
        self.selected_tool = "barrier"

        self.initialize_distances()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset()
                    if event.key == pygame.K_SPACE:
                        self.is_game_started = True
                    elif event.key == pygame.K_1:
                        self.selected_tool = "barrier"
                        pygame.display.set_caption(
                            f"Selected tool: {self.selected_tool}"
                        )
                    elif event.key == pygame.K_2:
                        self.selected_tool = "initial_position"
                        pygame.display.set_caption(
                            f"Selected tool: {self.selected_tool}"
                        )
                    elif event.key == pygame.K_3:
                        self.selected_tool = "destination"
                        pygame.display.set_caption(
                            f"Selected tool: {self.selected_tool}"
                        )
                    elif event.key == pygame.K_4:
                        self.selected_tool = "power_up"
                        pygame.display.set_caption(
                            f"Selected tool: {self.selected_tool}"
                        )
                    elif event.key == pygame.K_5:
                        self.selected_tool = "enemy"
                        pygame.display.set_caption(
                            f"Selected tool: {self.selected_tool}"
                        )
                    elif event.key == pygame.K_p:
                        print(self.barriers)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    print("mouse event")
                    x, y = event.pos
                    x = x // self.square_size
                    y = y // self.square_size

                    if self.selected_tool == "barrier":
                        if (x, y) not in self.barriers:
                            self.barriers.append((x, y))
                        else:
                            self.barriers.remove((x, y))
                    elif self.selected_tool == "initial_position":
                        self.player = (x, y)
                    elif self.selected_tool == "destination":
                        self.destination = (x, y)
                    elif self.selected_tool == "power_up":
                        self.power_up = (x, y)
                    elif self.selected_tool == "enemy":
                        self.enemy = (x, y)

                    self.update_map()

            self.draw_grid()

            pygame.display.flip()

            if self.is_game_started:
                if self.player != self.destination:
                    self.move_player_with_a_star()

            self.time += 1
            self.clock.tick(10)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
