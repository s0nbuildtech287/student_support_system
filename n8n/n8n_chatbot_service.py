import requests
import logging
from n8n.n8n_health_check import n8n_health

N8N_CHATBOT_URL = "http://localhost:5678/webhook/chatbot"


class N8NChatbotService:
    """
    Service trung gian Chatbot -> n8n -> Dify
    (file này chỉ để đủ structure, không bắt buộc dùng)
    """

    @staticmethod
    def send_message(
        user_id: str,
        message: str,
        conversation_id: str | None = None,
        metadata: dict | None = None
    ):
        """
        Gửi message chatbot qua n8n (fast-fail)
        """

        # Fast fail
        if not n8n_health.is_n8n_available():
            logging.info("⚡ N8N is down, skip chatbot request")
            return None

        payload = {
            "action": "chat",
            "user_id": user_id,
            "message": message,
            "conversation_id": conversation_id,
            "metadata": metadata or {}
        }

        try:
            res = requests.post(
                N8N_CHATBOT_URL,
                json=payload,
                timeout=3
            )
            res.raise_for_status()

            data = res.json()
            n8n_health.mark_success()

            # Chuẩn hoá output cho chatbot
            return {
                "reply": data.get("reply") or data.get("answer"),
                "conversation_id": data.get("conversation_id"),
                "raw": data
            }

        except requests.exceptions.Timeout:
            logging.warning("⏱️ N8N timeout (chatbot)")
            n8n_health.mark_failure()
            return None

        except requests.exceptions.ConnectionError:
            logging.warning("🔌 N8N connection error (chatbot)")
            n8n_health.mark_failure()
            return None

        except Exception as e:
            logging.error(f"❌ Chatbot service error: {e}")
            n8n_health.mark_failure()
            return None


# Alias function cho tiện import
def send_chatbot_message(user_id, message, conversation_id=None, metadata=None):
    return N8NChatbotService.send_message(
        user_id=user_id,
        message=message,
        conversation_id=conversation_id,
        metadata=metadata
    )
