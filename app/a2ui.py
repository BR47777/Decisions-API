from app.decisions import DecisionResult


CATALOG_ID = "https://a2ui.org/specification/v1_0/catalogs/basic/catalog.json"
SURFACE_ID = "decision"


def _binding(path: str) -> dict[str, str]:
    return {"@path": path}


def initial_surface() -> list[dict[str, object]]:
    return [
        {
            "version": "1.0",
            "createSurface": {
                "surfaceId": SURFACE_ID,
                "catalogId": CATALOG_ID,
                "components": [
                    {
                        "id": "root",
                        "component": "Column",
                        "children": [
                            "title",
                            "input",
                            "instructions",
                            "true_description",
                            "false_description",
                            "submit",
                            "status",
                            "error",
                            "result_title",
                            "result_label",
                            "result_noul",
                            "result_confidence",
                        ],
                    },
                    {"id": "title", "component": "Text", "text": "Decision check"},
                    {
                        "id": "input",
                        "component": "TextField",
                        "label": "Text to evaluate",
                        "placeholder": "Describe the text or situation",
                        "value": _binding("/input"),
                    },
                    {
                        "id": "instructions",
                        "component": "TextField",
                        "label": "Yes/no question",
                        "placeholder": "What should the API decide?",
                        "value": _binding("/instructions"),
                    },
                    {
                        "id": "true_description",
                        "component": "TextField",
                        "label": "What counts as Yes? (optional)",
                        "value": _binding("/true_description"),
                    },
                    {
                        "id": "false_description",
                        "component": "TextField",
                        "label": "What counts as No? (optional)",
                        "value": _binding("/false_description"),
                    },
                    {
                        "id": "submit",
                        "component": "Button",
                        "child": "submit_label",
                        "variant": "primary",
                        "action": {
                            "event": {
                                "name": "submit_decision",
                                "context": {
                                    "input": _binding("/input"),
                                    "instructions": _binding("/instructions"),
                                    "true_description": _binding(
                                        "/true_description"
                                    ),
                                    "false_description": _binding(
                                        "/false_description"
                                    ),
                                },
                            }
                        },
                    },
                    {
                        "id": "submit_label",
                        "component": "Text",
                        "text": "Check decision",
                    },
                    {
                        "id": "status",
                        "component": "Text",
                        "text": _binding("/status"),
                    },
                    {
                        "id": "error",
                        "component": "Text",
                        "text": _binding("/error"),
                    },
                    {
                        "id": "result_title",
                        "component": "Text",
                        "text": "Result",
                    },
                    {
                        "id": "result_label",
                        "component": "Text",
                        "text": _binding("/result/label"),
                    },
                    {
                        "id": "result_noul",
                        "component": "Text",
                        "text": _binding("/result/noulText"),
                    },
                    {
                        "id": "result_confidence",
                        "component": "Text",
                        "text": _binding("/result/confidenceText"),
                    },
                ],
                "dataModel": {
                    "input": "",
                    "instructions": "",
                    "true_description": "",
                    "false_description": "",
                    "status": "Ready",
                    "error": "",
                    "result": {
                        "label": "",
                        "noulText": "",
                        "confidenceText": "",
                    },
                },
            },
        }
    ]


def decision_update(result: DecisionResult) -> list[dict[str, object]]:
    return [
        {
            "version": "1.0",
            "updateDataModel": {
                "surfaceId": SURFACE_ID,
                "path": "/result",
                "value": {
                    "label": result.label,
                    "noul": result.noul,
                    "confidence": result.confidence,
                    "noulText": f"P(yes) = {result.noul:.2f}",
                    "confidenceText": f"Confidence = {result.confidence:.2f}",
                },
            },
        },
        {
            "version": "1.0",
            "updateDataModel": {
                "surfaceId": SURFACE_ID,
                "path": "/status",
                "value": "Decision complete",
            },
        },
        {
            "version": "1.0",
            "updateDataModel": {
                "surfaceId": SURFACE_ID,
                "path": "/error",
                "value": "",
            },
        },
    ]
