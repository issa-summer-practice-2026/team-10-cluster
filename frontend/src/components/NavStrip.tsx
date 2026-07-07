// Purely decorative navigation guidance widget. No routing, no backend, no
// geolocation: it just mimics the turn-by-turn card a real cluster shows, to
// round out the centre display. Static content by design.
import { memo } from "react";

export const NavStrip = memo(function NavStrip() {
  return (
    <div className="nav" aria-hidden="true">
      <div className="nav-maneuver">
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path
            d="M9 20V11a4 4 0 0 1 4-4h5"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <polygon points="15,3 22,7 15,11" fill="currentColor" />
        </svg>
      </div>
      <div className="nav-body">
        <div className="nav-dist">300 m</div>
        <div className="nav-street">Rautenweg</div>
      </div>
      <div className="nav-eta">
        <div className="nav-eta-time">14:32</div>
        <div className="nav-eta-sub">8 min &middot; 6.2 km</div>
      </div>
    </div>
  );
});
