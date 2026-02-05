from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

start_kb = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text = "👥 Обери групу")],
        [KeyboardButton(text = "🗓 Графік")]
    ],
    resize_keyboard = True,
    input_field_placeholder= "Розпочнемо!?"
)

ck_dtk_kb = ReplyKeyboardMarkup(
    keyboard = [
        [
        KeyboardButton(text="ЦЕК"),
        KeyboardButton(text="ДТЕК"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Обери постачальника електроенергії!"
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
        ],
        [
        KeyboardButton(text="Далі 👉"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Обери групу!"
)