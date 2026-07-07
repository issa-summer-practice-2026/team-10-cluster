import { describe, expect, it } from "vitest";

import { START_DEG, SWEEP_DEG, arcPath, fractionToAngle, polarToCartesian } from "./gauges";

describe("fractionToAngle", () => {
  it("maps 0 to the start angle", () => {
    expect(fractionToAngle(0)).toBe(START_DEG);
  });

  it("maps 1 to the end angle", () => {
    expect(fractionToAngle(1)).toBe(START_DEG + SWEEP_DEG);
  });

  it("maps 0.5 to the midpoint", () => {
    expect(fractionToAngle(0.5)).toBe(START_DEG + SWEEP_DEG / 2);
  });

  it("clamps values below 0", () => {
    expect(fractionToAngle(-0.5)).toBe(START_DEG);
  });

  it("clamps values above 1", () => {
    expect(fractionToAngle(2)).toBe(START_DEG + SWEEP_DEG);
  });
});

describe("polarToCartesian", () => {
  it("puts angle 0 straight up (−y)", () => {
    const p = polarToCartesian(100, 100, 80, 0);
    expect(p.x).toBeCloseTo(100);
    expect(p.y).toBeCloseTo(20);
  });

  it("puts angle 90 to the right (+x)", () => {
    const p = polarToCartesian(100, 100, 80, 90);
    expect(p.x).toBeCloseTo(180);
    expect(p.y).toBeCloseTo(100);
  });

  it("puts angle −90 to the left (−x)", () => {
    const p = polarToCartesian(100, 100, 80, -90);
    expect(p.x).toBeCloseTo(20);
    expect(p.y).toBeCloseTo(100);
  });
});

describe("arcPath", () => {
  it("starts at the start fraction point and ends at the end fraction point", () => {
    const r = 80;
    const start = polarToCartesian(100, 100, r, fractionToAngle(0));
    const end = polarToCartesian(100, 100, r, fractionToAngle(1));
    const d = arcPath(100, 100, r, 0, 1);
    expect(d.startsWith(`M ${start.x} ${start.y}`)).toBe(true);
    expect(d.endsWith(`${end.x} ${end.y}`)).toBe(true);
  });

  it("uses the large-arc flag when sweeping more than 180 degrees", () => {
    // full 0..1 sweep is 240 degrees > 180
    expect(arcPath(100, 100, 80, 0, 1)).toContain(" 1 1 ");
  });

  it("uses the small-arc flag for a short sweep", () => {
    // a tiny sweep is well under 180 degrees
    expect(arcPath(100, 100, 80, 0, 0.1)).toContain(" 0 1 ");
  });
});
