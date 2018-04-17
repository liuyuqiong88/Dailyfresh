from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import *
from django.shortcuts import render,redirect
from django.views.generic import View
from django_redis import get_redis_connection

from apps.goods.models import *
from apps.orders.models import *
from django.core.paginator import *
from utils.common import *
# from redis.client import StrictRedis



# Create your views here.



class IndexView(View):
    """显示主页"""



    def get(self,request):
        user = request.user
        context = cache.get('index_page_data')
        # context ={1:2}
        print(context)
        if context is  None:

            print('首页缓存为空，读取数据库数据')
            # 查询首页中要显示的数据
            # 所有商品的类别
            categories = GoodsCategory.objects.all()
            # 主页轮播商品
            slide = IndexSlideGoods.objects.all()
            # 主页促销活动
            promotion = IndexPromotion.objects.all()
            # 主页分类展示
            for i in categories:
                # 查询当前类别所有文字商品和图片商品
                text_skus = IndexCategoryGoods.objects.filter(category=i,display_type=0).order_by('index')
                imgs_skus = IndexCategoryGoods.objects.filter(category=i,display_type=1).order_by('index')
            #     动态地给类别对象，新增属性
                i.text_skus = text_skus
                i.imgs_skus = imgs_skus

            # 购物车数量
            # cart_count = 0

            strict_redis = get_redis_connection()
            strict_redis = get_redis_connection()

            key = 'cart_%s' % user.id
            print(user)
            context = {
                'categorise' : categories,
                'slide' : slide,
                'promotion' : promotion,

            }


            cache.set('index_page_data',context,3600)
        else:
            print('缓存不为空！读取缓存')

        cart_count = 0
        user_id = request.user.id
        strict_redis = get_redis_connection()


        key = 'cart_%s' % user_id

        vals = strict_redis.hvals(key)
        vals = strict_redis.hvals(key)

        for i in vals:
            cart_count += int(i.decode())


        context['cart_count'] =cart_count


        return render(request, 'index.html', context)


class DetailView(View):
    """商品详情界面"""

    def get(self,request,sku_id):

        # 获取所有的类别
        category = GoodsCategory.objects.all()

        try:
            # 获取当前要显示的商品sku
            goods_sku = GoodsSKU.objects.get(id= sku_id)

        except:
            return redirect(reverse('goods:index'))

        # 新品推荐
        new_skus = GoodsSKU.objects.filter(category=goods_sku.category).order_by('-create_time')[0:2]

        # todo :其他商品规格ｓｋｕ
        other_skus = GoodsSKU.objects.filter(spu=goods_sku.spu).exclude(id=sku_id)

        cart_count = 0

        if request.user.is_authenticated():
            strict_redis =get_redis_connection('default')

            cart_key = 'cart_%s' % request.user.id

            vals = strict_redis.hvals(cart_key)

            for i in vals :
                cart_count += int(i)

            history_key = 'history_%s' % request.user.id


            strict_redis.lrem(history_key,0,sku_id)

            strict_redis.lpush(history_key,sku_id)

            strict_redis.ltrim(history_key,0,3)


        context = {
            'category' : category,
            'goods_sku' : goods_sku,
            'new_skus' : new_skus,
            'other_skus' : other_skus,
            'cart_count' : cart_count,
        }

        return render(request,'detail.html',context)


class ListView(View):
    """商品列表"""

    def get(self,request,category_id,page_num):

        # 获取所有的类别
        category = GoodsCategory.objects.all()

        cho_category = None
        try:
            cho_category = GoodsCategory.objects.get(id = category_id)
        except:
            return redirect(reverse('goods:index'))

        # 读取这类商品的所有商品
        skus = GoodsSKU.objects.filter(category=cho_category)

        # 商品是按什么进行排列的
        sort = request.GET.get('sort')


        if sort == 'price':
            skus = skus.order_by('price')
        elif sort == 'hot':
            slus = skus.order_by('sales')



        # 新品推荐
        new_skus = GoodsSKU.objects.filter(category=cho_category).order_by('-create_time')[0:2]

        paginator = Paginator(skus,5)
        page = paginator.page(page_num)


        # 购物车商品数量
        cart_count = 0

        if request.user.is_authenticated():
            strict_redis =get_redis_connection('default')

            cart_key = 'cart_%s' % request.user.id

            vals = strict_redis.hvals(cart_key)

            for i in vals :
                cart_count += int(i)


        context = {
            'cho_category' :cho_category,
            'cart_count':cart_count,
            'category' : category,
            'new_skus' :new_skus,
            'page' : page,
            'paginator' : paginator,
            'sort' : sort,
        }

        return render(request,'list.html',context)

