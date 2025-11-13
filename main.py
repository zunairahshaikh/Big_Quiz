import pgzrun
from pygame import Rect
from pgzero.clock import schedule_interval
import random
import os

# --- Screen setup ---
WIDTH = 1280
HEIGHT = 720

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
player_name = "Player"  # default name
highscore_file = "highscore.txt"
name_input_active = False
player_name = ""
starting_page = True  # New state for the starting page
difficulty_selected = False
difficulty = "Medium"  # default


# New: store top scores as a list of (score, name)
highscores = []  # will hold up to 5 entries (score:int, name:str)

# Load the top 5 scores from the file
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
    highscores = highscores[:3]  # Keep only the top 3

# Save the top 3 scores to the file
def save_highscores():
    with open(highscore_file, "w", encoding="utf-8") as f:
        for score, name in highscores:
            f.write(f"{score},{name}\n")

# Load highscores at startup
load_highscores()

# --- Question Sets by Difficulty ---

easy_questions = [
    ["What is 2 + 2?", "4", "3", "5", "6", 1],
    ["What color is the sky?", "Blue", "Red", "Green", "Yellow", 1],
    ["What do bees make?", "Honey", "Milk", "Water", "Silk", 1],
    ["Which shape has 3 sides?", "Triangle", "Square", "Circle", "Pentagon", 1],
    ["Which animal says 'Meow'?", "Cat", "Dog", "Cow", "Lion", 1],
]

medium_questions = [
    ["What is the capital of France?", "Paris", "London", "Berlin", "Rome", 1],
    ["Which gas do plants release during photosynthesis?", "Oxygen", "Carbon Dioxide", "Nitrogen", "Hydrogen", 1],
    ["How many continents are there?", "7", "5", "6", "8", 1],
    ["What color do you get when you mix red and white?", "Pink", "Orange", "Purple", "Gray", 1],
    ["Which planet is known as the Red Planet?", "Mars", "Jupiter", "Venus", "Mercury", 1],
]

hard_questions = [
    ["Who developed the theory of relativity?", "Einstein", "Newton", "Tesla", "Darwin", 1],
    ["What is the square root of 144?", "12", "14", "10", "11", 1],
    ["What is the chemical symbol for Gold?", "Au", "Ag", "Pb", "Fe", 1],
    ["Which element has the atomic number 1?", "Hydrogen", "Oxygen", "Helium", "Carbon", 1],
    ["Which organ in the human body filters blood?", "Kidney", "Heart", "Liver", "Lungs", 1],
]

# Set default question set (Medium by default)
questions = medium_questions.copy()
random.shuffle(questions)
current_questions = questions.pop(0)


# --- Draw everything ---
def draw():
    screen.fill("dimgray")
    if starting_page:  # Starting page
        # Draw welcome text
        screen.draw.text(
            "Welcome to the Quiz Game!",
            center=(WIDTH // 2, HEIGHT // 2 - 200),
            color="white",
            fontsize=64,
        )
        # Draw the "Click to Start" button
        screen.draw.filled_rect(start_button, "orange")
        screen.draw.text(
            "Click to Start",
            center=start_button.center,
            color="white",
            fontsize=48,
        )
    elif name_input_active:  # Name input screen
        screen.draw.text(
            "Enter your name and press Enter:",
            center=(WIDTH // 2, HEIGHT // 2 - 50),
            color="white",
            fontsize=48,
        )
        screen.draw.text(
            player_name + "|",  # Show a cursor
            center=(WIDTH // 2, HEIGHT // 2 + 50),
            color="yellow",
            fontsize=48,
        )
    elif difficulty_selected == False and not name_input_active and not game_active and not starting_page:
        screen.draw.text(
            "Select Difficulty",
            center=(WIDTH // 2, HEIGHT // 2 - 150),
            color="white",
            fontsize=60,
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
            )
    elif game_active:
        # Gameplay UI (do NOT show high score here)
        screen.draw.filled_rect(main_box, "sky blue")
        screen.draw.filled_rect(timer_box, "sky blue")

        screen.draw.text(f"level {level}", (60, 60), color="black", fontsize=60)
        screen.draw.text(f"Lives: {lives}", (WIDTH - 200, 60), color="red", fontsize=48)

        for box in answer_boxes:
            screen.draw.filled_rect(box, "orange")

        screen.draw.text(
            str(time_left), center=timer_box.center, color="black", fontsize=72
        )
        screen.draw.text(
            current_questions[0],
            center=main_box.center,
            color="black",
            fontsize=48,
            align="center",
        )

        index = 1
        for box in answer_boxes:
            screen.draw.text(
                current_questions[index], center=box.center, color="black", fontsize=36
            )
            index += 1
    else:
        # End screen: show result and leaderboard
        screen.draw.text(
            game_over_message,
            center=(WIDTH // 2, HEIGHT // 2 - 120),
            color="green" if "New High Score" in game_over_message else "red",
            fontsize=72,
        )
        screen.draw.text(
            f"Your Score: {score}",
            center=(WIDTH // 2, HEIGHT // 2 - 40),
            color="white",
            fontsize=60,
        )

        # Leaderboard header
        screen.draw.text(
            "Leaderboard",
            center=(WIDTH // 2, HEIGHT // 2 + 40),
            color="gold",
            fontsize=48,
        )

        # Draw top 3 scores with proper font sizes
        ystart = HEIGHT // 2 + 100
        for i, (s, name) in enumerate(highscores):
            if i == 0:
                color = "gold"
                fontsize = 48
            elif i == 1:
                color = "silver"
                fontsize = 38
            elif i == 2:
                color = "orange"
                fontsize = 28
            else:
                color = "white"
                fontsize = 30
            screen.draw.text(
                f"{i + 1}. {name} - {s}",
                center=(WIDTH // 2, ystart + i * 50),  # Adjusted spacing
                color=color,
                fontsize=fontsize,
            )

        screen.draw.text(
            "Press Y to play again or N to quit",
            center=(WIDTH // 2, HEIGHT // 2 + 300),
            color="yellow",
            fontsize=40,
        )


# --- Advance to next level ---
def next_level():
    global level, time_left
    level += 1
    time_left = 10
    print("Advancing to level", level)


# --- Game over ---
def game_over():
    global game_active, time_left, score, player_name, highscores, game_over_message
    game_active = False
    time_left = 0

    # Clean up player name
    player_name_clean = player_name.strip() or "Player"

    # Reload highscores from file
    load_highscores()

    # Check if the player's score is a new high score
    if score > 0 and (len(highscores) < 3 or score > highscores[-1][0]):
        # Add the new high score
        highscores.append((score, player_name_clean))
        highscores.sort(key=lambda x: x[0], reverse=True)
        highscores = highscores[:3]  # Keep only the top 3
        save_highscores()

        # Set the game-over message for a new high score
        game_over_message = f"New High Score Achieved! Score: {score}"
        print(f"New High Score by {player_name_clean}: {score}")
    else:
        # Set the game-over message for a regular game over
        game_over_message = f"Game Over! Final Score: {score}"
        print(f"Game Over! Final Score: {score}")


# --- Correct answer ---
def correct_answer():
    global score, time_left, questions, current_questions, game_active
    score += 1
    if questions:
        current_questions = questions.pop(0)
        time_left = 10
        next_level()
    else:
        # No more questions
        game_active = False
        time_left = 0
        current_questions = [f"You Win! Final Score: {score}", "-", "-", "-", "-", 5]
        game_over()  # directly trigger game over handling for highscore update


# --- When the player clicks ---
def on_mouse_down(pos):
    global starting_page, name_input_active, difficulty_selected, game_active, difficulty, questions, current_questions

    if starting_page and start_button.collidepoint(pos):
        starting_page = False
        name_input_active = True

    elif not difficulty_selected:  # Difficulty selection screen
        difficulties = ["Easy", "Medium", "Hard"]
        for i, diff in enumerate(difficulties):
            box = Rect(WIDTH // 2 - 150, HEIGHT // 2 - 50 + i * 120, 300, 80)
            if box.collidepoint(pos):
                difficulty = diff
                difficulty_selected = True
                game_active = True
                time_left = 10  # same for all
                # Load question set based on difficulty
                if difficulty == "Easy":
                    questions = easy_questions.copy()
                elif difficulty == "Medium":
                    questions = medium_questions.copy()
                else:
                    questions = hard_questions.copy()
                random.shuffle(questions)
                current_questions = questions.pop(0)
                print(f"Difficulty selected: {difficulty}")
                break

    elif game_active:
        for i, box in enumerate(answer_boxes):
            if box.collidepoint(pos):
                if i + 1 == current_questions[5]:
                    correct_answer()
                else:
                    global lives
                    lives -= 1
                    if lives <= 0:
                        game_over()


# --- Restart or quit the game ---
def on_key_down(key):
    global game_active, score, level, time_left, current_questions, questions, lives
    global name_input_active, player_name, difficulty, difficulty_selected, starting_page

    # --- Handle name input ---
    if name_input_active:
        if key == keys.RETURN:
            if player_name.strip() == "":
                player_name = "Player"
            name_input_active = False
            # After name input, ask for difficulty
            difficulty_selected = False
            print("Select difficulty: E for Easy, M for Medium, H for Hard")
        elif key == keys.BACKSPACE:
            player_name = player_name[:-1]
        else:
            if len(key.name) == 1 and len(player_name) < 20:
                player_name += key.name

    # --- Handle difficulty selection (after name entered, before game starts) ---
    elif not game_active and not name_input_active:
        if not difficulty_selected:  # difficulty not chosen yet
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

        # --- Game Over Replay Logic ---
        elif key == keys.Y:
            # Reset game state
            score = 0
            level = 1
            lives = 3
            time_left = 10
            difficulty = None
            difficulty_selected = False
            name_input_active = True
            starting_page = True
            player_name = ""
            print("Enter your name:")
        elif key == keys.N:
            exit()
# --- Start the game after difficulty selection ---


def start_game():
    global game_active, current_questions
    game_active = True
    current_questions = questions.pop(0)
    print(f"Game started at {difficulty} difficulty.")


# --- Countdown timer ---
def update_time_left():
    global time_left
    # Only decrement the timer if the player has finished entering their name
    if not name_input_active and game_active:
        if time_left > 0:
            time_left -= 1
        else:
            game_over()


# --- Schedule timer update ---
schedule_interval(update_time_left, 1.0)

pgzrun.go()