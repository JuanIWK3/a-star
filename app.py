import pygame
import math
import heapq
import random
import time

# Directions: (dx, dy)
DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]


def is_valid(x, y, maze):
    return 0 <= x < len(maze) and 0 <= y < len(maze[0])


def generate_maze(rows, cols):
    random.seed(time.time())  # Seed the random number generator with the current time
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    visited = [[False for _ in range(cols)] for _ in range(rows)]

    def carve_passages(x, y):
        visited[x][y] = True
        maze[x][y] = 0  # Mark cell as path

        directions = DIRECTIONS[:]
        random.shuffle(directions)  # Randomize the order of exploration

        for dx, dy in directions:
            nx, ny = x + 2 * dx, y + 2 * dy
            if is_valid(nx, ny, maze) and not visited[nx][ny]:
                maze[x + dx][y + dy] = 0  # Remove the wall between cells
                carve_passages(nx, ny)

    start_x, start_y = random.randrange(rows // 2) * 2, random.randrange(cols // 2) * 2
    carve_passages(start_x, start_y)
    return maze


class Game:
    def __init__(self, square_size=50):
        self.mode = "menu"
        self.map = 0
        self.rows = 20
        self.cols = 20
        self.square_size = square_size
        self.destination = (14, 19)
        self.initial_position = (0, 0)
        self.current = self.initial_position
        self.maze = []
        self.barriers = []
        self.open = []
        self.closed = []
        self.path = []
        self.screen_width = self.cols * square_size
        self.screen_height = self.rows * square_size
        self.selected_tool = "barrier"

        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.fps = pygame.time.Clock()
        self.running = True
        self.dt = 0

        pygame.font.init()
        self.font = pygame.font.Font(None, 24)

        self.colors = {
            "black": pygame.Color(0, 0, 0),
            "white": pygame.Color(255, 255, 255),
            "red": pygame.Color(200, 0, 0),
            "green": pygame.Color(0, 255, 0),
            "blue": pygame.Color(0, 0, 255),
            "purple": pygame.Color(128, 0, 128),
            "gray": pygame.Color(128, 128, 128),
            "cyan": pygame.Color(0, 255, 255),
            "yellow": pygame.Color(255, 255, 0),
        }

        self.BARRIER = 1
        self.EMPTY = 0
        self.PLAYER = 2
        self.DESTINATION = 3
        self.CURRENT = 4
        self.CLOSED = 5
        self.OPEN = 6

        self.distances = {}
        self.prev_nodes = {}
        self.initialize_distances()

    def initialize_distances(self):
        for x in range(self.rows):
            for y in range(self.cols):
                self.distances[(x, y)] = float("inf")
        self.distances[self.initial_position] = 0

    def reset_game(self):
        print("Resetting game")
        self.open = []
        self.closed = []
        self.path = []
        self.current = self.initial_position
        self.initialize_distances()

        if self.mode == "maze":
            self.maze = generate_maze(self.rows, self.cols)
            self.barriers = [
                (x, y)
                for x in range(self.rows)
                for y in range(self.cols)
                if self.maze[x][y] == 1
            ]

            if self.destination in self.barriers:
                self.barriers.remove(self.destination)

        self.update_visualization()

    def move(self, direction):
        new_position = self.current

        if direction == "UP":
            new_position = (self.current[0] - 1, self.current[1])
        elif direction == "DOWN":
            new_position = (self.current[0] + 1, self.current[1])
        elif direction == "LEFT":
            new_position = (self.current[0], self.current[1] - 1)
        elif direction == "RIGHT":
            new_position = (self.current[0], self.current[1] + 1)
        elif direction == "UP_LEFT":
            new_position = (self.current[0] - 1, self.current[1] - 1)
        elif direction == "UP_RIGHT":
            new_position = (self.current[0] - 1, self.current[1] + 1)
        elif direction == "DOWN_LEFT":
            new_position = (self.current[0] + 1, self.current[1] - 1)
        elif direction == "DOWN_RIGHT":
            new_position = (self.current[0] + 1, self.current[1] + 1)

        if new_position in self.barriers:
            print("You hit a barrier")
            return
        elif (
            new_position[0] < 0
            or new_position[0] >= self.rows
            or new_position[1] < 0
            or new_position[1] >= self.cols
        ):
            print("You hit a wall")
            return
        elif new_position == self.destination:
            print("You reached the destination")
            return
        else:
            self.current = new_position

    def get_square_color(self, x, y):
        if (x, y) == self.destination:
            return self.colors["cyan"]
        elif (x, y) == self.initial_position:
            return self.colors["blue"]
        elif (x, y) in self.barriers:
            return self.colors["black"]
        elif (x, y) == self.current:
            return self.colors["blue"]
        elif (x, y) in self.open:
            return self.colors["gray"]
        elif (x, y) in self.closed:
            return self.colors["purple"]

        else:
            return self.colors["white"]

    def draw_grid(self):
        for x in range(self.rows):
            for y in range(self.cols):
                pygame.draw.rect(
                    self.screen,
                    self.colors["gray"],
                    (
                        y * self.square_size,
                        x * self.square_size,
                        self.square_size,
                        self.square_size,
                    ),
                    1,
                )

    def draw_objects(self):
        for x in range(self.rows):
            for y in range(self.cols):
                if (x, y) in self.barriers:  # draw the barrier image on the screen
                    image = pygame.image.load("barrier.png")

                    self.screen.blit(
                        image,
                        (
                            y * self.square_size,
                            x * self.square_size,
                            self.square_size / 2,
                            self.square_size / 2,
                        ),
                    )
                elif (x, y) == self.destination:
                    image = pygame.image.load("dest_flag.png")

                    self.screen.blit(
                        image,
                        (
                            y * self.square_size,
                            x * self.square_size,
                            self.square_size / 2,
                            self.square_size / 2,
                        ),
                    )
                else:
                    pygame.draw.rect(
                        self.screen,
                        self.get_square_color(x, y),
                        (
                            y * self.square_size,
                            x * self.square_size,
                            self.square_size,
                            self.square_size,
                        ),
                        0,
                    )

    def draw_open_closed(self):

        for x, y in self.open:
            pygame.draw.rect(
                self.screen,
                self.colors["gray"],
                (
                    y * self.square_size,
                    x * self.square_size,
                    self.square_size,
                    self.square_size,
                ),
                0,
            )

            g_cost = self.calculate_distance((x, y), self.initial_position)
            h_cost = self.calculate_distance((x, y), self.destination)
            f_cost = g_cost + h_cost

            g_cost_text = self.font.render(
                f"{g_cost:.2f}",
                True,
                self.colors["white"],
            )

            h_cost_text = self.font.render(
                f"{h_cost:.2f}",
                True,
                self.colors["white"],
            )

            f_cost_text = self.font.render(
                f"{f_cost:.2f}",
                True,
                self.colors["white"],
            )

            # self.screen.blit(
            #     g_cost_text,
            #     (
            #         y * self.square_size + self.square_size // 2 - self.square_size / 3,
            #         x * self.square_size + self.square_size // 2 - self.square_size / 3,
            #     ),
            # )

            # self.screen.blit(
            #     h_cost_text,
            #     (
            #         y * self.square_size + self.square_size // 2 + 20,
            #         x * self.square_size + self.square_size // 2 - self.square_size / 3,
            #     ),
            # )

            # self.screen.blit(
            #     f_cost_text,
            #     (
            #         y * self.square_size + self.square_size // 2 - 20,
            #         x * self.square_size + self.square_size // 2 - 20,
            #     ),
            # )

        for x, y in self.closed:
            pygame.draw.rect(
                self.screen,
                self.colors["purple"],
                (
                    y * self.square_size,
                    x * self.square_size,
                    self.square_size,
                    self.square_size,
                ),
                0,
            )

            g_cost = self.calculate_distance((x, y), self.initial_position)
            h_cost = self.calculate_distance((x, y), self.destination)
            f_cost = g_cost + h_cost

            g_cost_text = self.font.render(
                f"{g_cost:.2f}",
                True,
                self.colors["white"],
            )

            h_cost_text = self.font.render(
                f"{h_cost:.2f}",
                True,
                self.colors["white"],
            )

            f_cost_text = self.font.render(
                f"{f_cost:.2f}",
                True,
                self.colors["white"],
            )

            # self.screen.blit(
            #     g_cost_text,
            #     (
            #         y * self.square_size + self.square_size // 2 - self.square_size / 3,
            #         x * self.square_size + self.square_size // 2 - self.square_size / 3,
            #     ),
            # )

            # self.screen.blit(
            #     h_cost_text,
            #     (
            #         y * self.square_size + self.square_size // 2 + 20,
            #         x * self.square_size + self.square_size // 2 - self.square_size / 3,
            #     ),
            # )

            # self.screen.blit(
            #     f_cost_text,
            #     (
            #         y * self.square_size + self.square_size // 2 - 20,
            #         x * self.square_size + self.square_size // 2 - 20,
            #     ),
            # )

    def calculate_distance(self, node1, node2):
        return math.sqrt((node1[0] - node2[0]) ** 2 + (node1[1] - node2[1]) ** 2)

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
            if 0 <= neighbor[0] < self.rows and 0 <= neighbor[1] < self.cols:
                neighbors.append(neighbor)
        return neighbors

    # search for the node with the lowest f_cost
    # if there are multiple nodes with the same f_cost, return the one with the lowest h_cost
    def a_star(self):
        priority_queue = []
        heapq.heappush(priority_queue, (0, self.initial_position))

        while priority_queue:
            current_node = heapq.heappop(priority_queue)[1]

            if current_node == self.destination:
                print("Path found")
                self.reconstruct_path(current_node)
                break

            if current_node in self.closed:
                continue

            self.closed.append(current_node)
            neighbors = self.get_neighbors(current_node)

            for neighbor in neighbors:
                if neighbor in self.closed or neighbor in self.barriers:
                    continue

                g_cost = self.calculate_distance(current_node, self.initial_position)
                h_cost = self.heuristic(neighbor)
                f_cost = g_cost + h_cost

                if f_cost < self.distances[neighbor]:
                    self.distances[neighbor] = f_cost
                    self.prev_nodes[neighbor] = current_node
                    heapq.heappush(priority_queue, (f_cost, neighbor))

            self.open = [node for f_cost, node in priority_queue]
            self.update_visualization()

    def reconstruct_path(self, end_node):
        print("Reconstructing path")
        path = []
        while end_node in self.prev_nodes:
            path.append(end_node)
            end_node = self.prev_nodes[end_node]
        print(path)
        path.remove(self.destination)
        self.path = path
        self.closed = []
        self.open = []

    def heuristic(self, node):
        return abs(node[0] - self.destination[0]) + abs(node[1] - self.destination[1])

    def get_all_nodes(self):
        return [(x, y) for x in range(self.rows) for y in range(self.cols)]

    def draw_selected_tool(self):  # put the selected tool in the title
        pygame.display.set_caption(f"Selected tool: {self.selected_tool}")

    def update_visualization(self):
        print("Drawing editor")
        self.screen.fill(self.colors["white"])
        self.draw_selected_tool()
        self.draw_objects()

        self.screen.fill(self.colors["white"])
        self.draw_open_closed()
        self.draw_objects()

        self.draw_grid()

        if hasattr(self, "path"):
            for x, y in self.path:
                pygame.draw.rect(
                    self.screen,
                    pygame.Color(255, 255, 0),  # Yellow color
                    (
                        y * self.square_size,
                        x * self.square_size,
                        self.square_size,
                        self.square_size,
                    ),
                    0,
                )

        pygame.display.flip()
        # pygame.time.wait(10)  # Add a delay to visualize the algorithm's progress

    def choose_map(self):
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.screen.fill(self.colors["white"])
        text = self.font.render("Choose a map", True, self.colors["black"])
        self.screen.blit(
            text, (self.screen_width // 2 - 100, self.screen_height // 2 - 50)
        )
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.map = 1
                elif event.key == pygame.K_2:
                    self.map = 2
                elif event.key == pygame.K_3:
                    self.map = 3

    def choose_mode(self):
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.screen.fill(self.colors["white"])
        text = self.font.render("Choose a mode", True, self.colors["black"])
        self.screen.blit(
            text, (self.screen_width // 2 - 100, self.screen_height // 2 - 50)
        )

        maze = self.font.render("1. Maze", True, self.colors["black"])
        barricade = self.font.render("2. Barricade", True, self.colors["black"])

        self.screen.blit(maze, (self.screen_width // 2 - 100, self.screen_height // 2))
        self.screen.blit(
            barricade, (self.screen_width // 2 - 100, self.screen_height // 2 + 50)
        )

        pygame.display.flip()

    def select_maze(self):
        self.mode = "maze"
        self.reset_game()

    def select_barricade(self):
        self.mode = "barricade"
        self.reset_game()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEBUTTONDOWN and self.mode != "menu":
                    y, x = event.pos
                    x = x // self.square_size
                    y = y // self.square_size

                    if self.selected_tool == "barrier":
                        if (x, y) not in self.barriers:
                            self.barriers.append((x, y))
                        else:
                            self.barriers.remove((x, y))
                    elif self.selected_tool == "initial_position":
                        self.initial_position = (x, y)
                        self.current = self.initial_position
                    elif self.selected_tool == "destination":
                        self.destination = (x, y)

                    self.update_visualization()

                if event.type == pygame.KEYDOWN:
                    if self.mode == "menu":
                        if event.key == pygame.K_1:
                            self.select_maze()
                        elif event.key == pygame.K_2:
                            self.select_barricade()

                    else:
                        if event.key == pygame.K_r:
                            self.reset_game()
                        elif event.key == pygame.K_c:  # clear all barriers
                            self.barriers = []
                            self.update_visualization()
                        elif event.key == pygame.K_BACKSPACE:
                            self.mode = "menu"
                        elif event.key == pygame.K_a:
                            self.a_star()
                        elif event.key == pygame.K_1:
                            self.selected_tool = "barrier"
                            self.draw_selected_tool()
                        elif event.key == pygame.K_2:
                            self.selected_tool = "initial_position"
                            self.draw_selected_tool()
                        elif event.key == pygame.K_3:
                            self.selected_tool = "destination"
                            self.draw_selected_tool()

            if self.mode == "menu":
                self.choose_mode()

            self.fps.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
