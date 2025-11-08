"use client";

import { FileText, Clock, Mic, Upload, Menu, Home, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";

interface TimelineSidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function TimelineSidebar({ collapsed, onToggle }: TimelineSidebarProps) {
  const navItems = [
    { icon: Home, label: "Dashboard", active: false },
    { icon: Clock, label: "Timeline", active: true },
    { icon: FileText, label: "Documents", active: false },
    { icon: Mic, label: "Voice Notes", active: false },
    { icon: Upload, label: "Upload", active: false },
    { icon: Settings, label: "Settings", active: false },
  ];

  return (
    <div
      className={`
        bg-slate-900/50 backdrop-blur-xl border-r border-slate-700/50
        transition-all duration-300 flex flex-col
        ${collapsed ? "w-20" : "w-64"}
      `}
    >
      {/* Header */}
      <div className="p-6 border-b border-slate-700/50">
        <div className="flex items-center justify-between">
          {!collapsed && (
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              HealthFlow+
            </h1>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggle}
            className="text-slate-400 hover:text-white hover:bg-slate-800/50"
          >
            <Menu className="h-5 w-5" />
          </Button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => (
          <button
            key={item.label}
            className={`
              w-full flex items-center gap-4 px-4 py-3 rounded-lg
              transition-all duration-200
              ${item.active
                ? "bg-blue-500/20 text-blue-300 border border-blue-400/50"
                : "text-slate-400 hover:bg-slate-800/50 hover:text-white"
              }
            `}
          >
            <item.icon className="h-5 w-5 flex-shrink-0" />
            {!collapsed && (
              <span className="font-medium">{item.label}</span>
            )}
          </button>
        ))}
      </nav>

      {/* User Profile */}
      {!collapsed && (
        <div className="p-4 border-t border-slate-700/50">
          <div className="flex items-center gap-3 px-2">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-sm font-semibold">
              JD
            </div>
            <div className="flex-1">
              <div className="text-sm font-medium">John Doe</div>
              <div className="text-xs text-slate-400">john@example.com</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
