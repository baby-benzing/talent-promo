"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import SuggestionsPanel, { Suggestion } from "../../components/SuggestionsPanel";

export default function EditorPage() {
  const params = useParams();
  const documentId = params.documentId as string;

  // Mock suggestions for demonstration
  const [suggestions, setSuggestions] = useState<Suggestion[]>([
    {
      id: "sugg_1",
      targetPath: "sections.experience.roles.role_1.bullets.bullet_1",
      type: "edit",
      original: "Worked on web applications",
      suggested: "Built scalable web applications serving 1M+ users",
      reason: "More specific and quantifiable",
    },
    {
      id: "sugg_2",
      targetPath: "sections.experience.roles.role_1.bullets.bullet_2",
      type: "edit",
      original: "Led a team",
      suggested: "Led cross-functional team of 5 engineers to deliver critical features",
      reason: "Adds context and quantification",
    },
    {
      id: "sugg_3",
      targetPath: "sections.experience.roles.role_1.bullets.bullet_3",
      type: "add",
      suggested: "Implemented CI/CD pipeline reducing deployment time by 60%",
      reason: "Highlights technical achievement",
    },
  ]);

  const [acceptedCount, setAcceptedCount] = useState(0);
  const [rejectedCount, setRejectedCount] = useState(0);

  const handleAccept = (suggestionId: string) => {
    setSuggestions((prev) => prev.filter((s) => s.id !== suggestionId));
    setAcceptedCount((prev) => prev + 1);
    console.log("Accepted suggestion:", suggestionId);
  };

  const handleReject = (suggestionId: string) => {
    setSuggestions((prev) => prev.filter((s) => s.id !== suggestionId));
    setRejectedCount((prev) => prev + 1);
    console.log("Rejected suggestion:", suggestionId);
  };

  const handleAcceptAll = () => {
    setAcceptedCount((prev) => prev + suggestions.length);
    setSuggestions([]);
    console.log("Accepted all suggestions");
  };

  const handleRejectAll = () => {
    setRejectedCount((prev) => prev + suggestions.length);
    setSuggestions([]);
    console.log("Rejected all suggestions");
  };

  return (
    <div className="flex h-screen">
      {/* Editor Area */}
      <div className="flex-1 p-8 overflow-y-auto">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-2">Resume Editor</h1>
          <p className="text-gray-600 mb-8">Document ID: {documentId}</p>

          {/* Mock Resume Content */}
          <div className="space-y-6">
            <section>
              <h2 className="text-2xl font-semibold mb-4">Experience</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-xl font-medium">Software Engineer at Tech Corp</h3>
                  <ul className="list-disc list-inside mt-2 space-y-2">
                    <li>Worked on web applications</li>
                    <li>Led a team</li>
                  </ul>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4">Education</h2>
              <div>
                <h3 className="text-xl font-medium">BS Computer Science at State University</h3>
                <ul className="list-disc list-inside mt-2 space-y-2">
                  <li>Graduated with honors</li>
                </ul>
              </div>
            </section>
          </div>

          {/* Stats */}
          <div className="mt-8 p-4 bg-gray-100 rounded-lg">
            <p className="text-sm">
              <span className="font-semibold text-green-600">Accepted:</span> {acceptedCount} |{" "}
              <span className="font-semibold text-red-600">Rejected:</span> {rejectedCount}
            </p>
          </div>
        </div>
      </div>

      {/* Suggestions Panel */}
      <SuggestionsPanel
        suggestions={suggestions}
        onAccept={handleAccept}
        onReject={handleReject}
        onAcceptAll={handleAcceptAll}
        onRejectAll={handleRejectAll}
      />
    </div>
  );
}
