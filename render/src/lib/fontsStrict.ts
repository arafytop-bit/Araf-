// Strict font loading: every family must load AND actually change glyph metrics vs. the fallback, or the render is cancelled.
import {cancelRender, continueRender, delayRender, staticFile} from 'remotion';

export const FONT_FILES: [string, string, string, string][] = [
  ['Alegreya', 'alegreya-latin-800-normal.ttf', '800', 'normal'],
  ['Alegreya', 'alegreya-latin-700-italic.ttf', '700', 'italic'],
  ['Alegreya Sans', 'alegreya-sans-latin-800-normal.ttf', '800', 'normal'],
  ['Alegreya Sans', 'alegreya-sans-latin-500-normal.ttf', '500', 'normal'],
  ['Grenze Gotisch', 'grenze-gotisch-latin-800-normal.ttf', '800', 'normal'],
  ['Bitter', 'bitter-latin-800-normal.ttf', '800', 'normal'],
  ['Bitter', 'bitter-latin-900-normal.ttf', '900', 'normal'],
  ['Patua One', 'patua-one-latin-400-normal.ttf', '400', 'normal'],
];

let started = false;
export const loadFontsStrict = () => {
  if (started) return;
  started = true;
  const handle = delayRender('strict fonts');
  Promise.all(
    FONT_FILES.map(([family, file, weight, style]) => {
      const ff = new FontFace(family, `url(${staticFile('fonts/' + file)})`, {weight, style});
      return ff.load().then((f) => {
        (document as any).fonts.add(f);
        return [family, weight, style] as const;
      });
    }),
  )
    .then((loaded) => {
      const c = document.createElement('canvas').getContext('2d')!;
      const probe = 'WANTED Hamburgefonstiv 0123';
      for (const [family, weight, style] of loaded) {
        const spec = `${style} ${weight} 100px "${family}"`;
        if (!(document as any).fonts.check(spec, probe)) throw new Error(`FONT NOT AVAILABLE: ${spec}`);
        c.font = `${style} ${weight} 100px "${family}", monospace`;
        const wFont = c.measureText(probe).width;
        c.font = `${style} ${weight} 100px monospace`;
        const wMono = c.measureText(probe).width;
        c.font = `${style} ${weight} 100px "${family}", serif`;
        const wSerif = c.measureText(probe).width;
        // if the requested family were missing, both stacks would fall back and differ from each other
        if (Math.abs(wFont - wMono) < 0.5 || Math.abs(wFont - wSerif) > 0.5) throw new Error(`FONT FALLBACK DETECTED: ${spec} (font=${wFont}, mono=${wMono}, serif-stack=${wSerif})`);
      }
      continueRender(handle);
    })
    .catch((e) => cancelRender(e));
};
