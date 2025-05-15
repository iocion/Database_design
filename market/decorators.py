# import wraps
# from flask import abort
# from flask_login import current_user
# def admin_required():
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             if not current_user.is_authenticated or not current_user.is_admin:
#                 abort(403)  # 返回 403 Forbidden 错误，表示没有权限
#             return func(*args, **kwargs)
#         return wrapper
#     return decorator