from rest_framework import serializers

from job_catalog.models import JobTitle, JobCatalog

UPLOAD_INDUSTRIES = """
- api to upload the system defined industries.
- it takes xlsx/xls files in input body.
- the content of file should be like below

.. csv-table::

    change Indicator, 2017 NAICS Code, 2017 NAICS Title
    ,                   11,            Agriculture, Forestry
    ,                   111,           Crop ProductionT

"""

UPLOAD_CATEGORY = """
- api to upload the system defined category.
- it takes xlsx/xls files in input body.
- the content of file should be like below

.. csv-table::

    O*NET-SOC Code,     Job Category,       Description
    11-1011.00,         Chief Executives,	Determine .....

"""

GET_JOB_TITLES = """
- Method to list down all the job titles of a program id
  available in the system whose status is active.
- this can be further filter based on the given below parameter or headers
- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job_catalog/job_title?category=11-1011.00&title=Java Developerv367r5564&level=1&description=test tjhdgjsdhjkd&status=false
- Header samples:
        - Content-Type: application/json
        - X-SVMS-Program-Id:  <program_id>
"""

POST_JOB_TITLE = """ 
- Add a job title  with system defined category and program id. 
- Job Titles are unique for a Job Category.
  Programs cannot have Job Titles of the same name in the same Job Category.
Note:
- A job title may have multiple job tags while creating a new job title.
- A job title table will have description of the category selected
  at first latter user can modify it making no changes to category table
  description field.
"""

GET_JOB_TITLE = """
- Method to list down the details of a specific job titles of a program id
  available in the system whose status is active.
- Need to provide primary key in the request url to get the record specific to
  that primary key.
- this can be further filter based on the given below parameter or headers
- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job_catalog/job_title/ff8a7746-a8a7-4b99-9243-9dba0d2e1182?category=11-1011.00&title=Java Developerv367r5564&level=1&description=test tjhdgjsdhjkd&status=false
- Header samples:
        - Content-Type: application/json
        - X-SVMS-Program-Id:  <program_id>
"""

PUT_JOB_TITLE = """ 
- Method helps to update a job title of a program id record with the help
  of a primary key provided in the requested url.
Note:
    - Program id, system defined category and job title field must be unique.

- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job_catalog/job_title/ff8a7746-a8a7-4b99-9243-9dba0d2e1182

- Header samples:
        - Content-Type: application/json
        - X-SVMS-Program-Id:  <program_id>
"""

POST_JOB_CATALOG = """
- Method to Post the job catalog  
- below are the sample request url and body 

- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job_catalog/
        - body
            {
                "naics_code":"111",
                "category":"51-3099.00"
            }
"""

DELETE_JOB_TITLE = """ 
- Method helps to delete a job title record of a program id 
  with the help of the primary key provided in the requested url.
- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job_catalog/job_title/ff8a7746-a8a7-4b99-9243-9dba0d2e1182
- Header samples:
        - Content-Type: application/json
        - X-SVMS-Program-Id:  <program_id>
"""

UPLOAD_JOB_TITLE = """
- api to upload the Job title. 
- it takes xlsx/xls files in input body.
- the content of file should be like below

.. csv-table::

    O*NET-SOC Code	Job Category	    Job Titles	Job Tags
    11-1011.00	    Chief Executives	Aeronautics Commission Director

"""

GET_JOB_CATALOG = """
- Method to list down details of all the system defined industry,
  system defined category with job title forming unique set with
  job category, having status to be true.
Note:
- to perform any filter pass the field and its value in the request

- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job_catalog?category_name=Tool and Die Makers
- to perform search pass the value in the 'q' param

- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job_catalog?q=Tool and Die Makers
- Similarly you can pass the order_by fields, searchable fields and filterable
  fields altogether in a single request with help of "&" operator.

- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job_catalog?q=51-3099.00&order_by=job_title&level=1

- order_by fields:
        - category_name
        - o_net_soc_code
        - job_title
        - level
- searchable fields:
        - category_name
        - o_net_soc_code
        - job_title
        - level
        - description

- Filterable fields:
        - category_name
        - o_net_soc_code
        - job_title
        - level
        - description
   
- Header samples:
        - Content-Type: application/json
        - X-SVMS-Program-Id:  <program_id>
"""

GET_SINGLE_JOB_CATALOG = """ 
- Method to list down details of a specific record of the system defined
  industry, system defined catgeory with job title forming unique set with
  job category, having status to be true with the help of the primary key
  provided in the requested url.
- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job_catalog/ff8a7746-a8a7-4b99-9243-9dba0d2e1182

- Header samples:
        - X-SVMS-Program-Id:  <program_id>  (optional)
"""

PUT_SINGLE_JOB_CATALOG = """
- Method to update the job catalog entry with the help
  of primary key provided in the requested url.
  This method allows to update job level, job description,
  job tags etc,
Note:
Job Category and job title are not editable, you cannot update this fields.

- Request samples:
        - http://dev-awsnlb.simplifyvms.com:8002/job_catalog/ff8a7746-a8a7-4b99-9243-9dba0d2e1182

"""

class JobTitleQueryParams(serializers.ModelSerializer):
    """
    serializer for JobTitle Query Serializer
    """

    category = serializers.CharField(
        required=False, help_text="ex: 11-1011.00")
    title = serializers.CharField(required=False,
                                  help_text="ex: Java Developer")
    level = serializers.IntegerField(required=False, help_text="ex: 1")
    description = serializers.CharField(
        required=False, help_text="test description")
    status = serializers.BooleanField(default=True, help_text="ex: false")
    job_tag = serializers.CharField(
        required=False,
        help_text="comma separated filed ex: ml, science")
    limit = serializers.IntegerField(
        required=False, help_text="Number of results to return per page.")
    offset = serializers.IntegerField(
        required=False, help_text="The initial index from which to return the results.")

    class Meta:
        """
        Meta class for Job Title
        """
        model = JobTitle
        fields = ('category',
                  'title',
                  'level',
                  'description',
                  'status',
                  'job_tag',
                  'limit',
                  'offset'
                  )


class JobCatalogQueryParams(serializers.ModelSerializer):
    """
    serializer for Job Catalog Query Serializer
    """
    q = serializers.CharField(required=False, help_text="ex: Java Developer")
    category_name = serializers.CharField(required=False,
                                          help_text="ex: Chief Executives")
    o_net_soc_code = serializers.CharField(required=False,
                                           help_text="ex: 11-1011.00")
    description = serializers.CharField(
        required=False, help_text="test description")
    job_title = serializers.CharField(required=False,
                                      help_text="ex: Java Developer")
    level = serializers.IntegerField(required=False, help_text="ex: 1")
    order_by = serializers.CharField(
        required=False,
        help_text="ex: order_by=o_net_soc_code or order_by=-o_net_soc_code")
    limit = serializers.IntegerField(
        required=False, help_text="Number of results to return per page.")
    offset = serializers.IntegerField(
        required=False, help_text="The initial index from which to return the results.")
    job_title_limit = serializers.IntegerField(
        required=False, help_text="Number of job title results to return per page.")
    job_title_offset = serializers.IntegerField(
        required=False, help_text="The initial index from which to return the job title results.")

    class Meta:
        """
        Meta class for Job Title
        """
        model = JobCatalog
        fields = ('q',
                  'category_name',
                  'o_net_soc_code',
                  'description',
                  'job_title',
                  'level',
                  'order_by',
                  'limit',
                  'offset',
                  'job_title_limit',
                  'job_title_offset'
                  )