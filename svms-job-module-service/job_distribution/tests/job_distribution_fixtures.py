JOB_DISTRIBUTION_POST_BODY = {
    "job_id": "6a77ea6f3b6146468a43370908535233",
    "distribution_id": [{
        "id": "19106c90-e1f5-4016-b7bf-3cdf24a2b171",
        "schedules": [
            {
                "schedule_unit": "HOURS",
                "schedule_value": 20,
                "vendors": ["19106c90-e1f5-4016-b7bf-3cdf24a2b180"],
                "vendor_group_id": ["9b8226eb-37c8-47bd-9f9e-33bdf02c9841"]
            },
            {
                "schedule_unit": "HOURS",
                "schedule_value": 20,
                "vendors": ["19106c90-e1f5-4016-b7bf-3cdf24a2b178",
                            "19106c90-e1f5-4016-b7bf-3cdf24a2b179"],
                "vendor_group_id": ["9b8226eb-37c8-47bd-9f9e-33bdf02c9841"]
            },
            {
                "schedule_unit": "IMMEDIATE",
                "vendors": ["19106c90-e1f5-4016-b7bf-3cdf24a2b176"],
                "vendor_group_id": ["9b8226eb-37c8-47bd-9f9e-33bdf02c9841"]
            },
            {
                "schedule_unit": "IMMEDIATE",
                "vendors": ["19106c90-e1f5-4016-b7bf-3cdf24a2b177"]
            }

        ]
    }],
    "distribute_type": "scheduled"

}

JOB_DISTRIBUTION_POST_RESPONSE = {
    "data": [
        {
            "id": 79,
            "job": {
                "id": 26,
                "uid": "b70a136c-c9fd-4431-a570-7dc34f8e042f",
                "job_manager": None,
                "msp_manager": None,
                "title": {
                    "id": 26,
                    "title": "software developer555",
                    "level": 3,
                    "description": "",
                    "job_tag": []
                },
                "category": {
                    "id": 26,
                    "o_net_soc_code": "199999999",
                    "category_name": "Remote Sensing Scientists and Technologistss",
                    "description": "Apply remote sensing principles and methods to analyze\
     data and solve problems in areas such as natural resource management,\
     urban planning, or homeland security. May develop new sensor systems,\
     analytical techniques, or new applications for existing systems."
                },
                "foundational": 26,
                "type": None,
                "hire_type": None,
                "company_name": None,
                "level": None,
                "no_of_openings": 8,
                "rate": None,
                "rate_type": None,
                "hours_per_day": None,
                "total_hours": None,
                "total_days": None,
                "additional_amount": None,
                "adjustment_type": None,
                "allow_expense": False,
                "assignment_length": None,
                "min_budget": None,
                "max_budget": None,
                "adjustment_value": None,
                "location_id": {},
                "description": None,
                "start_date": "2020-11-27T00:00:00Z",
                "end_date": "2020-11-28T00:00:00Z",
                "hierarchy": None,
                "hierarchy_location": None,
                "budget_estimate": None,
                "currency": None,
                "min_bill_rate": None,
                "max_bill_rate": None,
                "shift": None,
                "distribution": None,
                "shift_calender": None,
                "pre_identified_candidate": False,
                "pre_identified_vendor": False,
                "schedule_interview": "N0",
                "response_by_date": None,
                "approve": True,
                "is_template": False,
                "template": None,
                "qualifications": [],
                "tags": [],
                "created_by": None,
                "modified_by": None,
                "is_delete": False,
                "status": "Nothing"
            },
            "distribution_id": "19106c90-e1f5-4016-b7bf-3cdf24a2b171",
            "distribute_method": None,
            "vendor_selection": None,
            "vendor_id": "19106c90-e1f5-4016-b7bf-3cdf24a2b176",
            "vendor_group_id": None,
            "distribute_type": "scheduled",
            "opt_option": "no_response"
        }
    ],
    "status": 200
}

POST_SCHEDULED_BODY = {
    "job_id": 2147,
    "distribute_type": "automatic",
    "distribute_method": "on_submit",
    "vendor_selection": "industry_region"
}

POST_AUTO_MANUAL_BODY = {
    "job_id": "6a77ea6f3b6146468a43370908535233",
    "distribute_type": "automatic",
    "distribute_method": "final_approval",
    "vendor_selection": "manual_input",
    "vendors": ["19106c90-e1f5-4016-b7bf-3cdf24a2b164"],
    "vendor_group_id": ["9b8226eb-37c8-47bd-9f9e-33bdf02c9841"],
    "submission_limit": 20

}

POST_AUTO_MANUAL_RESPONSE = {
    "data": [
        {
            "id": 94,
            "job": {
                "id": 2149,
                "uid": "2f52e95b-c3bf-45aa-bac0-651ec3d3ef70",
                "job_manager": None,
                "msp_manager": None,
                "title": {
                    "id": 1,
                    "title": "Python Engineer",
                    "level": 123,
                    "description": "Test",
                    "job_tag": []
                },
                "category": {
                    "id": 1,
                    "o_net_soc_code": "11.0.0.1",
                    "category_name": "Developer",
                    "description": "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."
                },
                "foundational": 1,
                "type": None,
                "hire_type": None,
                "company_name": None,
                "level": "Developer",
                "no_of_openings": None,
                "rate": None,
                "rate_type": None,
                "hours_per_day": None,
                "total_hours": None,
                "total_days": None,
                "additional_amount": None,
                "adjustment_type": None,
                "allow_expense": False,
                "assignment_length": None,
                "min_budget": None,
                "max_budget": None,
                "adjustment_value": None,
                "location_id": {},
                "description": "<p>Test desc...111</p>",
                "start_date": "2020-11-02T18:30:00Z",
                "end_date": "2020-11-29T18:30:00Z",
                "hierarchy": "afa5b89c-695b-4d5a-8a73-4d8fd0985d12",
                "hierarchy_location": None,
                "budget_estimate": None,
                "currency": "CAD",
                "min_bill_rate": None,
                "max_bill_rate": None,
                "shift": None,
                "distribution": None,
                "shift_calender": None,
                "pre_identified_candidate": False,
                "pre_identified_vendor": False,
                "schedule_interview": "N0",
                "response_by_date": "2020-11-18",
                "approve": True,
                "is_template": False,
                "template": None,
                "qualifications": [],
                "tags": [
                    {
                        "id": 1,
                        "tag": "Python"
                    }
                ],
                "created_by": None,
                "modified_by": None,
                "is_delete": False,
                "status": "pending_approval"
            },
            "distribution_id": None,
            "distribute_method": "final_approval",
            "vendor_selection": "manual_input",
            "vendor_id": "19106c90-e1f5-4016-b7bf-3cdf24a2b164",
            "vendor_group_id": None,
            "distribute_type": "automatic",
            "opt_option": "no_response"
        }
    ],
    "status": 200
}
POST_MANUAL_BODY = {
    "job_id": "6a77ea6f3b6146468a43370908535233",
    "vendors": ["39106c90-e1f5-4016-b7bf-3cdf24a2b181",
                "39106c90-e1f5-4016-b7bf-3cdf24a2b184",
                "59106c90-e1f5-4016-b7bf-3cdf24a2b187"],
    "vendor_group_id": ["9b8226eb-37c8-47bd-9f9e-33bdf02c9841"],
    "distribute_type": "manual"
}

GET_JD_LIST = {
    "id": 186,
    "job": {
        "id": 89,
        "uid": "4040e456-849f-4100-8cdc-6b38e43ef501",
        "job_manager": None,
        "msp_manager": None,
        "title": {
            "id": 89,
            "title": "software developer555",
            "level": 3,
            "description": "",
            "job_tag": []
        },
        "category": {
            "id": 89,
            "o_net_soc_code": "199999999",
            "category_name": "Remote Sensing Scientists and Technologistss",
            "description": "Apply remote sensing principles and methods to analyze\
     data and solve problems in areas such as natural resource management,\
     urban planning, or homeland security. May develop new sensor systems,\
     analytical techniques, or new applications for existing systems."
        },
        "foundational": 89,
        "type": None,
        "hire_type": None,
        "company_name": None,
        "level": None,
        "no_of_openings": 8,
        "rate": None,
        "rate_type": None,
        "hours_per_day": None,
        "total_hours": None,
        "total_days": None,
        "additional_amount": None,
        "adjustment_type": None,
        "allow_expense": False,
        "assignment_length": None,
        "min_budget": None,
        "max_budget": None,
        "adjustment_value": None,
        "location_id": {},
        "description": None,
        "start_date": "2020-11-27T00:00:00Z",
        "end_date": "2020-11-28T00:00:00Z",
        "hierarchy": None,
        "hierarchy_location": None,
        "budget_estimate": None,
        "currency": None,
        "min_bill_rate": None,
        "max_bill_rate": None,
        "shift": None,
        "distribution": None,
        "shift_calender": None,
        "pre_identified_candidate": False,
        "pre_identified_vendor": False,
        "schedule_interview": "N0",
        "response_by_date": None,
        "approve": True,
        "is_template": False,
        "template": None,
        "qualifications": [],
        "tags": [],
        "created_by": None,
        "modified_by": None,
        "is_delete": False,
        "status": "Nothing"
    },
    "distribution_id": None,
    "distribute_method": None,
    "vendor_selection": None,
    "vendor_id": "39106c90-e1f5-4016-b7bf-3cdf24a2b181",
    "vendor_group_id": None,
    "distribute_type": "manual",
    "opt_option": "no_response"
}

GET_LIST = {
    "count": 5,
    "next": None,
    "previous": None,
    "results": [
        {
            "id": 281,
            "job": {
                "id": 116,
                "uid": "eefe8b29-3a4c-4b1f-9a87-e33e4d1a93fe",
                "job_manager": None,
                "msp_manager": None,
                "title": {
                    "id": 116,
                    "title": "software developer555",
                    "level": 3,
                    "description": "",
                    "job_tag": []
                },
                "category": {
                    "id": 116,
                    "o_net_soc_code": "199999999",
                    "category_name": "Remote Sensing Scientists and Technologistss",
                    "description": ""
                },
                "foundational": 116,
                "type": None,
                "hire_type": None,
                "company_name": None,
                "level": None,
                "no_of_openings": 8,
                "rate": None,
                "rate_type": None,
                "hours_per_day": None,
                "total_hours": None,
                "total_days": None,
                "additional_amount": None,
                "adjustment_type": None,
                "allow_expense": False,
                "assignment_length": None,
                "min_budget": None,
                "max_budget": None,
                "adjustment_value": None,
                "location_id": {},
                "description": None,
                "start_date": "2020-11-29T00:00:00Z",
                "end_date": "2020-11-30T00:00:00Z",
                "hierarchy": None,
                "hierarchy_location": None,
                "budget_estimate": None,
                "currency": None,
                "min_bill_rate": None,
                "max_bill_rate": None,
                "shift": None,
                "distribution": None,
                "shift_calender": None,
                "pre_identified_candidate": False,
                "pre_identified_vendor": False,
                "schedule_interview": "N0",
                "response_by_date": None,
                "approve": True,
                "is_template": False,
                "template": None,
                "qualifications": [],
                "tags": [],
                "created_by": None,
                "modified_by": None,
                "is_delete": False,
                "status": "Nothing"
            },
            "distribution_id": None,
            "distribute_method": None,
            "vendor_selection": None,
            "vendor_id": "39106c90-e1f5-4016-b7bf-3cdf24a2b181",
            "vendor_group_id": None,
            "distribute_type": "manual",
            "opt_option": "no_response"
        }
    ],
    "program_id": "f1a9413d-1ef5-44d6-ac4b-90e4952890be"
}

res = {
    "id": 331,
    "job": {
        "id": 127,
        "uid": "ceeb5d50-e8d4-47d7-8ead-0eb2ece0b70a",
        "job_manager": None,
        "msp_manager": None,
        "title": {
            "id": 127,
            "title": "software developer555",
            "level": 3,
            "description": "",
            "job_tag": []
        },
        "category": {
            "id": 127,
            "o_net_soc_code": "199999999",
            "category_name": "Remote Sensing Scientists and Technologistss",
            "description": ""
        },
        "foundational": 127,
        "type": None,
        "hire_type": None,
        "company_name": None,
        "level": None,
        "no_of_openings": 8,
        "rate": None,
        "rate_type": None,
        "hours_per_day": None,
        "total_hours": None,
        "total_days": None,
        "additional_amount": None,
        "adjustment_type": None,
        "allow_expense": False,
        "assignment_length": None,
        "min_budget": None,
        "max_budget": None,
        "adjustment_value": None,
        "location_id": {},
        "description": None,
        "start_date": "2020-11-29T00:00:00Z",
        "end_date": "2020-11-30T00:00:00Z",
        "hierarchy": None,
        "hierarchy_location": None,
        "budget_estimate": None,
        "currency": None,
        "min_bill_rate": None,
        "max_bill_rate": None,
        "shift": None,
        "distribution": None,
        "shift_calender": None,
        "pre_identified_candidate": False,
        "pre_identified_vendor": False,
        "schedule_interview": "N0",
        "response_by_date": None,
        "approve": True,
        "is_template": False,
        "template": None,
        "qualifications": [],
        "tags": [],
        "created_by": None,
        "modified_by": None,
        "is_delete": False,
        "status": "Nothing"
    },
    "distribution_id": None,
    "distribute_method": None,
    "vendor_selection": None,
    "vendor_id": "39106c90-e1f5-4016-b7bf-3cdf24a2b181",
    "vendor_group_id": None,
    "distribute_type": "manual",
    "opt_option": "no_response"
}

POST_SCHEDULED_PERIODIC_BODY = {
    "job_id": "6a77ea6f3b6146468a43370908535233",
    "distribution_id": [{
        "id": "19106c90-e1f5-4016-b7bf-3cdf24a2b171",
        "schedules": [
            {
                "schedule_unit": "HOURS",
                "schedule_value": 20,
                "vendors": ["19106c90-e1f5-4016-b7bf-3cdf24a2b172",
                            "19106c90-e1f5-4016-b7bf-3cdf24a2b177",
                            "19106c90-e1f5-4016-b7bf-3cdf24a2b190",
                            "52b42aee-4680-49b7-9897-db26be8e7354"],
                "vendor_group_id": ["9b8226eb-37c8-47bd-9f9e-33bdf02c9841"]
            }

        ]
    }],
    "distribute_type": "scheduled",
    "submission_limit": 20

}
