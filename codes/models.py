from django.db import models

# Create your models here.
class Code(models.Model):
    token_id = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    liked_by = models.ManyToManyField(
        "users.User",
        related_name="liked_codes",
        blank=True,
    )
