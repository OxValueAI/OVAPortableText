import { OVAPortableTextEditor } from "@ova/portable-text-editor-react";
import { createRoot } from "react-dom/client";
import fixture from "../../../fixtures/report-v1.3-company.json";
import "./styles.css";

createRoot(document.getElementById("root")!).render(
  <OVAPortableTextEditor
    initialValue={fixture}
    versioning={{
      enabled: true,
      documentKey: "golden-fixture-company-report"
    }}
    onSave={(document) => {
      console.info("Saved document", document.schemaVersion);
    }}
    onRequestFinalPreview={(document) => {
      console.info("Final preview requested", document.schemaVersion);
    }}
  />
);
