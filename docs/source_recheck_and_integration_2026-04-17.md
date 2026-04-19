# Source recheck and integration note (2026-04-17)

## Archive recheck

The resent `jaciii_iihmsp2025.zip` still appeared to contain directory entries without file payloads when inspected locally.

## Concrete source used in this update

The usable source-of-truth input is therefore the separately attached `definitions.py`, now stored at:

- `external/jaciii_iihmsp2025/definitions.py`

## Mapping adopted in this repository

### Texts
- `T1` ↔ `t1` ↔ 懐中時計 / The Pocket Watch / 懷中時計
- `T2` ↔ `t2` ↔ お金とピストル / The Money and the Pistol / 錢與手槍
- `T3` ↔ `t3` ↔ ぼろぼろな駝鳥 / The Tattered Ostrich / 襤褸的鴕鳥

### Personas
- `p1` 大学1年生 / College Freshman / 大一新生
- `p2` 文学研究者 / Literary Scholar / 文學研究者
- `p3` 感情豊かな詩人 / The Emotive Poet / 感性詩人
- `p4` 無感情なロボット / The Emotionless Robot / 無情感機器人
- `p0` Neutral Reader (new, ICECCME primary analysis only)

## Design decision

For ICECCME, `p0` is the main paper persona so that the paper is centered on a human-grounded benchmark rather than on persona–temperature modulation. The original four personas remain available for sensitivity analysis and continuity with the prior repo lineage.
