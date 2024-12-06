import pygame
import json
import math

# Inicialización de Pygame
pygame.init()

# Dimensiones de la ventana
WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Editor de Niveles - Project Arrhythmia")

# Colores
BG_COLOR = (0, 0, 0)
GRID_COLOR = (100, 100, 100)
SELECTED_COLOR = (255, 0, 0)
BUTTON_COLOR = (50, 50, 50)
BUTTON_HOVER_COLOR = (80, 80, 80)
TEXT_COLOR = (255, 255, 255)

# Fuente para texto
font = pygame.font.SysFont(None, 24)

# Variables del editor
obstacles = []  # Lista para almacenar los obstáculos
scroll_speed = 10  # Velocidad del desplazamiento
camera_x, camera_y = 0, 0  # Posición de la cámara
selected_obstacle = None  # Obstáculo seleccionado para mover o modificar
music_playing = False  # Estado de la música
music_pos = 0  # Posición de la música en el tiempo
obstacle_types = ["circle", "square", "triangle"]  # Tipos de obstáculos
current_obstacle_type = "circle"  # Tipo de obstáculo seleccionado
volume = 1.0  # Volumen de la música (1.0 es máximo)

# Cargar música
pygame.mixer.music.load("resources/[PA] Geoxor - Virtual Arcadia 2020.ogg")

# Función para dibujar botones
def draw_button(x, y, width, height, text, color, hover_color, action=None):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    button_rect = pygame.Rect(x, y, width, height)

    if button_rect.collidepoint(mouse_x, mouse_y):
        pygame.draw.rect(screen, hover_color, button_rect)
        if pygame.mouse.get_pressed()[0] and action:
            action()
    else:
        pygame.draw.rect(screen, color, button_rect)

    text_surface = font.render(text, True, TEXT_COLOR)
    screen.blit(text_surface, (x + (width - text_surface.get_width()) // 2, y + (height - text_surface.get_height()) // 2))

# Función para cambiar la música (play/pause)
def toggle_music():
    global music_playing
    if music_playing:
        pygame.mixer.music.pause()
        music_playing = False
    else:
        pygame.mixer.music.unpause()
        music_playing = True

# Función para cambiar el volumen
def change_volume(increase=True):
    global volume
    if increase:
        volume = min(volume + 0.1, 1.0)
    else:
        volume = max(volume - 0.1, 0.0)
    pygame.mixer.music.set_volume(volume)

# Función para cambiar el tipo de obstáculo
def change_obstacle_type():
    global current_obstacle_type
    current_type_index = obstacle_types.index(current_obstacle_type)
    new_type_index = (current_type_index + 1) % len(obstacle_types)
    current_obstacle_type = obstacle_types[new_type_index]

# Dibujar la cuadrícula
def draw_grid(offset_x, offset_y):
    for x in range(-offset_x % 40, WINDOW_WIDTH, 40):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(-offset_y % 40, WINDOW_HEIGHT, 40):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))

# Guardar niveles en un archivo JSON
def save_levels(obstacles, filename="levels.json"):
    level_data = {"obstacles": []}
    for obstacle in obstacles:
        level_data["obstacles"].append({
            "x": obstacle["x"],
            "y": obstacle["y"],
            "type": obstacle["type"],
            "size": obstacle["size"],
            "time": obstacle["time"]
        })
    with open(filename, "w") as file:
        json.dump(level_data, file, indent=4)
    print("Niveles guardados en", filename)

# Cargar obstáculos desde el código
def load_obstacles():
    obstacles.append({"x": 200, "y": 150, "type": "circle", "size": 50, "time": 1000})
    obstacles.append({"x": 400, "y": 300, "type": "square", "size": 40, "time": 2000})

# Dibujar un obstáculo
def draw_obstacle(obstacle, camera_x, camera_y, selected=False):
    screen_x = obstacle["x"] - camera_x
    screen_y = obstacle["y"] - camera_y
    size = obstacle["size"]

    # Seleccionar el obstáculo
    if selected:
        pygame.draw.rect(screen, SELECTED_COLOR, (screen_x - 2, screen_y - 2, size + 4, size + 4), 2)

    # Dibujar el obstáculo según su tipo
    if obstacle["type"] == "circle":
        pygame.draw.circle(screen, (255, 0, 0), (screen_x + size // 2, screen_y + size // 2), size // 2)
    elif obstacle["type"] == "square":
        pygame.draw.rect(screen, (0, 255, 0), (screen_x, screen_y, size, size))
    elif obstacle["type"] == "triangle":
        pygame.draw.polygon(screen, (0, 0, 255), [(screen_x, screen_y), (screen_x + size, screen_y), (screen_x + size // 2, screen_y - size)])

# Función principal
def main():
    global camera_x, camera_y, selected_obstacle, music_pos, music_playing, current_obstacle_type
    load_obstacles()  # Cargar obstáculos de ejemplo
    pygame.mixer.music.play(-1, 0.0)  # Reproducir música en bucle

    running = True
    while running:
        screen.fill(BG_COLOR)
        draw_grid(camera_x, camera_y)

        # Control de la música
        music_pos = pygame.mixer.music.get_pos() / 1000  # Obtener el tiempo actual de la música en segundos
        if music_pos >= 0 and not music_playing:
            music_playing = True  # La música ha comenzado a reproducirse

        # Mostrar la posición de la música
        music_text = font.render(f"Tiempo: {math.floor(music_pos)}s", True, TEXT_COLOR)
        screen.blit(music_text, (10, 10))

        # Mostrar opciones en el panel lateral
        draw_button(WINDOW_WIDTH - 120, 50, 100, 40, "Play/Pause", BUTTON_COLOR, BUTTON_HOVER_COLOR, toggle_music)
        draw_button(WINDOW_WIDTH - 120, 100, 100, 40, "Vol +", BUTTON_COLOR, BUTTON_HOVER_COLOR, lambda: change_volume(True))
        draw_button(WINDOW_WIDTH - 120, 150, 100, 40, "Vol -", BUTTON_COLOR, BUTTON_HOVER_COLOR, lambda: change_volume(False))
        draw_button(WINDOW_WIDTH - 120, 200, 100, 40, "Change Obstacle", BUTTON_COLOR, BUTTON_HOVER_COLOR, change_obstacle_type)

        # Mostrar el tipo de obstáculo actual
        obstacle_type_text = font.render(f"Tipo: {current_obstacle_type}", True, TEXT_COLOR)
        screen.blit(obstacle_type_text, (WINDOW_WIDTH - 120, 250))

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:  # Guardar niveles con 'S'
                    save_levels(obstacles)
                elif event.key == pygame.K_LEFT:  # Mover la cámara con flechas
                    camera_x -= scroll_speed
                elif event.key == pygame.K_RIGHT:
                    camera_x += scroll_speed
                elif event.key == pygame.K_UP:
                    camera_y -= scroll_speed
                elif event.key == pygame.K_DOWN:
                    camera_y += scroll_speed

            # Detectar clic izquierdo del mouse para agregar un obstáculo o seleccionar uno
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                mouse_x += camera_x
                mouse_y += camera_y
                if event.button == 1:  # Botón izquierdo del mouse
                    obstacles.append({
                        "x": mouse_x,
                        "y": mouse_y,
                        "type": current_obstacle_type,
                        "size": 50,
                        "time": music_pos * 1000
                    })

        # Dibujar obstáculos
        for obstacle in obstacles:
            draw_obstacle(obstacle, camera_x, camera_y)

        pygame.display.flip()
        pygame.time.Clock().tick(60)

    pygame.quit()

# Iniciar el juego
if __name__ == "__main__":
    main()
