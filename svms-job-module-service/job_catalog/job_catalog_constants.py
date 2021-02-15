from enum import Enum

SORT_BY_REFERENCE_DICT = {"category_name": "category__category_name",
                          "-category_name": "-category__category_name",
                          "o_net_soc_code": "category__o_net_soc_code",
                          "-o_net_soc_code": "-category__o_net_soc_code",
                          "job_title": "category__job_title__title",
                          "-job_title": "-category__job_title__title",
                          "level": "category__job_title__level",
                          "-level": "-category__job_title__level"}

EDITABLE_FIELDS = ['level', 'description', 'job_tag']


class ErrorMessage(Enum):
    WRONG_FIELD_TYPE = "{} should be {}"
