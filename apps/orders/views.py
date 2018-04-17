from datetime import datetime
from time import sleep

from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
# Create your views here.
from django.views.generic import View
from django_redis import get_redis_connection
from redis.client import StrictRedis

from apps.goods.models import GoodsSKU
from apps.orders.models import OrderInfo, OrderGoods
from apps.users.models import Address
from utils.common import *


class UserOrderView(LoginRequiredView, View):
    """用户中心:订单显示界面"""

    def get(self, request, page_num):
        user = request.user
        orders = OrderInfo.objects.filter(user=user).order_by("-create_time")

        orders_goods_list = []
        for order in orders:
            order.order_goods = OrderGoods.objects.filter(order=order)
            order.order_price = 0
            for order_good in order.order_goods:
                order_good.sum_price = order_good.count * order_good.price
                order.order_price += order_good.sum_price




        paginator = Paginator(orders, 2)
        page = paginator.page(page_num)
        data = {
            'which_page': 1,
            'orders': orders,
            'orders_goods_list': orders_goods_list,
            'paginator': paginator,
            'page': page,
        }

        return render(request, 'user_center_order.html', data)


class PlaceOrderView(LoginRequiredView, View):
    def post(self, request):
        """进入确认订单界面"""
        user = request.user
        # 获取请求参数：sku_ids
        sku_ids = request.POST.getlist('sku_ids')

        # 校验参数不能为空
        if not all([user, sku_ids]):
            # 如果sku_ids为空，则重定向到购物车,让用户重选商品
            return redirect(reverse('cart:info'))
            # 获取用户地址信息(此处使用最新添加的地址)
        try:
            user_addr = Address.objects.get(user=user)
        except:
            user_addr = None

            # todo: 查询购物车中的所有的商品

            # 循环操作每一个订单商品
        strict_redis = get_redis_connection()

        sku_list = []

        cart_count = 0
        sum_price = 0

        for sku_id in sku_ids:

            try:
                # 查询一个商品对象
                sku = GoodsSKU.objects.get(id=sku_id)
            except:
                return redirect(reverse('cart:info'))

            key = "cart_%s" % user.id
            # 获取商品数量和小计金额(需要进行数据类型转换)
            # 新增实例属性,以便在模板界面中显示

            sku.sku_count = strict_redis.hget(key, sku_id)

            sku.sku_count = int(sku.sku_count.decode())
            sku.sku_sum_price = sku.price * sku.sku_count

            # 添加商品对象到列表中
            sku_list.append(sku)


            # 累计商品总数量和总金额
            cart_count += sku.sku_count
            sum_price += sku.sku_sum_price


            # 运费(运费模块)

        trans_cost = 10
        # 实付金额
        all_sum = trans_cost + sum_price

        # 定义模板显示的字典数据
        context = {
            'sku_list': sku_list,
            'cart_count': cart_count,
            'sum_price': sum_price,
            'user_addr': user_addr,
            'trans_cost': trans_cost,
            'all_sum': all_sum,
            'sum_price': sum_price,

        }
        # 响应结果: 返回确认订单html界面

        return render(request, 'place_order.html', context)


class DeleteOrderView(View):
    """删除购物车里一条商品"""

    def post(self,request):

        user = request.user

        if user.is_authenticated():

            sku_id = request.POST.get('sku_id')

            strict_redis = get_redis_connection()
            key = 'cart_%s' % user.id

            result = strict_redis.hdel(key,sku_id)

            print(result)

            return JsonResponse({'code': 0, 'errmsg': '订单修改成功'})




class CommitOrderView(View):
    """提交订单"""

    def post(self, request):
        # 登录判断
        user = request.user

        if (user.is_authenticated()):
            # 获取请求参数：address_id, pay_method, sku_ids_str
            #     pay_method = request.POST.get('pay_style')
            address_id = request.POST.get('address_id')
            pay_method = request.POST.get('pay_method')

            # 校验参数不能为空
            if not all([address_id, pay_method]):
                return JsonResponse({'code': 2, 'errmsg': '参数不能为空'})
            # 判断地址是否存在1


            try:
                address = Address.objects.get(id=address_id)
            except:
                return JsonResponse({'code': 3, 'errmsg': '地址不存在'})
            # todo: 修改订单信息表: 保存订单数据到订单信息表中
            order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(user.id)

            # 从Redis查询出购物车数据
            # 注意: 返回的是字典, 键值都为bytes类型
            # cart_1 = {1: 2, 2: 2}
            strict_redis = get_redis_connection()
            key = 'cart_%s' % user.id
            sku_ids = strict_redis.hkeys(key)

            total_count = 0
            total_amount = 0
            trans_cost = 10
            # todo: 核心业务: 遍历每一个商品, 并保存到订单商品表

            sku_list = []
            for sku_id in sku_ids:

                try:
                    # 查询一个商品对象
                    sku = GoodsSKU.objects.get(id=sku_id)
                except:
                    return JsonResponse({'code': 4, 'errmsg': '商品不存在'})

                # 获取商品数量和小计金额(需要进行数据类型转换)
                # 新增实例属性,以便在模板界面中显示

                sku.sku_count = strict_redis.hget(key, sku_id)

                sku.sku_count = int(sku.sku_count.decode())
                sku.sku_sum_price = sku.price * sku.sku_count

                if (sku.sku_count > sku.stock):
                    return JsonResponse({'code': 5, 'errmsg': '库存不足'})

                sku.stock -= sku.sku_count

                sku.sales += sku.sku_count

                # 添加商品对象到列表中
                sku_list.append(sku)

                # 删除购物车中的这个商品
                strict_redis.hdel(key, sku_id)

                # 累计商品总数量和总金额
                total_count += sku.sku_count
                total_amount += sku.sku_sum_price

            order = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                address=address,
                total_count=total_count,
                total_amount=total_count,
                trans_cost=trans_cost,
                pay_method=pay_method,
            )

            for sku in sku_list:
                order_goods = OrderGoods.objects.create(
                    order=order,
                    sku=sku,
                    comment='',
                    price=sku.price,
                    count=sku.sku_count,
                )

            return JsonResponse({'code': 0, 'errmsg': '订单提交成功'})
        else:
            return JsonResponse({'code': 1, 'errmsg': '请先登录'})
            # 订单创建成功， 响应请求，返回json


class OrderPayView(View):
    def post(self, request):
        """订单支付"""

        if not request.user.is_authenticated():
            return JsonResponse({'code': 1, 'message': '用户未登录'})

        # 获取订单id
        order_id = request.POST.get('order_id')

        # 判断订单是否有效(未支付)
        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          status=1,  # 未支付
                                          user=request.user)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'code': 2, 'message': '无效订单'})

        # 调用 第三方sdk, 实现支付功能
        # (1) 初始化sdk
        from alipay import AliPay
        app_private_key_string = open("/home/python/Desktop/dailyfresh/apps/orders/app_private_key.pem").read()
        alipay_public_key_string = open("/home/python/Desktop/dailyfresh/apps/orders/app_public_key.pem").read()


        alipay = AliPay(
            appid="2016091100485513",  # 沙箱应用
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2  # 不要使用rsa
            debug=True  # 默认False  True: 表示使用测试环境(沙箱环境)
        )

        # (2) 调用支付接口
        # 支付总金额
        total_pay = order.trans_cost + order.total_amount
        # 支付返回的支付结果参数
        order_str = alipay.api_alipay_trade_page_pay(
            subject="天天生鲜支付订单",
            out_trade_no=order_id,
            total_amount=str(total_pay)  # 需要使用str类型, 不能使用浮点型
        )

        # 定义支付引导界面,并返回给浏览器
        pay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_str
        return JsonResponse({'code': 0, 'pay_url': pay_url})


class CheckPayView(View):
    def post(self, request):
        print(1111111)

        if not request.user.is_authenticated():
            return JsonResponse({'code': 1, 'message': '用户未登录'})

        # 获取订单id
        order_id = request.POST.get('order_id')
        print(333333333333333333333)

        # 判断订单是否有效(未支付)
        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=request.user)
        except OrderInfo.DoesNotExist:

            return JsonResponse({'code': 2, 'message': '无效订单'})


        if not order_id:

            return JsonResponse({'code': 3, 'message': '订单id不能为空'})

        # 调用 第三方sdk, 实现支付功能
        # (1) 初始化sdk
        print(4444444444444444444)
        from alipay import AliPay
        app_private_key_string = open("/home/python/Desktop/dailyfresh/apps/orders/app_private_key.pem").read()
        alipay_public_key_string = open("/home/python/Desktop/dailyfresh/apps/orders/app_public_key.pem").read()

        alipay = AliPay(
            appid="2016091100485513",  # 沙箱应用
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2  # 不要使用rsa
            debug=True  # 默认False  True: 表示使用测试环境(沙箱环境)
        )

        # 调用第三方sdk查询订单支付结果
        print(555555555555555,order_id)
        '''
         {
            "trade_no": "2017032121001004070200176844",
            "code": "10000",
            "invoice_amount": "20.00",
            "open_id": "20880072506750308812798160715407",
            "fund_bill_list": [
              {
                "amount": "20.00",
                "fund_channel": "ALIPAYACCOUNT"
              }
            ],
            "buyer_logon_id": "csq***@sandbox.com",
            "send_pay_date": "2017-03-21 13:29:17",
            "receipt_amount": "20.00",
            "out_trade_no": "out_trade_no15",
            "buyer_pay_amount": "20.00",
            "buyer_user_id": "2088102169481075",
            "msg": "Success",
            "point_amount": "0.00",
            "trade_status": "TRADE_SUCCESS",
            "total_amount": "20.00"
          },
        '''

        while True:
            print(88888888888888)
            result_dict = alipay.api_alipay_trade_query(out_trade_no=order_id)

            print(999999999999)

            code = result_dict.get('code')
            trade_status = result_dict.get('trade_status')
            trade_no = result_dict.get('trade_no')

            # 10000: 接口调用成功
            print(66666666666666666666666)
            if code == '10000' and trade_status == 'TRADE_SUCCESS':
                # 支付成功
                order.status = 4  # 待评价
                order.trade_no = trade_no
                order.save()  # 修改订单信息表
                return JsonResponse({'code': 0, 'message': '支付成功'})
            elif (code == '10000' and trade_status == 'WAIT_BUYER_PAY') or code == '40004':
                # 等待买家付款
                # 40004: 支付暂时失败, 过一会可以成功
                sleep(2)
                print(code)
                continue
            else:
                print(code)
                return JsonResponse({'code': 4, 'message': '支付失败'})
