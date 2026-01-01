from database import execute_query, fetch_all


class FeedbackService:
    @staticmethod
    def add_feedback(user_id, name, avatar, comment, stars=5):
        query = """
        INSERT INTO feedbacks (user_id, name, avatar, comment, stars)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (user_id, name, avatar, comment, stars)
        return execute_query(query, params)

    @staticmethod
    def get_feedbacks(limit=100):
        query = """
        SELECT id, user_id, name, avatar, comment, stars, created_at
        FROM feedbacks
        ORDER BY created_at ASC
        LIMIT %s
        """
        return fetch_all(query, (limit,))
