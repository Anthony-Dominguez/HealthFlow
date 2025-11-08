"use client";

interface MedicalEvent {
  id: string;
  type: string;
  title: string;
  date: string;
  position: number;
  duration: number;
  color: string;
}

interface MedicalEventBlockProps {
  event: MedicalEvent;
  isSelected: boolean;
  onClick: () => void;
  compact?: boolean;
}

export function MedicalEventBlock({
  event,
  isSelected,
  onClick,
  compact = false,
}: MedicalEventBlockProps) {
  const height = compact ? "h-12" : "h-16";
  const topOffset = compact ? "top-2" : "top-8";

  return (
    <div
      onClick={onClick}
      className={`
        absolute ${topOffset} ${height}
        cursor-pointer group
        transition-all duration-200
        ${isSelected ? "z-20" : "z-10"}
      `}
      style={{
        left: `${event.position}%`,
        width: `${event.duration}%`,
      }}
    >
      {/* Event Block */}
      <div
        className={`
          h-full rounded-md
          ${event.color} bg-opacity-60
          border-2
          ${
            isSelected
              ? "border-white shadow-lg shadow-blue-500/50 scale-105"
              : "border-transparent group-hover:border-white/50 group-hover:shadow-md"
          }
          flex items-center px-3
          backdrop-blur-sm
          transition-all duration-200
        `}
      >
        {/* Event Title */}
        <div className="flex-1 min-w-0">
          <div
            className={`
              font-medium text-white truncate
              ${compact ? "text-xs" : "text-sm"}
            `}
          >
            {event.title}
          </div>
          {!compact && (
            <div className="text-xs text-white/70 truncate">{event.date}</div>
          )}
        </div>

        {/* Type Badge */}
        {!compact && (
          <div className="ml-2 px-2 py-0.5 rounded-full bg-black/30 text-xs text-white/90 uppercase">
            {event.type}
          </div>
        )}
      </div>

      {/* Resize Handles (show on hover) */}
      {isSelected && (
        <>
          <div className="absolute left-0 top-0 bottom-0 w-1 bg-white/50 cursor-ew-resize rounded-l-md" />
          <div className="absolute right-0 top-0 bottom-0 w-1 bg-white/50 cursor-ew-resize rounded-r-md" />
        </>
      )}
    </div>
  );
}
