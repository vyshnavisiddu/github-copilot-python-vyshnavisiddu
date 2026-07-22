import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app as app_module


def test_index_route_renders_template():
    client = app_module.app.test_client()
    response = client.get('/')

    assert response.status_code == 200
    assert b'<!doctype html>' in response.data.lower()


def test_new_game_and_check_routes_work():
    client = app_module.app.test_client()

    response = client.get('/new?clues=40')
    assert response.status_code == 200

    payload = response.get_json()
    assert 'puzzle' in payload
    assert len(payload['puzzle']) == 9

    solution = app_module.CURRENT['solution']
    assert solution is not None

    response = client.post('/check', json={'board': solution})
    assert response.status_code == 200
    assert response.get_json()['incorrect'] == []


def test_check_route_requires_active_game():
    client = app_module.app.test_client()
    app_module.CURRENT['puzzle'] = None
    app_module.CURRENT['solution'] = None

    response = client.post('/check', json={'board': []})
    assert response.status_code == 400
    assert response.get_json()['error'] == 'No game in progress'


def test_new_game_rejects_invalid_clues():
    client = app_module.app.test_client()

    response = client.get('/new?clues=abc')
    assert response.status_code == 400
    assert response.get_json()['error'] == 'Clues must be an integer'


def test_new_game_accepts_difficulty_selection():
    client = app_module.app.test_client()

    response = client.get('/new?difficulty=hard')
    assert response.status_code == 200
    payload = response.get_json()
    assert 'puzzle' in payload
    assert 'solution' in payload


def test_frontend_has_leaderboard_storage_logic():
    script_path = Path(__file__).resolve().parents[1] / 'static' / 'main.js'
    script_content = script_path.read_text(encoding='utf-8')

    assert 'LEADERBOARD_STORAGE_KEY' in script_content
    assert 'renderLeaderboard' in script_content
    assert 'localStorage' in script_content
