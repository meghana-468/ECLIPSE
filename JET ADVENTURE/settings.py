"""Central configuration for Level 2. Adjust these values to tune the game."""
WHITE = (255, 255, 255)
WIDTH, HEIGHT = 1100, 700                 # Window size
FPS = 60                                  # Target frames per second
GROUND_Y = 555                            # Top of the Moon surface
WORLD_LENGTH = 14500                      # World distance before the Mars rocket
PLAYER_START_X = 140
PLAYER_SPEED = 300.0                      # Base horizontal speed (pixels/second)
MAX_SPEED_BONUS = 125.0                   # Maximum speed increase over time
GRAVITY = 1550.0                          # Downward acceleration
JUMP_FORCE = 610.0                        # Initial upward velocity
OXYGEN_MAX = 100.0                        # Oxygen units
OXYGEN_DRAIN = 3.15                       # Oxygen units per second
TANK_REFILL = 24.0                        # Oxygen gained per tank
OBSTACLE_DAMAGE = 28.0                    # Oxygen lost on collision
OBSTACLE_FIRST_MIN, OBSTACLE_FIRST_MAX = 360, 560
OBSTACLE_LATER_MIN, OBSTACLE_LATER_MAX = 235, 390
PART_SPACING_MIN, PART_SPACING_MAX = 850, 1450
TANK_SPACING_MIN, TANK_SPACING_MAX = 330, 510
PLAYER_WIDTH, PLAYER_HEIGHT = 38, 68
PART_NAMES = ("engine", "fuel tank", "wing", "nose cone", "control panel")
# Palette
BLACK = (5, 7, 16); WHITE = (242, 245, 250); CYAN = (75, 220, 255)
GOLD = (255, 211, 95); RED = (255, 65, 75); GREEN = (95, 235, 145)
DARK = (18, 24, 38); PANEL = (18, 29, 48); MOON = (145, 147, 157)
MOON_LIGHT = (185, 187, 196); MOON_DARK = (85, 87, 98)
