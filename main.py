import pygame
import time
import random
import json
import os
from datetime import datetime

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 600
HEIGHT = 400
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ORANGE = (255, 140, 0)
PURPLE = (147, 112, 219)
GREEN = (60, 179, 113)
RED = (255, 0, 0)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Halloween Candyland Adventure")

# Font initialization
try:
    TITLE_FONT = pygame.font.SysFont('Courier', 48)
    TEXT_FONT = pygame.font.SysFont('Courier', 24)
    SMALL_FONT = pygame.font.SysFont('Courier', 18)
except:
    TITLE_FONT = pygame.font.Font(None, 48)
    TEXT_FONT = pygame.font.Font(None, 24)
    SMALL_FONT = pygame.font.Font(None, 18)

class ImageLoader:
    def __init__(self):
        self.images = {}
        self.load_images()
    
    def load_images(self):
        image_files = {
            'cover': 'cover.png',
            'player1': 'character1.png',
            'player2': 'character2.png',
            'player3': 'character3.png',
            'player4': 'character4.png',
            'player5': 'character5.png',
            'path': 'path.png'
        }
        
        for key, filename in image_files.items():
            try:
                img = pygame.image.load(filename)
                img = pygame.transform.scale(img, (80, 80))
                self.images[key] = img
            except:
                self.images[key] = None

class Monster:
    def __init__(self, name, difficulty, question_type):
        self.name = name
        self.difficulty = difficulty
        self.question_type = question_type
        self.defeated = False

    def generate_question(self):
        if self.question_type == "probability":
            num1 = random.randint(1, 6)
            num2 = random.randint(1, 6)
            answer = num1 / num2
            question = f"What is the probability of rolling a {num1} on a {num2}-sided die?"
            return question, answer

class MonsterManager:
    def __init__(self):
        self.monsters = self.load_monsters()
    
    def load_monsters(self):
        # This would typically load from a monsters.json file
        return [
            Monster("Spooky Ghost", 1, "probability"),
            Monster("Wicked Witch", 2, "probability"),
            Monster("Vampire Lord", 3, "probability"),
            Monster("Zombie Horde", 2, "probability"),
            Monster("Skeleton King", 3, "probability")
        ]
    
    def get_random_monster(self):
        return random.choice(self.monsters)

class Player:
    def __init__(self, character_id=1):
        self.character_id = character_id
        self.name = f"Player {character_id}"
        self.custom_name = ""
        self.position = 0
        self.completion_time = 0
        self.current_level = 0
        self.levels_completed = []

    def set_custom_name(self, name):
        if self.validate_name(name):
            self.custom_name = name
            return True
        return False

    @staticmethod
    def validate_name(name):
        # Add your name validation rules here
        return (len(name) >= 2 and len(name) <= 15 and 
                name.replace(' ', '').isalnum())

class Leaderboard:
    def __init__(self):
        self.scores = self.load_scores()
    
    def load_scores(self):
        try:
            with open('leaderboard.json', 'r') as f:
                return json.load(f)
        except:
            return []
    
    def save_scores(self):
        try:
            with open('leaderboard.json', 'w') as f:
                json.dump(self.scores, f)
        except:
            pass
    
    def add_score(self, player_name, time):
        score = {
            'name': player_name,
            'time': time,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.scores.append(score)
        self.scores.sort(key=lambda x: x['time'])
        self.scores = self.scores[:10]  # Keep only top 10
        self.save_scores()

class ParkourLevel:
    def __init__(self, level_num):
        self.level_num = level_num
        self.platforms = self.generate_platforms()
        self.monsters = []
        self.completed = False
        
    def generate_platforms(self):
        platforms = []
        num_platforms = random.randint(5, 8)
        for _ in range(num_platforms):
            x = random.randint(0, WIDTH - 60)
            y = random.randint(100, HEIGHT - 60)
            platforms.append(pygame.Rect(x, y, 60, 20))
        return platforms

    def add_monster(self, monster):
        self.monsters.append(monster)

class Game:
    def __init__(self):
        self.state = "START"
        self.images = ImageLoader()
        self.leaderboard = Leaderboard()
        self.monster_manager = MonsterManager()
        self.players = []
        self.current_player = None
        self.game_timer = 0
        self.game_started = False
        self.current_level = None
        self.levels = []
        self.destiny_cards = [
            "Move forward 2 spaces",
            "Move back 1 space",
            "Skip next turn",
            "Take an extra turn",
            "Challenge another player"
        ]

    def init_levels(self):
        self.levels = [ParkourLevel(i) for i in range(7)]
        for level in self.levels:
            level.add_monster(self.monster_manager.get_random_monster())

    def draw_character_selection(self):
        screen.fill(BLACK)
        title = TITLE_FONT.render("Choose Your Character", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        for i in range(5):
            x = 50 + i * 120
            y = HEIGHT//2 - 40
            
            if self.images.images[f'player{i+1}']:
                screen.blit(self.images.images[f'player{i+1}'], (x, y))
            else:
                pygame.draw.rect(screen, PURPLE, (x, y, 80, 80))
            
            name = TEXT_FONT.render(f"Player {i+1}", True, WHITE)
            screen.blit(name, (x, y + 90))

    def draw_name_input(self):
        screen.fill(BLACK)
        title = TITLE_FONT.render("Enter Your Name", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
        
        rules = [
            "Name Rules:",
            "- 2-15 characters",
            "- Letters and numbers only",
            "- Spaces allowed"
        ]
        
        for i, rule in enumerate(rules):
            text = SMALL_FONT.render(rule, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + i*25))

    def draw_path_page(self):
        screen.fill(BLACK)
        if self.images.images['path']:
            screen.blit(self.images.images['path'], (0, 0))
        else:
            # Draw default path if no image
            for i, level in enumerate(self.levels):
                x = 80 + i * 80
                y = HEIGHT//2
                color = GREEN if level.completed else WHITE
                pygame.draw.rect(screen, color, (x-20, y-20, 40, 40))

        # Draw timer
        timer_text = TEXT_FONT.render(f"Time: {int(self.game_timer)}s", True, WHITE)
        screen.blit(timer_text, (10, 10))

    def draw_destiny_card(self, card_text):
        screen.fill(BLACK)
        title = TITLE_FONT.render("Destiny Card", True, ORANGE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
        
        text = TEXT_FONT.render(card_text, True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))

    def draw_leaderboard(self):
        screen.fill(BLACK)
        title = TITLE_FONT.render("Leaderboard", True, ORANGE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        for i, score in enumerate(self.leaderboard.scores):
            text = TEXT_FONT.render(
                f"{i+1}. {score['name']} - {score['time']}s", 
                True, WHITE
            )
            screen.blit(text, (WIDTH//4, 100 + i*30))

    def handle_parkour_level(self):
        if self.current_level:
            screen.fill(BLACK)
            
            # Draw platforms
            for platform in self.current_level.platforms:
                pygame.draw.rect(screen, WHITE, platform)
            
            # Draw monsters and handle their questions
            for monster in self.current_level.monsters:
                if not monster.defeated:
                    # Draw monster and handle interaction
                    pass

    def run(self):
        clock = pygame.time.Clock()
        running = True
        input_text = ""
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if self.state == "NAME_INPUT":
                        if event.key == pygame.K_RETURN:
                            if self.current_player.set_custom_name(input_text):
                                self.state = "GAME"
                                self.game_started = True
                        elif event.key == pygame.K_BACKSPACE:
                            input_text = input_text[:-1]
                        else:
                            input_text += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == "CHARACTER_SELECT":
                        # Handle character selection
                        mouse_pos = pygame.mouse.get_pos()
                        for i in range(5):
                            x = 50 + i * 120
                            y = HEIGHT//2 - 40
                            if pygame.Rect(x, y, 80, 80).collidepoint(mouse_pos):
                                self.current_player = Player(i+1)
                                self.state = "NAME_INPUT"

            if self.game_started and self.state not in ["WIN", "DESTINY_CARD"]:
                self.game_timer += clock.get_time() / 1000

            # Draw current state
            if self.state == "START":
                screen.fill(BLACK)
                if self.images.images['cover']:
                    screen.blit(self.images.images['cover'], (0, 0))
                # Draw start screen elements
            elif self.state == "CHARACTER_SELECT":
                self.draw_character_selection()
            elif self.state == "NAME_INPUT":
                self.draw_name_input()
                # Draw input text
                text_surface = TEXT_FONT.render(input_text, True, WHITE)
                screen.blit(text_surface, (WIDTH//2 - text_surface.get_width()//2, 
                                         2*HEIGHT//3))
            elif self.state == "GAME":
                self.draw_path_page()
            elif self.state == "PARKOUR":
                self.handle_parkour_level()
            elif self.state == "DESTINY_CARD":
                self.draw_destiny_card(random.choice(self.destiny_cards))
            elif self.state == "LEADERBOARD":
                self.draw_leaderboard()
            elif self.state == "WIN":
                screen.fill(BLACK)
                win_text = TITLE_FONT.render(
                    f"Victory! Time: {int(self.game_timer)}s", 
                    True, ORANGE
                )
                screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2))

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.init_levels()
    game.run()
