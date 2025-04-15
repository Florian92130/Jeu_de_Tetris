import pygame
import random
import sys

# Paramètres de la grille de jeu
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30  # Taille de chaque cellule (en pixels)
PREVIEW_CELL_SIZE = 20  # Taille des cellules pour la prévisualisation

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
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

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

class Tetris:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Configuration de l'écran
        self.game_width = GRID_WIDTH * CELL_SIZE
        self.preview_width = 6 * PREVIEW_CELL_SIZE
        self.width = self.game_width + self.preview_width
        self.height = GRID_HEIGHT * CELL_SIZE
        self.screen = pygame.display.set_mode((self.width, self.height + 50))  # Espace supplémentaire pour le score
        pygame.display.set_caption("Tetris")
        self.soft_drop = False
        self.soft_drop_score = 0
        
        # Police pour le score
        self.font = pygame.font.Font(None, 36)
        
        # Charger la musique
        try:
            pygame.mixer.music.load("tetris_theme.mp3")  # Assurez-vous d'avoir un fichier MP3 de musique Tetris
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)  # Jouer en boucle
        except pygame.error:
            print("Erreur de chargement de la musique. Assurez-vous que le fichier tetris_theme.mp3 existe.")
        
        # Variables du jeu
        self.grid = self.create_empty_grid()
        self.piece = self.generate_piece()
        self.next_pieces = [self.generate_piece() for _ in range(3)]  # 3 prochaines pièces
        self.score = 0
        self.clock = pygame.time.Clock()
        self.game_over = False
        
        # Variables de contrôle
        self.drop_time = 0
        self.drop_speed = 500  # Temps en millisecondes entre chaque descente automatique
        self.last_drop_time = pygame.time.get_ticks()
        
    # [Tous les autres méthodes restent identiques]
    def create_empty_grid(self):
        return [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    
    def generate_piece(self):
        shape_name = random.choice(list(SHAPES.keys()))
        shape = SHAPES[shape_name]
        color = SHAPES_COLORS[shape_name]
        return {"shape": shape, "position": (GRID_WIDTH // 2 - 1, 0), "color": color}
    
    def rotate(self, shape):
        return [(y, -x) for x, y in shape]
    
    def check_collision(self, piece):
        for x, y in piece["shape"]:
            new_x = piece["position"][0] + x
            new_y = piece["position"][1] + y
            if (new_x < 0 or new_x >= GRID_WIDTH or 
                new_y >= GRID_HEIGHT or 
                (new_y >= 0 and self.grid[new_y][new_x] != 0)):
                return True
        return False
    
    def clear_lines(self):
        lines_to_clear = [i for i, row in enumerate(self.grid) if all(cell != 0 for cell in row)]
        for i in lines_to_clear:
            self.grid.pop(i)
            self.grid.insert(0, [0] * GRID_WIDTH)
        
        # Calcul du score (plus de points pour les lignes multiples)
        score_multipliers = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}
        self.score += score_multipliers.get(len(lines_to_clear), 1200)
    
    def draw_grid(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = self.grid[y][x] if self.grid[y][x] != 0 else WHITE
                pygame.draw.rect(self.screen, color, 
                                 (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(self.screen, GRAY, 
                                 (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
    
    def draw_piece(self, piece):
        for x, y in piece["shape"]:
            pygame.draw.rect(self.screen, piece["color"], 
                             ((piece["position"][0] + x) * CELL_SIZE, 
                              (piece["position"][1] + y) * CELL_SIZE, 
                              CELL_SIZE, CELL_SIZE))
    
    def draw_score(self):
        # Dessiner le score en bas de l'écran
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, self.height + 10))
    
    def move_piece(self, dx, dy):
        original_pos = self.piece["position"]
        self.piece["position"] = (self.piece["position"][0] + dx, self.piece["position"][1] + dy)
        
        if self.check_collision(self.piece):
            # Annuler le mouvement s'il y a collision
            self.piece["position"] = original_pos
            
            # Si la collision est vers le bas, figer la pièce
            if dy > 0:
                for x, y in self.piece["shape"]:
                    grid_x = self.piece["position"][0] + x
                    grid_y = self.piece["position"][1] + y
                    if 0 <= grid_y < GRID_HEIGHT:
                        self.grid[grid_y][grid_x] = self.piece["color"]
                
                # Vérifier et supprimer les lignes complètes
                self.clear_lines()
                
                # Générer une nouvelle pièce
                self.piece = self.generate_piece()
                
                # Vérifier la fin du jeu
                if self.check_collision(self.piece):
                    self.game_over = True
    
    def rotate_piece(self):
        original_shape = self.piece["shape"]
        self.piece["shape"] = self.rotate(self.piece["shape"])
        
        if self.check_collision(self.piece):
            # Annuler la rotation s'il y a collision
            self.piece["shape"] = original_shape
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.move_piece(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.move_piece(1, 0)
                elif event.key == pygame.K_DOWN:
                    self.soft_drop = True
                    self.soft_drop_score = 0
                elif event.key == pygame.K_UP:
                    self.rotate_piece()
            
            # Track key release for soft drop
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    self.soft_drop = False
        
        return True
    
    def run(self):
        while not self.game_over:
            # Gérer les événements
            if not self.handle_events():
                break
            
            # Descente automatique ou rapide de la pièce
            current_time = pygame.time.get_ticks()
            if current_time - self.last_drop_time > (self.drop_speed // (2 if self.soft_drop else 1)):
                rows_dropped = self.move_piece(0, 1)
                if self.soft_drop:
                    self.soft_drop_score += 1  # 1 point par ligne de descente rapide
                self.last_drop_time = current_time
            
            # Dessiner
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_piece(self.piece)
            self.draw_score()
            self.draw_preview_pieces()  # Dessiner les pièces à venir
            
            pygame.display.update()
            self.clock.tick(60)  # 60 FPS
        
        # Game Over
        self.show_game_over()
    
    def show_game_over(self):
        pygame.mixer.music.stop()
        self.screen.fill(BLACK)
        game_over_text = self.font.render("Game Over", True, RED)
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        
        self.screen.blit(game_over_text, (self.width // 2 - game_over_text.get_width() // 2, self.height // 2 - 50))
        self.screen.blit(score_text, (self.width // 2 - score_text.get_width() // 2, self.height // 2 + 50))
        
        pygame.display.update()
        
        # Attendre avant de quitter
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

    def draw_preview_pieces(self):
        # Dessiner le titre "Next"
        next_text = self.font.render("Next", True, WHITE)
        self.screen.blit(next_text, (self.game_width + 10, 10))
        
        # Dessiner les 3 prochaines pièces
        for i, next_piece in enumerate(self.next_pieces):
            # Position de prévisualisation avec plus d'espace
            start_x = self.game_width + (self.preview_width - 4 * PREVIEW_CELL_SIZE) // 2
            start_y = 100 + i * 120  # Augmenter l'espacement vertical
            
            # Dessiner le cadre de prévisualisation
            pygame.draw.rect(self.screen, DARK_GRAY, 
                             (self.game_width, start_y - 20, self.preview_width, 100), 2)
            
            # Dessiner la pièce
            for x, y in next_piece["shape"]:
                pygame.draw.rect(self.screen, next_piece["color"], 
                                 (start_x + x * PREVIEW_CELL_SIZE, 
                                  start_y + y * PREVIEW_CELL_SIZE, 
                                  PREVIEW_CELL_SIZE, PREVIEW_CELL_SIZE))
                pygame.draw.rect(self.screen, WHITE, 
                                 (start_x + x * PREVIEW_CELL_SIZE, 
                                  start_y + y * PREVIEW_CELL_SIZE, 
                                  PREVIEW_CELL_SIZE, PREVIEW_CELL_SIZE), 1)
    
    def move_piece(self, dx, dy):
        original_pos = self.piece["position"]
        self.piece["position"] = (self.piece["position"][0] + dx, self.piece["position"][1] + dy)
        
        if self.check_collision(self.piece):
            # Annuler le mouvement s'il y a collision
            self.piece["position"] = original_pos
            
            # Si la collision est vers le bas, figer la pièce
            if dy > 0:
                for x, y in self.piece["shape"]:
                    grid_x = self.piece["position"][0] + x 
                    grid_y = self.piece["position"][1] + y 
                    if 0 <= grid_y < GRID_HEIGHT:
                        self.grid[grid_y][grid_x] = self.piece["color"]
                
                # Vérifier et supprimer les lignes complètes
                self.clear_lines()
                
                # Ajouter le score de descente rapide
                self.score += self.soft_drop_score
                
                # Passer à la prochaine pièce
                self.piece = self.next_pieces.pop(0)
                self.piece["position"] = (GRID_WIDTH // 2 - 1, 0)
                
                # Réinitialiser le soft drop
                self.soft_drop = False
                self.soft_drop_score = 0
                
                # Générer une nouvelle pièce pour la prévisualisation
                self.next_pieces.append(self.generate_piece())
                
                # Vérifier la fin du jeu
                if self.check_collision(self.piece):
                    self.game_over = True
    
    def run(self):
        while not self.game_over:
            # Gérer les événements
            if not self.handle_events():
                break
            
            # Descente automatique ou rapide de la pièce
            current_time = pygame.time.get_ticks()
            if current_time - self.last_drop_time > (self.drop_speed // (2 if self.soft_drop else 1)):
                rows_dropped = self.move_piece(0, 1)
                if self.soft_drop:
                    self.soft_drop_score += 1  # 1 point par ligne de descente rapide
                self.last_drop_time = current_time
            
            # Dessiner
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_piece(self.piece)
            self.draw_score()
            self.draw_preview_pieces()  # Dessiner les pièces à venir
            
            pygame.display.update()
            self.clock.tick(60)  # 60 FPS
        
        # Game Over
        self.show_game_over()

# Le reste du code reste identique
def main():
    game = Tetris()
    game.run()

if __name__ == "__main__":
    main()