
This code is a Python-based implementation of the classic "Dino Run" (Chrome Dinosaur) game, but with a unique twist: it uses your webcam and computer vision to control the character.

Instead of just pressing keys, you physically jump and duck in front of your camera to make the dinosaur do the same.

🦖 Dino Run: Webcam Motion Control
A Python game that turns your body into the controller. Using OpenCV and MediaPipe, the game tracks your vertical movement in real-time to translate your physical actions into gameplay.

🛠️ How It Works
The game utilizes your webcam to establish a "baseline" position for your body.

Pose Tracking: It identifies key landmarks on your body (like your shoulders).

Calibration: During the first few seconds, it calculates your "Standing" height.

Motion Mapping: * If your shoulders move above a certain threshold, the game triggers a Jump.

If your shoulders move below a certain threshold, the game triggers a Duck.

Game Engine: Built with Pygame, it handles the physics, obstacle spawning (cacti and birds), and score tracking.

🚀 Getting Started
1. Requirements
You will need a webcam and Python installed on your system.

2. Install Dependencies
Run the following command in your terminal to install the necessary libraries:

Bash
pip install pygame opencv-python mediapipe numpy
3. Running the Game
Save the code as dino_run.py and run it:

Bash
python dino_run.py
🎮 How to Play
Physical Controls
Jump: Physically jump or lift your torso higher than your resting position.

Duck: Squat or lower your torso.

Stand: Return to your normal height to run normally.

Keyboard Shortcuts
Key	Action
Space / Up	Backup Jump
Down	Backup Duck
C	Toggle Webcam View (On/Off)
D	Toggle Debug Mode (Shows tracking lines)
R	Restart (After Game Over)
Q	Quit Game
💡 Pro-Tips for Best Performance
Distance: Stand about 5–8 feet away from the camera so your upper body is clearly visible.

Lighting: Ensure the room is well-lit. Shadows or a very dark background can confuse the motion tracking.

Calibration is Key: When the game starts, it will say "CALIBRATING". Stand perfectly still during this phase so it can accurately learn your height.

Debug Mode: If the dino isn't responding correctly, press 'D'. You will see a blue line (your baseline) and green/red lines (the jump/duck triggers). Adjust your position so your "tracking dot" sits near the blue line when standing normally.

🛠️ Troubleshooting
No Camera Found: Ensure no other apps (like Zoom or Teams) are using your webcam.

MediaPipe Error: If the game feels laggy, ensure you have the latest version of mediapipe installed. If it's not found, the game will automatically switch to a "Basic Motion" mode which is less accurate but faster on older computers.
