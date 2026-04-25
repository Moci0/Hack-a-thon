import json
import matplotlib.pyplot as plt
import os
import sys

# Configuration
INPUT_DIR = 'course_data'
OUTPUT_DIR = 'exported_maps_with_ids'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def get_centroid(nodes, item):
    """Calculates the average center of a way for label placement."""
    way_nodes = item.get('nodes', [])
    coords = [nodes[nid] for nid in way_nodes if nid in nodes]
    if not coords: return None
    avg_lon = sum(c[0] for c in coords) / len(coords)
    avg_lat = sum(c[1] for c in coords) / len(coords)
    return (avg_lon, avg_lat)

def draw_and_save_with_ids(json_path, output_path):
    with open(json_path, 'r') as f:
        try:
            data = json.load(f)
        except:
            return False

    # 1. Map all Nodes
    nodes = {item['id']: (item['lon'], item['lat']) for item in data['elements'] if item['type'] == 'node'}
    if not nodes: return False

    # 2. Setup Plot
    plt.figure(figsize=(15, 15), facecolor='#1e272e') # Larger size for better ID legibility
    ax = plt.gca()
    ax.set_facecolor('#2f3640')
    
    found_features = False

    # 3. Process Ways
    for item in data['elements']:
        if item['type'] == 'way':
            tags = item.get('tags', {})
            g_type = tags.get('golf') or tags.get('leisure')
            way_id = str(item['id'])
            
            way_nodes = item.get('nodes', [])
            coords = [nodes[node_id] for node_id in way_nodes if node_id in nodes]
            
            if not coords: continue
            x, y = zip(*coords)
            
            # Styling
            color = None
            if g_type == 'fairway': color = '#4cd137'
            elif g_type == 'green': color = '#006266'
            elif g_type == 'bunker': color = '#fbc531'
            elif g_type == 'water_hazard' or tags.get('natural') == 'water': color = '#00a8ff'
            
            if color:
                found_features = True
                plt.fill(x, y, color=color, alpha=0.7, zorder=2)
                
                # --- NEW: ID LABELING LOGIC ---
                if g_type in ['fairway', 'green']:
                    cx, cy = get_centroid(nodes, item)
                    # Label the ID in white with a small font
                    # Greens get a slightly different color to distinguish them
                    text_col = 'white' if g_type == 'fairway' else '#00d2d3'
                    plt.text(cx, cy, way_id, color=text_col, fontsize=7, 
                             ha='center', va='center', weight='bold', zorder=10,
                             bbox=dict(facecolor='black', alpha=0.4, edgecolor='none', pad=1))

    if not found_features:
        plt.close()
        return False

    # 4. Final Formatting
    plt.axis('equal')
    plt.axis('off')
    course_id = os.path.basename(json_path).replace('course_', '').replace('.json', '')
    plt.title(f"ID Map for Course: {course_id}\n(Fairways = White IDs, Greens = Cyan IDs)", 
              color='white', fontsize=16, pad=20)
    
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='#1e272e')
    plt.close() 
    return True

def main():
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.json')]
    print(f"🚀 Exporting ID maps for {len(files)} courses...")
    
    for i, filename in enumerate(files):
        json_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename.replace('.json', '_ids.png'))
        
        if draw_and_save_with_ids(json_path, output_path):
            print(f"✅ [{i+1}/{len(files)}] Generated: {output_path}")
        else:
            print(f"⏩ [{i+1}/{len(files)}] Skipped: {filename}")

    print(f"\n✨ DONE! Open the '{OUTPUT_DIR}' folder to see the IDs.")

if __name__ == "__main__":
    main()