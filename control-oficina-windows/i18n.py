# -*- coding: utf-8 -*-

LANG_KEY = "language"

_MONTHS = {
    "es": [
        "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
    ],
    "en": [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ],
}

_T = {
    "es": {
        "menu_show": "Mostrar",
        "menu_settings": "Configuración",
        "menu_quit": "Salir",
        "goal_message": "¡Meta cumplida! ({n} días este mes)",
        "status_current": "Estado actual",
        "status_office": "En la oficina",
        "status_away": "Fuera de la oficina",
        "today": "Hoy",
        "registered": "Registrado",
        "not_registered": "Sin registrar",
        "days": "días",
        "goal_reached": "¡Meta cumplida!",
        "days_to_goal": "Faltan {n} días para la meta",
        "workdays_remaining": "Días hábiles restantes",
        "registered_days": "Días registrados",
        "no_records_month": "No hay registros este mes",
        "autostart": "Iniciar al encender la PC",
        "settings": "Configuración",
        "records": "Días",
        "refresh": "Actualizar",
        "register_today": "Registrar hoy",
        "quit": "Salir",
        "minimize": "Minimizar",
        "close": "Cerrar",
        "records_tooltip": "Agregar, editar o eliminar días registrados",
        "register_today_tooltip": "Registra el día de hoy manualmente",
        "gateway_section": "Gateway de la oficina",
        "gateway_desc": "Dirección IP del gateway de tu red de oficina",
        "gateway_placeholder": "Ej: 10.15.16.1",
        "detect": "Detectar",
        "current_gateway": "Gateway actual: {gw}",
        "current_gateway_none": "Gateway actual: —",
        "interval_section": "Intervalo de chequeo",
        "interval_desc": "Cada cuánto tiempo verificar la conexión a la oficina",
        "minutes": "minutos",
        "quick": "Rápido:",
        "interval_note": "Intervalos muy cortos (< 5 min) pueden consumir más batería",
        "goal_section": "Meta mensual",
        "goal_desc": "Cuántos días al mes considerás como meta",
        "language_section": "Idioma",
        "language_desc": "Idioma de la aplicación",
        "cancel": "Cancelar",
        "save": "Guardar",
        "invalid_ip": "La dirección IP del gateway no es válida.\nFormato: xxx.xxx.xxx.xxx",
        "detect_failed": "No se pudo detectar el gateway actual",
        "error": "Error",
        "records_title": "Días registrados",
        "records_of_month": "Registros de {month} {year}",
        "days_count": "{n} días",
        "add_day": "Agregar día:",
        "add": "+ Agregar",
        "change_date": "Cambiar fecha",
        "delete": "Eliminar",
        "already_exists": "Ese día ya está registrado.",
        "exists_title": "Ya existe",
        "confirm_delete": "¿Eliminar el registro del {date}?",
        "confirm": "Confirmar",
    },
    "en": {
        "menu_show": "Show",
        "menu_settings": "Settings",
        "menu_quit": "Quit",
        "goal_message": "Goal reached! ({n} days this month)",
        "status_current": "Current status",
        "status_office": "At the office",
        "status_away": "Away from office",
        "today": "Today",
        "registered": "Registered",
        "not_registered": "Not registered",
        "days": "days",
        "goal_reached": "Goal reached!",
        "days_to_goal": "{n} days left to reach the goal",
        "workdays_remaining": "Working days remaining",
        "registered_days": "Registered days",
        "no_records_month": "No records this month",
        "autostart": "Start on login",
        "settings": "Settings",
        "records": "Days",
        "refresh": "Refresh",
        "register_today": "Register today",
        "quit": "Quit",
        "minimize": "Minimize",
        "close": "Close",
        "records_tooltip": "Add, edit or remove registered days",
        "register_today_tooltip": "Registers today manually",
        "gateway_section": "Office gateway",
        "gateway_desc": "IP address of your office network gateway",
        "gateway_placeholder": "e.g. 10.15.16.1",
        "detect": "Detect",
        "current_gateway": "Current gateway: {gw}",
        "current_gateway_none": "Current gateway: —",
        "interval_section": "Check interval",
        "interval_desc": "How often to check the office connection",
        "minutes": "minutes",
        "quick": "Quick:",
        "interval_note": "Very short intervals (< 5 min) may use more battery",
        "goal_section": "Monthly goal",
        "goal_desc": "How many days per month you aim for",
        "language_section": "Language",
        "language_desc": "Application language",
        "cancel": "Cancel",
        "save": "Save",
        "invalid_ip": "The gateway IP address is invalid.\nFormat: xxx.xxx.xxx.xxx",
        "detect_failed": "Could not detect the current gateway",
        "error": "Error",
        "records_title": "Registered days",
        "records_of_month": "Records for {month} {year}",
        "days_count": "{n} days",
        "add_day": "Add day:",
        "add": "+ Add",
        "change_date": "Change date",
        "delete": "Delete",
        "already_exists": "That day is already registered.",
        "exists_title": "Already exists",
        "confirm_delete": "Delete the record for {date}?",
        "confirm": "Confirm",
    },
}

_current = "es"


def set_language(lang: str):
    global _current
    if lang in _T:
        _current = lang


def get_language() -> str:
    return _current


def t(key: str, **kwargs) -> str:
    table = _T.get(_current, _T["es"])
    text = table.get(key, key)
    return text.format(**kwargs) if kwargs else text


def month_name(index: int) -> str:
    return _MONTHS.get(_current, _MONTHS["es"])[index]
