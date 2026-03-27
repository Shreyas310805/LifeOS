from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_id, db):
        self.id = user_id
        doc = db.collection('users').document(user_id).get()
        data = doc.to_dict() if doc.exists else {}
        
        
        self.name = data.get('name', 'Unknown User')
        self.email = data.get('email', '')
        
        
        self.friend_id = data.get('friend_id', '') 
        self.friends = data.get('friends', [])     
        
        
        self.level = data.get('level', 1)
        self.total_xp = data.get('total_xp', 0)
        self.is_connected = data.get('is_connected', False)
        self.steps = data.get('steps', 0)
        self.calories = data.get('calories', 0)
        self.health_conditions = data.get('health_conditions', '')

    @staticmethod
    def get(user_id, db):
        """Helper to fetch a user, returns None if they don't exist in DB."""
        if db.collection('users').document(user_id).get().exists:
            return User(user_id, db)
        return None
        
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "friend_id": self.friend_id,
            "level": self.level,
            "total_xp": self.total_xp,
            "steps": self.steps,
            "health_conditions": self.health_conditions
        }