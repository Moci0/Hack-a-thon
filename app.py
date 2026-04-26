from flask import Flask, request, jsonify, send_from_directory
import os
import time
import json
import subprocess
import shutil

app = Flask(__name__, static_folder='.', static_url_path='')

USER_STORE_FILE = 'users.json'

def load_user_store():
    if not os.path.exists(USER_STORE_FILE):
        return {'users': {}}
    try:
        with open(USER_STORE_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {'users': {}}


def save_user_store(store):
    with open(USER_STORE_FILE, 'w') as f:
        json.dump(store, f, indent=2)


def get_saved_user(email):
    if not email:
        return None
    store = load_user_store()
    return store.get('users', {}).get(email.lower())


def save_user_profile(user):
    if not user or not user.get('email'):
        return
    store = load_user_store()
    email = user['email'].lower()
    profile = store.get('users', {}).get(email, {})
    profile.update({
        'firstName': user.get('firstName', ''),
        'lastName': user.get('lastName', ''),
        'email': email,
        'handicap': user.get('handicap', ''),
        'clubs': user.get('clubs', state['clubs'])
    })
    if 'users' not in store:
        store['users'] = {}
    store['users'][email] = profile
    save_user_store(store)
    return profile


# Par data for courses
PAR_DATA = {
    "4617": [5, 4, 4, 3, 5, 3, 4, 3, 4, 4, 3, 4, 4, 3, 4, 5, 5, 4]  # Holes 1-18
}

def get_par_for_hole(course_id, hole):
    if course_id in PAR_DATA:
        pars = PAR_DATA[course_id]
        if isinstance(hole, str):
            if hole.isdigit():
                hole_num = int(hole) - 1
            else:
                return 4
        elif isinstance(hole, int):
            hole_num = hole - 1
        else:
            return 4
        if 0 <= hole_num < len(pars):
            return pars[hole_num]
    return 4  # default par


def get_cumulative_score(course_id, strokes_per_hole):
    total = 0
    for hole_str, strokes in strokes_per_hole.items():
        hole = int(hole_str)
        par = get_par_for_hole(course_id, hole)
        total += strokes - par
    return total


state = {
    'user': None,
    'clubs': {
        'Driver': 230,
        '3-Wood': 210,
        '5-Wood': 180,
        '5-Iron': 150,
        '6-Iron': 140,
        '7-Iron': 130,
        '8-Iron': 120,
        '9-Iron': 110,
        'Pitching Wedge': 100,
        'Sand Wedge': 80
    },
    'live': {
        'course_id': None,
        'hole': None,
        'distance': None,
        'speed': None,
        'status': 'Waiting for simulator...',
        'user_lon': None,
        'user_lat': None,
        'timestamp': None,
        'par': 4,
        'strokes': 0,
        'strokes_per_hole': {}
    }
}


@app.route('/')
def index():
    return send_from_directory('.', 'dashboard.html')


@app.route('/api/login', methods=['POST'])
def api_login():
    payload = request.json or {}
    user = {
        'firstName': payload.get('firstName', '').strip(),
        'lastName': payload.get('lastName', '').strip(),
        'email': payload.get('email', '').strip().lower(),
        'handicap': payload.get('handicap', '').strip()
    }

    if not user['firstName'] or not user['email']:
        return jsonify({'error': 'First name and email are required.'}), 400

    saved = get_saved_user(user['email'])
    if saved:
        state['user'] = saved
        if isinstance(saved.get('clubs'), dict) and saved['clubs']:
            state['clubs'] = saved['clubs']
    else:
        state['user'] = user
        state['user']['clubs'] = state['clubs']
        save_user_profile(state['user'])

    return jsonify({'message': 'User logged in.', 'user': state['user'], 'clubs': state['clubs']})


@app.route('/api/clubs', methods=['POST'])
def api_clubs():
    payload = request.json or {}
    clubs = payload.get('clubs', {})
    if not isinstance(clubs, dict) or not clubs:
        return jsonify({'error': 'Clubs data must be a non-empty object.'}), 400

    sanitized = {}
    for name, value in clubs.items():
        try:
            sanitized[name] = int(value)
        except (TypeError, ValueError):
            continue

    if not sanitized:
        return jsonify({'error': 'No valid club distances found.'}), 400

    state['clubs'] = sanitized
    if state['user'] and state['user'].get('email'):
        state['user']['clubs'] = state['clubs']
        save_user_profile(state['user'])

    return jsonify({'message': 'Club distances saved.', 'clubs': state['clubs']})


def recommend_club(distance_yards):
    if distance_yards is None:
        return None

    clubs = state['clubs']
    binary_path = os.path.abspath('./golf_cli')
    if os.path.exists(binary_path) and os.access(binary_path, os.X_OK):
        args = [binary_path, str(distance_yards)] + [f"{k}={v}" for k, v in clubs.items()]
        try:
            output = subprocess.check_output(args, stderr=subprocess.STDOUT, text=True, timeout=1)
            return output.strip()
        except Exception:
            pass

    sorted_clubs = sorted(clubs.items(), key=lambda item: item[1])
    best = None
    for club_name, yardage in sorted_clubs:
        if yardage >= distance_yards:
            best = club_name
            break
    if best is None and sorted_clubs:
        best = sorted_clubs[-1][0]
    return best


@app.route('/api/live/update', methods=['POST'])
def api_live_update():
    payload = request.json or {}
    current_hole = state['live']['hole']
    current_course = state['live']['course_id']
    current_strokes = state['live']['strokes']
    new_hole = payload.get('hole')
    new_course = payload.get('course_id', current_course)

    # Calculate score for previous hole if hole changed
    if current_hole and current_hole != new_hole and current_strokes > 0:
        state['live']['strokes_per_hole'][str(current_hole)] = current_strokes

    # Reset strokes on new hole
    if new_hole and new_hole != current_hole:
        state['live']['strokes'] = 0

    # Set par for new hole
    if new_hole:
        state['live']['par'] = get_par_for_hole(new_course, new_hole)

    state['live'].update({
        'course_id': new_course,
        'hole': new_hole,
        'distance': payload.get('distance'),
        'speed': payload.get('speed'),
        'status': payload.get('status', state['live']['status']),
        'user_lon': payload.get('user_lon'),
        'user_lat': payload.get('user_lat'),
        'timestamp': time.time()
    })
    state['live']['recommendation'] = recommend_club(state['live']['distance'])
    return jsonify({'message': 'Live state updated.', 'live': state['live']})


@app.route('/api/live/stroke', methods=['POST'])
def api_live_stroke():
    state['live']['strokes'] += 1
    return jsonify({'message': 'Stroke added.', 'strokes': state['live']['strokes']})


@app.route('/api/live', methods=['GET'])
def api_live():
    live_state = state['live'].copy()
    live_state['recommendation'] = recommend_club(live_state.get('distance'))
    live_state['cumulative_score'] = get_cumulative_score(live_state['course_id'], live_state['strokes_per_hole'])
    return jsonify({'user': state['user'], 'clubs': state['clubs'], 'live': live_state})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f'🚀 Starting dashboard backend on http://127.0.0.1:{port}')
    app.run(host='127.0.0.1', port=port, debug=True)
