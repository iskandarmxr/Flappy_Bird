import pygame
import random
import sys
import os

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 400, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Game constants
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -10
PIPE_WIDTH = 70
PIPE_GAP = 150

# Colors
WHITE = (255, 255, 255)
BLUE = (135, 206, 250)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Fonts
FONT = pygame.font.SysFont("Arial", 30)
BIG_FONT = pygame.font.SysFont("Arial", 45)

ASSETS_DIR = "assets"

# Load bird animation frames
bird_frames = [
    pygame.image.load(f"{ASSETS_DIR}/yellowbird-downflap.png"),
    pygame.image.load(f"{ASSETS_DIR}/yellowbird-midflap.png"),
    pygame.image.load(f"{ASSETS_DIR}/yellowbird-upflap.png")
]

# Load background
bg_image = pygame.image.load(f"{ASSETS_DIR}/background-day.png")
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

# Load base
base_image = pygame.image.load(f"{ASSETS_DIR}/base.png")
base_height = base_image.get_height()
BASE_Y = HEIGHT - base_height

# Load pipe
pipe_image = pygame.image.load(f"{ASSETS_DIR}/pipe-green.png")
pipe_image = pygame.transform.scale(pipe_image, (70, HEIGHT))  # just in case

message_image = pygame.image.load(f"{ASSETS_DIR}/message.png")
gameover_image = pygame.image.load(f"{ASSETS_DIR}/gameover.png")

# Optional scaling
message_image = pygame.transform.scale(message_image, (200, 300))
gameover_image = pygame.transform.scale(gameover_image, (192, 42))  # default size

class Bird:
    def __init__(self):
        self.x = 100
        self.y = HEIGHT // 2
        self.velocity = 0
        self.radius = 20
        self.frames = bird_frames
        self.index = 0
        self.frame_count = 0
        self.dead = False

    def jump(self):
        self.velocity = JUMP_STRENGTH

    def move(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.frame_count += 1
        if self.frame_count % 5 == 0:
            self.index = (self.index + 1) % len(self.frames)

    def draw(self):
        img = pygame.transform.scale(self.frames[self.index], (40, 40))
        SCREEN.blit(img, (self.x - 20, int(self.y) - 20))

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)
    def set_dead_pose(self):
        self.image = pygame.image.load("assets/yellowbird-downflap.png").convert_alpha()

class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(100, HEIGHT - PIPE_GAP - 100)
        self.passed = False

    def move(self):
        self.x -= 3

    def draw(self):
        top_pipe = pygame.transform.flip(pipe_image, False, True)
        bottom_pipe = pipe_image

        SCREEN.blit(top_pipe, (self.x, self.height - HEIGHT))
        SCREEN.blit(bottom_pipe, (self.x, self.height + PIPE_GAP))

    def collide(self, bird):
        bird_rect = bird.get_rect()
        top_pipe = pygame.Rect(self.x, 0, PIPE_WIDTH, self.height)
        bottom_pipe = pygame.Rect(self.x, self.height + PIPE_GAP, PIPE_WIDTH, HEIGHT)
        return bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe)

def draw_base():
    base_width = base_image.get_width()
    for x in range(0, WIDTH, base_width):
        SCREEN.blit(base_image, (x, HEIGHT - base_height))

def draw_window(bird, pipes, score, show_score=True):
    SCREEN.blit(bg_image, (0, 0))
    bird.draw()
    for pipe in pipes:
        pipe.draw()
    draw_base()

    if show_score:
        score_text = FONT.render(f"Score: {score}", True, WHITE)
        SCREEN.blit(score_text, (10, 10))

    pygame.display.update()
    
def show_start_screen():
    waiting = True
    while waiting:
        SCREEN.blit(bg_image, (0, 0))
        draw_base()
        SCREEN.blit(message_image, (WIDTH//2 - message_image.get_width()//2, HEIGHT//4))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

def draw_game_over(score, high_score):
    game_over_img = pygame.image.load("assets/gameover.png").convert_alpha()
    
    SCREEN.blit(game_over_img, ((WIDTH - game_over_img.get_width()) // 2, HEIGHT // 4))

    # Display score
    font = pygame.font.SysFont("Arial", 32)
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    high_text = font.render(f"High Score: {high_score}", True, (0, 0, 0))
    SCREEN.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 + 40))
    SCREEN.blit(high_text, (WIDTH//2 - high_text.get_width()//2, HEIGHT//2 + 80))

    # Try again button
    button_rect = pygame.Rect(WIDTH//2 - 80, HEIGHT//2 + 130, 160, 50)
    pygame.draw.rect(SCREEN, (255, 0, 0), button_rect)
    button_text = font.render("Try Again", True, (255, 255, 255))
    SCREEN.blit(button_text, (
        button_rect.x + (button_rect.width - button_text.get_width()) // 2,
        button_rect.y + (button_rect.height - button_text.get_height()) // 2
    ))

    pygame.display.update()
    return button_rect

def wait_for_retry(retry_rect):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_rect.collidepoint(pygame.mouse.get_pos()):
                    return  # Exit the loop to restart the game

def run_game():
    show_start_screen()
    clock = pygame.time.Clock()
    bird = Bird()
    pipes = [Pipe(WIDTH + 200)]
    score = 0
    game_over = False
    running = True

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if not game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird.jump()

        if not game_over:
            bird.move()

            for pipe in pipes:
                pipe.move()
                if pipe.collide(bird):
                    bird.set_dead_pose()
                    game_over = True

            if bird.y < 0 or bird.y + bird.radius >= BASE_Y:
                bird.set_dead_pose()
                game_over = True

            for pipe in pipes:
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    score += 1
                    pipes.append(Pipe(WIDTH + 200))

            pipes = [pipe for pipe in pipes if pipe.x + PIPE_WIDTH > 0]
        
            if not game_over:
                draw_window(bird, pipes, score)
            else:
                # Freeze the last drawn frame
                draw_window(bird, pipes, score, show_score=False)
                pygame.display.update()
                pygame.time.delay(500)  # Optional pause before showing Game Over

                high_score = get_high_score()
                if score > high_score:
                    save_high_score(score)
                    high_score = score

                retry_button = draw_game_over(score, high_score)
                wait_for_retry(retry_button)
                return
    
def get_high_score():
    if not os.path.exists("highscore.txt"):
        with open("highscore.txt", "w") as f:
            f.write("0")
    with open("highscore.txt", "r") as f:
        return int(f.read().strip())

def save_high_score(new_score):
    with open("highscore.txt", "w") as f:
        f.write(str(new_score))

def main():
    while True:
        run_game()

if __name__ == "__main__":
    main()