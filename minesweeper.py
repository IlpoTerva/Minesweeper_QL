import pygame
import random
import sys

"""
Game minesweeper implemented with pygame
"""

class Minesweeper:
    def __init__(self):
        """Initialize the Minesweeper game state."""
        self.state = {
            "minefield": [],    # The minefield (with mines)
            "visible_field": [] # The visible field shown to the player
        }
        self.remaining_cells = []  # Remaining squares for mine placement
        self.gameInfo = {
            "Mines": 0,
            "Moves": 0,
            "Size": 0,
            "Flags": 0
        }
        self.game_lost = False
        self.win = False

        # Pygame setup
        self.clock = pygame.time.Clock()
        self.TILE_SIZE = 40
        self.SPRITES = {}

        # Load images
        self.load_sprites()

    def load_sprites(self):
        """Load images for the game from the 'spritet' folder."""
        self.SPRITES["empty"] = pygame.image.load("spritet/ruutu_tyhja.png")
        self.SPRITES["mine"] = pygame.image.load("spritet/ruutu_miina.png")
        self.SPRITES["flag"] = pygame.image.load("spritet/ruutu_lippu.png")
        for i in range(1, 9):  # Load numbered tiles
            self.SPRITES[str(i)] = pygame.image.load(f"spritet/ruutu_{i}.png")
        self.SPRITES["unrevealed"] = pygame.image.load("spritet/ruutu_selka.png")

    def reset_game(self):
        """Reset the game state."""
        self.state["minefield"] = []
        self.state["visible_field"] = []
        self.remaining_cells.clear()
        self.gameInfo["Mines"] = 0
        self.gameInfo["Moves"] = 0
        self.gameInfo["Size"] = 0
        self.gameInfo["Flags"] = 0

        self.win = False
        self.game_lost = False

    def initialize_field(self, width=None, height=None, num_mines=10):
        """Initialize the minefield."""
        if width is None or height is None:
            width = int(input("Enter field width: "))
            height = int(input("Enter field height: "))
        self.gameInfo["Size"] = width * height
        self.place_mines(width, height, num_mines)

    def place_mines(self, width, height, num_mines):
        """Place mines on the field."""
        if num_mines >= height * width:
            print("Too many mines for the field.")
        else:
            self.gameInfo["Mines"] = num_mines
            field = [[" " for _ in range(width)] for _ in range(height)]
            visible_field = [[" " for _ in range(width)] for _ in range(height)]
            self.state["minefield"] = field
            self.state["visible_field"] = visible_field

            self.remaining_cells = [(x, y) for y in range(height) for x in range(width)]
            self.add_mines(num_mines)
            self.add_numbers(self.state["minefield"])

    def add_mines(self, num_mines):
        """Add mines randomly to the field."""
        for _ in range(num_mines):
            x, y = random.choice(self.remaining_cells)
            self.state["minefield"][y][x] = "x"
            self.remaining_cells.remove((x, y))

    def add_numbers(self, field):
        """Add numbers around mines to indicate danger levels."""
        for y, row in enumerate(field):
            for x, cell in enumerate(row):
                if cell != "x":
                    mines = 0
                    for y1 in range(max(0, y - 1), min(y + 2, len(field))):
                        for x1 in range(max(0, x - 1), min(x + 2, len(row))):
                            if field[y1][x1] == "x":
                                mines += 1
                    field[y][x] = str(mines) if mines > 0 else "0"

    def run_game(self, bot=None):
        """Main Pygame game loop with bot support."""
        width = len(self.state["visible_field"][0])  # Width of the grid
        height = len(self.state["visible_field"])    # Height of the grid
        pygame.init()
        # Create a window with the appropriate size
        screen = pygame.display.set_mode((width * self.TILE_SIZE, height * self.TILE_SIZE))
        pygame.display.set_caption("Minesweeper")

        if not bot:
            running = True
            while running:
                # Handle user input (quit or player interaction)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = pygame.mouse.get_pos()
                        grid_x = x // self.TILE_SIZE
                        grid_y = y // self.TILE_SIZE
                        if event.button == 1:  # Left click
                            self.handle_click(grid_x, grid_y, "left")
                        elif event.button == 3:  # Right click
                            self.handle_click(grid_x, grid_y, "right")

                # --- Update the display ---
                screen.fill((255, 255, 255))  # Clear the screen (white background)
                self.draw_field(screen)       # Redraw the game grid

                # Check for win/loss conditions
                if self.win or self.game_lost:
                    running = False  # End the game loop if the game is over

                pygame.display.flip()  # Update the entire display
                self.clock.tick(60)    # Limit the game to 60 frames per second

        else:
            bot.train(screen)
            print("All episodes completed")
            print(f"Training stats, won: {bot.won}, lost {bot.lost}")
            print("Testing model")
            bot.test(screen)
            print(f"Testing stats, won {bot.won_test}, lost {bot.lost_test}")

        pygame.quit()
        sys.exit()

    def draw_field(self, screen):
        """Draw the game board."""
        for y, row in enumerate(self.state["visible_field"]):
            for x, cell in enumerate(row):
                tile = self.SPRITES["unrevealed"]
                if cell == "f":
                    tile = self.SPRITES["flag"]
                elif cell == "x":
                    tile = self.SPRITES["mine"]
                elif cell == "0":
                    tile = self.SPRITES["empty"]
                elif cell in self.SPRITES:
                    tile = self.SPRITES[cell]

                screen.blit(tile, (x * self.TILE_SIZE, y * self.TILE_SIZE))

    def handle_click(self, grid_x, grid_y, button):
        """Handle mouse clicks."""
        if grid_x < 0 or grid_x >= len(self.state["visible_field"][0]) or grid_y < 0 or grid_y >= len(self.state["visible_field"]):
            return  # Ignore clicks outside the grid
        cell = self.state["visible_field"][grid_y][grid_x]

        if button == "left":
            if self.state["minefield"][grid_y][grid_x] == "x":
                self.game_lost = True
                print("You lost!")
                self.state["visible_field"][grid_y][grid_x] = "x"  # Reveal the mine
            elif cell == " ":
                self.gameInfo["Moves"] += 1
                self.reveal(grid_x, grid_y)  # Reveal the square
            self.check_win()

        elif button == "right":
            if cell == " " and self.gameInfo["Flags"] < self.gameInfo["Mines"]:
                self.state["visible_field"][grid_y][grid_x] = "f"  # Place a flag
                self.gameInfo["Flags"] += 1
            elif cell == "f":
                self.state["visible_field"][grid_y][grid_x] = " "  # Remove the flag
                self.gameInfo["Flags"] -= 1
            self.check_win()

    def reveal(self, grid_x, grid_y):
        """Reveal the clicked square using flood fill logic."""
        stack = [(grid_x, grid_y)]  # Use a stack to handle cells to be revealed
        while stack:
            x, y = stack.pop()
            if self.state["visible_field"][y][x] == " ":
                self.state["visible_field"][y][x] = self.state["minefield"][y][x]  # Reveal the tile
                if self.state["minefield"][y][x] == "0":  # If it's a zero, reveal neighbors
                    for new_y in range(max(0, y - 1), min(y + 2, len(self.state["minefield"]))):
                        for new_x in range(max(0, x - 1), min(x + 2, len(self.state["minefield"][0]))):
                            if self.state["visible_field"][new_y][new_x] == " ":
                                stack.append((new_x, new_y))  # Add the neighboring square to the stack

    def check_win(self):
        """Check if the player has won the game."""
        unrevealed_cells = 0
        flags = 0
        correct_flags = 0

        for y in range(len(self.state["visible_field"])):
            for x in range(len(self.state["visible_field"][y])):
                if self.state["visible_field"][y][x] == " ":
                    unrevealed_cells += 1  # Count unrevealed cells
                elif self.state["visible_field"][y][x] == "f":
                    flags += 1  # Count flagged cells
                    if self.state["minefield"][y][x] == "x":
                        correct_flags += 1  # Count correct flags

        # Win condition: all non-mine cells are revealed and all mines are flagged correctly
        if unrevealed_cells == 0 and flags == self.gameInfo["Mines"] and correct_flags == flags:
            print("You won!")
            self.win = True


def main():
    game = Minesweeper()
    game.initialize_field(5, 5, 1)
    game.run_game()

if __name__ == "__main__":
    main()
