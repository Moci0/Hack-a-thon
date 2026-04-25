import requests
import json
import os
import time

# Configuration
INPUT_FILE = 'all_courses_export.txt'
OUTPUT_DIR = 'course_data'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def fetch_osm_data(lat, lon, course_name):
    url = "https://overpass-api.de/api/interpreter"
    headers = {
        'User-Agent': 'GolfCaddieApp_Hackathon/2.0',
        'Accept': 'application/json'
    }
    
    query = f"""
    [out:json][timeout:60];
    (
      nwr["golf"~"hole|green|tee|fairway|bunker"](around:1500, {lat}, {lon});
      nwr["leisure"="golf_course"](around:1500, {lat}, {lon});
    );
    out body;
    >;
    out skel qt;
    """
    
    try:
        response = requests.get(url, params={'data': query}, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print("⚠️ Rate limited. Waiting 10 seconds...")
            time.sleep(10)
            return fetch_osm_data(lat, lon, course_name)
    except Exception as e:
        print(f"Error fetching {course_name}: {e}")
    return None

def parse_custom_txt(file_path):
    """Robustly extracts JSON objects by tracking brace depth."""
    courses = []
    with open(file_path, 'r') as f:
        content = f.read()

    start_idx = -1
    brace_count = 0
    
    for i, char in enumerate(content):
        if char == '{':
            if brace_count == 0:
                start_idx = i
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0 and start_idx != -1:
                json_str = content[start_idx:i+1]
                try:
                    courses.append(json.loads(json_str))
                except json.JSONDecodeError:
                    pass
    return courses

def main():
    print(f"Reading {INPUT_FILE}...")
    courses = parse_custom_txt(INPUT_FILE)
    print(f"Found {len(courses)} valid course objects in file.")

    if not courses:
        print("❌ Could not extract any JSON from the file. Check the format!")
        return

    # To test quickly, we only process the first few courses 
    # (Remove the [:10] later to do the whole file)
    for course in courses[:20]: 
        c_id = course.get('id', 'unknown')
        name = course.get('course_name', 'Unknown_Course')
        loc = course.get('location', {})
        lat = loc.get('latitude')
        lon = loc.get('longitude')

        filename = f"{OUTPUT_DIR}/course_{c_id}.json"
        
        if lat and lon:
            print(f"📡 Querying: {name} ({lat}, {lon})")
            data = fetch_osm_data(lat, lon, name)
            
            if data and len(data.get('elements', [])) > 1:
                with open(filename, 'w') as out:
                    json.dump(data, out, indent=4)
                print(f"✅ Saved detail to {filename}")
            else:
                print(f"ℹ️  No detailed map data for {name}")
            
            time.sleep(1.5) 
        else:
            print(f"⏩ Skipping {name}: Missing coordinates.")

if __name__ == "__main__":
    main()