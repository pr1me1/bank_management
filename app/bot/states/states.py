from aiogram.fsm.state import StatesGroup, State


class DocStates(StatesGroup):
    doc_number = State()
    doc_date = State()
    inn = State()
    pdf_upload = State()


class BotState(StatesGroup):
    awaiting_prompt = State()
    completing_transaction = State()
    awaiting_edit_action = State()
    awaiting_action = State()
    updating_transaction = State()


__all__ = [
    'DocStates',
    'BotState'
]
