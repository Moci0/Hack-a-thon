from flask import Flask, request, jsonify, send_from_directory
import os
import time
import subprocess
import shutil

app = Flask(__name__, static_folder='.', static_url_path='')

state = {
    'user': None,
    'clubs': {
        'Driver': 230,
        '3-Wood': 210,
        '5-Iron': 150,
        '7-Iron': 130,
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
        'timestamp': None
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
        'email': payload.get('email', '').strip(),
        'handicap': payload.get('handicap', '').strip()
    }

    if not user['firstName'] or not user['email']:
        return jsonify({'error': 'First name and email are required.'}), 400

    state['user'] = user
    return jsonify({'message': 'User logged in.', 'user': state['user']})


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
    state['live'].update({
        'course_id': payload.get('course_id'),
        'hole': payload.get('hole'),
        'distance': payload.get('distance'),
        'speed': payload.get('speed'),
        'status': payload.get('status', state['live']['status']),
        'user_lon': payload.get('user_lon'),
        'user_lat': payload.get('user_lat'),
        'timestamp': time.time()
    })
    state['live']['recommendation'] = recommend_club(state['live']['distance'])
    return jsonify({'message': 'Live state updated.', 'live': state['live']})


@app.route('/api/live', methods=['GET'])
def api_live():
    live_state = state['live'].copy()
    live_state['recommendation'] = recommend_club(live_state.get('distance'))
    return jsonify({'user': state['user'], 'clubs': state['clubs'], 'live': live_state})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f'🚀 Starting dashboard backend on http://127.0.0.1:{port}')
    app.run(host='127.0.0.1', port=port, debug=True)
