import datetime

from django.conf import settings
from django.core.cache import cache


def get_invalid_login_attempts(phone_number):
    return cache.get(f'invalid_login_attempts_{phone_number}', 0)


def set_invalid_login_attempts(phone_number, attempts):
    cache.set(f'invalid_login_attempts_{phone_number}', attempts, settings.INVALID_LOGIN_ATTEMPTS_TIMEOUT)


def increment_invalid_login_attempts(phone_number):
    attempts = get_invalid_login_attempts(phone_number)
    attempts += 1
    set_invalid_login_attempts(phone_number, attempts)
    set_last_invalid_login_attempt_time(phone_number, datetime.datetime.now(datetime.timezone.utc))


def get_last_invalid_login_attempt_time(phone_number):
    return cache.get(f'last_invalid_login_attempt_time_{phone_number}')


def set_last_invalid_login_attempt_time(phone_number, time):
    cache.set(f'last_invalid_login_attempt_time_{phone_number}', time, settings.INVALID_LOGIN_ATTEMPTS_TIMEOUT)


def is_user_blocked(phone_number):
    attempts = get_invalid_login_attempts(phone_number)
    if attempts >= settings.INVALID_LOGIN_ATTEMPTS_ALLOWED:
        last_attempt_time = get_last_invalid_login_attempt_time(phone_number)
        current_time = datetime.datetime.now(datetime.timezone.utc)
        time_diff = current_time - last_attempt_time if last_attempt_time else datetime.timedelta(seconds=3600)
        if time_diff.total_seconds() < 3600:
            return True
        else:
            set_invalid_login_attempts(phone_number, 0)
    return False