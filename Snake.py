import pygame

# Window
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
CELL_SIZE = 20
FPS = 60
MOVE_INTERVAL_MS = 100

BG_COLOR = (0, 0, 0)
GRID_COLOR = (40, 40, 40)

SNAKE_COLOR = (148, 0, 211)
SNAKE_BODY_MARGIN = 3

# Grid
def draw_grid(surface):
	for x in range(0, WINDOW_WIDTH, CELL_SIZE):
		pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT))
	for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
		pygame.draw.line(surface, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))


class Snake:

	def __init__(self):
		# start centered
		start_x = (WINDOW_WIDTH // CELL_SIZE) // 2
		start_y = (WINDOW_HEIGHT // CELL_SIZE) // 2
		self.segments = [(start_x - i, start_y) for i in range(3)]
		self.direction = (1, 0)
		self.next_direction = self.direction

	def set_direction(self, dir_tuple):
		# prevent reverse
		dx, dy = dir_tuple
		cdx, cdy = self.direction
		if (dx, dy) == (-cdx, -cdy):
			return
		self.next_direction = (dx, dy)

	def update(self):
		# move
		self.direction = self.next_direction
		hx, hy = self.segments[0]
		dx, dy = self.direction
		new_head = (hx + dx, hy + dy)
		# check wall
		max_x = WINDOW_WIDTH // CELL_SIZE
		max_y = WINDOW_HEIGHT // CELL_SIZE
		if new_head[0] < 0 or new_head[0] >= max_x or new_head[1] < 0 or new_head[1] >= max_y:
			# die
			self.alive = False
			return False

		# self-collision handling
		if getattr(self, 'grow_requested', False):
			collision = new_head in self.segments
		else:
			collision = new_head in self.segments[:-1]

		if collision:
			self.alive = False
			return False

		# apply move
		self.segments.insert(0, new_head)
		if getattr(self, 'grow_requested', False):
			self.grow_requested = False
		else:
			self.segments.pop()

		self.alive = True
		return True

	def grow(self):
		# grow next move
		self.grow_requested = True

	def draw(self, surface):
		# body
		for seg in self.segments[1:-1]:
			self._draw_body_segment(surface, seg)

		# tail
		if len(self.segments) >= 2:
			tail = self.segments[-1]
			before_tail = self.segments[-2]
			self._draw_tail(surface, tail, before_tail)

		# head
		head = self.segments[0]
		self._draw_head(surface, head)

	def _cell_to_px(self, cell):
		cx, cy = cell
		return (cx * CELL_SIZE, cy * CELL_SIZE)

	def _draw_body_segment(self, surface, cell):
		px, py = self._cell_to_px(cell)
		rect = pygame.Rect(px + SNAKE_BODY_MARGIN, py + SNAKE_BODY_MARGIN,
					   CELL_SIZE - 2 * SNAKE_BODY_MARGIN, CELL_SIZE - 2 * SNAKE_BODY_MARGIN)
		pygame.draw.rect(surface, SNAKE_COLOR, rect)

	def _draw_head(self, surface, cell):
		px, py = self._cell_to_px(cell)
		center = (px + CELL_SIZE // 2, py + CELL_SIZE // 2)
		radius = CELL_SIZE // 2 - 1
		pygame.draw.circle(surface, SNAKE_COLOR, center, radius)

	def _draw_tail(self, surface, tail, before_tail):
		# tail dir
		tx, ty = tail
		bx, by = before_tail
		dx, dy = tx - bx, ty - by

		px, py = self._cell_to_px(tail)
		cx = px + CELL_SIZE // 2
		cy = py + CELL_SIZE // 2

		if dx == 1:
			points = [(px, py), (px, py + CELL_SIZE), (px + CELL_SIZE, cy)]
		elif dx == -1:
			points = [(px + CELL_SIZE, py), (px + CELL_SIZE, py + CELL_SIZE), (px, cy)]
		elif dy == 1:
			points = [(px, py), (px + CELL_SIZE, py), (cx, py + CELL_SIZE)]
		else:
			points = [(px, py + CELL_SIZE), (px + CELL_SIZE, py + CELL_SIZE), (cx, py)]

		pygame.draw.polygon(surface, SNAKE_COLOR, points)



def main():
	pygame.init()
	screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
	pygame.display.set_caption('Snake Game')
	clock = pygame.time.Clock()

	snake = Snake()

	# food and score
	score = 0

	class Food:
		def __init__(self):
			self.pos = None

		def spawn(self, occupied):
			max_x = WINDOW_WIDTH // CELL_SIZE
			max_y = WINDOW_HEIGHT // CELL_SIZE
			import random
			while True:
				x = random.randrange(0, max_x)
				y = random.randrange(0, max_y)
				if (x, y) not in occupied:
					self.pos = (x, y)
					return

		def draw(self, surface):
			if self.pos is None:
				return
			px = self.pos[0] * CELL_SIZE
			py = self.pos[1] * CELL_SIZE
			rect = pygame.Rect(px + 4, py + 4, CELL_SIZE - 8, CELL_SIZE - 8)
			pygame.draw.rect(surface, (255, 100, 0), rect)

	food = Food()

	# spawn
	food.spawn(snake.segments)
	last_move_ms = pygame.time.get_ticks()

	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False

		screen.fill(BG_COLOR)
		draw_grid(screen)

		# draw food and score
		food.draw(screen)


		# input
		keys = pygame.key.get_pressed()
		if getattr(snake, 'alive', True):
			if keys[pygame.K_UP] or keys[pygame.K_w]:
				snake.set_direction((0, -1))
			elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
				snake.set_direction((0, 1))
			elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
				snake.set_direction((-1, 0))
			elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
				snake.set_direction((1, 0))


		# moving
		now = pygame.time.get_ticks()
		if now - last_move_ms >= MOVE_INTERVAL_MS:
			moved = snake.update()
			# eating
			if moved and snake.segments[0] == food.pos:
				snake.grow()
				score += 1
				food.spawn(snake.segments)
			last_move_ms = now
		snake.draw(screen)

		# game over
		if not getattr(snake, 'alive', True):
			font = pygame.font.Font(None, 48)
			text = font.render('Game Over - R to restart', True, (255, 50, 50))
			rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
			screen.blit(text, rect)
			# restart
			keys = pygame.key.get_pressed()
			if keys[pygame.K_r]:
				# reset
				snake = Snake()
				food.spawn(snake.segments)
				score = 0
				last_move_ms = pygame.time.get_ticks()

		# score
		font = pygame.font.Font(None, 24)
		score_surf = font.render(f"Score: {score}", True, (200, 200, 200))
		screen.blit(score_surf, (8, 8))

		pygame.display.flip()
		clock.tick(FPS)

	pygame.quit()



if __name__ == '__main__':
	main()
