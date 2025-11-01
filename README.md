🎮 Minesweeper Game 🎮


📌 Overview:
    A simple Pygame-based Minesweeper game written in Python. 
    Players can customize the board size and mine count, move a player cursor around the grid to reveal cells, and track their win/loss records which are saved automatically in a CSV file.


📌 Description:
    Features include:
        • Interactive graphical board using Pygame
        • Move the player cursor with arrow keys
        • Step on a cell to reveal it; mines end the game instantly
        • Auto-reveal for empty cells
        • Custom board size and mine count
        • Player records tracking (total games, wins, losses) saved in CSV
        • Main menu for Play, Rules, Records, and Exit


📌 Control:
    • Arrow keys → Move the player
    • Step on a cell → Reveal it automatically
    • ESC → Return to menu or exit
    • Mouse click → Select menu options or game setup inputs


📌 Dependencies:
    • Python 3.8 or higher (recommended Python 3.10+)
    • Operating System: Windows, macOS, or Linux
    • Required library: numpy, pygame

    Install dependencies: 
        pip install numpy
        pip install pygame


📌 Executing Program:
    Run the game: 
        python minesweeper.py

    Step-by-step:
        • Enter your player name.
        • Choose from the main menu:
            1. Play → Start a new game
            2. Rules → View game rules
            3. Records → View your win/loss record
            4. Exit → Save records and exit

    When playing:
        • Input the number of Rows, Cols, and Mines for your board.
        • Move the player cursor with arrow keys and step on cells to reveal them.
        • Reveal all safe cells to win the game. Stepping on a mine ends the game immediately.


📌 Minesweeper Rules:
    • Step onto a mine → Game over
    • Step onto a safe cell → Reveals number of nearby mines
    • Win by revealing all non-mine cells
    • Player records are saved automatically after each game


📌 CSV Records:
    Player statistics are saved automatically in minesweeper_records.csv.

    Columns:
        Player	Total	Win  Lose

    • Player: Player name
    • Total: Total games played
    • Win: Number of games won
    • Lose: Number of games lost


📌 License:
    This project is open-source and free to use.

    
