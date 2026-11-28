"""Assemble analysis/blueprint.json from the measured data.

Units: positions/sizes are given in reference pixels of the 854x480 source AND as % of frame
(x: % of width, y/size: % of height). Renderers should use the % values (resolution independent).
Frame N = N/30 s. Easing: CSS cubic-bezier [x1,y1,x2,y2] unless 'spring' or 'keyframes' is given.
"""
import json, numpy as np, pandas as pd
D = 'analysis/data/'
J = lambda p: json.load(open(D + p))
shots = J('shots.json'); cuts = J('cuts.json'); words = J('words.json'); sents = J('sentences.json')
stats = J('sync_stats.json'); voice = J('voice_stats.json'); music = J('music.json'); audio = J('audio_summary.json')
ev = J('visual_events.json'); ec = J('element_curves.json'); eas = J('easing_fits_calibration.json')
cct = J('chapter_card_timing.json'); colours = J('sampled_colours.json'); fm = json.load(open('analysis/fonts/font_metrics.json'))
sfx = pd.read_csv(D + 'sfx_candidates.csv')
W, H = 854, 480
pct = lambda x, y: [round(x/W*100, 2), round(y/H*100, 2)]
hpct = lambda v: round(v/H*100, 3)

bp = {}
bp['schema_version'] = '1.0'
bp['source'] = dict(file='What If You Were Born as Arthur Morgan | Red Dead Redemption 2 (480p download)', width=854, height=480, aspect='16:9 (854x480, SAR 1:1)',
                    fps=30, cfr=True, frames=16731, duration_s=557.7, video_codec='H.264 Main, yuv420p, BT.709 tv range, ~269 kbps',
                    audio='AAC-LC 44.1 kHz stereo ~128 kbps, start pts 0 (aligned with video)',
                    loudness=dict(integrated_lufs=-14.0, lra_lu=4.7, true_peak_dbtp=-1.3),
                    not_part_of_video='none detected: no platform watermark, no screen-recording UI; the end-screen disclaimer is part of the video',
                    resolution_caveat='480p re-encode of a 1080p+ master: fine detail (grain, 1-px strokes) is not recoverable; sizes are scaled from 854 px width')
bp['clock'] = dict(fps=30, frame_N_time='N/30 s', audio_feature_hop_samples=1470, audio_sr=44100, start_offsets='video pts 0, audio pts 0: frame N <-> audio [N*1470, (N+1)*1470)')
bp['canvas'] = dict(aspect='16:9', ref_px=[854, 480], recommended_render_px=[1920, 1080], safe_area_note='16:9 long-form: no platform UI overlay inside the frame during playback; keep text >= 3% from edges (observed min margin 2.6% for the HONOR HUD)',
                    coordinate_system='x right, y down, origin top-left; camera centre c = (427,240) ref px; world->screen: p_s = s*(p_w - c) + c + t')

# ---------------- style tokens ----------------
bp['style_tokens'] = {
 'fonts': {
  'display_serif': dict(family='Alegreya', weight=800, use='hero title (ARTHUR MORGAN), poster names', confidence='high (joint IoU 0.81, rank 1 of 1309 font files)', metrics=fm['alegreya-800']),
  'serif_italic': dict(family='Alegreya', weight=700, style='italic', use="storybook captions 'you, age 0', '(that's you)' (400-700 italic)", confidence='high (book caption rank 1)', metrics=fm['alegreya-700-italic']),
  'ui_sans': dict(family='Alegreya Sans', weight=800, use='name tags, speech bubbles, labels, counters, comment panel', confidence='high for bubbles (IoU 0.83-0.85), medium for tags/labels (rank 1 but low IoU because of tilt/outline)', metrics=fm['alegreya-sans-800']),
  'ui_sans_sub': dict(family='Alegreya Sans', weight=500, use='tag sub-lines (lowercase, e.g. "smooth talker")', confidence='medium', metrics=fm['alegreya-sans-500']),
  'chapter_title': dict(family='Grenze Gotisch', weight=800, use='chapter card titles (Blackwater, The Debt ...)', confidence='high (IoU 0.82, top 4 all Grenze Gotisch)', metrics=fm['grenze-gotisch-800']),
  'chapter_number': dict(family='Patua One', weight=400, letter_spacing_em=0.40, use='CHAPTER I.. IX small caps line', confidence='medium (IoU 0.79); alt Alegreya SC 700', metrics=fm['patua-one-400']),
  'poster_slab': dict(family='Source Serif 4', weight=900, use='wanted-poster WANTED / name / list items', confidence='medium (top-3 for both poster crops); alt Kameron 700, Literata 800', metrics=fm['source-serif-4-900']),
  'notebook_italic': dict(family='Arvo', weight=700, style='italic', use="THINGS TO REMEMBER journal lines", confidence='medium-low (IoU 0.65); alt Zilla Slab 700 italic', metrics=fm['arvo-700-italic']),
  'handwriting': dict(family='(unmatched) casual marker hand', use='map labels BLACKWATER, letter "Dear Arthur", "Dutch" note', confidence='not matched; closest free: Caveat 600 / Kalam 700', metrics=None),
  'all_free': 'every chosen family is a free Google Font (available as @fontsource packages)'},
 'colors': dict(colours, poster_red='#a62e1e', icon_red='#a62e1e', chapter_gold='#cfa65a', emblem_gold='#b8913f',
                vignette='#000000', black_card='#000000', note='sampled from 480p frames (median of masked pixels); thin inks are antialiased, accents corrected by eye on full-res frames'),
 'strokes': dict(title_outline=dict(color='#3f1f0e', width_pct_h=0.31, note='~1.5 px at 480p'), label_outline=dict(color='#140800', width_pct_h=0.5, note='outlined tagless labels (YEARS LATER, SMALL-TIME CROOK): dark 2-3 px stroke + soft shadow'),
                 tag_border='none (solid white card)', stamp_border=dict(color='stamp_red', double_rounded_rect=True, width_pct_h=0.6, gap_pct_h=0.6, corner_radius_pct_h=1.2, texture='grunge/eroded mask ~30% coverage')),
 'shadows': dict(title=dict(dx_pct_h=0.3, dy_pct_h=0.6, blur_pct_h=0.8, color='#000000', opacity=0.55),
                 tag=dict(dx_pct_h=0.0, dy_pct_h=0.6, blur_pct_h=1.0, color='#000000', opacity=0.35),
                 bubble=dict(dx_pct_h=0.0, dy_pct_h=0.6, blur_pct_h=1.2, color='#000000', opacity=0.30),
                 label=dict(dx_pct_h=0.3, dy_pct_h=0.5, blur_pct_h=0.6, color='#000000', opacity=0.6)),
 'radii': dict(tag_pct_h=1.5, bubble_pct_h=4.0, polaroid=0, panel_pct_h=1.5),
 'type_scale_cap_height_pct_h': dict(hero_title=5.9, poster_name=3.6, poster_list=4.0, name_tag_main=3.4, name_tag_sub=1.5, label=3.3, bubble=3.2, chapter_title=5.5, chapter_number=2.2, stamp=5.0, corner_tag=1.6, counter_number=6.0),
 'layout': dict(title_block_left_pct_w=6.9, title_block_baselines_pct_h=[73.8, 84.0], name_tags_typical_center_pct=[[31, 13], [30, 19], [51, 14], [73, 30]], labels_typical_center_pct=[[77, 28], [79, 52], [74, 30], [22, 33]],
                stamps_typical_center_pct=[[29, 19], [30, 13], [65, 28], [78, 24], [50, 12]], corner_tag_center_pct=[83, 7], honor_hud_center_pct=[14, 5], counter_hud_center_pct=[9, 9],
                rule='overlays sit in the upper third (tags, stamps) or beside the referenced character/prop with a hand-drawn arrow; nothing in the bottom 10% except the end-screen disclaimer'),
}

# ---------------- templates ----------------
nt = ec['name_tag_DUTCH']; nt2 = ec['name_tag_HOSEA']
bp['templates'] = {
 'name_tag': dict(
   look='white rounded card (radius 1.5% H), drop shadow, main line ALL CAPS Alegreya Sans 800 near-black, optional sub-line lowercase Alegreya Sans 500 ~45% size; padding x 3% W, y 1.2% H; tilted at rest -2..-3 deg',
   size=dict(width_pct_w='auto (text); observed 25-30% W for 2-3 words', height_pct_h=8.2),
   anim_in=dict(scale=dict(spring=dict(omega0_rad_per_frame=0.61, zeta=0.54, start_offset_frames=-1.7, remotion=dict(mass=1, stiffness=335, damping=19.8)),
                           keyframes=[[0, 0.35], [1, 0.70], [2, 0.93], [3, 1.06], [4, 1.12], [5, 1.13], [6, 1.10], [7, 1.06], [8, 1.01], [9, 1.0]]),
                rotation_deg=dict(keyframes=[[0, -11.5], [9, -2.5]], easing='linear', note='+1.0 deg/frame, settles at -2..-3 deg'),
                opacity='1 from first frame (no fade)', anchor='card centre', measured_from=['f1633-1642 DUTCH VAN DER LINDE', 'f1723-1732 HOSEA MATTHEWS']),
   anim_out='none: removed by the next hard cut (observed in >90% of cases); rare 3-frame fade',
   timing_rule='first frame = spoken name onset + median 5 f (IQR -0.5..+15); appears within the first sentence that names the character',
   sfx='none (event-locked average shows no transient)'),
 'label_outlined': dict(
   look='tagless ALL CAPS Alegreya Sans 800, white (commentary) or gold #ead999 (time jumps / ratings), dark 2-3 px outline + soft shadow, often followed by a hand-drawn white arrow to the referent',
   anim_in=dict(scale='same spring as name_tag (measured 0.38,0.67,0.85,0.96,1.0 on f910-914)', rotation_deg=dict(keyframes=[[0, -12], [10, -1]], easing='linear'), anchor='text centre', measured_from=['f910-920 SMALL-TIME CROOK']),
   anim_out='hard cut', timing_rule='first frame = matched word onset + median 3.5 f (IQR 1..11)', sfx='none'),
 'arrow_draw': dict(look='white hand-drawn curved stroke 0.6% H wide, round caps, small open arrowhead; curves from label to target', anim_in=dict(draw_on_frames=10, easing='ease-out [0,0,0.58,1]', start='label first frame + 3..4 f', arrowhead='appears on the last frame of the stroke'), measured_from=['f914-924', 'f546-555', 'f1008-1018'], sfx='none'),
 'speech_bubble': dict(
   look='white rounded rectangle (radius ~4% H) with long thin triangular tail pointing at the speaker; sentence-case Alegreya Sans 800 near-black, centred, 2-3 lines, max ~14 chars/line',
   anim_in=dict(scale=dict(spring=dict(omega0_rad_per_frame=0.72, zeta=0.57, start_offset_frames=-1.9, remotion=dict(mass=1, stiffness=466, damping=24.6)),
                           keyframes=[[0, 0.53], [1, 0.87], [2, 1.03], [3, 1.10], [4, 1.10], [5, 1.08], [6, 1.03], [7, 1.0]]),
                rotation_deg=dict(keyframes=[[0, -8.3], [7, 0]], easing='linear'), anchor='tail tip', measured_from=['f1115-1122', 'f1857-1864']),
   anim_out='hard cut', timing_rule='first frame = onset of the narration that paraphrases the quote + median 1 f (IQR -1.5..+15.5); bubble text is the character line, narration paraphrases it', sfx='none'),
 'stamp': dict(
   look='red #cb231e ALL CAPS slab/sans word inside a double rounded rectangle, eroded grunge texture, rotated -6..-8 deg',
   anim_in=dict(keyframes=dict(frames=[0, 1, 2, 3, 4], scale=[1.8, 1.5, 1.12, 1.0, 1.0], opacity=[0.25, 0.45, 1.0, 1.0, 1.0]),
                note='2 faint oversized ghost frames, 1 full-opacity overshoot frame, settle; slam is accelerating (ease-in) into the surface', measured_from=['f219-223 MOST WANTED', 'f1479-1483 TROUBLE', 'f4893-4898 MASSACRE']),
   anim_out='hard cut', timing_rule='slam frame (full opacity) = keyword onset + median 5 f (IQR 2..8.5)',
   sfx='stamp_thump: onset on ghost frame +1..+2 (event-locked drums 2-8 kHz +11 dB at +2 f)'),
 'list_item_stamped_icon': dict(
   look='Source Serif 4 900 caps item text + red circular outline icon (diameter 6.8% H at camera 1.0) with pictogram, dotted rule under the row',
   anim_in=dict(text_opacity_keyframes=[[0, 0.2], [1, 0.78], [2, 1.0]], icon_start_offset=1,
                icon_keyframes=dict(frames=[0, 1, 2, 3], scale=[1.75, 1.62, 1.23, 1.0], opacity=[0.35, 1.0, 1.0, 1.0])),
   follow_up='counter suffix (+"?") appears instantly 2 f after the icon settles (icon frame 0 + 5)',
   timing_rule='item text first frame = item word onset + (-1..+5) f (measured 0, +5, -1)',
   measured_from=['f86-90 TRAINS', 'f116-120 BANKS', 'f132-136 HALF THE WEST'], sfx='stamp_thump at icon frame 0 (+0/+1)'),
 'hero_title': dict(
   look='two lines ALL CAPS Alegreya 800, fill #e7d5bc, outline #3f1f0e ~0.31% H, drop shadow, left-aligned block at 6.9% W; thin rule (0.2% H, #c9a27a) with centred diamond; italic sub-line Alegreya 700i "(that\'s you)" ~40% size',
   anim_in=dict(line_stagger_frames=3, line_opacity_frames=8, tracking=dict(extra_px_per_gap_ref_start=4.8, duration_frames=10, easing=[0.0, 0.0, 0.2, 1.0]),
                rule=dict(start_offset=3, draw_from_centre_keyframes=[[0, 0.014], [1, 0.52], [2, 0.66], [3, 0.76], [4, 0.85], [5, 0.91], [6, 0.96], [7, 0.98], [8, 0.99], [9, 1.0]]),
                subline=dict(start_offset=8, fade_frames=6)), measured_from=['f37-51 ARTHUR / MORGAN / (that\'s you)'],
   timing_rule='line 1 first frame = 2 f before the name is spoken', sfx='none distinct (music swell only)'),
 'chapter_card': dict(
   look='full black; gold emblem (revolver cylinder, diameter 8.8% H) at y 38%; CHAPTER + roman numeral Patua One gold #cfa65a letter-spacing 0.4em cap 2.2% H at y 48%; title Grenze Gotisch 800 cream #efe5d4 cap 5.5% H at y 60%',
   timing=dict(scene_fade_out_frames=9.5, black_before_card_frames=9, card_visible_frames=36, card_fade_in_frames=8, card_fade_out_frames=9, black_after_frames=6, scene_fade_in_frames=11.5, total_frames=72,
               measured=[dict(c) for c in cct]),
   placement='at section boundaries; chapter number increments I..IX; title = 1-3 word noun phrase',
   timing_rule='scene fade-out starts in the pause after the last sentence of the section; next narration starts ~3-10 f after the scene fade-in begins',
   sfx='low boom/whoosh + music cue change starting ~+2 f after the card appears (event-locked other 2-8 kHz +20 dB)'),
 'storybook': dict(look='leather book on dark desk with candle; left page: "Born in Lore" running head, chapter label (Prologue), title Alegreya 800, rule; right page: "The Life of <Name>" head, framed illustration, caption "you, age 0" Alegreya 700i + red underline', uses=['open (f420-534, zoom-out from scene into the book, page flips 432-462, zoom-through into the picture 528-533)', 'end screen (f16439-16714)']),
 'things_to_remember': dict(look='notebook page in leather frame with red pin and bookmark ribbon; heading THINGS TO REMEMBER Arvo 700i; numbered caps lines; red hand-drawn ellipses/strikes; pencil sketch of the mentor', anim='lines type on ~1 char/frame (f2391-2421: 23 chars in 30 f), red ellipse draws in ~8 f, strike-through draws in ~6 f, red correction words type ~1 char/frame',
                           recurrence='f2305, 3155, 6000, 9519, 11850, 13894, 16323 - a running callback device'),
 'tally_sign': dict(look="wooden sign DUTCH'S PLANS / PLANS THAT WORKED with chalk tally strokes", anim='each tally stroke draws in 4-6 f', recurrence='f5970, 7496, 8371, 9598'),
 'counter': dict(look='Alegreya Sans 800 number (gold/white) with small caption label (COUGHS TODAY, LEFT BEHIND, $)', anim='pops like name_tag; value ticks slow then accelerates to 1 step/frame (e.g. 41->44 over 30 f, then 44->109 in 13 f); $ counter 730->5000 over 24 f', sfx='tick / cha-ching near the first frame'),
 'polaroid': dict(look='white-border instant photo, slight tilt, sepia or full colour, caption word', anim='flash/develop (white 3 f then sepia) or drop in; sets of 3 cards at 19-30 f intervals', sfx='camera shutter-like transient +5..+9 f'),
 'corner_tag': dict(look='small translucent dark tag top-right (83% W, 7% H): "RED DEAD REDEMPTION 2 · 1899", "EPILOGUE · 1907"', anim='fade in 6 f, persists across cuts, fade out 5-6 f'),
 'honor_hud': dict(look='game-style HONOR meter top-left (14%,5%), red->gold gradient bar with marker', anim='pop/slide in 3-4 f, marker moves with the story, fade out 3-4 f'),
 'subscribe_scroll': dict(look='rolled parchment banner top-right: "Born in Lore / subscribe for the next life" + red SUBSCRIBE button pressed by a stamp handle -> SUBSCRIBED + bell', frames=[3231, 3396], anim='unrolls downward 7 f, stamp press at f3277-3282, rolls up 10 f'),
 'comment_panel': dict(look='dark YouTube-style comment card centred top (50%,20%), "Which character should be born next?" + rows of names with like counts', frames=[6631, 6934], anim='dissolve in 8 f, rows fade in one by one every ~9 f, dissolve out 11 f'),
 'end_screen': dict(look='open storybook: left "Would you still follow Dutch?" + "Which character should be born next? Tell me in the comments."; right "the next life" + empty dashed box (end-screen video slot) + red wax-seal subscribe "B"; disclaimer line bottom', frames=[16439, 16730], anim='cross-dissolve in 5 f, static with candle flicker, fade to black last 14 f'),
 'pose_swap': dict(look='limited animation: character art swaps pose between drawings on a held background (no tween), occasionally through a 3-5 f white haze', examples=[14100, 14116, 14131, 11687]),
 'flash_white': dict(look='camera/gun/impact flash: 2-3 frames of near-white (luma ~235) hiding a cut or pose change', examples=[[960, 962], [12819, 12824], [14041, 14043], [2637, 2646]]),
}

# ---------------- camera grammar ----------------
sh = pd.DataFrame(shots)
mov = sh[sh.cam_kind != 'static']
bp['camera'] = dict(
  model='2.5D layered camera: background layer + character/prop layers scaled independently (parallax); overlays (tags, stamps, bubbles) are screen-space but drift with the layer they annotate',
  stats=dict(share_shots_static=round(float((sh.cam_kind == 'static').mean()), 3), share_push_in=round(float(sh.cam_kind.str.contains('push_in').mean()), 3), share_pull_out=round(float(sh.cam_kind.str.contains('pull_out').mean()), 3),
             zoom_pct_per_s_median_moving=round(float(mov.cam_zoom_pct_per_s.abs().median()), 2), zoom_pct_per_s_p90=round(float(sh.cam_zoom_pct_per_s.abs().quantile(0.9)), 2)),
  idle_move='slow push-in: median |zoom| 1-2 %/s over the whole shot (foreground layers move 5-10x more than the sky/background)',
  punch_moves=dict(fast_push_in=dict(frames=7, scale_ratio=1.42, easing=eas['s1_pushin_scale']['cubic_bezier'], note='to reveal a detail the narration names (TRAINS list)'),
                   cut_in_settle=dict(frames=4, scale_from=1.22, scale_to=1.0, easing=eas['s1_settle_scale']['cubic_bezier'], note='new shot starts 22% too close and settles - impact entrance'),
                   nudge=dict(frames=4, translate_pct_h=4.4, easing='ease-out', note='small re-frame 3-4 f before each new list item'),
                   pull_out_reveal=dict(frames=21, scale_ratio=0.353, easing_logscale=eas['s1_pullout_logscale']['cubic_bezier'], note='reveal of a larger context (wall of posters)')),
  layer_parallax_example=dict(shot=0, background_scale=[1.0, 1.008], character_scale=[1.0, 1.105], character_anchor_px=[569, 181], character_anchor_pct=pct(569, 181),
                              phases=[dict(frames=[0, 33], scale=[1.0, 1.052], easing=eas['s0_arthur_scale_a']['cubic_bezier']), dict(frames=[35, 46], scale=[1.053, 1.103], easing=eas['s0_arthur_scale_b']['cubic_bezier'], note='second push synced to the title reveal')]),
  shake='none measured (no handheld shake); micro-jitter <=2 px at 480p on some holds (likely encoding)', motion_blur='none on camera moves; speed-lines drawn for fast action', rotation='none (<0.1 deg)')

# ---------------- transitions ----------------
bp['transitions'] = dict(hard_cut_share=round(cuts['n_hard_cuts']/(cuts['n_hard_cuts']+len(cuts['transitions'])), 3), n_hard_cuts=cuts['n_hard_cuts'], soft=cuts['transitions'],
                         rule='hard cuts everywhere; soft transitions only at chapter cards (fade through black, 72 f), the storybook zooms, flashes that hide a cut, and the end-screen dissolve')

# ---------------- structure ----------------
chap = [('Cold open / hook', 0, 419), ('Storybook open + Prologue: The Wildest Kid', 420, 4422), ('I Blackwater', 4423, 6046), ('II The Debt', 6047, 7434), ('III One Last Job', 7435, 9004),
        ('IV Guarma', 9005, 9622), ('V The Cough', 9623, 10298), ('VI A Good Man', 10299, 11298), ('VII The Rat', 11299, 13063), ('VIII Go, John', 13064, 15157), ('IX The Hat (epilogue)', 15158, 16438), ('End screen / CTA loop', 16439, 16730)]
bp['structure'] = [dict(section=n, start_f=a, end_f=b, seconds=round((b-a+1)/30, 1)) for n, a, b in chap]

# ---------------- tracks ----------------
bp['shots'] = [{k: s[k] for k in ['shot', 'start', 'end', 'frames', 'cam_kind', 'cam_scale_total', 'cam_tx_total_px', 'cam_ty_total_px', 'y_mean', 'sat_mean', 'palette', 'content']} for s in shots]
bp['text_track'] = [dict(f0=e['f0'], f1=e['f1'], cls=e['cls'], type=e['type'], text=e['text'], where=e['where'], anim=e['anim'][:160], word=e.get('words'), word_onset_f=e.get('word_onset_f'), offset_f=e.get('offset_f'))
                    for e in ev if e['type'] in ('text', 'ui')]
bp['captions'] = dict(present=False, note='no burned-in narration captions; on-screen text is diegetic/labels only (see text_track)')
bp['words'] = dict(file='analysis/data/words.json', n=len(words), timing='MMS forced alignment (primary), Whisper (secondary); 434 words differ >2 f between methods -> treat onsets as +-2 f')

def sfx_cat(r):
    return r.category_guess
bp['sfx_cues'] = [dict(frame=int(r.frame), onset_s=float(r.onset_s), stem=r.stem, category_guess=r.category_guess, peak_dbfs=float(r.peak_dbfs), attack_ms=float(r.attack_ms),
                       decay20_ms=float(r.decay20_ms), dur_ms=float(r.dur_ms), centroid_hz=float(r.centroid_peak_hz), centroid_start_end_hz=[float(r.centroid_start_hz), float(r.centroid_end_hz)],
                       bands=dict(sub=float(r.sub_lt60), low=float(r.low_60_250), mid=float(r.mid_250_2k), high=float(r.high_2k_8k), air=float(r.air_gt8k)), flatness=float(r.flatness),
                       pan_R_minus_L_db=float(r.pan_R_minus_L_db), width=float(r.side_mid)) for _, r in sfx.iterrows()]
bp['music_cues'] = music['segments']
bp['mix'] = dict(voice_lufs=audio['stems']['vocals']['integrated_lufs'], music_sfx_bed_lufs=audio['stems']['music']['integrated_lufs'], voice_to_bed_lu=round(audio['stems']['vocals']['integrated_lufs'] - audio['stems']['music']['integrated_lufs'], 1),
                 master=dict(integrated_lufs=-14.0, true_peak_dbtp=-1.3, lra_lu=4.7, limiter='brickwall ~-1 dBTP (inferred from flat peak ceiling)'),
                 ducking=dict(depth_db=3.0, attack_ms=60, release_ms=150, confidence='medium (event-locked, n=97)'),
                 stereo=dict(voice='mono centre (side/mid 0.016)', bed='wide (side/mid 0.46, L/R corr 0.65)', master_lr_corr=0.98),
                 silences='music drops out for dramatic beats: 10.6-11.4 s ("Not a bullet, a cough"), 198.6-202.8 s, 300.4-302 s, 396.6-404 s, 411-435 s (sparse), 471-487 s; voice-free music swell 14600-15150 f (death scene)')
bp['voice'] = dict(stats={k: v for k, v in voice.items() if k != 'words_per_minute_by_minute'}, inferred_source='AI TTS or heavily edited human VO (no breaths in 177 sentence gaps, very even level) - confidence 0.6',
                   timbre='male, baseline f0 ~115-135 Hz with emphasis peaks to ~200-235 Hz, warm low-mids, presence bump 4-6 kHz, HPF ~100 Hz', processing='HPF ~100 Hz (steep), compression to crest 16.4 dB / active-level spread 12.4 dB, light de-essing (5-9 kHz 11.8 dB under 1-3 kHz), slight room/reverb (tail -10 dB per 100 ms)')

# ---------------- transfer rules ----------------
bp['transfer_rules'] = [
 dict(id='R1', rule='One shot per sentence', spec='Start a new shot for every sentence that introduces a new subject/beat; 62% of shots contain exactly one sentence start, 29% none (continuation), 9% two. Target median shot 66 f (2.2 s), IQR 50-87 f, never <12 f.'),
 dict(id='R2', rule='Cut pre-laps the sentence', spec='Place the cut 3 f before the first word onset of the sentence (histogram mode -3; 95% of cuts fall 0-6 f before the next word); cuts land in the inter-sentence pause (median pause 17 f), only 17% inside a word.'),
 dict(id='R3', rule='Cut rate', spec='~21.6 hard cuts/min; long holds (up to 13.7 s) only for emotional beats with no narration.'),
 dict(id='R4', rule='Text on the keyword', spec='Every proper noun, number, time jump or punchline word gets an on-screen element; first frame = word onset + 0..5 f (median +4; tags +5, labels +3.5, stamps +5, bubbles +1, list items 0).'),
 dict(id='R5', rule='Element vocabulary by meaning', spec='Character introduced -> name_tag (NAME + 1-3 word descriptor); time jump / rating -> gold outlined label; judgement / outcome word (TROUBLE, SAVED, MASSACRE, RAT) -> red stamp; quoted line -> speech bubble; enumerations -> list items or polaroid sets; numbers -> counter.'),
 dict(id='R6', rule='Pop physics', spec='Tags/labels/bubbles: underdamped spring (omega0 0.61-0.72 rad/f, zeta 0.54-0.57) from ~0.35-0.5 scale, 13-15% overshoot at +4..+5 f, settled at +7..+9 f; rotation linear from -8..-12 deg to -2..0 deg. Stamps: 2 ghost frames at 1.5-1.8x, slam at +2, settled +3.'),
 dict(id='R7', rule='Arrows follow labels', spec='When the label is not adjacent to its referent, a white arrow draws on 3-4 f after the label appears, 10 f long.'),
 dict(id='R8', rule='Silent pops, loud impacts', spec='No SFX on tags/labels/bubbles/arrows; SFX only on stamps (thump at slam), stamped icons, counters (ticks), polaroids (shutter), chapter cards (boom + new music cue), flashes and diegetic action.'),
 dict(id='R9', rule='Music is a bed, not a metronome', spec='Cuts are not beat-aligned (25% within +-2 f of a beat vs 27% chance). Music sits ~14.6 LU under the voice, ducks ~3 dB under speech, changes cue every 10-30 s at section/mood changes, and drops out for 0.5-1.5 s before a punchline.'),
 dict(id='R10', rule='Camera never still', spec='Every shot gets a slow push-in on the foreground layer (median 1-2 %/s, background 5-10x slower); when the narration enumerates or names a detail, punch in fast (7 f easeOut, x1.4) and nudge 4 f before each item.'),
 dict(id='R11', rule='Chapter rhythm', spec='Insert a chapter card at each life stage (every 30-70 s after the prologue): 72 f fade-through-black template, title = 1-3 words; next narration begins as the scene fades up.'),
 dict(id='R12', rule='Hook', spec='Frame 0 = hero portrait already moving; first word at 0.4 s; title lower-left 2 f before the name; first cut at 2.3 s; 3 enumerated deeds with stamped list; open loop question answered much later ("Not a bullet, a cough").'),
 dict(id='R13', rule='Callbacks', spec='Plant 2-3 running devices early (Remember-that-hat; THINGS TO REMEMBER list; plan tally) and revisit each 3-6 times, paying off at the end.'),
 dict(id='R14', rule='CTA placement', spec='Subscribe scroll at ~1:48 (19% in), comment prompt at ~3:41 (40% in), end screen in the last 9 s asking a question + "Which character should be born next?".'),
 dict(id='R15', rule='Pacing of narration', spec='Words: ~155 wpm, 7-word median sentences; between-sentence pause median 18 f (IQR 16-30); within-sentence pauses ~2 f.'),
 dict(id='R16', rule='Anchor mapping for new audio', spec='Anchors = word onsets/offsets, sentence starts, pauses >= 300 ms, emphasised words (top-20% loudness or pitch peak within sentence), proper nouns, numbers, section boundaries; never use absolute frames.'),
]

# ---------------- calibration edit plan (frames 0-149) ----------------
P = pd.read_csv(D + 'tracks/s1_poster_75_68_176.csv').set_index('frame')
A = pd.read_csv(D + 'tracks/s0_arthur_0_0_67.csv').set_index('frame')
def k(f, **v): return dict(f=f, **v)
cal = dict(fps=30, ref_px=[854, 480], frames=[0, 149],
  note='Edit plan for the first 150 frames, written only from measured templates/keyframes; visuals are placeholders. Camera keys map world->screen: p_s = s*(p_w-c)+c+t, c=(427,240). Each key carries the easing of the segment that ENDS at it.',
  shots=[
   dict(id='s0', start=0, end=67, world='sunset_landscape',
        layers=[dict(id='bg', placeholder='sunset_landscape', keys=[k(0, s=1.0), k(67, s=1.008, ease='linear')], anchor=[427, 240]),
                dict(id='hero', placeholder='hero_bust', box=[340, 40, 800, 480], anchor=[569, 181],
                     keys=[k(0, s=1.0), k(33, s=1.052, ease=eas['s0_arthur_scale_a']['cubic_bezier']), k(35, s=1.053, ease='linear'), k(46, s=1.103, ease=eas['s0_arthur_scale_b']['cubic_bezier']), k(67, s=1.105, ease='linear')])],
        elements=[dict(template='hero_title', start=37, lines=['ARTHUR', 'MORGAN'], subline="(that's you)", left_px=59, baselines_px=[354, 403], cap_px=28.5, rule_y_px=418, rule_x_px=[49, 265], subline_center_x_px=160, subline_baseline_px=445, subline_cap_px=9.5)]),
   dict(id='s1', start=68, end=149, world='wood_wall_poster',
        camera=[k(68, s=1.2199, tx=-1.72, ty=-11.58), k(72, s=1.0005, tx=-1.22, ty=0.61, ease=eas['s1_settle_scale']['cubic_bezier']), k(82, s=1.0, tx=-1.5, ty=1.5, ease='linear'),  # ty +4.0 on f68-82: the HQ lookdev measured the poster lines 3-4 px lower in the reference at f075 than the tracked keys put them, while f089+ already align within 1 px at f143
                k(89, s=1.4198, tx=-1.51, ty=-123.29, ease=eas['s1_pushin_scale']['cubic_bezier']), k(112, s=1.4198, tx=-2.48, ty=-123.34, ease='linear'), k(118, s=1.4198, tx=-2.15, ty=-144.6, ease=[0.25, 0.6, 0.4, 1]),
                k(127, s=1.4197, tx=-1.94, ty=-144.67, ease='linear'), k(133, s=1.4191, tx=-0.32, ty=-162.81, ease=[0.3, 0.3, 0.45, 1]), k(140, s=1.4193, tx=-1.8, ty=-161.96, ease='linear'),
                k(161, s=0.5015, tx=-0.46, ty=-3.8, ease=eas['s1_pullout_logscale']['cubic_bezier'], ease_ty=eas['s1_pullout_ty']['cubic_bezier'], ease_tx=eas['s1_pullout_ty']['cubic_bezier'], log_scale=True)],
        poster=dict(box=[278, 22, 580, 462], header='WANTED', header_y_px=[50, 90], portrait_box=[328, 98, 528, 232], name='ARTHUR MORGAN', name_cap_px=17, name_baseline_px=262,
                    subhead='WANTED FOR', subhead_y_px=277, rows_center_y_px=[312, 349.5, 386.5], icon_center_x_px=334, icon_diameter_px=32.75, item_text_left_px=361, item_cap_px=18.5,
                    reward_label_x_px=350, reward_value_x_px=443, reward_baseline_px=444, reward_cap_px=16),
        elements=[dict(template='list_item_stamped_icon', start=86, text='TRAINS', row=0, icon='train'), dict(template='list_item_stamped_icon', start=116, text='BANKS', row=1, icon='moneybag'),
                  dict(template='list_item_stamped_icon', start=132, text='HALF THE WEST', row=2, icon='map'),
                  dict(template='counter_suffix', text_sequence=[[68, '$?'], [92, '$??'], [122, '$???'], [137, '$????']]),
                  dict(template='poster_wall_reveal', start=145, stagger_frames=1, fade_frames=3, posters=[[60, 40], [800, 40], [60, 430], [800, 430], [-150, 240], [1000, 240], [430, -230], [430, 700]])])],
  sfx=[dict(f=70, recipe='paper_slap', anchor='cut 68 +2'), dict(f=87, recipe='stamp_thump', anchor='icon TRAINS first frame 87 +0'), dict(f=117, recipe='stamp_thump', anchor='icon BANKS first frame 117 +0'),
       dict(f=124, recipe='tick', anchor='reward suffix $??? at 122 +2'), dict(f=131, recipe='stamp_thump', anchor='icon HALF THE WEST first frame 133 -2'),
       dict(f=150, recipe='paper_flutter', anchor='wall reveal 145 +5'), dict(f=157, recipe='paper_flutter_b', anchor='wall reveal 145 +12')],
  sfx_recipes=dict(paper_slap=dict(noise_band_hz=[300, 8000], attack_ms=3, decay_tau_ms=35, low_thump=dict(hz=90, ms=60), peak_dbfs=-20),
                   stamp_thump=dict(sine_sweep_hz=[180, 70], sweep_ms=60, click_band_hz=[1000, 4000], click_ms=15, attack_ms=2, decay_tau_ms=40, peak_dbfs=-17),
                   tick=dict(band_hz=[3000, 6000], ms=15, peak_dbfs=-30), paper_flutter=dict(noise_band_hz=[1000, 6000], attack_ms=50, decay_tau_ms=55, am_hz=18, peak_dbfs=-30),
                   paper_flutter_b=dict(noise_band_hz=[1500, 7000], attack_ms=20, decay_tau_ms=125, am_hz=22, peak_dbfs=-24)),
  sfx_note='plan frame = reference onset frame + 1 for transient recipes (onset detectors backtrack ~1 frame); pass 1 placed the tick at 137 and the stamp at 132 -> corrected to the measured onsets 123/130',
  audio='reference audio track is used for timing (analysis only)')
bp['calibration'] = cal
bp['template_settings'] = json.load(open('analysis/template_settings.json'))
bp['calibration_hq'] = dict(composition='render/src/CalibrationHQ.tsx (CalibrationHQ 3840x2160)', plates='analysis/scripts/b03_plates.py -> render/public/hq/', poster_layout='render/src/data/poster_layout.json', pending_assets=['A02 hero bust (portrait shot)', 'A03 masked bust (poster prints)'])
json.dump(bp, open('analysis/blueprint.json', 'w'), indent=1)
print('blueprint written', round(len(json.dumps(bp))/1024), 'KB;', len(bp['text_track']), 'text events;', len(bp['sfx_cues']), 'sfx cues;', len(bp['shots']), 'shots')
