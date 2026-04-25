import json
import matplotlib.pyplot as plt
import os
import sys

# Configuration
INPUT_DIR = 'course_data'
OUTPUT_DIR = 'exported_maps'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def draw_and_save(json_path, output_path):
    with open(json_path, 'r') as f:
        try:
            data = json.load(f)
        except:
            return False

    # 1. Map all Nodes
    nodes = {item['id']: (item['lon'], item['lat']) for item in data['elements'] if item['type'] == 'node'}
    if not nodes: return False

    # 2. Setup Plot (Clear any previous data)
    plt.figure(figsize=(10, 10), facecolor='#1e272e')
    ax = plt.gca()
    ax.set_facecolor('#2f3640')
    
    found_features = False

    # 3. Process Ways
    for item in data['elements']:
        if item['type'] == 'way':
            tags = item.get('tags', {})
            g_type = tags.get('golf') or tags.get('leisure')
            
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
                plt.fill(x, y, color=color, alpha=0.8, zorder=2)

    if not found_features:
        plt.close()
        return False

    # 4. Final Formatting & Export
    plt.axis('equal')
    plt.axis('off')
    course_name = os.path.basename(json_path).replace('.json', '')
    plt.title(f"Course: {course_name}", color='white', fontsize=12)
    
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#1e272e')
    plt.close() # CRITICAL: Closes the plot memory so your computer doesn't lag
    return True

def main():
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.json')]
    print(f"🚀 Starting batch export of {len(files)} courses...")
    
    success_count = 0
    for i, filename in enumerate(files):
        json_path = os.path.join(INPUT_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, filename.replace('.json', '.png'))
        
        # Simple progress update
        if draw_and_save(json_path, output_path):
            success_count += 1
            print(f"[{i+1}/{len(files)}] ✅ Exported {filename}")
        else:
            print(f"[{i+1}/{len(files)}] ⏩ Skipped {filename} (No detail)")

    print(f"\n✨ Done! {success_count} maps are ready in the '{OUTPUT_DIR}' folder.")

if __name__ == "__main__":
    main()