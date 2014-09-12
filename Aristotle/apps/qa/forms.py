#!/usr/bin/env python
#
# @name: forms.py
# @create: Sep. 11th, 2014
# @update: Sep. 11th, 2014
# @author: Z. Huang

from django import forms


class SignInForm(forms.Form):
    username = forms.CharField(label='Username', max_length=30)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class SignUpForm(forms.Form):
    username = forms.CharField(label='Username', max_length=30)
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    repassword = forms.CharField(
        label='Repeat password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()
        password = cleaned_data.get('password')
        repassword = cleaned_data.get("repassword")

        if password and repassword and password != repassword:
            msg = 'passwords are not identical'
            self.add_error('repassword', msg)
