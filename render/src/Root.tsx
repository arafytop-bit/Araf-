import React from 'react';
import {Composition} from 'remotion';
import {Calibration} from './Calibration';
import {CalibrationHQ} from './CalibrationHQ';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Calibration" component={Calibration} durationInFrames={150} fps={30} width={854} height={480} />
    <Composition id="CalibrationHD" component={Calibration} durationInFrames={150} fps={30} width={1920} height={1080} />
    <Composition id="CalibrationHQ" component={CalibrationHQ} durationInFrames={150} fps={30} width={3840} height={2160} defaultProps={{heroSrc: null, posterPrintSrc: null}} />
    <Composition id="CalibrationHQ1080" component={CalibrationHQ} durationInFrames={150} fps={30} width={1920} height={1080} defaultProps={{heroSrc: null, posterPrintSrc: null}} />
  </>
);
