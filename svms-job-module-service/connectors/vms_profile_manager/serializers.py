from rest_framework import serializers
from connectors.vms_profile_manager.helpers import RemoteUserDataHandler
import collections


class RemoteUserInfoSerializer(serializers.ModelSerializer):

    created_by = serializers.SerializerMethodField()
    modified_by = serializers.SerializerMethodField()
    job_manager = serializers.SerializerMethodField()
    msp_manager = serializers.SerializerMethodField()

    def get_created_by(self, obj):
        user_info = RemoteUserDataHandler.get_user(user_id=obj.created_by)
        if user_info is not None:
            return collections.OrderedDict({
                'id': user_info.id,
                # 'name_prefix': user_info.name_prefix,
                'first_name': user_info.first_name,
                # 'middle_name': user_info.middle_name,
                'last_name': user_info.last_name,
                'email':user_info.email
                # 'name_suffix': user_info.name_suffix
            })
        else:
            return collections.OrderedDict({})

    def get_modified_by(self, obj):
        user_info = RemoteUserDataHandler.get_user(user_id=obj.modified_by)
        if user_info is not None:
            return collections.OrderedDict({
                'id': user_info.id,
                # 'name_prefix': user_info.name_prefix,
                'first_name': user_info.first_name,
                # 'middle_name': user_info.middle_name,
                'last_name': user_info.last_name,
                'email':user_info.email
                # 'name_suffix': user_info.name_suffix
            })
        else:
            return collections.OrderedDict({})



    def get_job_manager(self, obj):
        user_info = RemoteUserDataHandler.get_user(user_id=obj.job_manager)
        if user_info is not None:
            return collections.OrderedDict({
                'id': user_info.id,
                # 'name_prefix': user_info.name_prefix,
                'first_name': user_info.first_name,
                # 'middle_name': user_info.middle_name,
                'last_name': user_info.last_name,
                'email':user_info.email
                # 'name_suffix': user_info.name_suffix
            })
        else:
            return collections.OrderedDict({})

    def get_msp_manager(self, obj):
        user_info = RemoteUserDataHandler.get_user(user_id=obj.msp_manager)
        if user_info is not None:
            return collections.OrderedDict({
                'id': user_info.id,
                # 'name_prefix': user_info.name_prefix,
                'first_name': user_info.first_name,
                # 'middle_name': user_info.middle_name,
                'last_name': user_info.last_name,
                'email':user_info.email
                # 'name_suffix': user_info.name_suffix
            })
        else:
            return collections.OrderedDict({})
