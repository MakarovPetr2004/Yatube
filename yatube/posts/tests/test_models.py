from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_post_str(self):
        post = PostModelTest.post
        str_expected = post.text[:15]
        self.assertEqual(str_expected, str(post))

    def test_group_str(self):
        group = PostModelTest.group
        str_expected = group.title
        self.assertEqual(str_expected, str(group))
