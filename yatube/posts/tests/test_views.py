import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..models import Post, Group, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.objs = (Post(
            id=i + 1,
            text=f'Тестовый текст{i}',
            author=cls.author_create,
            group=cls.group,
            image=cls.uploaded,
        ) for i in range(12))
        cls.test_posts = Post.objects.bulk_create(cls.objs)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

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
                kwargs={'post_id': PostViewTests.test_posts[0].id},
            ): 'post_detail.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostViewTests.author_create.username},
            ): 'profile.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostViewTests.test_posts[0].id},
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
                post_image_0 = first_object.image
                self.assertEqual(post_text_0, 'Тестовый текст11')
                self.assertEqual(post_author_0, PostViewTests.author_create)
                self.assertEqual(post_group_0, PostViewTests.group)
                self.assertEqual(
                    post_image_0,
                    PostViewTests.test_posts[-1].image
                )

    def test_post_detail_page_show_correct_context(self):
        """Тест для проверки: Правильный context для страницы page_detail"""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewTests.test_posts[0].id},
            )
        )
        self.assertEqual(response.context.get('post').text, 'Тестовый текст0')
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
            PostViewTests.test_posts[0].text[:30]
        )

    def test_create_edit_page_forms(self):
        """Тест для проверки: Форм на страницах create, post_edit"""
        response_page = {
            'posts:post_create': self.authorized_client.get(reverse(
                'posts:post_create',
            )),
            'posts:post_edit': self.authorized_client.get(reverse(
                'posts:post_edit',
                kwargs={'post_id': PostViewTests.test_posts[0].id},
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


class CommentViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.author_create = User.objects.create_user(username='author')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author= cls.author_create,
        )
        cls.comment = Comment.objects.create(
            text='Тестовый текст для комментария',
            author=cls.author_create,
            post=cls.post,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewTests.author_create)

    def comment_on_post_detail_page(self):
        """Тест для проверки: добавления комментария на страницу post_detail"""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewTests.post.id},
            )
        )
        self.first_comment = response.context.get('comments')[0]
        self.assertEqual(
            self.first_comment.text,
            'Тестовый текст для комментария',
        )
        self.assertEqual(
            self.first_comment.author,
            PostViewTests.author_create,
        )
        self.assertEqual(
            self.first_comment.post,
            PostViewTests.group,
        )
