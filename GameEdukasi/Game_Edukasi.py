import pygame
import random
import sys
import os

# Inisialisasi pygame dan mixer
pygame.init()
try:
    pygame.mixer.init()
except Exception as e:
    print("Error initializing mixer:", e)

# Muat background music dan mainkan secara loop
try:
    pygame.mixer.music.load("BGM.mp3")  # Ubah ke "background.ogg" jika perlu
    pygame.mixer.music.play(-1)  # Loop tanpa henti
except Exception as e:
    print("Error loading background music:", e)
6
# Muat game over sound
try:
    game_over_sound = pygame.mixer.Sound("game_over.wav")  # Ubah ke "game_over.ogg" jika perlu
except Exception as e:
    print("Error loading game over sound:", e)

# Set ukuran window awal, tetapi window dapat di-resize
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Falling Circles - Dodge the Obstacles")

# Konstanta untuk lebar area highscore (scoreboard)
SCOREBOARD_WIDTH = 220  # Lebar area highscore (tetap)

# Warna-warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)

# Frame rate
FPS = 60
clock = pygame.time.Clock()

# Properti pemain
player_width, player_height = 50, 50
player_x = (WIDTH - SCOREBOARD_WIDTH) // 2 - player_width // 2  # di dalam area gameplay
player_y = HEIGHT - player_height - 10
player_speed = 5

# Properti lingkaran (rintangan)
circle_radius = 20
base_circle_speed = 4           # Kecepatan dasar lingkaran
stage_speed_increment = 1       # Penambahan kecepatan per stage
circle_speed = base_circle_speed  # Kecepatan awal
circles = []  # List untuk menyimpan lingkaran

# Skor dan Stage
score = 0
stage_threshold = 1000  # Skor untuk naik stage
stage = 1

font = pygame.font.SysFont(None, 36)

def draw_text(text, font, color, surface, x, y):
    """Menggambar teks pada layar."""
    text_obj = font.render(text, True, color)
    surface.blit(text_obj, (x, y))

def spawn_circle():
    """
    Menghasilkan lingkaran rintangan baru dengan posisi acak.
    Lingkaran hanya muncul dalam area gameplay, yaitu dari 0 sampai (WIDTH - SCOREBOARD_WIDTH)
    """
    gameplay_width = WIDTH - SCOREBOARD_WIDTH
    x_pos = random.randint(circle_radius, gameplay_width - circle_radius)
    y_pos = -circle_radius  # Mulai dari atas layar
    return {'x': x_pos, 'y': y_pos, 'radius': circle_radius}

def circle_rectangle_collision(circle, rect):
    """
    Deteksi tabrakan antara lingkaran dan persegi pemain.
    Caranya: cari titik terdekat pada persegi terhadap pusat lingkaran,
    lalu periksa apakah jarak titik tersebut ke pusat lingkaran kurang dari radius.
    """
    circle_x = circle['x']
    circle_y = circle['y']
    radius = circle['radius']
    
    closest_x = max(rect.left, min(circle_x, rect.right))
    closest_y = max(rect.top, min(circle_y, rect.bottom))
    
    distance_x = circle_x - closest_x
    distance_y = circle_y - closest_y
    
    return (distance_x**2 + distance_y**2) < (radius**2)

# --- Sistem Highscore ---

def load_highscores():
    """Memuat highscore dari file."""
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
    """Menyimpan highscore ke file."""
    try:
        with open("highscores.txt", "w") as f:
            for name, s in highscores:
                f.write(f"{name},{s}\n")
    except Exception as e:
        print("Error saving highscores:", e)

def update_highscores(name, score):
    """
    Memperbarui highscore dengan skor baru.
    Jika terdapat entry dengan nama yang sama, maka hanya akan di-overwrite
    jika skor baru lebih tinggi.
    """
    highscores = load_highscores()
    updated = False
    for i, (n, s) in enumerate(highscores):
        if n == name:
            if score > s:  # Hanya update jika skor baru lebih tinggi
                highscores[i] = (name, score)
            updated = True
            break
    if not updated:
        highscores.append((name, score))
    highscores.sort(key=lambda x: x[1], reverse=True)
    highscores = highscores[:10]  # Simpan 10 skor teratas
    save_highscores(highscores)
    return highscores

def get_player_name(current_score):
    """
    Meminta input nama pemain setelah game over.
    Pemain dapat mengetik dan menekan Enter untuk menyelesaikan input.
    """
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
                    name += event.unicode
        screen.fill(BLACK)
        draw_text("GAME OVER", font, RED, screen, 40, HEIGHT // 2 - 80)
        draw_text(f"Your Score: {current_score}", font, WHITE, screen, 40, HEIGHT // 2 - 40)
        draw_text("Enter your name: " + name, font, WHITE, screen, 40, HEIGHT // 2)
        pygame.display.update()
        clock.tick(FPS)
    return name

# --- Fungsi Game Over ---
def game_over():
    global score
    # Hentikan background music agar sound game over terdengar jelas
    pygame.mixer.music.stop()
    try:
        game_over_sound.play()
    except Exception as e:
        print("Error playing game over sound:", e)
    
    # Minta pemain memasukkan nama dan perbarui highscore
    player_name = get_player_name(score)
    highscores = update_highscores(player_name, score)
    
    waiting = True
    while waiting:
        screen.fill(BLACK)
        # Tampilan informasi game over di area gameplay (kiri)
        draw_text("GAME OVER", font, RED, screen, 20, 20)
        draw_text(f"Your Score: {score}", font, WHITE, screen, 20, 60)
        draw_text("Press R to Restart or Q to Quit", font, WHITE, screen, 20, HEIGHT - 50)
        
        # Tampilan area highscore di sisi kanan
        x_offset = WIDTH - SCOREBOARD_WIDTH + 10
        y_offset = 20
        draw_text("High Scores:", font, WHITE, screen, x_offset, y_offset)
        y_offset += 30
        for i, (n, s) in enumerate(highscores):
            draw_text(f"{i+1}. {n} - {s}", font, WHITE, screen, x_offset, y_offset)
            y_offset += 20

        # Gambar garis pemisah antara area gameplay dan area highscore
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
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        clock.tick(FPS)

# --- Fungsi Utama Game ---
def main_game():
    global score, circles, player_x, player_y, WIDTH, HEIGHT, circle_speed, stage, screen
    global stage_threshold, stage_speed_increment, player_width, player_height

    # Reset variabel game
    score = 0
    circles = []
    # Pastikan pemain muncul di area gameplay (0 sampai WIDTH - SCOREBOARD_WIDTH)
    player_x = (WIDTH - SCOREBOARD_WIDTH) // 2 - player_width // 2
    player_y = HEIGHT - player_height - 10
    stage = 1
    circle_speed = base_circle_speed
    spawn_timer = 0

    # Mulai kembali background music jika sebelumnya dihentikan
    if not pygame.mixer.music.get_busy():
        try:
            pygame.mixer.music.play(-1)
        except Exception as e:
            print("Error restarting background music:", e)

    running = True
    while running:
        clock.tick(FPS)
        spawn_timer += 1
        if spawn_timer >= 30:  # Spawn lingkaran kira-kira setiap 0.5 detik
            circles.append(spawn_circle())
            spawn_timer = 0

        # Tangani event, termasuk resize window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                # Update posisi pemain agar tetap berada di area gameplay
                player_y = HEIGHT - player_height - 10

        # Definisikan area gameplay (tanpa area highscore)
        gameplay_width = WIDTH - SCOREBOARD_WIDTH

        # Tangani input keyboard (pastikan pemain tidak keluar dari area gameplay)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < gameplay_width - player_width:
            player_x += player_speed

        # Update posisi lingkaran (muncul hanya di area gameplay)
        for circle in circles:
            circle['y'] += circle_speed

        # Hapus lingkaran yang sudah keluar layar
        circles = [circle for circle in circles if circle['y'] - circle['radius'] < HEIGHT]

        # Buat objek persegi untuk pemain (hanya di area gameplay)
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

        # Cek tabrakan antara pemain dan lingkaran
        for circle in circles:
            if circle_rectangle_collision(circle, player_rect):
                game_over()
                return

        # Update skor dan stage
        score += 1
        new_stage = score // stage_threshold + 1
        if new_stage != stage:
            stage = new_stage
            circle_speed = base_circle_speed + (stage - 1) * stage_speed_increment

        # Gambar area permainan
        screen.fill(BLACK)
        # Gambar area gameplay (seluruh area kecuali bagian highscore)
        pygame.draw.rect(screen, BLACK, (0, 0, gameplay_width, HEIGHT))
        # Gambar pemain dan lingkaran pada area gameplay
        pygame.draw.rect(screen, BLUE, player_rect)
        for circle in circles:
            pygame.draw.circle(screen, RED, (int(circle['x']), int(circle['y'])), circle['radius'])
        draw_text(f"Score: {score}", font, WHITE, screen, 10, 10)
        draw_text(f"Stage: {stage}", font, WHITE, screen, 10, 40)
        
        # Gambar garis pemisah antara area gameplay dan area highscore
        pygame.draw.line(screen, WHITE, (gameplay_width, 0), (gameplay_width, HEIGHT), 2)
        
        # Tampilkan Highscores di area highscore (sisi kanan)
        highscores = load_highscores()
        x_offset = gameplay_width + 10
        y_offset = 10
        draw_text("High Scores:", font, WHITE, screen, x_offset, y_offset)
        y_offset += 30
        for i, (n, s) in enumerate(highscores):
            draw_text(f"{i+1}. {n} - {s}", font, WHITE, screen, x_offset, y_offset)
            y_offset += 20

        pygame.display.update()

if __name__ == "__main__":
    main_game()
