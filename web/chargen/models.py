from django.db import models

# Create your models here.

class CharApp(models.Model):
    app_id = models.AutoField(primary_key=True)
    sexus = models.CharField(max_length=10, verbose_name = 'sexus persōnae')
    gens = models.CharField(max_length=12, verbose_name = 'gens persōnae')
    praenomen = models.CharField(max_length=12, verbose_name = 'praenōmen persōnae')
    account_id = models.IntegerField(default=1, verbose_name='Account ID')
    submitted = models.BooleanField(default=False)
