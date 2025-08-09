import re


def build_access_request_message(
    user: dict, role_name: str, target_area: str | None = None
) -> str:
    """
    Формирует сообщение для уведомления о запросе доступа.

    :param user: словарь с данными пользователя
    :param role_name: строка с названием запрашиваемой роли
    :param target_area: участок или филиал, если указан
    """
    text = (
        f"📥 Пользователь <b>{user['full_name']}</b> запросил роль <b>{role_name}</b>"
    )
    if target_area:
        text += f" для <b>{target_area}</b>"
    text += f".\n\nTelegram: @{user.get('username') or '—'}"
    return text


def format_housing_office_block(jeu) -> str:
    """
    Принимает либо строку ('нет информации'), либо словарь с данными ЖЭУ.
    Возвращает красивый блок для вставки в инфо о доме.
    """
    if not jeu or jeu == "нет информации":
        return "нет информации"

    # Если это строка (например, пользователь сам вставил)
    if isinstance(jeu, str):
        return jeu

    # Если это словарь/объект
    parts = []
    if jeu.get("name"):
        parts.append(f"<b>{jeu['name']}</b>")
    if jeu.get("address"):
        parts.append(f"📍 {jeu['address']}")
    if jeu.get("phone"):
        parts.append(f"☎️ {jeu['phone']}")
    if jeu.get("working_hours"):
        parts.append(f"⏰ {jeu['working_hours']}")
    if jeu.get("comments"):
        parts.append(f"💬 {jeu['comments']}")
    if not parts:
        return "нет информации"
    return "\n".join(parts)


def build_parsed_house_info(
    parsed_data: dict,
    db_city_name: str,
    db_zone_name: str,
    notes: str = None,
    updated_at: str = None,
    jeu_address: str = "нет информации",
) -> str:
    # Адресные данные
    address = parsed_data.get("address", "Не указано")
    title = parsed_data.get("title", "Не указано")
    floors_text = parsed_data.get("floors", "Не указано")
    entrances_text = parsed_data.get("entrances", "Не указано")
    apartments_list = parsed_data.get("apartments", [])

    # Парсим улицу и номер
    street_match = re.search(r"^(.*?)\s+(\S+)$", title)
    if street_match:
        street = street_match.group(1).strip()
        house_number = street_match.group(2).strip()
    else:
        street = title
        house_number = ""

    # Количество подъездов
    entrances_match = re.search(r"(\d+)", entrances_text)
    entrances_count = int(entrances_match.group(1)) if entrances_match else 1

    # Количество этажей
    floors_match = re.search(r"(\d+)", floors_text)
    floors_count = int(floors_match.group(1)) if floors_match else "Не указано"

    # Разбор квартир по подъездам
    entrances_info = {}
    for item in apartments_list:
        apt_match = re.match(r"(\d+) подъезд: квартиры (.+)", item)
        if apt_match:
            entrance_number = int(apt_match.group(1))
            flats = apt_match.group(2).strip()
            entrances_info[entrance_number] = flats

    # Сбор текста
    text = (
        f"🏠 <b>Дом:</b>\n"
        f"{db_city_name}, {db_zone_name}, {street} {house_number}\n\n"
        f"🏢 <b>Этажей:</b> {floors_count}\n"
        f"🚪 <b>Подъездов:</b> {entrances_count}\n\n"
    )

    if entrances_info:
        for entrance_number in sorted(entrances_info.keys()):
            text += (
                f"🚪 <b>Подъезд {entrance_number}</b>: "
                f"{floors_count} этажей, квартиры {entrances_info[entrance_number]}\n"
            )
    else:
        text += "🚪 Нет данных о подъездах.\n"

    text += (
        f"\n🏢 <b>ЖЭУ:</b>\n{format_housing_office_block(jeu_address)}\n"
        f"📝 <b>Комментарии:</b> {notes or 'Нет'}\n"
        f"🕓 <b>Дата обновления информации:</b> {updated_at or 'Не указано'}"
    )

    return text


def build_house_address_info(
    *,
    city_name: str,
    zone_name: str,
    street: str,
    house_number: str,
    floors: int,
    entrances: int,
    entrance_info: dict[int, str] = None,
    jeu_address: str = "нет информации",
    notes: str = None,
    updated_at: str = None,
) -> str:
    text = (
        f"🏠 <b>Дом:</b>\n"
        f"{city_name}, {zone_name}, {street} {house_number}\n\n"
        f"🏢 <b>Этажей:</b> {floors}\n"
        f"🚪 <b>Подъездов:</b> {entrances}\n\n"
    )

    if entrance_info:
        for entrance_number in sorted(entrance_info.keys()):
            flats = entrance_info[entrance_number]
            text += f"🚪 <b>Подъезд {entrance_number}</b>: {floors} этажей, квартиры {flats}\n"
    else:
        text += "🚪 Нет данных о подъездах.\n"

    text += (
        f"\n🏢 <b>ЖЭУ:</b>\n{format_housing_office_block(jeu_address)}\n"
        f"📝 <b>Комментарии:</b> {notes or 'Нет'}\n"
        f"🕓 <b>Дата обновления информации:</b> {updated_at or 'Не указано'}"
    )

    return text
