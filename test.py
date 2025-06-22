import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Grid settings
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 30
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 10  # Frames per second

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)

class Snake:
    def __init__(self, body, direction, color):
        self.body = body              # List of (x, y) tuples; head is index 0.
        self.direction = direction    # Tuple (dx, dy)
        self.color = color
        self.alive = True

    def get_head(self):
        return self.body[0]

    def choose_direction(self, apples, snakes):
        """
        Choose a direction that aims for the nearest apple while also avoiding collisions
        with walls, self, and other snakes. Uses a simple heuristic:
          - For each candidate direction (up/down/left/right), if the next cell is within the grid
            and not immediately colliding with self or with another snake (unless that cell is a tail
            cell likely to be vacated), then compute a cost.
          - The cost is the Manhattan distance to the nearest apple plus an extra penalty for being
            adjacent to other snake segments.
          - The snake returns the move (dx, dy) with the lowest total cost.
        """
        possible = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        head = self.get_head()

        # Determine the closest apple (by Manhattan distance)
        if apples:
            closest_apple = min(apples, key=lambda a: abs(head[0] - a[0]) + abs(head[1] - a[1]))
        else:
            closest_apple = (GRID_WIDTH // 2, GRID_HEIGHT // 2)

        candidates = []
        for d in possible:
            next_cell = (head[0] + d[0], head[1] + d[1])
            # --- 1. Check grid boundaries ---
            if not (0 <= next_cell[0] < GRID_WIDTH and 0 <= next_cell[1] < GRID_HEIGHT):
                continue

            # --- 2. Check collision with self ---
            # If next_cell is in our body, allow it only if it is our tail cell and we are NOT eating an apple.
            if next_cell in self.body:
                if next_cell == self.body[-1] and next_cell not in apples:
                    pass  # Allowed because the tail will be vacated.
                else:
                    continue

            # --- 3. Check collision with other snakes ---
            unsafe = False
            for other in snakes:
                if other is self or not other.alive:
                    continue
                if next_cell in other.body:
                    # Allow moving into the tail cell of a snake (if its length > 1) since that cell is expected to be freed.
                    if len(other.body) > 1 and next_cell == other.body[-1]:
                        pass
                    else:
                        unsafe = True
                        break
            if unsafe:
                continue

            # --- 4. Compute cost: distance to apple plus a penalty for proximity to other snakes ---
            cost = abs(next_cell[0] - closest_apple[0]) + abs(next_cell[1] - closest_apple[1])
            penalty = 0
            # Look at adjacent cells around next_cell.
            for nd in possible:
                neighbor = (next_cell[0] + nd[0], next_cell[1] + nd[1])
                for other in snakes:
                    if other is self or not other.alive:
                        continue
                    if neighbor in other.body:
                        penalty += 2  # Adjust this value for more caution.
            total_cost = cost + penalty

            candidates.append((total_cost, d))

        if candidates:
            # --- 5. Choose candidate move with lowest total cost ---
            candidates.sort(key=lambda x: x[0])
            return candidates[0][1]
        else:
            # --- 6. Fallback: if no safe move is found, keep moving in the current direction ---
            return self.direction

    def move(self, new_direction, ate_apple):
        """
        Update the snake’s body based on the chosen move.
          - If ate_apple is True then the snake grows (its tail remains).
          - Otherwise, the tail is removed.
        """
        head = self.get_head()
        new_head = (head[0] + new_direction[0], head[1] + new_direction[1])
        self.direction = new_direction
        self.body.insert(0, new_head)
        if not ate_apple:
            self.body.pop()

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("100 Snake Competition - Indefinite Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    # Create 100 snakes with random starting positions, directions, and colors.
    snakes = []
    occupied = set()  # To avoid overlapping starting positions.
    NUM_SNAKES = 100
    for i in range(NUM_SNAKES):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in occupied:
                break
        direction = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
        body = [(x, y)]
        # Attempt to create an initial length of 3 by extending in the opposite direction.
        dx, dy = -direction[0], -direction[1]
        second = (x + dx, y + dy)
        third = (x + 2 * dx, y + 2 * dy)
        if 0 <= second[0] < GRID_WIDTH and 0 <= second[1] < GRID_HEIGHT:
            body.append(second)
            if 0 <= third[0] < GRID_WIDTH and 0 <= third[1] < GRID_HEIGHT:
                body.append(third)
        for cell in body:
            occupied.add(cell)
        color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        snakes.append(Snake(body, direction, color))

    # --- Apple setup (multiple apples) ---
    NUM_APPLES = 5
    def spawn_apple(existing_apples):
        """
        Choose a random cell that is not occupied by any snake (alive or dead) or an existing apple.
        """
        occupied_cells = set()
        for snake in snakes:
            for cell in snake.body:
                occupied_cells.add(cell)
        for apple in existing_apples:
            occupied_cells.add(apple)
        free_cells = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)
                      if (x, y) not in occupied_cells]
        return random.choice(free_cells) if free_cells else None

    apples = []
    for _ in range(NUM_APPLES):
        new_apple = spawn_apple(apples)
        if new_apple is None:
            break
        apples.append(new_apple)

    running = True
    while running:
        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Determine each snake’s move ---
        moves = {}  # Map each snake to its chosen move.
        for snake in snakes:
            if snake.alive:
                new_dir = snake.choose_direction(apples, snakes)
                moves[snake] = new_dir

        # --- Determine which snakes will eat an apple ---
        ate = {}
        eaten_apples = set()  # To handle the case of multiple snakes moving into an apple cell.
        for snake in snakes:
            if snake.alive:
                head = snake.get_head()
                new_head = (head[0] + moves[snake][0], head[1] + moves[snake][1])
                if new_head in apples:
                    ate[snake] = True
                    eaten_apples.add(new_head)
                else:
                    ate[snake] = False

        # --- Compute new bodies for collision detection ---
        new_bodies = {}
        for snake in snakes:
            if snake.alive:
                head = snake.get_head()
                new_head = (head[0] + moves[snake][0], head[1] + moves[snake][1])
                if ate[snake]:
                    new_body = [new_head] + snake.body[:]  # Grow (tail remains)
                else:
                    new_body = [new_head] + snake.body[:-1]  # Normal move (tail removed)
                new_bodies[snake] = new_body

        # --- Collision detection ---
        for snake in snakes:
            if not snake.alive:
                continue
            new_body = new_bodies[snake]
            head = new_body[0]
            # Wall collision.
            if not (0 <= head[0] < GRID_WIDTH and 0 <= head[1] < GRID_HEIGHT):
                snake.alive = False
                continue
            # Self-collision.
            if head in new_body[1:]:
                snake.alive = False
                continue
            # Collision with any segment of any other snake.
            for other in snakes:
                if other is snake or not other.alive:
                    continue
                other_new_body = new_bodies.get(other, other.body)
                if head in other_new_body:
                    snake.alive = False
                    break

        # --- Update snakes that are still alive ---
        for snake in snakes:
            if snake.alive and snake in new_bodies:
                snake.body = new_bodies[snake]

        # --- Remove eaten apples and spawn new ones ---
        for apple in eaten_apples:
            if apple in apples:
                apples.remove(apple)
        while len(apples) < NUM_APPLES:
            new_apple = spawn_apple(apples)
            if new_apple is None:
                break
            apples.append(new_apple)

        # --- Drawing ---
        screen.fill(BLACK)
        # Draw apples.
        for apple in apples:
            rect = pygame.Rect(apple[0] * CELL_SIZE, apple[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, RED, rect)
        # Draw snakes.
        for snake in snakes:
            if not snake.alive:
                continue
            # Alive snakes are drawn in their color; dead snakes are drawn in gray.
            col = snake.color
            for segment in snake.body:
                rect = pygame.Rect(segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, col, rect)
        # Draw status text.
        alive_count = sum(1 for snake in snakes if snake.alive)
        text = font.render(f"Snakes alive: {alive_count}", True, WHITE)
        screen.blit(text, (5, 5))
        pygame.display.flip()

        clock.tick(FPS)

        # Note: We no longer automatically end the simulation.
        # The simulation will continue indefinitely until the user closes the window.

    pygame.quit()
    print("Simulation closed manually.")

if __name__ == "__main__":
    main()
