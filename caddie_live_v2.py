import json
import math
import matplotlib.pyplot as plt
from matplotlib.path import Path
import os

class IntegratedCaddie:
    def __init__(self, json_path, start_lat, start_lon):
        self.json_path = json_path
        self.user_lat = start_lat
        self.user_lon = start_lon
        self.last_hole_ref = None  # To track "Off of Hole X"
        self.on_fairway = False
        self.move_step = 0.0001 
        
        # Load and Index Data
        with open(json_path, 'r') as f:
            self.data = json.load(f)
        self.nodes = {item['id']: (item['lon'], item['lat']) for item in self.data['elements'] if item['type'] == 'node'}
        
        # Index fairways and greens by hole number for fast lookup
        self.fairways = {}
        self.greens = {}
        self.bunkers = []

        for item in self.data['elements']:
            if item['type'] == 'way':
                tags = item.get('tags', {})
                g_type = tags.get('golf')
                ref = tags.get('ref')
                
                if g_type == 'fairway' and ref:
                    self.fairways[ref] = item
                elif g_type == 'green' and ref:
                    self.greens[ref] = item
                elif g_type == 'bunker':
                    self.bunkers.append(item)

        # Setup Plot
        self.fig, self.ax = plt.subplots(figsize=(10, 10), facecolor='#1e272e')
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        
        self.update_logic()
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

    def check_fairway_boundary(self):
        """Checks which fairway the user is physically standing in."""
        for ref, item in self.fairways.items():
            path_coords = [self.nodes[nid] for nid in item['nodes'] if nid in self.nodes]
            if len(path_coords) >= 3:
                poly = Path(path_coords)
                if poly.contains_point((self.user_lon, self.user_lat)):
                    return ref
        return None

    def on_key(self, event):
        if event.key == 'up': self.user_lat += self.move_step
        elif event.key == 'down': self.user_lat -= self.move_step
        elif event.key == 'left': self.user_lon -= self.move_step
        elif event.key == 'right': self.user_lon += self.move_step
        self.update_logic()

    def update_logic(self):
        self.ax.clear()
        self.ax.set_facecolor('#2f3640')
        
        current_hole = self.check_fairway_boundary()
        title_text = ""
        
        if current_hole:
            self.on_fairway = True
            self.last_hole_ref = current_hole
            green = self.greens.get(current_hole)
            if green:
                gx, gy = self.get_centroid(green)
                dist = self.get_distance(self.user_lat, self.user_lon, gy, gx)
                title_text = f"⛳️ HOLE {current_hole} | {int(dist)} YARDS TO GREEN"
            else:
                title_text = f"⛳️ HOLE {current_hole} | GREEN DATA MISSING"
        else:
            self.on_fairway = False
            if self.last_hole_ref:
                title_text = f"⚠️ OFF OF HOLE {self.last_hole_ref}"
            else:
                title_text = "🌲 OFF FAIRWAY - FIND A TEE BOX"

        # DRAWING
        # 1. Draw Bunkers (always visible)
        for b in self.bunkers:
            coords = [self.nodes[nid] for nid in b['nodes'] if nid in self.nodes]
            if coords: self.ax.fill(*zip(*coords), color='#fbc531', alpha=0.6, zorder=1)

        # 2. Draw Active Fairway and Green
        if self.last_hole_ref:
            f_item = self.fairways.get(self.last_hole_ref)
            g_item = self.greens.get(self.last_hole_ref)
            
            if f_item:
                f_coords = [self.nodes[nid] for nid in f_item['nodes'] if nid in self.nodes]
                self.ax.fill(*zip(*f_coords), color='#4cd137', alpha=0.8, zorder=2)
            if g_item:
                g_coords = [self.nodes[nid] for nid in g_item['nodes'] if nid in self.nodes]
                self.ax.fill(*zip(*g_coords), color='#006266', zorder=3)

        # 3. User Marker
        self.ax.scatter([self.user_lon], [self.user_lat], color='#e84118', s=200, edgecolor='white', zorder=10)

        # 4. Smart View Port (Zoom)
        if self.on_fairway and current_hole in self.greens:
            gx, gy = self.get_centroid(self.greens[current_hole])
            pad = 0.002
            self.ax.set_xlim(min(self.user_lon, gx) - pad, max(self.user_lon, gx) + pad)
            self.ax.set_ylim(min(self.user_lat, gy) - pad, max(self.user_lat, gy) + pad)
        else:
            # Show broader area when off hole
            pad = 0.005
            self.ax.set_xlim(self.user_lon - pad, self.user_lon + pad)
            self.ax.set_ylim(self.user_lat - pad, self.user_lat + pad)

        self.ax.set_title(title_text, color='white', fontsize=16, fontweight='bold')
        self.ax.axis('off')
        self.fig.canvas.draw()

if __name__ == "__main__":
    # Launching for Forest of Dean (Course 26741)
    # Start coordinates inside Fairway #1
    IntegratedCaddie('course_data/course_26741.json', 51.7919, -2.6112)