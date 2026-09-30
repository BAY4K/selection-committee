from django.db import migrations


def normalize_statuses(apps, schema_editor):
    alias = schema_editor.connection.alias
    applicant = apps.get_model('main', 'Applicant').objects.using(alias)
    admission = apps.get_model('main', 'Admission').objects.using(alias)
    for old, new in {'watching': 'Рассмотрение', 'answered': 'Выдан ответ'}.items():
        applicant.filter(status=old).update(status=new)
    for old, new in {'watching': 'Рассмотрение', 'accepted': 'Принят', 'denied': 'Отказано', 'warn': 'Отправлен на заполнение'}.items():
        admission.filter(application_status=old).update(application_status=new)
    for old, new in {'male': 'Мужской', 'female': 'Женский'}.items():
        applicant.filter(gender=old).update(gender=new)


class Migration(migrations.Migration):
    dependencies = [('main', '0007_alter_admission_admission_date_and_more')]
    operations = [migrations.RunPython(normalize_statuses, migrations.RunPython.noop)]
