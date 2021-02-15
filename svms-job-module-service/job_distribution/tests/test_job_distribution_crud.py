import datetime
import uuid

from django.urls import reverse
from rest_framework.test import APITestCase

from job.models import Job, JobConfiguration, FoundationData
from job_catalog.models import Industry, JobCategory, JobCatalog, JobTag, \
    JobTitle
from job_distribution.config import get_auth_token
from .job_distribution_fixtures import *


class TestCreate(APITestCase):
    """
    tests for create
    """

    def setUp(self):
        self.token = get_auth_token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + str(self.token),
            HTTP_USER_AGENT="SYSTEM")
        self.create_initial_data()

    def create_initial_data(self):
        """
        create initials data
        :return:
        :rtype:
        """
        description = """Apply remote sensing principles and methods to analyze
                        data and solve problems in areas such as natural resource management,
                        urban planning, or homeland security. May develop new sensor systems,
                        analytical techniques, or new applications for existing systems."""

        self.industry, _ = Industry.objects.get_or_create(
            naics_code="313110", industry_type="Fiber, Yarn, and Thread Mills")

        self._test_category, _ = JobCategory.objects.get_or_create(
            o_net_soc_code="199999999",
            category_name="Remote Sensing Scientists and Technologistss")
        self._test_category.description = description
        self._test_category.save()

        self.test_catalog, _ = JobCatalog.objects.get_or_create(
            naics_code=self.industry,
            category=self._test_category)

        self.test_job_tag, _ = JobTag.objects.get_or_create(
            tag="machine learning")

        # self.test_program_id = uuid.uuid4()
        self.test_program_id = 'f1a9413d-1ef5-44d6-ac4b-90e4952890be'

        self.test_job_title, _ = JobTitle.objects.get_or_create(
            program_id=self.test_program_id,
            category=self._test_category,
            title="software developer555",
            level="3",
            status=True,
            created_by="jai",
            modified_by="jai"
        )

        self.test_job_config, _ = JobConfiguration.objects.get_or_create(
            program_id=self.test_program_id,
            config_json={'option': 'unKnown'},
            version='test'
        )

        current_date = datetime.date.today()

        self.test_job, _ = Job.objects.get_or_create(
            program_id=self.test_program_id,
            category=self._test_category,
            title=self.test_job_title,
            no_of_openings=8,
            salary_min_range=20000,
            salary_max_range=30000,
            start_date=current_date,
            end_date=current_date + datetime.timedelta(days=1)
        )

        self.current_user_id = uuid.uuid4()

        JOB_DISTRIBUTION_POST_BODY["job_id"] = self.test_job.uid
        self.body = JOB_DISTRIBUTION_POST_BODY

    def test_post_scheduled_jd(self):
        """
        post scheduled job distribution
        """

        url = reverse(
            'job_distribution:vendor_job__get_list',
            kwargs={
                'program_id': self.test_program_id})

        response = self.client.post(url, self.body, format='json')
        data = response.json()["data"][0]
        mock_response = JOB_DISTRIBUTION_POST_RESPONSE["data"][0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["distribution_id"],
                         mock_response["distribution_id"])
        self.assertEqual(data["distribute_type"],
                         mock_response["distribute_type"])

    def test_post_auto_industry_region_jd(self):
        """
        post auto_industry_region job distribution
        """

        url = reverse(
            'job_distribution:vendor_job__get_list',
            kwargs={
                'program_id': "ecb4d785-5b17-4546-8ed2-ca1a3f0cc653"})

        self.body = POST_SCHEDULED_BODY
        self.body["job_id"] = self.test_job.uid
        response = self.client.post(url, self.body, format='json')
        try:
            status = response.json()["status"]
            self.assertEqual(status, 200)
        except:
            self.assertEqual(response.json()[
                             "error"], "error: could not get content from url because of 404")

    def test_post_auto_manual_jd(self):
        """
        post auto_manual job distribution
        """

        url = reverse(
            'job_distribution:vendor_job__get_list',
            kwargs={
                'program_id': self.test_program_id})
        self.body = POST_AUTO_MANUAL_BODY
        self.body["job_id"] = self.test_job.uid
        response = self.client.post(url, self.body, format='json')
        mock_response = response.json()["data"][0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.body["distribute_type"],
                         mock_response["distribute_type"])
        self.assertEqual(self.body["distribute_method"],
                         mock_response["distribute_method"])
        self.assertEqual(self.body["vendor_selection"],
                         mock_response["vendor_selection"])

    def test_post_manual_jd(self):
        """
        post manual job distribution
        """

        url = reverse(
            'job_distribution:vendor_job__get_list',
            kwargs={
                'program_id': self.test_program_id})
        self.body = POST_MANUAL_BODY
        self.body["job_id"] = self.test_job.uid
        response = self.client.post(url, self.body, format='json')
        mock_response = response.json()["data"][0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.body["distribute_type"],
                         mock_response["distribute_type"])

    def test_get_jb_list(self):
        """
        get job distribution list
        :return:
        :rtype:
        """

        url = reverse(
            'job_distribution:vendor_job__get_list',
            kwargs={
                'program_id': self.test_program_id})
        self.body = POST_MANUAL_BODY
        self.body["job_id"] = self.test_job.uid
        self.client.post(url, self.body, format='json')
        get_list_response = self.client.get(url, format='json')
        self.assertGreaterEqual(get_list_response.data["count"],
                                1)

    def test_filters_on_jb_list(self):
        """
        filters_on_jb  list
        :return:
        :rtype:
        """

        url = reverse(
            'job_distribution:vendor_job__get_list',
            kwargs={
                'program_id': self.test_program_id})

        self.body = POST_MANUAL_BODY
        self.body["job_id"] = self.test_job.uid
        self.client.post(url, self.body, format='json')

        query_string = {
            'program_id': self.test_program_id,
            'job__id': self.test_job.id,
            'distribute_type': "manual",
            'vendor_id': "59106c90-e1f5-4016-b7bf-3cdf24a2b188",
            'vendor_group_id': "19106c90-e1f5-4016-b7bf-3cdf24a2b187",
            'opt_option': "no_response"
        }
        query_string_v2 = "&".join(
            ["{}={}".format(key, val) for key, val in query_string.items()])

        get_list_response = self.client.get(url, QUERY_STRING=query_string_v2,
                                            format='json')
        self.assertGreaterEqual(get_list_response.data["count"],
                                0)

    def test_wrong_filters_on_jb_list(self):
        """
        wrong filters_on_jb  list
        :return:
        :rtype:
        """

        url = reverse(
            'job_distribution:vendor_job__get_list',
            kwargs={
                'program_id': self.test_program_id})

        self.body = POST_MANUAL_BODY
        self.body["job_id"] = self.test_job.uid
        self.client.post(url, self.body, format='json')

        query_string = {
            'program_id': self.test_program_id,
            'job__id': self.test_job.uid,
            'distribute_type': "manual",
            'vendor_id': "9ba533e3-ca1c-4fbe-bd23-970e0dc44efb",
            'vendor_group_id': "9b8226eb-37c8-47bd-9f9e-33bdf02c9841",
            'opt_option': "no_response3"
        }
        query_string_v2 = "&".join(
            ["{}={}".format(key, val) for key, val in query_string.items()])

        get_list_response = self.client.get(url, QUERY_STRING=query_string_v2,
                                            format='json')
        self.assertEqual(get_list_response.status_code, 400)
        self.assertEqual(get_list_response.status_text, 'Bad Request')
        result = get_list_response.data["error"].find(
            "no_response3 is not one of the available choices")
        self.assertNotEqual(result, -1)

    def test_get_single_jd(self):
        """
        get single JD
        :return:
        :rtype:
        """

        url = reverse(
            'job_distribution:vendor_job__get_list',
            kwargs={
                'program_id': self.test_program_id})

        self.body = POST_MANUAL_BODY
        self.body["job_id"] = self.test_job.uid
        post_response = self.client.post(url, self.body, format='json')
        post_response = post_response.data["data"][0]

        url = reverse(
            'job_distribution:vendor_job__get_put_del',
            kwargs={
                'program_id': self.test_program_id, 'pk': post_response["id"]})

        get_single_response = self.client.get(url, format='json').data
        self.assertEqual(post_response["job"]["id"],
                         get_single_response["job"]["id"])
        self.assertEqual(post_response["vendor_id"],
                         get_single_response["vendor_id"])
        self.assertEqual(post_response["distribute_type"],
                         get_single_response["distribute_type"])
        self.assertEqual(post_response["opt_option"],
                         get_single_response["opt_option"])

    def test_update_single_jd(self):
        """
        get single JD
        :return:
        :rtype:
        """

        url = reverse(
            'job_distribution:vendor_job__get_list',
            kwargs={
                'program_id': self.test_program_id})

        self.body = POST_MANUAL_BODY
        self.body["job_id"] = self.test_job.uid
        post_response = self.client.post(url, self.body, format='json')
        post_response = post_response.data["data"][0]

        url = reverse(
            'job_distribution:vendor_job__get_put_del',
            kwargs={
                'program_id': self.test_program_id, 'pk': post_response["id"]})

        body = {
            "job_id": self.test_job.uid,
            "vendor_id": "79106c90-e1f5-4016-b7bf-3cdf24a2b140",
            "distribute_type": "manual",
            "opt_option": "no_response"
        }

        get_single_response = self.client.put(url, body, format='json').data
        self.assertEqual(post_response["job"]["id"],
                         get_single_response["job"]["id"])
        self.assertEqual(get_single_response["vendor_id"],
                         '79106c90-e1f5-4016-b7bf-3cdf24a2b140')
        self.assertEqual(post_response["distribute_type"],
                         get_single_response["distribute_type"])
        self.assertEqual(post_response["opt_option"],
                         get_single_response["opt_option"])

    def test_opt_in_opt_out(self):
        """
         update opt_in_opt_out JD
        :return:
        :rtype:
        """

        url = reverse(
            'job_distribution:vendor_job__get_list',
            kwargs={
                'program_id': self.test_program_id})

        self.body = POST_MANUAL_BODY
        self.body["job_id"] = self.test_job.uid
        post_response = self.client.post(url, self.body, format='json')
        post_response = post_response.data["data"][0]

        url = reverse(
            'job_distribution:vendor_job_patch',
            kwargs={
                'program_id': self.test_program_id,
                'vendor_id': '39106c90-e1f5-4016-b7bf-3cdf24a2b181',
                'job_id': self.test_job.uid
            })

        body = {
            "opt_option": "opt_out"
        }

        get_single_response = self.client.put(url, body, format='json').data[
            0]
        self.assertEqual(post_response["job"]["id"],
                         get_single_response["job"]["id"])
        self.assertEqual(get_single_response["vendor_id"],
                         '39106c90-e1f5-4016-b7bf-3cdf24a2b181')
        self.assertEqual(post_response["distribute_type"],
                         get_single_response["distribute_type"])
        self.assertEqual(get_single_response["opt_option"], 'opt_out')

    def test_scedule_get_jb_list(self):
        """
        get scedule_get_jb_list
        :return:
        :rtype:
        """

        url = reverse(
            'job_distribution:vendor_job__get_list',
            kwargs={
                'program_id': self.test_program_id})
        self.body = POST_SCHEDULED_PERIODIC_BODY
        self.body["job_id"] = self.test_job.uid
        dt_now = datetime.datetime.now()
        dt_next = dt_now + datetime.timedelta(
            seconds=int(7))
        dt_next_str = dt_next.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        self.body["distribution_id"][0]["schedules"][0]["after"] = dt_next_str
        res = self.client.post(url, self.body, format='json')
        url = reverse(
            'job_distribution:schedule_job__get_list',
            kwargs={
                'program_id': self.test_program_id})
        get_list_response = self.client.get(url, format='json')
        self.assertGreaterEqual(get_list_response.data["count"],
                                1)

    def test_scedule_get_single_jd(self):
        """
        get scedule_get_single_jd
        :return:
        :rtype:
        """

        url = reverse(
            'job_distribution:vendor_job__get_list',
            kwargs={
                'program_id': self.test_program_id})
        self.body = POST_SCHEDULED_PERIODIC_BODY
        self.body["job_id"] = self.test_job.uid
        dt_now = datetime.datetime.now()
        dt_next = dt_now + datetime.timedelta(
            seconds=int(7))
        dt_next_str = dt_next.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        self.body["distribution_id"][0]["schedules"][0]["after"] = dt_next_str
        res = self.client.post(url, self.body, format='json')
        url = reverse(
            'job_distribution:schedule_job__get_list',
            kwargs={
                'program_id': self.test_program_id})
        get_list_response = self.client.get(url, format='json')
        pk = get_list_response.data["results"][0]["id"]
        url = reverse(
            'job_distribution:schedule_job__get',
            kwargs={
                'program_id': self.test_program_id, "pk": pk})
        get_list_response = self.client.get(url, format='json')
        self.assertGreaterEqual(get_list_response.data["id"],
                                pk)
        self.assertEqual(isinstance(get_list_response.data["created_by"], dict),
                         True)

    def test_submission_limit_manual_jd(self):
        """
        test submission limit while posting manual jd
        """

        url = reverse(
            'job_distribution:vendor_job__get_list',
            kwargs={
                'program_id': self.test_program_id})
        self.body = POST_AUTO_MANUAL_BODY
        self.body["submission_limit"] = 1
        self.body["job_id"] = self.test_job.uid
        response = self.client.post(url, self.body, format='json')
        mock_response = response.json()["data"][0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.body["distribute_type"],
                         mock_response["distribute_type"])
        self.assertEqual(self.body["distribute_method"],
                         mock_response["distribute_method"])
        self.assertEqual(self.body["vendor_selection"],
                         mock_response["vendor_selection"])

