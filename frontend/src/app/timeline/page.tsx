"use client";

import { useState } from "react";
import { TimelineSidebar } from "@/components/timeline/TimelineSidebar";
import { TimelineCanvas } from "@/components/timeline/TimelineCanvas";
import { ChatPanel } from "@/components/timeline/ChatPanel";
import { Pill, Stethoscope, FileText, Mic, Activity } from "lucide-react";

// Mock medical events data
const medicalEvents = [
  {
    id: "evt-1",
    type: "medication",
    title: "Lisinopril 10mg",
    description: "Blood pressure medication",
    date: "2024-01-05",
    endDate: "2024-03-15",
    icon: Pill,
    color: "blue",
  },
  {
    id: "evt-2",
    type: "appointment",
    title: "Cardiology Checkup",
    description: "Dr. Smith - Annual heart checkup",
    date: "2024-01-15",
    icon: Stethoscope,
    color: "green",
  },
  {
    id: "evt-3",
    type: "lab",
    title: "Blood Work",
    description: "Cholesterol: 180 mg/dL, Blood Pressure: 120/80",
    date: "2024-02-01",
    icon: Activity,
    color: "purple",
  },
  {
    id: "evt-4",
    type: "diagnosis",
    title: "Hypertension",
    description: "Stage 1 - Monitor and medication prescribed",
    date: "2024-01-05",
    icon: FileText,
    color: "red",
  },
  {
    id: "evt-5",
    type: "voice",
    title: "Symptom Note",
    description: "Feeling dizzy after morning medication",
    date: "2024-02-10",
    icon: Mic,
    color: "yellow",
  },
  {
    id: "evt-6",
    type: "appointment",
    title: "Follow-up Visit",
    description: "Dr. Smith - Check medication effectiveness",
    date: "2024-02-28",
    icon: Stethoscope,
    color: "green",
  },
  {
    id: "evt-7",
    type: "lab",
    title: "Blood Pressure Check",
    description: "115/75 - Improved",
    date: "2024-03-10",
    icon: Activity,
    color: "purple",
  },
];

export default function TimelinePage() {
  const [selectedEvent, setSelectedEvent] = useState<string | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [chatCollapsed, setChatCollapsed] = useState(false);

  return (
    <div className="flex h-screen bg-slate-950 text-white overflow-hidden">
      {/* Left Sidebar */}
      <TimelineSidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main Timeline Canvas */}
      <TimelineCanvas
        selectedEvent={selectedEvent}
        onEventSelect={setSelectedEvent}
        events={medicalEvents}
      />

      {/* Right Chat Panel */}
      <ChatPanel
        collapsed={chatCollapsed}
        onToggle={() => setChatCollapsed(!chatCollapsed)}
        selectedEvent={selectedEvent}
        events={medicalEvents}
      />
    </div>
  );
}
