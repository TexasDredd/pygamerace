import pygame
import sys
import time
import math

# Inicializar Pygame
pygame.init()
gamestarted = False

# Configuración de pantalla (más grande)
width, height = 1000, 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Auto Fight!")
clock = pygame.time.Clock()

# Setting Background Music
pygame.mixer.music.load('theme.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

# Adding Sounds
sound1 = pygame.mixer.Sound('p1.wav')
sound1.set_volume(0.2)
sound2 = pygame.mixer.Sound('p2.wav')
sound2.set_volume(0.2)
ending = pygame.mixer.Sound('ending.wav')
ending.set_volume(0.4)

# Colores
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (232, 228, 83)

# Cargar la imagen de fondo
background_img = pygame.image.load('sfbg.jpg')  # Asegúrate de que este archivo exista
background_img = pygame.transform.scale(background_img, (width, height))  # Ajustar al tamaño de la ventana

# Tamaño del texto
font = pygame.font.SysFont('rockwellnegrita', 20)

# Estados y transiciones de los DFA y PDA
dfa_player1 = {
    'A': {'W': 'B', 'D': 'C'},
    'B': {'S': 'D', 'A': 'E'},
    'C': {'A': 'D', 'S': 'F'},
    'D': {'W': 'G'},
    'E': {'D': 'F'},
    'F': {'A': 'final'},
    'G': {'S': 'final'},
    'final': None
}

# PDA para el Jugador 2 (Convertido en DPDA)
pda_player2 = {
    '1': {'UP': ('2', 'PUSH', 'X')},
    '2': {'DOWN': ('3', 'PUSH', 'Y'), 'RIGHT': ('4', 'POP', 'X')},
    '3': {'DOWN': ('4', 'POP', 'Y')},
    '4': {'RIGHT': ('5', 'POP', 'Y') ,'DOWN': ('final', 'POP', 'Y')},
    '5': {'LEFT': ('6', 'POP', 'X')},
    '6': {'DOWN': ('7', 'PUSH', 'Z')},
    '7': {'LEFT': ('8', 'POP', 'Z')},
    '8': {'LEFT': ('final', 'POP', 'Z')},
    'final': {'UP': ('7', 'PUSH', 'Z')}
    
}

# Estado inicial
state_player1 = 'A'
state_player2 = '1'

# Pila del jugador 2
stack_player2 = []

# Secuencias más complicadas
sequence_player1 = ['W', 'S', 'D', 'A', 'W', 'S', 'A', 'D', 'W', 'D', 'S', 'A', 'W']
sequence_player2 = ['UP', 'DOWN', 'UP', 'RIGHT', 'LEFT', 'DOWN']

current_input1 = 0
current_input2 = 0

# Posiciones de los estados en el diagrama
state_positions_p1 = {
    'A': (200-150, 200),
    'B': (350-150, 100),
    'C': (350-150, 250),
    'D': (500-150, 100),
    'E': (500-150, 300),
    'F': (650-150, 200),
    'G': (800-150, 100),
    'final': (950-150, 200)
}

state_positions_p2 = {
    '1': (200-150, 500),
    '2': (350-150, 400),
    '3': (350-150, 600),
    '4': (500-150, 400),
    '5': (500-150, 600),
    '6': (650-150, 600),
    '7': (800-150, 500),
    '8': (950-150, 600),
    'final': (950-150, 400)
}

# Función para renderizar texto
def render_text(text, x, y, color=black):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))

# Función para dibujar diagramas de estados
def draw_dfa(states, transitions, current_state, positions, color, border_color=None):
    # Si no se especifica un color de borde, usar el color de las transiciones
    if border_color is None:
        border_color = color

    
    # Dibujar transiciones y flechas
    for state, pos in positions.items():
        if isinstance(transitions.get(state), dict):
            for symbol, target in transitions[state].items():
                start_pos = positions[state]
                end_pos = positions[target] if isinstance(target, str) else positions[target[0]]

                # Dibujar línea de transición
                pygame.draw.line(screen, color, start_pos, end_pos, 2)

                # Calcular dirección de la flecha
                dx = end_pos[0] - start_pos[0]
                dy = end_pos[1] - start_pos[1]
                angle = math.atan2(dy, dx)

                # Posición de la flecha (cercana al estado destino)
                arrow_x = end_pos[0] - 40 * math.cos(angle)  # Ajustar posición para no solaparse
                arrow_y = end_pos[1] - 40 * math.sin(angle)

                # Coordenadas del triángulo de la flecha (más grande)
                arrow_points = [
                    (arrow_x, arrow_y),
                    (arrow_x - 15 * math.cos(angle - math.pi / 6), arrow_y - 15 * math.sin(angle - math.pi / 6)),
                    (arrow_x - 15 * math.cos(angle + math.pi / 6), arrow_y - 15 * math.sin(angle + math.pi / 6))
                ]

                # Dibujar la flecha
                pygame.draw.polygon(screen, color, arrow_points)

                # Mostrar el símbolo de transición
               # Mostrar el símbolo de transición exactamente en la mitad de la flecha
                mid_x = (start_pos[0] + end_pos[0]) // 2
                mid_y = (start_pos[1] + end_pos[1]) // 2
                render_text(symbol, mid_x, mid_y - 15, color)


# Dibujar los estados
    for state, pos in positions.items():
        pygame.draw.circle(screen, yellow, pos, 40, 0)  # Círculo del estado (relleno)
        pygame.draw.circle(screen, border_color, pos, 40, 2)  # Borde del estado
        render_text(state, pos[0] - 10, pos[1] - 10)

        if state == 'final':  # Estado final
            pygame.draw.circle(screen, border_color, pos, 35, 2)

        if state == current_state:
            pygame.draw.circle(screen, color, pos, 45, 3)  # Resaltar estado actual


# Función para dibujar la uypila
def draw_stack(stack, x, y):
    for i, symbol in enumerate(reversed(stack)):
        pygame.draw.rect(screen, black, (x, y - i * 30, 40, 30))
        render_text(symbol, x + 10, y - i * 30 + 5, white)

def display_winner_screen(winner):
    while winner == 1 or winner == 2:
        screen.fill(white)
        render_text(f"¡Felicitaciones, Jugador {winner}!", width // 2 - 150, height // 2 - 50, red)
        render_text("Presiona 'R' para jugar de nuevo o 'Q' para salir.", width // 2 - 250, height // 2 + 50, black)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "restart"
                elif event.key == pygame.K_q:
                    return "quit"


# Bucle principal del juego
error_message_p1 = ""
error_message_timer_p1 = 0
error_message_p2 = ""
error_message_timer_p2 = 0

running = True
winner = 0
while running:
    screen.blit(background_img, (0, 0))

    draw_dfa(dfa_player1, dfa_player1, state_player1, state_positions_p1, red, border_color=black)
    draw_dfa(pda_player2, pda_player2, state_player2, state_positions_p2, green,  border_color=black)


    draw_stack(stack_player2, 900, 600)

    render_text(f"P1 (WASD)    - --->: {state_player1}", 850, 100, red)
    render_text(f"P2 (Flechas) -  --->: {state_player2}", 850, 550, green)

    if error_message_p1:
        render_text(error_message_p1, width // 2 - 200, height - 670, red)
    if error_message_p2:
        render_text(error_message_p2, width // 2 - 200, height - 50, green)

    if winner:
        result = display_winner_screen(winner)
        if result == "restart":
            state_player1 = 'A'
            state_player2 = '1'
            stack_player2 = ['Z']
            current_input1 = 0
            current_input2 = 0
            winner = None
            gamestarted = False
        elif result == "quit":
            running = False
            break
       
    if gamestarted == False:
        stack_player2.append('Z')
        gamestarted = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            key = pygame.key.name(event.key).upper()
            wasd_keys = {'W', 'A', 'S', 'D'}

            if key in wasd_keys:
                sound1.play()
                if state_player1 in dfa_player1 and key in dfa_player1[state_player1]:
                    state_player1 = dfa_player1[state_player1][key]
                    current_input1 += 1
                    if state_player1 == 'final':
                        winner = 1
                else:
                    state_player1 = 'A'
                    current_input1 = 0
                    error_message_p1 = "P1: Intenta de nuevo"
                    error_message_timer_p1 = 40

            arrow_keys = {pygame.K_UP: 'UP', pygame.K_DOWN: 'DOWN', pygame.K_LEFT: 'LEFT', pygame.K_RIGHT: 'RIGHT'}
            if event.key in arrow_keys:
                key = arrow_keys[event.key]
                sound2.play()

                if state_player2 in pda_player2 and key in pda_player2[state_player2]:
                    next_state, stack_op, stack_symbol = pda_player2[state_player2][key]
                    if stack_op == 'PUSH':
                        stack_player2.append(stack_symbol)
                    elif stack_op == 'POP' and stack_player2 and stack_player2[-1] == stack_symbol:
                        stack_player2.pop()
                    state_player2 = next_state
                    if state_player2 == 'final' and not stack_player2:
                        winner = 2
                else:
                    state_player2 = '1'
                    stack_player2 = []
                    stack_player2.append('Z')
                    current_input2 = 0
                    error_message_p2 = "P2: Intenta de nuevo"
                    error_message_timer_p2 = 40

        if error_message_timer_p1 > 0:
            error_message_timer_p1 -= 15
        else:
            error_message_p1 = ""

        if error_message_timer_p2 > 0:
            error_message_timer_p2 -= 15
        else:
            error_message_p2 = ""

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
