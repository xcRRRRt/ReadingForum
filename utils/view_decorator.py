# 装饰器
import inspect

from django.http import HttpResponseRedirect
from django.shortcuts import render


class AuthRequired:
    """
    这么逆天的屎山，我要铭记一辈子，骚凹瑞


    django View装饰器，可以装饰类，也可以装饰函数，可以无参，也可以有参
    若要在该类中增加新的装饰器，请务必严格遵守规则


    使用方法：@AuthRequired.xxx_required(argument1=2, argument2="hello", argument3="world", ...)
    请保证参数是以键值对的形式传入的


    如何添加新的装饰器(假设装饰器的名字叫 xyz_required)

    1. 新增一个@classmethod方法
        @classmethod
        def xyz_required(cls, *args, argument1, argument2, argument3, ...):
            :param cls:
            :param *args: 若为无参装饰器(指装饰器后面没有括号)，args[0]必定为被装饰的类/函数
                          若为有参装饰器, 则args无用
            :param **kwargs: 若为有参装饰器，则需要将**kwargs改为需要的参数
            return _auth_required(cls.xyz_required.__name__, *args, argument1=argument1， argument2=argument2, argument3=argument3)

    2. 在类下方新增两个函数
        def _xyz_required_cls_return(self, cls, request, decorator_kwargs, *args, **kwargs):
            该函数为类装饰器的判断逻辑
            :param self                 !important 请不要忘记该参数，因为这是给类用的
            :param cls                  被装饰的类
            :param request              请求
            :param decorator_kwargs     装饰器的参数
            :param *args                其他发送到view视图的参数
            :param **kwargs             其他发送到view视图的参数
            if ......:      可以通过request或者decorator_kwargs获取想要的值，进行验证
                return HttpResponse()/redirect()/......
            return cls(self, request, *args, **kwargs)  # 如果通过验证，则进如被装饰的类
        def _xyz_required_func_return(self, cls, request, decorator_kwargs, *args, **kwargs):
            该函数为函数装饰器的判断逻辑
            :param func                 被装饰的函数
            :param request              请求
            :param decorator_kwargs     装饰器的参数
            :param *args                其他发送到view视图的参数
            :param **kwargs             其他发送到view视图的参数
            if ......:      可以通过request或者decorator_kwargs获取想要的值，进行验证
                return HttpResponse()/redirect()/......
            return func(request, *args, **kwargs)  # 如果通过验证，则进如被装饰的类

    3. 下方还有一个字典，请将上方两个函数按照规则加入
        'xyz_required': [_xyz_required_cls_return, _xyz_required_func_return],
        装饰器名字: [类装饰器的判断逻辑，函数装饰器的判断逻辑]
    """

    @classmethod
    def admin_required(cls, *args, **kwargs):
        return _auth_required(cls.admin_required.__name__, *args, **kwargs)

    @classmethod
    def login_required(cls, *args, login_url='/user/login/'):
        return _auth_required(cls.login_required.__name__, *args, login_url=login_url)


def _admin_required_cls_return(self, cls, request, decorator_kwargs, *args, **kwargs):
    if not request.session.get("is_admin"):
        return render(request, "403.html")
    return cls(self, request, *args, **kwargs)


def _admin_required_func_return(func, request, decorator_kwargs, *args, **kwargs):
    if not request.session.get("is_admin"):
        return render(request, "403.html")
    return func(request, *args, **kwargs)


def _login_required_cls_return(self, cls, request, decorator_kwargs, *args, **kwargs):
    if request.session.get("username", None) is None:
        return HttpResponseRedirect(decorator_kwargs.get("login_url") + '?next=' + request.get_full_path())
    return cls(self, request, *args, **kwargs)


def _login_required_func_return(func, request, decorator_kwargs, *args, **kwargs):
    if request.session.get("username", None) is None:
        return HttpResponseRedirect(decorator_kwargs.get("login_url") + '?next=' + request.get_full_path())
    return func(request, *args, **kwargs)


return_dict = {
    'admin_required': [_admin_required_cls_return, _admin_required_func_return],
    'login_required': [_login_required_cls_return, _login_required_func_return],
}


def _auth_required_cls(cls, auth_required_name, **other_kwargs):
    def _wrapper(self, request, *args, **kwargs):
        return return_dict.get(auth_required_name)[0](self, cls, request, other_kwargs, *args, **kwargs)

    return _wrapper


def _auth_required_func(func, auth_required_name, **other_kwargs):
    def _wrapper(request, *args, **kwargs):
        return return_dict.get(auth_required_name)[1](func, request, other_kwargs, *args, **kwargs)

    return _wrapper


def _auth_required(auth_required_name, *other_args, **other_kwargs):
    if len(other_args) == 1 and (inspect.isclass(other_args[0]) or inspect.isfunction(other_args[0])):
        """无参装饰器"""
        _obj = other_args[0]
        if inspect.isclass(_obj):
            """类装饰器"""
            _obj.dispatch = _auth_required_cls(_obj.dispatch, auth_required_name, **other_kwargs)
            return _obj
        else:
            """函数装饰器"""
            return _auth_required_func(_obj, auth_required_name, **other_kwargs)
    else:
        """有参装饰器"""

        def _cls_dispatcher(obj):
            if inspect.isclass(obj):
                """类装饰器"""
                obj.dispatch = _auth_required_cls(obj.dispatch, auth_required_name, **other_kwargs)
                return obj
            else:
                """函数装饰器"""
                return _auth_required_func(obj, auth_required_name, **other_kwargs)

        return _cls_dispatcher

# def _admin_required_cls(cls):
#     def _wrapper(self, request, *args, **kwargs):
#         if not request.session.get("is_admin"):
#             return HttpResponseForbidden(
#                 "<h3>素惹，你没看错，本可站街13个小时无人问津，急需<span style=\"font-size: 54px\">403</span>个男人的安慰</h3>")
#
#         print(cls, request, args, kwargs)
#         return cls(self, request, *args, **kwargs)
#
#     return _wrapper
#
#
# def _admin_required_func(func):
#     def _wrapper(request, *args, **kwargs):
#         if not request.session.get("is_admin"):
#             return HttpResponseForbidden(
#                 "<h3>素惹，你没看错，本可站街13个小时无人问津，急需<span style=\"font-size: 54px\">403</span>个男人的安慰</h3>")
#
#         return func(request, *args, **kwargs)
#
#     return _wrapper
#
#
# def admin_required(*other_args, **kwargs):
#     if len(other_args) == 1 and (inspect.isclass(other_args[0]) or inspect.isfunction(other_args[0])):
#         """无参装饰器"""
#         _obj = other_args[0]
#         if inspect.isclass(_obj):
#             """类装饰器"""
#             _obj.dispatch = _admin_required_cls(_obj.dispatch)
#             return _obj
#         else:
#             """函数装饰器"""
#             return _admin_required_func(_obj)
#     else:
#         """有参装饰器"""
#
#         def _admin_required_class(obj):
#             if inspect.isclass(obj):
#                 """类装饰器"""
#                 obj.dispatch = _admin_required_cls(obj.dispatch)
#                 return obj
#             else:
#                 """函数装饰器"""
#                 return _admin_required_func(obj)
#
#         return _admin_required_class
