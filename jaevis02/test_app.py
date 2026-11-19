import io
import json
import unittest
from unittest.mock import patch

from app import Assistant


class ResponsesAPITest(unittest.TestCase):
    def test_reply_reads_text_from_rest_output(self):
        response = {
            "output": [
                {"type": "reasoning", "summary": []},
                {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {"type": "output_text", "text": " Ahoj"},
                        {"type": "output_text", "text": ", světe! "},
                    ],
                },
            ],
        }
        assistant = Assistant()
        assistant.api_key = "test"

        with patch("app.urlopen", return_value=io.BytesIO(json.dumps(response).encode())):
            self.assertEqual(assistant.reply("test", "Ahoj"), "Ahoj, světe!")

    def test_reply_handles_output_without_text(self):
        response = {
            "output": [
                {"type": "message", "content": [{"type": "refusal", "refusal": "Sorry"}]},
            ],
        }
        assistant = Assistant()
        assistant.api_key = "test"

        with patch("app.urlopen", return_value=io.BytesIO(json.dumps(response).encode())):
            self.assertIn("model returned no text", assistant.reply("test", "Ahoj"))
