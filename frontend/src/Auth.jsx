import React, { useState, useEffect, useRef } from 'react';
import jsQR from 'jsqr';

const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';

function Auth({ onLoginSuccess }) {


  const [isLogin, setIsLogin] = useState(false); // Default to register or landing view
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Form Fields
  const [name, setName] = useState('');
  const [country, setCountry] = useState('India');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [emailOrMobile, setEmailOrMobile] = useState('');
  const [password, setPassword] = useState('');
  
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [agreedToPrivacy, setAgreedToPrivacy] = useState(false);

  // Nav Modals
  const [showHowItWorks, setShowHowItWorks] = useState(false);
  const [showFeatures, setShowFeatures] = useState(false);
  const [showSupport, setShowSupport] = useState(false);
  const [showPrivacyPolicy, setShowPrivacyPolicy] = useState(false);

  // Forgot Password States
  const [showForgotPasswordModal, setShowForgotPasswordModal] = useState(false);
  const [forgotStep, setForgotStep] = useState(1);
  const [forgotIdentifier, setForgotIdentifier] = useState('');
  const [forgotOtp, setForgotOtp] = useState('');
  const [forgotQrToken, setForgotQrToken] = useState('');
  const [forgotNewPassword, setForgotNewPassword] = useState('');
  const [forgotLoading, setForgotLoading] = useState(false);
  const [forgotError, setForgotError] = useState(null);
  const [forgotSuccess, setForgotSuccess] = useState(null);

  const [isScanningCamera, setIsScanningCamera] = useState(false);
  const videoRef = React.useRef(null);
  const animFrameRef = React.useRef(null);

  const startCameraScan = async () => {
    setIsScanningCamera(true);
    setForgotError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.setAttribute('playsinline', 'true');
        await videoRef.current.play();
        animFrameRef.current = requestAnimationFrame(tickScan);
      }
    } catch (err) {
      setForgotError('⚠️ Camera Access Error: ' + err.message);
      setIsScanningCamera(false);
    }
  };

  const stopCameraScan = () => {
    setIsScanningCamera(false);
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current);
    }
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject;
      const tracks = stream.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
  };

  const tickScan = () => {
    if (videoRef.current && videoRef.current.readyState === videoRef.current.HAVE_ENOUGH_DATA) {
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const code = jsQR(imageData.data, imageData.width, imageData.height);

      if (code && code.data) {
        setForgotQrToken(code.data);
        setForgotSuccess('✓ Cloxel Security QR Code scanned successfully via Camera!');
        stopCameraScan();
        return;
      }
    }
    animFrameRef.current = requestAnimationFrame(tickScan);
  };

  const handleQrFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setForgotError(null);

    const reader = new FileReader();
    reader.onload = (event) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const code = jsQR(imageData.data, imageData.width, imageData.height);

        if (code && code.data) {
          setForgotQrToken(code.data);
          setForgotSuccess('✓ Cloxel Security QR Code detected & verified from uploaded image!');
        } else {
          setForgotError('⚠️ Could not decode QR Code. Please select a valid Cloxel Security QR Code image.');
        }
      };
      img.src = event.target.result;
    };
    reader.readAsDataURL(file);
  };


  const handleGoogleAuthCallback = async (response) => {
    if (!response || !response.credential) return;
    setForgotLoading(true);
    setForgotError(null);
    try {
      const res = await fetch(`${API_BASE}/api/auth/google-verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          credential: response.credential,
          email_or_mobile: forgotIdentifier
        })
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Google Account Verification failed');
      }

      const verifiedEmail = data.google_verified_email || forgotIdentifier;
      localStorage.setItem('cloxel_user_email', verifiedEmail.toLowerCase());
      localStorage.setItem('last_known_email', verifiedEmail.toLowerCase());

      setForgotSuccess(data.message || `✅ Google Account '${verifiedEmail}' Verified! Security QR Code sent.`);
      setForgotIdentifier(verifiedEmail);
      setForgotStep(2);
    } catch (err) {
      setForgotError(err.message);
    } finally {
      setForgotLoading(false);
    }
  };

  const triggerGoogleVerify = async () => {
    try {
      let clientId = '';
      const res = await fetch(`${API_BASE}/api/auth/google-client-id`);
      if (res.ok) {
        const data = await res.json();
        clientId = data.google_client_id || '';
      }

      if (!clientId || clientId.includes('placeholder')) {
        setForgotError("⚠️ Google OAuth Client ID is not configured on Render. Please add GOOGLE_CLIENT_ID to your Render Environment Variables.");
        return;
      }

      if (window.google?.accounts?.id) {
        window.google.accounts.id.initialize({
          client_id: clientId,
          callback: handleGoogleAuthCallback
        });
        window.google.accounts.id.prompt();
      } else {
        setForgotError("Google Services loading... Please wait 2 seconds and click again.");
      }
    } catch (err) {
      setForgotError("Failed to initialize Google Sign-In: " + err.message);
    }
  };

  useEffect(() => {
    if (showForgotPasswordModal) {
      fetch(`${API_BASE}/api/auth/google-client-id`)
        .then(r => r.json())
        .then(data => {
          if (data.google_client_id && window.google?.accounts?.id && !data.google_client_id.includes('placeholder')) {
            window.google.accounts.id.initialize({
              client_id: data.google_client_id,
              callback: handleGoogleAuthCallback
            });
          }
        }).catch(() => {});
    }
  }, [showForgotPasswordModal]);

  const handleRequestAccountVerify = async (e) => {
    e.preventDefault();
    setForgotError(null);
    setForgotSuccess(null);
    setForgotLoading(true);

    let activeUserId = localStorage.getItem('cloxel_user_id') || '';
    let activeUserEmail = (localStorage.getItem('cloxel_user_email') || '').toLowerCase();
    let activeUserPhone = localStorage.getItem('cloxel_user_phone') || '';

    if (!activeUserId || !activeUserEmail) {
      try {
        const userDataStr = localStorage.getItem('user_data');
        if (userDataStr) {
          const parsed = JSON.parse(userDataStr);
          if (!activeUserId) activeUserId = parsed.internal_id || '';
          if (!activeUserEmail) activeUserEmail = (parsed.email || '').toLowerCase();
          if (!activeUserPhone) activeUserPhone = parsed.phone || '';
        }
      } catch (err) {}
    }

    try {
      const response = await fetch(`${API_BASE}/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email_or_mobile: forgotIdentifier,
          current_session_user_id: activeUserId,
          current_session_user_email: activeUserEmail,
          current_session_user_phone: activeUserPhone
        })
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Failed to verify account');
      }

      setForgotSuccess(data.message || 'Account & Browser session verified! Please upload or scan your Cloxel Security QR Code.');
      setForgotStep(2);
    } catch (err) {
      setForgotError(err.message);
    } finally {
      setForgotLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setForgotError(null);
    setForgotSuccess(null);

    if (!forgotQrToken || !forgotQrToken.trim()) {
      setForgotError('⚠️ Security Error: Please upload your Cloxel Security QR Code image or scan with camera.');
      return;
    }

    setForgotLoading(true);

    let activeUserId = localStorage.getItem('cloxel_user_id') || '';
    let activeUserEmail = (localStorage.getItem('cloxel_user_email') || '').toLowerCase();
    let activeUserPhone = localStorage.getItem('cloxel_user_phone') || '';

    if (!activeUserId || !activeUserEmail) {
      try {
        const userDataStr = localStorage.getItem('user_data');
        if (userDataStr) {
          const parsed = JSON.parse(userDataStr);
          if (!activeUserId) activeUserId = parsed.internal_id || '';
          if (!activeUserEmail) activeUserEmail = (parsed.email || '').toLowerCase();
          if (!activeUserPhone) activeUserPhone = parsed.phone || '';
        }
      } catch (err) {}
    }

    try {
      const response = await fetch(`${API_BASE}/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email_or_mobile: forgotIdentifier,
          new_password: forgotNewPassword,
          qr_token: forgotQrToken,
          current_session_user_id: activeUserId,
          current_session_user_email: activeUserEmail,
          current_session_user_phone: activeUserPhone
        })
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Failed to reset password');
      }

      setForgotSuccess(data.message || 'Password reset successfully!');
      setTimeout(() => {
        setShowForgotPasswordModal(false);
        setIsLogin(true);
        setEmailOrMobile(forgotIdentifier);
        setPassword(forgotNewPassword);
      }, 1800);
    } catch (err) {
      setForgotError(err.message);
    } finally {
      setForgotLoading(false);
    }
  };




  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    const activeBrowserEmail = (localStorage.getItem('cloxel_user_email') || localStorage.getItem('last_known_email') || '').toLowerCase().trim();

    const endpoint = isLogin ? '/login' : '/register';
    const payload = isLogin ? {
      email_or_mobile: emailOrMobile,
      password: password
    } : {
      name: name,
      country: country,
      phone: phone,
      email: email,
      password: password,
      email_or_mobile: email,
      browser_email: activeBrowserEmail || email.toLowerCase()
    };



    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Authentication failed');
      }

      if (data.internal_id) {
        const userEmail = (data.email || (isLogin ? emailOrMobile : email) || '').toLowerCase();
        const userPhone = data.phone || (isLogin ? '' : phone);
        localStorage.setItem('cloxel_user_id', data.internal_id);
        if (userEmail) localStorage.setItem('cloxel_user_email', userEmail);
        if (userPhone) localStorage.setItem('cloxel_user_phone', userPhone);
        localStorage.setItem('user_data', JSON.stringify({
          internal_id: data.internal_id,
          email: userEmail,
          phone: userPhone,
          name: data.name || name
        }));

        onLoginSuccess(data.internal_id, { internal_id: data.internal_id, email: userEmail, phone: userPhone });
      } else {
        throw new Error("No internal ID received");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="landing-container">
      {/* Background Glowing Mesh / Orbs */}
      <div className="glow-orb orb-1"></div>
      <div className="glow-orb orb-2"></div>

      {/* Landing Navbar */}
      <nav className="landing-nav">
        <div className="nav-brand">
          <span className="brand-logo">✦</span> Cloxel <span>AI</span>
        </div>
        <div className="nav-links">
          <button className="nav-link-btn" onClick={() => setShowHowItWorks(true)}>How it works</button>
          <button className="nav-link-btn" onClick={() => setShowFeatures(true)}>Features</button>
          <button className="nav-link-btn" onClick={() => setShowSupport(true)}>Support</button>
          <button className="nav-link-btn" onClick={() => setShowPrivacyPolicy(true)}>Privacy Policy</button>
        </div>
        <div className="nav-actions">
          <button className="btn-nav-login" onClick={() => { setIsLogin(true); setShowAuthModal(true); setError(null); }}>
            Login
          </button>
          <button className="btn-nav-primary" onClick={() => { setIsLogin(false); setShowAuthModal(true); setError(null); }}>
            Get Early Access
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="landing-hero">
        <div className="hero-badge">✨ NEXT-GEN FACELESS VIDEO GENERATOR</div>
        <h1 className="hero-title">
          See your videos come to life <span>before your next move.</span>
        </h1>
        <p className="hero-subtitle">
          AI connects your script, voiceovers, video scenes, and subtitles before you make a move. Fully automated 100% cloud video engine.
        </p>

        <div className="hero-cta-box">
          <button className="btn-hero-cta" onClick={() => { setIsLogin(false); setShowAuthModal(true); setError(null); }}>
            Create Account & Generate Free Video →
          </button>
          <p className="hero-cta-subtext">No credit card required. Instant AI video creation.</p>
        </div>

        {/* Floating Feature Badges */}
        <div className="hero-stats">
          <div className="stat-card">
            <h3>24/7</h3>
            <p>Automated AI Video Processing</p>
          </div>
          <div className="stat-card">
            <h3>100%</h3>
            <p>Cloud Based & Secure Data</p>
          </div>
        </div>
      </header>

      {/* Auth Modal (Overlay) */}
      {showAuthModal && (
        <div className="auth-modal-overlay" onClick={() => setShowAuthModal(false)}>
          <div className="auth-modal-card" onClick={e => e.stopPropagation()}>
            <button className="modal-close-btn" onClick={() => setShowAuthModal(false)}>×</button>
            
            <div className="modal-header" style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100%', marginBottom: '16px' }}>
              <h2 style={{ textAlign: 'center', display: 'block', width: '100%', margin: '0 auto 6px auto' }}>{isLogin ? 'Welcome Back to Cloxel' : 'Create an Account'}</h2>
              <p style={{ textAlign: 'center', display: 'block', width: '100%', margin: '0 auto' }}>{isLogin ? 'Enter your credentials to access your dashboard' : 'Fill in mandatory details to get started'}</p>
            </div>

            {error && <div className="auth-error">{error}</div>}

            <form onSubmit={handleSubmit} className="auth-form">
              {!isLogin && (
                <>
                  <div className="form-group">
                    <label>Full Name *</label>
                    <input 
                      type="text" 
                      placeholder="e.g. Rahul Sharma" 
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      required 
                    />
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                    <div className="form-group">
                      <label>Country *</label>
                      <select value={country} onChange={(e) => setCountry(e.target.value)} required>
                        <option value="India">India</option>
                        <option value="United States">United States</option>
                        <option value="United Kingdom">United Kingdom</option>
                        <option value="Canada">Canada</option>
                        <option value="Australia">Australia</option>
                        <option value="United Arab Emirates">UAE</option>
                        <option value="Germany">Germany</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>

                    <div className="form-group">
                      <label>Phone Number *</label>
                      <input 
                        type="tel" 
                        placeholder="+91 9876543210" 
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        required 
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label>Email Address *</label>
                    <input 
                      type="email" 
                      placeholder="name@example.com" 
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required 
                    />
                  </div>
                </>
              )}

              {isLogin && (
                <div className="form-group">
                  <label>Email Address or Mobile Number *</label>
                  <input 
                    type="text" 
                    placeholder="Enter registered Email or Mobile" 
                    value={emailOrMobile}
                    onChange={(e) => setEmailOrMobile(e.target.value)}
                    required 
                  />
                </div>
              )}

              <div className="form-group">
                <label>Password *</label>
                <input 
                  type="password" 
                  placeholder="Enter secure password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required 
                />
              </div>

              {isLogin && (
                <div style={{ textAlign: 'right', marginTop: '-6px', marginBottom: '14px' }}>
                  <button 
                    type="button" 
                    onClick={() => {
                      setShowForgotPasswordModal(true);
                      setForgotStep(1);
                      setForgotIdentifier(emailOrMobile || '');
                      setForgotOtp('');
                      setForgotNewPassword('');
                      setForgotError(null);
                      setForgotSuccess(null);
                    }} 
                    className="btn-link"
                    style={{ fontSize: '0.85rem', color: '#c084fc' }}
                  >
                    🔑 Forgot Password?
                  </button>
                </div>
              )}


              {!isLogin && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '14px', marginBottom: '16px' }}>
                  <input 
                    type="checkbox" 
                    id="privacy-checkbox" 
                    checked={agreedToPrivacy}
                    onChange={(e) => setAgreedToPrivacy(e.target.checked)}
                    style={{ width: '18px', height: '18px', cursor: 'pointer', accentColor: '#a855f7' }}
                    required
                  />
                  <label htmlFor="privacy-checkbox" style={{ margin: 0, fontSize: '0.85rem', color: '#cbd5e1', cursor: 'pointer', textTransform: 'none', letterSpacing: 'normal' }}>
                    I agree to the <button type="button" onClick={() => setShowPrivacyPolicy(true)} className="btn-link" style={{ textDecoration: 'underline', color: '#c084fc', padding: 0 }}>Privacy Policy & Terms</button> *
                  </label>
                </div>
              )}

              <button 
                type="submit" 
                disabled={isLoading || (!isLogin && !agreedToPrivacy)} 
                className="btn-primary auth-submit"
                style={{ opacity: (!isLogin && !agreedToPrivacy && !isLoading) ? 0.5 : 1, cursor: (!isLogin && !agreedToPrivacy) ? 'not-allowed' : 'pointer' }}
              >
                {isLoading ? 'Processing...' : (isLogin ? 'Login to Dashboard' : 'Create Account')}
              </button>
            </form>

            {!isLogin && (
              <div className="auth-warning">
                <strong>Warning:</strong> Once you set your password, it cannot be changed. For security reasons, do not share your password or email with anyone.
              </div>
            )}

            <div className="auth-switch">
              {isLogin ? "Don't have an account? " : "Already have an account? "}
              <button 
                type="button" 
                onClick={() => { setIsLogin(!isLogin); setError(null); }} 
                className="btn-link"
              >
                {isLogin ? 'Register here' : 'Login here'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Forgot Password Modal */}
      {showForgotPasswordModal && (
        <div className="auth-modal-overlay" onClick={() => setShowForgotPasswordModal(false)}>
          <div className="auth-modal-card" onClick={e => e.stopPropagation()} style={{ maxWidth: '440px' }}>
            <button className="modal-close-btn" onClick={() => setShowForgotPasswordModal(false)}>×</button>
            
            <div className="modal-header" style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100%', marginBottom: '16px' }}>
              <h2 style={{ textAlign: 'center', display: 'block', width: '100%', margin: '0 auto 6px auto' }}>🔑 Reset Password</h2>
              <p style={{ textAlign: 'center', display: 'block', width: '100%', margin: '0 auto', fontSize: '0.88rem' }}>
                {forgotStep === 1 ? 'Enter your registered Email or Mobile Number to receive your Security QR Code' : 'Upload or scan your Security QR Code and set your new password'}
              </p>
            </div>

            {forgotError && <div className="auth-error">{forgotError}</div>}
            {forgotSuccess && (
              <div style={{ background: 'rgba(34, 197, 94, 0.15)', border: '1px solid #22c55e', color: '#4ade80', padding: '10px 14px', borderRadius: '10px', fontSize: '0.85rem', marginBottom: '14px', textAlign: 'center' }}>
                {forgotSuccess}
              </div>
            )}

            {forgotStep === 1 ? (
              <form onSubmit={handleRequestAccountVerify} className="auth-form">
                <div className="form-group">
                  <label>Email Address or Mobile Number *</label>
                  <input 
                    type="text" 
                    placeholder="Enter registered Email or Mobile" 
                    value={forgotIdentifier}
                    onChange={(e) => setForgotIdentifier(e.target.value)}
                    required 
                  />
                </div>
                <button 
                  type="submit" 
                  disabled={forgotLoading} 
                  className="btn-primary auth-submit"
                  style={{ width: '100%', marginTop: '10px' }}
                >
                  {forgotLoading ? 'Verifying Account...' : 'Verify Account →'}
                </button>

                <div style={{ textAlign: 'center', marginTop: '10px', marginBottom: '6px' }}>
                  <span style={{ color: '#94a3b8', fontSize: '0.78rem' }}>— OR —</span>
                </div>

                <button 
                  type="button" 
                  onClick={triggerGoogleVerify}
                  disabled={forgotLoading}
                  style={{
                    width: '100%',
                    background: '#ffffff',
                    color: '#1f2937',
                    border: '1px solid #e5e7eb',
                    borderRadius: '10px',
                    padding: '10px 14px',
                    fontWeight: 'bold',
                    fontSize: '0.88rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
                  }}
                >
                  <svg width="18" height="18" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
                  </svg>
                  🌐 Verify with Google Account (1-Click)
                </button>
              </form>
            ) : (

              <form onSubmit={handleResetPassword} className="auth-form">
                {/* Method 1: Upload QR Image */}
                <div style={{ background: 'rgba(168,85,247,0.1)', border: '1px dashed rgba(168,85,247,0.4)', padding: '14px', borderRadius: '12px', marginBottom: '14px', textAlign: 'center' }}>
                  <label style={{ display: 'block', color: '#c084fc', fontWeight: 'bold', fontSize: '0.85rem', marginBottom: '6px' }}>
                    📷 Upload Cloxel Security QR Code Image *
                  </label>
                  <input 
                    type="file" 
                    accept="image/*"
                    onChange={handleQrFileUpload}
                    style={{ fontSize: '0.8rem', color: '#cbd5e1', cursor: 'pointer' }}
                  />
                </div>

                {/* Method 2: Live Camera Scan */}
                <div style={{ textAlign: 'center', marginBottom: '14px' }}>
                  {!isScanningCamera ? (
                    <button 
                      type="button" 
                      onClick={startCameraScan}
                      style={{ background: 'rgba(56, 189, 248, 0.15)', border: '1px solid #38bdf8', color: '#38bdf8', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontSize: '0.85rem', fontWeight: 'bold' }}
                    >
                      🎥 Scan QR Code with Camera
                    </button>
                  ) : (
                    <div>
                      <video ref={videoRef} style={{ width: '100%', maxHeight: '200px', borderRadius: '8px', border: '2px solid #38bdf8', marginBottom: '8px' }}></video>
                      <button 
                        type="button" 
                        onClick={stopCameraScan}
                        style={{ background: 'rgba(239, 68, 68, 0.2)', border: '1px solid #ef4444', color: '#f87171', padding: '4px 12px', borderRadius: '6px', cursor: 'pointer', fontSize: '0.8rem' }}
                      >
                        Stop Camera Scan
                      </button>
                    </div>
                  )}
                </div>

                {/* QR Credential Verified Status Indicator */}
                <div style={{ textAlign: 'center', marginBottom: '14px' }}>
                  {forgotQrToken ? (
                    <div style={{ background: 'rgba(34, 197, 94, 0.15)', border: '1px solid #22c55e', color: '#4ade80', padding: '8px', borderRadius: '8px', fontSize: '0.8rem', fontWeight: 'bold' }}>
                      ✓ Cryptographic QR Code Credential Loaded & Verified
                    </div>
                  ) : (
                    <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px dashed rgba(239, 68, 68, 0.4)', color: '#fca5a5', padding: '8px', borderRadius: '8px', fontSize: '0.78rem' }}>
                      ⚠️ QR Code Required: Upload QR Image or Scan via Camera above. (Manual typing disabled)
                    </div>
                  )}
                </div>

                <div className="form-group">
                  <label>New Password *</label>
                  <input 
                    type="password" 
                    placeholder="Enter new secure password" 
                    value={forgotNewPassword}
                    onChange={(e) => setForgotNewPassword(e.target.value)}
                    required 
                  />
                </div>

                <button 
                  type="submit" 
                  disabled={forgotLoading || !forgotQrToken} 
                  className="btn-primary auth-submit"
                  style={{ width: '100%', marginTop: '10px', opacity: !forgotQrToken ? 0.5 : 1, cursor: !forgotQrToken ? 'not-allowed' : 'pointer' }}
                >
                  {forgotLoading ? 'Verifying Credentials...' : 'Confirm & Reset Password →'}
                </button>

                <div style={{ textAlign: 'center', marginTop: '12px' }}>
                  <button 
                    type="button" 
                    onClick={() => { setForgotStep(1); setForgotError(null); setForgotSuccess(null); stopCameraScan(); }} 
                    className="btn-link"
                    style={{ fontSize: '0.8rem', color: '#94a3b8' }}
                  >
                    ← Back to Enter Email / Mobile
                  </button>
                </div>
              </form>

            )}

          </div>
        </div>
      )}

      {/* Big Full-Screen Loading Animation Overlay */}
      {isLoading && (
        <div className="pricing-modal-overlay" style={{ zIndex: 5000, background: 'rgba(10, 7, 24, 0.85)', backdropFilter: 'blur(10px)' }}>
          <div style={{ maxWidth: '480px', textAlign: 'center', padding: '20px' }}>
            <lottie-player 
              src="/loding.json" 
              background="transparent" 
              speed="1" 
              style={{ width: '260px', height: '260px', margin: '0 auto', display: 'block' }} 
              loop 
              autoplay
            ></lottie-player>
            <h3 style={{ color: '#ffffff', fontSize: '1.5rem', marginTop: '14px', marginBottom: '8px', fontWeight: '800' }}>
              {isLogin ? 'Logging into Dashboard...' : 'Creating Your Account...'}
            </h3>
            <p style={{ color: '#cbd5e1', fontSize: '0.9rem', margin: 0 }}>
              Please wait a moment while we set up your session.
            </p>
          </div>
        </div>
      )}

      {/* 1. HOW IT WORKS MODAL */}
      {showHowItWorks && (
        <div className="pricing-modal-overlay" onClick={() => setShowHowItWorks(false)} style={{ zIndex: 3000 }}>
          <div className="pricing-modal-card" style={{ maxWidth: '850px', padding: '36px' }} onClick={e => e.stopPropagation()}>
            <button className="sidebar-close-btn" style={{ position: 'absolute', top: '20px', right: '20px', background: 'none', border: 'none', color: '#fff', fontSize: '1.8rem', cursor: 'pointer' }} onClick={() => setShowHowItWorks(false)}>×</button>

            <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100%', marginBottom: '28px' }}>
              <span className="pricing-badge">⚙️ AUTOMATION WORKFLOW GRAPH</span>
              <h2 style={{ color: '#ffffff', fontSize: '2rem', marginTop: '8px', fontWeight: '800', textAlign: 'center', display: 'block', width: '100%', margin: '8px auto 0 auto' }}>
                How Cloxel AI Automation Engine Works
              </h2>
              <p style={{ color: '#94a3b8', fontSize: '0.95rem', textAlign: 'center', display: 'block', width: '100%', margin: '4px auto 0 auto' }}>
                An end-to-end cloud pipeline converting your topics into 60FPS viral videos & auto-publishing.
              </p>
            </div>

            {/* Visual Step-by-step Flow Graph */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px', marginBottom: '28px' }}>
              <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(168,85,247,0.3)', borderRadius: '16px', padding: '20px 16px', textAlign: 'center' }}>
                <div style={{ fontSize: '2rem', marginBottom: '10px' }}>💡 Step 1</div>
                <h4 style={{ color: '#c084fc', marginBottom: '6px' }}>Script Generation</h4>
                <p style={{ color: '#cbd5e1', fontSize: '0.8rem', margin: 0 }}>Gemini AI parses your topic and writes viral scene hooks.</p>
              </div>

              <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(168,85,247,0.3)', borderRadius: '16px', padding: '20px 16px', textAlign: 'center' }}>
                <div style={{ fontSize: '2rem', marginBottom: '10px' }}>🗣️ Step 2</div>
                <h4 style={{ color: '#c084fc', marginBottom: '6px' }}>Madhur Voiceover</h4>
                <p style={{ color: '#cbd5e1', fontSize: '0.8rem', margin: 0 }}>Hyper-realistic Madhur Neural Voice synthesizes crisp speech.</p>
              </div>

              <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(168,85,247,0.3)', borderRadius: '16px', padding: '20px 16px', textAlign: 'center' }}>
                <div style={{ fontSize: '2rem', marginBottom: '10px' }}>🎬 Step 3</div>
                <h4 style={{ color: '#c084fc', marginBottom: '6px' }}>FFmpeg Compositing</h4>
                <p style={{ color: '#cbd5e1', fontSize: '0.8rem', margin: 0 }}>HD stock visuals + auto-animated yellow captions are merged.</p>
              </div>

              <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(168,85,247,0.3)', borderRadius: '16px', padding: '20px 16px', textAlign: 'center' }}>
                <div style={{ fontSize: '2rem', marginBottom: '10px' }}>🚀 Step 4</div>
                <h4 style={{ color: '#c084fc', marginBottom: '6px' }}>Cloud & YouTube</h4>
                <p style={{ color: '#cbd5e1', fontSize: '0.8rem', margin: 0 }}>100% Cloud storage delivery and 1-click YouTube auto-upload.</p>
              </div>
            </div>

            <button className="btn-hero-cta" style={{ width: '100%', padding: '12px' }} onClick={() => setShowHowItWorks(false)}>
              Got It! Close Guide →
            </button>
          </div>
        </div>
      )}

      {/* 2. FEATURES MODAL */}
      {showFeatures && (
        <div className="pricing-modal-overlay" onClick={() => setShowFeatures(false)} style={{ zIndex: 3000 }}>
          <div className="pricing-modal-card" style={{ maxWidth: '850px', padding: '36px' }} onClick={e => e.stopPropagation()}>
            <button className="sidebar-close-btn" style={{ position: 'absolute', top: '20px', right: '20px', background: 'none', border: 'none', color: '#fff', fontSize: '1.8rem', cursor: 'pointer' }} onClick={() => setShowFeatures(false)}>×</button>

            <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100%', marginBottom: '28px' }}>
              <span className="pricing-badge">⚡ CORE CAPABILITIES</span>
              <h2 style={{ color: '#ffffff', fontSize: '2rem', marginTop: '8px', fontWeight: '800', textAlign: 'center', display: 'block', width: '100%', margin: '8px auto 0 auto' }}>
                Cloxel AI Platform Features
              </h2>
              <p style={{ color: '#94a3b8', fontSize: '0.95rem', textAlign: 'center', display: 'block', width: '100%', margin: '4px auto 0 auto' }}>
                Everything you need to automate your YouTube & Shorts content creation.
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px', marginBottom: '28px' }}>
              <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(168,85,247,0.3)', borderRadius: '16px', padding: '20px' }}>
                <h4 style={{ color: '#c084fc', fontSize: '1.1rem', marginBottom: '8px' }}>📱 9:16 Shorts & Reels</h4>
                <p style={{ color: '#cbd5e1', fontSize: '0.85rem', margin: 0 }}>Create vertical viral Shorts with animated yellow subtitles.</p>
              </div>

              <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(168,85,247,0.3)', borderRadius: '16px', padding: '20px' }}>
                <h4 style={{ color: '#c084fc', fontSize: '1.1rem', marginBottom: '8px' }}>🖥️ 16:9 Long YouTube Videos</h4>
                <p style={{ color: '#cbd5e1', fontSize: '0.85rem', margin: 0 }}>Full length landscape videos for long-form documentary channels.</p>
              </div>

              <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(168,85,247,0.3)', borderRadius: '16px', padding: '20px' }}>
                <h4 style={{ color: '#c084fc', fontSize: '1.1rem', marginBottom: '8px' }}>🗣️ Madhur Neural Voice</h4>
                <p style={{ color: '#cbd5e1', fontSize: '0.85rem', margin: 0 }}>Natural human-like Indian voiceover with perfect pronunciation.</p>
              </div>

              <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(168,85,247,0.3)', borderRadius: '16px', padding: '20px' }}>
                <h4 style={{ color: '#c084fc', fontSize: '1.1rem', marginBottom: '8px' }}>📅 30-Day Auto Upload</h4>
                <p style={{ color: '#cbd5e1', fontSize: '0.85rem', margin: 0 }}>Schedule daily automated video generation and YouTube posting.</p>
              </div>
            </div>

            <button className="btn-hero-cta" style={{ width: '100%', padding: '12px' }} onClick={() => setShowFeatures(false)}>
              Explore Features & Start →
            </button>
          </div>
        </div>
      )}

      {/* 3. SUPPORT MODAL */}
      {showSupport && (
        <div className="pricing-modal-overlay" onClick={() => setShowSupport(false)} style={{ zIndex: 3000 }}>
          <div className="pricing-modal-card" style={{ maxWidth: '800px', padding: '36px' }} onClick={e => e.stopPropagation()}>
            <button className="sidebar-close-btn" style={{ position: 'absolute', top: '20px', right: '20px', background: 'none', border: 'none', color: '#fff', fontSize: '1.8rem', cursor: 'pointer' }} onClick={() => setShowSupport(false)}>×</button>

            <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100%', marginBottom: '24px' }}>
              <span className="pricing-badge">💬 24/7 SUPPORT CENTER</span>
              <h2 style={{ color: '#ffffff', fontSize: '2rem', marginTop: '8px', fontWeight: '800', textAlign: 'center', display: 'block', width: '100%', margin: '8px auto 0 auto' }}>
                Cloxel AI Help & Support
              </h2>
              <p style={{ color: '#94a3b8', fontSize: '0.95rem', textAlign: 'center', display: 'block', width: '100%', margin: '4px auto 0 auto' }}>
                Have questions or need assistance? Our support team is here to help you 24/7.
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
              <div style={{ background: 'rgba(255,255,255,0.04)', padding: '20px', borderRadius: '16px', border: '1px solid rgba(168,85,247,0.3)' }}>
                <h4 style={{ color: '#c084fc', marginBottom: '10px' }}>✉️ Direct Email Support</h4>
                <p style={{ color: '#cbd5e1', fontSize: '0.85rem', marginBottom: '8px' }}>Email us anytime for account or payment queries:</p>
                <a href="mailto:support@cloxel.com" style={{ color: '#ec4899', fontWeight: 'bold', fontSize: '0.95rem', display: 'block' }}>support@cloxel.com</a>
                <a href="mailto:contact@zobbly.com" style={{ color: '#a855f7', fontWeight: 'bold', fontSize: '0.85rem', display: 'block', marginTop: '4px' }}>contact@zobbly.com</a>
              </div>

              <div style={{ background: 'rgba(255,255,255,0.04)', padding: '20px', borderRadius: '16px', border: '1px solid rgba(168,85,247,0.3)' }}>
                <h4 style={{ color: '#c084fc', marginBottom: '10px' }}>👤 Founder & Executive Contact</h4>
                <p style={{ color: '#cbd5e1', fontSize: '0.85rem', margin: 0 }}><strong>Founder & CEO:</strong> Akash Raj</p>
                <p style={{ color: '#cbd5e1', fontSize: '0.85rem', marginTop: '4px' }}><strong>Organization:</strong> Cloxel AI Technologies India</p>
                <p style={{ color: '#22c55e', fontSize: '0.8rem', marginTop: '8px', margin: 0 }}>⚡ Guaranteed response within 24 hours.</p>
              </div>
            </div>

            <div style={{ background: 'rgba(0,0,0,0.2)', padding: '20px', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.06)' }}>
              <h4 style={{ color: '#ffffff', marginBottom: '10px' }}>❓ Frequently Asked Questions</h4>
              <ul style={{ color: '#cbd5e1', fontSize: '0.85rem', paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <li><strong>How do I activate my 30-day membership?</strong> Select your desired plan and complete Razorpay checkout. Activation is instant.</li>
                <li><strong>What if I repurchase an active plan?</strong> Your active membership is automatically extended by an additional 30 days.</li>
                <li><strong>Can I auto-upload videos to YouTube?</strong> Yes, connect your YouTube channel from the dashboard panel.</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* 4. OFFICIAL LEGAL PRIVACY POLICY MODAL */}
      {showPrivacyPolicy && (
        <div className="pricing-modal-overlay" onClick={() => setShowPrivacyPolicy(false)} style={{ zIndex: 3000 }}>
          <div className="pricing-modal-card" style={{ maxWidth: '850px', padding: '40px', background: '#0b071a', border: '2px solid rgba(168,85,247,0.5)' }} onClick={e => e.stopPropagation()}>
            <button className="sidebar-close-btn" style={{ position: 'absolute', top: '20px', right: '20px', background: 'none', border: 'none', color: '#fff', fontSize: '1.8rem', cursor: 'pointer' }} onClick={() => setShowPrivacyPolicy(false)}>×</button>

            {/* Official Legal Header */}
            <div style={{ borderBottom: '2px solid rgba(168,85,247,0.3)', paddingBottom: '16px', marginBottom: '24px', textAlign: 'center' }}>
              <div style={{ fontSize: '0.75rem', letterSpacing: '2px', color: '#c084fc', fontWeight: '800', textTransform: 'uppercase' }}>OFFICIAL LEGAL DOCUMENT • REPUBLIC OF INDIA COMPLIANT</div>
              <h2 style={{ color: '#ffffff', fontSize: '1.8rem', margin: '8px 0', fontWeight: '800' }}>
                Privacy Policy & User Terms Document
              </h2>
              <p style={{ color: '#94a3b8', fontSize: '0.82rem' }}>
                Issued by Cloxel AI Technologies India | IT Act 2000 & Digital Personal Data Protection (DPDP) Act 2023 Guidelines
              </p>
            </div>

            {/* Document Body */}
            <div style={{ maxHeight: '50vh', overflowY: 'auto', paddingRight: '12px', fontSize: '0.85rem', color: '#cbd5e1', lineHeight: '1.65', display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <section>
                <h4 style={{ color: '#ffffff', fontSize: '1rem', marginBottom: '4px' }}>1. Advanced Binary Security Architecture (SMS OTP Replacement)</h4>
                <p>To eliminate SIM-swapping vulnerabilities and SMS interception delays, Cloxel AI utilizes high-level <strong>Binary Cryptographic Hash Architecture & SHA-256 Protocol Encryption</strong>, which is exponentially more powerful, secure, and resilient than traditional OTP systems. Account authorization relies directly on binary token handshakes and encrypted credentials.</p>
              </section>

              <section style={{ background: 'rgba(239, 68, 68, 0.08)', padding: '14px', borderRadius: '12px', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
                <h4 style={{ color: '#f87171', fontSize: '1rem', marginBottom: '4px' }}>2. User Password Disclosure & Zero Responsibility Disclaimer</h4>
                <p style={{ color: '#fca5a5' }}>
                  While Cloxel AI implements state-of-the-art Binary Encryption, <strong>users remain 100% solely and completely responsible for maintaining strict password secrecy</strong>.
                </p>
                <p style={{ color: '#fca5a5', marginTop: '8px' }}>
                  <strong>Password Sharing Exclusion:</strong> If a user voluntarily or accidentally discloses, shares, or reveals their account password or email credentials to any third party, friend, or external service, <strong>Cloxel AI, its website, infrastructure, servers, and Founder Akash Raj hold ZERO legal liability, financial responsibility, or obligation for any resulting account breach, data loss, or unauthorized access.</strong>
                </p>
              </section>

              <section>
                <h4 style={{ color: '#ffffff', fontSize: '1rem', marginBottom: '4px' }}>3. Third-Party Integrations & YouTube API Services</h4>
                <p>By connecting YouTube channels, users agree to YouTube Terms of Service and Google Privacy Policy. Cloxel AI accesses OAuth tokens strictly for automated video publishing initiated by the user.</p>
              </section>

              <section>
                <h4 style={{ color: '#ffffff', fontSize: '1rem', marginBottom: '4px' }}>4. Official Company & Contact Details</h4>
                <p>For legal inquiries, formal notices, or privacy data requests, contact our legal office:</p>
                <ul style={{ paddingLeft: '20px', marginTop: '6px' }}>
                  <li><strong>Founder & Managing Director:</strong> Akash Raj</li>
                  <li><strong>Official Entity:</strong> Cloxel AI Technologies India</li>
                  <li><strong>Primary Contact Email:</strong> contact@zobbly.com</li>
                  <li><strong>Support Desk Email:</strong> support@cloxel.com</li>
                </ul>
              </section>
            </div>

            {/* Official Signature & Seal Block */}
            <div style={{ marginTop: '24px', paddingTop: '16px', borderTop: '2px dashed rgba(168,85,247,0.3)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <p style={{ color: '#94a3b8', fontSize: '0.75rem', margin: 0 }}>AUTHORIZATION SEAL</p>
                <div style={{ background: 'rgba(168,85,247,0.15)', border: '1px solid #a855f7', color: '#c084fc', padding: '6px 12px', borderRadius: '8px', fontSize: '0.75rem', fontWeight: 'bold', display: 'inline-block', marginTop: '4px' }}>
                  ✓ VERIFIED LEGAL POLICY DOC • REPUBLIC OF INDIA
                </div>
              </div>

              <div style={{ textAlign: 'right' }}>
                <p style={{ color: '#c084fc', fontFamily: 'cursive', fontSize: '1.4rem', margin: 0, fontWeight: 'bold' }}>
                  Akash Raj
                </p>
                <p style={{ color: '#ffffff', fontSize: '0.8rem', margin: 0, fontWeight: 'bold' }}>Akash Raj</p>
                <p style={{ color: '#94a3b8', fontSize: '0.75rem', margin: 0 }}>Founder & CEO, Cloxel AI</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Auth;
