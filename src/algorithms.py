import heapq
import time

class SPFA_Algorithms:
    @staticmethod
    def dijkstras(n, edges, src, dst, visualizer_callback=None, delay=0.05):
        adj = {i: [] for i in range(n)}

        # edges: (u,v,w)
        for u, v, w in edges:
            adj[u].append((v, w))

        dist = {i: float("inf") for i in range(n)}
        parent = {i: None for i in range(n)}
        visited = set()

        dist[src] = 0
        pq = [(0, src)]

        while pq:
            cur_dist, node = heapq.heappop(pq)

            if node == dst:
                break  # we found the shortest path to the goal

            if cur_dist > dist[node]:
                continue

            visited.add(node)
            
            # Visualize current exploration
            if visualizer_callback:
                visualizer_callback(list(visited), [])
                time.sleep(delay)

            for neigh, w in adj[node]:
                new_dist = cur_dist + w
                if new_dist < dist[neigh]:
                    dist[neigh] = new_dist
                    parent[neigh] = node
                    heapq.heappush(pq, (new_dist, neigh))

        # reconstruct path
        path = []
        cur = dst
        while cur is not None:
            path.append(cur)
            cur = parent[cur]

        path.reverse()
        
        # Final visualization with path
        if visualizer_callback:
            visualizer_callback(list(visited), path)
            
        return path, visited  # return both path and visited nodes
    
    @staticmethod
    def bellman_ford(n, edges, src, dst, visualizer_callback=None, delay=0.05):
    
        dist = {i: float("inf") for i in range(n)}
        parent = {i: None for i in range(n)}
        dist[src] = 0
        visited = set([src])

        # Relax edges n-1 times
        for iteration in range(n - 1):
            updated = False
            for u, v, w in edges:
                if dist[u] != float("inf") and dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    parent[v] = u
                    visited.add(v)
                    updated = True
                    
                    # Visualize current exploration
                    if visualizer_callback:
                        visualizer_callback(list(visited), [])
                        time.sleep(delay)
            
            if not updated:
                break  # No more updates, can exit early

        # Check for negative weight cycles
        for u, v, w in edges:
            if dist[u] != float("inf") and dist[u] + w < dist[v]:
                print("Warning: Negative weight cycle detected!")
                return [], set()

        # Check if destination is reachable
        if dist[dst] == float("inf"):
            return [], visited
            
        # Reconstruct path
        path = []
        cur = dst
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
        
        # Final visualization with path
        if visualizer_callback:
            visualizer_callback(list(visited), path)
        
        return path, visited
    
    @staticmethod
    def a_star(n, edges, src, dst, heuristic, visualizer_callback=None, delay=0.05):

        adj = {i: [] for i in range(n)}
        for u, v, w in edges:
            adj[u].append((v, w))

        g_score = {i: float("inf") for i in range(n)}
        f_score = {i: float("inf") for i in range(n)}
        parent = {i: None for i in range(n)}
        visited = set()

        g_score[src] = 0
        f_score[src] = heuristic(src)

        pq = [(f_score[src], src)]

        while pq:
            _, current = heapq.heappop(pq)

            if current == dst:
                break

            visited.add(current)
            
            # Visualize current exploration
            if visualizer_callback:
                visualizer_callback(list(visited), [])
                time.sleep(delay)

            for neighbor, w in adj[current]:
                tentative_g = g_score[current] + w
                if tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor)
                    parent[neighbor] = current
                    heapq.heappush(pq, (f_score[neighbor], neighbor))

        if g_score[dst] == float("inf"):
            return [], visited

        path = []
        cur = dst
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
        
        # Final visualization with path
        if visualizer_callback:
            visualizer_callback(list(visited), path)
            
        return path, visited

    @staticmethod
    def dfs(maze,start,goal,ROWS,COLS):
        # TODO: implement your code here
        pass

class PathFinder:
    """Handles pathfinding algorithms"""
    def __init__(self, visualizer, maze_state):
        self.viz = visualizer
        self.maze_state = maze_state
        self.is_computing = False
    
    def visualize_step(self, visited_ids, path_ids):
        """Callback function to update visualization during algorithm execution"""
        # Convert IDs to coordinates
        self.maze_state.intermediate_steps = [self.viz.coord_from_id(vid) for vid in visited_ids]
        self.maze_state.shortest_path = [self.viz.coord_from_id(pid) for pid in path_ids]
    
    def compute_path(self, algo_name, delay=0.05):
        """Compute shortest path using specified algorithm with real-time visualization"""
        if self.maze_state.start is None:
            raise ValueError("Start cell not set!")
        if self.maze_state.end is None:
            raise ValueError("End cell not set!")
        
        if self.is_computing:
            return  # Prevent multiple simultaneous computations
        
        self.is_computing = True
        
        # Clear previous results
        self.maze_state.shortest_path = []
        self.maze_state.intermediate_steps = []
        
        # Update visualizer references
        self.viz.start = self.maze_state.start
        self.viz.goal = self.maze_state.end
        self.viz.maze = self.maze_state.maze
        
        # Create graph from current maze
        graph = self.viz.maze_to_graph()
        graph.start = self.maze_state.start
        graph.goal = self.maze_state.end
        
        # Convert graph to edges
        edges = []
        for (r, c) in graph.nodes:
            u = self.viz.id_from_coord(r, c)
            for (nr, nc) in graph.neighbors((r, c)):
                v = self.viz.id_from_coord(nr, nc)
                edges.append((u, v, 1))
        
        src_id = self.viz.id_from_coord(*self.maze_state.start)
        dst_id = self.viz.id_from_coord(*self.maze_state.end)
        n = self.maze_state.rows * self.maze_state.cols
        
        # Run selected algorithm with visualization callback
        result = self._run_algorithm(algo_name, n, edges, src_id, dst_id, delay)
        path_ids, visited_ids = result
        
        self.is_computing = False
        
        if not path_ids:
            self.maze_state.shortest_path = []
            self.maze_state.intermediate_steps = []
            raise ValueError("No path found!")
        else:
            print(f"Found path length: {len(path_ids)}")
    
    def _run_algorithm(self, algo_name, n, edges, src_id, dst_id, delay):
        """Execute the specified pathfinding algorithm"""
        if algo_name == "Dijkstra":
            return SPFA_Algorithms.dijkstras(
                n=n, edges=edges, src=src_id, dst=dst_id,
                visualizer_callback=self.visualize_step,
                delay=delay
            )
        elif algo_name == "A*":
            return SPFA_Algorithms.a_star(
                n=n, edges=edges, src=src_id, dst=dst_id,
                heuristic=self._manhattan_heuristic,
                visualizer_callback=self.visualize_step,
                delay=delay
            )
        elif algo_name == "Bellman-Ford":
            return SPFA_Algorithms.bellman_ford(
                n=n, edges=edges, src=src_id, dst=dst_id,
                visualizer_callback=self.visualize_step,
                delay=delay
            )
        elif algo_name == "DFS":
            # TODO: Integrate DFS algorithm
            return
        else:
            raise ValueError(f"Unknown algorithm: {algo_name}")
    
    def _manhattan_heuristic(self, node_id):
        """Calculate Manhattan distance heuristic"""
        r, c = self.viz.coord_from_id(node_id)
        er, ec = self.maze_state.end
        return abs(r - er) + abs(c - ec)