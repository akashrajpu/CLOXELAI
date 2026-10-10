import React from 'react';
import { MessageSquare, Mail, HelpCircle, ShieldCheck, Zap, Globe, ChevronLeft } from 'lucide-react';

export default function Support({ onClose }) {
  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: '#0b071a',
      zIndex: 9999,
      overflowY: 'auto',
      color: '#f8fafc',
      fontFamily: "'Inter', sans-serif"
    }}>
      {/* Dark Grid Background */}
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
          Help & Support
        </h1>
        <div style={{ width: '130px' }}></div>
      </div>

      <div style={{ maxWidth: '1200px', margin: '40px auto', padding: '0 20px' }}>
        
        {/* Header Section */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', marginBottom: '80px' }}>
          <div style={{ padding: '8px 20px', background: 'rgba(59,130,246,0.2)', color: '#93c5fd', borderRadius: '50px', fontWeight: 'bold', marginBottom: '20px' }}>
            <MessageSquare size={16} style={{ display: 'inline', verticalAlign: 'text-bottom', marginRight: '6px' }} />
            24/7 SUPPORT CENTER
          </div>
          <h2 style={{ display: 'inline-block', fontSize: '3.5rem', margin: '0 0 20px 0', fontWeight: '900', background: 'linear-gradient(135deg, #fff 0%, #93c5fd 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', textAlign: 'center' }}>
            We're Here to Help
          </h2>
          <p style={{ fontSize: '1.2rem', color: '#cbd5e1', maxWidth: '700px', margin: '0 auto', lineHeight: '1.6' }}>
            Have questions about your subscription, facing rendering issues, or need API access? Our global support team is available around the clock.
          </p>
        </div>

        {/* Contact Methods */}
        <div style={{ display: 'flex', gap: '40px', marginBottom: '80px', flexWrap: 'wrap' }}>
          
          {/* Card 1 */}
          <div style={{ flex: '1 1 500px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(59,130,246,0.3)', borderRadius: '24px', padding: '40px', display: 'flex', gap: '30px', alignItems: 'center' }}>
            <div style={{ width: '80px', height: '80px', borderRadius: '20px', background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, boxShadow: '0 10px 30px rgba(59,130,246,0.4)' }}>
              <Mail size={40} color="#fff" />
            </div>
            <div>
              <h3 style={{ fontSize: '1.8rem', color: '#fff', margin: '0 0 10px 0' }}>Direct Email Support</h3>
              <p style={{ color: '#94a3b8', fontSize: '1.1rem', margin: '0 0 15px 0', lineHeight: '1.5' }}>
                Email our support team directly for account, billing, or general queries.
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <a href="mailto:support@cloxel.com" style={{ color: '#93c5fd', fontWeight: 'bold', textDecoration: 'none', fontSize: '1.1rem' }}>support@cloxel.com</a>
                <a href="mailto:zobbly.com@gmail.com" style={{ color: '#93c5fd', fontWeight: 'bold', textDecoration: 'none', fontSize: '1.1rem' }}>zobbly.com@gmail.com</a>
              </div>
            </div>
          </div>

          {/* Card 2 (Replaced Founder with Premium Enterprise Support) */}
          <div style={{ flex: '1 1 500px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: '24px', padding: '40px', display: 'flex', gap: '30px', alignItems: 'center' }}>
            <div style={{ width: '80px', height: '80px', borderRadius: '20px', background: 'linear-gradient(135deg, #10b981 0%, #3b82f6 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, boxShadow: '0 10px 30px rgba(16,185,129,0.4)' }}>
              <ShieldCheck size={40} color="#fff" />
            </div>
            <div>
              <h3 style={{ fontSize: '1.8rem', color: '#fff', margin: '0 0 10px 0' }}>Priority & Enterprise</h3>
              <p style={{ color: '#94a3b8', fontSize: '1.1rem', margin: '0 0 15px 0', lineHeight: '1.5' }}>
                Dedicated support queue for our premium subscribers with guaranteed fast resolution times.
              </p>
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 12px', background: 'rgba(16,185,129,0.1)', borderRadius: '8px', color: '#6ee7b7', fontWeight: 'bold' }}>
                <Zap size={16} /> Guaranteed response &lt; 12 hours
              </div>
            </div>
          </div>

        </div>

        {/* Visual Images Section */}
        <div style={{ display: 'flex', gap: '40px', marginBottom: '80px', flexWrap: 'wrap' }}>
          <div style={{ flex: '1 1 400px' }}>
            <img src="/priority_support_ai.jpg" alt="AI Support Assistant" style={{ width: '100%', borderRadius: '24px', boxShadow: '0 20px 50px rgba(236,72,153,0.2)', border: '1px solid rgba(255,255,255,0.1)' }} />
          </div>
          <div style={{ flex: '1 1 400px' }}>
            <img src="/global_support_network.jpg" alt="Global Network" style={{ width: '100%', borderRadius: '24px', boxShadow: '0 20px 50px rgba(59,130,246,0.2)', border: '1px solid rgba(255,255,255,0.1)' }} />
          </div>
        </div>

        {/* FAQ Section */}
        <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '24px', padding: '50px', marginBottom: '80px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '30px' }}>
            <HelpCircle size={32} color="#f43f5e" />
            <h3 style={{ fontSize: '2rem', color: '#fff', margin: 0 }}>Frequently Asked Questions</h3>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
            <div>
              <h4 style={{ color: '#fff', fontSize: '1.2rem', marginBottom: '10px' }}>How do I activate my 30-day membership?</h4>
              <p style={{ color: '#94a3b8', fontSize: '1.1rem', lineHeight: '1.6', margin: 0 }}>
                Select your desired plan from the pricing panel and complete the Razorpay checkout. Activation is completely automatic and instant.
              </p>
            </div>
            
            <div style={{ height: '1px', background: 'rgba(255,255,255,0.1)' }}></div>

            <div>
              <h4 style={{ color: '#fff', fontSize: '1.2rem', marginBottom: '10px' }}>What if I repurchase an active plan?</h4>
              <p style={{ color: '#94a3b8', fontSize: '1.1rem', lineHeight: '1.6', margin: 0 }}>
                Your active membership is automatically extended by an additional 30 days. No credits or time is lost.
              </p>
            </div>

            <div style={{ height: '1px', background: 'rgba(255,255,255,0.1)' }}></div>

            <div>
              <h4 style={{ color: '#fff', fontSize: '1.2rem', marginBottom: '10px' }}>Can I auto-upload videos to YouTube?</h4>
              <p style={{ color: '#94a3b8', fontSize: '1.1rem', lineHeight: '1.6', margin: 0 }}>
                Yes, connect your YouTube channel securely from the dashboard panel. Once connected, Cloxel will push generated videos straight to your studio.
              </p>
            </div>
          </div>
        </div>

        <div style={{ textAlign: 'center', padding: '40px 0', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
          <button onClick={onClose} style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)', color: '#fff', border: 'none', padding: '16px 40px', fontSize: '1.2rem', fontWeight: '900', borderRadius: '50px', cursor: 'pointer', boxShadow: '0 10px 30px rgba(59,130,246,0.4)' }}>
            Close Support & Return to App
          </button>
        </div>

      </div>
    </div>
  );
}
