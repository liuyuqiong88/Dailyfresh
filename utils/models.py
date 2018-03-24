from django.db import models

# Create your models here.


class BaseMedel(models.Model):
    """模型类基类"""

    create_time = models.DateTimeField(auto_now_add=True,null=True,verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True,null=True,verbose_name='更改时间')

    delete = models.SmallIntegerField(default=False,verbose_name='是否删除')


    class Meta(object):
        # 指定基类模型类为抽象类，否则迁移生成表时会出错
        abstract =True