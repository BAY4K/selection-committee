import datetime
from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth import get_user_model

from diplom import settings
from main.models import Applicant, School, Document, Parent, Admission
from main.captcha import ApplicationCaptchaWidget


class ApplicantShortForm(forms.ModelForm):
    captcha = CaptchaField(
        label='Проверка безопасности',
        widget=ApplicationCaptchaWidget(attrs={
            'class': 'input-control captcha-answer', 'placeholder': 'Код с картинки',
            'maxlength': '5', 'aria-describedby': 'captcha-hint',
        }),
        error_messages={
            'invalid': 'Код неверный или истёк. Введите код с новой картинки.',
            'required': 'Введите проверочный код с картинки.',
        },
    )
    accept = forms.BooleanField(
        label='Я даю согласие на обработку персональных данных',
        error_messages={'required': 'Для подачи заявки необходимо согласие на обработку персональных данных.'},
    )
    graduation_date = forms.ChoiceField(
        label='Год окончания школы',
        initial=lambda: str(datetime.date.today().year),
        choices=lambda: [(str(year), str(year)) for year in range(datetime.date.today().year - 3, datetime.date.today().year + 1)],
        widget=forms.Select(attrs={'class': 'input-control select-date-input'}),
    )

    class Meta:
        model = Applicant
        fields = ('last_name',
                  'first_name',
                  'patronymic',
                  'birth_date',
                  'gender',
                  'school',
                  'graduation_date',
                  'email',
                  'captcha', 'accept')
        widgets = {
            'last_name': forms.TextInput(
                attrs={'class': 'input-control', 'placeholder': 'Фамилия', 'pattern': '^[А-Яа-яЁё]+$'}),
            'first_name': forms.TextInput(
                attrs={'class': 'input-control', 'placeholder': 'Имя', 'pattern': '^[А-Яа-яЁё]+$'}),
            'patronymic': forms.TextInput(
                attrs={'class': 'input-control', 'placeholder': 'Отчество', 'pattern': '^[А-Яа-яЁё]+$'}),
            'school': forms.TextInput(attrs={'class': 'input-control', 'placeholder': 'Школа'}),
            'email': forms.EmailInput(attrs={'class': 'input-control', 'placeholder': 'Электронная почта'}),
            'gender': forms.RadioSelect(attrs={'class': 'radio-input'}),
            'birth_date': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'input-control', 'type': 'date'}),
            'graduation_date': forms.Select(attrs={'class': 'input-control select-date-input',
                                                   'data-placeholder': 'Год окончания школы'
                                                   })
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Такой E-mail уже существует!")
        return email


EXCLUDE_FIELDS = ['id', 'photo', 'consent', 'student', 'status', 'created_at', 'updated_at', 'applicant']


def get_fields_with_verbose_names(model):
    fields = []
    for field in model._meta.fields:
        if field.name not in EXCLUDE_FIELDS:
            fields.append((field.name, field.verbose_name))
    return fields


class FieldSelectionForm(forms.Form):
    APPLICANT_FIELDS = get_fields_with_verbose_names(Applicant)
    DOCUMENT_FIELDS = get_fields_with_verbose_names(Document)
    PARENT_FIELDS = get_fields_with_verbose_names(Parent)
    ADMISSION_FIELDS = get_fields_with_verbose_names(Admission)

    APPLICANT_CHOICES = forms.MultipleChoiceField(
        choices=APPLICANT_FIELDS,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'checked': 'checked'}),
        label='Поля абитуриента'
    )
    DOCUMENT_CHOICES = forms.MultipleChoiceField(
        choices=DOCUMENT_FIELDS,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'checked': 'checked'}),
        label='Поля документа'
    )
    PARENT_CHOICES = forms.MultipleChoiceField(
        choices=PARENT_FIELDS,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'checked': 'checked'}),
        label='Поля родителей'
    )
    ADMISSION_CHOICES = forms.MultipleChoiceField(
        choices=ADMISSION_FIELDS,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'checked': 'checked'}),
        label='Поля поступления'
    )
