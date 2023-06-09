import datetime
import random

from string import digits

from django.contrib import messages
from django.views.generic import FormView, TemplateView
from django.shortcuts import reverse, redirect
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from formtools.wizard.views import SessionWizardView

from .forms import PhoneNumberForm, LoginForm, ManagementForm, RegisterForm, CodeSend
from .time_block import *
from .models import User


def show_first_error(list_error):
    for field in list_error:
        if list_error.get(field):
            return {'text': list_error.get(field).as_text()}


class LoginRegister(TemplateView):
    template_name = 'login_register.html'


class Login(SessionWizardView):
    template_name = 'accounts/login.html'
    STEP_ONE, STEP_TWO = '0', '1'
    form_list = [
        (STEP_ONE, PhoneNumberForm),
        (STEP_TWO, LoginForm)
    ]

    def post(self, *args, **kwargs):
        data = self.request.POST
        # check step one
        if self.steps.current == self.STEP_ONE:
            form_obj = self.get_form(step=self.STEP_ONE, data=data)
            if form_obj.is_valid():
                phone_number = form_obj.cleaned_data['phone_number']
                if not User.objects.filter(phone_number=phone_number).exists():
                    message = '! این شماره تلفن تا به حال ثبت نشده است '
                    messages.error(self.request, message)
                    return self.render_goto_step(self.STEP_ONE)

        # check step two
        elif self.steps.current == self.STEP_TWO:
            form_obj = self.get_form(step=self.STEP_TWO, data=data)
            phone_number = self.get_cleaned_data_for_step(self.STEP_ONE).get('phone_number')
            if form_obj.is_valid():
                username, password = form_obj.cleaned_data['username'], form_obj.cleaned_data['password']
                user = User.objects.filter(username=username)
                message = "! نام کاربری یا رمز عبور اشتباه است "
                if is_user_blocked(phone_number):
                    message_block = " !شما به علت سه بار اشتباه برای ورود به مدت یک ساعت بلاک هستید لطفا پس از یک ساعت تلاش فرمایید  "
                    messages.error(self.request, message_block)
                    return self.render_goto_step(self.STEP_TWO)
                if user:
                    user = user[0]
                    if not check_password(password, user.password):
                        increment_invalid_login_attempts(phone_number)  # increment invalid login attempts
                        messages.error(self.request, message)
                        return self.render_goto_step(self.STEP_TWO)
                elif not user:
                    increment_invalid_login_attempts(phone_number)  # increment invalid login attempts
                    messages.error(self.request, message)
                    return self.render_goto_step(self.STEP_TWO)

        # Look for a wizard_goto_step element in the posted data which
        # contains a valid step name. If one was found, render the requested
        # form. (This makes stepping back a lot easier).
        wizard_goto_step = self.request.POST.get('wizard_goto_step', None)
        if wizard_goto_step and wizard_goto_step in self.get_form_list():
            return self.render_goto_step(wizard_goto_step)
        # Check if form was refreshed
        management_form = ManagementForm(self.request.POST, prefix=self.prefix)
        if not management_form.is_valid():
            raise ValidationError(
                'ManagementForm data is missing or has been tampered.',
                code='missing_management_form',
            )
        form_current_step = management_form.cleaned_data['current_step']
        if (form_current_step != self.steps.current and
                self.storage.current_step is not None):
            # form refreshed, change current step
            self.storage.current_step = form_current_step
        # get the form for the current step
        form = self.get_form(data=self.request.POST, files=self.request.FILES)
        # and try to validate
        if form.is_valid():
            # if the form is valid, store the cleaned data and files.
            self.storage.set_step_data(self.steps.current, self.process_step(form))
            self.storage.set_step_files(self.steps.current, self.process_step_files(form))
            # check if the current step is the last step
            if self.steps.current == self.steps.last:
                # no more steps, render done view
                return self.render_done(form, **kwargs)
            else:
                # proceed to the next step
                return self.render_next_step(form)
        message_box = show_first_error(form.errors)
        messages.error(self.request, f"{message_box.get('text').lstrip('*')}")
        return self.render(form)

    def done(self, form_list, **kwargs):
        username = self.get_cleaned_data_for_step(self.STEP_TWO)['username']
        user = User.objects.get(username=username)
        phone_number = user.phone_number
        login(self.request, user)
        message = f' عزیز شما با موفقیت وارد سایت شدید {user.first_name} {user.last_name}'
        set_invalid_login_attempts(phone_number, 0)
        messages.success(self.request, message)
        return redirect('home')


class Logout(LoginRequiredMixin, FormView):
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        logout(request)
        message = ' . شما با موفقیت از سایت خارج شدید '
        messages.success(request, message)
        return redirect('login_register')


class RegisterUser(SessionWizardView):
    template_name = 'accounts/register.html'
    STEP_ONE, STEP_TWO, STEP_THREE = '0', '1', '2'
    form_list = [
        (STEP_ONE, PhoneNumberForm),
        (STEP_TWO, CodeSend),
        (STEP_THREE, RegisterForm)
    ]

    def generate_code(self):
        code = ''.join(random.choices(digits, k=6))
        return code

    def post(self, *args, **kwargs):
        data = self.request.POST

        # check step one
        if self.steps.current == self.STEP_ONE:
            form_obj = self.get_form(step=self.STEP_ONE, data=data)
            if form_obj.is_valid():
                phone_number = form_obj.cleaned_data['phone_number']
                if is_user_blocked(phone_number):
                    message_block = " ! به علت اشتباه مکرر در ارسال کد ، کد منقضی و شما به مدت یک ساعت بلاک هستید "
                    messages.error(self.request, message_block)
                    return self.render_goto_step(self.STEP_ONE)
                if User.objects.filter(phone_number=phone_number).exists():
                    message = '! این شماره تلفن قبلا ثبت شده است '
                    messages.error(self.request, message)
                    return self.render_goto_step(self.STEP_ONE)
                # set code unique
                code = self.generate_code()
                print(code)
                cache.set(phone_number, code, timeout=80)

        elif self.steps.current == self.STEP_TWO:
            form_obj = self.get_form(step=self.STEP_TWO, data=data)
            phone_number = self.get_cleaned_data_for_step(self.STEP_ONE).get('phone_number')
            if form_obj.is_valid():
                code_post = form_obj.cleaned_data.get('code_user')

                if is_user_blocked(phone_number):
                    message_block = " ! به علت اشتباه مکرر در ارسال کد ، کد منقضی و شما به مدت یک ساعت بلاک هستید "
                    messages.error(self.request, message_block)
                    return self.render_goto_step(self.STEP_ONE)

                if cache.get(phone_number) is None:
                    message = ' . کد منقضی شده است دوباره تلاش فرمایید '
                    messages.error(self.request, message)
                    return self.render_goto_step(self.STEP_ONE)

                elif code_post != cache.get(phone_number):
                    increment_invalid_login_attempts(phone_number)
                    message = ' ! کد اشتباه است '
                    messages.error(self.request, message)
                    return self.render_goto_step(self.STEP_TWO)

        elif self.steps.current == self.STEP_THREE:
            form_obj = self.get_form(step=self.STEP_THREE, data=data)
            if form_obj.is_valid():
                data_clean = form_obj.cleaned_data
                username, password = data_clean.get('username'), data_clean.get('password')
                if User.objects.filter(username=username).exists():
                    message = ' ! این نام کاربری قبلا استفاده شده '
                    messages.error(self.request, message)
                    return self.render_goto_step(self.STEP_THREE)

        # Look for a wizard_goto_step element in the posted data which
        # contains a valid step name. If one was found, render the requested
        # form. (This makes stepping back a lot easier).
        wizard_goto_step = self.request.POST.get('wizard_goto_step', None)
        if wizard_goto_step and wizard_goto_step in self.get_form_list():
            return self.render_goto_step(wizard_goto_step)
        # Check if form was refreshed
        management_form = ManagementForm(self.request.POST, prefix=self.prefix)
        if not management_form.is_valid():
            raise ValidationError(
                'ManagementForm data is missing or has been tampered.',
                code='missing_management_form',
            )
        form_current_step = management_form.cleaned_data['current_step']
        if (form_current_step != self.steps.current and
                self.storage.current_step is not None):
            # form refreshed, change current step
            self.storage.current_step = form_current_step
        # get the form for the current step
        form = self.get_form(data=self.request.POST, files=self.request.FILES)
        # and try to validate
        if form.is_valid():
            # if the form is valid, store the cleaned data and files.
            self.storage.set_step_data(self.steps.current, self.process_step(form))
            self.storage.set_step_files(self.steps.current, self.process_step_files(form))
            # check if the current step is the last step
            if self.steps.current == self.steps.last:
                # no more steps, render done view
                return self.done(form, **kwargs)
            else:
                # proceed to the next step
                return self.render_next_step(form)
        message_box = show_first_error(form.errors)
        messages.error(self.request, f"{message_box.get('text').lstrip('*')}")
        return self.render(form)

    def done(self, form_list, **kwargs):
        phone_number = self.get_cleaned_data_for_step(self.STEP_ONE).get('phone_number')
        form_information_user = self.get_cleaned_data_for_step(self.STEP_THREE)
        password = form_information_user.get('password')
        password_hasher = make_password(password)
        form_information_user['password'] = password_hasher
        form_information_user['phone_number'] = phone_number
        del form_information_user['repeat_password']
        User.objects.create(**form_information_user)
        message = ' . شما با موفقیت ثبت نام شدید حال میتوانید وارد سایت شوید '
        set_invalid_login_attempts(phone_number, 0)
        messages.success(self.request, message)
        return redirect('login_register')
