from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch

User = get_user_model()

class SocialAuthTests(TestCase):
    def setUp(self):
        self.email = 'testuser@example.com'
        self.password = 'securepassword'
        self.user = User.objects.create_user(email=self.email, password=self.password, is_active=False)

    @patch('social_core.pipeline.social_auth.social_user')
    def test_user_activated_on_social_auth(self, mock_social_user):
        # Патчите метод `social_user` чтобы избежать фактической активации пользователя в тесте
        mock_social_user.return_value = None

        # Симуляция успешной аутентификации через социальную сеть
        response = self.client.get(reverse('social:complete', kwargs={'backend': 'github'}), data={
            'code': 'dummy_code',  # используйте фальшивый код для теста
            'state': 'dummy_state'
        })

        # Проверьте, что метод активации был вызван
        mock_social_user.assert_called_once()

        # Проверьте, что пользователь теперь активен
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

        # Проверьте, что редирект на нужную страницу выполнен
        self.assertRedirects(response, reverse('web:profile'))
