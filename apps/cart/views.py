from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic import View
from django_redis import get_redis_connection

from apps.goods.models import *
from utils.common import *


class AddCartView(BaseView):
    """添加到购物车"""

    def get(self, request):

        pass

    def post(self, request):

        # 判断用户是否登陆
        user = request.user
        if user.is_authenticated():
            # 接收数据：user_id，sku_id，count
            user_id = user.id
            sku_id = request.POST.get('sku_id')

            count = request.POST.get('count')

            print(sku_id, count)
            # 校验参数all()
            if not all([sku_id, count]):
                return JsonResponse({'code': 2, 'errmsg': '参数不能为空'})

            # 判断商品是否存在


            try:
                sku = GoodsSKU.objects.get(id=sku_id)
            except:
                return JsonResponse({'code': 3, 'errmsg': '商品不存在'})

            # 判断count是否是整数

            try:
                count = int(count)
            except:
                return JsonResponse({'code': 4, 'errmsg': '商品数量必须为整数'})

            # 判断库存


            strict_redis = get_redis_connection()

            key = 'cart_%s' % user.id

            val = strict_redis.hget(key, sku_id)

            if val:
                count += int(val)

            if count > sku.stock:
                return JsonResponse({'code': 5, 'errmsg': '库存不足'})

            # 操作redis数据库存储商品到购物车
            strict_redis.hset(key, sku_id, count)
            # 查询购物车中商品的总数量
            cart_count = 0
            vals = strict_redis.hvals(key)

            for val in vals:
                cart_count += int(val)

            # json方式响应添加购物车结果
            context = {
                'code': '0',
                'cart_count': cart_count,
            }

            return JsonResponse(context)


class CartInfoView(LoginRequiredView,View):
    """显示购物车"""

    def get(self, request):

        user = request.user

        if user.is_authenticated():
            strict_redis = get_redis_connection()

            key = 'cart_%s' % user.id
            skus = []

            sku_ids = strict_redis.hkeys(key)
            print()
            price_sum = 0
            count_sum = 0

            for sku_id in sku_ids:
                sku_id = sku_id.decode()
                sku = GoodsSKU.objects.get(id=sku_id)
                sku.goods_count = strict_redis.hget(key, sku_id).decode()

                sku.good_sum = (float(sku.price) * float(sku.goods_count))

                count_sum += int(sku.goods_count)
                price_sum += sku.good_sum
                skus.append(sku)

            data = {
                'skus': skus,
                'price_sum': price_sum,
                'count_sum': count_sum,
                'user' : user,
            }
        return render(request, 'cart.html', data)


class UpdateCartView(View):
    """更新购物车数据：+ -"""

    def post(self, request):


        # 获取登录用户
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({'code': 1, 'errmsg': '请先登录'})

        sku_id = request.POST.get('sku_id')
        # 获取参数：sku_id, count
        count = request.POST.get('count')
    # 校验参数all()
        if not all([sku_id, count]):
            return JsonResponse({'code': 1, 'errmsg': '参数不能为空'})
    # 判断商品是否存在
        try:
            sku = GoodsSKU.objects.get(id = sku_id)
        except:
            return JsonResponse({'code': 1, 'errmsg': '请求商品不存在'})
        # 判断count是否是整数
        try:
            count = int(count)
        except:
            return JsonResponse({'code': 1, 'errmsg': '购买数量参数不正确'})
        # 判断库存
        if (sku.stock<count):
            return JsonResponse({'code': 1, 'errmsg': '库存不足'})
    # 如果用户登陆，将修改的购物车数据存储到redis中

        strict_redis = get_redis_connection()
        key = "cart_%s" %user.id

        strict_redis.hset(key,sku_id,count)
    # 计算商品的总数量, 并响应请求

        total_count = 0
        vals = strict_redis.hvals(key)

        for i in vals:
            total_count += int(i.decode())

        data = {
            'code': 1,
             'message': '改商品数量成功',
             'total_count' : total_count,
             }
        return JsonResponse(data)



