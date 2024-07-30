import heapq


class Pathfinding:
    def __init__(
        self, cols=11, rows=6, barriers=None, initial_position=None, destination=None
    ):
        self.rows = rows
        self.cols = cols
        self.initial_position = initial_position if initial_position else (4, 7)
        self.destination = destination if destination else (1, 4)
        self.barriers = (
            barriers if barriers else [(1, 3), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7)]
        )

        self.distances = {}
        self.prev_nodes = {}
        self.closed = set()

    def get_neighbors(self, position):
        neighbors = []
        x, y = position
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (
                    (i, j) != (0, 0)
                    and 0 <= x + i < self.rows
                    and 0 <= y + j < self.cols
                ):
                    neighbors.append((x + i, y + j))
        return neighbors

    def calculate_distance(self, pos1, pos2):
        x1, y1 = pos1
        x2, y2 = pos2
        row_diff = abs(x1 - x2)
        col_diff = abs(y1 - y2)
        diagonal_steps = min(row_diff, col_diff)
        straight_steps = abs(row_diff - col_diff)
        distance = diagonal_steps * 14 + straight_steps * 10
        return distance

    def heuristic(self, node):
        return abs(node[0] - self.destination[0]) + abs(node[1] - self.destination[1])

    def get_all_nodes(self):
        return [(x, y) for x in range(self.rows) for y in range(self.cols)]

    def a_star(self):
        priority_queue = []
        heapq.heappush(priority_queue, (0, self.initial_position))

        self.distances = {node: float("inf") for node in self.get_all_nodes()}
        self.distances[self.initial_position] = 0

        self.prev_nodes = {node: None for node in self.get_all_nodes()}

        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)

            if current_node == self.destination:
                break

            if current_node in self.closed:
                continue

            self.closed.add(current_node)
            neighbors = self.get_neighbors(current_node)

            for neighbor in neighbors:
                if neighbor in self.closed or neighbor in self.barriers:
                    continue

                new_distance = current_distance + self.calculate_distance(
                    current_node, neighbor
                )
                if new_distance < self.distances[neighbor]:
                    self.distances[neighbor] = new_distance
                    self.prev_nodes[neighbor] = current_node
                    priority = new_distance + self.heuristic(neighbor)
                    heapq.heappush(priority_queue, (priority, neighbor))

        # Reconstruct path
        path = []
        step = self.destination
        while step is not None:
            path.append(step)
            step = self.prev_nodes[step]
        path.reverse()

        return path

    def print_path(self):
        path = self.a_star()
        print("Shortest Path:")
        # print the map with the path as a sequence of numbers
        for i in range(self.rows):
            for j in range(self.cols):
                if (i, j) in self.barriers:
                    print("X", end=" ")
                elif (i, j) == self.initial_position:
                    print("S", end=" ")
                elif (i, j) == self.destination:
                    print("D", end=" ")
                elif (i, j) in path:
                    print(path.index((i, j)), end=" ")
                else:
                    print(".", end=" ")
            print()


if __name__ == "__main__":
    pathfinder = Pathfinding()
    pathfinder.print_path()
