import json
import math
import matplotlib.pyplot as plt
import os

# --- CONFIG ---
COURSE_ID = "26741"
JSON_FILE = f'course_data/course_{COURSE_ID}.json'

# Simulated GPS for Forest of Dean (Hole 1 area)
SIM_LAT = 51.7919
SIM_LON = -2.6112

def get_distance(lat1, lon1, lat2, lon2):
    R = 6371000 
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return (R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))) * 1.09361

def get_centroid(nodes, item):
    if item['type'] == 'node': return (item['lon'], item['lat'])
    coords = [nodes[nid] for nid in item.get('nodes', []) if nid in nodes]
    if not coords: return None
    return (sum(c[0] for c in coords) / len(coords), sum(c[1] for c in coords) / len(coords))

def run_live_caddie(json_path, u_lat, u_lon):
    if not os.path.exists(json_path):
        print(f"❌ File not found: {json_path}")
        return

    with open(json_path, 'r') as f:
        data = json.load(f)

    nodes = {item['id']: (item['lon'], item['lat']) for item in data['elements'] if item['type'] == 'node'}
    if not nodes:
        print("❌ No coordinate data in JSON.")
        return

    active_hole_ref = None
    min_dist = float('inf')
    target_green_coords = None

    # Search for the closest green
    for item in data['elements']:
        tags = item.get('tags', {})
        if tags.get('golf') == 'green':
            center = get_centroid(nodes, item)
            if center:
                dist = get_distance(u_lat, u_lon, center[1], center[0])
                if dist < min_dist:
                    min_dist = dist
                    # Fallback to 'Unknown' if ref is missing
                    active_hole_ref = tags.get('ref', 'Unknown')
                    target_green_coords = center

    if not target_green_coords:
        # DIAGNOSTIC HINT
        sample = list(nodes.values())[0]
        print(f"❌ No greens found. Course is at ({sample[1]}, {sample[0]})")
        print(f"Check your SIM_LAT/SIM_LON in the code.")
        return

    print(f"⛳️ Locked onto Hole {active_hole_ref}")
    print(f"🚩 Distance to Green: {int(min_dist)} yards")

    plt.figure(figsize=(10, 12), facecolor='#1e272e')
    ax = plt.gca()
    ax.set_facecolor('#2f3640') 

    # Draw everything that belongs to this hole
    for item in data['elements']:
        if item['type'] == 'way':
            tags = item.get('tags', {})
            g_type = tags.get('golf')
            
            # Draw it if it's the current hole OR it's a general bunker/fairway
            # Some fairways aren't numbered, so we draw all nearby ones
            if tags.get('ref') == active_hole_ref or g_type in ['fairway', 'bunker', 'green']:
                way_nodes = item.get('nodes', [])
                coords = [nodes[node_id] for node_id in way_nodes if node_id in nodes]
                if not coords: continue
                x, y = zip(*coords)

                color = '#4cd137' if g_type == 'fairway' else '#006266' if g_type == 'green' else '#fbc531'
                plt.fill(x, y, color=color, alpha=0.9, zorder=2)

    # User Marker
    plt.scatter([u_lon], [u_lat], color='#e84118', s=250, edgecolor='white', zorder=10)

    # Dynamic Zoom: Frame the player and the green
    padding = 0.003
    plt.xlim(min(u_lon, target_green_coords[0]) - padding, max(u_lon, target_green_coords[0]) + padding)
    plt.ylim(min(u_lat, target_green_coords[1]) - padding, max(u_lat, target_green_coords[1]) + padding)

    plt.title(f"LIVE CADDIE - HOLE {active_hole_ref}\n{int(min_dist)} YARDS", color='white', fontsize=18, pad=20)
    plt.axis('off')
    plt.show()

if __name__ == "__main__":
    run_live_caddie(JSON_FILE, SIM_LAT, SIM_LON)