import {continueRender, delayRender, staticFile} from 'remotion';

const FONTS: [string, string, string, string][] = [
  ['Alegreya', 'alegreya-latin-800-normal.ttf', '800', 'normal'],
  ['Alegreya', 'alegreya-latin-700-italic.ttf', '700', 'italic'],
  ['Alegreya Sans', 'alegreya-sans-latin-800-normal.ttf', '800', 'normal'],
  ['Alegreya Sans', 'alegreya-sans-latin-500-normal.ttf', '500', 'normal'],
  ['Grenze Gotisch', 'grenze-gotisch-latin-800-normal.ttf', '800', 'normal'],
  ['Source Serif 4', 'source-serif-4-latin-900-normal.ttf', '900', 'normal'],
  ['Patua One', 'patua-one-latin-400-normal.ttf', '400', 'normal'],
  ['Arvo', 'arvo-latin-700-italic.ttf', '700', 'italic'],
];

let started = false;
export const loadFonts = () => {
  if (started) return;
  started = true;
  const handle = delayRender('fonts');
  Promise.all(
    FONTS.map(([family, file, weight, style]) => {
      const ff = new FontFace(family, `url(${staticFile('fonts/' + file)})`, {weight, style});
      return ff.load().then((f) => (document as any).fonts.add(f));
    }),
  )
    .then(() => continueRender(handle))
    .catch((e) => {
      console.error(e);
      continueRender(handle);
    });
};
