import os
from supabase import create_client, Client
from config import Config

class SupabaseClient:
    def __init__(self):
        self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    # User methods
    def create_user(self, email, password, username):
        return self.client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "username": username
                }
            }
        })
    
    def login_user(self, email, password):
        return self.client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
    
    def get_user(self):
        return self.client.auth.get_user()
    
    # Game methods
    def create_game(self, white_player, black_player, fen="start"):
        return self.client.table('games').insert({
            'white_player': white_player,
            'black_player': black_player,
            'fen': fen,
            'status': 'active'
        }).execute()
    
    def update_game(self, game_id, fen, status=None):
        data = {'fen': fen}
        if status:
            data['status'] = status
        return self.client.table('games').update(data).eq('id', game_id).execute()
    
    def get_user_games(self, user_id):
        return self.client.table('games').select('*').or_(f'white_player.eq.{user_id},black_player.eq.{user_id}').execute()
    
    # User stats methods
    def get_user_stats(self, user_id):
        return self.client.table('user_stats').select('*').eq('user_id', user_id).execute()
    
    def update_user_stats(self, user_id, wins=0, losses=0, draws=0):
        stats = self.get_user_stats(user_id)
        if not stats.data:
            # Create new stats
            return self.client.table('user_stats').insert({
                'user_id': user_id,
                'wins': wins,
                'losses': losses,
                'draws': draws,
                'rating': 1200
            }).execute()
        else:
            # Update existing stats
            current = stats.data[0]
            return self.client.table('user_stats').update({
                'wins': current['wins'] + wins,
                'losses': current['losses'] + losses,
                'draws': current['draws'] + draws
            }).eq('user_id', user_id).execute()
    
    # Achievements methods
    def grant_achievement(self, user_id, achievement_id):
        return self.client.table('user_achievements').insert({
            'user_id': user_id,
            'achievement_id': achievement_id,
            'earned_at': 'now()'
        }).execute()
    
    def get_user_achievements(self, user_id):
        return self.client.table('user_achievements').select('*, achievements(*)').eq('user_id', user_id).execute()

supabase = SupabaseClient()
