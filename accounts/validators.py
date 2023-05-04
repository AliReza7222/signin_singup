import re

from django.core.validators import ValidationError


def check_phone_number(value):
    regex_phone_number = re.findall('(09)[0-9]{9}', value)
    if regex_phone_number:
        phone_number = regex_phone_number[0]
        if phone_number == value:
            return phone_number
    return ValidationError("لطفا شماره تلفن همراه صحیح وارد نمایید .")


def check_last_and_first_name(value):
    get_regex_value = re.findall('[a-zA-Z ا-ی]+', value)
    if get_regex_value:
        name = get_regex_value[0]
        if name == value:
            return name
    return ValidationError("فیلد مورد نظر باید فقط شامل حروف باشد .")
