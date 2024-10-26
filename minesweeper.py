import pygame
import random
import sys

"""
Game minesweeper implemented with pygame
"""

class Minesweeper:
    def __init__(self):
        """Initialize the Minesweeper game state."""
        self.tila = {
            "kentta": [],    # The minefield (with mines)
            "pelikentta": [] # The visible field shown to the player
        }
        self.ruudut_jaljella = [] # Remaining squares for mine placement
        self.pelitiedot = {
            "Miinat": 0,
            "Siirrot": 0,
            "koko": 0,
            "liput": 0
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

    def nollaus(self):
        """Reset the game state."""
        self.tila["kentta"] = []
        self.tila["pelikentta"] = []
        self.ruudut_jaljella.clear()
        self.pelitiedot["Miinat"] = 0
        self.pelitiedot["Siirrot"] = 0
        self.pelitiedot["koko"] = 0
        self.pelitiedot["liput"] = 0
        
        self.win = False
        self.game_lost = False

    def pelikentta_alustus(self, leveys=None, korkeus=None, miinojen_maara=10):
        """Initialize the minefield."""
        if leveys is None or korkeus is None:
            leveys = int(input("Anna kentän leveys: "))
            korkeus = int(input("Anna kentän korkeus: "))
        self.pelitiedot["koko"] = leveys * korkeus
        self.miinat(leveys, korkeus, miinojen_maara)

    def miinat(self, leveys, korkeus, miinojen_maara):
        """Place mines on the field."""
        if miinojen_maara >= korkeus * leveys:
            print("Miinoja on liikaa kentälle.")
        else:
            self.pelitiedot["Miinat"] = miinojen_maara
            kentta = [[" " for _ in range(leveys)] for _ in range(korkeus)]
            kentta_peli = [[" " for _ in range(leveys)] for _ in range(korkeus)]
            self.tila["kentta"] = kentta
            self.tila["pelikentta"] = kentta_peli

            self.ruudut_jaljella = [(x, y) for y in range(korkeus) for x in range(leveys)]
            self.miinoita(miinojen_maara)
            self.numerointi(self.tila["kentta"])
            

    def miinoita(self, miinojen_maara):
        """Add mines randomly to the field."""
        for _ in range(miinojen_maara):
            x, y = random.choice(self.ruudut_jaljella)
            self.tila["kentta"][y][x] = "x"
            self.ruudut_jaljella.remove((x, y))

    def numerointi(self, kentta):
        """Add numbers around mines to indicate danger levels."""
        for y, rivi in enumerate(kentta):
            for x, sarake in enumerate(rivi):
                if sarake != "x":
                    miinat = 0
                    for y1 in range(max(0, y - 1), min(y + 2, len(kentta))):
                        for x1 in range(max(0, x - 1), min(x + 2, len(rivi))):
                            if kentta[y1][x1] == "x":
                                miinat += 1
                    kentta[y][x] = str(miinat) if miinat > 0 else "0"

    def run_game(self, bot=None):
        """Main Pygame game loop with bot support."""
        leveys = len(self.tila["pelikentta"][0])  # Width of the grid
        korkeus = len(self.tila["pelikentta"])    # Height of the grid
        pygame.init()
        # Create a window with the appropriate size
        screen = pygame.display.set_mode((leveys * self.TILE_SIZE, korkeus * self.TILE_SIZE))
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
                            self.kasittele_hiiri(grid_x, grid_y, "vasen")
                        elif event.button == 3:  # Right click
                            self.kasittele_hiiri(grid_x, grid_y, "oikea")

                    # --- Update the display ---
                screen.fill((255, 255, 255))  # Clear the screen (white background)
                self.piirra_kentta(screen)    # Redraw the game grid

                # Check for win/loss conditions
                #self.check_win()
                if self.win or self.game_lost:
                    running = False  # End the game loop if the game is over

                pygame.display.flip()  # Update the entire display
                self.clock.tick(60)    # Limit the game to 60 frames per second

            
        else:
            bot.train(screen)
            print("All episodes completed")
            print(f"Training stats, won: {bot.won}, lost {bot.lost}")
            print("Testing Q-table")
            bot.test(screen)
            print(f"Testing stats, won {bot.won_test}, lost {bot.lost_test}")
            bot.visualize_q_values()
            print(bot.Q_table)
        pygame.quit()
        sys.exit()


    def piirra_kentta(self, screen):
        """Draw the game board."""
        for y, rivi in enumerate(self.tila["pelikentta"]):
            for x, ruutu in enumerate(rivi):
                tile = self.SPRITES["unrevealed"]
                if ruutu == "f":
                    tile = self.SPRITES["flag"]
                elif ruutu == "x":
                    tile = self.SPRITES["mine"]
                elif ruutu == "0":
                    tile = self.SPRITES["empty"]
                elif ruutu in self.SPRITES:
                    tile = self.SPRITES[ruutu]

                screen.blit(tile, (x * self.TILE_SIZE, y * self.TILE_SIZE))

    def kasittele_hiiri(self, ruutu_x, ruutu_y, painike):
        """Handle mouse clicks."""
        if ruutu_x < 0 or ruutu_x >= len(self.tila["pelikentta"][0]) or ruutu_y < 0 or ruutu_y >= len(self.tila["pelikentta"]):
            return  # Ignore clicks outside the grid
        ruutu = self.tila["pelikentta"][ruutu_y][ruutu_x]
        
        if painike == "vasen":
            if self.tila["kentta"][ruutu_y][ruutu_x] == "x":
                self.game_lost = True
                print("Hävisit pelin!")
                self.tila["pelikentta"][ruutu_y][ruutu_x] = "x"  # Reveal the mine
                
            elif ruutu == " ":
                self.pelitiedot["Siirrot"] += 1
                self.pelaa(ruutu_x, ruutu_y)  # Reveal the square
            self.check_win()
            
        elif painike == "oikea":
            if ruutu == " " and self.pelitiedot["liput"] < self.pelitiedot["Miinat"]:
                self.tila["pelikentta"][ruutu_y][ruutu_x] = "f"  # Place a flag
                self.pelitiedot["liput"] += 1
            elif ruutu == "f":
                self.tila["pelikentta"][ruutu_y][ruutu_x] = " "  # Remove the flag
                self.pelitiedot["liput"] -= 1
            self.check_win()


    def pelaa(self, ruutu_x, ruutu_y):
        """Reveal the clicked square using flood fill logic."""
        stack = [(ruutu_x, ruutu_y)]  # Use a stack to handle cells to be revealed
        while stack:
            x, y = stack.pop()
            if self.tila["pelikentta"][y][x] == " ":
                self.tila["pelikentta"][y][x] = self.tila["kentta"][y][x]  # Reveal the tile
                if self.tila["kentta"][y][x] == "0":  # If it's a zero, reveal neighbors
                    for new_y in range(max(0, y - 1), min(y + 2, len(self.tila["kentta"]))):
                        for new_x in range(max(0, x - 1), min(x + 2, len(self.tila["kentta"][0]))):
                            if self.tila["pelikentta"][new_y][new_x] == " ":
                                stack.append((new_x, new_y))  # Add the neighboring square to the stack
            
            # Check win condition after revealing tiles
        

    def check_win(self):
        """Check if the player has won the game."""
        ruutu_avaamaton = 0
        lippu = 0
        correct_flags = 0
        
        for y in range(len(self.tila["pelikentta"])):
            for x in range(len(self.tila["pelikentta"][y])):
                if self.tila["pelikentta"][y][x] == " ":
                    ruutu_avaamaton += 1  # Count unrevealed cells
                elif self.tila["pelikentta"][y][x] == "f":
                    lippu += 1  # Count flagged cells
                    if self.tila["kentta"][y][x] == "x":
                        correct_flags += 1  # Count correct flags

        # Win condition: all non-mine cells are revealed and all mines are flagged correctly
        if ruutu_avaamaton == 0 and lippu == self.pelitiedot["Miinat"] and correct_flags == lippu:
            print("Voitit pelin!")
            self.win = True



def main():
    peli = Minesweeper()
    peli.pelikentta_alustus(5,5,1)
    peli.run_game()

if __name__ == "__main__":
    main()