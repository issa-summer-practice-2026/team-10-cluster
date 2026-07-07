import { memo, useEffect, useState } from "react";

// Purely decorative "now playing" widget. It calls no backend and drives
// nothing on the vehicle: it only exists to make the centre display look like
// a real car's infotainment surface. The progress bar advances on a local
// timer so the panel feels alive.
const TRACK = { title: "Neon Horizon", artist: "The Midnight Drive", duration: 214 };

function fmt(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export const MediaCard = memo(function MediaCard() {
  const [elapsed, setElapsed] = useState(47);

  useEffect(() => {
    const id = window.setInterval(() => {
      setElapsed((e) => (e + 1) % TRACK.duration);
    }, 1000);
    return () => window.clearInterval(id);
  }, []);

  const pct = (elapsed / TRACK.duration) * 100;

  return (
    <div className="media" aria-hidden="true">
      <div className="media-art">
        <svg viewBox="0 0 24 24" width="22" height="22">
          <path
            d="M9 18V6l10-2v12"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <circle cx="6.5" cy="18" r="2.4" fill="currentColor" />
          <circle cx="16.5" cy="16" r="2.4" fill="currentColor" />
        </svg>
      </div>

      <div className="media-body">
        <div className="media-title">{TRACK.title}</div>
        <div className="media-artist">{TRACK.artist}</div>
        <div className="media-progress">
          <span style={{ width: `${pct}%` }} />
        </div>
        <div className="media-times">
          <span>{fmt(elapsed)}</span>
          <span>{fmt(TRACK.duration)}</span>
        </div>
      </div>

      <div className="media-controls">
        <svg viewBox="0 0 24 24" width="16" height="16">
          <polygon points="18,6 8,12 18,18" fill="currentColor" />
          <rect x="6" y="6" width="2" height="12" fill="currentColor" />
        </svg>
        <svg viewBox="0 0 24 24" width="20" height="20" className="media-play">
          <polygon points="8,5 19,12 8,19" fill="currentColor" />
        </svg>
        <svg viewBox="0 0 24 24" width="16" height="16">
          <polygon points="6,6 16,12 6,18" fill="currentColor" />
          <rect x="16" y="6" width="2" height="12" fill="currentColor" />
        </svg>
      </div>
    </div>
  );
});
