import pygame
import math
from queue import PriorityQueue


# Setting game dimensions
gameBoardWidth = 800
win = pygame.display.set_mode((gameBoardWidth, gameBoardWidth))
pygame.display.set_caption("A* Path Finding Algorithm Solver")


# Define colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows


    # Check color of position
    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    # Set color of position
    def make_start(self):
        self.color = ORANGE

    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = RED
    
    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        # Neighbor below
        if self.row < (self.total_rows -1) and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        # Neighbor above
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        # Neighbor right
        if self.col < (self.total_rows -1) and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        # Neighbor left
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

    # If we spot two objects at the same spot, only set one of them.
    def __lt__(self, other):
        return False

# A star algorithm
def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            path_len = reconstruct_path(came_from, end, draw)
            end.make_end()
            return path_len

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()
        if current != start:
            current.make_closed()

    return False


# heuristic function. Guessing distance using manhattan distance (closest distance w one turn)
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

# Reconstructs shortest path by traversing through current nodes.
def reconstruct_path(came_from, current, draw):
    path_length = 0
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()
        path_length += 1
    
    # Set starting point to start color (orange)
    current.make_start()

    return path_length

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Node(i, j, gap, rows)
            grid[i].append(spot)

    return grid

# Draw grid lines at the borders of all spots
def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i* gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j* gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()

# Find user mouse position
def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col



def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Adds barrier with left click on grid
            if pygame.mouse.get_pressed()[0]:  # Left click
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()

                elif not end and spot != start:
                    end = spot
                    end.make_end()

                elif spot != end and spot != start:
                    spot.make_barrier()

            # Removes barrier with right click
            elif pygame.mouse.get_pressed()[2]:  # Right click
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()

                if spot == start:
                    start = None
                elif spot == end:
                    end = None


            if event.type == pygame.KEYDOWN:
                # Runs A*star algorithm with spacebar press
                if event.key == pygame.K_SPACE and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                # Clears grid and resets game.
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

                # Tests to confirm algorithm correctly finds shortest paths for test cases
                if event.key == pygame.K_t:
                    # Test Case # 1. Shortest path should be 42 steps.
                    start = grid[10][10]
                    start.make_start()
                    end = grid[10][40]
                    end.make_end()

                    for i in range(5, 30):
                        spot = grid[i][30]
                        spot.make_barrier()


                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    
                    assert 42 == algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end), "Not the shortest path"

                    # Reset Board
                    grid = make_grid(ROWS, width)
                    # Test Case # 2. Shortest path should be 26 steps.
                    start = grid[10][10]
                    start.make_start()
                    end = grid[20][10]
                    end.make_end()

                    for i in range(3, 19):
                        spot = grid[15][i]
                        spot.make_barrier()


                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    
                    assert 26 == algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end), "Not the shortest path"


                    

    pygame.quit()

main(win, gameBoardWidth)
