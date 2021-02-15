from django.test import RequestFactory, TestCase, Client

from job_catalog.models import *
from job_catalog.views import *


class JobCatalogTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.industry, _ = Industry.objects.get_or_create(
            naics_code="313110", industry_type="Fiber, Yarn, and Thread Mills")

        description = """Apply remote sensing principles and methods to analyze
         data and solve problems in areas such as natural resource management,
         urban planning, or homeland security. May develop new sensor systems,
         analytical techniques, or new applications for existing systems."""

        self.category, _ = JobCategory.objects.get_or_create(
            o_net_soc_code="199999999",
            category_name="Remote Sensing Scientists and Technodlogists")
        self.category.description = description
        self.category.save()

        self.catalog, _ = JobCatalog.objects.get_or_create(
            naics_code=self.industry,
            category=self.category)

        self.job_tag, _ = JobTag.objects.get_or_create(tag="machine learnig")

        self.job_title, _ = JobTitle.objects.get_or_create(
            program_id="p1",
            category=self.category,
            title="software developer555",
            level="3",
            status=True,
            created_by="jai",
            modified_by="jai")

        self.job_title.description = description
        self.job_title.job_tag.clear()
        self.job_title.job_tag.add(self.job_tag)
        self.job_title.save()

    def test_get_industries(self):
        request = self.factory.get('/job_catalog/industry')
        response = IndustryViewSet.as_view({'get': 'list'})(request)
        results = response.data["results"]
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(results.__len__(), 1)

    def test_get_single_industry(self):
        response = self.client.get(
            '/job_catalog/industry/{}'.format(self.industry.pk))
        results = response.data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], str(self.industry.id))

    def test_get_category(self):
        request = self.factory.get('/job_catalog/category')
        response = CategoryView.as_view(
            {'get': 'list'})(request)
        results = response.data["results"]
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(results.__len__(), 1)

    def test_get_single_category(self):
        response = self.client.get(
            '/job_catalog/category/{}'.format(self.category.pk))
        results = response.data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], str(self.category.id))

    def test_get_catalogs(self):
        request = self.factory.get('/job_catalog')
        response = JobCatalogViewList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data.__len__(), 1)

    def test_get_single_catalog(self):
        response = self.client.get(
            '/job_catalog/{}'.format(self.catalog.pk))
        results = response.data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], str(self.catalog.id))

    def test_get_job_titles(self):
        response = self.client.get('/job_catalog/job_title')
        results = response.data
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.data.__len__(), 1)
