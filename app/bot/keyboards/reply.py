# from aiogram.fsm.context import FSMContext
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram import types
#
#
#
# async def show_main_menu(message_or_query, lang: str, state: FSMContext):
#     """
#     Show main document menu with Create and Documents History buttons
#     """
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [
#             InlineKeyboardButton(
#                 text=get_message(lang, 'doc_create_button'),
#                 callback_data="doc_create"
#             )
#         ],
#         [
#             InlineKeyboardButton(
#                 text=get_message(lang, 'doc_history_button'),
#                 callback_data="doc_history"
#             )
#         ]
#     ])
#
#     menu_text = get_message(lang, 'doc_main_menu')
#
#     if isinstance(message_or_query, types.CallbackQuery):
#         await message_or_query.message.edit_text(
#             menu_text,
#             parse_mode="HTML",
#             reply_markup=keyboard
#         )
#     else:
#         await message_or_query.answer(
#             menu_text,
#             parse_mode="HTML",
#             reply_markup=keyboard
#         )
