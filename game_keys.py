import pygame
from random import randint


def run_game(difficulty):
    pygame.init()
    pygame.mixer.init()
    window_size = (1200, 800)
    window = pygame.display.set_mode(window_size)
    pygame.display.set_caption("Flappy Bird - Класика")

    clock = pygame.time.Clock()
    FPS = 60

    SND_CLICK = pygame.mixer.Sound('sfx/menuclick.mp3')
    SND_GAMEOVER = pygame.mixer.Sound('sfx/gameover.mp3')
    SND_FLAP = pygame.mixer.Sound('sfx/flap.mp3')
    SND_DEATH = pygame.mixer.Sound('sfx/death.mp3')

    if difficulty == "easy":
        pipe_speed = 5
        pipe_gap = 340
    elif difficulty == "medium":
        pipe_speed = 7
        pipe_gap = 270
    else:
        pipe_speed = 10
        pipe_gap = 210

    game_state = "PLAYING"
    death_timer = 0

    score = 0
    y_vel = 0.0
    gravity = 0.5
    IMPULSE = -9.0
    bird_angle = 0.0

    FONT_GAME_OVER = pygame.font.Font('Tiny5-Regular.ttf', 80)
    FONT_UI = pygame.font.Font('Tiny5-Regular.ttf', 45)

    COLOR_TEXT = (247, 183, 51)
    COLOR_HOVER = (255, 230, 150)
    COLOR_SHADOW = (34, 32, 52)

    # Змінено на gamebg.jpg
    BACKGROUND_IMG = pygame.image.load('bg/gamebg.jpg')
    BACKGROUND_IMG = pygame.transform.scale(BACKGROUND_IMG, window_size)

    BIRD_ORIGINAL = pygame.image.load('bird/bird.png')
    BIRD_ORIGINAL = pygame.transform.scale(BIRD_ORIGINAL, (100, 100))
    player_rect = pygame.Rect(100, 350, 100, 100)

    PIPE_BASE = pygame.image.load('pipe/pipe.png')
    PIPE_W, PIPE_H = 140, 440
    PIPE_BOTTOM = pygame.transform.scale(PIPE_BASE, (PIPE_W, PIPE_H))
    PIPE_TOP = pygame.transform.flip(PIPE_BOTTOM, False, True)

    def generate_pipes(count, pipe_width=140, gap=280, min_height=50, max_height=440, distance=650):
        pipes = []
        start_x = window_size[0]
        for i in range(count):
            height = randint(min_height, max_height)
            top_pipe = pygame.Rect(start_x, 0, pipe_width, height)
            bottom_pipe = pygame.Rect(start_x, height + gap, pipe_width, window_size[1] - (height + gap))
            pipes.extend([top_pipe, bottom_pipe])
            start_x += distance
        return pipes

    def draw_pixel_text(text, font, color, x, y):
        text_shadow = font.render(text, True, COLOR_SHADOW)
        text_main = font.render(text, True, color)
        rect = text_main.get_rect(center=(x, y))
        window.blit(text_shadow, (rect.x + 4, rect.y + 4))
        window.blit(text_main, rect)
        return rect

    pipes = generate_pipes(150, gap=pipe_gap)

    run = True
    while run:
        mouse_clicked = False
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_state == "PLAYING":
                    y_vel = IMPULSE
                    SND_FLAP.play()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        window.blit(BACKGROUND_IMG, (0, 0))

        if game_state == "PLAYING":
            y_vel += gravity
            player_rect.y += int(y_vel)
            target_angle = max(-70, min(30, -y_vel * 5))
            bird_angle += (target_angle - bird_angle) * 0.2

            if player_rect.bottom > window_size[1]:
                player_rect.bottom = window_size[1]
                game_state = "DYING"
                death_timer = pygame.time.get_ticks()
                SND_DEATH.play()

        elif game_state == "DYING":
            if player_rect.bottom < window_size[1]:
                player_rect.y += 12
            bird_angle += (-90 - bird_angle) * 0.2

            if pygame.time.get_ticks() - death_timer >= 2000:
                game_state = "GAMEOVER"
                SND_GAMEOVER.play()

        if player_rect.top < 0:
            player_rect.top = 0
            y_vel = 0

        if len(pipes) < 8:
            pipes += generate_pipes(150, gap=pipe_gap)

        for pipe in pipes[:]:
            if game_state == "PLAYING":
                pipe.x -= pipe_speed

            if pipe.y == 0:
                pipe_img = pygame.transform.scale(PIPE_TOP, (pipe.width, pipe.height))
                window.blit(pipe_img, (pipe.x, pipe.y))
            else:
                pipe_img = pygame.transform.scale(PIPE_BOTTOM, (pipe.width, pipe.height))
                window.blit(pipe_img, (pipe.x, pipe.y))

            if pipe.x <= -140:
                pipes.remove(pipe)
                score += 0.5

            if game_state == "PLAYING" and player_rect.colliderect(pipe):
                game_state = "DYING"
                death_timer = pygame.time.get_ticks()
                SND_DEATH.play()

        rotated_bird = pygame.transform.rotate(BIRD_ORIGINAL, bird_angle)
        new_rect = rotated_bird.get_rect(center=player_rect.center)
        window.blit(rotated_bird, new_rect.topleft)

        if game_state == "PLAYING" or game_state == "DYING":
            draw_pixel_text(f"РАХУНОК: {int(score)}", FONT_UI, (255, 255, 255), window_size[0] // 2, 50)

        # Переклад екрана Game Over
        if game_state == "GAMEOVER":
            overlay = pygame.Surface(window_size)
            overlay.fill(COLOR_SHADOW)
            overlay.set_alpha(150)
            window.blit(overlay, (0, 0))

            draw_pixel_text("КІНЕЦЬ ГРИ", FONT_GAME_OVER, (242, 83, 83), window_size[0] // 2, 250)
            draw_pixel_text(f"ФІНАЛЬНИЙ РАХУНОК: {int(score)}", FONT_UI, (255, 255, 255), window_size[0] // 2, 340)

            again_rect = pygame.Rect(0, 0, 300, 60)
            again_rect.center = (window_size[0] // 2, 460)
            color_again = COLOR_HOVER if again_rect.collidepoint(mouse_pos) else COLOR_TEXT
            draw_pixel_text("ГРАТИ ЗНОВУ", FONT_UI, color_again, window_size[0] // 2, 460)

            if again_rect.collidepoint(mouse_pos) and mouse_clicked:
                SND_CLICK.play()
                game_state = "PLAYING"
                score = 0
                pipes = generate_pipes(150, gap=pipe_gap)
                player_rect.center = (150, 350)
                y_vel = 0.0
                bird_angle = 0.0

            exit_rect = pygame.Rect(0, 0, 200, 60)
            exit_rect.center = (window_size[0] // 2, 550)
            color_exit = COLOR_HOVER if exit_rect.collidepoint(mouse_pos) else COLOR_TEXT
            draw_pixel_text("ВИХІД", FONT_UI, color_exit, window_size[0] // 2, 550)

            if exit_rect.collidepoint(mouse_pos) and mouse_clicked:
                SND_CLICK.play()
                run = False

        pygame.display.update()
        clock.tick(FPS)