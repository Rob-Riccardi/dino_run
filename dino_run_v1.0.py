"""
Dino Run Clone with Webcam Motion Controls
==========================================
Controls:
- Stand up/Jump motion: Makes the dino jump
- Duck down motion: Makes the dino duck
- Press 'Q' to quit
- Press 'R' to restart after game over
- Press 'C' to toggle camera view
- Press 'D' to toggle debug mode
Requirements:
pip install pygame opencv-python mediapipe numpy
"""
import pygame
import cv2
import numpy as np
import random
import sys
# Try to import mediapipe for better pose detection
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("MediaPipe not found. Using basic motion detection.")
    print("For better tracking, install mediapipe: pip install mediapipe")
# Initialize Pygame
pygame.init()
# Game Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
FPS = 60
GROUND_HEIGHT = 50
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GREEN = (34, 139, 34)
SKY_BLUE = (135, 206, 235)
DARK_GREEN = (0, 100, 0)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dino Run - Webcam Motion Control")
clock = pygame.time.Clock()
# Fonts
font_large = pygame.font.Font(None, 74)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)
class Dino:
    """The player's dinosaur character."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.x = 80
        self.ground_y = SCREEN_HEIGHT - GROUND_HEIGHT - 70
        self.y = self.ground_y
        self.width = 44
        self.height = 60
        self.vel_y = 0
        self.is_jumping = False
        self.is_ducking = False
        self.jump_power = -16
        self.gravity = 0.9
        self.animation_frame = 0
        self.animation_timer = 0
    def jump(self):
        """Make the dino jump if not already jumping or ducking."""
        if not self.is_jumping and not self.is_ducking:
            self.is_jumping = True
            self.vel_y = self.jump_power
            
    def duck(self, ducking):
        """Make the dino duck or stand up."""
        if not self.is_jumping:
            self.is_ducking = ducking
            if ducking:
                self.y = self.ground_y + 35
            else:
                self.y = self.ground_y
    def update(self):
        """Update dino position and animation."""
        if self.is_jumping:
            self.vel_y += self.gravity
            self.y += self.vel_y
            
            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.is_jumping = False
                self.vel_y = 0
        
        self.animation_timer += 1
        if self.animation_timer >= 6:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 2
    def draw(self, surface):
        """Draw the dinosaur."""
        if self.is_ducking:
            # Ducking pose - horizontal body
            pygame.draw.ellipse(surface, DARK_GREEN, (self.x, self.y, 70, 35))
            # Head
            pygame.draw.ellipse(surface, DARK_GREEN, (self.x + 50, self.y - 8, 25, 22))
            # Eye
            pygame.draw.circle(surface, WHITE, (self.x + 65, self.y - 1), 5)
            pygame.draw.circle(surface, BLACK, (self.x + 67, self.y - 1), 3)
            # Legs
            leg_offset = 4 if self.animation_frame == 0 else -4
            pygame.draw.ellipse(surface, DARK_GREEN, (self.x + 15 + leg_offset, self.y + 28, 12, 18))
            pygame.draw.ellipse(surface, DARK_GREEN, (self.x + 40 - leg_offset, self.y + 28, 12, 18))
        else:
            # Standing pose
            # Body
            pygame.draw.ellipse(surface, DARK_GREEN, (self.x, self.y + 20, 40, 50))
            # Head
            pygame.draw.ellipse(surface, DARK_GREEN, (self.x + 5, self.y, 40, 30))
            # Eye
            pygame.draw.circle(surface, WHITE, (self.x + 35, self.y + 10), 6)
            pygame.draw.circle(surface, BLACK, (self.x + 37, self.y + 10), 3)
            # Mouth line
            pygame.draw.line(surface, BLACK, (self.x + 40, self.y + 18), (self.x + 45, self.y + 18), 2)
            # Tail
            pygame.draw.polygon(surface, DARK_GREEN, [
                (self.x + 5, self.y + 35),
                (self.x - 20, self.y + 45),
                (self.x + 5, self.y + 55)
            ])
            # Small arms
            pygame.draw.ellipse(surface, DARK_GREEN, (self.x + 32, self.y + 30, 15, 8))
            # Legs (animated when running)
            if not self.is_jumping:
                leg_offset = 6 if self.animation_frame == 0 else -6
                pygame.draw.ellipse(surface, DARK_GREEN, (self.x + 8 + leg_offset, self.y + 60, 14, 22))
                pygame.draw.ellipse(surface, DARK_GREEN, (self.x + 22 - leg_offset, self.y + 60, 14, 22))
            else:
                # Legs together when jumping
                pygame.draw.ellipse(surface, DARK_GREEN, (self.x + 10, self.y + 60, 14, 22))
                pygame.draw.ellipse(surface, DARK_GREEN, (self.x + 22, self.y + 60, 14, 22))
    def get_rect(self):
        """Get collision rectangle."""
        if self.is_ducking:
            return pygame.Rect(self.x, self.y, 70, 35)
        return pygame.Rect(self.x + 5, self.y + 5, 35, 75)
class Cactus:
    """Cactus obstacle."""
    
    def __init__(self, x, size='small'):
        self.x = x
        self.size = size
        self.passed = False
        
        if size == 'small':
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - 45
            self.width = 25
            self.height = 45
        else:  # large
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - 65
            self.width = 35
            self.height = 65
    def update(self, speed):
        self.x -= speed
    def draw(self, surface):
        if self.size == 'small':
            # Main stem
            pygame.draw.rect(surface, GREEN, (self.x + 7, self.y, 12, 45), border_radius=4)
            # Left arm
            pygame.draw.rect(surface, GREEN, (self.x, self.y + 15, 10, 8), border_radius=3)
            pygame.draw.rect(surface, GREEN, (self.x, self.y + 8, 6, 12), border_radius=3)
            # Right arm
            pygame.draw.rect(surface, GREEN, (self.x + 16, self.y + 20, 10, 8), border_radius=3)
            pygame.draw.rect(surface, GREEN, (self.x + 20, self.y + 12, 6, 14), border_radius=3)
        else:
            # Main stem
            pygame.draw.rect(surface, GREEN, (self.x + 10, self.y, 16, 65), border_radius=5)
            # Left arm
            pygame.draw.rect(surface, GREEN, (self.x, self.y + 20, 14, 10), border_radius=4)
            pygame.draw.rect(surface, GREEN, (self.x, self.y + 10, 8, 18), border_radius=4)
            # Right arm
            pygame.draw.rect(surface, GREEN, (self.x + 22, self.y + 30, 14, 10), border_radius=4)
            pygame.draw.rect(surface, GREEN, (self.x + 28, self.y + 18, 8, 20), border_radius=4)
    def get_rect(self):
        return pygame.Rect(self.x + 5, self.y + 5, self.width - 10, self.height - 5)
class Bird:
    """Flying bird obstacle."""
    
    def __init__(self, x):
        self.x = x
        # Different flight heights
        heights = [
            SCREEN_HEIGHT - GROUND_HEIGHT - 100,  # High - must duck
            SCREEN_HEIGHT - GROUND_HEIGHT - 70,   # Medium - can duck or jump
            SCREEN_HEIGHT - GROUND_HEIGHT - 140,  # Very high - just run
        ]
        self.y = random.choice(heights)
        self.width = 50
        self.height = 35
        self.passed = False
        self.animation_frame = 0
        self.animation_timer = 0
    def update(self, speed):
        self.x -= speed + 1  # Birds move slightly faster
        self.animation_timer += 1
        if self.animation_timer >= 8:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 2
    def draw(self, surface):
        # Body
        pygame.draw.ellipse(surface, GRAY, (self.x + 10, self.y + 12, 35, 18))
        # Head
        pygame.draw.ellipse(surface, GRAY, (self.x + 38, self.y + 10, 18, 16))
        # Beak
        pygame.draw.polygon(surface, (255, 165, 0), [
            (self.x + 52, self.y + 16),
            (self.x + 62, self.y + 20),
            (self.x + 52, self.y + 22)
        ])
        # Eye
        pygame.draw.circle(surface, BLACK, (self.x + 48, self.y + 16), 3)
        # Wings (animated)
        if self.animation_frame == 0:
            # Wings up
            pygame.draw.ellipse(surface, GRAY, (self.x + 5, self.y - 8, 35, 22))
        else:
            # Wings down
            pygame.draw.ellipse(surface, GRAY, (self.x + 5, self.y + 20, 35, 22))
    def get_rect(self):
        return pygame.Rect(self.x + 12, self.y + 10, 40, 22)
class Cloud:
    """Background cloud decoration."""
    
    def __init__(self, x=None):
        self.x = x if x is not None else SCREEN_WIDTH + random.randint(50, 200)
        self.y = random.randint(30, 100)
        self.speed = random.uniform(0.3, 1.0)
        self.size = random.uniform(0.8, 1.2)
    def update(self):
        self.x -= self.speed
    def draw(self, surface):
        s = self.size
        pygame.draw.ellipse(surface, WHITE, (self.x, self.y, int(50*s), int(25*s)))
        pygame.draw.ellipse(surface, WHITE, (self.x + int(15*s), self.y - int(12*s), int(40*s), int(30*s)))
        pygame.draw.ellipse(surface, WHITE, (self.x + int(35*s), self.y - int(5*s), int(45*s), int(28*s)))
class MotionDetector:
    """Handles webcam input and motion detection."""
    
    def __init__(self):
        print("Initializing camera...")
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            print("ERROR: Could not open camera!")
            self.cap = None
            return
            
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Camera initialized: {self.frame_width}x{self.frame_height}")
        
        # Motion detection variables
        self.baseline_y = None
        self.calibration_frames = 45
        self.frame_count = 0
        self.calibration_values = []
        self.is_calibrated = False
        
        # Smoothing
        self.current_y = None
        self.smooth_alpha = 0.4
        
        # Sensitivity settings (percentage of frame height)
        self.jump_threshold = 0.06   # 6% up from baseline = jump
        self.duck_threshold = 0.08   # 8% down from baseline = duck
        
        # Current frame for display
        self.display_frame = None
        self.debug_mode = True
        
        # State tracking to prevent repeated triggers
        self.last_action = 'stand'
        self.action_cooldown = 0
        
        # MediaPipe setup if available
        if MEDIAPIPE_AVAILABLE:
            print("Using MediaPipe for pose detection")
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
                model_complexity=0
            )
        else:
            print("Using basic motion detection")
            self.pose = None
            # Background subtractor for basic detection
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                history=60, varThreshold=40, detectShadows=False
            )
    def get_pose_position(self, frame):
        """Get vertical position using MediaPipe pose detection."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # Get shoulder positions (more stable than nose)
            left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
            
            # Use average of shoulders
            if left_shoulder.visibility > 0.5 and right_shoulder.visibility > 0.5:
                avg_y = (left_shoulder.y + right_shoulder.y) / 2
                avg_x = (left_shoulder.x + right_shoulder.x) / 2
                
                # Convert to pixel coordinates
                pixel_y = int(avg_y * self.frame_height)
                pixel_x = int(avg_x * self.frame_width)
                
                return pixel_y, (pixel_x, pixel_y), results.pose_landmarks
        
        return None, None, None
    def get_basic_position(self, frame):
        """Get vertical position using basic motion detection."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(gray)
        
        # Clean up mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get largest contour
            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)
            
            if area > 3000:  # Minimum area threshold
                x, y, w, h = cv2.boundingRect(largest)
                
                # Track the top-center of the bounding box (head area)
                center_x = x + w // 2
                top_y = y + h // 4  # Upper portion
                
                return top_y, (center_x, top_y), (x, y, w, h)
        
        return None, None, None
    def get_motion(self):
        """Process webcam frame and detect motion."""
        if self.cap is None:
            return 'no_camera', None, None
        
        ret, frame = self.cap.read()
        if not ret:
            return 'no_frame', None, None
        
        # Mirror the frame
        frame = cv2.flip(frame, 1)
        self.display_frame = frame.copy()
        
        # Get position based on available method
        if MEDIAPIPE_AVAILABLE and self.pose:
            y_pos, center, pose_data = self.get_pose_position(frame)
            
            # Draw pose landmarks if debug mode
            if self.debug_mode and pose_data:
                mp.solutions.drawing_utils.draw_landmarks(
                    self.display_frame, pose_data, 
                    self.mp_pose.POSE_CONNECTIONS,
                    mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp.solutions.drawing_utils.DrawingSpec(color=(0, 0, 255), thickness=2)
                )
        else:
            y_pos, center, bbox = self.get_basic_position(frame)
            
            # Draw bounding box if debug mode
            if self.debug_mode and bbox:
                x, y, w, h = bbox
                cv2.rectangle(self.display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        if y_pos is None:
            cv2.putText(self.display_frame, "No person detected!", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            if self.frame_count < self.calibration_frames:
                return 'calibrating', self.frame_count / self.calibration_frames, self.display_frame
            return 'stand', None, self.display_frame
        
        # Apply smoothing
        if self.current_y is None:
            self.current_y = y_pos
        else:
            self.current_y = self.smooth_alpha * y_pos + (1 - self.smooth_alpha) * self.current_y
        
        # Draw tracking point
        if center:
            cv2.circle(self.display_frame, (center[0], int(self.current_y)), 10, (0, 255, 255), -1)
        
        # Calibration phase
        if self.frame_count < self.calibration_frames:
            self.calibration_values.append(self.current_y)
            self.frame_count += 1
            
            progress = self.frame_count / self.calibration_frames
            cv2.putText(self.display_frame, f"Calibrating: {int(progress * 100)}%", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            cv2.putText(self.display_frame, "Stand still!", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            return 'calibrating', progress, self.display_frame
        
        # Set baseline after calibration
        if not self.is_calibrated:
            # Use median for robustness
            self.baseline_y = np.median(self.calibration_values)
            self.is_calibrated = True
            print(f"Calibration complete! Baseline Y: {self.baseline_y:.1f}")
        
        # Calculate movement relative to baseline
        y_offset = (self.current_y - self.baseline_y) / self.frame_height
        
        # Draw debug visualization
        if self.debug_mode:
            # Baseline (blue)
            cv2.line(self.display_frame, (0, int(self.baseline_y)), 
                    (self.frame_width, int(self.baseline_y)), (255, 100, 0), 2)
            
            # Current position line (green)
            cv2.line(self.display_frame, (0, int(self.current_y)), 
                    (self.frame_width, int(self.current_y)), (0, 255, 0), 2)
            
            # Jump threshold line
            jump_y = int(self.baseline_y - self.jump_threshold * self.frame_height)
            cv2.line(self.display_frame, (0, jump_y), (self.frame_width, jump_y), (0, 255, 0), 1)
            cv2.putText(self.display_frame, "JUMP", (5, jump_y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Duck threshold line
            duck_y = int(self.baseline_y + self.duck_threshold * self.frame_height)
            cv2.line(self.display_frame, (0, duck_y), (self.frame_width, duck_y), (0, 0, 255), 1)
            cv2.putText(self.display_frame, "DUCK", (5, duck_y + 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            # Show offset percentage
            cv2.putText(self.display_frame, f"Offset: {y_offset*100:.1f}%", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Cooldown for actions
        if self.action_cooldown > 0:
            self.action_cooldown -= 1
        
        # Detect action
        action = 'stand'
        
        # Jump detection (y goes up = negative offset)
        if y_offset < -self.jump_threshold:
            action = 'jump'
            cv2.putText(self.display_frame, "JUMP!", (self.frame_width // 2 - 60, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
        # Duck detection (y goes down = positive offset)
        elif y_offset > self.duck_threshold:
            action = 'duck'
            cv2.putText(self.display_frame, "DUCK!", (self.frame_width // 2 - 60, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
        else:
            cv2.putText(self.display_frame, "STANDING", (self.frame_width // 2 - 80, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 2)
        
        return action, None, self.display_frame
    def reset_calibration(self):
        """Reset the calibration state."""
        self.baseline_y = None
        self.frame_count = 0
        self.calibration_values = []
        self.is_calibrated = False
        self.current_y = None
        self.last_action = 'stand'
        
        if not MEDIAPIPE_AVAILABLE:
            self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
                history=60, varThreshold=40, detectShadows=False
            )
    def release(self):
        """Release camera resources."""
        if self.cap:
            self.cap.release()
        if MEDIAPIPE_AVAILABLE and self.pose:
            self.pose.close()
class Game:
    """Main game class."""
    
    def __init__(self):
        self.dino = Dino()
        self.obstacles = []
        self.clouds = [Cloud(random.randint(0, SCREEN_WIDTH)) for _ in range(4)]
        self.motion_detector = MotionDetector()
        
        self.score = 0
        self.high_score = 0
        self.game_speed = 7
        self.game_over = False
        self.show_camera = True
        self.spawn_timer = 0
        self.ground_offset = 0
    def reset(self):
        """Reset game state."""
        self.dino.reset()
        self.obstacles = []
        self.score = 0
        self.game_speed = 7
        self.game_over = False
        self.spawn_timer = 0
        self.motion_detector.reset_calibration()
    def spawn_obstacle(self):
        """Spawn a new obstacle."""
        # Don't spawn if last obstacle is too close
        if self.obstacles and self.obstacles[-1].x > SCREEN_WIDTH - 350:
            return
        
        obstacle_type = random.choices(
            ['cactus_small', 'cactus_large', 'bird'],
            weights=[40, 35, 25]
        )[0]
        
        if obstacle_type == 'cactus_small':
            self.obstacles.append(Cactus(SCREEN_WIDTH + 50, 'small'))
        elif obstacle_type == 'cactus_large':
            self.obstacles.append(Cactus(SCREEN_WIDTH + 50, 'large'))
        else:
            self.obstacles.append(Bird(SCREEN_WIDTH + 50))
    def update(self):
        """Update game state."""
        self.dino.update()
        
        # Update obstacles
        for obstacle in self.obstacles:
            obstacle.update(self.game_speed)
            
            # Check collision
            if self.dino.get_rect().colliderect(obstacle.get_rect()):
                self.game_over = True
                if self.score > self.high_score:
                    self.high_score = self.score
            
            # Score when passing obstacle
            if not obstacle.passed and obstacle.x + obstacle.width < self.dino.x:
                obstacle.passed = True
                self.score += 10
        
        # Remove off-screen obstacles
        self.obstacles = [obs for obs in self.obstacles if obs.x > -100]
        
        # Spawn new obstacles
        self.spawn_timer += 1
        if self.spawn_timer > random.randint(50, 100):
            self.spawn_timer = 0
            self.spawn_obstacle()
        
        # Update clouds
        for cloud in self.clouds:
            cloud.update()
        self.clouds = [c for c in self.clouds if c.x > -100]
        if len(self.clouds) < 4 and random.random() < 0.01:
            self.clouds.append(Cloud())
        
        # Increase speed over time
        self.game_speed = min(14, 7 + self.score / 150)
        
        # Update ground scroll
        self.ground_offset = (self.ground_offset + self.game_speed) % 20
    def draw(self):
        """Draw all game elements."""
        # Sky gradient
        screen.fill(SKY_BLUE)
        
        # Clouds
        for cloud in self.clouds:
            cloud.draw(screen)
        
        # Ground
        pygame.draw.rect(screen, BROWN, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
        pygame.draw.rect(screen, (120, 80, 40), (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, 3))
        
        # Ground texture lines
        for i in range(-20, SCREEN_WIDTH + 20, 20):
            x = i - self.ground_offset
            pygame.draw.line(screen, (100, 60, 30), 
                           (x, SCREEN_HEIGHT - GROUND_HEIGHT + 15),
                           (x + 10, SCREEN_HEIGHT - GROUND_HEIGHT + 15), 2)
        
        # Obstacles
        for obstacle in self.obstacles:
            obstacle.draw(screen)
        
        # Dino
        self.dino.draw(screen)
        
        # Score display
        score_text = font_medium.render(f"Score: {self.score}", True, BLACK)
        screen.blit(score_text, (SCREEN_WIDTH - 220, 15))
        
        high_text = font_small.render(f"Best: {self.high_score}", True, GRAY)
        screen.blit(high_text, (SCREEN_WIDTH - 220, 55))
        
        # Camera feed (smaller in corner)
        if self.show_camera and self.motion_detector.display_frame is not None:
            cam_frame = cv2.cvtColor(self.motion_detector.display_frame, cv2.COLOR_BGR2RGB)
            cam_frame = cv2.resize(cam_frame, (180, 135))
            cam_frame = np.rot90(cam_frame)
            cam_surface = pygame.surfarray.make_surface(cam_frame)
            screen.blit(cam_surface, (8, 8))
            pygame.draw.rect(screen, WHITE, (8, 8, 180, 135), 2)
    def draw_calibration_overlay(self, progress):
        """Draw calibration screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        title = font_large.render("CALIBRATING", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
        
        instruction = font_small.render("Stand still in front of your camera", True, WHITE)
        screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
        
        # Progress bar
        bar_width = 350
        bar_height = 25
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = SCREEN_HEIGHT // 2 + 30
        
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        pygame.draw.rect(screen, GREEN, (bar_x + 3, bar_y + 3, int((bar_width - 6) * progress), bar_height - 6))
        
        percent_text = font_small.render(f"{int(progress * 100)}%", True, WHITE)
        screen.blit(percent_text, (SCREEN_WIDTH // 2 - percent_text.get_width() // 2, bar_y + 40))
    def draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        title = font_large.render("GAME OVER", True, RED)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
        
        score_text = font_medium.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 10))
        
        if self.score >= self.high_score and self.score > 0:
            new_best = font_small.render("NEW HIGH SCORE!", True, YELLOW)
            screen.blit(new_best, (SCREEN_WIDTH // 2 - new_best.get_width() // 2, SCREEN_HEIGHT // 2 + 30))
        
        restart_text = font_small.render("Press R to restart | Q to quit", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 70))
    def run(self):
        """Main game loop."""
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset()
                    elif event.key == pygame.K_c:
                        self.show_camera = not self.show_camera
                    elif event.key == pygame.K_d:
                        self.motion_detector.debug_mode = not self.motion_detector.debug_mode
                    # Keyboard backup controls
                    elif event.key in (pygame.K_SPACE, pygame.K_UP):
                        if not self.game_over:
                            self.dino.jump()
                    elif event.key == pygame.K_DOWN:
                        if not self.game_over:
                            self.dino.duck(True)
                            
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        self.dino.duck(False)
            
            # Get motion from webcam
            motion, progress, _ = self.motion_detector.get_motion()
            
            # Process motion controls
            if not self.game_over and motion != 'calibrating':
                if motion == 'jump':
                    self.dino.jump()
                elif motion == 'duck':
                    self.dino.duck(True)
                elif motion == 'stand':
                    self.dino.duck(False)
                
                # Update game
                self.update()
            
            # Draw everything
            self.draw()
            
            # Draw overlays
            if motion == 'calibrating' and progress is not None:
                self.draw_calibration_overlay(progress)
            elif self.game_over:
                self.draw_game_over()
            
            # Controls help
            help_text = font_small.render("C: Camera | D: Debug | Arrow keys: Backup controls", True, GRAY)
            screen.blit(help_text, (10, SCREEN_HEIGHT - 30))
            
            pygame.display.flip()
            clock.tick(FPS)
        
        # Cleanup
        self.motion_detector.release()
        pygame.quit()
        cv2.destroyAllWindows()
def main():
    print("=" * 55)
    print("   DINO RUN - Webcam Motion Control Game")
    print("=" * 55)
    print()
    print("CONTROLS:")
    print("  • Jump up in real life → Dino jumps")
    print("  • Duck/crouch down → Dino ducks")
    print("  • Space/Up Arrow → Jump (keyboard backup)")
    print("  • Down Arrow → Duck (keyboard backup)")
    print("  • C → Toggle camera view")
    print("  • D → Toggle debug overlay")
    print("  • R → Restart after game over")
    print("  • Q → Quit")
    print()
    print("TIPS:")
    print("  • Stand about 5-6 feet from camera")
    print("  • Make sure your upper body is visible")
    print("  • Good lighting helps detection")
    print("  • Stand still during calibration")
    print()
    
    if MEDIAPIPE_AVAILABLE:
        print("✓ MediaPipe detected - using advanced pose tracking")
    else:
        print("! MediaPipe not found - using basic motion detection")
        print("  For better results: pip install mediapipe")
    
    print()
    print("=" * 55)
    print("Starting game...")
    print("=" * 55)
    print()
    
    game = Game()
    game.run()
    sys.exit()
if __name__ == "__main__":
    main()