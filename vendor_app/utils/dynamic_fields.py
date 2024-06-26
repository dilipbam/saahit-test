VENDOR_INDUSTRY_ADDITIONAL_FIELDS = {
    "field_name": {
        "validation": {
            "type": "string",
            "required": True,
        }
    },
    "display_name": {
        "validation": {
            "type": "string",
            "required": True
        }
    },
    "required": {
        "validation": {
            "type": "boolean",
            "required": True
        }
    },
    "type_of_field": {
        "validation": {
            "type": "select",
            "required": True,
            "selection_type": "string",
            "options": [
                "number",
                "range",
                "textarea",
                "file",
                "checklist",
                "radio"
            ]
        }
    },
    "data_type": {
        "validation": {
            "type": "select",
            "required": True,
            "selection_type": "string",
            "options": ["string", "integer", "date", "datetime", "decimal","image"]
        }
    },
    "field_value": {
        "checklist": "list",
    }
}
