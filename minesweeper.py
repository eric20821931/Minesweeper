import pygame
import numpy as np
import csv
import os
import sys

# --- Constants ---
FONT_SIZE = 24
PLAYER_COLOR = (255, 230, 0)
HIDDEN_COLOR = (120, 120, 120)
REVEALED_COLOR = (200, 200, 200)
MINE_COLOR = (255, 80, 80)
TEXT_COLOR = (0, 0, 0)
BG_COLOR = (30, 30, 30)
WIN_COLOR = (0, 200, 0)
LOSE_COLOR = (200, 50, 50)

# CSV setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "minesweeper_records.csv")
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Player", "Total", "Win", "Lose"])

def load_player(name):
    players = {}
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            players[row["Player"]] = {"Total": int(row["Total"]),
                                      "Win": int(row["Win"]),
                                      "Lose": int(row["Lose"])}
    if name not in players:
        players[name] = {"Total": 0, "Win": 0, "Lose": 0}
    return players

def save_player(players):
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Player", "Total", "Win", "Lose"])
        for name, data in players.items():
            writer.writerow([name, data["Total"], data["Win"], data["Lose"]])

# --- Board generation ---
def generate_board(rows, cols, mines):
    board = np.zeros((rows, cols), dtype=int)
    mine_positions = np.random.choice(rows * cols, mines, replace=False)
    for pos in mine_positions:
        r, c = divmod(pos, cols)
        board[r, c] = -1
    for r in range(rows):
        for c in range(cols):
            if board[r, c] == -1:
                continue
            count = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and board[nr, nc] == -1:
                        count += 1
            board[r, c] = count
    return board

def reveal_cell(board, revealed, r, c):
    if revealed[r, c]:
        return 0
    revealed[r, c] = True
    count = 1
    if board[r, c] == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < board.shape[0] and 0 <= nc < board.shape[1]:
                    if not revealed[nr, nc]:
                        count += reveal_cell(board, revealed, nr, nc)
    return count

# --- Draw functions ---
def draw_text(screen, text, size, color, pos, center=False):
    font = pygame.font.SysFont("Arial", size)
    render = font.render(text, True, color)
    rect = render.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    screen.blit(render, rect)

def draw_board(screen, font, board, revealed, player_pos, cell_size, margin):
    rows, cols = board.shape
    for r in range(rows):
        for c in range(cols):
            x = c * (cell_size + margin)
            y = r * (cell_size + margin)
            rect = pygame.Rect(x, y, cell_size, cell_size)
            color = REVEALED_COLOR if revealed[r, c] else HIDDEN_COLOR
            if board[r, c] == -1 and revealed[r, c]:
                color = MINE_COLOR
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)
            if revealed[r, c] and board[r, c] > 0:
                text = font.render(str(board[r, c]), True, TEXT_COLOR)
                screen.blit(text, text.get_rect(center=rect.center))
    # draw player
    pr, pc = player_pos
    px = pc * (cell_size + margin)
    py = pr * (cell_size + margin)
    pygame.draw.rect(screen, PLAYER_COLOR, (px, py, cell_size, cell_size), 3)

def select_starting_position(screen, board, revealed, cell_size, margin):
    rows, cols = board.shape
    font = pygame.font.SysFont("Arial", max(12, cell_size // 2))
    while True:
        screen.fill(BG_COLOR)
        for r in range(rows):
            for c in range(cols):
                x = c * (cell_size + margin)
                y = r * (cell_size + margin)
                rect = pygame.Rect(x, y, cell_size, cell_size)
                pygame.draw.rect(screen, HIDDEN_COLOR, rect)
                pygame.draw.rect(screen, (0, 0, 0), rect, 1)
        draw_text(screen, "Click a cell to start", 24, (255, 255, 255),
                  (screen.get_width() // 2, screen.get_height() - 40), center=True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                c = mx // (cell_size + margin)
                r = my // (cell_size + margin)

                if 0 <= r < rows and 0 <= c < cols:
                    if board[r, c] == -1:
                        revealed[:, :] = True
                        screen.fill(BG_COLOR)
                        draw_board(screen, font, board, revealed, [r, c], cell_size, margin)
                        draw_text(screen, "GAME OVER", 36, (255, 80, 80),
                                  (screen.get_width() // 2, screen.get_height() - 40), center=True)
                        pygame.display.flip()
                        pygame.time.wait(2000)
                        return None 
                    else:
                        reveal_cell(board, revealed, r, c)
                        return [r, c]

# --- Dynamic cell size ---
def calculate_cell_size(rows, cols, screen_width, screen_height):
    max_width = screen_width - 40
    max_height = screen_height - 80
    cell_width = max_width // cols
    cell_height = max_height // rows
    return max(10, min(cell_width, cell_height))

# --- Game ---
def play_game(screen, name, players, rows, cols, mines):
    board = generate_board(rows, cols, mines)
    revealed = np.zeros((rows, cols), dtype=bool)
    
    cell_size = calculate_cell_size(rows, cols, screen.get_width(), screen.get_height())
    margin = max(1, cell_size // 15)
    font = pygame.font.SysFont("Arial", max(12, cell_size // 2))
    
    player_pos = select_starting_position(screen, board, revealed, cell_size, margin)
    if player_pos is None:
        players[name]["Total"] += 1
        players[name]["Lose"] += 1
        save_player(players)
        return

    running = True
    game_over = False
    win = False
    clock = pygame.time.Clock()

    while running:
        screen.fill(BG_COLOR)
        draw_board(screen, font, board, revealed, player_pos, cell_size, margin)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_player(players)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and not game_over:
                r, c = player_pos
                if event.key == pygame.K_UP and r > 0:
                    player_pos[0] -= 1
                elif event.key == pygame.K_DOWN and r < rows - 1:
                    player_pos[0] += 1
                elif event.key == pygame.K_LEFT and c > 0:
                    player_pos[1] -= 1
                elif event.key == pygame.K_RIGHT and c < cols - 1:
                    player_pos[1] += 1
                r, c = player_pos
                if not revealed[r, c]:
                    if board[r, c] == -1:
                        revealed[:, :] = True
                        game_over = True
                        win = False
                    else:
                        reveal_cell(board, revealed, r, c)

        if not game_over and np.sum(revealed & (board != -1)) == rows * cols - mines:
            revealed[:, :] = True
            game_over = True
            win = True

        if game_over:
            msg = "YOU WIN" if win else "GAME OVER"
            color = WIN_COLOR if win else LOSE_COLOR
            draw_text(screen, msg, 36, color, (screen.get_width() // 2, screen.get_height() - 40), center=True)
            pygame.display.flip()
            pygame.time.wait(2500)

            players[name]["Total"] += 1
            if win:
                players[name]["Win"] += 1
            else:
                players[name]["Lose"] += 1
            save_player(players)
            running = False

# --- Menu and setup ---
def main_menu(screen, players, name):
    font = pygame.font.SysFont("Arial", 30)
    while True:
        screen.fill(BG_COLOR)
        draw_text(screen, "Minesweeper", 50, (255, 255, 255), (screen.get_width() // 2, 80), center=True)
        options = ["Play", "Rules", "Record", "Exit"]
        buttons = []
        for i, opt in enumerate(options):
            rect = pygame.Rect(screen.get_width() // 2 - 100, 180 + i * 70, 200, 50)
            pygame.draw.rect(screen, (180, 180, 180), rect, border_radius=10)
            draw_text(screen, opt, 28, (0, 0, 0), rect.center, center=True)
            buttons.append((opt, rect))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_player(players)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for opt, rect in buttons:
                    if rect.collidepoint(mx, my):
                        if opt == "Play":
                            setup_game(screen, players, name)
                        elif opt == "Rules":
                            show_rules(screen)
                        elif opt == "Record":
                            show_record(screen, players, name)
                        elif opt == "Exit":
                            save_player(players)
                            pygame.quit()
                            sys.exit()

def setup_game(screen, players, name):
    font = pygame.font.SysFont("Arial", 28)
    input_boxes = ["Rows", "Cols", "Mines"]
    values = ["", "", ""]
    active_index = 0

    while True:
        screen.fill(BG_COLOR)
        draw_text(screen, "Game Setup", 40, (255, 255, 255), (screen.get_width() // 2, 80), center=True)
        
        boxes = []
        for i, label in enumerate(input_boxes):
            rect = pygame.Rect(screen.get_width() // 2 - 100, 150 + i * 70, 200, 50)
            color = (255, 255, 255) if i == active_index else (180, 180, 180)
            pygame.draw.rect(screen, color, rect, border_radius=8)
            draw_text(screen, f"{label}: {values[i]}", 24, (0, 0, 0), rect.center, center=True)
            boxes.append(rect)

        start_rect = pygame.Rect(screen.get_width() // 2 - 100, 400, 200, 50)
        pygame.draw.rect(screen, (0, 200, 0), start_rect, border_radius=8)
        draw_text(screen, "Start", 28, (0, 0, 0), start_rect.center, center=True)
        draw_text(screen, "Press ESC to return", 22, (200, 200, 200), (screen.get_width() // 2, 470), center=True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active_index = (active_index + 1) % 3  
                elif event.key == pygame.K_BACKSPACE:
                    values[active_index] = values[active_index][:-1]
                elif event.key == pygame.K_ESCAPE:
                    return 
                elif event.unicode.isdigit():
                    values[active_index] += event.unicode

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                for i, rect in enumerate(boxes):
                    if rect.collidepoint(mx, my):
                        active_index = i

                if start_rect.collidepoint(mx, my):
                    try:
                        rows, cols, mines = map(int, values)
                        if 1 <= mines < rows * cols:
                            play_game(screen, name, players, rows, cols, mines)
                            return
                    except:
                        pass

# --- Rules & Record ---
def show_rules(screen):
    font = pygame.font.SysFont("Arial", 26)
    running = True
    while running:
        screen.fill(BG_COLOR)
        draw_text(screen, "Rules", 40, (255, 255, 255), (screen.get_width() // 2, 60), center=True)
        lines = [
            "• Move with arrow keys.",
            "• Walk onto a cell to reveal it.",
            "• Mines make you lose instantly.",
            "• Reveal all safe cells to win!",
            "• Records are saved automatically."
        ]
        for i, line in enumerate(lines):
            draw_text(screen, line, 24, (230, 230, 230), (80, 150 + i * 50))
        draw_text(screen, "Press ESC to return", 22, (200, 200, 200), (80, 450))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

def show_record(screen, players, name):
    font = pygame.font.SysFont("Arial", 28)
    running = True
    while running:
        data = players[name]
        screen.fill(BG_COLOR)
        draw_text(screen, f"{name}'s Record", 40, (255, 255, 255), (screen.get_width() // 2, 80), center=True)
        draw_text(screen, f"Total: {data['Total']}", 28, (255, 255, 255), (100, 200))
        draw_text(screen, f"Win: {data['Win']}", 28, WIN_COLOR, (100, 260))
        draw_text(screen, f"Lose: {data['Lose']}", 28, LOSE_COLOR, (100, 320))
        draw_text(screen, "Press ESC to return", 22, (200, 200, 200), (100, 400))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

# --- Main ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
    pygame.display.set_caption("Minesweeper")
    font = pygame.font.SysFont("Arial", 30)

    name = ""
    input_active = True
    while input_active:
        screen.fill(BG_COLOR)
        draw_text(screen, "Enter your name:", 30, (255, 255, 255), (screen.get_width() // 2, 150), center=True)
        draw_text(screen, name, 30, (255, 255, 0), (screen.get_width() // 2, 220), center=True)
        draw_text(screen, "Press Enter to continue", 22, (180, 180, 180), (screen.get_width() // 2, 300), center=True)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(name) > 0:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isprintable():
                    name += event.unicode

    players = load_player(name)
    main_menu(screen, players, name)

if __name__ == "__main__":
    main()
