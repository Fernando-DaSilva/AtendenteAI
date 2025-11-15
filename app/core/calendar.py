def get_available_slots(nlu):
    # mock for MVP
    return ["2025-01-10 14:00"]

def create_event(slot, lead, nlu):
    return {"status": "created", "slot": slot}
