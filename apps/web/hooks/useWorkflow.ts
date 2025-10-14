import { useState } from "react";

interface WorkflowState {
  status: string;
  error: string | null;
  loading: boolean;
}

export function useWorkflow(runId: string) {
  const [state, setState] = useState<WorkflowState>({
    status: "waiting",
    error: null,
    loading: false,
  });

  const submitEdits = async (edits: unknown[]) => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const response = await fetch("http://localhost:8000/api/workflow/submit_edits", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ run_id: runId, edits }),
      });

      if (!response.ok) {
        throw new Error("Failed to submit edits");
      }

      const data = await response.json();
      setState({ status: data.status, error: null, loading: false });
      return data;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Unknown error";
      setState((prev) => ({ ...prev, error: errorMsg, loading: false }));
      throw error;
    }
  };

  const resolveSuggestions = async (suggestionIds: string[]) => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const response = await fetch("http://localhost:8000/api/workflow/resolve_suggestions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ run_id: runId, suggestion_ids: suggestionIds }),
      });

      if (!response.ok) {
        throw new Error("Failed to resolve suggestions");
      }

      const data = await response.json();
      setState({ status: data.status || "processing", error: null, loading: false });
      return data;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Unknown error";
      setState((prev) => ({ ...prev, error: errorMsg, loading: false }));
      throw error;
    }
  };

  const approve = async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const response = await fetch("http://localhost:8000/api/workflow/approve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ run_id: runId }),
      });

      if (!response.ok) {
        throw new Error("Failed to approve");
      }

      const data = await response.json();
      setState({ status: data.status, error: null, loading: false });
      return data;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Unknown error";
      setState((prev) => ({ ...prev, error: errorMsg, loading: false }));
      throw error;
    }
  };

  const getStatus = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/workflow/status/${runId}`);

      if (!response.ok) {
        throw new Error("Failed to get status");
      }

      const data = await response.json();
      setState((prev) => ({ ...prev, status: data.status }));
      return data;
    } catch (error) {
      console.error("Failed to get workflow status:", error);
      return null;
    }
  };

  return {
    ...state,
    submitEdits,
    resolveSuggestions,
    approve,
    getStatus,
  };
}
