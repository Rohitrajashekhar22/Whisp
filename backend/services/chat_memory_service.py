from services.chat_service import get_chat_history


def get_meeting_chat_memory(
    meeting_id,
    user_id
):
    return get_chat_history(
        meeting_id,
        user_id
    )