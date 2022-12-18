from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        cls.author_create = User.objects.create_user(username='author')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author_create,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.author_create)

    def test_urls_uses_correct_template(self):
        """Тест для проверки: URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'index.html',
            '/group/test_group/': 'group_list.html',
            f'/posts/{PostURLTests.post.id}/': 'post_detail.html',
            f'/profile/{PostURLTests.author_create.username}/': 'profile.html',
            f'/posts/{PostURLTests.post.id}/edit/': 'create_post.html',
            '/create/': 'create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, f'posts/{template}')

    def test_OK_status_for_pages(self):
        """Тест для проверки: При переходе на страницу всё хорошо."""
        url_name_status = {
            '/': self.guest_client.get(
                '/'
            ),
            '/group/test_group/': self.guest_client.get(
                '/group/test_group/'
            ),
            f'/posts/{PostURLTests.post.id}/': self.guest_client.get(
                f'/posts/{PostURLTests.post.id}/'
            ),
            f'/profile/{PostURLTests.author_create.username}/':
                self.guest_client.get(
                    f'/profile/{PostURLTests.author_create.username}/'
            ),
            f'/posts/{PostURLTests.post.id}/edit/': self.authorized_client.get(
                f'/posts/{PostURLTests.post.id}/edit/'
            ),
            '/create/': self.authorized_client.get(
                '/create/'
            ),
        }
        for url, status in url_name_status.items():
            with self.subTest(url=url):
                self.assertEqual(status.status_code, HTTPStatus.OK)

    def test_redirects(self):
        """Тест для проверки: редиректов"""
        self.another_user_create = User.objects.create_user(username='another')
        self.another_user_client = Client()
        self.another_user_client.force_login(self.another_user_create)
        user_redirect_to = {
            f'/posts/{PostURLTests.post.id}/': self.another_user_client.get(
                f'/posts/{PostURLTests.post.id}/edit/', follow=True
            ),
            '/auth/login/?next=/create/': self.guest_client.get(
                '/create/', follow=True
            ),
        }
        for url, redirect in user_redirect_to.items():
            with self.subTest(url=url):
                self.assertRedirects(redirect, url)

    def test_error_404(self):
        """Тест для проверки: Ошибки при переходе на несуществующую страницу"""
        users = [
            self.guest_client,
            self.authorized_client,
        ]
        for user in users:
            with self.subTest(user=user):
                self.assertEqual(
                    user.get('/unexciting_page/').status_code,
                    HTTPStatus.NOT_FOUND,
                )
