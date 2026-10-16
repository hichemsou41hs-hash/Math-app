<div dir="rtl">

# قواعد Remotion في هذا المشروع

## المبدأ: كل إطار دالة في الزمن
- يُرسم كل إطار من رقمه فقط. ولهذا تطابق المعاينة في Studio الفيديو المرندر تمامًا.
- **ممنوع:**
  - CSS transitions أو animations.
  - `setTimeout`.
  - state يتراكم بين الإطارات.
  - `Math.random()`.
- **العشوائية:** استخدم `random('seed-' + i)` من `remotion`، فهي تعطي نفس الرقم في كل مرة.

## شكل المشهد
```tsx
import React from 'react';
import { AbsoluteFill, Easing, useCurrentFrame } from 'remotion';
import { line, word, prog, toSec } from '../timing';

export const Hook: React.FC<{ from: number }> = ({ from }) => {
  const t = from + toSec(useCurrentFrame()); // ساعة الفيديو بالثواني (نفس أرقام words.json)
  const l = line('أول كلمات الجملة');
  const w = word(l, 'الكلمة');
  const k = prog(t, w.start, w.start + 0.45, Easing.out(Easing.cubic));
  return (
    <AbsoluteFill>
      <div style={{ opacity: k, transform: `translateY(${(1 - k) * 40}px)` }}>{w.w}</div>
    </AbsoluteFill>
  );
};
```
- `useCurrentFrame()` داخل `<Sequence>` يبدأ من صفر عند بداية المشهد. لذلك نضيف `from` (يمرّره `Video.tsx`) لنحصل على ساعة الفيديو.
- **حدود المشهد** في `Video.tsx`:
  - البداية: `from: cutBefore('أول كلمات جملته')`.
  - النهاية: `to:` بداية المشهد التالي.
  - القطع يكون في الوقفة قبل الجملة، لا في منتصفها.
- **لا تكتب ثوانيَ بالأرقام.** المدد الصغيرة مسموحة، مثل 0.45 ثانية لدخول عنصر. أما **متى** يحدث الشيء، فيأتي دائمًا من كلمة.

## كاميرا تسافر فوق ورقة واحدة
إن كان المرجع ينتقل بين المشاهد بحركة كاميرا لا بقطع:
- ضع كل المشاهد في عالم واحد، وأعطِ كل مشهد مكانًا فيه.
- في `Video.tsx`، لُفّ المشاهد في حاوية واحدة عليها تحويل الكاميرا:
  ```
  transform: translate(W/2, H/2) scale(z) translate(-x, -y)
  ```
- استخدم `<Sequence layout="none">` حتى لا يضع Remotion كل مشهد في `AbsoluteFill` خاص به خارج العالم.
- مدّد ظهور كل مشهد حتى نهاية حركة الكاميرا إلى المشهد التالي، فيبقى المشهدان ظاهرين أثناء السفر.
- اجعل الخلفية المشتركة (ورق أو شبكة) جزءًا من نفس الحاوية، فتتحرك مع الكاميرا.

## الحركة
- `prog(t, a, b, easing)`: من 0 إلى 1 بين ثانيتين. استخدم معه `interpolate` لأي قيمة.
- **المنحنيات:**
  - `Easing.out(Easing.cubic)`: للدخول.
  - `Easing.in(Easing.cubic)`: للخروج.
  - `Easing.inOut(Easing.sin)`: لحركة الكاميرا الهادئة.
  - `Easing.bezier(...)`: لمنحنى قِسته من المرجع.
- **النوابض:** `spring({ frame, fps, config: { damping: 200 } })` للهادئ، ودرجة damping أقل للمطاطي، إن كان المرجع يرتد.
- **الكاميرا:** `transform` على حاوية المشهد (`scale` و`translate`). وحركة الكاميرا لا تقل عن 0.6 ثانية إلا إن كان المرجع أسرع.

## الرسم
- **النص:** HTML وCSS أسهل، لأن المتصفح يتولّى تشكيل العربية والاتجاه.
- **الخطوط والأشكال والرسم التدريجي:** SVG.
  ```tsx
  <path d="..." pathLength={1} strokeDasharray={1} strokeDashoffset={1 - k} fill="none" stroke="#fff" />
  ```
- **الصور:** في `video/public/`، وتُعرض بـ `<Img src={staticFile('x.png')} />`.

## الخطوط
حمّل الخط في أعلى الملف، مرة واحدة. `loadFont` ينتظر تحميل الخط قبل الرسم وحده.
```ts
import { loadFont } from '@remotion/google-fonts/IBMPlexSansArabic';
const { fontFamily } = loadFont('normal', { weights: ['400', '700'], subsets: ['arabic', 'latin'] });
```
اسم الحزمة هو اسم الخط بلا مسافات: `Cairo`، و`ReadexPro`، و`NotoKufiArabic`، و`IBMPlexMono`...

## الصوت
- **التعليق:** `Video.tsx` يشغّله وحده من `words.json` (الحقل `audio`).
- **المؤثر الصوتي:** داخل `<Sequence>` يبدأ عند الحدث:
  ```tsx
  <Sequence from={toFrame(w.start)} durationInFrames={30}><Html5Audio src={staticFile('sfx/hit.wav')} volume={0.4} /></Sequence>
  ```
  ومن `@remotion/sfx`: `import { whoosh } from '@remotion/sfx'` ثم `src={whoosh}`.

## اللمسة الأخيرة (حسب المرجع فقط)
- **توهج:** نسخة ثانية من الطبقة فوقها، عليها `filter: blur(8px)` و`mixBlendMode: 'screen'`. ولا تستخدم `blur` كبيرًا على الإطار كله، لأنه بطيء.
- **حبيبات:** SVG `feTurbulence` بـ `seed` يتغير مع الإطار، وشفافية 0.08 أو أقل، و`mixBlendMode: 'soft-light'`. يجب ألا تظهر كنقاط أبدًا.
- **تعتيم الأطراف:** `radial-gradient` من شفاف في المنتصف إلى أسود خفيف عند الحواف.

## الأوامر (من داخل `video/`)
| الأمر | متى |
|---|---|
| `npm run studio` | المعاينة. شغّله في الخلفية، فهو يتحدّث وحده مع كل تعديل |
| `npm run stills -- 3 7.5` | صور ثابتة للمراجعة، مسموح في أي وقت |
| `npm run typecheck` | قبل التسليم |
| `npm run render -- --approved` | **فقط** بعد موافقة المستخدم |

## الأداء
- `premountFor` موجود على كل مشهد.
- لا ترسم آلاف العناصر في كل إطار.
- إن صار Studio بطيئًا: قلّل الـ `blur`، واستخدم `will-change: transform`.

</div>
