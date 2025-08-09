from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# Кнопка "Запросить доступ" (для роли 50)
def request_access_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔓 Запросить доступ", callback_data="request_access"
                )
            ]
        ]
    )
    return keyboard


def build_main_menu(role_id: int) -> InlineKeyboardMarkup:
    buttons = []

    # Общие кнопки
    buttons.append(
        [InlineKeyboardButton(text="🔍 Поиск дома", callback_data="find_house")],
    )
    buttons.append(
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")],
    )

    # Админские кнопки (роль < 3)
    if role_id < 30:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="🛠 Администрирование", callback_data="admin_panel"
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def select_role_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🧠 РН (Руководитель направления)", callback_data="role_rn"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🧰 РГКС (Рук. группы клиентского сервиса)",
                    callback_data="role_rgks",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔧 СИ (Старший инженер)", callback_data="role_si"
                )
            ],
        ]
    )


def build_approval_keyboard(
    user_id: int, role_id: int, target: str
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Одобрить",
                    callback_data=f"approve:{user_id}:{role_id}:{target}",
                ),
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=f"reject:{user_id}:{role_id}:{target}",
                ),
            ]
        ]
    )


def get_admin_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="➕ Филиал", callback_data="add_branch")],
        [InlineKeyboardButton(text="➕ ГКС", callback_data="admin:add_gks")],
        [InlineKeyboardButton(text="➕ Город", callback_data="add_city")],
        [InlineKeyboardButton(text="➕ Районы", callback_data="admin:add_zone")],
        [
            InlineKeyboardButton(
                text="➕ Добавить ЖЭУ", callback_data="add_housing_office"
            )
        ],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="start")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_list_gks_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="➕ Добавить ГКС", callback_data="admin:add_gks")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="admin_panel")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirm_add_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="✅ Добавить в базу", callback_data="confirm_add_house"
            ),
            InlineKeyboardButton(text="❌ Отмена", callback_data="start"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_list_houses_menu(
    housing_office_id: int | None, house_id: int
) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="ℹ️ Подробно", callback_data="house:details")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="house:edit")],
    ]
    if housing_office_id is None:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="🔗 Привязать ЖЭУ",
                    callback_data=f"attach_housing_office:{house_id}",
                )
            ]
        )
    keyboard.append([InlineKeyboardButton(text="↩️ Назад", callback_data="start")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_housing_offices_keyboard(housing_offices: list) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=office.name, callback_data=f"select_housing_office:{office.id}"
            )
        ]
        for office in housing_offices
    ]
    buttons.append([InlineKeyboardButton(text="↩️ Назад", callback_data="start")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirm_add_housing_office_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Добавить", callback_data="add_housing_office_confirm"
                ),
                InlineKeyboardButton(text="↩️ Отмена", callback_data="start"),
            ]
        ]
    )


def get_confirm_add_branch_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Добавить", callback_data="add_branch_confirm"
                )
            ],
            [InlineKeyboardButton(text="↩️ Назад", callback_data="start")],
        ]
    )


def get_confirm_add_city_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Добавить", callback_data="add_city_confirm"
                )
            ],
            [InlineKeyboardButton(text="↩️ Отмена", callback_data="start")],
        ]
    )


def get_regions_keyboard(regions: list) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=region.name, callback_data=f"add_city_region_{region.id}"
            )
        ]
        for region in regions
    ]
    buttons.append(
        [
            InlineKeyboardButton(text="➕ Добавить регион", callback_data="add_branch"),
            InlineKeyboardButton(text="↩️ Назад", callback_data="start"),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_regions_gks_keyboard(regions: list) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=region.name, callback_data=f"add_gks_region_{region.id}"
            )
        ]
        for region in regions
    ]
    buttons.append(
        [
            InlineKeyboardButton(text="➕ Добавить регион", callback_data="add_branch"),
            InlineKeyboardButton(text="↩️ Назад", callback_data="start"),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_branches_keyboard(branches: list) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=branch.name, callback_data=f"add_zone_branch_{branch.id}"
                )
            ]
            for branch in branches
        ]
        + [
            [
                InlineKeyboardButton(text="↩️ Назад", callback_data="start"),
            ]
        ]
    )


def get_cities_keyboard(cities: list) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=city.name, callback_data=f"add_zone_city_{city.id}"
                )
            ]
            for city in cities
        ]
        + [
            [
                InlineKeyboardButton(
                    text="↩️ Назад", callback_data="add_zone_choose_branch"
                ),
            ]
        ]
    )


def get_areas_keyboard(areas: list) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=area.name, callback_data=f"add_zone_area_{area.id}"
                )
            ]
            for area in areas
        ]
        + [
            [
                InlineKeyboardButton(
                    text="↩️ Назад", callback_data="add_zone_choose_city"
                ),
            ]
        ]
    )


def get_house_cities_keyboard(cities):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=city.name, callback_data=f"find_house_city_{city.id}"
                )
            ]
            for city in cities
        ]
    )


def get_setting_cities_keyboard(cities, current_city_id: int | None = None):
    keyboard = []
    for city in cities:
        is_current = city.id == current_city_id
        text = f"✅ {city.name}" if is_current else city.name
        keyboard.append(
            [InlineKeyboardButton(text=text, callback_data=f"settings_city_{city.id}")]
        )
    keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="start")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
