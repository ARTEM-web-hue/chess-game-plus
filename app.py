from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from supabase_client import supabase
import chess
import json
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        response = supabase.login_user(email, password)
        if response and response.user:
            session['user'] = {
                'id': response.user.id,
                'email': response.user.email,
                'username': response.user.user_metadata.get('username', '')
            }
            return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        
        response = supabase.create_user(email, password, username)
        if response and response.user:
            # Создаем профиль
            supabase.create_profile(response.user.id, username)
            session['user'] = {
                'id': response.user.id,
                'email': response.user.email,
                'username': username
            }
            return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_stats = supabase.get_user_stats(session['user']['id'])
    user_games = supabase.get_user_games(session['user']['id'])
    achievements = supabase.get_user_achievements(session['user']['id'])
    
    return render_template('dashboard.html', 
                         user=session['user'],
                         stats=user_stats.data[0] if user_stats.data else None,
                         games=user_games.data,
                         achievements=achievements.data)

@app.route('/play')
def play():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('game.html', user=session['user'])

@app.route('/api/create_game', methods=['POST'])
def create_game():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user']['id']
    # Пока создаем игру с самим собой для теста
    response = supabase.create_game(user_id, user_id)
    return jsonify({'game_id': response.data[0]['id']})
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))
@app.route('/api/make_move', methods=['POST'])
def make_move():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    game_id = data['game_id']
    move = data['move']
    
    # Получаем текущую игру
    game_response = supabase.get_game(game_id)
    if not game_response.data:
        return jsonify({'error': 'Game not found'}), 404
    
    game = game_response.data[0]
    board = chess.Board(game['fen'])
    
    # Пробуем сделать ход
    try:
        chess_move = board.parse_san(move)
        if chess_move in board.legal_moves:
            board.push(chess_move)
            
            # Обновляем игру
            moves = json.loads(game['moves'] or '[]')
            moves.append(move)
            
            supabase.update_game(
                game_id, 
                board.fen(), 
                moves,
                'finished' if board.is_game_over() else 'active',
                session['user']['id'] if board.is_checkmate() else None
            )
            
            return jsonify({
                'fen': board.fen(),
                'is_checkmate': board.is_checkmate(),
                'is_draw': board.is_game_over() and not board.is_checkmate()
            })
        else:
            return jsonify({'error': 'Illegal move'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid move'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
