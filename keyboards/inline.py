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
    buttons.append(
        [InlineKeyboardButton(text="📋 Меню", callback_data="user_menu")],
        )
    buttons.append(
        [InlineKeyboardButton(text="🔍 Поиск дома", callback_data="find_house")],
        )
    

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
        [InlineKeyboardButton(text="➕ Добавить ЖЭУ", callback_data="add_housing_office")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="start")],
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
        [InlineKeyboardButton(text="↩️ Назад", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirm_add_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Добавить в базу", callback_data="confirm_add_house"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="start"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_list_houses_menu(housing_office_id: int | None, house_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="ℹ️ Подробно", callback_data="house:details")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="house:edit")],
    ]
    if housing_office_id is None:
        keyboard.append([
            InlineKeyboardButton(
                text="🔗 Привязать ЖЭУ",
                callback_data=f"attach_housing_office:{house_id}"
            )
        ])
    keyboard.append([
        InlineKeyboardButton(text="↩️ Назад", callback_data="start")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirm_add_housing_office_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Добавить", callback_data="add_housing_office_confirm"),
            InlineKeyboardButton(text="↩️ Отмена", callback_data="start"),
        ]
    ])