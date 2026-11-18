import { useEffect, useMemo, useRef, useState } from "react";

import { A2uiSurface, type ReactCatalogComponent } from "@a2ui/react";
import { basicCatalog } from "@a2ui/web_core/catalogs/basic/v1";
import {
  AgentToRendererMessageSchema,
  type AgentToRendererMessage,
} from "@a2ui/web_core/v1_0";
import { MessageProcessor } from "@a2ui/web_core";

import { submitDecisionAction } from "./decisionClient";
import "./styles.css";

export function App() {
  const processorRef = useRef<MessageProcessor<ReactCatalogComponent> | null>(
    null,
  );
  const processor = useMemo(
    () =>
      new MessageProcessor<ReactCatalogComponent>([basicCatalog], (action) =>
        processorRef.current
          ? submitDecisionAction(processorRef.current, action)
          : undefined,
      ),
    [],
  );
  processorRef.current = processor;
  const [surfaces, setSurfaces] = useState(() =>
    Array.from(processor.model.surfacesMap.values()),
  );
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    const created = processor.onSurfaceCreated(() => {
      setSurfaces(Array.from(processor.model.surfacesMap.values()));
    });
    const deleted = processor.onSurfaceDeleted(() => {
      setSurfaces(Array.from(processor.model.surfacesMap.values()));
    });
    let active = true;

    async function loadSurface() {
      try {
        const response = await fetch("/api/surface");
        if (!response.ok) {
          throw new Error(`Could not load the decision form (${response.status}).`);
        }
        const messages: AgentToRendererMessage[] =
          AgentToRendererMessageSchema.array().parse(await response.json());
        if (active) {
          processor.processMessages(messages);
        }
      } catch (error) {
        if (active) {
          setLoadError(
            error instanceof Error ? error.message : "Could not load the decision form.",
          );
        }
      }
    }

    void loadSurface();
    return () => {
      active = false;
      created.unsubscribe();
      deleted.unsubscribe();
    };
  }, [processor]);

  return (
    <main className="app-shell">
      <header className="app-header">
        <p className="eyebrow">Gemini Decision 1</p>
        <h1>Make a decision from text</h1>
        <p>
          Ask a focused yes/no question. The result includes a calibrated
          probability and confidence.
        </p>
      </header>
      {loadError && <p className="load-error" role="alert">{loadError}</p>}
      <section className="decision-surface" aria-label="Decision form">
        {surfaces.map((surface) => (
          <A2uiSurface key={surface.id} surface={surface} />
        ))}
      </section>
      <footer>
        Use the probability and confidence as signals, not guarantees. Choose
        decision thresholds appropriate to your application.
      </footer>
    </main>
  );
}
