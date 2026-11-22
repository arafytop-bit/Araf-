import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { ThreeCanvas } from "@remotion/three";
export const Dbg: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#204" }}>
      <ThreeCanvas width={1080} height={1920} camera={{ fov: 40, position: [0, 0, 6] }}>
        <ambientLight intensity={1} />
        <directionalLight position={[2, 3, 4]} intensity={2} />
        <mesh rotation={[0.4, f * 0.05, 0]}><boxGeometry args={[2, 2, 2]} /><meshStandardMaterial color="orange" /></mesh>
      </ThreeCanvas>
    </AbsoluteFill>
  );
};
