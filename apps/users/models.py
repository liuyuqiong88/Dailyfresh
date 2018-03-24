from django.db import models
from django.contrib.auth.models import *
from utils.models import *
from tinymce.models import HTMLField


# Create your models here.

class User(BaseMedel,AbstractUser):
    """用户信息模型类"""

    class Meta(object):
        db_table = "db_user"

    def __str__(self):

        return self.username


class Address(BaseMedel):
    """地址"""

    receiver_name = models.CharField(max_length=20,verbose_name='收件人')
    receiver_mobile = models.CharField(max_length=11,verbose_name='联系电话')
    detail_addr = models.CharField(max_length=256,verbose_name='详细地址')
    zip_code = models.CharField(max_length=6,null=True,verbose_name='邮件编码')
    is_default = models.BooleanField(default=False,verbose_name='默认地址')

    user = models.ForeignKey(User, verbose_name='所属用户')

    class Meta:
        db_table = 'df_address'

class TestModel(BaseMedel):


    GENDER_CHOICES = (
        (0,'男'),
        (1,'女'),
    )
    gender = models.SmallIntegerField(default=0,choices=GENDER_CHOICES)

    # 福文本文框
    desc = HTMLField(verbose_name='商品描述',null=True)