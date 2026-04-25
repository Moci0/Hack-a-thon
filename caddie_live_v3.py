import json
import math
import matplotlib.pyplot as plt
from matplotlib.path import Path
import os
import sys

class ProximityCaddie:
    def __init__(self, json_path):
        self.json_path = json_path
        self.last_known_hole = "None"
        self.on_fairway = False
        
        # --- JUMP SIZE SETTING ---
        # 0.0001 is ~10 yards. 0.00002 is ~2 yards per tap.
        self.move_step = 0.00002 
        
        self.current_hole_index = 0 
        
        # 1. Load Data
        with open(json_path, 'r') as f:
            self.data = json.load(f)
        
        # 2. Index Nodes
        self.nodes = {item['id']: (item['lon'], item['lat']) for item in self.data['elements'] if item['type'] == 'node'}
        
        # 3. Organize features
        self.fairways = []
        self.greens = []
        self.bunkers = []

        green_count = 1
        for item in self.data['elements']:
            if item['type'] == 'way':
                tags = item.get('tags', {})
                g_type = tags.get('golf')
                
                if g_type == 'fairway':
                    self.fairways.append(item)
                elif g_type == 'green':
                    item['centroid'] = self.get_centroid(item)
                    if item['centroid']:
                        item['assigned_ref'] = tags.get('ref', str(green_count))
                        self.greens.append(item)
                        green_count += 1
                elif g_type == 'bunker':
                    self.bunkers.append(item)

        # Sort greens numerically
        self.greens.sort(key=lambda x: int(x['assigned_ref']) if x['assigned_ref'].isdigit() else 99)

        # 4. START POSITION: Green 1
        if self.greens:
            self.user_lon, self.user_lat = self.greens[0]['centroid']
        else:
            sample = list(self.nodes.values())[0]
            self.user_lon, self.user_lat = sample[0], sample[1]

        # 5. Setup Interactive Plot
        self.fig, self.ax = plt.subplots(figsize=(10, 10), facecolor='#1e272e')
        self.fig.canvas.manager.set_window_title(f'Caddie Live v3 - {os.path.basename(json_path)}')
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        
        self.update_logic()
        print("\n🎮 PRECISION MODE ACTIVE")
        print(f"-> Arrow Keys: Move (~2 yards per tap)")
        print(f"-> 'N': Jump to Next Hole | 'P': Jump to Prev Hole")
        plt.show()

    def get_distance(self, lat1, lon1, lat2, lon2):
        R = 6371000 
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi, dlambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        return (R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))) * 1.09361

    def get_centroid(self, item):
        coords = [self.nodes[nid] for nid in item.get('nodes', []) if nid in self.nodes]
        if not coords: return None
        return (sum(c[0] for c in coords) / len(coords), sum(c[1] for c in coords) / len(coords))

    def get_current_fairway(self):
        for fairway in self.fairways:
            path_coords = [self.nodes[nid] for nid in fairway['nodes'] if nid in self.nodes]
            if len(path_coords) >= 3:
                if Path(path_coords).contains_point((self.user_lon, self.user_lat)):
                    return fairway
        return None

    def on_key(self, event):
        # Micro-Movement
        if event.key == 'up': self.user_lat += self.move_step
        elif event.key == 'down': self.user_lat -= self.move_step
        elif event.key == 'left': self.user_lon -= self.move_step
        elif event.key == 'right': self.user_lon += self.move_step
        
        # Teleport
        elif event.key == 'n':
            self.current_hole_index = (self.current_hole_index + 1) % len(self.greens)
            self.user_lon, self.user_lat = self.greens[self.current_hole_index]['centroid']
        elif event.key == 'p':
            self.current_hole_index = (self.current_hole_index - 1) % len(self.greens)
            self.user_lon, self.user_lat = self.greens[self.current_hole_index]['centroid']
        
        self.update_logic()

    def update_logic(self):
        self.ax.clear()
        self.ax.set_facecolor('#2f3640')
        
        current_fairway = self.get_current_fairway()
        target_green = None
        title_text = ""

        closest_green = None
        min_dist = float('inf')
        for g in self.greens:
            dist = self.get_distance(self.user_lat, self.user_lon, g['centroid'][1], g['centroid'][0])
            if dist < min_dist:
                min_dist = dist
                closest_green = g

        if current_fairway:
            self.on_fairway = True
            self.last_known_hole = closest_green['assigned_ref'] if closest_green else "Unknown"
            title_text = f"⛳️ ON HOLE {self.last_known_hole} | {int(min_dist)} YARDS"
            target_green = closest_green
        else:
            self.on_fairway = False
            title_text = f"⚠️ OFF OF HOLE {self.last_known_hole}"

        # Render Bunkers
        for b in self.bunkers:
            b_coords = [self.nodes[nid] for nid in b['nodes'] if nid in self.nodes]
            if b_coords: self.ax.fill(*zip(*b_coords), color='#fbc531', alpha=0.5, zorder=1)

        # Render All Fairways (Faded)
        for f in self.fairways:
            f_coords = [self.nodes[nid] for nid in f['nodes'] if nid in self.nodes]
            if f_coords:
                is_active = (f == current_fairway)
                self.ax.fill(*zip(*f_coords), color='#4cd137', alpha=0.9 if is_active else 0.1, zorder=2)

        # Render All Greens
        for g in self.greens:
            is_target = (g == closest_green and self.on_fairway)
            g_coords = [self.nodes[nid] for nid in g['nodes'] if nid in self.nodes]
            if g_coords:
                self.ax.fill(*zip(*g_coords), color='#006266', alpha=1.0 if is_target else 0.2, zorder=3)

        # User Marker
        self.ax.scatter([self.user_lon], [self.user_lat], color='#e84118', s=200, edgecolor='white', zorder=10)

        # Camera Zoom
        if self.on_fairway and target_green:
            gx, gy = target_green['centroid']
            pad = 0.002
            self.ax.set_xlim(min(self.user_lon, gx) - pad, max(self.user_lon, gx) + pad)
            self.ax.set_ylim(min(self.user_lat, gy) - pad, max(self.user_lat, gy) + pad)
        else:
            pad = 0.004
            self.ax.set_xlim(self.user_lon - pad, self.user_lon + pad)
            self.ax.set_ylim(self.user_lat - pad, self.user_lat + pad)

        self.ax.set_title(title_text, color='white', fontsize=18, fontweight='bold')
        self.ax.axis('off')
        self.fig.canvas.draw()

if __name__ == "__main__":
    DATA_DIR = 'course_data'
    available_files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.json')])
    
    print("\n--- GOLF CADDIE: SELECT COURSE ---")
    for idx, filename in enumerate(available_files):
        print(f"[{idx}] {filename}")

    try:
        choice = int(input("\nEnter the number of the course: "))
        selected_path = os.path.join(DATA_DIR, available_files[choice])
        ProximityCaddie(selected_path)
    except:
        print("❌ Invalid selection.")