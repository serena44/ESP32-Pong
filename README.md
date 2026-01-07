# Embedded Pong Game - ESP32 & Python
A simple pong style game where the player controls the paddle using ESP32 microcontroller and competes against a computer opponent. The game uses a Flask server to store and display post-game stats. 

## Tech Stack
- Python
- ESP32 Microcontroller
- Arduino
- Flask
- JSON

## Features 
- ESP32-based hardware input for player control
- Computer-controlled opponent
- Flask server to store game play data
- Post- game stats page displaying score, paddle hit counts and gam duration

## How It Works
1. The ESP32 send player input to the Python gam
2. Gameplay data is sent to Flask server
3. The server store data into a JSON file
4. After game ends, the URL can be opened to show game statistics

## Future Improvements
- Multiplayer support
- Enhanced UI for game menu and statistics
