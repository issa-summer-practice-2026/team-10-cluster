interface DigitalReadoutProps {
  speed: number;
  unit: string;
  gear: string;
}

export function DigitalReadout({ speed, unit, gear }: DigitalReadoutProps) {
  return (
    <div className="digital">
      <div className="digital-speed">{Math.round(speed)}</div>
      <div className="digital-unit">{unit}</div>
      <div className="digital-gear">{gear}</div>
    </div>
  );
}
