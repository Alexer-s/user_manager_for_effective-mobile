from django.db import models
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
    """Кастомная модель пользователя. Пользователю доступна только одна роль."""
    role = models.ForeignKey(
        'Role',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Роль пользователя'
    )
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='myuser_set',
        blank=True,
        verbose_name='Группы'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='myuser_set',
        blank=True,
        verbose_name='Права пользователя'
    )

    def __str__(self):
        return f'{self.username} ({self.role})' if self.role else self.username


class Role(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название роли'
    )

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.name


class BisinessElement(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название бизнес-элемента'
    )

    class Meta:
        verbose_name = 'Бизнес-элемент'
        verbose_name_plural = 'Бизнес-элементы'

    def __str__(self):
        return self.name


class AccessRoleRule(models.Model):
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        verbose_name='Роль'
    )
    element = models.ForeignKey(
        BisinessElement,
        on_delete=models.CASCADE,
        verbose_name='Бизнес-элемент'
    )
    can_read_own = models.BooleanField(
        default=False,
        verbose_name='Просмотр своих'
    )
    can_read_all = models.BooleanField(
        default=False,
        verbose_name='Просмотр всех'
    )
    can_create = models.BooleanField(
        default=False,
        verbose_name='Создание'
    )
    can_update_own = models.BooleanField(
        default=False,
        verbose_name='Редактирование своих'
    )
    can_update_all = models.BooleanField(
        default=False,
        verbose_name='Редактирование всех'
    )
    can_delete_own = models.BooleanField(
        default=False,
        verbose_name='Удаление своих'
    )
    can_delete_all = models.BooleanField(
        default=False,
        verbose_name='Удаление всех'
    )

    class Meta:
        verbose_name = 'Правило доступа для роли'
        verbose_name_plural = 'Правила доступа для ролей'
        unique_together = ('role', 'element')

    def __str__(self):
        return f'Роль: {self.role}, Элемент: {self.element}'
