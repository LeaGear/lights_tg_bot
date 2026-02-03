from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

start_kb = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text = "👥 Choose group")],
        [KeyboardButton(text = "🗓 Schedule")],
        [KeyboardButton(text = "🔄 Update")]
    ],
    resize_keyboard = True,
    input_field_placeholder= "Let`s Start!?"
)

ck_dtk_kb = ReplyKeyboardMarkup(
    keyboard = [
        [
        KeyboardButton(text="CEK"),
        KeyboardButton(text="DTEK"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Choose your supplier!"
)

group_kb = ReplyKeyboardMarkup(
    keyboard = [
        [
        KeyboardButton(text="1.1"),
        KeyboardButton(text="1.2"),
        KeyboardButton(text="2.1"),
        KeyboardButton(text="2.2"),
        ],
        [
        KeyboardButton(text="3.1"),
        KeyboardButton(text="3.2"),
        KeyboardButton(text="4.1"),
        KeyboardButton(text="4.2"),
        ],
        [
        KeyboardButton(text="5.1"),
        KeyboardButton(text="5.2"),
        KeyboardButton(text="6.1"),
        KeyboardButton(text="6.2"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Choose your group!"
)