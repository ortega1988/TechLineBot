from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Кнопка "Запросить доступ" (для роли 50)
def request_access_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔓 Запросить доступ",
                callback_data="request_access"
            )
        ]
    ])
    return keyboard

def build_main_menu(role_id: int) -> InlineKeyboardMarkup:
    buttons = []

    # Общие кнопки
    buttons.append([
        InlineKeyboardButton(text="📋 Меню", callback_data="user_menu")
    ])

    # Админские кнопки (роль < 3)
    if role_id < 3:
        buttons.append([
            InlineKeyboardButton(text="🛠 Администрирование", callback_data="admin_panel")
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def select_role_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 РН (Руководитель направления)", callback_data="role_rn")],
        [InlineKeyboardButton(text="🧰 РГКС (Рук. группы клиентского сервиса)", callback_data="role_rgks")],
        [InlineKeyboardButton(text="🔧 СИ (Старший инженер)", callback_data="role_si")]
    ])

def build_approval_keyboard(user_id: int, role_id: int, target: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Одобрить",
                callback_data=f"approve:{user_id}:{role_id}:{target}"
            ),
            InlineKeyboardButton(
                text="❌ Отклонить",
                callback_data=f"reject:{user_id}:{role_id}:{target}"
            )
        ]
    ])



def get_admin_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="➕ ГКС", callback_data="admin:gks_menu")],
        [InlineKeyboardButton(text="➕ Районы", callback_data="admin:zone_menu")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="admin:back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_list_zones_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="➕ Добавить район", callback_data="admin:add_zone")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)



def get_list_gks_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="➕ Добавить ГКС", callback_data="admin:add_gks")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="admin:gks_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
