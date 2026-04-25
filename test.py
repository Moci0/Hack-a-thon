import requests
import json
import os
import time
import re

# Configuration
INPUT_FILE = 'all_courses_export.txt'
OUTPUT_DIR = 'course_data'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def fetch_osm_data(lat, lon, course_name):
    url = "https://overpass-api.de/api/interpreter"
    headers = {
        'User-Agent': 'GolfCaddieApp_Hackathon/1.0',
        'Accept': 'application/json'
    }
    
    # Radius of 1500m to catch the whole course
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
        else:
            return None
    except Exception as e:
        print(f"Error fetching {course_name}: {e}")
        return None

def parse_custom_txt(file_path):
    """Parses your specific txt format by finding JSON blocks between braces."""
    courses = []
    with open(file_path, 'r') as f:
        content = f.read()
        
    # Use regex to find every valid JSON block {} in the file
    json_blocks = re.findall(r'(\{.*?\})', content, re.DOTALL)
    
    for block in json_blocks:
        try:
            course_data = json.loads(block)
            courses.append(course_data)
        except json.JSONDecodeError:
            continue
    return courses

def main():
    print(f"Reading {INPUT_FILE}...")
    courses = parse_custom_txt(INPUT_FILE)
    
    print(f"Found {len(courses)} courses in file.")

    for course in courses:
        c_id = course.get('id', 'unknown')
        name = course.get('course_name', 'Unknown_Course')
        loc = course.get('location', {})
        lat = loc.get('latitude')
        lon = loc.get('longitude')

        # Check if we already have this data to save time/API hits
        filename = f"{OUTPUT_DIR}/course_{c_id}.json"
        if os.path.exists(filename):
            print(f"⏩ Skipping {name} (File already exists)")
            continue

        if lat and lon:
            print(f"📡 Querying OSM for: {name}...")
            data = fetch_osm_data(lat, lon, name)
            
            if data and data.get('elements'):
                with open(filename, 'w') as out:
                    json.dump(data, out, indent=4)
                print(f"✅ Saved to {filename}")
            else:
                print(f"ℹ️  No detailed map data for {name} in OpenStreetMap yet.")
            
            # API Courtesy Sleep
            time.sleep(2) 

if __name__ == "__main__":
    main()