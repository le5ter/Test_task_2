from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.contrib.auth.forms import UserCreationForm


class RegisterViewTests(TestCase):
    def setUp(self):
        """Настройка для тестов"""
        self.url = reverse('register')
        self.valid_data = {
            'username': 'testuser',
            'password1': '{2An=7,!22^O',
            'password2': '{2An=7,!22^O',
        }
        self.invalid_data = {
            'username': '',
            'password1': 'Asd619^#a8',
            'password2': 'Asd65434',
        }
        self.mismatched_data = {
            'username': 'testuser',
            'password1': 'password123',
            'password2': 'differentpassword',
        }

    def test_register_view_get(self):
        """Тест для отображения страницы регистрации с пустой формой"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], UserCreationForm)

    def test_register_view_post_valid_data(self):
        """Тест для отправки правильных данных на регистрацию"""
        response = self.client.post(self.url, self.valid_data)

        self.assertTrue(User.objects.filter(username='testuser').exists())

        self.assertRedirects(response, reverse('login'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Аккаунт testuser был успешно создан! Теперь вы можете войти.")

    def test_register_view_post_invalid_data(self):
        """Тест для отправки неправильных данных на регистрацию"""
        response = self.client.post(self.url, self.invalid_data)

        self.assertFalse(User.objects.filter(username='').exists())

        self.assertFormError(response.context['form'], 'username', 'This field is required.')

    def test_register_view_post_mismatched_passwords(self):
        """Тест для отправки данных с несовпадающими паролями"""

        response = self.client.post(self.url, self.mismatched_data)

        self.assertFormError(response.context['form'], 'password2', 'The two password fields didn’t match.')

        self.assertFalse(User.objects.filter(username='testuser').exists())
