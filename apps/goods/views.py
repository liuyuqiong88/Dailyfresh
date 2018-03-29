from django.http import *
from django.shortcuts import render
from django.views.generic import View
from apps.goods.models import *
from apps.orders.models import *

# Create your views here.
def index(request):

    login_user = request.user
    print(login_user)

    order = None
    try:
        usr = User.objects.get(id=login_user.id)
        order = OrderInfo.objects.filter(user=usr)
    except:
        pass

    data = {
        'order' :order
    }


    return render(request, 'index2.html', data)


class IndexView(View):
    """显示主页"""

    def get(self,request):

        # 查询首页中要显示的数据
        # 所有商品的类别
        gategories = GoodsCategory.objects.all()
        # 主页轮播商品
        slide = IndexSlideGoods.objects.all()
        # 主页促销活动
        promotion = IndexPromotion.objects.all()
        # 主页分类展示
        for i in gategories:
            # 查询当前类别所有文字商品和图片商品
            text_skus = IndexCategoryGoods.objects.filter(category=i,display_type=0).order_by('index')
            imgs_skus = IndexCategoryGoods.objects.filter(category=i,display_type=1).order_by('index')
        #     动态地给类别对象，新增属性
            i.text_skus = text_skus
            i.imgs_skus = imgs_skus

        cart_count = 12

        data = {
            'gategorise' : gategories,
            'slide' : slide,
            'promotion' : promotion,
            'cart_count' : cart_count,

        }
        # print(gategories[0][0].imgs_skus.sku.name)


        return render(request, 'index.html', data)