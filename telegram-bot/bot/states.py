from aiogram.fsm.state import State, StatesGroup

class ApplicationState(StatesGroup):
    waiting_for_telegram_id = State()
    waiting_for_discord_id = State()
    waiting_for_email = State()
    waiting_for_phone = State()
    waiting_for_full_name = State()
    waiting_for_university = State()
    waiting_for_student_group = State()
    waiting_for_applicant_role = State()
    waiting_for_title = State()
    waiting_for_adviser = State()
    waiting_for_coauthors = State()
    editing_application = State()
    editing_field = State()
