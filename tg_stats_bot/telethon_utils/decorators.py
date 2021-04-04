from functools import wraps


def white_list_user_only(username_whitelist: set):
    def outer_wrapper(func):
        @wraps(func)
        async def wrapper(event):
            sender = await event.get_sender()
            if sender.username not in username_whitelist:
                return
            ret = await func(event)
            return ret
        return wrapper
    return outer_wrapper
