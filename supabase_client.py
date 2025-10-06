import os
from supabase import create_client, Client
from config import Config
import json
from typing import Optional, Dict, Any

class SupabaseClient:
    def __init__(self):
        url = Config.SUPABASE_URL
        key = Config.SUPABASE_KEY
        if not url or not key:
            raise ValueError("Supabase URL and KEY must be set in environment variables")
        
        self.client: Client = create_client(url, key)
    
    def create_user(self, email: str, password: str, username: str):
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "username": username
                    }
                }
            })
            return response
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    def create_profile(self, user_id: str, username: str):
        """Создает профиль пользователя"""
        try:
            return self.client.table('profiles').insert({
                'id': user_id,
                'username': username
            }).execute()
        except Exception as e:
            print(f"Error creating profile: {e}")
            return None

    def login_user(self, email: str, password: str):
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email, 
                "password": password
            })
            return response
        except Exception as e:
            print(f"Error logging in: {e}")
            return None

    def get_current_user(self):
        try:
            return self.client.auth.get_user()
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    def logout(self):
        try:
            return self.client.auth.sign_out()
        except Exception as e:
            print(f"Error logging out: {e}")
            return None

    # Остальные методы остаются как были...

supabase = SupabaseClient()
