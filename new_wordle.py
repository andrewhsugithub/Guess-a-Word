import threading
import pygame
import os
import time
import random
from convert import WORDS
pygame.init()
clock = pygame.time.Clock()
# Constants
FPS = 60
WIDTH = 528
HEIGHT = 800

# Color
YELLOW = (201, 180, 88)
GREEN = (106, 170, 100)
GREY = (120, 124, 126)
BOX_COLOR = (211, 214, 218)
FILL_BOX_COLOR = (135, 138, 140)

# interface
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('WORDLE!')

# images
box_img = pygame.image.load(os.path.join(
    "assets", "tiles.png")).convert()
box_img = pygame.transform.scale(box_img, (353, 482))
box_rect = box_img.get_rect(center=(WIDTH/2, HEIGHT/3+30))

coin_img = pygame.image.load(os.path.join("assets", "coin.png")).convert()
coin_img = pygame.transform.scale(coin_img, (40, 40))
coin_img.set_colorkey("black")
coin_rect = coin_img.get_rect(topleft=(0, 0))

shop_img = pygame.image.load(os.path.join(
    "assets", "lightbulb.png")).convert()
shop_img = pygame.transform.scale(shop_img, (70, 70))
shop_rect = shop_img.get_rect(topleft=(WIDTH-70, 0))

info_img = pygame.image.load(os.path.join("assets", "info.png")).convert()
info_img = pygame.transform.scale(info_img, (2035/4, 2461/4))

help_img = pygame.image.load(os.path.join("assets", "help.png"))
help_img = pygame.transform.scale(help_img, (30, 30))
help_rect = help_img.get_rect(topleft=(WIDTH-110, 0))

# sound
pygame.mixer.music.load(os.path.join("assets", "think.wav"))
pygame.mixer.music.set_volume(1)
pygame.mixer.music.play(-1)

# word
# CORRECT_WORD = "coder"
CORRECT_WORD = random.choice(WORDS)
ALPHABET = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
letters = {}
letters = set(letters)
for temp in ALPHABET:
    temp = temp.lower()
    for c in temp:
        if c in CORRECT_WORD:
            continue
        letters.add(c)


# fonts
GUESSED_LETTER_FONT = pygame.font.Font("assets/FreeSansBold.otf", 41)
KEY_LETTER_FONT = pygame.font.Font("assets/FreeSansBold.otf", 20)
font_name = pygame.font.match_font('Times New Roman')

# letter spacing
LETTER_X_SPACING = 71
LETTER_Y_SPACING = 56
LETTER_SIZE = 62

# time
times_out = False
timer = ""
t = 120
end_time = 0

# coin
coins = 0

# Global variables(important)
guessCount = 0
keyboards = []
all_guesses = [[] for _ in range(6)]
current_guess = ""
current_letter_box_x = 91  # start from x=91
game_result = ""


def draw_text(surf, letter, size, x, y):
    font = pygame.font.Font(font_name, size)
    letter_surface = font.render(letter, True, "black")
    letter_rect = letter_surface.get_rect()
    letter_rect.centerx = x
    letter_rect.top = y
    pygame.draw.rect(SCREEN, "white", letter_rect)
    surf.blit(letter_surface, letter_rect)


# display
SCREEN.fill("white")
SCREEN.blit(box_img, box_rect)  # won't update so update here
SCREEN.blit(coin_img, coin_rect)
SCREEN.blit(shop_img, shop_rect)
SCREEN.blit(help_img, help_rect)
draw_text(SCREEN, str(coins), 18, 85, 15)
draw_text(SCREEN, str("10"), 18, 498, 75)
draw_text(SCREEN, "00:00", 36, WIDTH/2, 15)
pygame.display.update()

# timer


def countdown():
    global times_out, timer, t, end_time
    while t:
        mins = t // 60
        secs = t % 60
        timer = "{:02d}:{:02d}".format(mins, secs)
        time.sleep(1)
        t -= 1
    #     draw_text(SCREEN, timer, 36, WIDTH/2, 15)
    #     pygame.display.update()
    # draw_text(SCREEN, timer, 36, WIDTH/2, 15)
    # pygame.display.update()
    if t == 0:
        end_time = 0
        times_out = True


# coin
def coin_count():
    global coins, guessCount, game_result, end_time
    if game_result == "W":
        coins += end_time*(6-guessCount+1)
    draw_text(SCREEN, str(coins), 18, 85, 15)
    pygame.display.update()

# shop


def no_money():
    surf = pygame.Surface((400, 100))
    # surf.fill("white")
    surf_rect = surf.get_rect(center=(WIDTH/2, HEIGHT/4))
    # SCREEN.blit(surf, surf_rect)
    pygame.draw.rect(SCREEN, "white", surf_rect)
    draw_text(SCREEN, 'You don\'t have enough money', 32, WIDTH/2, HEIGHT/4)
    pygame.display.update()
    time.sleep(0.5)


def no_hint():
    surf = pygame.Surface((400, 100))
    # surf.fill("white")
    surf_rect = surf.get_rect(center=(WIDTH/2, HEIGHT/4))
    # SCREEN.blit(surf, surf_rect)
    pygame.draw.rect(SCREEN, "white", surf_rect)
    draw_text(SCREEN, 'You have all the hints', 32, WIDTH/2, HEIGHT/4)
    pygame.display.update()
    time.sleep(0.5)


def shop():
    global coins, letters
    if coins < 10:
        no_money()
        return
    if len(letters) == 0:
        no_hint()
        return
    coins -= 10
    draw_text(SCREEN, str(coins), 18, 85, 15)
    hint = random.choice(list(letters))
    letters.remove(hint)
    for keys in keyboards:
        if keys.letter == hint.upper():
            keys.box_color = GREY
            keys.draw()
    pygame.display.update()

# all about typing


class character:
    def __init__(self, letter, position):
        # box
        self.box_color = "white"
        self.box_x = position[0]
        self.box_y = position[1]
        self.box_rect = (self.box_x, self.box_y, LETTER_SIZE, LETTER_SIZE)
        # letter
        self.letter = letter
        self.letter_color = "black"
        self.letter_pos = (self.box_x+30, self.box_y+28)
        self.letter_surf = GUESSED_LETTER_FONT.render(
            self.letter, True, self.letter_color)
        self.letter_rect = self.letter_surf.get_rect(center=self.letter_pos)

    def draw(self):
        pygame.draw.rect(SCREEN, self.box_color, self.box_rect)
        if self.box_color == "white":
            pygame.draw.rect(SCREEN, FILL_BOX_COLOR, self.box_rect, 2)
        self.letter_surface = GUESSED_LETTER_FONT.render(
            self.letter, True, self.letter_color)
        SCREEN.blit(self.letter_surface, self.letter_rect)
        # pygame.display.update()

    def delete(self):
        pygame.draw.rect(SCREEN, "white", self.box_rect)  # fill the rectangle
        # border line thickness = 3/1.2
        pygame.draw.rect(SCREEN, BOX_COLOR, self.box_rect, 2)
        # pygame.display.update()


def create_new_char():
    # Creates a new letter and adds it to the guess.
    global current_guess, current_letter_box_x, guessCount
    current_guess += typed
    # print(current_guess)
    new_letter = character(typed, (current_letter_box_x,
                                   guessCount*83.5+LETTER_Y_SPACING))
    current_letter_box_x += LETTER_X_SPACING  # for next letter
    all_guesses[guessCount].append(new_letter)
    for letter in all_guesses[guessCount]:
        letter.draw()


def delete_letter():
    # Deletes the last letter from the guess.
    global current_guess, current_letter_box_x
    current_guess = current_guess[:-1]  # delete last letter
    all_guesses[guessCount].pop().delete()
    current_letter_box_x -= LETTER_X_SPACING


def too_many_letters():
    surf = pygame.Surface((400, 100))
    # surf.fill("white")
    surf_rect = surf.get_rect(center=(WIDTH/2, HEIGHT/4))
    # SCREEN.blit(surf, surf_rect)
    pygame.draw.rect(SCREEN, "white", surf_rect)
    draw_text(SCREEN, 'Too Many', 32, WIDTH/2, HEIGHT/4)
    pygame.display.update()
    time.sleep(0.5)


def cant_delete():
    surf = pygame.Surface((400, 100))
    # surf.fill("white")
    surf_rect = surf.get_rect(center=(WIDTH/2, HEIGHT/4))
    # SCREEN.blit(surf, surf_rect)
    pygame.draw.rect(SCREEN, "white", surf_rect)
    draw_text(SCREEN, 'No more letters to delete', 32, WIDTH/2, HEIGHT/4)
    pygame.display.update()
    time.sleep(0.5)

# all about pressing


class Key:
    def __init__(self, x, y, letter):
        self.box_color = BOX_COLOR
        self.x = x
        self.y = y
        self.letter = letter
        self.rect = (self.x, self.y, 47, 62)

    def draw(self):
        pygame.draw.rect(SCREEN, self.box_color, self.rect)  # box
        self.letter_surf = KEY_LETTER_FONT.render(
            self.letter, True, "white")  # letter
        self.letter_rect = self.letter_surf.get_rect(
            center=(self.x+22, self.y+25))
        SCREEN.blit(self.letter_surf, self.letter_rect)

    def press(self):
        global current_guess, current_letter_box_x, guessCount
        current_guess += self.letter
        # print(current_guess)
        new_letter = character(self.letter, (current_letter_box_x,
                                             guessCount*83+LETTER_Y_SPACING))
        current_letter_box_x += LETTER_X_SPACING  # for next letter
        all_guesses[guessCount].append(new_letter)
        for letter in all_guesses[guessCount]:
            letter.draw()


# init keyboard
keyboard_x, keyboard_y = 16, 550
for i in range(3):
    for letter in ALPHABET[i]:
        new_keyboard = Key(keyboard_x, keyboard_y, letter)
        keyboards.append(new_keyboard)
        new_keyboard.draw()
        keyboard_x += 50
    keyboard_y += 83
    if i == 0:  # rows 2
        keyboard_x = 41
    elif i == 1:  # rows 3
        keyboard_x = 91

# check


def not_a_word():
    surf = pygame.Surface((400, 100))
    # surf.fill("white")
    surf_rect = surf.get_rect(center=(WIDTH/2, HEIGHT/4))
    # SCREEN.blit(surf, surf_rect)
    pygame.draw.rect(SCREEN, "white", surf_rect)
    draw_text(SCREEN, 'NOT A WORD', 32, WIDTH/2, HEIGHT/4)
    pygame.display.update()
    time.sleep(0.5)


def not_enough_letters():
    surf = pygame.Surface((400, 100))
    # surf.fill("white")
    surf_rect = surf.get_rect(center=(WIDTH/2, HEIGHT/4))
    # SCREEN.blit(surf, surf_rect)
    pygame.draw.rect(SCREEN, "white", surf_rect)
    draw_text(SCREEN, 'Please type a 5-letter word', 32, WIDTH/2, HEIGHT/4)
    pygame.display.update()
    time.sleep(0.5)


def check_guess(my_guess):
    # Goes through each letter and checks if it should be green, yellow, or grey.
    global all_guesses, current_guess, guessCount, current_letter_box_x, game_result, t, end_time, letters
    wrong_ans = False  # cannot set correct_ans = True cause you need all green in order to be correct, so if you encounter the first green it doesn't mean it is the correct answer
    # print(my_guess)
    for i in range(5):
        char = my_guess[i].letter.lower()
        if char in letters:
            letters.remove(char)
        if char in CORRECT_WORD:  # have a correct letter
            if char == CORRECT_WORD[i]:  # correct pos=>green
                my_guess[i].box_color = GREEN
                for keys in keyboards:
                    if keys.letter == char.upper():
                        if keys.box_color != GREEN:
                            t += 5
                        keys.box_color = GREEN
                        # keys.draw()
                my_guess[i].letter_color = "white"
                # if ans is correct (wrong ans is still false)
                if not wrong_ans:
                    game_result = "W"  # correct ans
                    # print(t)
                    end_time = t
            else:  # correct letter=>yellow
                my_guess[i].box_color = YELLOW
                for keys in keyboards:
                    if keys.letter == char.upper():
                        if keys.box_color == GREY:
                            t += 1
                        keys.box_color = YELLOW
                        keys.draw()
                my_guess[i].letter_color = "white"
                game_result = ""
                wrong_ans = True  # means wrong answer cause got at least one yellow
        else:  # not in word
            my_guess[i].box_color = GREY
            for keys in keyboards:
                if keys.letter == char.upper():
                    keys.box_color = GREY
                    keys.draw()
            my_guess[i].letter_color = "white"
            game_result = ""
            wrong_ans = True  # means wrong answer cause got at least one yellow
        my_guess[i].draw()  # update letter
        # pygame.display.update()
        # time.sleep(0.3)

    guessCount += 1  # add current guess
    current_guess = ""  # clear
    current_letter_box_x = 91  # reset starting x

    if guessCount == 6 and game_result == "":
        game_result = "L"

# reseting


def play_again():
    # Puts the play again text on the SCREEN.
    pygame.draw.rect(SCREEN, "white", (8,
                     550, 833, 500))
    play_again_font = pygame.font.Font("assets/FreeSansBold.otf", 33)
    play_again_text = play_again_font.render(
        "Press ENTER to Play Again!", True, "black")
    play_again_rect = play_again_text.get_rect(
        center=(WIDTH/2, 633))
    word_was_text = play_again_font.render(
        f"The word was {CORRECT_WORD}!", True, "black")
    word_was_rect = word_was_text.get_rect(center=(WIDTH/2, 591))
    SCREEN.blit(word_was_text, word_was_rect)
    SCREEN.blit(play_again_text, play_again_rect)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        # GET INPUT
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False


def reset():
    global t, times_out, current_letter_box_x
    # Resets all global variables to their default states.
    global guessCount, CORRECT_WORD, all_guesses, current_guess, game_result, letters
    SCREEN.fill("white")
    SCREEN.blit(box_img, box_rect)
    SCREEN.blit(coin_img, coin_rect)
    coin_count()
    if times_out == True:
        t = 120
        threading.Thread(target=countdown).start()
    else:
        t = 120
    times_out = False
    guessCount = 0
    CORRECT_WORD = random.choice(WORDS)
    letters.clear()
    for temp in ALPHABET:
        temp = temp.lower()
        for c in temp:
            if c in CORRECT_WORD:
                continue
            letters.add(c)
    all_guesses = [[] for _ in range(6)]
    current_guess = ""
    game_result = ""
    current_letter_box_x = 91
    for keys in keyboards:
        keys.box_color = BOX_COLOR
        keys.draw()


def info():
    surf = pygame.Surface((550, 615+70))
    # surf.fill("white")
    surf_rect = surf.get_rect(topleft=(WIDTH/60, 70))
    # SCREEN.blit(surf, surf_rect)
    pygame.draw.rect(SCREEN, "white", surf_rect)
    SCREEN.blit(info_img, (WIDTH/60, 70))
    draw_text(SCREEN, 'PRESS ANY KEY TO PLAY!', 32, WIDTH/2, 615+70)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False


info()
running = True
click = False
threading.Thread(target=countdown).start()
while running:
    clock.tick(FPS)
    if game_result != "" or times_out == True:
        close = play_again()
        if close:
            break
        reset()
    mouse_pos = pygame.mouse.get_pos()
    if shop_rect.collidepoint(mouse_pos):
        if click:
            shop()
    if help_rect.collidepoint(mouse_pos):
        if click:
            info()
    for keys in keyboards:
        if pygame.Rect(keys).collidepoint(mouse_pos):
            if click:
                if len(current_guess) < 5:
                    keys.press()
                else:
                    too_many_letters()
    click = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button:
                click = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # enter key
                if len(current_guess) == 5:
                    if current_guess.lower() in WORDS:
                        # for i in all_guesses[guessCount]:
                        #     print(i.letter)
                        check_guess(all_guesses[guessCount])
                    else:
                        not_a_word()
                    # time.sleep(1.6)
                else:
                    not_enough_letters()
            elif event.key == pygame.K_BACKSPACE:
                if game_result != "" or times_out == True:
                    continue
                if len(current_guess) > 0:
                    delete_letter()
                else:
                    cant_delete()
            else:
                if game_result != "" or times_out == True:
                    continue
                typed = event.unicode.upper()
                if typed in "QWERTYUIOPASDFGHJKLZXCVBNM" and typed != "":
                    if len(current_guess) < 5:
                        create_new_char()
                    else:
                        too_many_letters()
    # update
    SCREEN.fill("white")
    SCREEN.blit(box_img, box_rect)
    for guesses in all_guesses:
        for letter in guesses:
            letter.draw()
    for keys in keyboards:
        keys.draw()
    SCREEN.blit(coin_img, coin_rect)
    SCREEN.blit(shop_img, shop_rect)
    SCREEN.blit(help_img, help_rect)
    draw_text(SCREEN, str(coins), 18, 85, 15)
    draw_text(SCREEN, str("10"), 18, 498, 75)
    draw_text(SCREEN, timer, 36, WIDTH/2, 15)
    pygame.display.update()
pygame.quit()
