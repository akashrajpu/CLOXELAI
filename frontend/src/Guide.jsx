import React from 'react';
import { Rocket, MonitorPlay, Sparkles, Clapperboard, CheckCircle2, ChevronLeft, Bot, Wand2, Video, Cloud } from 'lucide-react';

export default function Guide({ onClose }) {
  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: '#0b071a',
      zIndex: 9999,
      overflowY: 'auto',
      color: '#f8fafc',
      fontFamily: "'Inter', sans-serif"
    }}>
      {/* Dark Grid Background matching main app */}
      <div style={{
        position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: -1,
        backgroundImage: `
          radial-gradient(circle at 50% 0%, rgba(168, 85, 247, 0.18) 0%, transparent 60%),
          linear-gradient(to bottom, transparent 50%, #0b071a 100%),
          linear-gradient(rgba(168, 85, 247, 0.22) 1px, transparent 1px),
          linear-gradient(90deg, rgba(168, 85, 247, 0.22) 1px, transparent 1px)
        `,
        backgroundSize: '100% 100vh, 100% 100vh, 45px 45px, 45px 45px',
        backgroundPosition: 'center top'
      }} />

      {/* Navigation Bar */}
      <div style={{
        position: 'sticky', top: 0,
        background: 'rgba(11, 7, 26, 0.85)', backdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(168, 85, 247, 0.3)',
        padding: '16px 32px', display: 'flex', alignItems: 'center', zIndex: 10
      }}>
        <button 
          onClick={onClose}
          style={{
            background: 'transparent', border: '1px solid rgba(255,255,255,0.2)',
            color: '#fff', padding: '8px 16px', borderRadius: '12px',
            display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer',
            fontWeight: 'bold', transition: 'all 0.2s'
          }}
          onMouseOver={e => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
          onMouseOut={e => e.currentTarget.style.background = 'transparent'}
        >
          <ChevronLeft size={20} /> Back to Home
        </button>
        <h1 style={{ margin: '0 auto', fontSize: '1.4rem', color: '#c084fc', fontWeight: '800' }}>
          Cloxel AI Platform Guide
        </h1>
        <div style={{ width: '130px' }}></div> {/* Spacer for centering */}
      </div>

      <div style={{ maxWidth: '1100px', margin: '40px auto', padding: '0 20px' }}>
        
        {/* Header Section */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', marginBottom: '60px' }}>
          <div style={{ padding: '8px 20px', background: 'rgba(168,85,247,0.2)', color: '#c084fc', borderRadius: '50px', fontWeight: 'bold', marginBottom: '20px' }}>
            <Sparkles size={16} style={{ display: 'inline', verticalAlign: 'text-bottom', marginRight: '6px' }} />
            COMPLETE WORKFLOW TUTORIAL
          </div>
          <h2 style={{ display: 'inline-block', fontSize: '3.5rem', margin: '0 0 20px 0', fontWeight: '900', background: 'linear-gradient(135deg, #fff 0%, #c084fc 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', textAlign: 'center' }}>
            How to Create Viral Videos
          </h2>
          <p style={{ fontSize: '1.2rem', color: '#cbd5e1', maxWidth: '700px', margin: '0 auto', lineHeight: '1.6' }}>
            Cloxel AI is a fully automated cloud engine. Follow these 4 simple steps to generate high-retention Faceless YouTube videos in minutes.
          </p>
        </div>

        {/* Step by Step Section */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '40px', marginBottom: '80px' }}>
          
          {/* Step 1 */}
          <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(168,85,247,0.3)', borderRadius: '24px', padding: '40px', display: 'flex', gap: '30px', alignItems: 'center' }}>
            <div style={{ width: '80px', height: '80px', borderRadius: '20px', background: 'linear-gradient(135deg, #a855f7 0%, #6366f1 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, boxShadow: '0 10px 30px rgba(168,85,247,0.4)' }}>
              <Bot size={40} color="#fff" />
            </div>
            <div style={{ textAlign: 'left' }}>
              <h3 style={{ fontSize: '1.8rem', color: '#fff', margin: '0 0 10px 0' }}>Step 1: Choose Your Topic & Format</h3>
              <p style={{ color: '#94a3b8', fontSize: '1.1rem', margin: '0 0 15px 0', lineHeight: '1.5' }}>
                Select whether you want a <strong>Short (9:16)</strong> for YouTube Shorts/Reels, a <strong>Long (16:9)</strong> video for standard YouTube, or our premium <strong>Ultra Photo Motion</strong> format. Then, simply type a topic like <em>"History of Black Holes"</em>.
              </p>
              <div style={{ display: 'flex', gap: '15px' }}>
                <span style={{ padding: '6px 12px', background: 'rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '0.9rem', color: '#c084fc' }}><CheckCircle2 size={14} style={{ display: 'inline', marginRight: '4px' }}/> 30+ Categories Supported</span>
                <span style={{ padding: '6px 12px', background: 'rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '0.9rem', color: '#c084fc' }}><CheckCircle2 size={14} style={{ display: 'inline', marginRight: '4px' }}/> Multiple Aspect Ratios</span>
              </div>
            </div>
          </div>

          {/* Step 2 */}
          <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(168,85,247,0.3)', borderRadius: '24px', padding: '40px', display: 'flex', gap: '30px', alignItems: 'center', flexDirection: 'row-reverse' }}>
            <div style={{ width: '80px', height: '80px', borderRadius: '20px', background: 'linear-gradient(135deg, #ec4899 0%, #a855f7 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, boxShadow: '0 10px 30px rgba(236,72,153,0.4)' }}>
              <Wand2 size={40} color="#fff" />
            </div>
            <div style={{ textAlign: 'right' }}>
              <h3 style={{ fontSize: '1.8rem', color: '#fff', margin: '0 0 10px 0' }}>Step 2: Auto-Generate Script</h3>
              <p style={{ color: '#94a3b8', fontSize: '1.1rem', margin: '0 0 15px 0', lineHeight: '1.5' }}>
                Click the magical <strong>Auto-Generate Script via AI</strong> button. Our Gemini AI will parse your topic and write a highly engaging, viral script with hooks, scene descriptions, and perfect pacing. You can also manually edit the script if you want.
              </p>
              <div style={{ display: 'flex', gap: '15px', justifyContent: 'flex-end' }}>
                <span style={{ padding: '6px 12px', background: 'rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '0.9rem', color: '#f472b6' }}><CheckCircle2 size={14} style={{ display: 'inline', marginRight: '4px' }}/> Viral Hooks Built-in</span>
                <span style={{ padding: '6px 12px', background: 'rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '0.9rem', color: '#f472b6' }}><CheckCircle2 size={14} style={{ display: 'inline', marginRight: '4px' }}/> Scene-by-Scene Breakdown</span>
              </div>
            </div>
          </div>

          {/* Step 3 */}
          <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(168,85,247,0.3)', borderRadius: '24px', padding: '40px', display: 'flex', gap: '30px', alignItems: 'center' }}>
            <div style={{ width: '80px', height: '80px', borderRadius: '20px', background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, boxShadow: '0 10px 30px rgba(59,130,246,0.4)' }}>
              <Clapperboard size={40} color="#fff" />
            </div>
            <div style={{ textAlign: 'left' }}>
              <h3 style={{ fontSize: '1.8rem', color: '#fff', margin: '0 0 10px 0' }}>Step 3: Customize Visuals & Audio</h3>
              <p style={{ color: '#94a3b8', fontSize: '1.1rem', margin: '0 0 15px 0', lineHeight: '1.5' }}>
                Use the settings panel on the right to personalize your video. Choose a hyper-realistic AI Voice (Male or Female), pick a cinematic filter (like Warm Epic), add background music, and set your target duration (e.g., 60 seconds).
              </p>
              <div style={{ display: 'flex', gap: '15px' }}>
                <span style={{ padding: '6px 12px', background: 'rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '0.9rem', color: '#93c5fd' }}><CheckCircle2 size={14} style={{ display: 'inline', marginRight: '4px' }}/> Neural Voices</span>
                <span style={{ padding: '6px 12px', background: 'rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '0.9rem', color: '#93c5fd' }}><CheckCircle2 size={14} style={{ display: 'inline', marginRight: '4px' }}/> Color Grading Filters</span>
              </div>
            </div>
          </div>

          {/* Step 4 */}
          <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(168,85,247,0.3)', borderRadius: '24px', padding: '40px', display: 'flex', gap: '30px', alignItems: 'center', flexDirection: 'row-reverse' }}>
            <div style={{ width: '80px', height: '80px', borderRadius: '20px', background: 'linear-gradient(135deg, #10b981 0%, #3b82f6 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, boxShadow: '0 10px 30px rgba(16,185,129,0.4)' }}>
              <Rocket size={40} color="#fff" />
            </div>
            <div style={{ textAlign: 'right' }}>
              <h3 style={{ fontSize: '1.8rem', color: '#fff', margin: '0 0 10px 0' }}>Step 4: Generate & Auto-Upload</h3>
              <p style={{ color: '#94a3b8', fontSize: '1.1rem', margin: '0 0 15px 0', lineHeight: '1.5' }}>
                Hit the <strong>Generate Video</strong> button. Our powerful <strong>Cloxel Engine</strong> takes over: it fetches HD media, synthesizes the voiceover, generates auto-animated yellow captions, merges everything, and optionally auto-uploads directly to your YouTube channel!
              </p>
              <div style={{ display: 'flex', gap: '15px', justifyContent: 'flex-end' }}>
                <span style={{ padding: '6px 12px', background: 'rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '0.9rem', color: '#6ee7b7' }}><CheckCircle2 size={14} style={{ display: 'inline', marginRight: '4px' }}/> Cloxel Engine Rendering</span>
                <span style={{ padding: '6px 12px', background: 'rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '0.9rem', color: '#6ee7b7' }}><Video size={14} style={{ display: 'inline', marginRight: '4px' }}/> 1-Click YouTube Publish</span>
              </div>
            </div>
          </div>
        </div>

        {/* Example Videos Section */}
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h2 style={{ fontSize: '2.5rem', margin: '0 0 15px 0', fontWeight: '900', color: '#fff' }}>
            See What You Can Build
          </h2>
          <p style={{ fontSize: '1.1rem', color: '#94a3b8', marginBottom: '40px' }}>
            Check out these actual videos generated completely on autopilot by Cloxel AI.
          </p>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '30px' }}>
            
            <div style={{ background: 'rgba(0,0,0,0.4)', borderRadius: '20px', padding: '15px', border: '1px solid rgba(168,85,247,0.3)', boxShadow: '0 10px 30px rgba(0,0,0,0.5)' }}>
              <video src="https://res.cloudinary.com/dlf3caco8/video/upload/v1791608984/tqavkizjcsugjvpo44ta.mp4" style={{ width: '100%', borderRadius: '12px', objectFit: 'cover', aspectRatio: '16/9' }} autoPlay loop muted playsInline controls={false} />
              <div style={{ marginTop: '12px', fontWeight: 'bold', color: '#c084fc' }}>Ultra Photo Motion</div>
            </div>

            <div style={{ background: 'rgba(0,0,0,0.4)', borderRadius: '20px', padding: '15px', border: '1px solid rgba(168,85,247,0.3)', boxShadow: '0 10px 30px rgba(0,0,0,0.5)' }}>
              <video src="https://res.cloudinary.com/dlf3caco8/video/upload/v1788896103/duk8gsaalrfmhdnz0qmm.mp4" style={{ width: '100%', borderRadius: '12px', objectFit: 'cover', aspectRatio: '16/9' }} autoPlay loop muted playsInline controls={false} />
              <div style={{ marginTop: '12px', fontWeight: 'bold', color: '#c084fc' }}>AI History Long</div>
            </div>

            <div style={{ background: 'rgba(0,0,0,0.4)', borderRadius: '20px', padding: '15px', border: '1px solid rgba(168,85,247,0.3)', boxShadow: '0 10px 30px rgba(0,0,0,0.5)' }}>
              <video src="https://res.cloudinary.com/dlf3caco8/video/upload/v1788584205/tueaktarhjeugs3r11jc.mp4" style={{ width: '100%', borderRadius: '12px', objectFit: 'cover', aspectRatio: '16/9' }} autoPlay loop muted playsInline controls={false} />
              <div style={{ marginTop: '12px', fontWeight: 'bold', color: '#c084fc' }}>Mystery & Facts</div>
            </div>

            <div style={{ background: 'rgba(0,0,0,0.4)', borderRadius: '20px', padding: '15px', border: '1px solid rgba(168,85,247,0.3)', boxShadow: '0 10px 30px rgba(0,0,0,0.5)' }}>
              <video src="https://res.cloudinary.com/dlf3caco8/video/upload/v1788544557/xtnrv0cnnolqrvlwrpsr.mp4" style={{ width: '100%', borderRadius: '12px', objectFit: 'cover', aspectRatio: '16/9' }} autoPlay loop muted playsInline controls={false} />
              <div style={{ marginTop: '12px', fontWeight: 'bold', color: '#c084fc' }}>Motivational Story</div>
            </div>

          </div>
        </div>

        <div style={{ textAlign: 'center', padding: '60px 0', borderTop: '1px solid rgba(255,255,255,0.1)', marginTop: '40px' }}>
          <button onClick={onClose} style={{ background: 'linear-gradient(135deg, #ec4899 0%, #a855f7 100%)', color: '#fff', border: 'none', padding: '16px 40px', fontSize: '1.2rem', fontWeight: '900', borderRadius: '50px', cursor: 'pointer', boxShadow: '0 10px 30px rgba(236,72,153,0.4)' }}>
            Start Generating Videos Now 🚀
          </button>
        </div>

      </div>
    </div>
  );
}
