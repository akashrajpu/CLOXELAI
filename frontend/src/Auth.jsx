import React, { useState, useEffect, useRef } from 'react';
import jsQR from 'jsqr';
import lottie from 'lottie-web';
import heroAnimationData from './lottie_hero.json';
import Guide from './Guide';
import Features from './Features';
import Support from './Support';

const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';

function LottieHeroAnimation() {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;
    containerRef.current.innerHTML = '';
    const anim = lottie.loadAnimation({
      container: containerRef.current,
      renderer: 'svg',
      loop: true,
      autoplay: true,
      animationData: heroAnimationData,
    });

    return () => {
      anim.destroy();
    };
  }, []);

  return (
    <div 
      ref={containerRef} 
      className="lottie-hero-wrapper" 
    />
  );
}

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
  const [forgotConfirmPassword, setForgotConfirmPassword] = useState('');
  const [qrRetryCount, setQrRetryCount] = useState(0);
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

  const resetForgotModal = () => {
    setShowForgotPasswordModal(false);
    setForgotStep(1);
    setForgotIdentifier('');
    setForgotQrToken('');
    setForgotNewPassword('');
    setForgotConfirmPassword('');
    setQrRetryCount(0);
    setForgotError(null);
    setForgotSuccess(null);
    stopCameraScan();
  };

  const verifyQrTokenWithServer = async (qrData) => {
    setForgotLoading(true);
    setForgotError(null);
    setForgotSuccess(null);
    try {
      const response = await fetch(`${API_BASE}/verify-reset-qr`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email_or_mobile: forgotIdentifier,
          qr_token: qrData
        })
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Invalid Security QR Code');
      }

      // Valid QR Token!
      setForgotQrToken(qrData);
      setForgotSuccess('✅ Security QR Code Verified! Step 3: Please set your new password.');
      setForgotStep(3);
    } catch (err) {
      setForgotQrToken('');
      setQrRetryCount(prevCount => {
        const newRetry = prevCount + 1;
        if (newRetry >= 2) {
          setForgotError(`❌ Security Alert: Failed QR verification 2 times! Request terminated for safety.`);
          setTimeout(() => {
            resetForgotModal();
          }, 2200);
        } else {
          setForgotError(`⚠️ Warning: Invalid Security QR Code! The scanned QR code does not belong to '${forgotIdentifier}'. Please upload/scan the correct QR code (Attempt 1/2).`);
        }
        return newRetry;
      });
    } finally {
      setForgotLoading(false);
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
        stopCameraScan();
        verifyQrTokenWithServer(code.data);
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
          verifyQrTokenWithServer(code.data);
        } else {
          setForgotError('⚠️ Could not decode QR Code. Please select a valid Cloxel Security QR Code image.');
        }
      };
      img.src = event.target.result;
    };
    reader.readAsDataURL(file);
  };


  const handleRequestAccountVerify = async (e) => {
    e.preventDefault();
    setForgotError(null);
    setForgotSuccess(null);
    setForgotLoading(true);

    try {
      const response = await fetch(`${API_BASE}/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email_or_mobile: forgotIdentifier
        })
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Failed to verify account');
      }

      setForgotSuccess(data.message || 'Account verified! Security QR Code sent to your email.');
      setForgotStep(2);
      setQrRetryCount(0);
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

    if (!forgotNewPassword || !forgotConfirmPassword) {
      setForgotError('⚠️ Mandatory Field: Both New Password and Confirm Password are required!');
      return;
    }

    if (forgotNewPassword.length < 6) {
      setForgotError('⚠️ Password Length Error: New password must be at least 6 characters long!');
      return;
    }

    if (forgotNewPassword !== forgotConfirmPassword) {
      setForgotError('⚠️ Password Mismatch: New Password and Confirm Password do not match!');
      return;
    }

    if (!forgotQrToken) {
      setForgotError('⚠️ Security Error: Security QR Code not verified. Please scan/upload your QR code first.');
      setForgotStep(2);
      return;
    }

    setForgotLoading(true);

    try {
      const response = await fetch(`${API_BASE}/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email_or_mobile: forgotIdentifier,
          new_password: forgotNewPassword,
          qr_token: forgotQrToken
        })
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Failed to reset password');
      }

      setForgotSuccess('✅ Password reset successfully! Redirecting to login...');
      setTimeout(() => {
        resetForgotModal();
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

    if (!isLogin) {
      const cleanPhone = phone.replace(/\D/g, '');
      if (cleanPhone.length !== 10) {
        setError('⚠️ Registration Failed: Mobile Number must be exactly 10 digits (e.g. 9876543210)!');
        return;
      }
      const emailFormat = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
      if (!emailFormat.test(email.trim())) {
        setError('⚠️ Registration Failed: Please enter a valid Email ID (e.g. name@domain.com)!');
        return;
      }
    }

    setIsLoading(true);

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
      email_or_mobile: email
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
        {/* Floating Left Side Lottie Animation */}
        <div className="hero-lottie-side-left">
          <LottieHeroAnimation />
        </div>

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
        <div className="auth-modal-overlay" onClick={resetForgotModal}>
          <div className="auth-modal-card" onClick={e => e.stopPropagation()} style={{ maxWidth: '440px' }}>
            <button className="modal-close-btn" onClick={resetForgotModal}>×</button>
            
            <div className="modal-header" style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100%', marginBottom: '16px' }}>
              <h2 style={{ textAlign: 'center', display: 'block', width: '100%', margin: '0 auto 6px auto' }}>
                {forgotStep === 1 ? '🔐 Step 1: Account Verification' : forgotStep === 2 ? '📷 Step 2: Verify Security QR Code' : '🔑 Step 3: Set New Password'}
              </h2>
              <p style={{ textAlign: 'center', display: 'block', width: '100%', margin: '0 auto', fontSize: '0.85rem', color: '#cbd5e1' }}>
                {forgotStep === 1 && 'Enter your registered Email or Mobile Number to verify account.'}
                {forgotStep === 2 && 'Upload or scan your official Cloxel Security QR Code (received during registration).'}
                {forgotStep === 3 && 'Enter and confirm your new password below.'}
              </p>
            </div>

            {forgotError && <div className="auth-error" style={{ whiteSpace: 'pre-line' }}>{forgotError}</div>}
            {forgotSuccess && (
              <div style={{ background: 'rgba(34, 197, 94, 0.15)', border: '1px solid #22c55e', color: '#4ade80', padding: '10px 14px', borderRadius: '10px', fontSize: '0.85rem', marginBottom: '14px', textAlign: 'center' }}>
                {forgotSuccess}
              </div>
            )}

            {/* STEP 1: Enter Email or Mobile */}
            {forgotStep === 1 && (
              <form onSubmit={handleRequestAccountVerify} className="auth-form">
                <div className="form-group">
                  <label>Registered Email Address or Mobile Number *</label>
                  <input 
                    type="text" 
                    placeholder="e.g. user@example.com or 9876543210" 
                    value={forgotIdentifier}
                    onChange={(e) => setForgotIdentifier(e.target.value)}
                    required 
                  />
                </div>
                <button 
                  type="submit" 
                  disabled={forgotLoading || !forgotIdentifier.trim()} 
                  className="btn-primary auth-submit"
                  style={{ width: '100%', marginTop: '10px' }}
                >
                  {forgotLoading ? 'Verifying Account...' : 'Verify Account & Continue →'}
                </button>
              </form>
            )}

            {/* STEP 2: Scan / Upload QR Code */}
            {forgotStep === 2 && (
              <div className="auth-form">
                {/* Method 1: Upload QR Image */}
                <div style={{ background: 'rgba(168,85,247,0.1)', border: '1px dashed rgba(168,85,247,0.4)', padding: '16px', borderRadius: '12px', marginBottom: '14px', textAlign: 'center' }}>
                  <label style={{ display: 'block', color: '#c084fc', fontWeight: 'bold', fontSize: '0.88rem', marginBottom: '6px' }}>
                    📁 Upload Cloxel Security QR Code Image *
                  </label>
                  <input 
                    type="file" 
                    accept="image/*"
                    onChange={handleQrFileUpload}
                    disabled={forgotLoading}
                    style={{ fontSize: '0.8rem', color: '#cbd5e1', cursor: 'pointer', margin: '0 auto' }}
                  />
                </div>

                {/* Method 2: Live Camera Scan */}
                <div style={{ textAlign: 'center', marginBottom: '14px' }}>
                  {!isScanningCamera ? (
                    <button 
                      type="button" 
                      onClick={startCameraScan}
                      disabled={forgotLoading}
                      style={{ background: 'rgba(56, 189, 248, 0.15)', border: '1px solid #38bdf8', color: '#38bdf8', padding: '10px 18px', borderRadius: '8px', cursor: 'pointer', fontSize: '0.85rem', fontWeight: 'bold', width: '100%' }}
                    >
                      🎥 Scan QR Code with Camera
                    </button>
                  ) : (
                    <div>
                      <video ref={videoRef} style={{ width: '100%', maxHeight: '200px', borderRadius: '8px', border: '2px solid #38bdf8', marginBottom: '8px' }}></video>
                      <button 
                        type="button" 
                        onClick={stopCameraScan}
                        style={{ background: 'rgba(239, 68, 68, 0.2)', border: '1px solid #ef4444', color: '#f87171', padding: '6px 14px', borderRadius: '6px', cursor: 'pointer', fontSize: '0.8rem' }}
                      >
                        Stop Camera Scan
                      </button>
                    </div>
                  )}
                </div>

                <div style={{ textAlign: 'center', marginTop: '14px' }}>
                  <button 
                    type="button" 
                    onClick={() => { setForgotStep(1); setForgotError(null); setForgotSuccess(null); stopCameraScan(); }} 
                    className="btn-link"
                    style={{ fontSize: '0.8rem', color: '#94a3b8' }}
                  >
                    ← Back to Enter Email / Mobile
                  </button>
                </div>
              </div>
            )}

            {/* STEP 3: Set New Password & Confirm Password */}
            {forgotStep === 3 && (
              <form onSubmit={handleResetPassword} className="auth-form">
                <div className="form-group" style={{ marginBottom: '12px' }}>
                  <label>New Password *</label>
                  <input 
                    type="password" 
                    placeholder="Enter new password (min. 6 characters)" 
                    value={forgotNewPassword}
                    onChange={(e) => setForgotNewPassword(e.target.value)}
                    required 
                  />
                </div>

                <div className="form-group" style={{ marginBottom: '14px' }}>
                  <label>Confirm New Password *</label>
                  <input 
                    type="password" 
                    placeholder="Re-enter new password to confirm" 
                    value={forgotConfirmPassword}
                    onChange={(e) => setForgotConfirmPassword(e.target.value)}
                    required 
                  />
                </div>

                <button 
                  type="submit" 
                  disabled={forgotLoading || !forgotNewPassword || !forgotConfirmPassword} 
                  className="btn-primary auth-submit"
                  style={{ width: '100%', marginTop: '10px' }}
                >
                  {forgotLoading ? 'Updating Password...' : 'Confirm & Set New Password →'}
                </button>

                <div style={{ textAlign: 'center', marginTop: '12px' }}>
                  <button 
                    type="button" 
                    onClick={() => { setForgotStep(2); setForgotError(null); setForgotSuccess(null); }} 
                    className="btn-link"
                    style={{ fontSize: '0.8rem', color: '#94a3b8' }}
                  >
                    ← Back to QR Code Verification
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
          <div style={{ maxWidth: '480px', textAlign: 'center', padding: '20px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <lottie-player 
              src="/loding.json" 
              background="transparent" 
              speed="1" 
              style={{ width: '260px', height: '260px', margin: '0 auto', display: 'block' }} 
              loop 
              autoplay
            ></lottie-player>
            <h3 style={{ color: '#ffffff', fontSize: '1.5rem', marginTop: '14px', marginBottom: '8px', fontWeight: '800', textAlign: 'center', display: 'block', width: '100%' }}>
              {isLogin ? 'Logging into Dashboard...' : 'Creating Your Account...'}
            </h3>
            <p style={{ color: '#cbd5e1', fontSize: '0.9rem', margin: 0, textAlign: 'center', display: 'block', width: '100%' }}>
              Please wait a moment while we set up your session.
            </p>
          </div>
        </div>
      )}

      {/* 1. HOW IT WORKS MODAL */}
      {showHowItWorks && (
        <Guide onClose={() => setShowHowItWorks(false)} />
      )}

      {/* 2. FEATURES MODAL */}
      {showFeatures && (
        <Features onClose={() => setShowFeatures(false)} />
      )}

      {/* 3. SUPPORT MODAL */}
      {showSupport && (
        <Support onClose={() => setShowSupport(false)} />
      )}

      {/* 4. OFFICIAL LEGAL PRIVACY POLICY MODAL */}
      {showPrivacyPolicy && (
        <div className="pricing-modal-overlay" onClick={() => setShowPrivacyPolicy(false)} style={{ zIndex: 3000 }}>
          <div className="pricing-modal-card" style={{ maxWidth: '950px', padding: 0, background: 'transparent', border: 'none', overflow: 'hidden' }} onClick={e => e.stopPropagation()}>
            <button className="sidebar-close-btn" style={{ position: 'absolute', top: '-40px', right: '0px', background: 'rgba(0,0,0,0.5)', border: '1px solid rgba(255,255,255,0.2)', color: '#fff', fontSize: '1.8rem', cursor: 'pointer', borderRadius: '50%', width: '36px', height: '36px', display: 'flex', alignItems: 'center', justifyContent: 'center' }} onClick={() => setShowPrivacyPolicy(false)}>×</button>
            <img src="/privacy_policy_doc.jpg" alt="Official Privacy Policy Document" style={{ width: '100%', height: 'auto', display: 'block', borderRadius: '24px', border: '2px solid rgba(168,85,247,0.5)', boxShadow: '0 20px 50px rgba(0,0,0,0.8)' }} />
          </div>
        </div>
      )}
    </div>
  );
}

export default Auth;
