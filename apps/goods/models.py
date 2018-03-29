from django.db import models
from utils.models import *
from tinymce.models import HTMLField

# Create your models here.


class GoodsCategory(BaseMedel):
    """商品类别表"""

    name = models.CharField(max_length=20,verbose_name='类别名称')
    logo = models.CharField(max_length=100,verbose_name='图片标识')
    image = models.ImageField(upload_to='category',verbose_name='类别图片')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'df_goods_category'
        verbose_name = '商品类别'
        verbose_name_plural = verbose_name


class GooodsSPU(BaseMedel):
    """商品SPU表"""

    name = models.CharField(max_length=100,verbose_name='名称')
    desc = HTMLField(blank=True,default='',verbose_name='商品描述')  #HTMLField富文本框

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'df_goods_spu'
        verbose_name = '商品'
        verbose_name_plural = verbose_name



class GoodsSKU(BaseMedel):
    """商品SKU表"""

    name = models.CharField(max_length=100,verbose_name='名称')
    title = models.CharField(max_length=200,verbose_name='简介')
    unit = models.CharField(max_length=10,verbose_name='销售单位')
    print = models.DecimalField(max_digits=10,decimal_places=2,verbose_name='价格')
    stock = models.IntegerField(default=0,verbose_name='库存')
    sales = models.IntegerField(default=0,verbose_name='销量')
    default_image = models.ImageField(upload_to='goods',verbose_name='图片')
    status = models.BooleanField(default=True,verbose_name='是否上线')
    category = models.ForeignKey(GoodsCategory,verbose_name='类别')
    spu = models.ForeignKey(GooodsSPU,verbose_name='商品SPU')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'df_goods_sku'
        verbose_name = '商品SKU'
        verbose_name_plural = verbose_name


class GoodsImage(BaseMedel):
    """商品图片"""

    image = models.ImageField(upload_to='goods',verbose_name='图片')
    sku = models.ForeignKey(GoodsSKU, verbose_name='商品SKU')

    def __str__(self):
        return str(self.sku)

    class Meta:
        verbose_name = '商品图片'
        verbose_name_plural = verbose_name

class IndexSlideGoods(BaseMedel):
    """主页轮播商品展示"""

    image = models.ImageField(upload_to='banner',verbose_name='图片')
    index = models.SmallIntegerField(default=0, verbose_name='顺序')
    sku = models.ForeignKey(GoodsSKU,verbose_name='商品SKU')

    def __str__(self):
        return str(self.sku)

    class Meta:
        db_table = 'df_index_slide_goods'
        verbose_name = '主页轮播商品'
        verbose_name_plural = verbose_name


class IndexCategoryGoods(BaseMedel):
    """主页分类商品展示"""

    DISPLAY_TYPE_CJOIES = (
        (0,'标题'),
        (1,'图片'),
    )

    display_type = models.SmallIntegerField(choices=DISPLAY_TYPE_CJOIES, verbose_name='展示类型')
    index = models.SmallIntegerField(default=0,verbose_name='顺序')
    category = models.ForeignKey(GoodsCategory,verbose_name='商品类别')
    sku = models.ForeignKey(GoodsSKU,verbose_name='商品SKU')

    def __str__(self):
        return str(self.sku)

    class Meta:
        db_table = 'df_index_category_goods'
        verbose_name = '主页分类展示商品'
        verbose_name_plural = verbose_name


class IndexPromotion(BaseMedel):
    """主页促销活动展示"""
    class Meta:
        db_table = 'df_index_promotion'
        verbose_name = '主页促销活动'
        verbose_name_plural = verbose_name


    name = models.CharField(max_length=50,verbose_name='活动名称')
    url = models.CharField(max_length=100,verbose_name='活动链接')
    image = models.ImageField(upload_to='banner',verbose_name='图片')
    index = models.SmallIntegerField(default=0,verbose_name='顺序')

    def __str__(self):
        return self.name

