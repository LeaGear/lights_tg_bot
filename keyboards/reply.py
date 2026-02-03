from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

start_kb = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text = "👥 Выбери группу")],
        [KeyboardButton(text = "🗓 График")],
        [KeyboardButton(text = "🔄 Автообновление")]
    ],
    resize_keyboard = True,
    input_field_placeholder= "Давай начнем!?"
)

ck_dtk_kb = ReplyKeyboardMarkup(
    keyboard = [
        [
        KeyboardButton(text="ЦЕК"),
        KeyboardButton(text="ДТЭК"),
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выбери своего поставщика електроэнергии!"
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
    input_field_placeholder="Выбери группу!"
)

update_kb = ReplyKeyboardMarkup(
    keyboard = [
        [
        KeyboardButton(text = "🟢 Включить"),
        KeyboardButton(text = "🔴 Выключить")
        ]
    ],
    resize_keyboard=True,
)