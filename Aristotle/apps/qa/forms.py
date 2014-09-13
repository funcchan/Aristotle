#!/usr/bin/env python
#
# @name: forms.py
# @create: Sep. 11th, 2014
# @update: Sep. 12th, 2014
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


class ResetForm(forms.Form):
    email = forms.EmailField(label='Email')


class ResetPasswordForm(forms.Form):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    repassword = forms.CharField(
        label='Repeat password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(ResetPasswordForm, self).clean()
        password = cleaned_data.get('password')
        repassword = cleaned_data.get("repassword")

        if password and repassword and password != repassword:
            msg = 'passwords are not identical'
            self.add_error('repassword', msg)


class EditProfileForm(forms.Form):
    GENDER_CHOICES = (('M', 'male'), ('F', 'female'), ('UN', 'unknown'))
    first_name = forms.CharField(label='First Name', max_length=30)
    last_name = forms.CharField(label='Last Name', max_length=30)
    age = forms.DecimalField(label='Age', min_value=0)
    gender = forms.ChoiceField(
        label='Gender', choices=GENDER_CHOICES)
    occupation = forms.CharField(label='Occupation', required=False)
    education = forms.CharField(label='Education', required=False)
    address = forms.CharField(label='Address', required=False)
    phone = forms.CharField(label='Phone', required=False)
    company = forms.CharField(label='Company', required=False)
    website = forms.URLField(label='Website', required=False)
    interests = forms.CharField(
        label='Interests', widget=forms.Textarea, required=False)
    bio = forms.CharField(
        label='About me', widget=forms.Textarea, required=False)


class EditAccountForm(forms.Form):
    password = forms.CharField(
        label='Verify Password', widget=forms.PasswordInput)
    username = forms.CharField(label='Username', max_length=30)
    email = forms.EmailField(label='Email')
    newpassword = forms.CharField(
        label='New Password', widget=forms.PasswordInput)
    repassword = forms.CharField(
        label='Repeat Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(EditAccountForm, self).clean()
        newpassword = cleaned_data.get('newpassword')
        repassword = cleaned_data.get("repassword")

        if newpassword and repassword and newpassword != repassword:
            msg = 'New passwords are not identical'
            self.add_error('repassword', msg)


class EditAvatarForm(forms.Form):
    avatar = forms.FileField(label='Avatar')


class AskQuestionForm(forms.Form):
    title = forms.CharField(label='Title', max_length=255)
    content = forms.CharField(label='Content', widget=forms.Textarea)
    tags = forms.CharField(label='Tags', required=False)


class EditQuestionForm(forms.Form):
    title = forms.CharField(label='Title', max_length=255)
    content = forms.CharField(label='Content', widget=forms.Textarea)
    tags = forms.CharField(label='Tags', required=False)


class CommentQuestionForm(forms.Form):
    question_comment_content = forms.CharField(widget=forms.Textarea)


class AppendQuestionForm(forms.Form):
    question_append_content = forms.CharField(widget=forms.Textarea)


class AnswerForm(forms.Form):
    answer_content = forms.CharField(widget=forms.Textarea)


class CommentAnswerForm(forms.Form):
    answer_comment_content = forms.CharField(widget=forms.Textarea)


class AppendAnswerForm(forms.Form):
    answer_append_content = forms.CharField(widget=forms.Textarea)


class EditAnswerForm(forms.Form):
    answer_content = forms.CharField(widget=forms.Textarea)
