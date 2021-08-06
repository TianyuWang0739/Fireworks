from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.urls import reverse


class Category(models.Model):
    NAME_MAX_LENGTH = 128

    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Page(models.Model):
    TITLE_MAX_LENGTH = 128
    URL_MAX_LENGTH = 200

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=TITLE_MAX_LENGTH)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        return self.user.username


class Product(models.Model):
    SIZE_CHOICES = (
        ('Small', 'Small'),
        ('Middle', 'Middle'),
        ('Big', 'Big')
    )

    TYPE_CHOICES = (
        ('Beans', 'Beans'),
        ('Milk', 'Milk')
    )

    SWEETNESS_CHOICES = (
        ('100%', '100%'),
        ('70%', '70%'),
        ('30%', '30%')

    )

    name = models.CharField(max_length=255)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES)
    type = models.CharField(max_length=255, choices=TYPE_CHOICES)
    sweetness = models.CharField(max_length=10, choices=SWEETNESS_CHOICES)
    img = models.ImageField(upload_to='products')
    location = models.TextField()

    def get_absolute_url(self):
        return reverse('rango:product-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name


class FavoritePage(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class FavoriteProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.user
