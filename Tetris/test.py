import pygame
import random

# Paramètres de la grille de jeu
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30  # Taille de chaque cellule (en pixels)

# Définir les couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Les formes des pièces (tetriminos)
SHAPES = {
    "I": [(0, 1), (1, 1), (2, 1), (3, 1)],
    "O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "T": [(0, 1), (1, 0), (1, 1), (2, 1)],
    "L": [(0, 0), (0, 1), (1, 1), (2, 1)],
    "J": [(2, 0), (0, 1), (1, 1), (2, 1)],
    "S": [(0, 1), (1, 1), (1, 0), (2, 0)],
    "Z": [(0, 0), (1, 0), (1, 1), (2, 1)]
}

# Les couleurs des pièces
SHAPES_COLORS = {
    "I": CYAN,
    "O": YELLOW,
    "T": MAGENTA,
    "L": ORANGE,
    "J": BLUE,
    "S": GREEN,
    "Z": RED
}

def create_empty_grid():
    return [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def generate_piece():
    shape_name = random.choice(list(SHAPES.keys()))
    shape = SHAPES[shape_name]
    color = SHAPES_COLORS[shape_name]
    return {"shape": shape, "position": (GRID_WIDTH // 2 - 1, 0), "color": color}

def rotate(shape):
    return [(y, -x) for x, y in shape]

def check_collision(grid, piece):
    for x, y in piece["shape"]:
        new_x = piece["position"][0] + x
        new_y = piece["position"][1] + y
        if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT or grid[new_y][new_x] != 0:
            return True
    return False

def clear_lines(grid):
    global score
    lines_to_clear = [i for i, row in enumerate(grid) if all(cell != 0 for cell in row)]
    for i in lines_to_clear:
        grid.pop(i)
        grid.insert(0, [0] * GRID_WIDTH)
    score += len(lines_to_clear) * 100
    return len(lines_to_clear)

def handle_input():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  # Déplacer à gauche
        return "LEFT"
    elif keys[pygame.K_RIGHT]:  # Déplacer à droite
        return "RIGHT"
    elif keys[pygame.K_DOWN]:  # Accélérer la chute
        return "DOWN"
    elif keys[pygame.K_UP]:  # Rotation
        return "ROTATE"
    return None

pygame.init()
WIDTH, HEIGHT = GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()

def draw_grid(screen, grid):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color = WHITE if grid[y][x] == 0 else grid[y][x]
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, BLACK, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

def draw_piece(screen, piece):
    for x, y in piece["shape"]:
        pygame.draw.rect(screen, piece["color"], 
                         ((piece["position"][0] + x) * CELL_SIZE, 
                          (piece["position"][1] + y) * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def game_loop():
    global score
    grid = create_empty_grid()
    piece = generate_piece()
    running = True

    while running:
        screen.fill(BLACK)  # Fond noir
        draw_grid(screen, grid)
        draw_piece(screen, piece)

        input_action = handle_input()
        if input_action == "LEFT":
            piece["position"] = (piece["position"][0] - 1, piece["position"][1])
            if check_collision(grid, piece):
                piece["position"] = (piece["position"][0] + 1, piece["position"][1])
        elif input_action == "RIGHT":
            piece["position"] = (piece["position"][0] + 1, piece["position"][1])
            if check_collision(grid, piece):
                piece["position"] = (piece["position"][0] - 1, piece["position"][1])
        elif input_action == "DOWN":
            piece["position"] = (piece["position"][0], piece["position"][1] + 1)
            if check_collision(grid, piece):
                piece["position"] = (piece["position"][0], piece["position"][1] - 1)
                for x, y in piece["shape"]:
                    grid[piece["position"][1] + y][piece["position"][0] + x] = piece["color"]
                piece = generate_piece()
                clear_lines(grid)

        elif input_action == "ROTATE":
            rotated_shape = rotate(piece["shape"])
            piece["shape"] = rotated_shape
            if check_collision(grid, piece):
                piece["shape"] = rotate(rotated_shape)  # Revert rotation

        # Vérifier la fin du jeu
        if any(grid[0][x] != 0 for x in range(GRID_WIDTH)):
            running = False

        pygame.display.update()
        clock.tick(10)  # 10 frames par seconde

    pygame.quit()

score = 0
game_loop()
