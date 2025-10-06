from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
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
        
        try:
            response = supabase.login_user(email, password)
            if response and response.user:
                session['user'] = {
                    'id': response.user.id,
                    'email': response.user.email,
                    'username': response.user.user_metadata.get('username', '')
                }
                return redirect(url_for('dashboard'))
            else:
                flash('Неверный email или пароль', 'error')
        except Exception as e:
            flash('Ошибка подключения к серверу', 'error')
            print(f"Login error: {e}")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        
        try:
            response = supabase.create_user(email, password, username)
            if response and response.user:
                # Создаем профиль
                supabase.create_profile(response.user.id, username)
                session['user'] = {
                    'id': response.user.id,
                    'email': response.user.email,
                    'username': username
                }
                flash('Регистрация успешна!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Ошибка регистрации', 'error')
        except Exception as e:
            flash('Ошибка подключения к серверу. Попробуйте позже.', 'error')
            print(f"Registration error: {e}")
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('index'))
@app.route('/debug')
def debug():
    """Диагностика подключения"""
    import os
    info = {
        'supabase_url': os.environ.get('SUPABASE_URL'),
        'supabase_key_length': len(os.environ.get('SUPABASE_KEY', '')) if os.environ.get('SUPABASE_KEY') else 0,
        'config_url': Config.SUPABASE_URL,
        'config_key_length': len(Config.SUPABASE_KEY) if Config.SUPABASE_KEY else 0,
        'message': 'Supabase connected successfully!'
    }
    return jsonify(info)
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Временные данные для теста
    user_stats = {
        'wins': 0,
        'losses': 0, 
        'draws': 0,
        'rating': 1200,
        'games_played': 0
    }
    
    return render_template('dashboard.html', 
                         user=session['user'],
                         stats=user_stats,
                         games=[],
                         achievements=[])

@app.route('/play')
def play():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Временная страница игры
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Шахматная игра</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                padding: 50px;
            }
            .game-container {
                background: rgba(255,255,255,0.1);
                padding: 30px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
        </style>
    </head>
    <body>
        <div class="game-container">
            <h1>🎯 Шахматная игра</h1>
            <p>Игровой модуль в разработке...</p>
            <p>Скоро здесь будет полноценная шахматная доска!</p>
            <a href="/dashboard" style="color: #f39c12;">Вернуться в дашборд</a>
        </div>
    </body>
    </html>
    """

# Временные API методы для теста
@app.route('/api/create_game', methods=['POST'])
def create_game():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return jsonify({'game_id': 'temp-game', 'message': 'Game system in development'})

@app.route('/api/make_move', methods=['POST'])
def make_move():
    return jsonify({'message': 'Game system in development'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
