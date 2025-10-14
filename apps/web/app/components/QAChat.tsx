"use client";

import { useState, useEffect, useRef, ChangeEvent } from "react";

interface Message {
  id: string;
  type: "question" | "answer";
  content: string;
  timestamp: Date;
}

interface QAChatProps {
  sessionId: string;
  onComplete?: () => void;
}

const STORAGE_KEY_PREFIX = "qa_session_";

export default function QAChat({ sessionId, onComplete }: QAChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [isWaitingForQuestion, setIsWaitingForQuestion] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Load draft from localStorage on mount
  useEffect(() => {
    const savedData = localStorage.getItem(STORAGE_KEY_PREFIX + sessionId);
    if (savedData) {
      try {
        const { messages: savedMessages, currentAnswer: savedAnswer } = JSON.parse(savedData);
        setMessages(savedMessages.map((m: Message) => ({ ...m, timestamp: new Date(m.timestamp) })));
        setCurrentAnswer(savedAnswer || "");
      } catch (err) {
        console.error("Failed to load saved session", err);
      }
    }

    // Simulate initial question
    if (messages.length === 0) {
      setTimeout(() => {
        const initialQuestion: Message = {
          id: "q1",
          type: "question",
          content: "Tell us about your most significant professional achievement.",
          timestamp: new Date(),
        };
        setMessages([initialQuestion]);
      }, 500);
    }
  }, [sessionId]);

  // Autosave to localStorage
  useEffect(() => {
    if (messages.length > 0 || currentAnswer) {
      const dataToSave = {
        messages,
        currentAnswer,
        lastSaved: new Date().toISOString(),
      };
      localStorage.setItem(STORAGE_KEY_PREFIX + sessionId, JSON.stringify(dataToSave));
      setIsSaving(true);
      const timer = setTimeout(() => setIsSaving(false), 1000);
      return () => clearTimeout(timer);
    }
  }, [messages, currentAnswer, sessionId]);

  // Auto-scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = textareaRef.current.scrollHeight + "px";
    }
  }, [currentAnswer]);

  const handleAnswerChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setCurrentAnswer(e.target.value);
  };

  const handleSubmit = async () => {
    if (!currentAnswer.trim() || isWaitingForQuestion) return;

    // Add answer to messages
    const answer: Message = {
      id: `a${messages.length + 1}`,
      type: "answer",
      content: currentAnswer,
      timestamp: new Date(),
    };
    setMessages([...messages, answer]);
    setCurrentAnswer("");
    setIsWaitingForQuestion(true);

    // Simulate receiving next question from SSE
    setTimeout(() => {
      const nextQuestion: Message = {
        id: `q${messages.length + 2}`,
        type: "question",
        content: "What skills did you develop in this role?",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, nextQuestion]);
      setIsWaitingForQuestion(false);

      // After 3 questions, trigger completion
      if (messages.length >= 5) {
        setTimeout(() => {
          onComplete?.();
        }, 1000);
      }
    }, 2000);
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLTextAreaElement>) => {
    // Preserve formatting on paste
    const pastedText = e.clipboardData.getData("text");
    if (pastedText) {
      // Allow default paste behavior but could add custom handling here
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-white">
      {/* Header */}
      <div className="border-b p-4 bg-gray-50">
        <h2 className="text-xl font-semibold">Q&A Session</h2>
        <p className="text-sm text-gray-600 mt-1">
          Answer questions to help us understand your background
        </p>
        {isSaving && (
          <p className="text-xs text-green-600 mt-1">Draft saved...</p>
        )}
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === "answer" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-2xl p-4 rounded-lg ${
                message.type === "question"
                  ? "bg-blue-100 text-blue-900"
                  : "bg-gray-100 text-gray-900"
              }`}
            >
              <p className="text-sm font-medium mb-1">
                {message.type === "question" ? "Question" : "Your Answer"}
              </p>
              <p className="whitespace-pre-wrap">{message.content}</p>
              <p className="text-xs text-gray-500 mt-2">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}

        {isWaitingForQuestion && (
          <div className="flex justify-start">
            <div className="bg-blue-100 text-blue-900 p-4 rounded-lg">
              <p className="text-sm">Loading next question...</p>
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t p-4 bg-gray-50">
        <div className="space-y-2">
          <textarea
            ref={textareaRef}
            value={currentAnswer}
            onChange={handleAnswerChange}
            onPaste={handlePaste}
            onKeyDown={handleKeyDown}
            disabled={isWaitingForQuestion}
            placeholder="Type your answer here... (Cmd/Ctrl+Enter to submit)"
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none min-h-[100px] max-h-[300px] disabled:opacity-50"
            rows={3}
          />
          <div className="flex items-center justify-between">
            <p className="text-xs text-gray-500">
              {currentAnswer.length} characters
            </p>
            <button
              onClick={handleSubmit}
              disabled={!currentAnswer.trim() || isWaitingForQuestion}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {isWaitingForQuestion ? "Submitting..." : "Submit Answer"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
