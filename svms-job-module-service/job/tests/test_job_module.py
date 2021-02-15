from django.test import RequestFactory, TestCase
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from job.models import *
from job.views import *
from job_catalog.models import Industry, JobCategory, JobCatalog, JobTag, JobTitle
from job.models import Job, JobConfiguration, FoundationData
from django.urls import reverse
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from django.conf import settings


class JobTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        payload = {
            "username": settings.AUTH_TOKEN_USERNAME,
            "password": settings.AUTH_TOKEN_PASSWORD
        }

        headers = {
            'user-agent': 'SYSTEM',
            "Content-Type": "application/json"
        }
        url = settings.AUTH_TOKEN_ENDPOINT
        response = requests.post(
            url, data=json.dumps(payload), headers=headers)

        self.token = response.json()['token']
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer {}'.format(self.token)
        )

        self.test_program_id = 'e0ed0ed7-7423-4ae2-8439-ae71c54b5090'

        description = """Apply remote sensing principles and methods to analyze
         data and solve problems in areas such as natural resource management,
         urban planning, or homeland security. May develop new sensor systems,
         analytical techniques, or new applications for existing systems."""

        self._test_category, _ = JobCategory.objects.get_or_create(
            o_net_soc_code="199999999",
            category_name="Remote Sensing Scientists and Technodlogists")
        self._test_category.description = description
        self._test_category.save()

        self.test_job_title, _ = JobTitle.objects.get_or_create(
            program_id=self.test_program_id,
            category=self._test_category,
            title="software developer555",
            level="3",
            status=True,
            created_by="b04e32cd-0584-41d0-89a1-8eac3101c046",
            modified_by="b04e32cd-0584-41d0-89a1-8eac3101c046"
        )
        self.test_job_tag, _ = JobTag.objects.get_or_create(tag="machine learnig")

        self.test_foundation_data, _ = FoundationData.objects.get_or_create(
            program_id=self.test_program_id
        )

        current_date = timezone.now()
        self.test_job, _ = Job.objects.get_or_create(
            program_id=self.test_program_id,
            category=self._test_category,
            title=self.test_job_title,
            no_of_openings=8,
            salary_min_range=20000,
            salary_max_range=30000,
            start_date=current_date,
            end_date=current_date + relativedelta(days=+1),

        )

    def test_post_job(self):
        data = {"category": self._test_category.id, "title": self.test_job_title.id,
                "foundational": self.test_foundation_data.id, "tags": [self.test_job_tag.id], "type": "Permanent",
                "hire_type": "testt", "company_name": "wipro", "level": "1", "no_of_openings": 10,
                "salary_min_range": 10, "salary_max_range": 15,
                "description": "Lorem Ipsum is simply dummy text of the printing and typesetting industry.",
                "start_date": "2020-08-24T07:02:44Z", "end_date": "2020-10-24T07:02:47Z", "status": "pending_approval",
                "created_on": "2020-09-04T07:45:26.057000Z", "modified_on": "2020-09-28T05:55:30.389699Z",
                "custom_field_010": "column1", "custom_field_020": "column2", "custom_field_030": "column3",
                "submit_type": "Submit", "min_bill_rate": 7000, "max_bill_rate": 9000,
                "job_manager": "e8831a81-ba2f-4be9-8e82-c1ae0e6c84c7",
                "msp_manager": "e8831a81-ba2f-4be9-8e82-c1ae0e6c84c7",
                "created_by": "e8831a81-ba2f-4be9-8e82-c1ae0e6c84c7",
                "modified_by": "e8831a81-ba2f-4be9-8e82-c1ae0e6c84c7",
                "checklist": {"id": ["c08077b0-0b8e-4c47-9d6f-52451eb03171"]},
                "hierarchy": "ff783263-ec5f-401d-b52b-4a2dbcd9128f",
                "location_id": "723aed60-cf23-4344-8130-2456e09d5656", "candidates": [
                {"name_prefix": "Mr.", "first_name": "TESTF", "middle_name": "D.", "last_name": "TESTL",
                 "name_suffix": "Jr.", "email": "test@example.com", "phone_isdcode": "+91",
                 "phone_number": "0000000000", "vendor_id": "28f84a9e3e2d41e7ad7b081e91f049ff"}]}
        response = self.client.post(reverse('job:joblist', kwargs={'program_id': self.test_program_id}), data=data,
                                    format='json')
        self.assertEqual(response.status_code, 200)

    def test_get_job(self):
        response = self.client.get(reverse('job:joblist', kwargs={'program_id': self.test_program_id}))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('job:joblist', kwargs={'program_id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], 0)

        response = self.client.get(
            reverse('job:joblist', kwargs={'program_id': 'e0ed0ed7-7423-4ae2-8439-ae71c54b509000'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], 0)

        response = self.client.get(
            reverse('job:detailjob', kwargs={'program_id': self.test_program_id, 'uid': self.test_job.uid}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('job:detailjob', kwargs={'program_id': self.test_program_id,
                                                                    'uid': '8dd23352-760a-4474-8346-076c3669fa05'}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            '/job-manager/{}/job?title__title={}'.format(self.test_program_id, self.test_job.title.title))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data['total_count'], 1)

        response = self.client.get('/job-manager/{}/job?category__category_name={}'.format(self.test_program_id,
                                                                                           self.test_job.category.category_name))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data['total_count'], 1)

        response = self.client.get(
            '/job-manager/{}/job?category__category_name={}?title__title={}'.format(self.test_program_id,
                                                                                    self.test_job.category.category_name,
                                                                                    self.test_job.title.title))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data['total_count'], 1)

        response = self.client.get('/job-manager/{}/job?title__title={}'.format(self.test_program_id, 'xyz'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], 0)

        response = self.client.get('/job-manager/{}/job?category__category_name={}'.format(self.test_program_id, 'xyz'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], 0)

        response = self.client.get(
            '/job-manager/{}/job?category__category_name={}?title__title={}'.format(self.test_program_id, 'xyz', 'xyz'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], 0)

    def test_put_job(self):
        response = self.client.put(
            reverse('job:detailjob', kwargs={'program_id': self.test_program_id, 'uid': self.test_job.uid}),
            data={"note_for_approver": "tes111t", "foundational_data": [
                {"foundational_data_type_id": "foundational_data_type_UUID_01",
                 "values": [{"id": "first_UUID_01"}, {"id": "Second_UUID_02"}]}], "qualifications": [
                {"qualification_type_id": "0c3bcbf8a6f5458786b9bf2ee9a53cea", "qualification_type": "skills",
                 "values": [{"id": "0ad52a03ebdf419486dca5a85deb1e9b", "level": "top", "is_active": "False"}]}],
                  "checklist": {"id": ["c08077b0-0b8e-4c47-9d6f-52451eb03171"]}}, format='json')
        self.assertEqual(response.status_code, 200)

    def test_delete_job(self):
        response = self.client.delete(
            reverse('job:detailjob', kwargs={'program_id': self.test_program_id, 'uid': self.test_job.uid}))
        self.assertEqual(response.status_code, 200)

    def test_get_recent_job(self):
        response = self.client.get('/job-manager/{}/recent_job?page=1&limit=1'.format(self.test_program_id))
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/job-manager/{}/recent_job/{}'.format(self.test_program_id, self.test_job.uid))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            '/job-manager/{}/recent_job/{}'.format('e0ed0ed7-7423-4ae2-8439-ae71c54b5090', self.test_job.uid))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            '/job-manager/{}/recent_job/{}'.format(self.test_program_id, '19106c90-e1f5-4016-b7bf-3cdf24a2b184'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            '/job-manager/{}/recent_job?title__title={}'.format(self.test_program_id, self.test_job.title.title))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data['total_count'], 1)

        response = self.client.get('/job-manager/{}/recent_job?category__category_name={}'.format(self.test_program_id,
                                                                                                  self.test_job.category.category_name))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data['total_count'], 1)

        response = self.client.get(
            '/job-manager/{}/recent_job?category__category_name={}?title__title={}'.format(self.test_program_id,
                                                                                           self.test_job.category.category_name,
                                                                                           self.test_job.title.title))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data['total_count'], 1)

        response = self.client.get('/job-manager/{}/recent_job?title__title={}'.format(self.test_program_id, 'xyz'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], 0)

        response = self.client.get(
            '/job-manager/{}/recent_job?category__category_name={}'.format(self.test_program_id, 'xyz'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], 0)

        response = self.client.get(
            '/job-manager/{}/recent_job?category__category_name={}?title__title={}'.format(self.test_program_id, 'xyz',
                                                                                           'xyz'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], 0)

    def test_get_draft_job(self):
        response = self.client.get('/job-manager/{}/draft_job?page=1&limit=1'.format(self.test_program_id))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            '/job-manager/{}/draft_job/{}'.format(self.test_program_id, '19106c90-e1f5-4016-b7bf-3cdf24a2b184'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            '/job-manager/{}/draft_job?title__title={}'.format(self.test_program_id, self.test_job.title.title))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data['total_count'], 1)

        response = self.client.get('/job-manager/{}/draft_job?category__category_name={}'.format(self.test_program_id,
                                                                                                 self.test_job.category.category_name))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data['total_count'], 1)

        response = self.client.get(
            '/job-manager/{}/draft_job?category__category_name={}?title__title={}'.format(self.test_program_id,
                                                                                          self.test_job.category.category_name,
                                                                                          self.test_job.title.title))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data['total_count'], 1)

        response = self.client.get('/job-manager/{}/draft_job?title__title={}'.format(self.test_program_id, 'xyz'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], 0)

        response = self.client.get(
            '/job-manager/{}/draft_job?category__category_name={}'.format(self.test_program_id, 'xyz'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], 0)

        response = self.client.get(
            '/job-manager/{}/draft_job?category__category_name={}?title__title={}'.format(self.test_program_id, 'xyz',
                                                                                          'xyz'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], 0)

    def test_get_popular_job(self):
        response = self.client.get('/job-manager/{}/popular_job?page=1&limit=1'.format(self.test_program_id))
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/job-manager/{}/popular_job/{}'.format(self.test_program_id, self.test_job.uid))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            '/job-manager/{}/popular_job/{}'.format('e0ed0ed7-7423-4ae2-8439-ae71c54b5090', self.test_job.uid))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            '/job-manager/{}/popular_job/{}'.format(self.test_program_id, '19106c90-e1f5-4016-b7bf-3cdf24a2b184'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            '/job-manager/{}/popular_job?title__title={}'.format(self.test_program_id, self.test_job.title.title))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data['total_count'], 1)

        response = self.client.get('/job-manager/{}/popular_job?category__category_name={}'.format(self.test_program_id,
                                                                                                   self.test_job.category.category_name))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data['total_count'], 1)

        response = self.client.get(
            '/job-manager/{}/popular_job?category__category_name={}?title__title={}'.format(self.test_program_id,
                                                                                            self.test_job.category.category_name,
                                                                                            self.test_job.title.title))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data['total_count'], 1)

        response = self.client.get('/job-manager/{}/popular_job?title__title={}'.format(self.test_program_id, 'xyz'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], 0)

        response = self.client.get(
            '/job-manager/{}/popular_job?category__category_name={}'.format(self.test_program_id, 'xyz'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], 0)

        response = self.client.get(
            '/job-manager/{}/popular_job?category__category_name={}?title__title={}'.format(self.test_program_id, 'xyz',
                                                                                            'xyz'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], 0)

    def test_get_job_template(self):
        response = self.client.get('/job-manager/{}/job_template?page=1&limit=1'.format(self.test_program_id))
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/job-manager/{}/job_template/{}'.format(self.test_program_id, self.test_job.uid))
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/job-manager/{}/job_template?page=1&limit=1'.format('e0ed0ed7-7423-4ae2-8439-ae71c54b5090'))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data['total_count'], 0)

        response = self.client.get(
            '/job-manager/{}/job_template/{}'.format(self.test_program_id, '19106c90-e1f5-4016-b7bf-3cdf24a2b184'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            '/job-manager/{}/job_template?title__title={}'.format(self.test_program_id, self.test_job.title.title))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            '/job-manager/{}/job_template?category__category_name={}'.format(self.test_program_id,
                                                                             self.test_job.category.category_name))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            '/job-manager/{}/job_template?category__category_name={}?title__title={}'.format(self.test_program_id,
                                                                                             self.test_job.category.category_name,
                                                                                             self.test_job.title.title))
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/job-manager/{}/job_template?title__title={}'.format(self.test_program_id, 'xyz'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], 0)

        response = self.client.get(
            '/job-manager/{}/job_template?category__category_name={}'.format(self.test_program_id, 'xyz'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], 0)

        response = self.client.get(
            '/job-manager/{}/job_template?category__category_name={}?title__title={}'.format(self.test_program_id,
                                                                                             'xyz', 'xyz'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], 0)

    def test_job_approval_status(self):
        self.job_pk = self.test_job.id
        self.client.credentials()
        response = self.client.put('/job-manager/{}/job_approval/{}'.format(self.test_program_id,32),data={"status":"Open (Approved)"},format='json')
        self.assertEqual(response.status_code, 200)
        response = self.client.put('/job-manager/{}/job_approval/{}'.format(self.test_program_id,32),data={"status":"Rejected"},format='json')
        self.assertEqual(response.status_code, 200)

    def test_copy_job_post(self):
        data = {}
        response = self.client.post('/job-manager/{}/copyjob/{}'.format(self.test_program_id, self.test_job.uid),
                                    data=data,
                                    format='json')
        self.assertEqual(response.status_code, 201)
