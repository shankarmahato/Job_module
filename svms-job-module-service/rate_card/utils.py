from .models import RateCardConfig
from .rate_card_constants import RATE_CARD_CONFIG


def arrange_priority_search_keys_n_get_queryset(program_id, query_params,
                                                queryset):
    """

    @param program_id:
    @type program_id:
    @param query_params:
    @type query_params:
    @param queryset:
    @type queryset:
    @return:
    @rtype:
    """

    search_params = []
    search_params_not_found = []

    filters_based_on_priority = RATE_CARD_CONFIG["filters_based_on_priority"]

    rate_card_config_obj = RateCardConfig.objects.filter(
        program_id=program_id).first()

    if rate_card_config_obj:
        filters_based_on_priority = rate_card_config_obj.config_json[
            "filters_based_on_priority"]

    search_params_order_list = [None] * filters_based_on_priority.__len__()

    for key, val in query_params.items():
        index = filters_based_on_priority.get(key)
        if index:
            search_params_order_list[index - 1] = {key: val}
        else:
            search_params_not_found.append({key: val})

    search_params.extend(list(filter(None, search_params_order_list)))
    search_params.extend(search_params_not_found)

    for items in search_params:
        queryset_result = queryset.filter(**items)
        if queryset_result:
            queryset = queryset_result

    return queryset
