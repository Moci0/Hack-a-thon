import json
import math
import matplotlib.pyplot as plt
from matplotlib.path import Path
import os
import sys
import urllib.request
import urllib.error

# ============================================================
# MANUAL MAPPING AREA: CLOVERNOOK CC (4617)
# This links specific OpenStreetMap IDs to Hole Numbers
# ============================================================
CLOVERNOOK_MAP = {
    # Hole 1
    "923574499": "1", "923574498": "1", "923561394": "1",
    # Hole 2
    "923561389": "2", "923561393": "2",
    # Hole 3
    "939088695": "3", "923561382": "3", "923561383": "3", "923561392": "3",
    # Hole 4
    "923570971": "4", "923561395": "4",
    # Hole 5
    "923570972": "5", "923570973": "5", "923561399": "5",
    # Hole 6
    "923570974": "6", "923561400": "6",
    # Hole 7
    "923570975": "7", "923570976": "7", "923561404": "7",
    # Hole 8
    "923570978": "8", "923561405": "8",
    # Hole 9
    "923570977": "9", "923561401": "9",
    # Hole 10
    "923570979": "10", "923570980": "10", "923570966": "10",
    # Hole 11
    "923580089": "11", "923570968": "11",
    # Hole 12
    "923570970": "12",
    # Hole 13
    "923571155": "13", "923561397": "13",
    # Hole 14
    "923573807": "14", "923561398": "14",
    # Hole 15
    "923574497": "15", "923561396": "15",
    # Hole 16
    "923570984": "16", "923561402": "16",
    # Hole 17
    "923570982": "17", "923578903": "17", "923570967": "17",
    # Hole 18
    "923570981": "18", "923570969": "18"
}

MANUAL_HOLE_MAP = {"4617": CLOVERNOOK_MAP}
SHOW_IDS = False  # Set to True if you need to debug more IDs

class ProCaddieSim:
    def __init__(self, json_path):
        self.json_path = json_path
        self.course_id = os.path.basename(json_path).replace('course_', '').replace('.json', '')
        self.last_known_hole = "1" # Default to 1
        self.move_step = 0.00005 
        self.speed_multiplier = 1.0
        self.dashboard_mode = '--dashboard' in sys.argv or os.environ.get('DASHBOARD_MODE') == '1'
        self.dashboard_url = os.environ.get('DASHBOARD_URL', 'http://127.0.0.1:5000/api/live/update')
        self.live_distance = None
        
        # Load JSON Data
        with open(json_path, 'r') as f:
            self.data = json.load(f)
        
        # Map IDs to Lon/Lat
        self.nodes = {item['id']: (item['lon'], item['lat']) for item in self.data['elements'] if item['type'] == 'node'}
        
        self.fairways = {} # Map ref -> List of fairway ways
        self.greens = {}   # Map ref -> Way
        self.bunkers = []

        course_overrides = MANUAL_HOLE_MAP.get(self.course_id, {})

        # Parse Course Elements
        for item in self.data['elements']:
            if item['type'] == 'way':
                tags = item.get('tags', {})
                g_type = tags.get('golf')
                osm_id = str(item['id'])
                h_ref = course_overrides.get(osm_id) or tags.get('ref')

                if g_type == 'green' and h_ref:
                    item['centroid'] = self.get_centroid(item)
                    self.greens[h_ref] = item
                elif g_type == 'fairway' and h_ref:
                    if h_ref not in self.fairways: self.fairways[h_ref] = []
                    self.fairways[h_ref].append(item)
                elif g_type == 'bunker':
                    self.bunkers.append(item)

        self.sorted_refs = sorted(self.greens.keys(), key=lambda x: int(x) if x.isdigit() else 99)
        self.current_hole_index = 0
        
        # Start at Tee of Hole 1
        if self.sorted_refs:
            self.teleport_to_tee(self.sorted_refs[0])
        else:
            print("⚠️ No data found for this course!")
            sys.exit()

        # Init Figure
        self.fig, self.ax = plt.subplots(figsize=(10, 10), facecolor='#1e272e')
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.update_logic()
        plt.show()

    def get_distance(self, lat1, lon1, lat2, lon2):
        """Calculates distance in Yards using the Haversine Formula."""
        R = 6371000 # Earth radius in meters
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi, dlambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        meters = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return meters * 1.09361

    def get_centroid(self, item):
        coords = [self.nodes[nid] for nid in item.get('nodes', []) if nid in self.nodes]
        if not coords: return None
        return (sum(c[0] for c in coords) / len(coords), sum(c[1] for c in coords) / len(coords))

    def push_dashboard_state(self, status=None):
        if not self.dashboard_mode:
            return
        payload = {
            'course_id': self.course_id,
            'hole': self.last_known_hole,
            'distance': self.live_distance,
            'speed': f'{self.speed_multiplier:.1f}x',
            'status': status or 'Simulator running',
            'user_lon': self.user_lon,
            'user_lat': self.user_lat
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(self.dashboard_url, data=data, headers={'Content-Type': 'application/json'})
        try:
            urllib.request.urlopen(req, timeout=1)
        except Exception:
            pass

    def teleport_to_tee(self, hole_ref):
        """Places user at the fairway point furthest from the green."""
        green = self.greens.get(hole_ref)
        fairways = self.fairways.get(hole_ref, [])
        if not green or not fairways: return

        gx, gy = green['centroid']
        max_dist = -1
        tee_coords = (gx, gy)

        for fairway in fairways:
            for nid in fairway['nodes']:
                if nid in self.nodes:
                    lon, lat = self.nodes[nid]
                    d = self.get_distance(lat, lon, gy, gx)
                    if d > max_dist:
                        max_dist = d
                        tee_coords = (lon, lat)
        self.user_lon, self.user_lat = tee_coords
        self.last_known_hole = hole_ref

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
        
        # 1. Detection Logic
        current_fairway_ref = None
        for ref, f_list in self.fairways.items():
            for f in f_list:
                path_coords = [self.nodes[nid] for nid in f['nodes'] if nid in self.nodes]
                if len(path_coords) >= 3 and Path(path_coords).contains_point((self.user_lon, self.user_lat)):
                    current_fairway_ref = ref
                    break

        if current_fairway_ref:
            self.last_known_hole = current_fairway_ref

        # 2. Yardage Logic (Always from last known green)
        target_green = self.greens.get(self.last_known_hole)
        if target_green:
            gx, gy = target_green['centroid']
            dist = self.get_distance(self.user_lat, self.user_lon, gy, gx)
            self.live_distance = int(dist)
            if current_fairway_ref:
                title = f"⛳️ HOLE {current_fairway_ref} | 🚩 {int(dist)} YARDS"
            else:
                title = f"⚠️ OFF HOLE {self.last_known_hole} | 🚩 {int(dist)} YDS TO PIN"
        else:
            title = "🌲 FIND A FAIRWAY"
            self.live_distance = None

        self.push_dashboard_state(status=title)

        # 3. Draw Course
        for b in self.bunkers:
            coords = [self.nodes[nid] for nid in b['nodes'] if nid in self.nodes]
            if coords: self.ax.fill(*zip(*coords), color='#fbc531', alpha=0.5, zorder=1)

        for ref, f_list in self.fairways.items():
            is_active = (ref == self.last_known_hole)
            for f in f_list:
                f_coords = [self.nodes[nid] for nid in f['nodes'] if nid in self.nodes]
                if f_coords:
                    self.ax.fill(*zip(*f_coords), color='#4cd137', alpha=0.9 if is_active else 0.1, zorder=2)

        for ref, g in self.greens.items():
            is_target = (ref == self.last_known_hole)
            g_coords = [self.nodes[nid] for nid in g['nodes'] if nid in self.nodes]
            if g_coords:
                self.ax.fill(*zip(*g_coords), color='#006266', alpha=1.0 if is_target else 0.2, zorder=3)

        self.ax.scatter([self.user_lon], [self.user_lat], color='#e84118', s=200, edgecolor='white', zorder=10)

        # 4. Camera Zoom
        zoom_target = target_green['centroid'] if target_green else (self.user_lon, self.user_lat)
        pad = 0.0015
        self.ax.set_xlim(min(self.user_lon, zoom_target[0]) - pad, max(self.user_lon, zoom_target[0]) + pad)
        self.ax.set_ylim(min(self.user_lat, zoom_target[1]) - pad, max(self.user_lat, zoom_target[1]) + pad)

        self.ax.set_title(f"{title} (Speed: {self.speed_multiplier:.1f}x)", color='white', fontsize=16, fontweight='bold')
        self.ax.axis('off')
        self.fig.canvas.draw()

if __name__ == "__main__":
    DATA_DIR = 'course_data'
    available_files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.json')])
    print("\n--- GOLF CADDIE PRO: SELECT COURSE ---")
    for idx, f in enumerate(available_files): print(f"[{idx}] {f}")
    try:
        choice = int(input("\nSelect course: "))
        ProCaddieSim(os.path.join(DATA_DIR, available_files[choice]))
    except:
        print("❌ Invalid selection.")