from services.live_meeting_service import (
    create_live_meeting
)

meeting_id = create_live_meeting(
    1,
    "Test Live Meeting"
)

print(meeting_id)