# resources.py
from import_export import resources, fields
from import_export.widgets import *

from .models import ApplicantAdmissionView, Applicant, Admission, Document, Parent


class ApplicantAdmissionViewResource(resources.ModelResource):
    applicant__last_name = fields.Field(attribute='applicant__last_name', column_name='Фамилия')

    class Meta:
        model = ApplicantAdmissionView
        fields = (
            'applicant__last_name', 'applicant__first_name', 'applicant__patronymic',
            'applicant__gender', 'applicant__birth_date', 'applicant__email', 'applicant__phone',
            'applicant__address', 'applicant__school', 'applicant__graduation_date', 'applicant__education',
            'applicant__status', 'admission__department', 'admission__admission_date',
            'admission__number_of_5', 'admission__number_of_4', 'admission__number_of_3',
            'admission__average_score', 'admission__internal_exam', 'admission__application_status',
            'admission__original_or_copy', 'admission__out_of_budget', 'admission__received_receipt',
            'admission__internal_exam_conducted', 'admission__documents_collected',
            'admission__application_in_gov_services', 'document__SNILS', 'document__INN',
            'document__passport_number', 'document__issued_by', 'document__issue_date',
            'parent__mother_full_name', 'parent__mother_phone',
            'parent__father_full_name', 'parent__father_phone'
        )
        export_order = (
            'applicant__last_name', 'applicant__first_name', 'applicant__patronymic',
            'applicant__gender', 'applicant__birth_date', 'applicant__email', 'applicant__phone',
            'applicant__address', 'applicant__school', 'applicant__graduation_date', 'applicant__education',
            'applicant__status', 'admission__department', 'admission__admission_date',
            'admission__number_of_5', 'admission__number_of_4', 'admission__number_of_3',
            'admission__average_score', 'admission__internal_exam', 'admission__application_status',
            'admission__original_or_copy', 'admission__out_of_budget', 'admission__received_receipt',
            'admission__internal_exam_conducted', 'admission__documents_collected',
            'admission__application_in_gov_services', 'document__SNILS', 'document__INN',
            'document__passport_number', 'document__issued_by', 'document__issue_date',
            'parent__mother_full_name', 'parent__mother_phone',
            'parent__father_full_name', 'parent__father_phone'
        )
