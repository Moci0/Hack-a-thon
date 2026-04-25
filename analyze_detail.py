import json
import os

# Configuration
DATA_DIR = 'course_data'

def analyze_courses():
    if not os.path.exists(DATA_DIR):
        print(f"❌ Folder '{DATA_DIR}' not found. Run test.py first!")
        return

    report = []
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]

    if not files:
        print("ℹ️ No JSON files found in course_data.")
        return

    print(f"🔎 Analyzing {len(files)} courses for map detail...\n")

    for filename in files:
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'r') as f:
            try:
                data = json.load(f)
            except:
                continue

            elements = data.get('elements', [])
            
            # Count specific high-value features
            stats = {
                'id': filename.replace('course_', '').replace('.json', ''),
                'fairways': 0,
                'bunkers': 0,
                'greens': 0,
                'holes': 0,
                'total_features': 0,
                'file_size_kb': round(os.path.getsize(filepath) / 1024, 2)
            }

            for item in elements:
                if 'tags' in item:
                    g = item['tags'].get('golf')
                    if g == 'fairway': stats['fairways'] += 1
                    if g == 'bunker': stats['bunkers'] += 1
                    if g == 'green': stats['greens'] += 1
                    if g == 'hole': stats['holes'] += 1
            
            stats['total_features'] = stats['fairways'] + stats['bunkers'] + stats['greens'] + stats['holes']
            report.append(stats)

    # Sort by total features (highest detail first)
    report.sort(key=lambda x: x['total_features'], reverse=True)

    # Display results in a table format
    print(f"{'Course ID':<12} | {'Fairways':<8} | {'Bunkers':<8} | {'Greens':<8} | {'Size (KB)':<10}")
    print("-" * 60)
    
    for r in report[:15]:  # Show top 15 most detailed
        print(f"{r['id']:<12} | {r['fairways']:<8} | {r['bunkers']:<8} | {r['greens']:<8} | {r['file_size_kb']:<10}")

    if report:
        best = report[0]
        print(f"\n🏆 PRO-TIP: Course {best['id']} is your best demo candidate.")
        print(f"Run: python3 draw_map.py course_data/course_{best['id']}.json")

if __name__ == "__main__":
    analyze_courses()

    