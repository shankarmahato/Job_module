from django.db import models
import uuid


class Industry(models.Model):
    """
    containing the list of nic code and the industry type 
    defined by the system
    """
    uid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True)
    naics_code = models.CharField(max_length=100, unique=True, db_index=True)
    industry_type = models.CharField(max_length=1000)

    def __str__(self):
        """
        string representation of industry object
        """
        return "{}_{}".format(self.naics_code, self.industry_type)

    class Meta:
        """
        Meta class for Industry
        """
        verbose_name = 'Industry'
        verbose_name_plural = 'Industries'
        unique_together = ('naics_code', 'industry_type')


class JobCategory(models.Model):
    """
    containing the list of o net soc and the job category along with job descrption
    defined by the system
    """
    uid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True)
    o_net_soc_code = models.CharField(
        max_length=30, unique=True, db_index=True)
    category_name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        """
        string representation of JobCategory object
        :return:
        :rtype:
        """
        return "{}_{}".format(self.o_net_soc_code, self.category_name)

    class Meta:
        """
        Meta class for Job Category
        """
        verbose_name = 'Job Category'
        verbose_name_plural = 'Job Categories'
        unique_together = ('o_net_soc_code', 'category_name')


class JobCatalog(models.Model):
    """
    containing all unique industry and job category listing 
    """
    uid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True)
    naics_code = models.ForeignKey(Industry, to_field="naics_code",  related_name='job_catalog',
                                   on_delete=models.DO_NOTHING)
    category = models.ForeignKey(JobCategory, to_field="o_net_soc_code",  related_name='job_catalog',
                                 on_delete=models.DO_NOTHING)

    def __str__(self):
        """
        string representation of JobCatalog object

        :return:
        :rtype:
        """
        return "{}_{}".format(self.naics_code, self.category)

    class Meta:
        """
        Meta class for Job Catalog
        """
        verbose_name = 'Job Catalog'
        verbose_name_plural = 'Job Catalogs'


class JobTitle(models.Model):
    """
    containing the list of unique combination of
    program id,job category and job title
    also contains the multiple tag for job titles
    """
    uid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True)
    program_id = models.CharField(max_length=100, db_index=True)
    category = models.ForeignKey(JobCategory, to_field='o_net_soc_code',
                                 related_name='job_title',
                                 on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=100, db_index=True)
    level = models.IntegerField()
    description = models.TextField()
    status = models.BooleanField(default=True)
    job_tag = models.ManyToManyField("JobTag", related_name='job_title',
                                     blank=True)
    created_by = models.CharField(max_length=100)
    modified_by = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        string representation of JobTitle object

        :return:
        :rtype:
        """
        return "{}_{}_{}".format(self.program_id, self.category,
                                 self.title)

    class Meta:
        """
        Meta class for JobTitle
        """
        unique_together = ('program_id', 'category', 'title')
        verbose_name = 'Job Title'
        verbose_name_plural = 'Job Titles'


class JobTag(models.Model):
    """
    containing the list of unique tags
    that will be used in job titles,
    A single job title can have multiple job tags 
    """
    tag = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        """
        string representation of JobTag object
        :return:
        :rtype:
        """
        return "{}".format(self.tag)

    class Meta:
        """
        Meta class for Job Tag
        """
        verbose_name = 'Job Tag'
        verbose_name_plural = 'Job Tags'
