class ResponseHandler:
    def generate_response(self, query, user_role, format_preference):
        response = {
            "quick_summary": self._generate_summary(),
            "detailed_content": self._generate_detailed(),
            "related_topics": self._get_related_topics(),
            "follow_up_suggestions": self._generate_suggestions()
        }
        return response 