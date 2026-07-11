import unittest
from draft_machine import draft_reply

class TestDraftMachine(unittest.TestCase):
    def test_draft_reply(self):
        mock_thread = {
            "subject": "Project Update",
            "messages": [
                {
                    "from": "alice@example.com",
                    "date": "2026-07-08",
                    "body": "Hi Rahul, can you provide an update on the project status?"
                },
                {
                    "from": "rahul@example.com",
                    "date": "2026-07-08",
                    "body": "Sure, I will get back to you shortly."
                }
            ]
        }
        
        response = draft_reply(mock_thread)
        print("Drafted Reply:", response)

if __name__ == "__main__":
    unittest.main()