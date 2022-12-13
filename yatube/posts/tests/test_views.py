from django import forms
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostViewTests(TestCase):
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
            author=PostViewTests.author_create,
            group=PostViewTests.group
        )
        cls.post1 = Post.objects.create(
            text='Тестовый текст1',
            author=PostViewTests.author_create,
            group=PostViewTests.group
        )
        cls.post2 = Post.objects.create(
            text='Тестовый текст2',
            author=PostViewTests.author_create,
            group=PostViewTests.group
        )
        cls.post3 = Post.objects.create(
            text='Тестовый текст3',
            author=PostViewTests.author_create,
            group=PostViewTests.group
        )
        cls.post4 = Post.objects.create(
            text='Тестовый текст4',
            author=PostViewTests.author_create,
            group=PostViewTests.group
        )
        cls.post5 = Post.objects.create(
            text='Тестовый текст5',
            author=PostViewTests.author_create,
            group=PostViewTests.group
        )
        cls.post6 = Post.objects.create(
            text='Тестовый текст6',
            author=PostViewTests.author_create,
            group=PostViewTests.group
        )
        cls.post7 = Post.objects.create(
            text='Тестовый текст7',
            author=PostViewTests.author_create,
            group=PostViewTests.group
        )
        cls.post8 = Post.objects.create(
            text='Тестовый текст8',
            author=PostViewTests.author_create,
            group=PostViewTests.group
        )
        cls.post9 = Post.objects.create(
            text='Тестовый текст9',
            author=PostViewTests.author_create,
            group=PostViewTests.group
        )
        cls.post10 = Post.objects.create(
            text='Тестовый текст10',
            author=PostViewTests.author_create,
            group=PostViewTests.group
        )
        cls.post11 = Post.objects.create(
            text='Тестовый текст11',
            author=PostViewTests.author_create,
            group=PostViewTests.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewTests.author_create)

    def test_views_uses_correct_template(self):
        """Тест для проверки: view использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewTests.group.slug},
            ): 'group_list.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewTests.post.id},
            ): 'post_detail.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostViewTests.author_create.username},
            ): 'profile.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostViewTests.post.id},
            ): 'create_post.html',
            reverse('posts:post_create'): 'create_post.html',
        }
        for view, template in templates_pages_names.items():
            with self.subTest(view=view):
                response = self.authorized_client.get(f'posts:{view}')
                self.assertTemplateUsed(response, f'posts/{template}')

    def test_index_profile_group_page_show_correct_context(self):
        """
        Тест для проверки: Правильный context для страниц index,
        group_list, profile
        """
        response_page = {
            self.authorized_client.get(reverse('posts:index')): 'index',
            self.authorized_client.get(reverse(
                'posts:group_list',
                kwargs={'slug': PostViewTests.group.slug},
            )): 'group_list',
            self.authorized_client.get(reverse(
                'posts:profile',
                kwargs={'username': PostViewTests.author_create.username},
            )): 'profile',
        }
        for response, page in response_page.items():
            with self.subTest(page=page):
                first_object = response.context['page_obj'][0]
                post_text_0 = first_object.text
                post_author_0 = first_object.author
                post_group_0 = first_object.group
                self.assertEqual(post_text_0, 'Тестовый текст11')
                self.assertEqual(post_author_0, PostViewTests.author_create)
                self.assertEqual(post_group_0, PostViewTests.group)

    def test_post_detail_page_show_correct_context(self):
        """Тест для проверки: Правильный context для страницы page_detail"""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewTests.post.id},
            )
        )
        self.assertEqual(response.context.get('post').text, 'Тестовый текст')
        self.assertEqual(
            response.context.get('post').author,
            PostViewTests.author_create,
        )
        self.assertEqual(
            response.context.get('post').group,
            PostViewTests.group,
        )
        self.assertEqual(
            response.context.get('title'),
            PostViewTests.post.text[:30]
        )

    def test_create_edit_page_forms(self):
        """Тест для проверки: Форм на страницах create, post_edit"""
        response_page = {
            'posts:post_create': self.authorized_client.get(reverse(
                'posts:post_create',
            )),
            'posts:post_edit': self.authorized_client.get(reverse(
                'posts:post_edit',
                kwargs={'post_id': PostViewTests.post.id},
            )),
        }
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for page, response in response_page.items():
            for value, expected in form_fields.items():
                with self.subTest(page=page, value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_pagintor_first_page_contains_10_posts(self):
        """
        Тест для проверки:
        Правильности работы первой страницы паджинатора на страницах:
        index, profile, group_list
        """
        response_page = {
            'posts:index': self.authorized_client.get(reverse(
                'posts:index',
            )),
            'posts:profile': self.authorized_client.get(reverse(
                'posts:profile',
                kwargs={'username': PostViewTests.author_create.username},
            )),
            'posts:group_list': self.authorized_client.get(reverse(
                'posts:group_list',
                kwargs={'slug': PostViewTests.group.slug},
            )),
        }
        for page, response in response_page.items():
            with self.subTest(page=page):
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_pagintor_second_page_contains_2_posts(self):
        """
        Тест для проверки:
        Правильности работы второй страницы паджинатора на страницах:
        index, profile, group_list
        """
        response_page = {
            'posts:index': self.authorized_client.get(reverse(
                'posts:index',
            ) + '?page=2'),
            'posts:profile': self.authorized_client.get(reverse(
                'posts:profile',
                kwargs={'username': PostViewTests.author_create.username},
            ) + '?page=2'),
            'posts:group_list': self.authorized_client.get(reverse(
                'posts:group_list',
                kwargs={'slug': PostViewTests.group.slug},
            ) + '?page=2'),
        }
        for page, response in response_page.items():
            with self.subTest(page=page):
                self.assertEqual(len(response.context['page_obj']), 2)
