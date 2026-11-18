from app.a2ui import decision_update, initial_surface
from app.decisions import DecisionResult


def test_initial_surface_uses_a2ui_v1():
    messages = initial_surface()
    create = messages[0]["createSurface"]
    components = create["components"]

    assert messages[0]["version"] == "1.0"
    assert create["catalogId"] == (
        "https://a2ui.org/specification/v1_0/catalogs/basic/catalog.json"
    )
    assert create["surfaceId"] == "decision"
    assert create["dataModel"]["input"] == ""
    assert create["dataModel"]["instructions"] == ""
    assert any(
        component.get("component") == "TextField"
        and component.get("value") == {"@path": "/input"}
        for component in components
    )
    submit = next(
        component
        for component in components
        if component.get("component") == "Button"
    )
    assert submit["action"]["event"]["name"] == "submit_decision"
    assert submit["action"]["event"]["context"]["input"] == {"@path": "/input"}


def test_decision_update_is_a_v1_data_model_message():
    result = DecisionResult(noul=0.99, confidence=0.99, label="Yes")

    messages = decision_update(result)

    assert messages[0] == {
        "version": "1.0",
        "updateDataModel": {
            "surfaceId": "decision",
            "path": "/result",
            "value": {
                "label": "Yes",
                "noul": 0.99,
                "confidence": 0.99,
                "noulText": "P(yes) = 0.99",
                "confidenceText": "Confidence = 0.99",
            },
        },
    }
