from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth import get_user_model

from diplom import settings
from main.models import Applicant, School, Document, Parent, Admission


class ApplicantShortForm(forms.ModelForm):
    captcha = CaptchaField()

    class Meta:
        model = Applicant
        fields = ('last_name',
                  'first_name',
                  'patronymic',
                  'gender',
                  'birth_date',
                  'school',
                  'graduation_date',
                  'email',
                  'captcha')
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
            'birth_date': forms.TextInput(attrs={'class': 'input-control date-input',
                                                 'placeholder': "Дата рождения",
                                                 'onfocus': "(this.type='date')",
                                                 'onblur': "(this.type='text')"}),
            'graduation_date': forms.Select(attrs={'class': 'input-control select-date-input',
                                                   'data-placeholder': 'Год окончания школы'
                                                   })
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
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
        widget=forms.CheckboxSelectMultiple(attrs={'checked': 'checked'}),
        label='Поля абитуриента'
    )
    DOCUMENT_CHOICES = forms.MultipleChoiceField(
        choices=DOCUMENT_FIELDS,
        widget=forms.CheckboxSelectMultiple(attrs={'checked': 'checked'}),
        label='Поля документа'
    )
    PARENT_CHOICES = forms.MultipleChoiceField(
        choices=PARENT_FIELDS,
        widget=forms.CheckboxSelectMultiple(attrs={'checked': 'checked'}),
        label='Поля родителей'
    )
    ADMISSION_CHOICES = forms.MultipleChoiceField(
        choices=ADMISSION_FIELDS,
        widget=forms.CheckboxSelectMultiple(attrs={'checked': 'checked'}),
        label='Поля поступления'
    )
