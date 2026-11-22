import React from "react";
import { Composition } from "remotion";
import { Dbg } from "./videos/dbg/Dbg";
import { MincemeatShort, MINCEMEAT_FRAMES } from "./videos/mincemeat/Mincemeat";
import { BridgeShort, BRIDGE_FRAMES } from "./videos/bridge/Bridge";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="BridgeShort" component={BridgeShort} durationInFrames={BRIDGE_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="MincemeatShort" component={MincemeatShort} durationInFrames={MINCEMEAT_FRAMES} fps={30} width={1080} height={1920} />
    <Composition id="Dbg" component={Dbg} durationInFrames={30} fps={30} width={1080} height={1920} />
  </>
);
