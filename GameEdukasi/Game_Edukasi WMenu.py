import pygame
import random
import sys
import os
import pygame_menu

# --- GLOBALS ---
WIDTH, HEIGHT = 800, 600
SCOREBOARD_WIDTH = 220
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
FPS = 60

# Difficulty mapping
DIFFICULTY_SPEED_MAP = {'Easy': 1, 'Medium': 2, 'Hard': 3}
current_difficulty = 'Medium'

# --- INIT ---
pygame.init()
try:
    pygame.mixer.init()
except Exception as e:
    print("Error initializing mixer:", e)

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
def load_highscores():
    highscores = []
    if os.path.exists("highscores.txt"):
        try:
            with open("highscores.txt", "r") as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) == 2:
                        name, s = parts
                        try:
                            s = int(s)
                            highscores.append((name, s))
                        except:
                            continue
        except Exception as e:
            print("Error loading highscores:", e)
    return highscores

def save_highscores(highscores):
    try:
        with open("highscores.txt", "w") as f:
            for name, s in highscores:
                f.write(f"{name},{s}\n")
    except Exception as e:
        print("Error saving highscores:", e)

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
    circle_x = circle['x']
    circle_y = circle['y']
    radius = circle['radius']
    closest_x = max(rect.left, min(circle_x, rect.right))
    closest_y = max(rect.top, min(circle_y, rect.bottom))
    distance_x = circle_x - closest_x
    distance_y = circle_y - closest_y
    return (distance_x**2 + distance_y**2) < (radius**2)

# --- SPAWN CIRCLE ---
def spawn_circle(WIDTH, SCOREBOARD_WIDTH, circle_radius):
    gameplay_width = WIDTH - SCOREBOARD_WIDTH
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
    return name if name.strip() else "Player"

# --- GAME OVER ---
def game_over(screen, font, clock, score, WIDTH, HEIGHT, SCOREBOARD_WIDTH):
    try:
        pygame.mixer.music.stop()
        game_over_sound.play()
    except Exception as e:
        print("Error playing game over sound:", e)
    player_name = get_player_name(screen, font, clock, score, WIDTH, HEIGHT)
    highscores = update_highscores(player_name, score)
    waiting = True
    while waiting:
        screen.fill(BLACK)
        draw_text("GAME OVER", font, RED, screen, 20, 20)
        draw_text(f"Your Score: {score}", font, WHITE, screen, 20, 60)
        draw_text("Press R to Restart, Q to Menu", font, WHITE, screen, 20, HEIGHT - 50)
        x_offset = WIDTH - SCOREBOARD_WIDTH + 10
        y_offset = 20
        draw_text("High Scores:", font, WHITE, screen, x_offset, y_offset)
        y_offset += 30
        for i, (n, s) in enumerate(highscores):
            draw_text(f"{i+1}. {n} - {s}", font, WHITE, screen, x_offset, y_offset)
            y_offset += 20
        pygame.draw.line(screen, WHITE, (WIDTH - SCOREBOARD_WIDTH, 0), (WIDTH - SCOREBOARD_WIDTH, HEIGHT), 2)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                    main_game()
                    return  # Ensure we exit game_over after restarting
                elif event.key == pygame.K_q:
                    waiting = False
                    main()  # Return to the main menu
                    return #exit this function
        clock.tick(FPS)

# --- MAIN GAME ---
def main_game():
    global current_difficulty
    # --- Game variables ---
    WIDTH, HEIGHT = 800, 600
    SCOREBOARD_WIDTH = 220
    player_width, player_height = 50, 50
    player_speed = 5
    circle_radius = 20
    base_circle_speed = 4
    stage_speed_increment = DIFFICULTY_SPEED_MAP[current_difficulty]
    circle_speed = base_circle_speed
    circles = []
    score = 0
    stage_threshold = 1000
    stage = 1
    font = pygame.font.SysFont(None, 36)
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Falling Circles - Dodge the Obstacles")
    clock = pygame.time.Clock()
    try:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)
    except Exception as e:
        print("Error playing background music:", e)
    player_x = (WIDTH - SCOREBOARD_WIDTH) // 2 - player_width // 2
    player_y = HEIGHT - player_height - 10
    spawn_timer = 0
    running = True
    while running:
        clock.tick(FPS)
        spawn_timer += 1
        if spawn_timer >= 30:
            circles.append(spawn_circle(WIDTH, SCOREBOARD_WIDTH, circle_radius))
            spawn_timer = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                player_y = HEIGHT - player_height - 10
            if event.type == pygame.KEYDOWN:  # Added this block
                if event.key == pygame.K_q:
                    running = False  # Exit the game loop
                    main()  # Return to the main menu
                    return
        gameplay_width = WIDTH - SCOREBOARD_WIDTH
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < gameplay_width - player_width:
            player_x += player_speed
        for circle in circles:
            circle['y'] += circle_speed
        circles = [circle for circle in circles if circle['y'] - circle['radius'] < HEIGHT]
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        for circle in circles:
            if circle_rectangle_collision(circle, player_rect):
                game_over(screen, font, clock, score, WIDTH, HEIGHT, SCOREBOARD_WIDTH)
                return
        score += 1
        new_stage = score // stage_threshold + 1
        if new_stage != stage:
            stage = new_stage
            circle_speed = base_circle_speed + (stage - 1) * stage_speed_increment
        screen.fill(BLACK)
        pygame.draw.rect(screen, BLACK, (0, 0, gameplay_width, HEIGHT))
        pygame.draw.rect(screen, BLUE, player_rect)
        for circle in circles:
            pygame.draw.circle(screen, RED, (int(circle['x']), int(circle['y'])), circle['radius'])
        draw_text(f"Score: {score}", font, WHITE, screen, 10, 10)
        draw_text(f"Stage: {stage}", font, WHITE, screen, 10, 40)
        pygame.draw.line(screen, WHITE, (gameplay_width, 0), (gameplay_width, HEIGHT), 2)
        highscores = load_highscores()
        x_offset = gameplay_width + 10
        y_offset = 10
        draw_text("High Scores:", font, WHITE, screen, x_offset, y_offset)
        y_offset += 30
        for i, (n, s) in enumerate(highscores):
            draw_text(f"{i+1}. {n} - {s}", font, WHITE, screen, x_offset, y_offset)
            y_offset += 20
        pygame.display.update()

# --- MENU ---
def set_difficulty(selected, value):
    global current_difficulty
    current_difficulty = value

def main():
    global current_difficulty
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Falling Circles - Menu")
    menu = pygame_menu.Menu('Falling Circles', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
    menu.add.selector('Difficulty :', [('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')],
                     default=1, onchange=lambda v, d: set_difficulty(v, d))
    menu.add.button('Start', main_game)
    menu.add.button('Exit', pygame_menu.events.EXIT)
    menu.mainloop(screen)

if __name__ == "__main__":
    main()