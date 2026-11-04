// 9:16 version of Promo2: the 16:9 film fitted to the width, framed by a title above and the contact row below.
import React from 'react';
import { AbsoluteFill, useCurrentFrame } from 'remotion';
import { DISPLAY, FontGate, LATIN } from '../lib/fonts';
import { Promo2 } from './Promo2';

const GOLD = '#F5B54A';
const W = 1080, VW = 1080, VH = (1080 * 1080) / 1920; // the 16:9 film scaled to the full width

export const Promo2Vertical: React.FC = () => {
  const frame = useCurrentFrame();
  const glow = 0.5 + 0.5 * Math.sin(frame / 18);
  const top = 560;
  return (
    <FontGate>
      <AbsoluteFill style={{ background: 'radial-gradient(ellipse at 50% 40%, #16306A 0%, #0A1638 70%)' }}>
        <div style={{ position: 'absolute', top: 170, width: W, textAlign: 'center', direction: 'rtl' }}>
          <div style={{ fontFamily: DISPLAY, fontWeight: 800, fontSize: 70, color: '#fff', lineHeight: 1.25 }}>مكتبة الأستاذ</div>
          <div style={{ fontFamily: DISPLAY, fontWeight: 800, fontSize: 82, color: GOLD, lineHeight: 1.25 }}>سوايسية هشام</div>
          <div style={{ marginTop: 26, display: 'inline-block', padding: '10px 34px', borderRadius: 40, background: GOLD, color: '#10203F', fontFamily: DISPLAY, fontWeight: 800, fontSize: 40 }}>
            <span style={{ fontFamily: LATIN }}>+140</span> ملفًا للسنوات الثلاث ثانوي
          </div>
        </div>
        <div style={{ position: 'absolute', left: 0, top, width: VW, height: VH, overflow: 'hidden', borderTop: `4px solid ${GOLD}`, borderBottom: `4px solid ${GOLD}`, boxShadow: `0 0 ${30 + 30 * glow}px rgba(245,181,74,0.45)` }}>
          <div style={{ width: 1920, height: 1080, transform: `scale(${VW / 1920})`, transformOrigin: 'top left' }}>
            <Promo2 />
          </div>
        </div>
        <div style={{ position: 'absolute', top: top + VH + 90, width: W, textAlign: 'center', direction: 'rtl' }}>
          <div style={{ fontFamily: DISPLAY, fontWeight: 800, fontSize: 46, color: '#fff' }}>مطابقة للمنهاج وللتوزيع السنوي</div>
          <div style={{ fontFamily: DISPLAY, fontWeight: 700, fontSize: 38, color: '#9FE7FF', marginTop: 14 }}>PDF · Word · LaTeX — قابلة للتعديل</div>
          <div style={{ margin: '48px auto 0', width: 820, padding: '22px 0', borderRadius: 30, border: '3px solid #25D366', background: 'rgba(37,211,102,0.12)', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 26, direction: 'ltr' }}>
            <svg width={78} height={78} viewBox="0 0 32 32"><circle cx="16" cy="16" r="16" fill="#25D366" /><path fill="#fff" d="M16 6.2a9.7 9.7 0 0 0-8.4 14.6L6.3 25.7l5-1.3A9.7 9.7 0 1 0 16 6.2zm0 17.7a8 8 0 0 1-4.1-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8 8 0 1 1 16 23.9zm4.4-6c-.2-.1-1.4-.7-1.7-.8-.2-.1-.4-.1-.5.1l-.8 1c-.1.2-.3.2-.5.1a6.6 6.6 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.5-.4h-.5a.9.9 0 0 0-.6.3 2.7 2.7 0 0 0-.8 2c0 1.2.9 2.3 1 2.5.1.2 1.7 2.6 4.2 3.7 1.6.7 2.2.7 3 .6.5-.1 1.4-.6 1.6-1.1.2-.6.2-1 .1-1.1l-.6-.4z" /></svg>
            <span style={{ fontFamily: LATIN, fontWeight: 800, fontSize: 64, color: '#fff', letterSpacing: 2 }}>0699 92 80 24</span>
          </div>
          <div style={{ marginTop: 26, fontFamily: DISPLAY, fontWeight: 700, fontSize: 34, color: '#C9D4F0' }}>فايسبوك: الأستاذ سوايسية هشام للرياضيات</div>
          <div style={{ marginTop: 8, fontFamily: DISPLAY, fontWeight: 700, fontSize: 34, color: '#C9D4F0' }}>إنستغرام: <span style={{ fontFamily: LATIN }}>prof_hicham_math</span></div>
        </div>
      </AbsoluteFill>
    </FontGate>
  );
};
