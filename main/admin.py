from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from import_export import resources, fields
from import_export.admin import ExportMixin, ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

from account.forms import InterviewAdminForm, InternalExamAdminForm
from .resources import ApplicantAdmissionViewResource
from .utils import create_account, send_invite_email, confirm_student, deny_student, warn_student, make_docunment
from .models import *


# from .resources import ApplicantAdmissionViewResource


# Register your models here.
class DocumentInline(admin.StackedInline):  # или TabularInline, в зависимости от предпочтений дизайна
    model = Document
    can_delete = False  # если вы не хотите удалять документы из приемов
    verbose_name_plural = 'Документы'


class ParentsInline(admin.StackedInline):  # или TabularInline, в зависимости от предпочтений дизайна
    model = Parent
    can_delete = False  # если вы не хотите удалять документы из приемов
    verbose_name_plural = 'Родители'


class ApplicantInline(admin.StackedInline):  # или TabularInline, в зависимости от предпочтений дизайна
    model = Applicant
    can_delete = False  # если вы не хотите удалять документы из приемов
    verbose_name_plural = 'Абитуриенты'


class AdmissionInline(admin.StackedInline):
    model = Admission
    can_delete = False
    verbose_name_plural = 'Поступления'
    fk_name = 'applicant'


class ParentInline(admin.StackedInline):
    model = Parent
    can_delete = False
    verbose_name_plural = 'Родители'


class StudentResource(resources.ModelResource):
    fio = fields.Field(
        column_name='ФИО',
        attribute='get_fio',
    )
    departments = fields.Field(
        column_name='Отделения',
        attribute='get_departments',
    )

    class Meta:
        model = Admission
        fields = ('id',
                  'fio',
                  'departments',
                  'admission_date',
                  'number_of_5',
                  'number_of_4',
                  'number_of_3',
                  'average_score',
                  'internal_exam',
                  'original_or_copy',
                  'application_status',
                  'internal_exam_conducted',
                  'received_receipt',
                  'out_of_budget',
                  'documents_collected',
                  'application_in_gov_services',
                  )


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    order = 0
    inlines = [DocumentInline, ParentsInline]
    list_display = ('id',
                    'last_name',
                    'first_name',
                    'patronymic',
                    'gender',
                    'birth_date',
                    'email',
                    'school',
                    'education',
                    'get_graduation_date',
                    'address',
                    'status',
                    'updated_at',
                    'created_at')
    ordering = ('-status', '-created_at', '-updated_at', 'last_name', 'first_name', 'patronymic')
    list_editable = ('status',)
    list_filter = ('gender', 'status', 'school', 'created_at', 'updated_at')
    list_display_links = ('last_name', 'first_name', 'patronymic')
    actions = ('confirm_applicant',)
    search_fields = ('last_name',
                     'first_name',
                     'patronymic',)

    @admin.action(description='Принять заявку на регистрацию')
    def confirm_applicant(self, request, queryset):
        count = 0
        for obj in queryset:
            response = create_account(obj)
            if response:
                count += 1

        self.message_user(request, f'Успешно приняты {count} пользователей')


class StudentAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = StudentResource

    def download_application(self, obj):
        return format_html(
            '<a class="button" style="margin-top: 15px" href="{}">Скачать заявление</a>',
            reverse('generate_document', args=[obj.applicant.pk])
        )

    download_application.short_description = 'Скачать заявление'
    download_application.allow_tags = True

    list_display = ('id',
                    'get_fio',
                    'get_departments',
                    'admission_date',
                    'number_of_5',
                    'number_of_4',
                    'number_of_3',
                    'average_score',
                    'internal_exam',
                    'original_or_copy',
                    'application_status',
                    'internal_exam_conducted',
                    'received_receipt',
                    'out_of_budget',
                    'documents_collected',
                    'application_in_gov_services',
                    'download_application')
    list_editable = (
        'number_of_5',
        'number_of_4',
        'number_of_3',
        'internal_exam',
        'application_status',
        'original_or_copy',
        'out_of_budget',
        'received_receipt',
        'documents_collected',
        'application_in_gov_services',
        'internal_exam_conducted',)

    list_filter = ('department', 'application_status', 'created_at',
                   'updated_at', 'internal_exam_conducted', 'application_in_gov_services')
    list_display_links = ('get_fio',)
    search_fields = ('applicant__last_name', 'applicant__first_name', 'applicant__patronymic',)
    actions = ('confirm_applicant', 'deny_applicant', 'warn_applicant')

    def get_export_queryset(self, request):
        # Получаем queryset с примененными фильтрами, сортировкой и поиском
        queryset = super().get_export_queryset(request)
        return queryset

    @admin.action(description='Скачать заявление студента')
    def download_acception(self, request, queryset):
        count = 0
        for obj in queryset:
            response = make_docunment(obj)

            if response:
                count += 1

        self.message_user(request, f'Успешно приняты {count} студенты')


    @admin.action(description='Принять студента')
    def confirm_applicant(self, request, queryset):
        count = 0
        for obj in queryset:
            response = confirm_student(obj)

            if response:
                count += 1

        self.message_user(request, f'Успешно приняты {count} студенты')

    @admin.action(description='Отказать студенту')
    def deny_applicant(self, request, queryset):
        count = 0
        for obj in queryset:
            subject = "Ваша заявка отклонена."
            message = f"""Добрый день, вы не прошли на конкурс для вступления на бюджет ."""
            response = deny_student(obj)
            if response:
                count += 1
        self.message_user(request, f'Успешно отклонены {count} студенты')

    @admin.action(description='Отправить предупреждение о нехватке данных студента')
    def warn_applicant(self, request, queryset):
        count = 0
        for obj in queryset:
            subject = "Ваша заявка отклонена."
            message = f"""Добрый день, вы подали недостаточное количество документов. Пожалуйста зайдите в свой личный кабинет и укажите недостающие данные."""
            response = warn_student(obj)
            if response:
                count += 1
        self.message_user(request, f'Успешно предупреждены {count} студенты')


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    form = InterviewAdminForm
    actions = ('send_invite_to_meet',)
    filter_horizontal = ('students',)

    @admin.action(description='Отправить приглашение на собеседование выбранным студентам')
    def send_invite_to_meet(self, request, queryset):
        for interview in queryset:
            interview_date = interview.interview_date
            subject = "Приглашение на собеседование."
            message = f"""Добрый день, мы одобряем вашу заявку и приглашаем пройти собеседование.
Вам необходимо явиться {str(interview_date.day).zfill(2)}.{str(interview_date.month).zfill(2)}.{str(interview_date.year).zfill(2)} в {str(interview_date.hour).zfill(2)}:{str(interview_date.minute).zfill(2)} для прохождения экзамена. Явка обязательна."""

            for student in interview.students.all():
                send_invite_email(student.email, subject, message)
        self.message_user(request, f'Сообщения успешно отправлены.')


@admin.register(InternalExam)
class InternalExamAdmin(admin.ModelAdmin):
    form = InternalExamAdminForm
    actions = ('send_invite_to_exam',)
    filter_horizontal = ('students',)

    @admin.action(description='Отправить приглашение на вступительный экзамен выбранным студентам')
    def send_invite_to_exam(self, request, queryset):
        for internal_exam in queryset:
            exam_date = internal_exam.exam_date
            subject = "Приглашение на собеседование."
            message = f"""Добрый день, мы одобряем вашу заявку и приглашаем пройти вступительный экзамен.
Вам необходимо явиться {str(exam_date.day).zfill(2)}.{str(exam_date.month).zfill(2)}.{str(exam_date.year).zfill(2)} в {str(exam_date.hour).zfill(2)}:{str(exam_date.minute).zfill(2)} для прохождения экзамена. Явка обязательна."""
            for student in internal_exam.students.all():
                send_invite_email(student.email, subject, message)
        self.message_user(request, f'Сообщения успешно отправлены.')


class ApplicantAdmissionViewAdmin(ImportExportModelAdmin):
    resource_class = ApplicantAdmissionViewResource

    list_display = (
        'get_applicant_full_name', 'get_admission_status', 'get_document_snils', 'get_parent_names'
    )

    search_fields = (
        'applicant__last_name',
        'applicant__first_name',
        'applicant__patronymic',
        'admission__application_status',
        'document__SNILS',
        'parent__mother_full_name'
    )

    list_filter = (
        'admission__application_status', 'admission__admission_date'
    )

    readonly_fields = (
        'get_applicant_full_name', 'get_admission_status',
        'get_document_snils', 'get_parent_names', 'get_applicant_gender',
        'get_applicant_birth_date', 'get_applicant_email', 'get_applicant_phone',
        'get_applicant_address', 'get_applicant_school', 'get_applicant_graduation_date',
        'get_applicant_education', 'get_applicant_status',
        'get_admission_department', 'get_admission_date', 'get_admission_number_of_5',
        'get_admission_number_of_4', 'get_admission_number_of_3', 'get_admission_average_score',
        'get_admission_internal_exam', 'get_admission_application_status', 'get_admission_original_or_copy',
        'get_admission_out_of_budget', 'get_admission_received_receipt',
        'get_admission_internal_exam_conducted', 'get_admission_documents_collected',
        'get_admission_application_in_gov_services', 'get_document_inn', 'get_document_passport_number',
        'get_document_issued_by', 'get_document_issue_date', 'get_parent_mother_full_name', 'get_parent_mother_phone',
        'get_parent_father_full_name', 'get_parent_father_phone'
    )

    def get_applicant_full_name(self, obj):
        return f"{obj.applicant.last_name} {obj.applicant.first_name} {obj.applicant.patronymic}"

    get_applicant_full_name.short_description = 'ФИО абитуриента'

    def get_admission_status(self, obj):
        return obj.admission.application_status

    get_admission_status.short_description = 'Статус заявки'

    def get_document_snils(self, obj):
        return obj.document.SNILS

    get_document_snils.short_description = 'СНИЛС'

    def get_parent_names(self, obj):
        return f"{obj.parent.mother_full_name}, {obj.parent.father_full_name}"

    get_parent_names.short_description = 'Родители'

    def get_applicant_gender(self, obj):
        return obj.applicant.gender

    get_applicant_gender.short_description = 'Пол'

    def get_applicant_birth_date(self, obj):
        return obj.applicant.birth_date

    get_applicant_birth_date.short_description = 'Дата рождения'

    def get_applicant_email(self, obj):
        return obj.applicant.email

    get_applicant_email.short_description = 'Эл.Почта'

    def get_applicant_phone(self, obj):
        return obj.applicant.phone

    get_applicant_phone.short_description = 'Номер телефона'

    def get_applicant_address(self, obj):
        return obj.applicant.address

    get_applicant_address.short_description = 'Адрес проживания'

    def get_applicant_school(self, obj):
        return obj.applicant.school

    get_applicant_school.short_description = 'Школа'

    def get_applicant_graduation_date(self, obj):
        return obj.applicant.graduation_date

    get_applicant_graduation_date.short_description = 'Дата окончания школы'

    def get_applicant_education(self, obj):
        return obj.applicant.education

    get_applicant_education.short_description = 'Образование'

    def get_applicant_status(self, obj):
        return obj.applicant.status

    get_applicant_status.short_description = 'Статус абитуриента'

    def get_admission_department(self, obj):
        return obj.admission.department

    get_admission_department.short_description = 'Отделение'

    def get_admission_date(self, obj):
        return obj.admission.admission_date

    get_admission_date.short_description = 'Дата подачи'

    def get_admission_number_of_5(self, obj):
        return obj.admission.number_of_5

    get_admission_number_of_5.short_description = 'Количество пятерок'

    def get_admission_number_of_4(self, obj):
        return obj.admission.number_of_4

    get_admission_number_of_4.short_description = 'Количество четверок'

    def get_admission_number_of_3(self, obj):
        return obj.admission.number_of_3

    get_admission_number_of_3.short_description = 'Количество троек'

    def get_admission_average_score(self, obj):
        return obj.admission.average_score

    get_admission_average_score.short_description = 'Средний балл'

    def get_admission_internal_exam(self, obj):
        return obj.admission.internal_exam

    get_admission_internal_exam.short_description = 'Внутренний экзамен'

    def get_admission_application_status(self, obj):
        return obj.admission.application_status

    get_admission_application_status.short_description = 'Статус заявки'

    def get_admission_original_or_copy(self, obj):
        return obj.admission.original_or_copy

    get_admission_original_or_copy.short_description = 'Оригинал/Копия'

    def get_admission_out_of_budget(self, obj):
        return obj.admission.out_of_budget

    get_admission_out_of_budget.short_description = 'Вне бюджета'

    def get_admission_received_receipt(self, obj):
        return obj.admission.received_receipt

    get_admission_received_receipt.short_description = 'Получена квитанция'

    def get_admission_internal_exam_conducted(self, obj):
        return obj.admission.internal_exam_conducted

    get_admission_internal_exam_conducted.short_description = 'Проведен внутренний экзамен'

    def get_admission_documents_collected(self, obj):
        return obj.admission.documents_collected

    get_admission_documents_collected.short_description = 'Собраны документы'

    def get_admission_application_in_gov_services(self, obj):
        return obj.admission.application_in_gov_services

    get_admission_application_in_gov_services.short_description = 'Заявка в госуслуги'

    def get_document_inn(self, obj):
        return obj.document.INN

    get_document_inn.short_description = 'ИНН'

    def get_document_passport_number(self, obj):
        return obj.document.passport_number

    get_document_passport_number.short_description = 'Номер паспорта'

    def get_document_issued_by(self, obj):
        return obj.document.issued_by

    get_document_issued_by.short_description = 'Кем выдан'

    def get_document_issue_date(self, obj):
        return obj.document.issue_date

    get_document_issue_date.short_description = 'Дата выдачи'

    def get_parent_mother_full_name(self, obj):
        return obj.parent.mother_full_name

    get_parent_mother_full_name.short_description = 'ФИО матери'

    def get_parent_mother_phone(self, obj):
        return obj.parent.mother_phone

    get_parent_mother_phone.short_description = 'Телефон матери'

    def get_parent_father_full_name(self, obj):
        return obj.parent.father_full_name

    get_parent_father_full_name.short_description = 'ФИО отца'

    def get_parent_father_phone(self, obj):
        return obj.parent.father_phone

    get_parent_father_phone.short_description = 'Телефон отца'


admin.site.register(ApplicantAdmissionView, ApplicantAdmissionViewAdmin)
admin.site.register(Admission, StudentAdmin)
admin.site.register(Department)
# admin.site.register(School)

admin.site.sort_by = 'order'

