from django.contrib import admin

# Register your models here.
from apps.goods.models import *
from celery_tasks.tasks import generate_static_index_html
from django.contrib import admin
from django.core.cache import cache

class BaseAdmin(admin.ModelAdmin):
    """模型管理类父类"""

    def save_model(self, request, obj, form, change):

        """管理员在管理后台新增/修改了数据后,会执行此方法"""
        super().save_model(request, obj, form, change)

        #         重新生成首页静态页面
        generate_static_index_html.delay()
        #         删除缓存数据
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        """管理员在后台删除数据时会调用此方法"""
        super().delete_model(request,obj)
        #         重新生成首页静态页面

        generate_static_index_html.delay()
        # 删除缓存数据
        cache.delete('index_page_data')


class GoodsCategoryAdmin(BaseAdmin):
    pass
class GooodsSPUAdmin(BaseAdmin):
    pass
class GoodsSKUyAdmin(BaseAdmin):
    pass
class GoodsImageAdmin(BaseAdmin):
    pass
class IndexCategoryGoodsAdmin(BaseAdmin):
    pass
class IndexPromotionAdmin(BaseAdmin):
    pass

admin.site.register(GoodsCategory,GoodsCategoryAdmin)
admin.site.register(GooodsSPU,GooodsSPUAdmin)
admin.site.register(GoodsSKU,GoodsSKUyAdmin)
admin.site.register(GoodsImage,GoodsImageAdmin)
admin.site.register(IndexCategoryGoods,IndexCategoryGoodsAdmin)
admin.site.register(IndexPromotion,IndexPromotionAdmin)