from django.conf import settings


def logger_decorator(f):
    """
    logger decorator for the given method 
    :param f:
    :type f:
    :return:
    :rtype:
    """
    def new_f(*args, **kwargs):
        """
        log the request and response of the given method
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        res = f(*args, **kwargs)
        settings.LOGGER.info(
            "args: {}, kwargs: {}, res: {}".format(args, kwargs, res))
        return res

    return new_f
