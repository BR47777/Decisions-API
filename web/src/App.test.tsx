import { describe, expect, it, vi } from "vitest";

import type { ReactCatalogComponent } from "@a2ui/react";
import { basicCatalog } from "@a2ui/web_core/catalogs/basic/v1";
import { MessageProcessor } from "@a2ui/web_core";

import { submitDecisionAction } from "./decisionClient";

const action = {
  name: "submit_decision",
  surfaceId: "decision",
  sourceComponentId: "submit",
  timestamp: "2026-11-18T00:00:00Z",
  context: {
    input: "The mug arrived cracked.",
    instructions: "Did it arrive damaged?",
    true_description: "",
    false_description: "",
  },
};

function createProcessor(initialResult = { label: "", noulText: "" }) {
  const processor = new MessageProcessor<ReactCatalogComponent>([basicCatalog]);
  processor.processMessages([
    {
      version: "1.0",
      createSurface: {
        surfaceId: "decision",
        catalogId: basicCatalog.id,
        components: [
          { id: "root", component: "Text", text: "Decision check" },
        ],
        dataModel: { result: initialResult, status: "Ready", error: "" },
      },
    },
  ]);
  return processor;
}

describe("submitDecisionAction", () => {
  it("applies the A2UI result update from the server", async () => {
    const processor = createProcessor();
    const responseMessages = [
      {
        version: "1.0",
        updateDataModel: {
          surfaceId: "decision",
          path: "/result",
          value: {
            label: "Yes",
            noul: 0.99,
            confidence: 0.99,
            noulText: "P(yes) = 0.99",
            confidenceText: "Confidence = 0.99",
          },
        },
      },
    ];
    const fetcher = vi.fn(async () => ({
      ok: true,
      status: 200,
      json: async () => responseMessages,
    }) as Response);

    await submitDecisionAction(processor, action, fetcher);

    expect(fetcher).toHaveBeenCalledWith(
      "/api/actions",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ version: "1.0", action }),
      }),
    );
    expect(
      processor.model.surfacesMap.get("decision")?.dataModel.get("/result"),
    ).toEqual(responseMessages[0].updateDataModel.value);
  });

  it("clears stale results and shows a transport error", async () => {
    const processor = createProcessor({ label: "Yes", noulText: "P(yes) = 0.99" });
    const fetcher = vi.fn(async () => ({
      ok: false,
      status: 502,
      json: async () => ({ detail: "Decision request failed." }),
    }) as Response);

    await submitDecisionAction(processor, action, fetcher);

    const surface = processor.model.surfacesMap.get("decision");
    expect(surface?.dataModel.get("/result")).toEqual({
      label: "",
      noul: null,
      confidence: null,
      noulText: "",
      confidenceText: "",
    });
    expect(surface?.dataModel.get("/error")).toBe("Decision request failed.");
  });
});
