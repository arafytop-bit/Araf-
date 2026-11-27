import React from 'react';
import {Composition} from 'remotion';
import {Calibration} from './Calibration';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Calibration" component={Calibration} durationInFrames={150} fps={30} width={854} height={480} />
    <Composition id="CalibrationHD" component={Calibration} durationInFrames={150} fps={30} width={1920} height={1080} />
  </>
);
