import re

from django.core.validators import ValidationError


def check_last_and_first_name(value):
    get_regex_value = re.findall('[a-zA-Z ا-ی]+', value)
    if get_regex_value:
        name = get_regex_value[0]
        if name == value:
            return name
    raise ValidationError("فیلد مورد نظر باید فقط شامل حروف باشد .")
