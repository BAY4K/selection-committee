from django.test import TestCase
from .models import School

class SchoolTestCase(TestCase):
    def setUp(self):
        School.objects.create(name="Test")

    def test_model_creation(self):
        """Проверка, что объект был успешно создан"""
        obj = School.objects.get(name="Test")
        self.assertEqual(obj.name, "Test")

    def test_model_update(self):
        """Проверка, что объект успешно обновляется"""
        obj = School.objects.get(name="Test")
        obj.name = "Updated Test"
        obj.save()
        updated_obj = School.objects.get(pk=obj.pk)
        self.assertEqual(updated_obj.name, "Updated Test")

    def test_model_deletion(self):
        """Проверка на то, что объект удаляется без проблем"""
        obj = School.objects.get(name="Test")
        obj.delete()
        with self.assertRaises(School.DoesNotExist):
            School.objects.get(name="Test")