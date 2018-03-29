from django.contrib import admin

# Register your models here.
from apps.goods.models import *

admin.site.register(GoodsCategory)
# admin.site.register(GooodsSPU)
# admin.site.register(GoodsSKU)
admin.site.register(GoodsImage)
admin.site.register(IndexCategoryGoods)
admin.site.register(IndexPromotion)