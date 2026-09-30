from bs4 import BeautifulSoup
import requests
from django.shortcuts import get_object_or_404
from docx import Document as docs
from django.core.mail import send_mail

from account.models import User
from django.conf import settings
from django.db import transaction
from django.utils.crypto import get_random_string
from main.models import School, Parent, Document, Admission, Applicant, ApplicantAdmissionView

urls = [
    'https://edu.tatar.ru/agryz/type/1',
    'https://edu.tatar.ru/aznakaevo/type/1',
    'https://edu.tatar.ru/aksubaevo/type/1',
    'https://edu.tatar.ru/aktanysh/type/1',
    'https://edu.tatar.ru/alekseevo/type/1',
    'https://edu.tatar.ru/alkeevo/type/1',
    'https://edu.tatar.ru/almet/type/1',
    'https://edu.tatar.ru/apastovo/type/1',
    'https://edu.tatar.ru/arsk/type/1',
    'https://edu.tatar.ru/atnya/type/1',
    'https://edu.tatar.ru/bauly/type/1',
    'https://edu.tatar.ru/baltasi/type/1',
    'https://edu.tatar.ru/bugulma/type/1',
    'https://edu.tatar.ru/buinsk/type/1',
    'https://edu.tatar.ru/v_uslon/type/1',
    'https://edu.tatar.ru/v_gora/type/1',
    'https://edu.tatar.ru/n_chelny/type/1',
    'https://edu.tatar.ru/drozhanoye/type/1',
    'https://edu.tatar.ru/elabuga/type/1',
    'https://edu.tatar.ru/zainsk/type/1',
    'https://edu.tatar.ru/z_dol/type/1',
    'https://edu.tatar.ru/kaybitcy/type/1',
    'https://edu.tatar.ru/k_ustye/type/1',
    'https://edu.tatar.ru/kukmor/type/1',
    'https://edu.tatar.ru/laishevo/type/1',
    'https://edu.tatar.ru/l-gorsk/type/1',
    'https://edu.tatar.ru/mamadysh/type/1',
    'https://edu.tatar.ru/mendeleevsk/type/1',
    'https://edu.tatar.ru/menzelinsk/type/1',
    'https://edu.tatar.ru/muslum/type/1',
    'https://edu.tatar.ru/nkamsk/type/1',
    'https://edu.tatar.ru/nsheshma/type/1',
    'https://edu.tatar.ru/nurlat/type/1',
    'https://edu.tatar.ru/pestretcy/type/1',
    'https://edu.tatar.ru/r_sloboda/type/1',
    'https://edu.tatar.ru/saby/type/1',
    'https://edu.tatar.ru/sarmanovo/type/1',
    'https://edu.tatar.ru/spassk/type/1',
    'https://edu.tatar.ru/tetyushi/type/1',
    'https://edu.tatar.ru/tukaj/type/1',
    'https://edu.tatar.ru/tulachi/type/1',
    'https://edu.tatar.ru/cheremshan/type/1',
    'https://edu.tatar.ru/chistopol/type/1',
    'https://edu.tatar.ru/yutaza/type/1',
]


def parse_schools():
    names = set()
    for url in urls:
        names.update(parse_info(url))
    if not names:
        raise ValueError("Список школ пуст; существующие данные сохранены")
    with transaction.atomic():
        School.objects.all().delete()
        School.objects.bulk_create([School(name=name) for name in sorted(names)])


def parse_info(url):
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    return [school.get_text(' ', strip=True)
            for schools in soup.find_all('ul', class_='edu-list col-md-4')
            for school in schools.find_all('li') if school.get_text(strip=True)]


def make_docunment(student):
    ...


@transaction.atomic
def create_account(applicant):
    applicant = Applicant.objects.select_for_update().get(pk=applicant.pk)
    if not User.objects.filter(email__iexact=applicant.email).exists():
        new_user = User()
        new_user.username = (str(applicant.pk).zfill(2) +
                             str(applicant.birth_date.year) +
                             str(applicant.birth_date.month).zfill(2) +
                             str(applicant.birth_date.day).zfill(2))
        password = get_random_string(20)
        new_user.set_password(password)

        new_user.email = applicant.email
        new_user.student = applicant
        new_user.save()
        applicant.change_status_to_answered()
        applicant.save()
        parents = Parent.objects.get_or_create(student=applicant)[0]
        documents = Document.objects.get_or_create(student=applicant)[0]
        admission = Admission.objects.get_or_create(applicant=applicant)[0]
        parents.save()
        documents.save()
        admission.save()
        ApplicantAdmissionView.objects.create(applicant=applicant, admission=admission,
                                              document=documents, parent=parents).save()
        send_mail(
            "Ваша заявка принята.",
            f"""Ваша заявка принята, приступайте к заполнению вашей личной страницы с документами.
Вот ваши данные для авторизации на сайте:
Логин:{new_user.username}
Пароль:{password}

Можно также использовать почту для авторизации.""",
            settings.DEFAULT_FROM_EMAIL,
            [new_user.email],
            fail_silently=False,
        )
        return True
    return False


def confirm_student(admission):
    admission.change_status_to_accepted()
    return True


def deny_student(admission):
    admission.change_status_to_denied()
    return True


def warn_student(admission):
    admission.change_status_to_warn()
    return True


def send_invite_email(email, subject, message):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )


def replace_text_in_runs(paragraph, replacements):
    for key, value in replacements.items():
        value = str(value or '')
        if key in paragraph.text:
            full_text = ''.join([run.text for run in paragraph.runs])
            new_text = full_text.replace(key, value)

            for i in range(len(paragraph.runs)):
                paragraph.runs[i].text = ''

            if paragraph.runs:
                paragraph.runs[0].text = new_text
            else:
                paragraph.add_run(new_text)


def fill_template(person_id, template_path):
    person = get_object_or_404(Applicant, id=person_id)
    doc = docs(template_path)

    document = getattr(person, 'document', None) or Document()
    admission = getattr(person, 'student', None)
    replacements = {
        '{last_name}': person.last_name,
        '{first_name}': person.first_name,
        '{patronymic}': person.patronymic,
        '{birth_date}': person.birth_date.strftime('%d.%m.%Y'),
        '{passport}': f'Серия  {document.get_passport_series()}   № {document.get_passport_num()}',
        '{issued_by}': document.issued_by,
        '{issue_date}': document.issue_date.strftime('%d.%m.%Y') if document.issue_date else '',
        '{phone}': person.phone,
        '{snils}': document.SNILS,
        '{addmissions}': admission.get_departments() if admission else '',
    }

    for paragraph in doc.paragraphs:
        replace_text_in_runs(paragraph, replacements)


    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    replace_text_in_runs(paragraph, replacements)

    return doc