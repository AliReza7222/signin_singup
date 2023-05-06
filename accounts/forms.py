import re

from django import forms

from .models import User


class RegisterForm(forms.ModelForm):
    repeat_password = forms.CharField(max_length=128, widget=forms.PasswordInput(attrs={
        'placeholder': 'تکرار رمز عبور را وارد کنید'
    }), label='تکرار رمز عبور')

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'password',
        ]
        widgets = {
            'username':forms.TextInput(attrs={'placeholder': 'نام کاربری خود را وارد کنید '}),
            'first_name':forms.TextInput(attrs={'placeholder': 'نام خود را وارد کنید ' }),
            'last_name': forms.TextInput(attrs={'placeholder': 'نام خانوادگی خود را وارد کنید '}),
            'password': forms.PasswordInput(attrs={'placeholder': 'رمز عبور مورد نظر را وارد کنید '}),
        }
        labels = {
            'username': 'نام کاربری',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'password':'رمز عبور',
        }

    def clean_repeat_password(self):
        password, re_password = self.cleaned_data.get('password'), self.cleaned_data.get('repeat_password')
        if password != re_password:
            raise forms.ValidationError('رمز شما با تکرار ان برابر نیست !')
        elif len(password) < 7:
            raise forms.ValidationError("رمز شما باید بیشتر از ۶ حرف باشد .")
        return password


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(
        attrs={'placeholder': 'نام کاربری خود را وارد کنید '}), label='نام کاربری')
    password = forms.CharField(max_length=128, widget=forms.PasswordInput(
        attrs={'placeholder': 'رمز عبور خود را وارد کنید '}), label='رمز عبور')


class PhoneNumberForm(forms.Form):
    phone_number = forms.CharField(max_length=11, widget=forms.TextInput(attrs={
        'placeholder': 'مثال : 09115213672'
    }), label='شماره تلفن همراه')

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        regex_phone_number = re.findall('09[0-9]{9}', phone_number)
        if regex_phone_number:
            phone_number = regex_phone_number[0]
            if phone_number == phone_number:
                return phone_number
        raise forms.ValidationError(". لطفا شماره تلفن همراه صحیح وارد نمایید ")


class CodeSend(forms.Form):
    code_user = forms.CharField(max_length=6, widget=forms.TextInput(
        attrs={'placeholder': 'کد ارسالی را وارد نمایید '}), label='کد ارسالی')


class ManagementForm(forms.Form):
    """
    ``ManagementForm`` is used to keep track of the current wizard step.
    """
    template_name = "django/forms/p.html"  # Remove when Django 5.0 is minimal version.
    current_step = forms.CharField(widget=forms.HiddenInput)
