import pygame
import math
import heapq


class Game:
    def __init__(self, cols=11, rows=6, square_size=150):
        self.rows = rows
        self.cols = cols
        self.square_size = square_size
        self.destination = (1, 4)
        self.initial_position = (4, 7)
        self.current = self.initial_position
        self.barriers = [(1, 3), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7)]
        self.open = []
        self.closed = []

        self.screen_width = cols * square_size
        self.screen_height = rows * square_size

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
            "red": pygame.Color(255, 0, 0),
            "green": pygame.Color(0, 255, 0),
            "blue": pygame.Color(0, 0, 255),
            "purple": pygame.Color(128, 0, 128),
            "gray": pygame.Color(128, 128, 128),
            "cyan": pygame.Color(0, 255, 255),
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
        self.open = []
        self.closed = []
        self.current = self.initial_position
        self.initialize_distances()

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
            return self.colors["red"]
        elif (x, y) == self.current:
            return self.colors["blue"]
        elif (x, y) in self.open:
            return self.colors["green"]
        elif (x, y) in self.closed:
            return self.colors["purple"]

        else:
            return self.colors["black"]

    def draw_grid(self):
        for x in range(self.rows):
            for y in range(self.cols):
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
                if (x, y) == self.destination:
                    text = self.font.render(f"D", True, self.colors["white"])
                elif (x, y) == self.initial_position:
                    text = self.font.render(f"I", True, self.colors["white"])
                elif (x, y) in self.barriers:
                    text = self.font.render(f"B", True, self.colors["white"])
                elif (x, y) == self.current:
                    text = self.font.render(f"C", True, self.colors["white"])
                else:
                    text = self.font.render(f"", True, self.colors["white"])

                text_rect = text.get_rect(
                    center=(
                        y * self.square_size + self.square_size // 2,
                        x * self.square_size + self.square_size // 2,
                    )
                )
                self.screen.blit(text, text_rect)

    def draw_open_closed(self):

        for x, y in self.open:
            pygame.draw.rect(
                self.screen,
                self.colors["green"],
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

            self.screen.blit(
                g_cost_text,
                (
                    y * self.square_size + self.square_size // 2 - self.square_size / 3,
                    x * self.square_size + self.square_size // 2 - self.square_size / 3,
                ),
            )

            self.screen.blit(
                h_cost_text,
                (
                    y * self.square_size + self.square_size // 2 + 20,
                    x * self.square_size + self.square_size // 2 - self.square_size / 3,
                ),
            )

            self.screen.blit(
                f_cost_text,
                (
                    y * self.square_size + self.square_size // 2 - 20,
                    x * self.square_size + self.square_size // 2 - 20,
                ),
            )

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

            self.screen.blit(
                g_cost_text,
                (
                    y * self.square_size + self.square_size // 2 - self.square_size / 3,
                    x * self.square_size + self.square_size // 2 - self.square_size / 3,
                ),
            )

            self.screen.blit(
                h_cost_text,
                (
                    y * self.square_size + self.square_size // 2 + 20,
                    x * self.square_size + self.square_size // 2 - self.square_size / 3,
                ),
            )

            self.screen.blit(
                f_cost_text,
                (
                    y * self.square_size + self.square_size // 2 - 20,
                    x * self.square_size + self.square_size // 2 - 20,
                ),
            )

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

    def heuristic(self, node):
        return abs(node[0] - self.destination[0]) + abs(node[1] - self.destination[1])

    def get_all_nodes(self):
        return [(x, y) for x in range(self.rows) for y in range(self.cols)]

    def update_visualization(self):
        self.screen.fill(self.colors["black"])
        self.draw_grid()
        self.draw_open_closed()
        self.draw_objects()
        pygame.display.flip()
        pygame.time.wait(100)  # Add a delay to visualize the algorithm's progress

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.a_star()  # Run Dijkstra's algorithm
            self.fps.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
