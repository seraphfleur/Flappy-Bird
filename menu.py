import pygame
import math
import sys

pygame.init()
pygame.mixer.init()

window_size = (1200, 800)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Flappy Bird - Головне Меню")

clock = pygame.time.Clock()
FPS = 60

# =========================================================================
# ======================== ШРИФТИ, ЗВУКИ ТА ЗОБРАЖЕННЯ ====================
# =========================================================================

FONT_BIG = pygame.font.Font('Tiny5-Regular.ttf', 70)
FONT_MENU = pygame.font.Font('Tiny5-Regular.ttf', 55)

SND_CLICK = pygame.mixer.Sound('sfx/menuclick.mp3')

# Змінено на menubg.png
BACKGROUND_IMG = pygame.image.load('bg/menubg.png')
BACKGROUND_IMG = pygame.transform.scale(BACKGROUND_IMG, window_size)

LOGO_IMG = pygame.image.load('logo.png')

COLOR_TEXT = (247, 183, 51)
COLOR_HOVER = (255, 230, 150)
COLOR_SHADOW = (34, 32, 52)

# =========================================================================
# =========================== СТАНУ ТА СТРУКТУРА ==========================
# =========================================================================

STATE_MAIN = "main_menu"
STATE_MODES = "mode_selection"
STATE_DIFFICULTY = "difficulty_selection"
current_state = STATE_MAIN
chosen_mode = None

logo_hover_timer = 0
pulse_timer = 0
arrow_y = 450.0
target_arrow_y = 450.0

fade_alpha = 0
fade_speed = 15
is_fading = False
next_state = None


def draw_pixel_text(text, font, color, x, y, center=True):
    text_shadow = font.render(text, True, COLOR_SHADOW)
    text_main = font.render(text, True, color)
    rect_main = text_main.get_rect()
    if center:
        rect_main.center = (x, y)
    else:
        rect_main.topleft = (x, y)
    window.blit(text_shadow, (rect_main.x + 4, rect_main.y + 4))
    window.blit(text_main, rect_main)
    return rect_main


run = True
while run:
    clock.tick(FPS)
    logo_hover_timer += 0.05
    pulse_timer += 0.1
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_clicked = True

    window.blit(BACKGROUND_IMG, (0, 0))

    logo_y_offset = math.sin(logo_hover_timer) * 15
    window.blit(LOGO_IMG, ((window_size[0] - 987) // 2, 80 + logo_y_offset))

    # Переклад кнопок меню
    buttons = []
    if current_state == STATE_MAIN:
        buttons = [
            {"text": "ГРАТИ", "action": "go_to_modes", "y": 450},
            {"text": "ВИХІД", "action": "exit_game", "y": 550}
        ]
    elif current_state == STATE_MODES:
        buttons = [
            {"text": "РЕЖИМ КЛАВІАТУРИ", "action": "set_keys", "y": 420},
            {"text": "ГОЛОСОВИЙ РЕЖИМ", "action": "set_voice", "y": 510},
            {"text": "НАЗАД", "action": "go_to_main", "y": 620}
        ]
    elif current_state == STATE_DIFFICULTY:
        buttons = [
            {"text": "ЛЕГКА", "action": "start_easy", "y": 400},
            {"text": "СЕРЕДНЯ", "action": "start_medium", "y": 490},
            {"text": "ВАЖКА", "action": "start_hard", "y": 580},
            {"text": "НАЗАД", "action": "go_to_modes", "y": 670}
        ]

    any_hovered = False
    for btn in buttons:
        temp_surf = FONT_MENU.render(btn["text"], True, COLOR_TEXT)
        temp_rect = temp_surf.get_rect(center=(window_size[0] // 2, btn["y"]))

        if temp_rect.collidepoint(mouse_pos):
            any_hovered = True
            target_arrow_y = btn["y"]
            draw_pixel_text(btn["text"], FONT_MENU, COLOR_HOVER, window_size[0] // 2, btn["y"])

            if mouse_clicked and not is_fading:
                SND_CLICK.play()
                if btn["action"] == "go_to_modes":
                    is_fading = True;
                    next_state = STATE_MODES
                elif btn["action"] == "go_to_main":
                    is_fading = True;
                    next_state = STATE_MAIN
                elif btn["action"] == "exit_game":
                    run = False
                elif btn["action"] == "set_keys":
                    chosen_mode = "keys";
                    is_fading = True;
                    next_state = STATE_DIFFICULTY
                elif btn["action"] == "set_voice":
                    chosen_mode = "voice";
                    is_fading = True;
                    next_state = STATE_DIFFICULTY
                elif btn["action"].startswith("start_"):
                    diff = btn["action"].split("_")[1]
                    if chosen_mode == "keys":
                        import game_keys

                        game_keys.run_game(diff)
                    elif chosen_mode == "voice":
                        import game_voice

                        game_voice.run_game(diff)
        else:
            draw_pixel_text(btn["text"], FONT_MENU, COLOR_TEXT, window_size[0] // 2, btn["y"])

    if any_hovered:
        arrow_y += (target_arrow_y - arrow_y) * 0.15
        # Збільшено відступ до -340 через довжину фрази "РЕЖИМ КЛАВІАТУРИ"
        arrow_x = window_size[0] // 2 - 340 + math.sin(pulse_timer * 1.5) * 8
        draw_pixel_text(">", FONT_MENU, COLOR_TEXT, arrow_x, arrow_y)

    if is_fading:
        fade_alpha += fade_speed
        if fade_alpha >= 255:
            fade_alpha = 255
            current_state = next_state
            is_fading = False
    else:
        if fade_alpha > 0:
            fade_alpha -= fade_speed

    if fade_alpha > 0:
        fade_surface = pygame.Surface(window_size)
        fade_surface.fill(COLOR_SHADOW)
        fade_surface.set_alpha(fade_alpha)
        window.blit(fade_surface, (0, 0))

    pygame.display.update()

pygame.quit()
sys.exit()