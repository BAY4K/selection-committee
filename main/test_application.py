from datetime import timedelta
from io import BytesIO

from captcha.models import CaptchaStore
from django.test import TestCase, Client
from django.utils import timezone
from PIL import Image

from main.captcha import readable_challenge
from main.models import Applicant


class ApplicationCaptchaTests(TestCase):
    def payload(self, response=None):
        key = CaptchaStore.generate_key()
        store = CaptchaStore.objects.get(hashkey=key)
        return {
            'last_name': 'Иванов', 'first_name': 'Иван', 'patronymic': 'Иванович',
            'gender': 'Мужской', 'birth_date': '2008-04-12', 'school': 'Школа № 1',
            'graduation_date': str(timezone.now().year), 'email': 'test@example.com',
            'captcha_0': key, 'captcha_1': store.response if response is None else response,
            'accept': 'on',
        }

    def test_challenge_avoids_ambiguous_characters(self):
        for _ in range(50):
            challenge, response = readable_challenge()
            self.assertEqual(len(challenge), 5)
            self.assertEqual(challenge.lower(), response)
            self.assertFalse(set(challenge) & set('01ILO'))

    def test_captcha_image_and_refresh(self):
        response = self.client.get('/captcha/refresh/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(CaptchaStore.objects.filter(hashkey=data['key']).exists())
        image = self.client.get(data['image_url'])
        self.assertEqual(image.status_code, 200)
        self.assertEqual(image['Content-Type'], 'image/png')
        self.assertEqual(Image.open(BytesIO(image.content)).size, (220, 72))

    def test_valid_code_saves_and_cannot_be_reused(self):
        payload = self.payload()
        payload['captcha_1'] = payload['captcha_1'].upper()
        self.assertRedirects(self.client.post('/form/', payload), '/')
        self.assertEqual(Applicant.objects.count(), 1)
        self.assertFalse(CaptchaStore.objects.filter(hashkey=payload['captcha_0']).exists())
        payload['email'] = 'second@example.com'
        response = self.client.post('/form/', payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('captcha', response.context['form'].errors)
        self.assertEqual(Applicant.objects.count(), 1)

    def test_wrong_code_preserves_other_fields(self):
        response = self.client.post('/form/', self.payload('wrong'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('captcha', response.context['form'].errors)
        self.assertContains(response, 'value="Иванов"')
        self.assertContains(response, 'Код неверный или истёк')
        self.assertEqual(Applicant.objects.count(), 0)

    def test_expired_code_is_rejected(self):
        payload = self.payload()
        CaptchaStore.objects.filter(hashkey=payload['captcha_0']).update(expiration=timezone.now() - timedelta(minutes=1))
        response = self.client.post('/form/', payload)
        self.assertIn('captcha', response.context['form'].errors)
        self.assertEqual(Applicant.objects.count(), 0)

    def test_consent_is_required_on_server(self):
        payload = self.payload()
        del payload['accept']
        response = self.client.post('/form/', payload)
        self.assertIn('accept', response.context['form'].errors)
        self.assertEqual(Applicant.objects.count(), 0)

    def test_csrf_protects_submission(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/form/', self.payload()).status_code, 403)

    def test_success_message_and_archive_present(self):
        self.assertContains(self.client.post('/form/', self.payload(), follow=True), 'Заявка отправлена!')
        self.assertContains(self.client.get('/'), 'Архив · 2023–2024')
