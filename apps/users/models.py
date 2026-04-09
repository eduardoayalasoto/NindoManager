from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.common.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    whatsapp_number = models.CharField(
        max_length=20, blank=True,
        help_text="Número con código de país, ej: 5215512345678"
    )
    whatsapp_notifications = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return self.get_full_name() or self.username

    def get_primary_branch(self):
        role = self.user_roles.filter(is_active=True).first()
        return role.branch if role else None

    def get_accessible_branches(self):
        from apps.branches.models import Branch
        from apps.common.permissions import user_has_role, ROLE_GERENTE
        if self.is_superuser or user_has_role(self, ROLE_GERENTE):
            return Branch.objects.filter(is_active=True)
        branch_ids = self.user_roles.filter(
            is_active=True
        ).values_list("branch_id", flat=True)
        return Branch.objects.filter(id__in=branch_ids, is_active=True)
