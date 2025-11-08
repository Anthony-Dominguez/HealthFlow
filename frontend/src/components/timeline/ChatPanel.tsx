"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ArrowUp, MessageCircle, ChevronRight, Loader2 } from "lucide-react";
import { useState } from "react";

interface MedicalEvent {
  id: string;
  type: string;
  title: string;
  description: string;
  date: string;
  endDate?: string;
}

interface ChatPanelProps {
  collapsed: boolean;
  onToggle: () => void;
  selectedEvent: string | null;
  events?: MedicalEvent[];
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export function ChatPanel({ collapsed, onToggle, selectedEvent, events = [] }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Show selected event details in chat
  const handleEventSelection = (eventId: string | null) => {
    if (!eventId || !events.length) return;

    const event = events.find(e => e.id === eventId);
    if (!event) return;

    const eventMessage: Message = {
      id: `event-${eventId}-${Date.now()}`,
      role: "assistant",
      content: `📋 **${event.title}**\n\n${event.description}\n\n📅 Date: ${new Date(event.date).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}${event.endDate ? ` - ${new Date(event.endDate).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}` : ""}\n\n💊 Type: ${event.type}`,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, eventMessage]);
  };

  // Watch for selected event changes
  useState(() => {
    if (selectedEvent) {
      handleEventSelection(selectedEvent);
    }
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Call backend API
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: input,
          events: events, // Send medical context
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response");
      }

      const data = await response.json();

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.message || "I'm analyzing your health data.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, I'm having trouble connecting to the server. Using demo mode: Based on your timeline, you have 1 active medication (Lisinopril) and your last checkup was in February 2024.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className={`
        bg-slate-900/50 backdrop-blur-xl border-l border-slate-700/50
        transition-all duration-300 flex flex-col
        ${collapsed ? "w-16" : "w-80"}
      `}
    >
      {/* Header */}
      <div className="p-4 border-b border-slate-700/50">
        <div className="flex items-center justify-between">
          {!collapsed && (
            <div className="flex items-center gap-2">
              <MessageCircle className="h-5 w-5 text-blue-400" />
              <h2 className="text-lg font-semibold text-white">Chat</h2>
            </div>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggle}
            className="text-slate-400 hover:text-white hover:bg-slate-800/50"
          >
            <ChevronRight
              className={`h-5 w-5 transition-transform ${collapsed ? "rotate-180" : ""}`}
            />
          </Button>
        </div>
      </div>

      {!collapsed && (
        <>
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="bg-white/[0.02] rounded-lg p-4">
                <h3 className="text-white/50 font-medium text-sm mb-3">
                  Ask about your health
                </h3>
                <ul className="space-y-2 text-slate-400 text-sm">
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>What medications am I taking?</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>When was my last checkup?</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Show my lab results</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>Summarize my symptoms</span>
                  </li>
                </ul>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`p-3 rounded-lg ${
                    message.role === "user"
                      ? "bg-slate-800/50 border border-slate-600/50 ml-8"
                      : "mr-8"
                  }`}
                >
                  <div
                    className={`text-sm ${
                      message.role === "user" ? "text-gray-300" : "text-[#B7BCC5]"
                    }`}
                  >
                    {message.content}
                  </div>
                </div>
              ))
            )}

            {isLoading && (
              <div className="flex items-center gap-2 text-slate-400 text-sm">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Thinking...</span>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-slate-700/50">
            <form onSubmit={handleSubmit}>
              <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-600/50">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask about your health..."
                  className="bg-transparent border-none text-white placeholder-gray-500 p-0 focus-visible:ring-0"
                  disabled={isLoading}
                />
                <div className="flex justify-end mt-2">
                  <Button
                    type="submit"
                    variant="ghost"
                    size="sm"
                    className={`h-8 w-8 p-0 rounded-md transition-all ${
                      !input.trim() || isLoading
                        ? "text-gray-400"
                        : "bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:opacity-90 shadow-lg shadow-blue-500/20"
                    }`}
                    disabled={!input.trim() || isLoading}
                  >
                    <ArrowUp className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </form>
          </div>
        </>
      )}
    </div>
  );
}
