# Audit of the last MP4 (most_epic_deaths.mp4, 17:53, 1920x1080, 30 fps)

Same tools as the style bible, run on the rendered file.

## A. Mistakes found by viewing the 4 fps contact sheets

| Time | Mistake |
|---|---|
| 0:00.0–0:02.0 | Hook frames are static: the kinetic title sits small (lines about 5–8% of height) in the top third, with a tiny frozen host bottom-left. The reference opens with characters running in. |
| 0:00.0 | The hook line is generic ("These are the most epic deaths in human history"), with no curiosity gap in the first 2 s. |
| 0:05.0–0:06.0 | "GREATEST HITS" card is on screen **empty** for 1 s. |
| 0:06.0–0:13.0 | Playlist card text about 1.5% of height (unreadable on a phone); large dead black area. |
| 0:11.75 | The green recycle icon overlaps the card's right edge. |
| 0:16.5–0:19.0 | Two monks against a flat beige wall, static for 2.5 s. |
| 0:19.75–0:21.5 | Red callout over a busy stone photo (low contrast). |
| 0:23.25 | Callout drawn on top of the host's hat. |
| 0:48.0–0:49.5 | "AGE 15" callout on the host's hat. |
| 0:50.5–0:54.75 | Harald + Olaf static for 4 s on a flat field; name tags about 1.5% of height. |
| 0:54.5 | Olaf vanishes in one frame when he dies (no animation). |
| 0:58.5–1:00 | Map of Europe shown small; "NORWAY" label about 1% of height. |
| 1:15.25–1:15.33 | Jail drawn intact and broken **at the same time** (double draw). |
| 1:16.5–1:18.5 | "CENSORED" bar floats **above** the emperor's head instead of covering his eyes. |
| 1:21.0–1:22.75 | Picture-in-picture host is cut off by the bottom edge (only the head visible). |
| 1:23.0 | "One ship snaps in half" reads as two ships overlapping; illegible. |
| 3:30.25–3:34.75 | Harald static for 4.5 s; the "arrow hits him in the windpipe" arrow **flies past above his head**. |
| 4:40.75–4:42.5 | Two Romans against a flat beige wall, static. |
| 4:43.5–4:45.0 | Priscus alone on black, static, with a tiny name tag. |
| 4:46.5–4:47.25 | "449 AD" on the host's hat, then red on a brown painting (low contrast). |
| 8:29.25–8:33.0 | "Parthian shot" dictionary card nearly empty for 3 s; then a **missing-glyph box (▯)** before "parting shot". |
| HUD, throughout entries | Top-left skull tracker clutters every host shot; its "DEATH n OF 5" label is about 1.5% of height (unreadable). |
| 17:44.0–17:53.7 | Frozen end screen for about 10 s with an empty white box; no loop back to the opening. |
| Throughout | Host only ever swaps expressions: no walk/run cycles, no secondary motion, no flipbook loops. |

## B. Automated detections (whole file, 191 items)

| # | Time | Problem | Detail |
|---|---|---|---|
| 1 | 0:05.00 | Card on screen with no content yet | 'HISTORY YOUTUBE: GREATEST HITS' card shows empty for 1.00s |
| 2 | 0:05.00 | Card text under 3% of frame height (unreadable on phone) | playlist card body text under 3% of frame height (unreadable on phones) |
| 3 | 0:16.40 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'people who wrote them down' on a flat 'hall' backdrop for 2.8s |
| 4 | 0:23.17 | Callout collides with the host’s hat | callout 'WINS A BATTLE... THE SAME WAY' overlaps the zoomed host's hat |
| 5 | 0:24.60 | Element pops in within one frame (no easing) | element appears in one frame (diff 6.4) with no ease |
| 6 | 0:31.27 | Card text under 3% of frame height (unreadable on phone) | bio card body text under 3% of frame height (unreadable on phones) |
| 7 | 0:34.40 | Element pops in within one frame (no easing) | element appears in one frame (diff 3.9) with no ease |
| 8 | 0:50.43 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'his half-brother Olaf' on a flat 'field' backdrop for 3.3s |
| 9 | 1:15.30 | 2-frame flash / double-draw | 2-frame flash/jump in and out |
| 10 | 1:15.33 | 2-frame flash / double-draw | 2-frame flash/jump in and out |
| 11 | 1:30.07 | Callout collides with the host’s hat | callout '1066' overlaps the zoomed host's hat |
| 12 | 1:33.67 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'three different men' on a flat 'hall' backdrop for 10.7s |
| 13 | 1:46.70 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'smashes the first English' on a flat 'field' backdrop for 2.8s |
| 14 | 1:52.47 | Element pops in within one frame (no easing) | element appears in one frame (diff 22.4) with no ease |
| 15 | 1:53.93 | Element pops in within one frame (no easing) | element appears in one frame (diff 22.3) with no ease |
| 16 | 2:02.33 | Red callout on a busy photo (low contrast) | red callout '160 YEARS LATER' over a photo (busy background) |
| 17 | 2:06.23 | Element pops in within one frame (no easing) | element appears in one frame (diff 12.2) with no ease |
| 18 | 2:09.67 | Element pops in within one frame (no easing) | element appears in one frame (diff 2.8) with no ease |
| 19 | 2:18.57 | Card text under 3% of frame height (unreadable on phone) | inventory card body text under 3% of frame height (unreadable on phones) |
| 20 | 2:29.40 | Element pops in within one frame (no easing) | element appears in one frame (diff 2.7) with no ease |
| 21 | 2:33.17 | 2-frame flash / double-draw | 2-frame flash/jump in and out |
| 22 | 2:38.50 | Element pops in within one frame (no easing) | element appears in one frame (diff 24.1) with no ease |
| 23 | 2:47.80 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'his horse stumbles' on a flat 'field' backdrop for 3.4s |
| 24 | 2:56.30 | Element pops in within one frame (no easing) | element appears in one frame (diff 24.2) with no ease |
| 25 | 2:57.70 | Element pops in within one frame (no easing) | element appears in one frame (diff 24.2) with no ease |
| 26 | 3:00.20 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'asks who the big man' on a flat 'field' backdrop for 4.0s |
| 27 | 3:05.67 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'And he says, roughly' on a flat 'field' backdrop for 4.3s |
| 28 | 3:09.97 | Host-only hold over 4 s | host-only shot lasts 5.8s |
| 29 | 3:12.37 | Element pops in within one frame (no easing) | element appears in one frame (diff 3.4) with no ease |
| 30 | 3:15.77 | Element pops in within one frame (no easing) | element appears in one frame (diff 4.0) with no ease |
| 31 | 3:18.13 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'seven feet of English ground' on a flat 'black' backdrop for 3.6s |
| 32 | 3:21.70 | Element pops in within one frame (no easing) | element appears in one frame (diff 10.6) with no ease |
| 33 | 3:30.30 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'charged out ahead' on a flat 'field' backdrop for 3.1s |
| 34 | 3:35.00 | 2-frame flash / double-draw | 2-frame flash/jump in and out |
| 35 | 3:35.03 | 2-frame flash / double-draw | 2-frame flash/jump in and out |
| 36 | 3:40.43 | Red callout on a busy photo (low contrast) | red callout 'ARMOR: "OPTIONAL"' over a photo (busy background) |
| 37 | 3:42.73 | Element pops in within one frame (no easing) | element appears in one frame (diff 3.1) with no ease |
| 38 | 3:54.00 | Host-only hold over 4 s | host-only shot lasts 4.1s |
| 39 | 4:03.33 | Host-only hold over 4 s | host-only shot lasts 4.3s |
| 40 | 4:16.20 | Callout collides with the host’s hat | callout '3 DAYS LATER' overlaps the zoomed host's hat |
| 41 | 4:30.30 | Element pops in within one frame (no easing) | element appears in one frame (diff 23.5) with no ease |
| 42 | 4:45.20 | Element pops in within one frame (no easing) | element appears in one frame (diff 12.8) with no ease |
| 43 | 4:47.50 | Red callout on a busy photo (low contrast) | red callout '449 AD' over a photo (busy background) |
| 44 | 4:48.47 | Callout collides with the host’s hat | callout '449 AD' overlaps the zoomed host's hat |
| 45 | 4:59.30 | Red callout on a busy photo (low contrast) | red callout '2,100 LBS OF GOLD' over a photo (busy background) |
| 46 | 5:00.93 | Red callout on a busy photo (low contrast) | red callout 'PER. YEAR.' over a photo (busy background) |
| 47 | 5:06.23 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'his brother, Bleda' on a flat 'black' backdrop for 2.5s |
| 48 | 5:25.80 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'sword of the war god' on a flat 'black' backdrop for 3.9s |
| 49 | 5:29.70 | Element pops in within one frame (no easing) | element appears in one frame (diff 23.2) with no ease |
| 50 | 5:32.40 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'silver plates' on a flat 'hall' backdrop for 5.9s |
| 51 | 5:39.17 | Card text under 3% of frame height (unreadable on phone) | inventory card body text under 3% of frame height (unreadable on phones) |
| 52 | 5:44.43 | Element pops in within one frame (no easing) | element appears in one frame (diff 23.4) with no ease |
| 53 | 5:44.43 | Callout collides with the host’s hat | callout 'DIED OF A... NOSEBLEED' overlaps the zoomed host's hat |
| 54 | 5:58.47 | 2-frame flash / double-draw | 2-frame flash/jump in and out |
| 55 | 5:58.50 | 2-frame flash / double-draw | 2-frame flash/jump in and out |
| 56 | 6:01.67 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'broke down the door' on a flat 'hall' backdrop for 4.8s |
| 57 | 6:08.70 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'claimed she killed him' on a flat 'hall' backdrop for 8.1s |
| 58 | 6:20.20 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'cut off their hair' on a flat 'night' backdrop for 4.0s |
| 59 | 6:26.67 | Element pops in within one frame (no easing) | element appears in one frame (diff 22.2) with no ease |
| 60 | 6:28.03 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'three coffins' on a flat 'black' backdrop for 6.3s |
| 61 | 6:34.37 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'buried him at night' on a flat 'night' backdrop for 4.1s |
| 62 | 6:41.43 | Callout collides with the host’s hat | callout '1,500+ YEARS: STILL MISSING' overlaps the zoomed host's hat |
| 63 | 6:44.53 | Host-only hold over 4 s | host-only shot lasts 5.4s |
| 64 | 7:00.63 | Card on screen with no content yet | 'dict' card shows empty for 0.63s |
| 65 | 7:03.70 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'richest man in Rome' on a flat 'black' backdrop for 2.7s |
| 66 | 7:09.47 | Element pops in within one frame (no easing) | element appears in one frame (diff 11.2) with no ease |
| 67 | 7:16.87 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'house went up in flames' on a flat 'field' backdrop for 6.0s |
| 68 | 7:22.83 | Host-only hold over 4 s | host-only shot lasts 6.3s |
| 69 | 7:29.13 | Red callout on a busy photo (low contrast) | red callout 'BUYING YOUR HOUSE WHILE IT BURNS' over a photo (busy background) |
| 70 | 7:34.17 | Element pops in within one frame (no easing) | element appears in one frame (diff 27.1) with no ease |
| 71 | 7:34.17 | Host-only hold over 4 s | host-only shot lasts 4.0s |
| 72 | 7:38.20 | Element pops in within one frame (no easing) | element appears in one frame (diff 4.2) with no ease |
| 73 | 7:42.73 | Element pops in within one frame (no easing) | element appears in one frame (diff 25.4) with no ease |
| 74 | 7:44.07 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'Pompey and Julius Caesar' on a flat 'black' backdrop for 6.8s |
| 75 | 8:02.33 | Callout collides with the host’s hat | callout '53 BC' overlaps the zoomed host's hat |
| 76 | 8:08.97 | 2-frame flash / double-draw | 2-frame flash/jump in and out |
| 77 | 8:09.00 | 2-frame flash / double-draw | 2-frame flash/jump in and out |
| 78 | 8:09.03 | 2-frame flash / double-draw | 2-frame flash/jump in and out |
| 79 | 8:09.07 | 2-frame flash / double-draw | 2-frame flash/jump in and out |
| 80 | 8:14.10 | 2-frame flash / double-draw | 2-frame flash/jump in and out |
| 81 | 8:14.97 | Element pops in within one frame (no easing) | element appears in one frame (diff 6.8) with no ease |
| 82 | 8:29.20 | Card on screen with no content yet | 'dict' card shows empty for 3.00s |
| 83 | 8:37.43 | Element pops in within one frame (no easing) | element appears in one frame (diff 23.4) with no ease |
| 84 | 8:41.87 | 2-frame flash / double-draw | 2-frame flash/jump in and out |
| 85 | 8:41.90 | 2-frame flash / double-draw | 2-frame flash/jump in and out |
| 86 | 8:41.93 | 2-frame flash / double-draw | 2-frame flash/jump in and out |
| 87 | 8:41.97 | 2-frame flash / double-draw | 2-frame flash/jump in and out |
| 88 | 8:42.57 | Host-only hold over 4 s | host-only shot lasts 6.0s |
| 89 | 8:45.60 | Element pops in within one frame (no easing) | element appears in one frame (diff 2.9) with no ease |
| 90 | 8:48.23 | Element pops in within one frame (no easing) | element appears in one frame (diff 3.4) with no ease |
| 91 | 8:50.73 | Red callout on a busy photo (low contrast) | red callout '30+ YEARS TO GET THEM BACK' over a photo (busy background) |
| 92 | 8:53.10 | Host-only hold over 4 s | host-only shot lasts 5.4s |
| 93 | 9:11.53 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'snatches the head' on a flat 'black' backdrop for 4.4s |
| 94 | 9:21.23 | Element pops in within one frame (no easing) | element appears in one frame (diff 22.9) with no ease |
| 95 | 9:21.23 | Callout collides with the host’s hat | callout 'ROME'S RICHEST MAN: STAGE PROP' overlaps the zoomed host's hat |
| 96 | 9:23.63 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'fake Roman victory parade' on a flat 'field' backdrop for 7.1s |
| 97 | 9:30.77 | Host-only hold over 4 s | host-only shot lasts 5.4s |
| 98 | 9:36.07 | Element pops in within one frame (no easing) | element appears in one frame (diff 3.0) with no ease |
| 99 | 9:37.97 | Element pops in within one frame (no easing) | element appears in one frame (diff 14.8) with no ease |
| 100 | 9:37.97 | Host-only hold over 4 s | host-only shot lasts 4.3s |
| 101 | 9:45.07 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'chasing gold' on a flat 'field' backdrop for 2.8s |
| 102 | 9:55.33 | Host-only hold over 4 s | host-only shot lasts 4.1s |
| 103 | 10:05.17 | Red callout on a busy photo (low contrast) | red callout 'SINCE 648 BC' over a photo (busy background) |
| 104 | 10:16.73 | Card on screen with no content yet | 'ILLEGAL' card shows empty for 0.80s |
| 105 | 10:16.73 | Card text under 3% of frame height (unreadable on phone) | list card body text under 3% of frame height (unreadable on phones) |
| 106 | 10:20.67 | Card on screen with no content yet | 'LEGAL' card shows empty for 0.87s |
| 107 | 10:20.67 | Card text under 3% of frame height (unreadable on phone) | list card body text under 3% of frame height (unreadable on phones) |
| 108 | 10:33.67 | Card text under 3% of frame height (unreadable on phone) | list card body text under 3% of frame height (unreadable on phones) |
| 109 | 10:40.97 | Host-only hold over 4 s | host-only shot lasts 5.2s |
| 110 | 10:46.17 | Element pops in within one frame (no easing) | element appears in one frame (diff 23.9) with no ease |
| 111 | 10:51.73 | Element pops in within one frame (no easing) | element appears in one frame (diff 3.4) with no ease |
| 112 | 10:53.17 | Element pops in within one frame (no easing) | element appears in one frame (diff 22.8) with no ease |
| 113 | 10:53.17 | Callout collides with the host’s hat | callout 'AGAIN.' overlaps the zoomed host's hat |
| 114 | 10:53.37 | Callout collides with the host’s hat | callout '564 BC: GOING FOR #3' overlaps the zoomed host's hat |
| 115 | 10:59.77 | Element pops in within one frame (no easing) | element appears in one frame (diff 22.9) with no ease |
| 116 | 11:09.13 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'a man named Eryxias' on a flat 'arena' backdrop for 5.8s |
| 117 | 11:14.97 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'What a noble epitaph' on a flat 'arena' backdrop for 2.9s |
| 118 | 11:20.17 | Element pops in within one frame (no easing) | element appears in one frame (diff 10.6) with no ease |
| 119 | 11:26.23 | Element pops in within one frame (no easing) | element appears in one frame (diff 24.3) with no ease |
| 120 | 11:29.87 | Element pops in within one frame (no easing) | element appears in one frame (diff 24.9) with no ease |
| 121 | 11:32.37 | Element pops in within one frame (no easing) | element appears in one frame (diff 24.2) with no ease |
| 122 | 11:36.13 | Host-only hold over 4 s | host-only shot lasts 5.4s |
| 123 | 11:43.23 | 2-frame flash / double-draw | 2-frame flash/jump in and out |
| 124 | 11:43.30 | 2-frame flash / double-draw | 2-frame flash/jump in and out |
| 125 | 11:43.33 | 2-frame flash / double-draw | 2-frame flash/jump in and out |
| 126 | 11:53.27 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'named Pausanias' on a flat 'black' backdrop for 3.2s |
| 127 | 11:56.50 | Element pops in within one frame (no easing) | element appears in one frame (diff 20.8) with no ease |
| 128 | 12:04.27 | Host-only hold over 4 s | host-only shot lasts 5.9s |
| 129 | 12:05.70 | Element pops in within one frame (no easing) | element appears in one frame (diff 2.7) with no ease |
| 130 | 12:10.17 | Element pops in within one frame (no easing) | element appears in one frame (diff 4.5) with no ease |
| 131 | 12:17.03 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'A statue many believe' on a flat 'black' backdrop for 3.8s |
| 132 | 12:20.87 | Element pops in within one frame (no easing) | element appears in one frame (diff 13.7) with no ease |
| 133 | 12:20.87 | Host-only hold over 4 s | host-only shot lasts 5.1s |
| 134 | 12:25.93 | Element pops in within one frame (no easing) | element appears in one frame (diff 23.3) with no ease |
| 135 | 12:25.93 | Callout collides with the host’s hat | callout 'WON AN OLYMPIC FINAL AFTER DYING' overlaps the zoomed host's hat |
| 136 | 12:32.67 | Element pops in within one frame (no easing) | element appears in one frame (diff 22.5) with no ease |
| 137 | 12:33.90 | Element pops in within one frame (no easing) | element appears in one frame (diff 22.7) with no ease |
| 138 | 12:41.37 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'a Viking who was killed' on a flat 'black' backdrop for 3.3s |
| 139 | 12:48.70 | Element pops in within one frame (no easing) | element appears in one frame (diff 17.4) with no ease |
| 140 | 12:49.80 | Element pops in within one frame (no easing) | element appears in one frame (diff 23.1) with no ease |
| 141 | 12:51.93 | Element pops in within one frame (no easing) | element appears in one frame (diff 4.9) with no ease |
| 142 | 12:54.80 | Card text under 3% of frame height (unreadable on phone) | comment card body text under 3% of frame height (unreadable on phones) |
| 143 | 12:57.57 | Card text under 3% of frame height (unreadable on phone) | likes card body text under 3% of frame height (unreadable on phones) |
| 144 | 12:59.73 | Element pops in within one frame (no easing) | element appears in one frame (diff 23.6) with no ease |
| 145 | 13:00.37 | Element pops in within one frame (no easing) | element appears in one frame (diff 23.7) with no ease |
| 146 | 13:10.73 | Host-only hold over 4 s | host-only shot lasts 4.5s |
| 147 | 13:18.77 | Element pops in within one frame (no easing) | element appears in one frame (diff 8.6) with no ease |
| 148 | 13:20.73 | Callout collides with the host’s hat | callout '1592' overlaps the zoomed host's hat |
| 149 | 13:29.40 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'one Korean admiral starts' on a flat 'sea' backdrop for 2.7s |
| 150 | 13:35.90 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'covered decks studded' on a flat 'sea' backdrop for 6.0s |
| 151 | 13:57.23 | Element pops in within one frame (no easing) | element appears in one frame (diff 23.4) with no ease |
| 152 | 13:57.23 | Callout collides with the host’s hat | callout '~23 NAVAL BATTLES' overlaps the zoomed host's hat |
| 153 | 13:58.37 | Callout collides with the host’s hat | callout 'LOSSES: 0' overlaps the zoomed host's hat |
| 154 | 14:02.67 | Host-only hold over 4 s | host-only shot lasts 5.5s |
| 155 | 14:10.73 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'an enemy tip he suspected' on a flat 'black' backdrop for 3.8s |
| 156 | 14:17.47 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'demoted to a common foot soldier' on a flat 'field' backdrop for 2.8s |
| 157 | 14:22.23 | Element pops in within one frame (no easing) | element appears in one frame (diff 4.1) with no ease |
| 158 | 14:25.80 | Element pops in within one frame (no easing) | element appears in one frame (diff 3.2) with no ease |
| 159 | 14:40.73 | Element pops in within one frame (no easing) | element appears in one frame (diff 4.5) with no ease |
| 160 | 14:42.43 | Element pops in within one frame (no easing) | element appears in one frame (diff 4.3) with no ease |
| 161 | 14:47.90 | Element pops in within one frame (no easing) | element appears in one frame (diff 20.5) with no ease |
| 162 | 15:05.10 | Element pops in within one frame (no easing) | element appears in one frame (diff 24.0) with no ease |
| 163 | 15:14.80 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'Yi's flagship held off' on a flat 'sea' backdrop for 5.8s |
| 164 | 15:23.73 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'crashing into each other' on a flat 'sea' backdrop for 3.2s |
| 165 | 15:29.57 | Host-only hold over 4 s | host-only shot lasts 4.6s |
| 166 | 15:31.87 | Element pops in within one frame (no easing) | element appears in one frame (diff 2.8) with no ease |
| 167 | 15:35.37 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'In his war diary' on a flat 'black' backdrop for 5.2s |
| 168 | 15:42.13 | Callout collides with the host’s hat | callout '1598' overlaps the zoomed host's hat |
| 169 | 15:43.60 | Red callout on a busy photo (low contrast) | red callout '1598' over a photo (busy background) |
| 170 | 15:46.70 | Host-only hold over 4 s | host-only shot lasts 7.4s |
| 171 | 15:58.77 | Element pops in within one frame (no easing) | element appears in one frame (diff 23.8) with no ease |
| 172 | 15:59.23 | 2-frame flash / double-draw | 2-frame flash/jump in and out |
| 173 | 15:59.27 | 2-frame flash / double-draw | 2-frame flash/jump in and out |
| 174 | 16:00.47 | Element pops in within one frame (no easing) | element appears in one frame (diff 3.4) with no ease |
| 175 | 16:04.80 | Element pops in within one frame (no easing) | element appears in one frame (diff 22.2) with no ease |
| 176 | 16:04.80 | Host-only hold over 4 s | host-only shot lasts 4.6s |
| 177 | 16:09.40 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'picked up the war drum' on a flat 'sea' backdrop for 7.7s |
| 178 | 16:17.13 | Host-only hold over 4 s | host-only shot lasts 4.3s |
| 179 | 16:21.40 | Element pops in within one frame (no easing) | element appears in one frame (diff 4.2) with no ease |
| 180 | 16:24.37 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'the Chinese admiral Chen Lin' on a flat 'sea' backdrop for 4.0s |
| 181 | 16:29.97 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'fell to the deck three times' on a flat 'sea' backdrop for 3.2s |
| 182 | 16:45.20 | Element pops in within one frame (no easing) | element appears in one frame (diff 3.5) with no ease |
| 183 | 16:45.20 | Host-only hold over 4 s | host-only shot lasts 4.8s |
| 184 | 16:55.20 | Card on screen with no content yet | 'PART ONE: THE DEATHS' card shows empty for 0.73s |
| 185 | 16:55.20 | Card text under 3% of frame height (unreadable on phone) | list card body text under 3% of frame height (unreadable on phones) |
| 186 | 17:06.23 | Host-only hold over 4 s | host-only shot lasts 4.5s |
| 187 | 17:10.70 | Element pops in within one frame (no easing) | element appears in one frame (diff 23.8) with no ease |
| 188 | 17:10.70 | Host-only hold over 4 s | host-only shot lasts 4.1s |
| 189 | 17:14.83 | Card on screen with no content yet | 'LIFE LESSONS' card shows empty for 2.47s |
| 190 | 17:14.83 | Card text under 3% of frame height (unreadable on phone) | list card body text under 3% of frame height (unreadable on phones) |
| 191 | 17:36.47 | Scene on a flat cartoon backdrop, held over 2.5 s | scene 'Sources: a pile' on a flat 'hall' backdrop for 4.0s |

## C. Audio issues

| Time | Issue |
|---|---|
| 11:25.26 | Music starts abruptly from silence (no fade or pickup). |
| 9:18.13, 9:18.45 | Possible clicks (sample jumps in a quiet passage). |
| Throughout | **73 music cue changes**, one every 14.7 s. Tempo and key restart mid-phrase, so the score sounds choppy. The reference changes track once per entry. |
| Throughout | Voice is an offline TTS (Kokoro): synthetic timbre and flat prosody. |
| Throughout | Music is General MIDI soundfont playback of algorithmic parts, so it sounds like "video-game MIDI". |
| Throughout | SFX are procedurally synthesized (crowds, whooshes, impacts) and sound thin and artificial. |
| Throughout | Over-compressed master: LRA 1.8 LU (reference 3.2), so the mix sounds flat. |

## D. Gap table

| Area | Reference | Last version | Fix |
|---|---|---|---|
| **Look** | 73% black stage, corner/centre 0.12; black/white/red only; real photos about 30% of runtime | 51% black, corner/centre 0.38; brown/olive/sky palette; 39 flat cartoon backdrops | Rebuild every scene on real photos with blur-fill; strict black/white/red palette; darker vignette |
| **Animation** | Flipbook walk/run cycles, 3–5-frame settles, characters enter and exit | Expression swaps only; 65 one-frame pop-ins; holds up to 6.3 s | New animation layer: eased/spring entrances with overshoot, flipbook cycles, enter/exit moves, secondary motion, push-in on every hold |
| **Pacing** | Median shot 2.73 s, 2.8 changes per 5 s, at most 7 s per hold | Median 2.53 s, 3.2 changes per 5 s, but 24 host holds over 4 s | Cap any hold at 3.5 s with a new beat (punch-in, gag, label) |
| **Typography** | One heavy-wide sans; callouts about 9% of height; never small UI text | Archivo Expanded; cards and tags at 1.5–3% of height; callouts on the hat and on photos | Unbounded 800/900 (open-licence twin of the reference face); minimum text 4.5% of height; safe-zone layout engine so text never touches characters |
| **Sound** | Human VO, library beds about 100 BPM, 24 dB under; title hits; gag SFX | TTS; GM-MIDI score with 73 changes; synthetic SFX; LRA 1.8 | Needs your assets (see questions). Otherwise: one bed per entry, longer music phrases, recorded-style SFX layering, less compression |
| **Hook** | Motion and a spoken hook in frame 1 | Static title, generic line | Open mid-action on the strongest visual (the crowned corpse / war drum) with the curiosity line in the first 1.5 s |

## E. Root causes of the cheap look (to rebuild, not patch)

1. **Assets**: procedural cartoon backdrops and UI-mock cards instead of real photos and clean big type.
2. **Animation system**: the rig can only swap faces. There's no motion grammar: no entrances, cycles or follow-through.
3. **Layout**: no collision or safe-zone logic, so text hits characters, lands on busy photos, and sits tiny.
4. **Audio sources**: TTS voice, General MIDI instruments, synthesized SFX. These are the main reasons it "sounds cheap", and no mixing can fully fix them.
5. **Music editing**: a cue every 15 s instead of a track per entry.
6. **Hook**: a static title card as frame 1.
