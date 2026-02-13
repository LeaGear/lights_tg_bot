from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


start_kb = ReplyKeyboardMarkup(
    keyboard = [
        [
            KeyboardButton(text="🗓 Графік"),
            KeyboardButton(text="👥 Обери групу")
        ],
        [
            KeyboardButton(text="📋 Мої групи"),
            KeyboardButton(text="❌ Видалення групи")
        ]
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

def get_keyboard(
    *btns: list,
    placeholder: str = None,
    request_contact: int = None,
    request_location: int = None,
    sizes: tuple[int] = (2,),
):
    keyboard = ReplyKeyboardBuilder()
    for btn in btns:
        for index, text in enumerate(btn, start = 0):
            if request_contact and request_contact == index:
                keyboard.add(KeyboardButton(text=text, request_contact=True))
            elif request_location and request_location == index:
                keyboard.add(KeyboardButton(text=text, request_location=True))
            else:
                keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(resize_keyboard=True, input_field_placeholder=placeholder)