from flask import request
import json

class VerifyLinks():
    def __init__(self):
        pass

    def verify_flask(self):
        data = request.get_json()
        if not "VERIFY_TOKEN" in data or data["VERIFY_TOKEN"] != self.VERIFY_TOKEN:
            return json.dumps({ "error": "401", "type": "INVALID_TOKEN" }), 200
        
        link = data["link"]

        content = self.get_content_object({}, link)
        response_text = self.process_post(content)

        return json.dumps({ "response": response_text }), 200