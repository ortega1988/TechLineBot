def build_access_request_message(user: dict, role_name: str, target_area: str | None = None) -> str:
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
