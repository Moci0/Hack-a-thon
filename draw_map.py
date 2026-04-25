import json
import matplotlib.pyplot as plt
import sys
import os

def draw_golf_map(json_file):
    if not os.path.exists(json_file):
        print(f"❌ File {json_file} not found.")
        return

    with open(json_file, 'r') as f:
        data = json.load(f)

    # 1. Map all Nodes (The dots)
    nodes = {item['id']: (item['lon'], item['lat']) for item in data['elements'] if item['type'] == 'node'}

    plt.figure(figsize=(12, 12), facecolor='#2c3e50') # Dark background for the app feel
    ax = plt.gca()
    ax.set_facecolor('#27ae60') # Grass green background
    
    found_features = False

    # 2. Process Ways (The shapes)
    for item in data['elements']:
        if item['type'] == 'way':
            tags = item.get('tags', {})
            golf_type = tags.get('golf') or tags.get('leisure')
            
            way_nodes = item.get('nodes', [])
            coords = [nodes[node_id] for node_id in way_nodes if node_id in nodes]
            
            if not coords: continue
            
            x, y = zip(*coords)
            
            # STYLING RULES
            color = None
            alpha = 0.6
            zorder = 1
            
            if golf_type == 'fairway':
                color = '#2ecc71' # Bright Green
                zorder = 2
            elif golf_type == 'green':
                color = '#006400' # Darker Green
                zorder = 4
            elif golf_type == 'bunker':
                color = '#f1c40f' # Sand Yellow
                zorder = 3
                alpha = 0.9
            elif golf_type == 'water_hazard' or tags.get('natural') == 'water':
                color = '#3498db' # Water Blue
                zorder = 3
            elif golf_type == 'tee':
                color = '#ffffff' # White Tee Box
                zorder = 4
            elif golf_type == 'hole': # The path line
                plt.plot(x, y, color='white', linestyle='--', linewidth=1, alpha=0.5, zorder=5)
                continue

            if color:
                found_features = True
                plt.fill(x, y, color=color, alpha=alpha, zorder=zorder, edgecolor='none')
                
                # Label Hole Numbers
                if 'ref' in tags:
                    plt.text(x[0], y[0], tags['ref'], color='white', fontsize=10, weight='bold', zorder=6)

    if not found_features:
        print(f"⚠️ No drawable shapes in {json_file}. The data might be stored as 'Relations'.")
        return

    # 3. Final Formatting
    plt.axis('equal')
    plt.axis('off') # Hide lat/lon numbers for a clean app look
    course_name = json_file.split('/')[-1]
    plt.title(f"Vector Map: {course_name}", color='white', pad=20, fontsize=15)
    
    print(f"🎨 Rendering map for {json_file}...")
    plt.show()

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else 'course_data/course_26741.json'
    draw_golf_map(target)