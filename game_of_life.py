import pygame, sys, time

WWIDTH, WHEIGHT = 1000, 1000
TS = 20
ROW, COL = WHEIGHT // TS, WWIDTH // TS

T_FPS = 1200
DT_INITIAL = 0

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (60, 60, 60)

class Cell:
    def __init__(self, game, j, i) -> None:
        self.game = game
        self.j = j
        self.i = i

        self.x = self.j * TS
        self.y = self.i * TS

        self.rect = pygame.Rect(self.x, self.y, TS, TS)

        self.TOPNEIGHBOUR = None
        self.BOTTOMNEIGHBOUR = None
        self.LEFTNEIGHBOUR = None
        self.RIGHTNEIGHBOUR = None
        self.TOPLEFTNEIGHBOUR = None
        self.TOPRIGHTNEIGHBOUR = None
        self.BOTTOMLEFTNEIGHBOUR = None
        self.BOTTOMRIGHTNEIGHBOUR = None

        self.alive = False
        self.next_cell_state = False
        self.neighbours = []

    def update_state(self):
        self.alive = self.next_cell_state

    def get_neighbours(self):

        if self.i > 0: # top neighbour
            self.TOPNEIGHBOUR = self.game.cells[self.i - 1][self.j]
        if self.i < ROW - 1: # bottom neighbour
            self.BOTTOMNEIGHBOUR = self.game.cells[self.i + 1][self.j]
        if self.j > 0: # left neighbour
            self.LEFTNEIGHBOUR = self.game.cells[self.i][self.j - 1]
        if self.j < COL - 1: # right neighbour
            self.RIGHTNEIGHBOUR = self.game.cells[self.i][self.j + 1]

        if self.i > 0 and self.j > 0: # topleft neighbour
            self.TOPLEFTNEIGHBOUR = self.game.cells[self.i - 1][self.j - 1]
        if self.i > 0 and self.j < COL - 1: # topright neighbour
            self.TOPRIGHTNEIGHBOUR = self.game.cells[self.i - 1][self.j + 1]
        if self.i < ROW - 1 and self.j > 0: # bottomleft neighbour
            self.BOTTOMLEFTNEIGHBOUR = self.game.cells[self.i + 1][self.j - 1]
        if self.i < ROW - 1 and self.j < COL - 1: # bottomright neighbour
            self.BOTTOMRIGHTNEIGHBOUR = self.game.cells[self.i + 1][self.j + 1]

        self.neighbours = [
            self.TOPNEIGHBOUR,
            self.BOTTOMNEIGHBOUR,
            self.LEFTNEIGHBOUR,
            self.RIGHTNEIGHBOUR,
            self.TOPLEFTNEIGHBOUR,
            self.TOPRIGHTNEIGHBOUR,
            self.BOTTOMLEFTNEIGHBOUR,
            self.BOTTOMRIGHTNEIGHBOUR
        ]
        
    def update(self):
        
        if self.alive:
            self.draw()

    def draw(self):
        pygame.draw.rect(self.game.screen, WHITE, self.rect)

    def __repr__(self):
        return f"({self.j}, {self.i})"


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WWIDTH, WHEIGHT))
        pygame.display.set_caption("Game of Life")

        self.run = False
        self.FPSClock = pygame.time.Clock()

        self.tilemap = []
        for r in range(ROW):
            self.tilemap.append(
                [0] * COL
            )

        self.alive_on_click = True
        self.start_game = False
        self.cells = []

        # delta time
        self.dt_i = DT_INITIAL
        self.ct = time.time()

        self.ticks = 0
        self.tick_threshold = 60

    def update(self):
        self.screen.fill(BLACK)

        for r in self.cells:
            for cell in r:
                cell.update()


        self.mk_grid()
        pygame.display.update()

    def mk_grid(self):

        for row in range(ROW + 1):
            pygame.draw.line(self.screen, (GRAY), (0, row * TS), (WWIDTH, row * TS), 2)
        for col in range(COL + 1):
            pygame.draw.line(self.screen, (GRAY), (col * TS, 0), (col * TS, WHEIGHT), 2)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    self.start_game = not self.start_game
                    print(f'self.start_game set to {self.start_game}')

    def init_cells(self):

        self.cells = []
        for i in range(ROW):
            row_i = []
            for j in range(COL):
                row_i.append(
                    Cell(self, j, i)
                )

            self.cells.append(row_i)

    def paint_tiles(self):
        if pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for row in self.cells:
                for cell in row:
                    if cell.rect.collidepoint(pos):
                        if pygame.mouse.get_pressed()[0]: 
                            cell.alive = True
                            return

                        if pygame.mouse.get_pressed()[2]: 
                            cell.alive = False
                            return
                        
    def change_tick_threshold(self, dt):
        if 0 < self.tick_threshold + dt:
            self.tick_threshold += dt
            print(f'new tick threshold is {self.tick_threshold}')
                        
    def keyboard_listener(self):
        if pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.change_tick_threshold(1)

            if keys[pygame.K_DOWN]:
                self.change_tick_threshold(-1)

            if keys[pygame.K_r]:
                self.start_game = False
                for r in self.cells:
                    for cell in r:
                        cell.alive = False

            # cool different functions

            # invert  cell states
            if keys[pygame.K_i]:
                for r in self.cells:
                    for cell in r:
                        cell.alive = not cell.alive

    def handle_tick_rate(self):
        self.ticks += 1
        if self.ticks >= self.tick_threshold:
            self.ticks = 0
            return True
        return False
    
    def apply_laws(self):
        if not self.handle_tick_rate():
            return
        else:
            for r in self.cells:
                for cell in r:
                    num_alive = 0

                    for neighbour in cell.neighbours:
                        if neighbour is not None and neighbour.alive: num_alive += 1
                    
                    if cell.alive:
                        if num_alive < 2 or num_alive > 3:
                            cell.next_cell_state = False

                        else:
                            cell.next_cell_state = True

                    else:
                        if num_alive == 3:
                            cell.next_cell_state = True

                        else:
                            cell.next_cell_state = False
            
            for r in self.cells:
                for cell in r:
                    cell.update_state()


    def start(self):
        self.run = True

        self.init_cells()

        for row in self.cells:
            for cell in row:
                cell.get_neighbours()

        while self.run:
            self.FPSClock.tick(T_FPS)

            self.events()

            self.paint_tiles()
            self.keyboard_listener()

            if self.start_game:
                self.apply_laws()

            self.update()

if __name__ == '__main__':
    game = Game()
    game.start()