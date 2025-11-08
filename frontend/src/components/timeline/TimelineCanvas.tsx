"use client";

import { useState } from "react";
import { Filter, Search, Calendar, Pill, Stethoscope, FileText, Mic, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface MedicalEvent {
  id: string;
  type: string;
  title: string;
  description: string;
  date: string;
  endDate?: string;
  icon: any;
  color: string;
}

interface TimelineCanvasProps {
  selectedEvent: string | null;
  onEventSelect: (eventId: string | null) => void;
  events: MedicalEvent[];
}

const colorMap: Record<string, string> = {
  blue: "bg-blue-500/10 border-blue-400/30 hover:bg-blue-500/20 hover:border-blue-400/50",
  green: "bg-emerald-500/10 border-emerald-400/30 hover:bg-emerald-500/20 hover:border-emerald-400/50",
  purple: "bg-purple-500/10 border-purple-400/30 hover:bg-purple-500/20 hover:border-purple-400/50",
  red: "bg-rose-500/10 border-rose-400/30 hover:bg-rose-500/20 hover:border-rose-400/50",
  yellow: "bg-amber-500/10 border-amber-400/30 hover:bg-amber-500/20 hover:border-amber-400/50",
};

export function TimelineCanvas({ selectedEvent, onEventSelect, events }: TimelineCanvasProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [activeFilter, setActiveFilter] = useState<string | null>(null);

  const filters = [
    { type: "all", label: "All Events", count: events.length },
    { type: "medication", label: "Medications", count: events.filter(e => e.type === "medication").length },
    { type: "appointment", label: "Appointments", count: events.filter(e => e.type === "appointment").length },
    { type: "lab", label: "Lab Results", count: events.filter(e => e.type === "lab").length },
    { type: "diagnosis", label: "Diagnoses", count: events.filter(e => e.type === "diagnosis").length },
  ];

  // Filter events
  const filteredEvents = events
    .filter(event => {
      if (activeFilter && activeFilter !== "all" && event.type !== activeFilter) return false;
      if (searchQuery && !event.title.toLowerCase().includes(searchQuery.toLowerCase()) &&
          !event.description.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      return true;
    })
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  };

  return (
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <div className="bg-slate-900/50 backdrop-blur-xl border-b border-slate-700/50 p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Calendar className="h-5 w-5 text-blue-400" />
            <h2 className="text-lg font-semibold text-white">Medical Timeline</h2>
          </div>
          <div className="text-sm text-slate-400">
            {filteredEvents.length} {filteredEvents.length === 1 ? "event" : "events"}
          </div>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search events, medications, symptoms..."
            className="pl-10 bg-slate-800/50 border-slate-600/50 text-white placeholder-slate-400 focus:border-blue-400/50 focus:ring-1 focus:ring-blue-400/20"
          />
        </div>

        {/* Filters */}
        <div className="flex gap-2 mt-3 overflow-x-auto">
          {filters.map((filter) => (
            <Button
              key={filter.type}
              variant="ghost"
              size="sm"
              onClick={() => setActiveFilter(filter.type === "all" ? null : filter.type)}
              className={`
                flex-shrink-0 text-xs
                ${(activeFilter === filter.type || (!activeFilter && filter.type === "all"))
                  ? "bg-blue-500/20 text-blue-300 border border-blue-400/50"
                  : "text-slate-400 hover:text-white hover:bg-slate-800/50"
                }
              `}
            >
              {filter.label} ({filter.count})
            </Button>
          ))}
        </div>
      </div>

      {/* Timeline Content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-3xl">
          {filteredEvents.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-slate-400">No events found</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredEvents.map((event, index) => {
                const Icon = event.icon;
                const isSelected = selectedEvent === event.id;

                return (
                  <div key={event.id} className="flex gap-3">
                    {/* Timeline Line */}
                    <div className="flex flex-col items-center flex-shrink-0">
                      <div className={`
                        p-2.5 rounded-full border-2 backdrop-blur-sm transition-all
                        ${isSelected
                          ? "bg-blue-500/20 border-blue-400 shadow-lg shadow-blue-500/20"
                          : "bg-slate-800/50 border-slate-600/50"
                        }
                      `}>
                        <Icon className={`h-5 w-5 transition-colors ${isSelected ? "text-blue-300" : "text-slate-400"}`} />
                      </div>
                      {index < filteredEvents.length - 1 && (
                        <div className="w-px flex-1 bg-gradient-to-b from-slate-600/50 to-slate-700/30 my-2 min-h-[20px]" />
                      )}
                    </div>

                    {/* Event Card */}
                    <div
                      onClick={() => onEventSelect(event.id)}
                      className={`
                        flex-1 p-4 rounded-xl border cursor-pointer
                        transition-all duration-200 backdrop-blur-sm
                        ${isSelected
                          ? "bg-blue-500/20 border-blue-400/60 shadow-xl shadow-blue-500/10"
                          : colorMap[event.color]
                        }
                      `}
                    >
                      <div className="flex flex-col gap-2">
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1 flex-wrap">
                              <h3 className="font-semibold text-white text-base">{event.title}</h3>
                              <span className={`
                                text-xs px-2.5 py-0.5 rounded-full font-medium flex-shrink-0
                                ${event.type === "medication" ? "bg-blue-500/20 text-blue-300" : ""}
                                ${event.type === "appointment" ? "bg-emerald-500/20 text-emerald-300" : ""}
                                ${event.type === "lab" ? "bg-purple-500/20 text-purple-300" : ""}
                                ${event.type === "diagnosis" ? "bg-rose-500/20 text-rose-300" : ""}
                                ${event.type === "voice" ? "bg-amber-500/20 text-amber-300" : ""}
                              `}>
                                {event.type}
                              </span>
                            </div>
                            <p className="text-sm text-slate-300 leading-relaxed">{event.description}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 text-xs text-slate-400">
                          <Calendar className="h-3 w-3" />
                          <span>{formatDate(event.date)}</span>
                          {event.endDate && (
                            <>
                              <span>→</span>
                              <span>{formatDate(event.endDate)}</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
