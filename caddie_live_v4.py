import json
import math
import matplotlib.pyplot as plt
from matplotlib.path import Path
import os
import sys

class ProCaddieSim:
    def __init__(self, json_path):
        self.json_path = json_path
        self.last_known_hole = "None"
        self.on_fairway = False
        self.current_hole_index = 0 
        self.move_step = 0.00005 
        self.speed_multiplier = 1.0
        
        with open(json_path, 'r') as f:
            self.data = json.load(f)
        self.nodes = {item['id']: (item['lon'], item['lat']) for item in self.data['elements'] if item['type'] == 'node'}
        
        self.fairways = {} 
        self.greens = {}   
        self.bunkers = []

        # 1. First Pass: Find all features
        temp_greens = []
        temp_fairways = []
        for item in self.data['elements']:
            if item['type'] == 'way':
                tags = item.get('tags', {})
                g_type = tags.get('golf')
                if g_type == 'green': temp_greens.append(item)
                elif g_type == 'fairway': temp_fairways.append(item)
                elif g_type == 'bunker': self.bunkers.append(item)

        if not temp_greens:
            print("❌ This course data has no 'greens' mapped. Try another course.")
            return

        # 2. Second Pass: Assign IDs to Greens and Fairways
        # If 'ref' is missing, we assign numbers 1, 2, 3...
        for idx, g in enumerate(temp_greens):
            ref = g.get('tags', {}).get('ref', str(idx + 1))
            g['assigned_ref'] = ref
            g['centroid'] = self.get_centroid(g)
            self.greens[ref] = g

        for idx, f in enumerate(temp_fairways):
            ref = f.get('tags', {}).get('ref')
            if not ref:
                # Match fairway to nearest green if ref is missing
                f_center = self.get_centroid(f)
                closest_ref = "Unknown"
                min_d = float('inf')
                for g_ref, g_obj in self.greens.items():
                    d = self.get_distance(f_center[1], f_center[0], g_obj['centroid'][1], g_obj['centroid'][0])
                    if d < min_d:
                        min_d = d
                        closest_ref = g_ref
                ref = closest_ref
            self.fairways[ref] = f

        self.sorted_refs = sorted(self.greens.keys(), key=lambda x: int(x) if x.isdigit() else 99)
        
        # Start at Hole 1
        self.teleport_to_tee(self.sorted_refs[0])

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

    def teleport_to_tee(self, hole_ref):
        green = self.greens.get(hole_ref)
        fairway = self.fairways.get(hole_ref)
        if not green or not fairway:
            if green: self.user_lon, self.user_lat = green['centroid']
            return

        gx, gy = green['centroid']
        max_dist = -1
        tee_coords = (gx, gy)
        for nid in fairway['nodes']:
            if nid in self.nodes:
                lon, lat = self.nodes[nid]
                d = self.get_distance(lat, lon, gy, gx)
                if d > max_dist:
                    max_dist = d
                    tee_coords = (lon, lat)
        self.user_lon, self.user_lat = tee_coords

    def on_key(self, event):
        step = self.move_step * self.speed_multiplier
        if event.key == 'up': self.user_lat += step
        elif event.key == 'down': self.user_lat -= step
        elif event.key == 'left': self.user_lon -= step
        elif event.key == 'right': self.user_lon += step
        elif event.key in ['+', '=']: self.speed_multiplier *= 1.5
        elif event.key in ['-', '_']: self.speed_multiplier /= 1.5
        elif event.key == 'n':
            self.current_hole_index = (self.current_hole_index + 1) % len(self.sorted_refs)
            self.teleport_to_tee(self.sorted_refs[self.current_hole_index])
        elif event.key == 'p':
            self.current_hole_index = (self.current_hole_index - 1) % len(self.sorted_refs)
            self.teleport_to_tee(self.sorted_refs[self.current_hole_index])
        self.update_logic()

    def update_logic(self):
        self.ax.clear()
        self.ax.set_facecolor('#2f3640')
        
        current_fairway_ref = None
        for ref, f in self.fairways.items():
            path_coords = [self.nodes[nid] for nid in f['nodes'] if nid in self.nodes]
            if len(path_coords) >= 3 and Path(path_coords).contains_point((self.user_lon, self.user_lat)):
                current_fairway_ref = ref
                break

        target_green = self.greens.get(current_fairway_ref)
        if target_green:
            self.last_known_hole = current_fairway_ref
            gx, gy = target_green['centroid']
            dist = self.get_distance(self.user_lat, self.user_lon, gy, gx)
            title = f"⛳️ HOLE {current_fairway_ref} | 🚩 {int(dist)} YARDS"
        else:
            title = f"⚠️ OFF OF HOLE {self.last_known_hole}"

        for b in self.bunkers:
            b_coords = [self.nodes[nid] for nid in b['nodes'] if nid in self.nodes]
            if b_coords: self.ax.fill(*zip(*b_coords), color='#fbc531', alpha=0.5, zorder=1)

        for ref, f in self.fairways.items():
            f_coords = [self.nodes[nid] for nid in f['nodes'] if nid in self.nodes]
            if f_coords:
                self.ax.fill(*zip(*f_coords), color='#4cd137', alpha=0.9 if ref == current_fairway_ref else 0.1, zorder=2)

        for ref, g in self.greens.items():
            g_coords = [self.nodes[nid] for nid in g['nodes'] if nid in self.nodes]
            if g_coords:
                self.ax.fill(*zip(*g_coords), color='#006266', alpha=1.0 if ref == current_fairway_ref else 0.2, zorder=3)

        self.ax.scatter([self.user_lon], [self.user_lat], color='#e84118', s=200, edgecolor='white', zorder=10)

        # Camera
        zoom_target = target_green['centroid'] if target_green else (self.user_lon, self.user_lat)
        pad = 0.002 if target_green else 0.004
        self.ax.set_xlim(min(self.user_lon, zoom_target[0]) - pad, max(self.user_lon, zoom_target[0]) + pad)
        self.ax.set_ylim(min(self.user_lat, zoom_target[1]) - pad, max(self.user_lat, zoom_target[1]) + pad)

        self.ax.set_title(f"{title} (Spd: {self.speed_multiplier:.1f}x)", color='white', fontsize=16, fontweight='bold')
        self.ax.axis('off')
        self.fig.canvas.draw()

if __name__ == "__main__":
    DATA_DIR = 'course_data'
    files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.json')])
    for idx, f in enumerate(files): print(f"[{idx}] {f}")
    choice = int(input("\nSelect course: "))
    ProCaddieSim(os.path.join(DATA_DIR, files[choice]))