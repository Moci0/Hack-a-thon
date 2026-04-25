import json
import math
import matplotlib.pyplot as plt
import os

class GolfCaddieApp:
    def __init__(self, json_path, start_lat, start_lon):
        self.json_path = json_path
        self.user_lat = start_lat
        self.user_lon = start_lon
        self.move_step = 0.0001 # Roughly 10 yards per press
        
        # Load Data
        with open(json_path, 'r') as f:
            self.data = json.load(f)
        self.nodes = {item['id']: (item['lon'], item['lat']) for item in self.data['elements'] if item['type'] == 'node'}
        
        # Setup Figure
        self.fig, self.ax = plt.subplots(figsize=(10, 10), facecolor='#1e272e')
        self.fig.canvas.manager.set_window_title('Interactive Golf Caddie')
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        
        self.update_display()
        print("⌨️ Controls: Use Arrow Keys to move your position.")
        plt.show()

    def get_distance(self, lat1, lon1, lat2, lon2):
        R = 6371000 
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi, dlambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return (R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))) * 1.09361

    def get_centroid(self, item):
        if item['type'] == 'node': return (item['lon'], item['lat'])
        coords = [self.nodes[nid] for nid in item.get('nodes', []) if nid in self.nodes]
        if not coords: return None
        return (sum(c[0] for c in coords) / len(coords), sum(c[1] for c in coords) / len(coords))

    def on_key(self, event):
        if event.key == 'up': self.user_lat += self.move_step
        elif event.key == 'down': self.user_lat -= self.move_step
        elif event.key == 'left': self.user_lon -= self.move_step
        elif event.key == 'right': self.user_lon += self.move_step
        else: return
        
        self.update_display()

    def update_display(self):
        self.ax.clear()
        self.ax.set_facecolor('#2f3640')
        
        # 1. Find Closest Green
        active_hole = "Unknown"
        min_dist = float('inf')
        target_green = None

        for item in self.data['elements']:
            if item.get('tags', {}).get('golf') == 'green':
                center = self.get_centroid(item)
                if center:
                    dist = self.get_distance(self.user_lat, self.user_lon, center[1], center[0])
                    if dist < min_dist:
                        min_dist = dist
                        active_hole = item['tags'].get('ref', 'Unknown')
                        target_green = center

        # 2. Draw Map Features
        for item in self.data['elements']:
            if item['type'] == 'way':
                tags = item.get('tags', {})
                g_type = tags.get('golf')
                
                # Draw if it's the active hole or general fairway/bunker
                if tags.get('ref') == active_hole or g_type in ['fairway', 'bunker', 'green']:
                    coords = [self.nodes[nid] for nid in item.get('nodes', []) if nid in self.nodes]
                    if not coords: continue
                    x, y = zip(*coords)
                    
                    color = '#4cd137' if g_type == 'fairway' else '#006266' if g_type == 'green' else '#fbc531'
                    self.ax.fill(x, y, color=color, alpha=0.8, zorder=2)

        # 3. Draw User
        self.ax.scatter([self.user_lon], [self.user_lat], color='#e84118', s=200, edgecolor='white', zorder=10)
        
        # 4. Zoom Camera
        pad = 0.003
        if target_green:
            self.ax.set_xlim(min(self.user_lon, target_green[0]) - pad, max(self.user_lon, target_green[0]) + pad)
            self.ax.set_ylim(min(self.user_lat, target_green[1]) - pad, max(self.user_lat, target_green[1]) + pad)

        self.ax.set_title(f"HOLE {active_hole} | {int(min_dist)} YARDS", color='white', fontsize=20, pad=10)
        self.ax.axis('off')
        self.fig.canvas.draw()

if __name__ == "__main__":
    # Starting coordinates for Forest of Dean (Course 26741)
    GolfCaddieApp('course_data/course_26741.json', 51.7919, -2.6112)