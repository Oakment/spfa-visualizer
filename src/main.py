import pygame
from maze import MazeVisualizer, MazeState, UIState
from algorithms import PathFinder

# CONFIG
ROWS = 10
COLS = 10
CELL_SIZE = 50  # Slightly larger cells


class SPFAVisualizer:
    """Main application class"""
    def __init__(self):
        pygame.init()
        
        # Get display info and set window size
        display_info = pygame.display.Info()
        self.screen_width = min(1400, display_info.current_w - 100)
        self.screen_height = min(900, display_info.current_h - 100)
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("SPFA Visualizer - Interactive")
        self.clock = pygame.time.Clock()
        
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 32)
        self.error_font = pygame.font.SysFont(None, 20)
        
        # Calculate grid position (centered)
        self.grid_width = COLS * CELL_SIZE
        self.grid_height = ROWS * CELL_SIZE
        self.grid_origin = (
            (self.screen_width - self.grid_width) // 2,
            (self.screen_height - self.grid_height) // 2
        )
        
        # Calculate panel positions
        self.left_panel_x = 40
        self.right_panel_x = self.screen_width - 280
        
        # Initialize state components
        self.maze_state = MazeState(ROWS, COLS)
        self.ui_state = UIState(self.left_panel_x, self.right_panel_x, self.screen_height)
        
        # Initialize visualizer
        self.viz = MazeVisualizer(
            rows=ROWS, cols=COLS, cell_size=CELL_SIZE,
            grid_origin=self.grid_origin, maze=self.maze_state.maze,
            start=None, end=None
        )
        
        # Initialize pathfinder
        self.pathfinder = PathFinder(self.viz, self.maze_state)
        
        self.running = True
    
    def handle_grid_click(self, mx, my):
        """Handle clicks on the maze grid"""
        gx = mx - self.grid_origin[0]
        gy = my - self.grid_origin[1]
        
        if gx < 0 or gy < 0:
            return
        
        col = gx // CELL_SIZE
        row = gy // CELL_SIZE
        
        if 0 <= row < ROWS and 0 <= col < COLS:
            if self.ui_state.edit_mode == "wall":
                self.maze_state.toggle_wall(row, col)
            elif self.ui_state.edit_mode == "start":
                self.maze_state.set_start(row, col)
            elif self.ui_state.edit_mode == "end":
                self.maze_state.set_end(row, col)
    
    def handle_button_clicks(self, mx, my):
        """Handle clicks on UI buttons"""
        # Find Path button
        if self.ui_state.find_button.collidepoint(mx, my):
            try:
                self.pathfinder.compute_path(self.ui_state.selected_algo)
            except ValueError as e:
                self.ui_state.show_error(f"Error: {str(e)}")
            except Exception as e:
                self.ui_state.show_error(f"Error: {str(e)}")
            return True
        
        # Clear Maze button
        if self.ui_state.clear_button.collidepoint(mx, my):
            self.maze_state.clear()
            return True
        
        # Algorithm selection buttons
        for rect, name in self.ui_state.algo_buttons:
            if rect.collidepoint(mx, my):
                self.ui_state.selected_algo = name
                return True
        
        # Edit mode buttons
        for rect, mode, _ in self.ui_state.mode_buttons:
            if rect.collidepoint(mx, my):
                self.ui_state.edit_mode = mode
                return True
        
        return False
    
    def handle_events(self):
        """Process pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                
                # Check grid clicks first
                grid_rect = pygame.Rect(
                    self.grid_origin[0], self.grid_origin[1],
                    self.grid_width, self.grid_height
                )
                if grid_rect.collidepoint(mx, my):
                    self.handle_grid_click(mx, my)
                else:
                    self.handle_button_clicks(mx, my)
    
    def draw_ui(self):
        """Draw all UI elements"""
        # Background with gradient effect
        self.screen.fill((45, 45, 55))
        
        # Draw title
        title_surf = self.title_font.render("SPFA Pathfinding Visualizer", True, (220, 220, 240))
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, 30))
        self.screen.blit(title_surf, title_rect)
        
        # Update visualizer state before drawing
        self.viz.start = self.maze_state.start
        self.viz.goal = self.maze_state.end
        self.viz.end = self.maze_state.end
        self.viz.maze = self.maze_state.maze
        self.viz.draw_grid(self.screen, path=self.maze_state.shortest_path)
        
        # LEFT PANEL - Edit Controls
        self.draw_left_panel()
        
        # RIGHT PANEL - Algorithm Selection
        self.draw_right_panel()
        
        # Error message at bottom
        if self.ui_state.error_timer > 0:
            error_surf = self.error_font.render(
                self.ui_state.error_message, True, (255, 120, 120)
            )
            error_rect = error_surf.get_rect(center=(self.screen_width // 2, self.screen_height - 30))
            bg_rect = error_rect.inflate(30, 15)
            pygame.draw.rect(self.screen, (60, 40, 40), bg_rect, border_radius=8)
            pygame.draw.rect(self.screen, (255, 100, 100), bg_rect, 2, border_radius=8)
            self.screen.blit(error_surf, error_rect)
    
    def draw_left_panel(self):
        """Draw left control panel"""
        panel_x = self.left_panel_x
        panel_y = 80
        panel_width = 240
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, self.screen_height - 160)
        pygame.draw.rect(self.screen, (35, 35, 45), panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, (80, 80, 100), panel_rect, 2, border_radius=10)
        
        # Section title
        y_offset = panel_y + 20
        title = self.font.render("Edit Controls", True, (220, 220, 240))
        self.screen.blit(title, (panel_x + 50, y_offset))
        
        y_offset += 50
        
        # Edit mode buttons
        for rect, mode, label in self.ui_state.mode_buttons:
            is_selected = mode == self.ui_state.edit_mode
            color = (100, 150, 220) if is_selected else (70, 70, 85)
            border_color = (150, 180, 240) if is_selected else (100, 100, 120)
            
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=8)
            
            text = self.font.render(label, True, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
        
        # Clear button
        pygame.draw.rect(self.screen, (180, 70, 70), self.ui_state.clear_button, border_radius=8)
        pygame.draw.rect(self.screen, (220, 100, 100), self.ui_state.clear_button, 2, border_radius=8)
        clear_text = self.font.render("Clear Maze", True, (255, 255, 255))
        clear_rect = clear_text.get_rect(center=self.ui_state.clear_button.center)
        self.screen.blit(clear_text, clear_rect)
        
        # Status info
        status_y = self.ui_state.clear_button.bottom + 40
        
        status_lines = [
            f"Current Mode:",
            f"  {self.ui_state.edit_mode.title()}",
            "",
            f"Start Position:",
            f"  {self.maze_state.start if self.maze_state.start else 'Not set'}",
            "",
            f"End Position:",
            f"  {self.maze_state.end if self.maze_state.end else 'Not set'}",
        ]
        
        for i, line in enumerate(status_lines):
            color = (200, 200, 220) if line and not line.startswith("  ") else (160, 160, 180)
            text = self.error_font.render(line, True, color)
            self.screen.blit(text, (panel_x + 20, status_y + i * 22))
    
    def draw_right_panel(self):
        """Draw right algorithm panel"""
        panel_x = self.right_panel_x
        panel_y = 80
        panel_width = 240
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, self.screen_height - 160)
        pygame.draw.rect(self.screen, (35, 35, 45), panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, (80, 80, 100), panel_rect, 2, border_radius=10)
        
        # Section title
        y_offset = panel_y + 20
        title = self.font.render("Algorithm", True, (220, 220, 240))
        self.screen.blit(title, (panel_x + 70, y_offset))
        
        y_offset += 50
        
        # Algorithm buttons
        for rect, name in self.ui_state.algo_buttons:
            is_selected = name == self.ui_state.selected_algo
            color = (100, 180, 120) if is_selected else (70, 70, 85)
            border_color = (130, 220, 150) if is_selected else (100, 100, 120)
            
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=8)
            
            text = self.font.render(name, True, (255, 255, 255))
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
        
        # Find Path button
        pygame.draw.rect(self.screen, (70, 140, 200), self.ui_state.find_button, border_radius=8)
        pygame.draw.rect(self.screen, (100, 170, 230), self.ui_state.find_button, 3, border_radius=8)
        find_text = self.font.render("Find Path", True, (255, 255, 255))
        find_rect = find_text.get_rect(center=self.ui_state.find_button.center)
        self.screen.blit(find_text, find_rect)
        
        # Selected algorithm info
        info_y = self.ui_state.find_button.bottom + 40
        info_lines = [
            "Selected Algorithm:",
            f"  {self.ui_state.selected_algo}",
        ]
        
        for i, line in enumerate(info_lines):
            color = (200, 200, 220) if not line.startswith("  ") else (160, 220, 160)
            text = self.error_font.render(line, True, color)
            self.screen.blit(text, (panel_x + 20, info_y + i * 22))
    
    def run(self):
        """Main application loop"""
        while self.running:
            self.handle_events()
            self.ui_state.update_error_timer()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()


def main():
    app = SPFAVisualizer()
    app.run()


if __name__ == "__main__":
    main()