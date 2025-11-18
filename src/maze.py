from graph import Graph
import pygame

class MazeVisualizer:
    def __init__(self, rows=10, cols=10, cell_size=50, grid_origin=(50,50),
                 maze=None, start=(0,0), end=None):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.grid_origin = grid_origin

        # Enhanced colors
        self.WHITE = (250, 250, 250)
        self.BLACK = (40, 40, 50)
        self.START_COLOR = (100, 220, 120)
        self.END_COLOR = (240, 100, 100)
        self.GRID_LINE = (100, 100, 120)
        self.PATH_COLOR = (100, 150, 255)

        # Maze (0 = path, 1 = wall). If not provided, initialize empty.
        if maze is None:
            self.maze = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        else:
            self.maze = maze

        self.start = start
        self.end = end if end is not None else (self.rows - 1, self.cols - 1)

    def id_from_coord(self, r, c):
        return r * self.cols + c

    def coord_from_id(self, id_):
        return (id_ // self.cols, id_ % self.cols)

    def draw_grid(self, surface, path=None):
        ox, oy = self.grid_origin

        # Draw grid border
        border_rect = pygame.Rect(
            ox - 3, oy - 3,
            self.cols * self.cell_size + 6,
            self.rows * self.cell_size + 6
        )
        pygame.draw.rect(surface, (80, 80, 100), border_rect, 3, border_radius=5)

        for r in range(self.rows):
            for c in range(self.cols):
                # Determine cell color with priority
                if path and (r, c) in path:
                    color = self.PATH_COLOR
                elif (r, c) == self.start:
                    color = self.START_COLOR
                elif (r, c) == self.end:
                    color = self.END_COLOR
                else:
                    color = self.BLACK if self.maze[r][c] == 1 else self.WHITE

                rect = pygame.Rect(
                    ox + c * self.cell_size,
                    oy + r * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )

                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, self.GRID_LINE, rect, 1)
                
                # Add labels for start and end
                font = pygame.font.SysFont(None, 20)
                if (r, c) == self.start:
                    text = font.render("S", True, (255, 255, 255))
                    text_rect = text.get_rect(center=rect.center)
                    surface.blit(text, text_rect)
                elif (r, c) == self.end:
                    text = font.render("E", True, (255, 255, 255))
                    text_rect = text.get_rect(center=rect.center)
                    surface.blit(text, text_rect)

    def maze_to_graph(self):
        """Convert maze to graph where white cells are nodes connected orthogonally."""
        g = Graph()

        # Create a node for each white cell
        for r in range(self.rows):
            for c in range(self.cols):
                if self.maze[r][c] == 0:  # white path cell
                    node_id = (r, c)
                    g.add_node(node_id, x=c, y=r)

        # Connect orthogonal neighbors (no diagonals)
        for r in range(self.rows):
            for c in range(self.cols):
                if self.maze[r][c] == 0:  # current cell is white
                    current = (r, c)

                    # Check all 4 orthogonal directions
                    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

                    for dr, dc in directions:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols and self.maze[nr][nc] == 0:
                            neighbor = (nr, nc)
                            g.add_edge(current, neighbor)

        return g


class MazeState:
    """Manages the maze grid and start/end positions"""
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.maze = [[0 for _ in range(cols)] for _ in range(rows)]
        self.start = None
        self.end = None
        self.shortest_path = []
    
    def toggle_wall(self, row, col):
        """Toggle wall at given position"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.maze[row][col] = 1 - self.maze[row][col]
            self.shortest_path = []
    
    def set_start(self, row, col):
        """Set start position and ensure it's not a wall"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.start = (row, col)
            self.maze[row][col] = 0
            self.shortest_path = []
    
    def set_end(self, row, col):
        """Set end position and ensure it's not a wall"""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.end = (row, col)
            self.maze[row][col] = 0
            self.shortest_path = []
    
    def clear(self):
        """Reset maze to empty state"""
        self.maze = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.start = None
        self.end = None
        self.shortest_path = []


class UIState:
    """Manages UI state and button definitions with responsive positioning"""
    def __init__(self, left_panel_x=40, right_panel_x=1120, screen_height=900):
        self.selected_algo = "Dijkstra"
        self.edit_mode = "wall"
        self.error_message = ""
        self.error_timer = 0
        
        # Left panel buttons (Edit Controls)
        left_x = left_panel_x + 20
        button_width = 200
        button_height = 45
        
        mode_start_y = 150
        self.mode_buttons = [
            (pygame.Rect(left_x, mode_start_y, button_width, button_height), 
             "wall", "Toggle Wall"),
            (pygame.Rect(left_x, mode_start_y + 60, button_width, button_height), 
             "start", "Set Start"),
            (pygame.Rect(left_x, mode_start_y + 120, button_width, button_height), 
             "end", "Set End"),
        ]
        
        self.clear_button = pygame.Rect(left_x, mode_start_y + 200, button_width, button_height)
        
        # Right panel buttons (Algorithm Selection)
        right_x = right_panel_x + 20
        
        algo_start_y = 150
        self.algo_buttons = [
            (pygame.Rect(right_x, algo_start_y, button_width, button_height), "Dijkstra"),
            (pygame.Rect(right_x, algo_start_y + 60, button_width, button_height), "A*"),
            (pygame.Rect(right_x, algo_start_y + 120, button_width, button_height), "Bellman-Ford"),
            (pygame.Rect(right_x, algo_start_y + 180, button_width, button_height), "DFS"),
            (pygame.Rect(right_x, algo_start_y + 240, button_width, button_height), "BFS"),
        ]
        
        self.find_button = pygame.Rect(right_x, algo_start_y + 320, button_width, 55)
    
    def show_error(self, message):
        """Display error message for 3 seconds"""
        self.error_message = message
        self.error_timer = 180  # 3 seconds at 60 FPS
    
    def update_error_timer(self):
        """Decrease error timer"""
        if self.error_timer > 0:
            self.error_timer -= 1