"use client";

import { useState } from "react";

export interface Suggestion {
  id: string;
  targetPath: string;
  type: "edit" | "add" | "remove";
  original?: string;
  suggested: string;
  reason?: string;
}

interface SuggestionsPanelProps {
  suggestions: Suggestion[];
  onAccept: (suggestionId: string) => void;
  onReject: (suggestionId: string) => void;
  onAcceptAll: () => void;
  onRejectAll: () => void;
}

export default function SuggestionsPanel({
  suggestions,
  onAccept,
  onReject,
  onAcceptAll,
  onRejectAll,
}: SuggestionsPanelProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const handleAccept = (id: string) => {
    onAccept(id);
    // Move to next suggestion if available
    const currentIndex = suggestions.findIndex((s) => s.id === id);
    if (currentIndex < suggestions.length - 1) {
      setSelectedId(suggestions[currentIndex + 1].id);
    }
  };

  const handleReject = (id: string) => {
    onReject(id);
    // Move to next suggestion if available
    const currentIndex = suggestions.findIndex((s) => s.id === id);
    if (currentIndex < suggestions.length - 1) {
      setSelectedId(suggestions[currentIndex + 1].id);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent, id: string) => {
    if (e.key === "a" && e.metaKey) {
      e.preventDefault();
      handleAccept(id);
    } else if (e.key === "r" && e.metaKey) {
      e.preventDefault();
      handleReject(id);
    }
  };

  if (suggestions.length === 0) {
    return (
      <div className="w-96 border-l bg-gray-50 p-6">
        <h2 className="text-lg font-semibold mb-4">Suggestions</h2>
        <p className="text-sm text-gray-600">No suggestions at this time.</p>
      </div>
    );
  }

  return (
    <div className="w-96 border-l bg-gray-50 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b bg-white">
        <h2 className="text-lg font-semibold mb-2">Suggestions</h2>
        <p className="text-sm text-gray-600 mb-4">
          {suggestions.length} suggestion{suggestions.length !== 1 ? "s" : ""} pending
        </p>
        <div className="flex gap-2">
          <button
            onClick={onAcceptAll}
            className="flex-1 px-3 py-2 text-sm bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
          >
            Accept All
          </button>
          <button
            onClick={onRejectAll}
            className="flex-1 px-3 py-2 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
          >
            Reject All
          </button>
        </div>
      </div>

      {/* Suggestions List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {suggestions.map((suggestion) => (
          <div
            key={suggestion.id}
            className={`border rounded-lg p-4 bg-white ${
              selectedId === suggestion.id ? "ring-2 ring-blue-500" : ""
            }`}
            onClick={() => setSelectedId(suggestion.id)}
            onKeyDown={(e) => handleKeyDown(e, suggestion.id)}
            tabIndex={0}
            role="button"
          >
            {/* Type Badge */}
            <div className="flex items-center justify-between mb-2">
              <span
                className={`text-xs px-2 py-1 rounded font-medium ${
                  suggestion.type === "edit"
                    ? "bg-blue-100 text-blue-800"
                    : suggestion.type === "add"
                    ? "bg-green-100 text-green-800"
                    : "bg-red-100 text-red-800"
                }`}
              >
                {suggestion.type.toUpperCase()}
              </span>
              <span className="text-xs text-gray-500">{suggestion.targetPath.split(".").pop()}</span>
            </div>

            {/* Original Text */}
            {suggestion.original && (
              <div className="mb-2">
                <p className="text-xs text-gray-600 mb-1">Original:</p>
                <p className="text-sm text-gray-800 bg-gray-50 p-2 rounded line-through">
                  {suggestion.original}
                </p>
              </div>
            )}

            {/* Suggested Text */}
            <div className="mb-2">
              <p className="text-xs text-gray-600 mb-1">Suggested:</p>
              <p className="text-sm text-gray-900 bg-yellow-50 p-2 rounded">
                {suggestion.suggested}
              </p>
            </div>

            {/* Reason */}
            {suggestion.reason && (
              <div className="mb-3">
                <p className="text-xs text-gray-600 mb-1">Reason:</p>
                <p className="text-xs text-gray-700">{suggestion.reason}</p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-2">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleAccept(suggestion.id);
                }}
                className="flex-1 px-3 py-2 text-sm bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                title="Cmd+A"
              >
                Accept
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleReject(suggestion.id);
                }}
                className="flex-1 px-3 py-2 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
                title="Cmd+R"
              >
                Reject
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Keyboard Shortcuts Help */}
      <div className="p-4 border-t bg-white">
        <p className="text-xs text-gray-600">
          Keyboard shortcuts: <kbd className="px-1 py-0.5 bg-gray-100 rounded">Cmd+A</kbd> Accept,{" "}
          <kbd className="px-1 py-0.5 bg-gray-100 rounded">Cmd+R</kbd> Reject
        </p>
      </div>
    </div>
  );
}
