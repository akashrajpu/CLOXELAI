import React from 'react';
import { Sparkles, Layers, CloudUpload, Clapperboard, AudioLines, BrainCircuit, ChevronLeft } from 'lucide-react';

export default function Features({ onClose }) {
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
          Platform Features
        </h1>
        <div style={{ width: '130px' }}></div> {/* Spacer for centering */}
      </div>

      <div style={{ maxWidth: '1200px', margin: '40px auto', padding: '0 20px' }}>
        
        {/* Header Section */}
        <div style={{ textAlign: 'center', marginBottom: '80px' }}>
          <div style={{ display: 'inline-block', padding: '8px 20px', background: 'rgba(168,85,247,0.2)', color: '#c084fc', borderRadius: '50px', fontWeight: 'bold', marginBottom: '20px' }}>
            <Sparkles size={16} style={{ display: 'inline', verticalAlign: 'text-bottom', marginRight: '6px' }} />
            ⚡ CORE CAPABILITIES
          </div>
          <h2 style={{ fontSize: '3.5rem', margin: '0 0 20px 0', fontWeight: '900', background: 'linear-gradient(135deg, #fff 0%, #c084fc 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Everything You Need To Dominate
          </h2>
          <p style={{ fontSize: '1.2rem', color: '#cbd5e1', maxWidth: '700px', margin: '0 auto', lineHeight: '1.6' }}>
            Cloxel AI is packed with cutting-edge cloud rendering, AI script generation, and YouTube automation features. Build your faceless empire today.
          </p>
        </div>

        {/* Highlight 1: AI Script Generation */}
        <div style={{ display: 'flex', gap: '40px', alignItems: 'center', marginBottom: '80px', flexWrap: 'wrap' }}>
          <div style={{ flex: '1 1 500px', order: 1 }}>
            <img src="/ai_script_writer.jpg" alt="AI Script Writer" style={{ width: '100%', borderRadius: '24px', boxShadow: '0 20px 50px rgba(168,85,247,0.3)', border: '1px solid rgba(168,85,247,0.4)' }} />
          </div>
          <div style={{ flex: '1 1 400px', order: 2 }}>
            <div style={{ width: '60px', height: '60px', borderRadius: '16px', background: 'rgba(168,85,247,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '20px' }}>
              <BrainCircuit size={32} color="#c084fc" />
            </div>
            <h3 style={{ fontSize: '2.2rem', color: '#fff', margin: '0 0 15px 0' }}>Neural Script & Voice Generation</h3>
            <p style={{ color: '#94a3b8', fontSize: '1.1rem', lineHeight: '1.6', marginBottom: '20px' }}>
              Powered by advanced Google Gemini AI, Cloxel generates captivating, highly-retaining scripts automatically from just a single prompt. Integrated with our hyper-realistic neural voice synthesizer, your videos will sound just like a human narrator.
            </p>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, color: '#e2e8f0', display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <li>✅ Built-in hook writing for maximum engagement</li>
              <li>✅ Scene-by-scene visual direction & breakdown</li>
              <li>✅ Hyper-realistic Madhur Neural Voice (Hindi/English)</li>
            </ul>
          </div>
        </div>

        {/* Highlight 2: Ultra Photo Motion */}
        <div style={{ display: 'flex', gap: '40px', alignItems: 'center', marginBottom: '80px', flexWrap: 'wrap' }}>
          <div style={{ flex: '1 1 400px', order: 1 }}>
            <div style={{ width: '60px', height: '60px', borderRadius: '16px', background: 'rgba(236,72,153,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '20px' }}>
              <Layers size={32} color="#f472b6" />
            </div>
            <h3 style={{ fontSize: '2.2rem', color: '#fff', margin: '0 0 15px 0' }}>Ultra Photo Motion Format</h3>
            <p style={{ color: '#94a3b8', fontSize: '1.1rem', lineHeight: '1.6', marginBottom: '20px' }}>
              Stand out from standard stock footage with our exclusive <strong>Ultra Photo Motion</strong> mode. Cloxel takes multiple high-res static images and intelligently animates them into a dynamic, flowing 60FPS sequence with cinematic transitions and parallax effects.
            </p>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, color: '#e2e8f0', display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <li>✅ Unique style perfect for History and Documentary channels</li>
              <li>✅ Cinematic panning, zooming, and ink transition effects</li>
              <li>✅ Automatic color grading to fit the mood (Epic, Dark, Warm)</li>
            </ul>
          </div>
          <div style={{ flex: '1 1 500px', order: 2 }}>
            <img src="/ultra_photo_motion.jpg" alt="Ultra Photo Motion" style={{ width: '100%', borderRadius: '24px', boxShadow: '0 20px 50px rgba(236,72,153,0.3)', border: '1px solid rgba(236,72,153,0.4)' }} />
          </div>
        </div>

        {/* Highlight 3: YouTube Auto Upload */}
        <div style={{ display: 'flex', gap: '40px', alignItems: 'center', marginBottom: '80px', flexWrap: 'wrap' }}>
          <div style={{ flex: '1 1 500px', order: 1 }}>
            <img src="/youtube_auto_upload.jpg" alt="YouTube Auto Upload" style={{ width: '100%', borderRadius: '24px', boxShadow: '0 20px 50px rgba(59,130,246,0.3)', border: '1px solid rgba(59,130,246,0.4)' }} />
          </div>
          <div style={{ flex: '1 1 400px', order: 2 }}>
            <div style={{ width: '60px', height: '60px', borderRadius: '16px', background: 'rgba(59,130,246,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '20px' }}>
              <CloudUpload size={32} color="#93c5fd" />
            </div>
            <h3 style={{ fontSize: '2.2rem', color: '#fff', margin: '0 0 15px 0' }}>1-Click YouTube Auto-Publish</h3>
            <p style={{ color: '#94a3b8', fontSize: '1.1rem', lineHeight: '1.6', marginBottom: '20px' }}>
              Why download heavy video files manually? Our powerful cloud engine renders the video securely and directly pushes it to your YouTube channel as a Draft or Public video using the official YouTube API.
            </p>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, color: '#e2e8f0', display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <li>✅ 100% Cloud-based rendering (No GPU required on your end)</li>
              <li>✅ Automatic Title & Description generation</li>
              <li>✅ Secure OAuth 2.0 integration with Google</li>
            </ul>
          </div>
        </div>

        {/* Additional Mini Features Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginBottom: '60px' }}>
          <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)', padding: '24px', borderRadius: '16px' }}>
            <Clapperboard size={24} color="#a855f7" style={{ marginBottom: '15px' }} />
            <h4 style={{ color: '#fff', fontSize: '1.2rem', marginBottom: '10px' }}>Multiple Aspect Ratios</h4>
            <p style={{ color: '#94a3b8', fontSize: '0.9rem', lineHeight: '1.5' }}>Generate 9:16 vertical Shorts for TikTok/Reels, or 16:9 widescreen videos for standard YouTube.</p>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)', padding: '24px', borderRadius: '16px' }}>
            <AudioLines size={24} color="#10b981" style={{ marginBottom: '15px' }} />
            <h4 style={{ color: '#fff', fontSize: '1.2rem', marginBottom: '10px' }}>Dynamic Captions</h4>
            <p style={{ color: '#94a3b8', fontSize: '0.9rem', lineHeight: '1.5' }}>Auto-synced, glowing yellow animated subtitles to keep viewers hooked till the very end.</p>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)', padding: '24px', borderRadius: '16px' }}>
            <CloudUpload size={24} color="#f59e0b" style={{ marginBottom: '15px' }} />
            <h4 style={{ color: '#fff', fontSize: '1.2rem', marginBottom: '10px' }}>30-Day Auto Schedule</h4>
            <p style={{ color: '#94a3b8', fontSize: '0.9rem', lineHeight: '1.5' }}>Subscribe to a plan and schedule videos to generate and upload automatically every day.</p>
          </div>
        </div>

        <div style={{ textAlign: 'center', padding: '60px 0', borderTop: '1px solid rgba(255,255,255,0.1)', marginTop: '40px' }}>
          <button onClick={onClose} style={{ background: 'linear-gradient(135deg, #ec4899 0%, #a855f7 100%)', color: '#fff', border: 'none', padding: '16px 40px', fontSize: '1.2rem', fontWeight: '900', borderRadius: '50px', cursor: 'pointer', boxShadow: '0 10px 30px rgba(236,72,153,0.4)' }}>
            Start Using Cloxel AI 🚀
          </button>
        </div>

      </div>
    </div>
  );
}
