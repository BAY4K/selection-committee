from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
import datetime


def current_graduation_year():
    return str(datetime.date.today().year)


class School(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")

    class Meta:
        verbose_name = "Школа"
        verbose_name_plural = "Школы"

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")

    class Meta:
        verbose_name = "Отделение"
        verbose_name_plural = "Отделения"

    def __str__(self):
        return self.name


class Applicant(models.Model):
    photo = models.ImageField(upload_to="applicants_photos/", default="applicants_photos/default.jpg",
                              verbose_name="Фото лица, 3x4")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    patronymic = models.CharField(max_length=100, verbose_name="Отчество")
    gender = models.CharField(max_length=10, verbose_name="Пол", choices=(("Мужской", "Мужской"),
                                                                          ("Женский", "Женский")),
                              default='Мужской')
    birth_date = models.DateField(verbose_name="Дата рождения")
    email = models.EmailField(verbose_name="Эл.Почта")
    phone = models.CharField(max_length=20, verbose_name='Номер телефона студента', blank=True, null=True)
    address = models.CharField(max_length=255, verbose_name="Адрес проживания")
    school = models.CharField(max_length=255, verbose_name="Школа")

    graduation_date = models.CharField(max_length=20, default=current_graduation_year,
                                       verbose_name="Дата окончания школы", )
    education = models.CharField(max_length=100, verbose_name="Образование",
                                 choices=(("Основное общее", "Основное общее"),
                                          ("Среднее(полное) общее образование", "Среднее(полное) общее образование"),
                                          ("Начальное профессиональное образование", "Начальное профессиональное "
                                                                                     "образование"),
                                          ("Среднее профессиональное образование", "Среднее профессиональное "
                                                                                   "образование"),
                                          ("Высшее профессиональное образование", "Высшее профессиональное "
                                                                                  "образование")),
                                 default='Среднее(полное) общее образование'
                                 )
    consent = models.FileField(upload_to="consents/",
                               verbose_name='Согласие на обработку данных', blank=True, null=True)
    status = models.CharField(max_length=20, verbose_name="Статус заявки",
                              choices=(("Рассмотрение", "Рассмотрение"), ("Выдан ответ", "Выдан ответ")),
                              default='Рассмотрение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = "Абитуриент"
        verbose_name_plural = "Абитуриенты"

    def change_status_to_answered(self):
        self.status = 'Выдан ответ'
        self.save()

    def get_graduation_date(self):
        return f'{self.graduation_date}'

    get_graduation_date.short_description = 'Год окончания'

    def get_gender(self):
        if self.gender == 'Мужской':
            return 'Мужской'
        else:
            return 'Женский'

    @classmethod
    def get_students_without_interview(cls):
        return cls.objects.exclude(id__in=Interview.objects.values_list('students__id', flat=True))

    def __str__(self):
        return f"{self.id} {self.last_name} {self.first_name} {self.patronymic} - {self.birth_date}"


class Document(models.Model):
    student = models.OneToOneField('Applicant', on_delete=models.CASCADE, verbose_name="Абитуриент",
                                   related_name='document', blank=True, null=True)
    SNILS = models.CharField(max_length=15, verbose_name="СНИЛС", blank=True, null=True)
    INN = models.CharField(max_length=15, verbose_name="ИНН", blank=True, null=True)
    passport_number = models.CharField(max_length=20, verbose_name="Номер паспорта", blank=True, null=True)
    issued_by = models.CharField(max_length=255, verbose_name="Кем выдан", blank=True, null=True)
    issue_date = models.DateField(verbose_name="Дата выдачи", blank=True, null=True)

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"

    def __str__(self):
        if self.student is None:
            return "NULL"
        return f'{self.student}'

    def get_passport_series(self):
        digits = ''.join(char for char in (self.passport_number or '') if char.isdigit())
        return digits[:4] if len(digits) == 10 else ''

    def get_passport_num(self):
        digits = ''.join(char for char in (self.passport_number or '') if char.isdigit())
        return digits[4:] if len(digits) == 10 else ''


class Parent(models.Model):
    student = models.OneToOneField(Applicant, on_delete=models.CASCADE, verbose_name="Ребёнок",
                                   related_name="parents", blank=True, null=True)
    mother_full_name = models.CharField(max_length=255, verbose_name="ФИО матери", blank=True, null=True)
    mother_phone = models.CharField(max_length=20, verbose_name="Телефон матери", blank=True, null=True)
    father_full_name = models.CharField(max_length=255, verbose_name="ФИО отца", blank=True, null=True)
    father_phone = models.CharField(max_length=20, verbose_name="Телефон отца", blank=True, null=True)

    class Meta:
        verbose_name = "Родитель"
        verbose_name_plural = "Родители"

    def __str__(self):
        return f"Родители {self.student}"


class InternalExam(models.Model):
    exam_date = models.DateTimeField('Дата экзамена', blank=True)
    students = models.ManyToManyField('Applicant', verbose_name="Студент", related_name="exam")

    class Meta:
        verbose_name = 'Журнал вступительных экзаменов'
        verbose_name_plural = 'Журналы вступительных экзаменов'

    def __str__(self):
        return f'Вступительный экзамен от {self.exam_date.date()}'


class Interview(models.Model):
    interview_date = models.DateTimeField('Дата собеседования', blank=True)
    students = models.ManyToManyField('Applicant', verbose_name="Студент")

    class Meta:
        verbose_name = 'Журнал собеседований'
        verbose_name_plural = 'Журналы собеседований'

    def __str__(self):
        return f'Собеседование от {self.interview_date.date()}'


def mask_name(name):
    if len(name) > 1:
        return name[0] + '*' * (len(name) - 1)
    else:
        return '*'


class Admission(models.Model):
    applicant = models.OneToOneField(Applicant, on_delete=models.CASCADE, verbose_name="Абитуриент",
                                     related_name="student")
    department = models.ManyToManyField('Department', verbose_name="Отделение",
                                        blank=True)
    admission_date = models.DateField(verbose_name="Дата поступления", auto_now_add=True)
    number_of_5 = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(20)],
                                              verbose_name="Количество пятерок", blank=True, null=True)
    number_of_4 = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(20)],
                                              verbose_name="Количество четверок", blank=True, null=True)
    number_of_3 = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(20)],
                                              verbose_name="Количество троек", blank=True, null=True)
    average_score = models.DecimalField(default=0.0, max_digits=5, decimal_places=2,
                                        verbose_name="Средний балл", blank=True, null=True)
    internal_exam = models.DecimalField(default=Decimal(0.0), max_digits=5, decimal_places=2,
                                        verbose_name="Результаты экзамена", blank=True, null=True)
    application_status = models.CharField(max_length=50, verbose_name="Статус заявки",
                                          choices=(("Рассмотрение", "Рассмотрение"),
                                                   ("Отказано", "Отказано"),
                                                   ("Принят", "Принят"),
                                                   ("Отправлен на заполнение", "Отправлен на заполнение")),
                                          default='Рассмотрение')
    original_or_copy = models.BooleanField(verbose_name="Оригинал или копия", blank=True, null=True, default=False)
    out_of_budget = models.BooleanField(default=False, verbose_name="Внебюджет", blank=True, null=True)

    received_receipt = models.BooleanField(default=False, verbose_name="Получил расписку", blank=True, null=True)
    internal_exam_conducted = models.BooleanField(default=False, verbose_name="Вступительный экзамен проведен",
                                                  blank=True, null=True)
    documents_collected = models.BooleanField(default=False, verbose_name="Документы забраны", blank=True, null=True)
    application_in_gov_services = models.BooleanField(default=False, verbose_name="Заявление в гос. услугах",
                                                      blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отправки', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления', blank=True, null=True)

    class Meta:
        verbose_name = "Поступление"
        verbose_name_plural = "Поступления"

    def get_departments(self):
        response = ''
        if self.department.exists():
            for department in self.department.all():
                response += f'{department.name}  '
        response.replace(',', '.')
        return response

    def change_status_to_accepted(self):
        self.application_status = 'Принят'
        self.save()

    def change_status_to_denied(self):
        self.application_status = 'Отказано'
        self.save()

    def change_status_to_watching(self):
        self.application_status = 'Рассмотрение'
        self.save()

    def change_status_to_warn(self):
        self.application_status = 'Отправлен на заполнение'
        self.save()

    def get_status(self):
        if self.application_status in ('watching', 'Рассмотрение'):
            return 'Рассмотрение'
        elif self.application_status in ('denied', 'Отказано'):
            return 'Ваша заявка отклонена'
        elif self.application_status in ('accepted', 'Принят'):
            return 'Ваша заявка принята. Вы участвуете в конкурсе'
        elif self.application_status in ('warn', 'Отправлен на заполнение'):
            return 'Ваша заявка под предупреждением. Заполните недостающие данные.'
        else:
            return self.get_application_status_display()

    def get_fio(self):
        return f'{self.applicant.last_name} {self.applicant.first_name} {self.applicant.patronymic}'

    def get_secret_fio(self):
        return f'{mask_name(self.applicant.last_name)} {mask_name(self.applicant.first_name)} {mask_name(self.applicant.patronymic)}'

    get_fio.short_description = 'ФИО'
    get_departments.short_description = 'Выбранные отделения'

    def get_original_or_copy(self):
        if self.original_or_copy:
            return '✔'
        else:
            return '✖'

    def save(self, *args, **kwargs):
        five, four, three = (self.number_of_5 or 0, self.number_of_4 or 0, self.number_of_3 or 0)
        total_subjects = five + four + three
        self.average_score = (Decimal(five * 5 + four * 4 + three * 3) / Decimal(total_subjects)
                              if total_subjects else Decimal('0'))
        self.internal_exam_conducted = bool(self.internal_exam)
        if kwargs.get('update_fields') is not None:
            kwargs['update_fields'] = set(kwargs['update_fields']) | {'average_score', 'internal_exam_conducted'}

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.applicant}'


class ApplicantAdmissionView(models.Model):
    applicant = models.OneToOneField(
        Applicant,
        on_delete=models.CASCADE,
        verbose_name="Абитуриент",
        related_name="admission_view_applicant"
    )
    admission = models.OneToOneField(
        Admission,
        on_delete=models.CASCADE,
        verbose_name="Поступление",
        related_name="admission_view_admission"
    )
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        verbose_name="Документ",
        related_name="admission_view_document"
    )
    parent = models.OneToOneField(
        Parent,
        on_delete=models.CASCADE,
        verbose_name="Родитель",
        related_name="admission_view_parent"
    )

    class Meta:
        verbose_name = "Общая таблица"
        verbose_name_plural = "Общая таблица"
