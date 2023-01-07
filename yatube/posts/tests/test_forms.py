import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from ..forms import PostForm, CommentForm
from ..models import Post, Group, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
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
            group=cls.group
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.author_create)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'group': PostCreateFormTests.group.id,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.author_create.username}
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                group=PostCreateFormTests.group,
                author=PostCreateFormTests.author_create,
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый тестовый текст',
            'group': PostCreateFormTests.group.id,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostCreateFormTests.post.id},
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': PostCreateFormTests.post.id},
        ))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Новый тестовый текст',
                group=PostCreateFormTests.group,
                author=PostCreateFormTests.author_create,
            ).exists()
        )

    def test_guest_can_not_create_post(self):
        """Незарегистрированный пользователь не может создать запись"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': PostCreateFormTests.group.id,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_guest_can_not_edit_post(self):
        """Незарегистрированный пользователь не может редактировать запись"""
        form_data = {
            'text': 'Новый тестовый текст',
            'group': PostCreateFormTests.group.id,
        }
        response = self.guest_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostCreateFormTests.post.id},
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')
        self.assertFalse(
            Post.objects.filter(
                text='Новый тестовый текст',
                group=PostCreateFormTests.group,
                author=PostCreateFormTests.author_create,
            ).exists()
        )


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_create = User.objects.create_user(username='author')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author_create,
        )
        cls.form = CommentForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(
            CommentCreateFormTests.author_create
        )

    def test_guest_can_not_create_comment(self):
        """
        Незарегистрированный пользователь не может оставить комментарий
        """
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'post': CommentCreateFormTests.post
        }
        response = self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': CommentCreateFormTests.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/auth/login/?next=/posts/1/comment/')
        self.assertEqual(Comment.objects.count(), comment_count)

    def test_add_comment(self):
        """Валидная форма создает запись в Post."""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый текст комментария',
            'post': CommentCreateFormTests.post,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': CommentCreateFormTests.post.id},
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': CommentCreateFormTests.post.id}
        ))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый текст комментария',
                author=CommentCreateFormTests.author_create,
            ).exists()
        )
