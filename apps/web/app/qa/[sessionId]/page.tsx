"use client";

import { useParams, useRouter } from "next/navigation";
import QAChat from "../../components/QAChat";

export default function QASessionPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const handleComplete = () => {
    console.log("Q&A session completed");
    // Navigate to next step
    // router.push(`/review/${sessionId}`);
  };

  return <QAChat sessionId={sessionId} onComplete={handleComplete} />;
}
