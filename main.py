import pygame
import requests
import time
import random

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("ESP32 Pong")
clock = pygame.time.Clock()

    # GAME VARIABLES
paddle_y = 250
ai_y = 250
ai_speed = 4.7

ball_x, ball_y = 400, 300
ball_dx, ball_dy = 5, 5

score_player, score_ai = 0, 0
WIN_SCORE = 5

# hit counters + timer
player_hits_count = 0
ai_hits_count = 0
game_start_time = 0

font = pygame.font.Font(None, 60)
small_font = pygame.font.Font(None, 40)

# Server URL
SERVER_PADDLE_URL = "http://172.20.10.2:5000/get"

running = True
game_over = False
game_started = False

#SEND SUMMARY TO SERVER
def send_game_summary():
    global game_start_time

    game_length = round(time.time() - game_start_time, 2)
    winner = "player" if score_player == WIN_SCORE else "computer"

    summary = {
        "player_score": score_player,
        "ai_score": score_ai,
        "player_hits": player_hits_count,
        "ai_hits": ai_hits_count,
        "game_length": game_length,
        "winner": winner
    }

    try:
        requests.post(
            "http://172.20.10.2:5000/gameover",
            json=summary,
            timeout=0.5
        )
        print("Game summary sent.")
    except:
        print("Failed to send summary")

# RESET GAME SERVER
def reset_game():
    global paddle_y, ai_y, ball_x, ball_y, ball_dx, ball_dy
    global score_player, score_ai, game_over, game_started
    global player_hits_count, ai_hits_count, game_start_time

    paddle_y = 250
    ai_y = 250
    ball_x, ball_y = 400, 300
    ball_dx, ball_dy = 5, 5
    score_player = 0
    score_ai = 0
    game_over = False
    game_started = False

    player_hits_count = 0
    ai_hits_count = 0

    game_start_time = time.time()

    # Clear the server JSON log
    try:
        requests.get("http://172.20.10.2:5000/reset", timeout=0.5)
    except:
        print("Failed to clear paddle log")


# BUTTON CLICK HELPER
def is_clicked(rect, mouse_pos):
    return rect.collidepoint(mouse_pos)


# MAIN LOOP
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # START button click
        if not game_started and event.type == pygame.MOUSEBUTTONDOWN:
            if start_button_rect.collidepoint(event.pos):
                game_started = True
                game_over = False
                game_start_time = time.time()
                player_hits_count = 0
                ai_hits_count = 0

        # RESTART button click after game over
        if game_over and event.type == pygame.MOUSEBUTTONDOWN:
            if start_button_rect.collidepoint(event.pos):
                reset_game()

    # START SCREEN
    if not game_started:
        screen.fill((0, 0, 0))

        title = font.render("ESP32 PONG", True, (255, 255, 255))
        screen.blit(title, (280, 150))

        start_button_rect = pygame.Rect(300, 300, 200, 80)
        pygame.draw.rect(screen, (255, 255, 255), start_button_rect, border_radius=10)

        start_text = small_font.render("START", True, (0, 0, 0))
        screen.blit(start_text, (360, 325))

        pygame.display.flip()
        clock.tick(60)
        continue

    # GAME ACTIVE
    if not game_over:

        # Read paddle value from ESP32 via server
        try:
            r = requests.get(SERVER_PADDLE_URL, timeout=0.05)
            paddle_value = r.json().get("paddle", 240)
        except:
            paddle_value = 240

        # Smooth movement
        target_y = int(paddle_value)
        if target_y > 500:
            target_y = 500
        paddle_y += (target_y - paddle_y) * 0.3

        # AI movement
        ai_error = random.randint(-40, 40)
        target_y = ball_y + ai_error

        if ai_y + 50 < target_y:
            ai_y += ai_speed
        elif ai_y + 50 > target_y:
            ai_y -= ai_speed

        # Ball movement
        ball_x += ball_dx
        ball_y += ball_dy

        if ball_y <= 0 or ball_y >= 580:
            ball_dy *= -1

        # Player paddle collision
        if (50 < ball_x < 70) and (paddle_y < ball_y < paddle_y + 100):
            ball_dx *= -1
            player_hits_count += 1

        # AI paddle collision
        if (730 < ball_x < 750) and (ai_y < ball_y < ai_y + 100):
            ball_dx *= -1
            ai_hits_count += 1

        # Scoring
        if ball_x < 0:
            score_ai += 1
            ball_x, ball_y = 400, 300
            ball_dx = 5

        if ball_x > 800:
            score_player += 1
            ball_x, ball_y = 400, 300
            ball_dx = -5

        # Game Over
        if score_player >= WIN_SCORE or score_ai >= WIN_SCORE:
            game_over = True
            send_game_summary()

    #DRAW GAME SCREEN
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (255, 255, 255), (50, paddle_y, 20, 100))
    pygame.draw.rect(screen, (255, 255, 255), (730, ai_y, 20, 100))
    pygame.draw.circle(screen, (255, 255, 255), (ball_x, ball_y), 10)

    text = font.render(f"{score_player}   {score_ai}", True, (255, 255, 255))
    screen.blit(text, (350, 20))

    # GAME OVER SCREEN
    if game_over:
        winner = "PLAYER WINS!" if score_player == WIN_SCORE else "COMPUTER WINS!"
        win_text = font.render(winner, True, (255, 255, 255))
        screen.blit(win_text, (230, 200))

        start_button_rect = pygame.Rect(300, 350, 200, 80)
        pygame.draw.rect(screen, (255, 255, 255), start_button_rect, border_radius=10)

        restart_text = small_font.render("RESTART", True, (0, 0, 0))
        screen.blit(restart_text, (340, 375))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
