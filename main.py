import pgzrun
from pygame import Rect
from pgzero.clock import schedule_interval
import random
import os
import ast

# --- Screen setup ---
WIDTH = 1280
HEIGHT = 720

# --- Custom Pixel Font ---
pixel_font = "pixeltype"

# Use the same pixel font for all text sizes
title_font = pixel_font
large_font = pixel_font
medium_font = pixel_font
small_font = pixel_font

# Cat images
cat_images = [
    Actor("cat1"),
    Actor("cat2"),
    Actor("cat3"),
    Actor("cat4")
]

# Background images
bg_image = Actor("firstfinal")  # For starting page
main_background = Actor("mainback")  # For all question screens

# --- Boxes setup ---
main_box = Rect(0, 0, 820, 240)
timer_box = Rect(0, 0, 240, 240)
answer_box1 = Rect(0, 0, 495, 165)
answer_box2 = Rect(0, 0, 495, 165)
answer_box3 = Rect(0, 0, 495, 165)
answer_box4 = Rect(0, 0, 495, 165)

main_box.move_ip(50, 40)
timer_box.move_ip(990, 40)
answer_box1.move_ip(50, 358)
answer_box2.move_ip(735, 358)
answer_box3.move_ip(50, 538)
answer_box4.move_ip(735, 538)

answer_boxes = [answer_box1, answer_box2, answer_box3, answer_box4]

# --- Start button setup ---
start_button = Rect(WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 100)

# --- Game variables ---
score = 0
time_left = 10
level = 1
game_active = False
lives = 3
high_score = 0
highscore_holder = "Nobody"
player_name = "Player"
highscore_file = "highscore.txt"
name_input_active = False
player_name = ""
starting_page = True
difficulty_selected = False
difficulty = "Medium"
player_selection_active = False
selected_player = None

# Player characters data WITH IMAGE REFERENCES
players = [
    {"name": "OLIVIA", "color": "pink", "selected": False, "image": cat_images[0]},
    {"name": "SAMIRA", "color": "purple", "selected": False, "image": cat_images[1]},
    {"name": "KIM", "color": "lightblue", "selected": False, "image": cat_images[2]},
    {"name": "DREW", "color": "lightgreen", "selected": False, "image": cat_images[3]}
]

# Player selection boxes
player_box_width = 250
player_box_height = 300
player_spacing = 50
total_players_width = len(players) * player_box_width + (len(players) - 1) * player_spacing
players_start_x = (WIDTH - total_players_width) // 2
players_start_y = HEIGHT // 2 - 50

# Continue button
continue_button = Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 60)

# Yes/No buttons for game over
yes_button = Rect(WIDTH // 2 - 250, HEIGHT - 100, 150, 60)
no_button = Rect(WIDTH // 2 + 100, HEIGHT - 100, 150, 60)

# Highscores
highscores = []


def load_highscores():
    global highscores
    highscores = []
    if os.path.exists(highscore_file):
        with open(highscore_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                try:
                    score = int(parts[0])
                    name = ",".join(parts[1:]).strip()
                    highscores.append((score, name))
                except ValueError:
                    continue
    highscores.sort(key=lambda x: x[0], reverse=True)
    highscores = highscores[:3]


def save_highscores():
    with open(highscore_file, "w", encoding="utf-8") as f:
        for score, name in highscores:
            f.write(f"{score},{name}\n")


load_highscores()


# --- Loading questions from file (if exists) ---
def load_questions_from_file(filename):
    questions = []
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        q = ast.literal_eval(line)  # convert string → list
                        questions.append(q)
                    except Exception as e:
                        print("Error loading question:", e)
    return questions


# --- Question Sets by Difficulty ---
easy_questions = load_questions_from_file("easy.txt")
medium_questions = load_questions_from_file("medium.txt")
hard_questions = load_questions_from_file("hard.txt")

# Set default question set
questions = medium_questions.copy()
random.shuffle(questions)
current_questions = questions.pop(0) if questions else ["No questions loaded!", "-", "-", "-", "-", 1]


# --- Draw everything with pixel font ---
def draw():
    if starting_page:
        # For starting page, use firstbg image
        draw_starting_page()
    elif name_input_active:
        # For name input, use mainback image
        main_background.pos = (WIDTH // 2, HEIGHT // 2)
        main_background.draw()
        draw_name_input()
    elif player_selection_active:
        # For player selection, use mainback image
        main_background.pos = (WIDTH // 2, HEIGHT // 2)
        main_background.draw()
        draw_player_selection()
    elif not difficulty_selected and not name_input_active and not game_active and not starting_page:
        # For difficulty selection, use mainback image
        main_background.pos = (WIDTH // 2, HEIGHT // 2)
        main_background.draw()
        draw_difficulty_selection()
    elif game_active:
        # For game active, use mainback image
        main_background.pos = (WIDTH // 2, HEIGHT // 2)
        main_background.draw()
        draw_game_active()
    else:
        # For game over, use mainback image
        main_background.pos = (WIDTH // 2, HEIGHT // 2)
        main_background.draw()
        draw_game_over()


def draw_starting_page():
    # Draw background image covering the entire screen
    bg_image.pos = (WIDTH // 2, HEIGHT // 2)
    bg_image.draw()

    # Draw welcome text on top of background
    screen.draw.text(
        "Welcome to the Quiz Game!",
        center=(WIDTH // 2, HEIGHT // 2 - 200),
        color="white",
        fontsize=64,
        fontname=title_font
    )
    screen.draw.filled_rect(start_button, "orange")
    screen.draw.text(
        "Click to Start",
        center=start_button.center,
        color="white",
        fontsize=48,
        fontname=large_font
    )


def draw_name_input():
    screen.draw.text(
        "Enter your name and press Enter:",
        center=(WIDTH // 2, HEIGHT // 2 - 50),
        color="white",
        fontsize=48,
        fontname=large_font
    )
    screen.draw.text(
        player_name + "|",
        center=(WIDTH // 2, HEIGHT // 2 + 50),
        color="yellow",
        fontsize=48,
        fontname=large_font
    )


def draw_player_selection():
    screen.draw.text(
        "PLAYERS",
        center=(WIDTH // 2, HEIGHT // 2 - 200),
        color="white",
        fontsize=72,
        fontname=title_font
    )

    for i, player in enumerate(players):
        player_x = players_start_x + i * (player_box_width + player_spacing)
        player_y = players_start_y

        if player["selected"]:
            box_color = "gold"
            border_color = "yellow"
        else:
            box_color = player["color"]
            border_color = "white"

        player_rect = Rect(player_x, player_y, player_box_width, player_box_height)
        screen.draw.filled_rect(player_rect, box_color)
        screen.draw.rect(player_rect, border_color)

        # DRAW CAT IMAGE
        image_x = player_x + player_box_width // 2
        image_y = player_y + player_box_height // 2 - 20

        # Position and draw the cat image
        player["image"].pos = (image_x, image_y)
        player["image"].draw()

        # Draw player name below the image
        screen.draw.text(
            player["name"],
            center=(player_x + player_box_width // 2, player_y + player_box_height - 40),
            color="black",
            fontsize=36,
            fontname=medium_font
        )

    if selected_player is not None:
        screen.draw.filled_rect(continue_button, "green")
        screen.draw.text(
            "Continue",
            center=continue_button.center,
            color="white",
            fontsize=36,
            fontname=medium_font
        )


def draw_difficulty_selection():
    screen.draw.text(
        "Select Difficulty",
        center=(WIDTH // 2, HEIGHT // 2 - 150),
        color="white",
        fontsize=60,
        fontname=title_font
    )
    difficulties = ["Easy", "Medium", "Hard"]
    colors = ["green", "orange", "red"]

    for i, (diff, color) in enumerate(zip(difficulties, colors)):
        box = Rect(WIDTH // 2 - 150, HEIGHT // 2 - 50 + i * 120, 300, 80)
        screen.draw.filled_rect(box, color)
        screen.draw.text(
            diff,
            center=box.center,
            color="white",
            fontsize=48,
            fontname=large_font
        )


def draw_game_active():
    # Draw semi-transparent boxes for better readability
    screen.draw.filled_rect(main_box, (135, 206, 235, 200))  # sky blue with transparency
    screen.draw.filled_rect(timer_box, (135, 206, 235, 200))  # sky blue with transparency

    for box in answer_boxes:
        screen.draw.filled_rect(box, (255, 165, 0, 200))  # orange with transparency

    screen.draw.text(
        f"level {level}",
        (60, 60),
        color="white",
        fontsize=60,
        fontname=title_font
    )
    screen.draw.text(
        f"Lives: {lives}",
        (WIDTH - 200, 60),
        color="white",
        fontsize=48,
        fontname=large_font
    )

    screen.draw.text(
        str(time_left),
        center=timer_box.center,
        color="white",
        fontsize=72,
        fontname=title_font
    )
    screen.draw.text(
        current_questions[0],
        center=main_box.center,
        color="white",
        fontsize=48,
        align="center",
        fontname=large_font
    )

    index = 1
    for box in answer_boxes:
        screen.draw.text(
            current_questions[index],
            center=box.center,
            color="white",
            fontsize=36,
            fontname=medium_font
        )
        index += 1


def draw_game_over():
    screen.draw.text(
        game_over_message,
        center=(WIDTH // 2, HEIGHT // 2 - 120),
        color="gold" if "New High Score" in game_over_message else "red",
        fontsize=72,
        fontname=title_font
    )
    screen.draw.text(
        f"Your Score: {score}",
        center=(WIDTH // 2, HEIGHT // 2 - 40),
        color="white",
        fontsize=60,
        fontname=large_font
    )

    screen.draw.text(
        "Leaderboard",
        center=(WIDTH // 2, HEIGHT // 2 + 40),
        color="gold",
        fontsize=48,
        fontname=large_font
    )

    ystart = HEIGHT // 2 + 100
    for i, (s, name) in enumerate(highscores):
        if i == 0:
            color = "gold"
            fontsize = 48
            font = title_font
        elif i == 1:
            color = "silver"
            fontsize = 38
            font = large_font
        elif i == 2:
            color = "orange"
            fontsize = 28
            font = medium_font
        else:
            color = "white"
            fontsize = 30
            font = small_font
        screen.draw.text(
            f"{i + 1}. {name} - {s}",
            center=(WIDTH // 2, ystart + i * 50),
            color=color,
            fontsize=fontsize,
            fontname=font
        )

    # Yes/No buttons
    screen.draw.filled_rect(yes_button, "green")
    screen.draw.text(
        "YES",
        center=yes_button.center,
        color="white",
        fontsize=36,
        fontname=large_font
    )

    screen.draw.filled_rect(no_button, "red")
    screen.draw.text(
        "NO",
        center=no_button.center,
        color="white",
        fontsize=36,
        fontname=large_font
    )


# --- Game functions ---
def next_level():
    global level, time_left
    level += 1
    time_left = 10


def game_over():
    global game_active, time_left, score, player_name, highscores, game_over_message
    game_active = False
    time_left = 0

    player_name_clean = player_name.strip() or "Player"
    load_highscores()

    if score > 0 and (len(highscores) < 3 or score > highscores[-1][0]):
        highscores.append((score, player_name_clean))
        highscores.sort(key=lambda x: x[0], reverse=True)
        highscores = highscores[:3]
        save_highscores()
        game_over_message = f"New High Score Achieved! Score: {score}"
    else:
        game_over_message = f"Game Over! Final Score: {score}"


def correct_answer():
    global score, time_left, questions, current_questions, game_active
    score += 1
    if questions:
        current_questions = questions.pop(0)
        time_left = 10
        next_level()
    else:
        game_active = False
        time_left = 0
        current_questions = [f"You Win! Final Score: {score}", "-", "-", "-", "-", 5]
        game_over()


def on_mouse_down(pos):
    global starting_page, name_input_active, difficulty_selected, game_active
    global difficulty, questions, current_questions, player_selection_active, selected_player
    global score, level, lives, time_left, player_name

    if starting_page and start_button.collidepoint(pos):
        starting_page = False
        name_input_active = True

    elif player_selection_active:
        for i, player in enumerate(players):
            player_x = players_start_x + i * (player_box_width + player_spacing)
            player_y = players_start_y
            player_rect = Rect(player_x, player_y, player_box_width, player_box_height)

            if player_rect.collidepoint(pos):
                for p in players:
                    p["selected"] = False
                player["selected"] = True
                selected_player = player["name"]
                break

        if selected_player is not None and continue_button.collidepoint(pos):
            player_selection_active = False
            difficulty_selected = False

    elif not difficulty_selected:
        difficulties = ["Easy", "Medium", "Hard"]
        for i, diff in enumerate(difficulties):
            box = Rect(WIDTH // 2 - 150, HEIGHT // 2 - 50 + i * 120, 300, 80)
            if box.collidepoint(pos):
                difficulty = diff
                difficulty_selected = True
                game_active = True
                time_left = 10
                if difficulty == "Easy":
                    questions = easy_questions.copy()
                elif difficulty == "Medium":
                    questions = medium_questions.copy()
                else:
                    questions = hard_questions.copy()
                random.shuffle(questions)
                current_questions = questions.pop(0)
                break

    elif game_active:
        for i, box in enumerate(answer_boxes):
            if box.collidepoint(pos):
                if i + 1 == current_questions[5]:
                    correct_answer()
                else:
                    lives -= 1
                    if lives <= 0:
                        game_over()

    elif not game_active and not name_input_active and not player_selection_active and difficulty_selected:
        if yes_button.collidepoint(pos):
            score = 0
            level = 1
            lives = 3
            time_left = 10
            difficulty = None
            difficulty_selected = False
            name_input_active = True
            starting_page = True
            player_selection_active = False
            player_name = ""
            selected_player = None
            for player in players:
                player["selected"] = False
        elif no_button.collidepoint(pos):
            exit()


def on_key_down(key):
    global game_active, score, level, time_left, current_questions, questions, lives
    global name_input_active, player_name, difficulty, difficulty_selected, starting_page
    global player_selection_active, selected_player, players

    if name_input_active:
        if key == keys.RETURN:
            if player_name.strip() == "":
                player_name = "Player"
            name_input_active = False
            player_selection_active = True
        elif key == keys.BACKSPACE:
            player_name = player_name[:-1]
        else:
            if len(key.name) == 1 and len(player_name) < 20:
                player_name += key.name

    elif not game_active and not name_input_active and not player_selection_active:
        if not difficulty_selected:
            if key == keys.E:
                difficulty = "Easy"
                questions = easy_questions.copy()
                random.shuffle(questions)
                start_game()
            elif key == keys.M:
                difficulty = "Medium"
                questions = medium_questions.copy()
                random.shuffle(questions)
                start_game()
            elif key == keys.H:
                difficulty = "Hard"
                questions = hard_questions.copy()
                random.shuffle(questions)
                start_game()


def start_game():
    global game_active, current_questions
    game_active = True
    current_questions = questions.pop(0)


def update_time_left():
    global time_left
    if not name_input_active and game_active:
        if time_left > 0:
            time_left -= 1
        else:
            game_over()


schedule_interval(update_time_left, 1.0)

pgzrun.go()