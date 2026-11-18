import type { ActionPayload } from "@a2ui/web_core";
import type { ReactCatalogComponent } from "@a2ui/react";
import {
  AgentToRendererMessageSchema,
  type AgentToRendererMessage,
} from "@a2ui/web_core/v1_0";
import type { MessageProcessor } from "@a2ui/web_core";

type DataModelUpdate = Extract<
  AgentToRendererMessage,
  { updateDataModel: unknown }
>;

function update(
  surfaceId: string,
  path: string,
  value: unknown,
): DataModelUpdate {
  return {
    version: "1.0",
    updateDataModel: { surfaceId, path, value },
  };
}

export async function submitDecisionAction(
  processor: MessageProcessor<ReactCatalogComponent>,
  action: ActionPayload,
  fetcher: typeof fetch = fetch,
): Promise<void> {
  if (action.name !== "submit_decision") {
    return;
  }

  processor.processMessages([
    update(action.surfaceId, "/result", {
      label: "",
      noul: null,
      confidence: null,
      noulText: "",
      confidenceText: "",
    }),
    update(action.surfaceId, "/status", "Checking…"),
    update(action.surfaceId, "/error", ""),
  ]);

  try {
    const response = await fetcher("/api/actions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ version: "1.0", action }),
    });

    if (!response.ok) {
      const body: unknown = await response.json();
      const detail =
        typeof body === "object" &&
        body !== null &&
        "detail" in body &&
        typeof body.detail === "string"
          ? body.detail
          : `Decision request failed (${response.status}).`;
      throw new Error(detail);
    }

    const messages = AgentToRendererMessageSchema.array().parse(
      await response.json(),
    );
    processor.processMessages(messages);
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Decision request failed.";
    processor.processMessages([
      update(action.surfaceId, "/status", "Decision failed"),
      update(action.surfaceId, "/error", message),
    ]);
  }
}
