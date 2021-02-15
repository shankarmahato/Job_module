POST_JOB_DISTRIBUTION = """ 
Add Vendors to job with three types of distribution method
manual, scheduled and automatic distribution.
- For manual distribution vendor could be added in the job detail
page passing all the vendors and vendor_group id to that job.

sample request body 
    
        {
            "program_id": "program1",
            "job_id": "6a77ea6f3b6146468a43370908535233",
            "vendor_id": ["04f00cc1-67ef-435b-884a-654e20587a2a","04f00cc1-67ef-435b-884a-654e20587a24"],
            "vendor_group_id":[
                {
                "id":1,
                "vendor_id":["04f00cc1-67ef-435b-884a-654e20587a2a","04f00cc1-67ef-435b-884a-654e20587a24"]
                }
            ],
            "distribute_type": "manual"            
        }
- For schedule distribution, distribution_id is required, a list of
distribution_id will be available from the configurator, each
distribution_id contains schedule method Immediate and Periodic
with vendor-id and vendor_group_id belonging to it.

sample request body 


    {
        "job_id": "6a77ea6f3b6146468a43370908535233",
        "program_id": "11e0",
        "distribution_id": [{
            "id": "123",
            "schedules": [{
                    "schedule_type": "PERIODIC",
                    "after": "2020-12-17T19:34:00.000Z",
                    "vendors": ["04f00cc1-67ef-435b-884a-654e20587a27"],
                    "vendor_group_id": [{
                        "id": "vender_123",
                        "vendor_id": ["04f00cc1-67ef-435b-884a-654e20587a2a", "04f00cc1-67ef-435b-884a-654e20587a27"]
                    }]
                },
                {
                    "schedule_type": "IMMEDIATE",
                    "vendors": ["04f00cc1-67ef-435b-884a-654e20587a2a", "04f00cc1-67ef-435b-884a-654e20587a28"],
                    "vendor_group_id": [{
                        "id": "vender_123",
                        "vendor_id": ["04f00cc1-67ef-435b-884a-654e20587a2a", "04f00cc1-67ef-435b-884a-654e20587a29"]
                    }]
                }
            ]
        }],
        "distribute_type": "scheduled"

    }

- For automatic distribution, distribution method and vendor selection are
required.


- If vendor selection method is industry and region then vendors
and vendor_group id will be selected based on job's region and industry,

sample request body for industry

    {
            "program_id": "04f00cc1-67ef-435b-884a-654e20587a2a",
            "job_id": "6a77ea6f3b6146468a43370908535233",
            "distribute_type": "automatic",
            "distribute_method":"on_submit",
            "vendor_selection":"industry_region"            
    }

- if vendor selection method is manual_input then vendors and vendor_group
id must be provided.

Sample request body for manual  input 

    {
            "program_id": "04f00cc1-67ef-435b-884a-654e20587a2a",
            "job_id": "6a77ea6f3b6146468a43370908535233",
            "distribute_type": "automatic",
            "distribute_method":"final_approval",
            "vendor_selection":"manual_input",
            "vendors": ["04f00cc1-67ef-435b-884a-654e20587a2a", "04f00cc1-67ef-435b-884a-654e20587a28"],
            "vendor_group_id":[
                {
                    "id":1,
                    "vendor_id":["04f00cc1-67ef-435b-884a-654e20587a2a", "04f00cc1-67ef-435b-884a-654e20587a28"]
                }
            ]
            
    } 



"""


PUT_OPT_IN_OPT_OUT = """ api to opt in and opt out venders from the job for the given program id

by default the opt_option field is set to "no_response" and other option are opt_in and opt_out

sample url
    
    /<program_id>/job_distribution/<uuid:vendor_id>/<str:job_id>

example:

    /19106c90-e1f5-4016-b7bf-3cdf24a2b183/job_distribution/85a1e450-e5ba-4558-9baa-8f36d5d1966f/38a111d6-8770-41fe-8d4a-ad13ff468749

where sample request body are given below 

    {
            "opt_option": "opt_out"
    }

Sample response are given below 

    [
        {
            "id": 99,
            "job": {
                "id": 4,
                "uid": "38a111d6-8770-41fe-8d4a-ad13ff468749",
                "job_manager": {
                    "id": "b04e32cd-0584-41d0-89a1-8eac3101c046",
                    "first_name": "SK12",
                    "last_name": "simplify",
                    "email": "shahbaz@vms.com"
                },
                "msp_manager": {
                    "id": "b04e32cd-0584-41d0-89a1-8eac3101c046",
                    "first_name": "SK12",
                    "last_name": "simplify",
                    "email": "shahbaz@vms.com"
                },
                "title": 166,
                "category": 1,
                "foundational": 1,
                "type": "Permanent",
                "hire_type": "testt",
                "company_name": "Wiproooo",
                "level": "101",
                "no_of_openings": 10,
                "rate": null,
                "rate_type": null,
                "hours_per_day": null,
                "total_hours": null,
                "total_days": null,
                "additional_amount": null,
                "adjustment_type": null,
                "allow_expense": false,
                "assignment_length": null,
                "min_budget": 5000.0,
                "max_budget": 7000.0,
                "adjustment_value": null,
                "location_id": "2b531d63-c901-4cb1-8d61-b306768a4fe1",
                "description": "<p>its for update new update</p>",
                "start_date": "2020-08-24T07:02:44Z",
                "end_date": "2020-10-24T07:02:47Z",
                "hierarchy": "0fbc31e5-3461-456d-bf0f-5c5ea986c919",
                "hierarchy_location": null,
                "budget_estimate": null,
                "currency": null,
                "min_bill_rate": 7000.0,
                "max_bill_rate": 9000.0,
                "shift": null,
                "distribution": null,
                "shift_calender": null,
                "pre_identified_candidate": false,
                "pre_identified_vendor": false,
                "schedule_interview": "No",
                "response_by_date": null,
                "approve": true,
                "is_template": true,
                "template": null,
                "qualifications": [
                    {
                        "values": [
                            {
                                "id": "681a0053-43cd-4b5f-93a6-411ab3816b3f",
                                "level": 0,
                                "is_active": false
                            },
                            {
                                "id": "83e31c1c-46df-4600-bb6a-c8e9fa5236c8",
                                "level": 0,
                                "is_active": false
                            }
                        ],
                        "qualification_type": "credential",
                        "qualification_type_id": "0c3bcbf8-a6f5-4587-86b9-bf2ee9a53cea"
                    },
                    {
                        "values": [
                            {
                                "id": "6a646011-05f0-400e-b7bc-072c928ab1df",
                                "level": 0,
                                "is_active": false
                            }
                        ],
                        "qualification_type": "certification",
                        "qualification_type_id": "c86ff0d8-8752-4f6c-ace7-eb095a165168"
                    },
                    {
                        "values": [
                            {
                                "id": "0fab15f5-ac63-48c7-b908-60d463b56556",
                                "level": 1,
                                "is_active": false
                            },
                            {
                                "id": "5c124241-997d-4198-be36-60bf3008ed89",
                                "level": 3,
                                "is_active": false
                            }
                        ],
                        "qualification_type": "skill",
                        "qualification_type_id": "9cfbe517-66e3-4d2b-a92e-e070c25d9ee1"
                    }
                ],
                "tags": [
                    1
                ],
                "created_by": {
                    "id": "b04e32cd-0584-41d0-89a1-8eac3101c046",
                    "first_name": "SK12",
                    "last_name": "simplify",
                    "email": "shahbaz@vms.com"
                },
                "modified_by": {
                    "id": "2bf449a9-66ac-4d4b-96e1-164a396ca9bb",
                    "first_name": "SimplifyVMS",
                    "last_name": "Admin",
                    "email": "simplifyvms.superadmin@simplifyvms.info"
                },
                "is_delete": false,
                "status": "pending_approval"
            },
            "distribution_id": null,
            "distribute_method": null,
            "vendor_selection": null,
            "vendor_id": "85a1e450-e5ba-4558-9baa-8f36d5d1966f",
            "vendor_group_id": null,
            "distribute_type": "manual",
            "opt_option": "opt_out"
        }
    ]
"""
