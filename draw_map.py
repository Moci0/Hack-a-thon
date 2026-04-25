import json
import matplotlib.pyplot as plt

def draw_golf_map(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    # 1. Create a lookup dictionary for nodes {id: (lat, lon)}
    nodes = {item['id']: (item['lon'], item['lat']) for item in data['elements'] if item['type'] == 'node'}

    plt.figure(figsize=(10, 10))
    
    found_features = False

    # 2. Iterate through "ways" (the shapes)
    for item in data['elements']:
        if item['type'] == 'way':
            tags = item.get('tags', {})
            golf_type = tags.get('golf')
            hole_ref = tags.get('ref', 'Unknown')

            # We want to draw fairways, greens, and hole paths
            if golf_type in ['fairway', 'green', 'hole', 'tee']:
                found_features = True
                
                # Get the coordinates for every node in this way
                way_nodes = item.get('nodes', [])
                x = [nodes[node_id][0] for node_id in way_nodes if node_id in nodes]
                y = [nodes[node_id][1] for node_id in way_nodes if node_id in nodes]

                # Choose color based on type
                color = 'green'
                if golf_type == 'fairway': color = '#2ecc71' # Light Green
                if golf_type == 'green': color = '#27ae60'   # Dark Green
                if golf_type == 'hole': color = 'blue'        # Path line
                
                # Plot the shape
                plt.plot(x, y, color=color, linewidth=1)
                plt.fill(x, y, color=color, alpha=0.3) # Fill the shape with color
                
                # Label the hole number if available
                if hole_ref != 'Unknown' and x and y:
                    plt.text(x[0], y[0], f"Hole {hole_ref}", fontsize=9)

    if not found_features:
        print("No fairway or hole shapes found in this JSON file.")
        return

    # Clean up the map appearance
    plt.axis('equal') # Keeps the course from looking stretched
    plt.title("Golf Course Vector Map")
    plt.xlabel("Longitude") 
    plt.ylabel("Latitude")
    plt.show()

if __name__ == "__main__":
    # Run this on the output file you generated earlier
    draw_golf_map('test_output.json')