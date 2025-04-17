import pygame
import random
import sys
import os
import pygame_menu

# --- INIT ---
pygame.init()
pygame.display.init()
try:
    pygame.mixer.init()
except Exception as e:
    print("Error initializing mixer:", e)

# --- GLOBALS ---
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
SCOREBOARD_WIDTH = int(WIDTH * 0.2)  # 20% of screen width
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
FPS = 60

# Difficulty mapping
DIFFICULTY_SPEED_MAP = {'Easy': 1, 'Medium': 2, 'Hard': 3}
# Spawn rate mapping: lower is faster spawning
SPAWN_RATE_MAP = {'Easy': 80, 'Medium': 50, 'Hard': 30}
current_difficulty = 'Medium'

# Highscore file pattern per difficulty
HIGHSCORE_FILE_PATTERN = "highscores_{}.txt"

# --- AUDIO ---
try:
    pygame.mixer.music.load("BGM.mp3")
except Exception as e:
    print("Error loading background music:", e)
try:
    game_over_sound = pygame.mixer.Sound("game_over.wav")
except Exception as e:
    print("Error loading game over sound:", e)

# --- FONTS ---
font = pygame.font.SysFont(None, 36)

# --- HIGHSCORE SYSTEM ---
def get_highscores_filename():
    return HIGHSCORE_FILE_PATTERN.format(current_difficulty.lower())

def load_highscores():
    highscores = []
    filename = get_highscores_filename()
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) == 2:
                        name, s = parts
                        try:
                            highscores.append((name, int(s)))
                        except ValueError:
                            continue
        except Exception as e:
            print(f"Error loading highscores from {filename}: {e}")
    return highscores

def save_highscores(highscores):
    filename = get_highscores_filename()
    try:
        with open(filename, "w") as f:
            for name, score in highscores:
                f.write(f"{name},{score}\n")
    except Exception as e:
        print(f"Error saving highscores to {filename}: {e}")

def update_highscores(name, score):
    highscores = load_highscores()
    updated = False
    for i, (n, s) in enumerate(highscores):
        if n == name:
            if score > s:
                highscores[i] = (name, score)
            updated = True
            break
    if not updated:
        highscores.append((name, score))
    highscores.sort(key=lambda x: x[1], reverse=True)
    highscores = highscores[:10]
    save_highscores(highscores)
    return highscores

# --- DRAWING ---
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    surface.blit(text_obj, (x, y))

# --- COLLISION ---
def circle_rectangle_collision(circle, rect):
    cx, cy = circle['x'], circle['y']
    r = circle['radius']
    closest_x = max(rect.left, min(cx, rect.right))
    closest_y = max(rect.top, min(cy, rect.bottom))
    return (cx - closest_x) ** 2 + (cy - closest_y) ** 2 < r ** 2

# --- SPAWN CIRCLE ---
def spawn_circle(gameplay_width, circle_radius):
    x_pos = random.randint(circle_radius, gameplay_width - circle_radius)
    y_pos = -circle_radius
    return {'x': x_pos, 'y': y_pos, 'radius': circle_radius}

# --- GET PLAYER NAME ---
def get_player_name(screen, font, clock, score, WIDTH, HEIGHT):
    name = ""
    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 12 and event.unicode.isprintable():
                        name += event.unicode
        screen.fill(BLACK)
        draw_text("GAME OVER", font, RED, screen, 40, HEIGHT // 2 - 80)
        draw_text(f"Your Score: {score}", font, WHITE, screen, 40, HEIGHT // 2 - 40)
        draw_text("Enter your name: " + name, font, WHITE, screen, 40, HEIGHT // 2)
        pygame.display.update()
        clock.tick(FPS)
    return name.strip() or "Player"

# --- GAME OVER ---
def game_over(screen, font, clock, score, WIDTH, HEIGHT, SCOREBOARD_WIDTH):
    try:
        pygame.mixer.music.stop()
        game_over_sound.play()
    except Exception as e:
        print(f"Error playing game over sound: {e}")
    player_name = get_player_name(screen, font, clock, score, WIDTH, HEIGHT)
    highscores = update_highscores(player_name, score)
    waiting = True
    while waiting:
        screen.fill(BLACK)
        draw_text("GAME OVER", font, RED, screen, 20, 20)
        draw_text(f"Your Score: {score}", font, WHITE, screen, 20, 60)
        draw_text(f"Difficulty: {current_difficulty}", font, WHITE, screen, 20, 100)
        draw_text("Press R to Restart, Q to Menu", font, WHITE, screen, 20, HEIGHT - 50)
        pygame.draw.line(screen, WHITE, (WIDTH - SCOREBOARD_WIDTH, 0), (WIDTH - SCOREBOARD_WIDTH, HEIGHT), 2)
        x_off = WIDTH - SCOREBOARD_WIDTH + 10
        y_off = 20
        draw_text("High Scores:", font, WHITE, screen, x_off, y_off)
        for i, (n, s) in enumerate(highscores, start=1):
            y_off += 20
            draw_text(f"{i}. {n} - {s}", font, WHITE, screen, x_off, y_off)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main_game()
                    return
                elif event.key == pygame.K_q:
                    main()
                    return
        clock.tick(FPS)

# --- MAIN GAME ---
def main_game():
    global current_difficulty, WIDTH, HEIGHT, SCOREBOARD_WIDTH
    SCOREBOARD_WIDTH = int(WIDTH * 0.2)
    gameplay_width = WIDTH - SCOREBOARD_WIDTH
    player_w, player_h = 50, 50
    player_speed = 7
    circle_radius = 20
    base_speed = 6
    spawn_rate = SPAWN_RATE_MAP[current_difficulty]
    speed_inc = DIFFICULTY_SPEED_MAP[current_difficulty]
    circles = []
    score = 0
    stage = 1
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    pygame.mixer.music.play(-1)
    player_x = gameplay_width // 2 - player_w // 2
    player_y = HEIGHT - player_h - 10
    timer = 0
    running = True
    while running:
        clock.tick(FPS)
        timer += 1
        if timer >= spawn_rate:
            circles.append(spawn_circle(gameplay_width, circle_radius))
            timer = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < gameplay_width - player_w:
            player_x += player_speed
        for c in circles:
            c['y'] += base_speed + (stage - 1) * speed_inc
        circles = [c for c in circles if c['y'] - c['radius'] < HEIGHT]
        player_rect = pygame.Rect(player_x, player_y, player_w, player_h)
        if any(circle_rectangle_collision(c, player_rect) for c in circles):
            game_over(screen, font, clock, score, WIDTH, HEIGHT, SCOREBOARD_WIDTH)
            return
        score += 1
        stage = score // 1000 + 1
        screen.fill(BLACK)
        pygame.draw.rect(screen, BLUE, player_rect)
        for c in circles:
            pygame.draw.circle(screen, RED, (int(c['x']), int(c['y'])), c['radius'])
        draw_text(f"Score: {score}", font, WHITE, screen, 10, 10)
        draw_text(f"Stage: {stage}", font, WHITE, screen, 10, 40)
        pygame.draw.line(screen, WHITE, (gameplay_width, 0), (gameplay_width, HEIGHT), 2)
        highscores = load_highscores()
        x_off = gameplay_width + 10
        y_off = 10
        draw_text(f"High Scores ({current_difficulty}):", font, WHITE, screen, x_off, y_off)
        for i, (n, s) in enumerate(highscores, start=1):
            y_off += 20
            draw_text(f"{i}. {n} - {s}", font, WHITE, screen, x_off, y_off)
        pygame.display.update()

# --- MENU ---
def set_difficulty(selected, value):
    global current_difficulty
    current_difficulty = value

def main():
    global WIDTH, HEIGHT, SCOREBOARD_WIDTH
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Falling Circles - Menu")
    menu = pygame_menu.Menu('Falling Circles', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
    menu.add.selector('Difficulty :', [('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')], default=1, onchange=set_difficulty)
    menu.add.button('Start', main_game)
    menu.add.button('Exit', pygame_menu.events.EXIT)
    menu.mainloop(screen)

if __name__ == "__main__":
    main()
