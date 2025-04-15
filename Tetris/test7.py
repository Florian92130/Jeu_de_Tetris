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

def get_high_score():
    try:
        with open('high_score.txt', 'r') as file:
            return int(file.read().strip())
    except (FileNotFoundError, ValueError):
        return 0

def save_high_score(score):
    with open('high_score.txt', 'w') as file:
        file.write(str(score))

class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, 36)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

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
        self.soft_drop_speed = 50
        
        # Police pour les stats
        self.stats_font = pygame.font.Font(None, 36)

        # Initialiser le high score
        self.high_score = get_high_score()

        # Nouvelles statistiques
        self.total_lines_cleared = 0
        self.level = 1
        self.lines_to_next_level = 10
        
        # Initialiser la vitesse de base
        self.base_drop_speed = 500
        # Initialiser le reste du jeu
        self.reset_game()
        
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

        self.move_left = False
        self.move_right = False
        self.move_delay = 200  # Initial delay before rapid movement
        self.move_interval = 50  # Interval between movements after initial delay
        self.last_move_time = 0
        self.move_cooldown = 0

    def reset_game(self):
        self.grid = self.create_empty_grid()
        self.piece = self.generate_piece()
        self.next_pieces = [self.generate_piece() for _ in range(3)]
        self.score = 0
        self.clock = pygame.time.Clock()
        self.game_over = False
        
        # Variables de contrôle
        self.drop_time = 0
        self.drop_speed = 500  # Temps en millisecondes entre chaque descente automatique
        self.last_drop_time = pygame.time.get_ticks()

        self.move_left = False
        self.move_right = False
        self.move_delay = 200
        self.move_interval = 50
        self.last_move_time = 0
        self.move_cooldown = 0
        
        self.soft_drop = False
        self.soft_drop_score = 0
        self.soft_drop_speed = 50

        self.total_lines_cleared = 0
        self.level = 1
        self.lines_to_next_level = 10
        
        # Réinitialiser la vitesse de descente
        self.drop_speed = self.base_drop_speed
        
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
        # Trouver les lignes complètes
        lines_to_clear = [i for i, row in enumerate(self.grid) if all(cell != 0 for cell in row)]
        
        # Supprimer les lignes complètes
        for i in lines_to_clear:
            self.grid.pop(i)
            self.grid.insert(0, [0] * GRID_WIDTH)
        
        # Calculer le nombre de lignes complétées
        lines_cleared = len(lines_to_clear)
        
        # Mettre à jour le nombre total de lignes complétées
        self.total_lines_cleared += lines_cleared
        
        # Calculer le score
        score_multipliers = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}
        self.score += score_multipliers.get(lines_cleared, 1200)
        
        # Gérer le passage de level
        self.lines_to_next_level -= lines_cleared
        
        # Augmenter le level si nécessaire
        if self.lines_to_next_level <= 0:
            self.level_up()
    
    def draw_grid(self):
        # Fill the entire grid background with black
        self.screen.fill(BLACK)
        
        # Draw the grid with gray borders
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                # Draw the cell color or black for empty cells
                cell_color = self.grid[y][x] if self.grid[y][x] != 0 else BLACK
                pygame.draw.rect(self.screen, cell_color, 
                                (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                
                # Draw gray border for each cell
                pygame.draw.rect(self.screen, DARK_GRAY, 
                                (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
    
    def draw_piece(self, piece):
        for x, y in piece["shape"]:
            pygame.draw.rect(self.screen, piece["color"], 
                            ((piece["position"][0] + x) * CELL_SIZE, 
                            (piece["position"][1] + y) * CELL_SIZE, 
                            CELL_SIZE, CELL_SIZE))
            # Add dark gray border to each piece block
            pygame.draw.rect(self.screen, DARK_GRAY, 
                            ((piece["position"][0] + x) * CELL_SIZE, 
                            (piece["position"][1] + y) * CELL_SIZE, 
                            CELL_SIZE, CELL_SIZE), 1)
    
    def level_up(self):
        # Augmenter le level
        self.level += 1
        
        # Réinitialiser les lignes pour le prochain level
        self.lines_to_next_level = 10
        
        # Accélérer la chute des pièces
        # Plus le level est élevé, plus la vitesse de descente est rapide
        # Diminuer le drop_speed de 10% à chaque level
        self.drop_speed = max(50, int(self.base_drop_speed * (0.9 ** (self.level - 1))))
        
        # Option: rendre le soft drop aussi plus rapide
        self.soft_drop_speed = max(25, int(self.soft_drop_speed * (0.9 ** (self.level - 1))))

    def draw_score(self):
        # Nettoyer la zone de score
        pygame.draw.rect(self.screen, BLACK, (0, self.height, self.width, 50))
        
        # Position pour centrer les statistiques
        center_x = self.width // 2
        
        # Créer les surfaces de texte avec la nouvelle police
        level_text = self.stats_font.render(f"Level: {self.level}", True, CYAN)
        lines_text = self.stats_font.render(f"Lines: {self.total_lines_cleared}", True, GREEN)
        score_text = self.stats_font.render(f"Score: {self.score}", True, WHITE)
        
        # Positionner les textes de manière espacée
        level_rect = level_text.get_rect(center=(center_x - 150, self.height + 25))
        lines_rect = lines_text.get_rect(center=(center_x, self.height + 25))
        score_rect = score_text.get_rect(center=(center_x + 150, self.height + 25))
        
        # Dessiner les textes
        self.screen.blit(level_text, level_rect)
        self.screen.blit(lines_text, lines_rect)
        self.screen.blit(score_text, score_rect)

    
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
                    self.move_left = True
                    self.move_right = False
                    self.last_move_time = pygame.time.get_ticks()
                elif event.key == pygame.K_RIGHT:
                    self.move_right = True
                    self.move_left = False
                    self.last_move_time = pygame.time.get_ticks()
                elif event.key == pygame.K_DOWN:
                    self.soft_drop = True
                elif event.key == pygame.K_UP:
                    self.rotate_piece()
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.move_left = False
                elif event.key == pygame.K_RIGHT:
                    self.move_right = False
                elif event.key == pygame.K_DOWN:
                    self.soft_drop = False
                    self.soft_drop_score = 0
        
        return True
    
    def run(self):
        while True:  # Boucle principale pour permettre le replay
            # Réinitialiser le jeu avant chaque partie
            self.reset_game()
            
            # Jouer une partie
            while not self.game_over:
                # [Le reste du code de run() reste identique]
                if not self.handle_events():
                    pygame.quit()
                    sys.exit()
                
                current_time = pygame.time.get_ticks()
                move_time = self.move_delay if self.move_cooldown == 0 else self.move_interval
                
                if (self.move_left or self.move_right) and current_time - self.last_move_time > move_time:
                    if self.move_left:
                        self.move_piece(-1, 0)
                    elif self.move_right:
                        self.move_piece(1, 0)
                    
                    self.last_move_time = current_time
                    self.move_cooldown = 1
                
                drop_interval = self.soft_drop_speed if self.soft_drop else self.drop_speed
                
                if current_time - self.last_drop_time > drop_interval:
                    original_y = self.piece["position"][1]
                    self.move_piece(0, 1)
                    
                    if self.soft_drop:
                        lines_dropped = self.piece["position"][1] - original_y
                        self.score += lines_dropped
                    
                    self.last_drop_time = current_time
                
                self.screen.fill(BLACK)
                self.draw_grid()
                self.draw_piece(self.piece)
                self.draw_score()
                self.draw_preview_pieces()
                
                pygame.display.update()
                self.clock.tick(60)
            
            # Afficher l'écran de game over et attendre un replay
            if self.show_game_over():
                continue  # Recommencer une nouvelle partie
            else:
                break  # Quitter le jeu
    
    def show_game_over(self):
        # Mettre à jour le high score si nécessaire
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.high_score)
        
        # Créer le bouton replay
        replay_button = Button(
            self.width // 2 - 100, 
            self.height // 2 + 100, 
            200, 50, 
            "Replay", 
            GREEN, 
            WHITE
        )
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if replay_button.is_clicked(event.pos):
                        return True  # Signal pour redémarrer le jeu
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return True  # Redémarrer avec la touche R
            
            self.screen.fill(BLACK)
            
            # Texte Game Over
            game_over_text = self.font.render("Game Over", True, RED)
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            high_score_text = self.font.render(f"High Score: {self.high_score}", True, YELLOW)
            
            self.screen.blit(game_over_text, (self.width // 2 - game_over_text.get_width() // 2, self.height // 2 - 100))
            self.screen.blit(score_text, (self.width // 2 - score_text.get_width() // 2, self.height // 2 - 50))
            self.screen.blit(high_score_text, (self.width // 2 - high_score_text.get_width() // 2, self.height // 2))
            
            # Dessiner le bouton replay
            replay_button.draw(self.screen)
            
            pygame.display.update()
            self.clock.tick(30)

    def draw_preview_pieces(self):
        # Dessiner le titre "Next"
        next_text = self.stats_font.render("Next", True, WHITE)
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
        while True:  # Boucle principale pour permettre le replay
            # Réinitialiser le jeu avant chaque partie
            self.reset_game()
            
            # Jouer une partie
            while not self.game_over:
                # [Le reste du code de run() reste identique]
                if not self.handle_events():
                    pygame.quit()
                    sys.exit()
                
                current_time = pygame.time.get_ticks()
                move_time = self.move_delay if self.move_cooldown == 0 else self.move_interval
                
                if (self.move_left or self.move_right) and current_time - self.last_move_time > move_time:
                    if self.move_left:
                        self.move_piece(-1, 0)
                    elif self.move_right:
                        self.move_piece(1, 0)
                    
                    self.last_move_time = current_time
                    self.move_cooldown = 1
                
                drop_interval = self.soft_drop_speed if self.soft_drop else self.drop_speed
                
                if current_time - self.last_drop_time > drop_interval:
                    original_y = self.piece["position"][1]
                    self.move_piece(0, 1)
                    
                    if self.soft_drop:
                        lines_dropped = self.piece["position"][1] - original_y
                        self.score += lines_dropped
                    
                    self.last_drop_time = current_time
                
                self.screen.fill(BLACK)
                self.draw_grid()
                self.draw_piece(self.piece)
                self.draw_score()
                self.draw_preview_pieces()
                
                pygame.display.update()
                self.clock.tick(60)
            
            # Afficher l'écran de game over et attendre un replay
            if self.show_game_over():
                continue  # Recommencer une nouvelle partie
            else:
                break  # Quitter le jeu

# Le reste du code reste identique
def main():
    game = Tetris()
    game.run()

if __name__ == "__main__":
    main()