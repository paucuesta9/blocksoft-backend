from django.db import models

# Create your models here.
class User(models.Model):
    hash = models.CharField(max_length=42, unique=True)
    nonce = models.CharField(max_length=100)
    name = models.CharField(max_length=100, null=True)
    username = models.CharField(max_length=50, null=True)
    email = models.EmailField(max_length=100, null=True)
    description = models.TextField(max_length=1000, null=True)
    image = models.ImageField(upload_to="images/", null=True)
    githubToken = models.CharField(max_length=100, null=True)
    github = models.CharField(max_length=100, null=True)
    twitter = models.CharField(max_length=100, null=True)
    linkedin = models.CharField(max_length=100, null=True)
    website = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.username

