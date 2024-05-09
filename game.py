import pygame
import random
import os
import sys

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
PIPE_WIDTH = 100
PIPE_HEIGHT = 500
GRAVITY = 0.90
JUMP = 12
PIPE_SPEED = 7
GAP_SIZE = 200
PIPE_ADD_INTERVAL = 1500
PIPE_INITIAL_X = 500
BACKGROUND_COLOR = (135, 206, 250)  # Light blue color for background
BLUR_COLOR = (255, 255, 255, 50)  # Transparent white color for blur effect
BUTTON_COLOR = (0, 255, 0)  # Green color for button
BUTTON_TEXT_COLOR = (255, 255, 255)  # White color for button text

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Load images
current_dir = os.path.dirname(os.path.abspath(__file__))
try:
    bird_img = pygame.image.load(os.path.join(current_dir, 'bird.png')).convert_alpha()
    bird_img = pygame.transform.scale(bird_img, (50, 50))
    pipe_img = pygame.image.load(os.path.join(current_dir, 'pipe.png')).convert_alpha()  # Changed image name
except FileNotFoundError:
    print("Error: Could not find image files 'bird.png' or 'pipe2.jpeg'. Make sure they are in the correct directory.")
    pygame.quit()
    sys.exit()

# Font for rendering text
font = pygame.font.SysFont(None, 36)

class Bird:
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        # Scale up the bird image
        self.image = pygame.transform.scale(bird_img, (70, 70))

    def jump(self):
        self.velocity = -JUMP

    def move(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def draw(self):
        screen.blit(self.image, (self.x, self.y))


class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(50, SCREEN_HEIGHT - GAP_SIZE - 50)
        self.passed = False  # Indicates whether bird has passed this pair of pipes

    def move(self):
        self.x -= PIPE_SPEED

    def draw(self):
        # Draw upper pipe
        screen.blit(pygame.transform.scale(pipe_img, (PIPE_WIDTH, self.height)), (self.x, 0))
        # Draw lower pipe
        screen.blit(pygame.transform.scale(pipe_img, (PIPE_WIDTH, SCREEN_HEIGHT - self.height - GAP_SIZE)), (self.x, self.height + GAP_SIZE))

class Ground:
    def __init__(self):
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT

    def draw(self):
        pygame.draw.rect(screen, GROUND_COLOR, (0, self.y, SCREEN_WIDTH, GROUND_HEIGHT))

def add_pipe():
    pipes.append(Pipe(PIPE_INITIAL_X))

def update_score():
    global score
    score += 1

def show_game_over():
    # Create a surface for the blur effect
    blur_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    blur_surface.fill(BLUR_COLOR)
    screen.blit(blur_surface, (0, 0))

    # Render "You Lost" text
    text = font.render("You Lost , You Have " + str(score) + " Points", True, (255, 0, 0))  # Red color
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
    screen.blit(text, text_rect)

    # Render retry button
    button_rect = pygame.Rect(150, SCREEN_HEIGHT // 2 + 20, 100, 50)
    pygame.draw.rect(screen, BUTTON_COLOR, button_rect)
    button_text = font.render("Retry", True, BUTTON_TEXT_COLOR)
    text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, text_rect)
    return button_rect

bird = Bird()
pipes = []
score = 0
game_over = False

add_pipe_event = pygame.USEREVENT + 1
pygame.time.set_timer(add_pipe_event, PIPE_ADD_INTERVAL)

# Ground initialization
GROUND_HEIGHT = 50
GROUND_COLOR = (0, 128, 0)  # Dark green color for ground
ground = Ground()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                bird.jump()
            elif event.key == pygame.K_RETURN and game_over:
                # Restart the game
                bird = Bird()
                pipes = []
                score = 0
                game_over = False
                pygame.time.set_timer(add_pipe_event, PIPE_ADD_INTERVAL)
        elif event.type == pygame.MOUSEBUTTONDOWN and game_over:
            # Check if the retry button is clicked
            button_rect = show_game_over()
            if button_rect.collidepoint(event.pos):
                # Restart the game
                bird = Bird()
                pipes = []
                score = 0
                game_over = False
                pygame.time.set_timer(add_pipe_event, PIPE_ADD_INTERVAL)

        elif event.type == add_pipe_event:
            add_pipe()

    screen.fill(BACKGROUND_COLOR)

    if not game_over:
        bird.move()
        bird.draw()

        # Collision detection with ground
        if bird.y + bird_img.get_height() > ground.y:
            game_over = True

        for pipe in pipes:
            pipe.move()
            pipe.draw()
            # Check if bird has passed through this pair of pipes
            if not pipe.passed and pipe.x + PIPE_WIDTH < bird.x:
                pipe.passed = True
                update_score()

        # Collision detection
        for pipe in pipes:
            if bird.x + bird_img.get_width() > pipe.x and bird.x < pipe.x + PIPE_WIDTH:
                if bird.y < pipe.height or bird.y + bird_img.get_height() > pipe.height + GAP_SIZE:
                    # Collision occurred
                    game_over = True
                    pygame.time.set_timer(add_pipe_event, 0)  # Stop adding pipes
                    break

        # Remove pipes that have gone off screen
        pipes = [pipe for pipe in pipes if pipe.x > -PIPE_WIDTH]

        # Display score
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

    else:
        retry_button_rect = show_game_over()

    # Draw ground after pipes to make it appear on top
    ground.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
