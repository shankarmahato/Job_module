import datetime
import uuid

from django.urls import reverse
from rest_framework.test import APITestCase

from interviews.tests.util.common import uuid_shuffle
from job.models import Job, JobConfiguration, FoundationData
from job_catalog.models import Industry, JobCategory, JobCatalog, JobTag, \
    JobTitle
from job_distribution.config import get_auth_token
from submissions.models import Submission
from .rate_card_fixtures import RATE_CARD_POST_RESPONSE


class TestCreate(APITestCase):
    """
    tests for create
    """

    def setUp(self):
        self.token = get_auth_token()
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + str(self.token))
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

        self.test_foundation_data, _ = FoundationData.objects.get_or_create(
            program_id=self.test_program_id
        )

        current_date = datetime.date.today()

        self.test_job, _ = Job.objects.get_or_create(
            program_id=self.test_program_id,
            config_id=self.test_job_config,
            category=self._test_category,
            title=self.test_job_title,
            no_of_openings=8,
            salary_min_range=20000,
            salary_max_range=30000,
            start_date=current_date,
            end_date=current_date + datetime.timedelta(days=1),
            foundational=self.test_foundation_data
        )

        self.current_user_id = uuid.uuid4()

        self.test_candidate_id = uuid_shuffle(self.current_user_id)

        self.test_submission = Submission(
            job=self.test_job,
            program_id=self.test_program_id,
            organization_id='test_organization_id',
            candidate_id=self.test_candidate_id,
            created_by=self.current_user_id,
            modified_by=self.current_user_id
        )
        self.test_submission.save()

        self.body = {"job_template_id": self.test_job.id,
                     "job_category_id": self._test_category.id,
                     "job_level": 7,
                     "job_title_id": self.test_job_title.id,
                     "min_rate_rule": "Cannot Change",
                     "max_rate_rule": "Cannot Change",
                     "min_rate": 75.0,
                     "max_rate": 88.0,
                     "currency": "USD",
                     "work_location": "UP"
                     }

    def test_post_rate_card(self):
        """
        post rate card test
        """

        url = reverse(
            'rate_card:rate_card_get_list_n_post',
            kwargs={
                'program_id': self.test_program_id})

        response = self.client.post(url, self.body, format='json')
        data = response.data

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data["program_id"],
                         RATE_CARD_POST_RESPONSE["program_id"])
        self.assertEqual(data["job_level"],
                         RATE_CARD_POST_RESPONSE["job_level"])
        self.assertEqual(data["min_rate_rule"],
                         RATE_CARD_POST_RESPONSE["min_rate_rule"])
        self.assertEqual(data["max_rate_rule"],
                         RATE_CARD_POST_RESPONSE["max_rate_rule"])
        self.assertEqual(data["min_rate"],
                         RATE_CARD_POST_RESPONSE["min_rate"])
        self.assertEqual(data["max_rate"],
                         RATE_CARD_POST_RESPONSE["max_rate"])
        self.assertEqual(data["currency"],
                         RATE_CARD_POST_RESPONSE["currency"])
        self.assertEqual(data["work_location"],
                         RATE_CARD_POST_RESPONSE["work_location"])

    def test_get_rate_card_list(self):
        """
        get rate_card_list
        :return:
        :rtype:
        """

        url = reverse(
            'rate_card:rate_card_get_list_n_post',
            kwargs={
                'program_id': self.test_program_id})

        post_response = self.client.post(url, self.body, format='json').data
        get_list_response = self.client.get(url, format='json').data["results"][
            0]
        self.assertEqual(post_response["program_id"],
                         get_list_response["program_id"])
        self.assertEqual(post_response["job_template"]["id"],
                         get_list_response["job_template"]["id"])
        self.assertEqual(post_response["job_category"]["id"],
                         get_list_response["job_category"]["id"])
        self.assertEqual(post_response["job_title"]["id"],
                         get_list_response["job_title"]["id"])
        self.assertEqual(post_response["job_level"],
                         get_list_response["job_level"])
        self.assertEqual(post_response["min_rate_rule"],
                         get_list_response["min_rate_rule"])
        self.assertEqual(post_response["max_rate_rule"],
                         get_list_response["max_rate_rule"])
        self.assertEqual(post_response["min_rate"],
                         get_list_response["min_rate"])
        self.assertEqual(post_response["max_rate"],
                         get_list_response["max_rate"])
        self.assertEqual(post_response["currency"],
                         get_list_response["currency"])
        self.assertEqual(post_response["work_location"],
                         get_list_response["work_location"])

    def test_get_single_rate_card(self):
        """
        get single rate_card
        :return:
        :rtype:
        """

        url = reverse(
            'rate_card:rate_card_get_list_n_post',
            kwargs={
                'program_id': self.test_program_id})

        post_response = self.client.post(url, self.body, format='json').data

        url = reverse(
            'rate_card:rate_card_get_put_del',
            kwargs={
                'program_id': self.test_program_id, 'pk': post_response["id"]})

        get_single_response = self.client.get(url, format='json').data
        self.assertEqual(post_response["program_id"],
                         get_single_response["program_id"])
        self.assertEqual(post_response["job_template"]["id"],
                         get_single_response["job_template"]["id"])
        self.assertEqual(post_response["job_category"]["id"],
                         get_single_response["job_category"]["id"])
        self.assertEqual(post_response["job_title"]["id"],
                         get_single_response["job_title"]["id"])
        self.assertEqual(post_response["job_level"],
                         get_single_response["job_level"])
        self.assertEqual(post_response["min_rate_rule"],
                         get_single_response["min_rate_rule"])
        self.assertEqual(post_response["max_rate_rule"],
                         get_single_response["max_rate_rule"])
        self.assertEqual(post_response["min_rate"],
                         get_single_response["min_rate"])
        self.assertEqual(post_response["max_rate"],
                         get_single_response["max_rate"])
        self.assertEqual(post_response["currency"],
                         get_single_response["currency"])
        self.assertEqual(post_response["work_location"],
                         get_single_response["work_location"])

    def test_update_single_rate_card(self):
        """
        update single rate_card
        :return:
        :rtype:
        """

        url = reverse(
            'rate_card:rate_card_get_list_n_post',
            kwargs={
                'program_id': self.test_program_id})

        post_response = self.client.post(url, self.body, format='json').data

        url = reverse(
            'rate_card:rate_card_get_put_del',
            kwargs={
                'program_id': self.test_program_id, 'pk': post_response["id"]})

        work_location = self.body["work_location"]
        self.body["work_location"] = "New Delhi"

        get_single_response = self.client.put(url, self.body,
                                              format='json').data
        self.body["work_location"] = work_location
        self.assertEqual(post_response["program_id"],
                         get_single_response["program_id"])
        self.assertEqual(post_response["job_template"]["id"],
                         get_single_response["job_template"]["id"])
        self.assertEqual(post_response["job_category"]["id"],
                         get_single_response["job_category"]["id"])
        self.assertEqual(post_response["job_title"]["id"],
                         get_single_response["job_title"]["id"])
        self.assertEqual(post_response["job_level"],
                         get_single_response["job_level"])
        self.assertEqual(post_response["min_rate_rule"],
                         get_single_response["min_rate_rule"])
        self.assertEqual(post_response["max_rate_rule"],
                         get_single_response["max_rate_rule"])
        self.assertEqual(post_response["min_rate"],
                         get_single_response["min_rate"])
        self.assertEqual(post_response["max_rate"],
                         get_single_response["max_rate"])
        self.assertEqual(post_response["currency"],
                         get_single_response["currency"])
        self.assertEqual(get_single_response["work_location"],
                         "New Delhi")

    def test_filter_rate_card(self):
        """
        filter rate_card
        :return:
        :rtype:
        """

        url = reverse(
            'rate_card:rate_card_get_list_n_post',
            kwargs={
                'program_id': self.test_program_id})

        post_response = self.client.post(url, self.body, format='json').data

        query_string = {"job_template_id": self.test_job.id,
                        "job_category_id": self._test_category.id,
                        "job_level": 7,
                        "job_title_id": self.test_job_title.id,
                        "min_rate_rule": "Cannot Change",
                        "max_rate_rule": "Cannot Change",
                        "min_rate": 75.0,
                        "max_rate": 88.0,
                        "currency": "USD",
                        "work_location": "UP"
                        }
        query_string_v2 = "&".join(
            ["{}={}".format(key, val) for key, val in query_string.items()])

        get_list_response = self.client.get(
            url,
            QUERY_STRING=query_string_v2,
            format='json')
        get_list_response = get_list_response.data["results"][0]
        self.assertEqual(post_response["program_id"],
                         get_list_response["program_id"])
        self.assertEqual(post_response["job_template"]["id"],
                         get_list_response["job_template"]["id"])
        self.assertEqual(post_response["job_category"]["id"],
                         get_list_response["job_category"]["id"])
        self.assertEqual(post_response["job_title"]["id"],
                         get_list_response["job_title"]["id"])
        self.assertEqual(post_response["job_level"],
                         get_list_response["job_level"])
        self.assertEqual(post_response["min_rate_rule"],
                         get_list_response["min_rate_rule"])
        self.assertEqual(post_response["max_rate_rule"],
                         get_list_response["max_rate_rule"])
        self.assertEqual(post_response["min_rate"],
                         get_list_response["min_rate"])
        self.assertEqual(post_response["max_rate"],
                         get_list_response["max_rate"])
        self.assertEqual(post_response["currency"],
                         get_list_response["currency"])
        self.assertEqual(post_response["work_location"],
                         get_list_response["work_location"])

    def test_negative_filter_rate_card(self):
        """
        negative filter rate_card
        :return:
        :rtype:
        """

        url = reverse(
            'rate_card:rate_card_get_list_n_post',
            kwargs={
                'program_id': self.test_program_id})

        post_response = self.client.post(url, self.body, format='json').data

        query_string = {"job_template_id": self.test_job.id,
                        "job_category_id": self._test_category.id,
                        "job_level": 7,
                        "job_title_id": self.test_job_title.id,
                        "min_rate_rule": "Cannot Change",
                        "max_rate_rule": "Cannot Change",
                        "min_rate": 75.0,
                        "max_rate": 88.0,
                        "currency": "USD",
                        "work_location": "Delhi"
                        }
        query_string_v2 = "&".join(
            ["{}={}".format(key, val) for key, val in query_string.items()])

        get_list_response = self.client.get(
            url,
            QUERY_STRING=query_string_v2,
            format='json')
        get_list_response = get_list_response.data["results"]
        self.assertEqual(get_list_response.__len__(),0)
