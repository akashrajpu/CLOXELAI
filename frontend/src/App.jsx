import React, { useState, useEffect } from 'react';
import Auth from './Auth';
import YouTubeIntegration from './YouTubeIntegration';

const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';

const CATEGORIES = [
  '🎲 Random / All Categories',
  '🤖 AI & Technology',
  '🌌 Space & Astronomy',
  '🦁 Nature & Wildlife',
  '🏛️ History & Ancient Mysteries',
  '💰 Wealth & Finance',
  '🏋️ Fitness & Health',
  '🎨 Cartoon & Animation',
  '👻 Horror & Paranormal',
  '🎮 Gaming & Esports',
  '🍕 Food & Cooking',
  '🔥 Motivation & Success',
  '🎬 Movie Recaps & Reviews',
  '💡 Life Hacks & Science Facts',
  '🧠 Philosophy & Psychology',
  '💼 Business & Startups',
  '🕵️ True Crime & Mystery',
  '📱 Tech Gadgets & Unboxing',
  '🔱 Mythology & Legends',
  '✈️ Travel & Adventure',
  '🚗 Luxury Cars & Supercars',
  '⚽ Sports & Athletics',
  '👗 Fashion & Lifestyle',
  '🎶 Music & Pop Culture',
  '🧪 Physics & Chemistry Wonders',
  '🐶 Pets & Animals',
  '🧘 Meditation & Mindfulness',
  '📖 Book Summaries & Literature',
  '🚀 Future Tech & Sci-Fi',
  '🌐 World News & Geopolitics',
  '🛠️ DIY & Crafts',
  '✍️ Custom Category (Type Below)'
];

function CustomSelect({ value, onChange, options }) {
  const [isOpen, setIsOpen] = useState(false);
  const isPastel = typeof document !== 'undefined' && document.body.classList.contains('theme-pastel');

  const selectedOption = options.find(opt => (typeof opt === 'object' ? opt.value : opt) === value);
  const selectedLabel = selectedOption 
    ? (typeof selectedOption === 'object' ? selectedOption.label : selectedOption) 
    : value;
  const selectedFontFamily = selectedOption && typeof selectedOption === 'object' ? selectedOption.fontFamily : undefined;

  return (
    <div className="custom-select-container" style={{ position: 'relative', width: '100%' }}>
      <div 
        className="custom-select-trigger" 
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: '100%',
          padding: '0.85rem 1.1rem',
          background: isPastel 
            ? (isOpen ? 'rgba(255, 255, 255, 0.98)' : 'rgba(255, 255, 255, 0.94)') 
            : (isOpen ? 'rgba(24, 18, 55, 0.95)' : 'rgba(15, 23, 42, 0.7)'),
          border: isPastel 
            ? '2px solid #9333ea' 
            : (isOpen ? '2px solid #c084fc' : '2px solid rgba(168, 85, 247, 0.4)'),
          borderRadius: '20px',
          color: isPastel ? '#1e1b4b' : '#ffffff',
          fontSize: '0.95rem',
          fontWeight: '700',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: 'pointer',
          boxShadow: isPastel 
            ? '0 4px 15px rgba(147, 51, 234, 0.12)' 
            : (isOpen ? '0 0 0 3px rgba(192, 132, 252, 0.35), 0 8px 25px rgba(0,0,0,0.5)' : 'inset 0 2px 4px rgba(0,0,0,0.3)'),
          transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)'
        }}
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: '8px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontFamily: selectedFontFamily || 'inherit' }}>
          {selectedLabel}
        </span>
        <span style={{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.25s ease', color: isPastel ? '#7e22ce' : '#c084fc', fontSize: '0.8rem', fontWeight: 'bold' }}>
          ▼
        </span>
      </div>

      {isOpen && (
        <>
          <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 998 }} onClick={() => setIsOpen(false)} />
          <div 
            className="custom-select-dropdown"
            style={{
              position: 'absolute',
              top: 'calc(100% + 6px)',
              left: 0,
              width: '100%',
              maxHeight: '260px',
              overflowY: 'auto',
              background: isPastel ? 'rgba(255, 255, 255, 0.98)' : 'rgba(19, 13, 42, 0.96)',
              backdropFilter: 'blur(20px)',
              WebkitBackdropFilter: 'blur(20px)',
              border: isPastel ? '2px solid #9333ea' : '2px solid rgba(168, 85, 247, 0.45)',
              borderRadius: '20px',
              boxShadow: isPastel ? '0 15px 40px rgba(147, 51, 234, 0.2)' : '0 15px 40px rgba(0, 0, 0, 0.7), 0 0 20px rgba(168, 85, 247, 0.25)',
              zIndex: 999,
              padding: '6px'
            }}
          >
            {options.map((opt, idx) => {
              const optValue = typeof opt === 'object' ? opt.value : opt;
              const optLabel = typeof opt === 'object' ? opt.label : opt;
              const optFontFamily = typeof opt === 'object' ? opt.fontFamily : undefined;
              const isSelected = optValue === value;

              return (
                <div 
                  key={idx}
                  onClick={() => {
                    onChange(optValue);
                    setIsOpen(false);
                  }}
                  style={{
                    padding: '10px 14px',
                    borderRadius: '12px',
                    margin: '2px 0',
                    cursor: 'pointer',
                    fontSize: '1rem',
                    fontWeight: isSelected ? '800' : '600',
                    fontFamily: optFontFamily || 'inherit',
                    color: isSelected 
                      ? (isPastel ? '#581c87' : '#ffffff') 
                      : (isPastel ? '#334155' : '#cbd5e1'),
                    background: isSelected 
                      ? (isPastel ? 'linear-gradient(135deg, rgba(168, 85, 247, 0.25) 0%, rgba(217, 70, 239, 0.2) 100%)' : 'linear-gradient(135deg, rgba(168, 85, 247, 0.4) 0%, rgba(6, 182, 212, 0.3) 100%)') 
                      : 'transparent',
                    border: isSelected ? (isPastel ? '1px solid #c084fc' : '1px solid rgba(192, 132, 252, 0.4)') : '1px solid transparent',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    transition: 'all 0.15s ease'
                  }}
                  onMouseEnter={(e) => {
                    if (!isSelected) {
                      e.currentTarget.style.background = isPastel ? 'rgba(168, 85, 247, 0.12)' : 'rgba(255, 255, 255, 0.08)';
                      e.currentTarget.style.color = isPastel ? '#1e1b4b' : '#ffffff';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isSelected) {
                      e.currentTarget.style.background = 'transparent';
                      e.currentTarget.style.color = isPastel ? '#334155' : '#cbd5e1';
                    }
                  }}
                >
                  <span style={{ fontFamily: optFontFamily || 'inherit' }}>{optLabel}</span>
                  {isSelected && <span style={{ color: isPastel ? '#7e22ce' : '#c084fc', fontWeight: 'bold' }}>✓</span>}
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}

function App() {
  const [ytStatus, setYtStatus] = useState(null);
  const [theme, setTheme] = useState(() => localStorage.getItem('cloxel_theme') || 'pastel');
  const [topic, setTopic] = useState('Space Exploration');
  const [duration, setDuration] = useState(20);
  const [videoType, setVideoType] = useState('short'); // 'short' or 'long'
  const [fullScript, setFullScript] = useState('');

  useEffect(() => {
    document.body.className = theme === 'pastel' ? 'theme-pastel' : 'theme-dark';
    localStorage.setItem('cloxel_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'pastel' ? 'dark' : 'pastel'));
  };
  
  // Customization Settings
  const [fontName, setFontName] = useState('Arial.ttf');
  const [fontList, setFontList] = useState(['Arial.ttf', 'AgentOrange.ttf', 'BetsyFlanagan.ttf', 'CarbonBlock.ttf', 'Cartoon Blocks.ttf', 'GrapeSoda.ttf', 'HighLevel.ttf', 'RaceFlow.ttf']);
  const [fontSize, setFontSize] = useState(220);
  const [fontColor, setFontColor] = useState('yellow');
  const [voiceId, setVoiceId] = useState('hi-IN-MadhurNeural');
  const [bgMusic, setBgMusic] = useState('cool.mp3');
  const [bgMusicList, setBgMusicList] = useState(['cool.mp3', 'cool1.mp3', 'cool2.mp3', 'cool3.mp3', 'cool4.mp3', 'cool5.mp3', 'random', 'none']);

  const [category, setCategory] = useState('🎲 Random / All Categories');
  const [customCategory, setCustomCategory] = useState('');

  // Ultra Photo Motion Engine Settings
  const [generationMode, setGenerationMode] = useState('ultra'); // 'ultra' or 'standard'
  const [aspectRatio, setAspectRatio] = useState('16:9'); // '16:9' default (1920x1080)
  const [filterStyle, setFilterStyle] = useState('warm_epic'); // 'warm_epic', 'vintage_parchment', 'dramatic_cinematic', 'none'

  const [scenes, setScenes] = useState([
    { text: '', keyword: '' },
    { text: '', keyword: '' }
  ]);
  
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [cloudinaryUrl, setCloudinaryUrl] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [isGeneratingScript, setIsGeneratingScript] = useState(false);
  const [history, setHistory] = useState(() => {
    try {
      const savedUserId = localStorage.getItem('cloxel_user_id');
      if (savedUserId) {
        const cached = localStorage.getItem(`user_history_cache_${savedUserId}`);
        if (cached) {
          const parsed = JSON.parse(cached);
          if (Array.isArray(parsed)) return parsed;
        }
      }
    } catch (e) {}
    return [];
  });
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [showPricingModal, setShowPricingModal] = useState(false);
  const [showPaymentSuccessModal, setShowPaymentSuccessModal] = useState(false);
  const [showAutoUploadModal, setShowAutoUploadModal] = useState(false);
  const [showStopScheduleWarningModal, setShowStopScheduleWarningModal] = useState(false);
  const [customAlert, setCustomAlert] = useState(null);
  const [playingHistoryVideo, setPlayingHistoryVideo] = useState(null);

  const triggerAlert = (title, message, icon = '⚠️', type = 'info', onConfirm = null, confirmText = 'OK', cancelText = 'Cancel') => {
    setCustomAlert({
      title,
      message,
      icon,
      type,
      onConfirm,
      confirmText,
      cancelText
    });
  };

  const [selectedPlan, setSelectedPlan] = useState('long'); // 'short', 'long', 'combo'
  const [subStatus, setSubStatus] = useState(() => {
    const defaultSub = { free_demo_count: 2, has_active_subscription: false, plan_type: 'none' };
    try {
      const savedUserId = localStorage.getItem('cloxel_user_id');
      if (savedUserId) {
        const cached = localStorage.getItem(`user_sub_cache_${savedUserId}`);
        if (cached) {
          const parsed = JSON.parse(cached);
          if (parsed && typeof parsed === 'object') return parsed;
        }
      }
    } catch (e) {}
    return defaultSub;
  });

  const openPricingModal = (plan = 'long') => {
    if (plan && typeof setSelectedPlan === 'function') {
      setSelectedPlan(plan);
    }
    setIsSidebarOpen(false);
    setShowAutoUploadModal(false);
    setShowStopScheduleWarningModal(false);
    setCustomAlert(null);
    setShowPricingModal(true);
  };

  const [isPaymentProcessing, setIsPaymentProcessing] = useState(false);
  const [enableCheckbox, setEnableCheckbox] = useState(false);
  const [autoSchedule, setAutoSchedule] = useState({
    schedule_enabled: false,
    short_auto_topic: true,
    short_topic: 'Space Exploration, AI Innovations',
    short_category: '🎲 Random / All Categories',
    short_voice: 'hi-IN-MadhurNeural',
    short_font: 'Arial.ttf',
    short_color: 'yellow',
    short_duration: 30,
    short_time: '10:00',
    short_language: 'hi',
    long_auto_topic: true,
    long_topic: 'Space Exploration, AI Technology',
    long_category: '🎲 Random / All Categories',
    long_voice: 'hi-IN-MadhurNeural',
    long_font: 'Arial.ttf',
    long_color: 'yellow',
    long_duration: 60,
    long_time: '18:00',
    long_language: 'hi',
    topics: 'Space Exploration, AI Innovations, Ancient Mysteries, Wealth & Finance',
    total_videos_created: 0,
    remaining_plan_videos: 60,
    next_scheduled_run: 'Short: Daily at 10:00 | Long: Daily at 18:00'
  });
  
  const [userId, setUserId] = useState(() => {
    try {
      const stored = localStorage.getItem('cloxel_user_id');
      if (stored && stored !== 'null' && stored !== 'undefined' && stored.trim() !== '') {
        return stored.trim();
      }
    } catch(e) {}
    return null;
  });
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
  const [isSavingSchedule, setIsSavingSchedule] = useState(false);
  const [isUploadingPic, setIsUploadingPic] = useState(false);

  const fetchWithTimeout = async (url, options = {}, timeoutMs = 12000) => {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(url, { ...options, signal: controller.signal });
      clearTimeout(timer);
      return response;
    } catch (err) {
      clearTimeout(timer);
      throw err;
    }
  };

  const fetchSubscriptionStatus = async () => {
    if (!userId) return;
    try {
      const response = await fetch(`${API_BASE}/user-subscription/${userId}`);
      if (response.ok) {
        const data = await response.json();
        setSubStatus(data);
        try {
          localStorage.setItem(`user_sub_cache_${userId}`, JSON.stringify(data));
        } catch (e_cache) {}
      }
    } catch (e) {
      console.error("Failed to fetch subscription status:", e);
    }
  };

  const fetchAutoSchedule = async () => {
    if (!userId) return;
    try {
      const res = await fetchWithTimeout(`${API_BASE}/get-auto-schedule/${userId}`);
      if (res.ok) {
        const data = await res.json();
        setAutoSchedule(data);
        setEnableCheckbox(!!data.schedule_enabled);
      }
    } catch (e) {
      console.error("Failed to fetch auto schedule:", e);
    }
  };

  const fetchHistory = async () => {
    if (!userId) return;
    try {
      const response = await fetch(`${API_BASE}/history/${userId}`);
      if (response.ok) {
        const data = await response.json();
        const newHist = data.history || [];
        setHistory(newHist);
        try {
          localStorage.setItem(`user_history_cache_${userId}`, JSON.stringify(newHist));
        } catch (e_hist) {}
      }
    } catch (e) {
      console.error("Failed to fetch history:", e);
    }
  };

  const fetchBgMusicAndFonts = async () => {
    try {
      const resM = await fetchWithTimeout(`${API_BASE}/bg-music-list`);
      if (resM.ok) {
        const dataM = await resM.json();
        if (dataM.music_tracks && dataM.music_tracks.length > 0) {
          setBgMusicList(['cool.mp3', 'cool1.mp3', 'cool2.mp3', 'cool3.mp3', 'cool4.mp3', 'cool5.mp3', 'random', 'none', ...dataM.music_tracks.filter(t => !['cool.mp3', 'cool1.mp3', 'cool2.mp3', 'cool3.mp3', 'cool4.mp3', 'cool5.mp3'].includes(t))]);
        }
      }
      const resF = await fetch(`${API_BASE}/fonts-list`);
      if (resF.ok) {
        const dataF = await resF.json();
        if (dataF.fonts && dataF.fonts.length > 0) {
          setFontList(dataF.fonts);
        }
      }
    } catch (e) {
      console.error("Failed to fetch bg music or fonts:", e);
    }
  };

  const fetchYoutubeStatus = async () => {
    if (!userId) return;
    try {
      const res = await fetchWithTimeout(`${API_BASE}/youtube/status/${userId}`);
      if (res.ok) {
        const data = await res.json();
        setYtStatus(data);
      }
    } catch (e) {
      console.error("Failed to fetch YouTube status:", e);
    }
  };

  useEffect(() => {
    Promise.allSettled([
      fetchBgMusicAndFonts(),
      userId ? fetchHistory() : Promise.resolve(),
      userId ? fetchSubscriptionStatus() : Promise.resolve(),
      userId ? fetchAutoSchedule() : Promise.resolve(),
      userId ? fetchYoutubeStatus() : Promise.resolve()
    ]);
  }, [userId]);

  const handleSaveAutoSchedule = async (explicitEnabledState = null) => {
    if (!userId || isSavingSchedule) return;
    if (!subStatus.has_active_subscription) {
      triggerAlert(
        "Active Membership Required",
        "Auto-Schedule & YouTube Auto-Upload are exclusive to active paid members. Please upgrade your plan to activate auto-scheduling!",
        "🔒",
        "danger",
        () => {
          setShowAutoUploadModal(false);
          setShowPricingModal(true);
        },
        "Upgrade Membership Plan →"
      );
      return;
    }

    const finalEnabledState = explicitEnabledState !== null ? explicitEnabledState : enableCheckbox;

    if (finalEnabledState) {
      // 1. Checkbox Check
      if (!enableCheckbox) {
        triggerAlert(
          "Checkbox Selection Required",
          "Please check the \"ENABLE DAILY AUTOMATED AI VIDEO GENERATION & YOUTUBE UPLOAD\" checkbox first before clicking the Start button!",
          "☑️",
          "info"
        );
        return;
      }

      // 2. YouTube Connection Check
      if (!ytStatus || !ytStatus.linked) {
        triggerAlert(
          "🔴 YouTube Channel Not Connected",
          "Your YouTube channel is NOT connected yet!\n\nPlease open the ☰ Menu Drawer and link your YouTube account first before starting the Auto-Publishing Engine.",
          "📺",
          "danger",
          () => {
            setShowAutoUploadModal(false);
            setIsSidebarOpen(true);
          },
          "🔗 Open ☰ Menu & Connect YouTube →"
        );
        return;
      }
    }

    setIsSavingSchedule(true);
    try {
      const res = await fetch(`${API_BASE}/save-auto-schedule`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          internal_id: userId,
          schedule_enabled: finalEnabledState,
          
          short_auto_topic: autoSchedule.short_auto_topic !== false,
          short_topic: autoSchedule.short_topic || 'Space Exploration, AI Innovations',
          short_category: autoSchedule.short_category || 'Random',
          short_voice: autoSchedule.short_voice || 'hi-IN-MadhurNeural',
          short_font: autoSchedule.short_font || 'Arial.ttf',
          short_color: autoSchedule.short_color || 'yellow',
          short_duration: autoSchedule.short_duration || 20,
          short_time: autoSchedule.short_time || '10:00',
          short_language: 'hi',

          long_auto_topic: autoSchedule.long_auto_topic !== false,
          long_topic: autoSchedule.long_topic || 'Space Exploration, AI Technology',
          long_category: autoSchedule.long_category || 'Random',
          long_voice: autoSchedule.long_voice || 'hi-IN-MadhurNeural',
          long_font: autoSchedule.long_font || 'Arial.ttf',
          long_color: autoSchedule.long_color || 'yellow',
          long_duration: autoSchedule.long_duration || 60,
          long_time: autoSchedule.long_time || '18:00',
          long_language: 'hi',

          ultra_enabled: autoSchedule.ultra_enabled || false,
          ultra_auto_topic: autoSchedule.ultra_auto_topic !== false,
          ultra_topic: autoSchedule.ultra_topic || 'History of Ancient Warriors',
          ultra_category: autoSchedule.ultra_category || 'Random',
          ultra_aspect_ratio: autoSchedule.ultra_aspect_ratio || '16:9',
          ultra_voice: autoSchedule.ultra_voice || 'hi-IN-MadhurNeural',
          ultra_font: autoSchedule.ultra_font || 'Arial.ttf',
          ultra_color: autoSchedule.ultra_color || 'yellow',
          ultra_duration: autoSchedule.ultra_duration || 60,
          ultra_time: autoSchedule.ultra_time || '21:00',
          ultra_language: 'hi'
        })
      });
      if (res.ok) {
        await fetchAutoSchedule();
        setShowAutoUploadModal(false);

        if (finalEnabledState) {
          triggerAlert(
            "⚡ Auto-Publishing Engine ACTIVE & SAVED IN DB",
            "Saved to backend database! Your account is now active for daily 1-hour pre-rendering & automated YouTube publishing.",
            "🟢",
            "success"
          );
        } else {
          triggerAlert(
            "🛑 Auto-Publishing Engine STOPPED",
            "Auto-publishing has been stopped and saved in your profile database.",
            "🛑",
            "info"
          );
        }
      } else {
        const errData = await res.json();
        triggerAlert("Error", errData.detail || "Failed to save schedule settings.", "⚠️", "danger");
      }
    } catch (err) {
      triggerAlert("Error", "Error saving auto schedule.", "⚠️", "danger");
    } finally {
      setIsSavingSchedule(false);
    }
  };

  const handleLoginSuccess = (id, userObj = {}) => {
    setUserId(id);
    localStorage.setItem('cloxel_user_id', id);
    if (userObj.email) localStorage.setItem('cloxel_user_email', userObj.email.toLowerCase());
    if (userObj.phone) localStorage.setItem('cloxel_user_phone', userObj.phone);
  };

  const handleLogout = () => {
    try {
      localStorage.clear();
      sessionStorage.clear();
      localStorage.removeItem('cloxel_user_id');
      localStorage.removeItem('user_data');
    } catch (e) {
      console.error("Error clearing browser storage:", e);
    }

    setUserId(null);
    setHistory([]);
    setFullScript('');
    setTopic('Space Exploration');
    setJobId(null);
    setJobStatus(null);
    setCloudinaryUrl(null);
    setDownloadUrl(null);
    setPlayingHistoryVideo(null);
    setIsSidebarOpen(false);
    setShowPricingModal(false);
    setShowAutoUploadModal(false);
    setShowStopScheduleWarningModal(false);
    setCustomAlert(null);
    setSubStatus({ free_demo_count: 2, has_active_subscription: false, plan_type: 'none' });

    window.location.href = window.location.origin + window.location.pathname;
  };

  // Update scenes array when duration changes
  useEffect(() => {
    // Check for youtube success or error param
    const params = new URLSearchParams(window.location.search);
    if (params.get('yt_success')) {
      alert('YouTube Account successfully linked!');
      window.history.replaceState({}, document.title, window.location.pathname);
    } else if (params.get('yt_error')) {
      alert(`YouTube Link Error: ${params.get('yt_error')}`);
      window.history.replaceState({}, document.title, window.location.pathname);
    }

    const chunkCount = Math.max(1, Math.floor(duration / 10));
    setScenes(prev => {
      if (prev.length === chunkCount) return prev;
      const newScenes = [...prev];
      if (newScenes.length < chunkCount) {
        while (newScenes.length < chunkCount) {
          newScenes.push({ text: '', keyword: '' });
        }
      } else {
        newScenes.length = chunkCount;
      }
      return newScenes;
    });
  }, [duration]);

  const handleSceneChange = (index, field, value) => {
    const newScenes = [...scenes];
    newScenes[index][field] = value;
    setScenes(newScenes);
  };

  const isLimitExhausted = !subStatus.has_active_subscription && (subStatus.free_demo_count !== undefined ? subStatus.free_demo_count <= 0 : false);

  const handleAutoGenerate = async () => {
    if (isLimitExhausted) {
      triggerAlert(
        "🔒 Free Demo Limit Reached!",
        "You have completed your 2 free demo videos & scripts. Please upgrade to a Premium Plan to generate unlimited scripts & videos!",
        "🔒",
        "warning",
        () => openPricingModal('long'),
        "Upgrade to Premium 🚀"
      );
      openPricingModal('long');
      return;
    }
    setIsGeneratingScript(true);
    const finalCategory = (category || '').includes('Custom Category') ? (customCategory || 'Random') : category;
    try {
      const response = await fetch(`${API_BASE}/generate-script`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          topic: topic,
          category: finalCategory,
          duration_seconds: duration,
          video_type: videoType
        })
      });
      const data = await response.json();
      if (data.full_script) {
        setFullScript(data.full_script);
      }
      if (data.scenes && data.scenes.length > 0) {
        setScenes(data.scenes);
        if (!data.full_script) {
          const combinedScript = data.scenes.map(s => s.text).join(" ");
          setFullScript(combinedScript);
        }
      }
    } catch (error) {
      console.error("Script generation error:", error);
    } finally {
      setIsGeneratingScript(false);
    }
  };

  const handleGenerateVideo = async () => {
    if (isGeneratingVideo || jobStatus === 'processing' || jobStatus === 'initializing') return;
    if (isLimitExhausted) {
      triggerAlert(
        "🔒 Free Demo Limit Reached!",
        "You have completed your 2 free demo videos. Please upgrade to a Premium Plan to generate unlimited videos!",
        "🔒",
        "warning",
        () => openPricingModal('long'),
        "Upgrade to Premium 🚀"
      );
      openPricingModal('long');
      return;
    }

    setIsGeneratingVideo(true);
    setJobStatus('initializing');
    setJobId(null);
    setCloudinaryUrl(null);
    setDownloadUrl(null);
    
    try {
      const response = await fetch(`${API_BASE}/generate-custom-video`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: topic,
          category: (category || '').includes('Custom Category') ? (customCategory || 'Random') : category,
          scenes: scenes,
          font_name: fontName,
          font_color: fontColor,
          font_size: parseInt(fontSize),
          voice_id: voiceId,
          language: 'hi',
          video_type: videoType,
          full_script: fullScript,
          bg_music: bgMusic,
          user_id: userId,
          mode: generationMode,
          aspect_ratio: aspectRatio,
          filter_style: filterStyle
        })
      });
      const data = await response.json();
      if (data.job_id) {
        setJobId(data.job_id);
        setJobStatus('processing');
        pollStatus(data.job_id);
      } else if (data.detail) {
        setIsGeneratingVideo(false);
        setJobStatus(null);
        triggerAlert("⚠️ Daily Limit Reached", data.detail, "⚠️", "warning");
      } else {
        setIsGeneratingVideo(false);
        setJobStatus(null);
        triggerAlert("⚠️ Generation Error", "Failed to start video generation. Please check your account subscription or login status.", "⚠️", "warning");
      }
    } catch (error) {
      setIsGeneratingVideo(false);
      setJobStatus(null);
      triggerAlert("⚠️ Network Error", "Failed to connect to video generator backend.", "⚠️", "warning");
    }
  };

  const pollStatus = async (id) => {
    let notFoundStrikes = 0;
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE}/status/${id}`);
        if (!response.ok) return;
        const data = await response.json();
        
        if (data.status === 'not_found') {
          notFoundStrikes++;
          if (notFoundStrikes >= 3) {
            clearInterval(interval);
            setJobStatus(null);
            setIsGeneratingVideo(false);
            triggerAlert(
              "⚠️ Server Status Notice",
              "Video rendering status was not found on the server. Please click Generate Video again.",
              "⚠️",
              "warning"
            );
          }
          return;
        }

        notFoundStrikes = 0;
        setJobStatus(data.status);
        
        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(interval);
          setIsGeneratingVideo(false);

          if (data.status === 'completed') {
            if (data.cloudinary_url) {
              setCloudinaryUrl(data.cloudinary_url);
            }
            setDownloadUrl(`${API_BASE}/download/${id}`);
            if (userId) {
              fetchHistory();
              fetchSubscriptionStatus();
            }
          } else if (data.status === 'failed') {
            setJobStatus(null);
            triggerAlert(
              "⚠️ Generation Error",
              data.error || "Video generation encountered an error. Please try again.",
              "⚠️",
              "warning"
            );
          }
        }
      } catch (e) {
        console.error("Poll status error:", e);
      }
    }, 2000);
  };

  const handleProfilePicUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onloadend = async () => {
      const base64Image = reader.result;
      setSubStatus(prev => ({ ...prev, profile_pic: base64Image }));
      try {
        await fetch(`${API_BASE}/update-profile-pic`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ internal_id: userId, profile_pic: base64Image })
        });
      } catch (err) {
        console.error("Profile picture upload error:", err);
      }
    };
    reader.readAsDataURL(file);
  };

  const PLAN_RANKS = { short: 1, long: 2, combo: 3 };
  const PLAN_NAMES = { ultra: 'Ultra Cinematic (₹20)', short: 'Short Starter (₹50)', long: 'Long Master (₹100)', combo: 'Pro Combo (₹119)' };

  const executeCheckout = async (planType) => {
    try {
      setIsPaymentProcessing(true);
      const response = await fetch(`${API_BASE}/create-razorpay-order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ internal_id: userId, plan_type: planType })
      });
      const orderData = await response.json();
      setIsPaymentProcessing(false);
      
      if (!response.ok) {
        triggerAlert("Order Creation Failed", orderData.detail || "Failed to create order.", "❌", "danger");
        return;
      }

      // Real Razorpay Popup Checkout Integration
      if (window.Razorpay && orderData.key_id) {
        const options = {
          key: orderData.key_id,
          amount: orderData.amount,
          currency: orderData.currency,
          name: "Cloxel AI Video Generator",
          description: `30 Days Membership (${planType.toUpperCase()})`,
          order_id: orderData.order_id,
          prefill: {
            name: "Cloxel User",
            email: "user@cloxel.com",
            contact: "9876543210"
          },
          handler: async function (res) {
            // Verify payment on backend ONLY when payment actually succeeds!
            const verifyResp = await fetch(`${API_BASE}/verify-razorpay-payment`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                internal_id: userId,
                plan_type: planType,
                razorpay_order_id: res.razorpay_order_id,
                razorpay_payment_id: res.razorpay_payment_id,
                razorpay_signature: res.razorpay_signature
              })
            });
            
            const verifyData = await verifyResp.json();
            if (verifyResp.ok) {
              setShowPricingModal(false);
              setShowPaymentSuccessModal(true);
              fetchSubscriptionStatus();
              fetchAutoSchedule();
            } else {
              triggerAlert("Payment Verification Failed", verifyData.detail || "Payment Verification Failed.", "❌", "danger");
            }
          },
          modal: {
            ondismiss: function () {
              triggerAlert("Payment Cancelled", "Transaction was cancelled.", "ℹ️", "info");
            }
          }
        };

        const rzp = new window.Razorpay(options);
        rzp.open();
      } else {
        triggerAlert("Razorpay Notice", "Live Razorpay API Keys are not configured in Cloxel Server Environment. Please configure RAZORPAY_KEY_ID & RAZORPAY_KEY_SECRET.", "⚠️", "info");
      }
    } catch (err) {
      setIsPaymentProcessing(false);
      triggerAlert("Payment Error", "Payment processing error. Please try again.", "❌", "danger");
    }
  };

  const handleBuyPlan = async (planType) => {
    if (planType === 'ultra') {
      if (subStatus.has_active_ultra_subscription) {
        triggerAlert(
          "Ultra Mode Subscription Active",
          `⚠️ You already have an active Ultra Cinematic subscription.\n\nUltra Mode subscription can only be purchased once a month and will be available to renew after your current 30-day plan expires.`,
          "⚠️",
          "danger"
        );
        return;
      }
      executeCheckout('ultra');
      return;
    }
    if (subStatus.has_active_subscription) {
      const currRank = PLAN_RANKS[subStatus.plan_type] || 0;
      const newRank = PLAN_RANKS[planType] || 0;

      if (newRank < currRank) {
        triggerAlert(
          "Plan Downgrade Restricted",
          `You currently have an active high-tier plan (${PLAN_NAMES[subStatus.plan_type] || subStatus.plan_type.toUpperCase()}).\n\nYou cannot downgrade to ${PLAN_NAMES[planType]} until your current high-tier plan expires on ${subStatus.expires_at ? new Date(subStatus.expires_at).toLocaleDateString() : 'expiry'}.`,
          "⚠️",
          "danger"
        );
        return;
      } else if (newRank > currRank) {
        triggerAlert(
          "Upgrade Membership Notice",
          `Upgrading to ${PLAN_NAMES[planType]} will replace your current ${PLAN_NAMES[subStatus.plan_type]} plan and start a fresh 30-day high-tier subscription immediately!`,
          "🚀",
          "info",
          () => executeCheckout(planType),
          `Upgrade Now (₹${planType === 'combo' ? 119 : 100})`,
          "Cancel"
        );
        return;
      } else {
        triggerAlert(
          "Same Plan Duration Stacking",
          `You already have an active ${PLAN_NAMES[planType]} plan.\n\nPurchasing this plan again will stack and extend your active membership duration by an additional +30 days!`,
          "🔄",
          "info",
          () => executeCheckout(planType),
          "Proceed to Stack (+30 Days)",
          "Cancel"
        );
        return;
      }
    }
    executeCheckout(planType);
  };

  if (!userId) {
    return <Auth onLoginSuccess={handleLoginSuccess} />;
  }

  const isAutoScheduleActive = !!(autoSchedule?.schedule_enabled && ytStatus?.linked);

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-left">
          <button className="hamburger-btn" onClick={() => { setIsSidebarOpen(true); fetchSubscriptionStatus(); fetchYoutubeStatus(); }} title="Open Menu">
            ☰
          </button>
          <h1>Cloxel <span>AI Video Generator</span></h1>
        </div>
        <div className="header-right" style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          {isAutoScheduleActive && (
            <div style={{ background: 'rgba(34, 197, 94, 0.15)', border: '1px solid rgba(34, 197, 94, 0.4)', color: '#4ade80', padding: '5px 12px', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '6px', boxShadow: '0 0 12px rgba(34, 197, 94, 0.3)' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#22c55e', boxShadow: '0 0 8px #22c55e' }}></span>
              <span>Auto-Upload: 🟢 ACTIVE</span>
            </div>
          )}
          {/* Animated Toggle Switch */}
          <div 
            onClick={toggleTheme}
            title={theme === 'pastel' ? 'Pastel Theme Active (Click to switch to Dark)' : 'Dark Theme Active (Click to switch to Pastel)'}
            style={{
              width: '54px',
              height: '28px',
              borderRadius: '9999px',
              padding: '2px',
              cursor: 'pointer',
              background: theme === 'pastel' ? 'linear-gradient(135deg, #a855f7 0%, #d946ef 100%)' : '#1e1b4b',
              border: theme === 'pastel' ? '2px solid #7e22ce' : '2px solid #38bdf8',
              boxShadow: theme === 'pastel' ? '0 0 10px rgba(168, 85, 247, 0.4)' : '0 0 10px rgba(56, 189, 248, 0.4)',
              display: 'flex',
              alignItems: 'center',
              position: 'relative',
              transition: 'all 0.3s ease'
            }}
          >
            <div 
              style={{
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                background: '#ffffff',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.7rem',
                transform: theme === 'pastel' ? 'translateX(26px)' : 'translateX(0px)',
                transition: 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
              }}
            >
              {theme === 'pastel' ? '✨' : '🌙'}
            </div>
          </div>
          <button className="btn-upgrade-pill" onClick={() => openPricingModal()}>
            💎 Upgrade Plan
          </button>
          <button className="profile-pill-btn" onClick={() => { setIsSidebarOpen(true); fetchSubscriptionStatus(); fetchYoutubeStatus(); }} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {subStatus?.profile_pic ? (
              <img src={subStatus.profile_pic} alt="User" style={{ width: '24px', height: '24px', borderRadius: '50%', objectFit: 'cover' }} />
            ) : (
              <span>👤</span>
            )}
            <span>{subStatus?.name ? subStatus.name.split(' ')[0] : 'Account'}</span>
          </button>
        </div>
      </header>

      <div className="dashboard">
        <main className="panel">
          <h2>🎬 Script & Content Editor</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label>Video Type</label>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button 
                  className={`button ${videoType === 'short' ? 'primary' : 'secondary'}`}
                  onClick={() => {
                    setVideoType('short');
                    if (duration > 55) setDuration(30);
                  }}
                  style={{ 
                    flex: 1, 
                    padding: '12px 10px',
                    background: videoType === 'short' ? 'linear-gradient(135deg, #a855f7 0%, #7e22ce 100%)' : 'rgba(255, 255, 255, 0.05)',
                    border: videoType === 'short' ? '1px solid #c084fc' : '1px solid rgba(255, 255, 255, 0.12)',
                    color: '#ffffff',
                    fontWeight: '800',
                    borderRadius: '14px',
                    boxShadow: videoType === 'short' ? '0 4px 18px rgba(168, 85, 247, 0.45)' : 'none',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '6px',
                    fontSize: '0.9rem'
                  }}
                >📱 Short</button>
                <button 
                  className={`button ${videoType === 'long' ? 'primary' : 'secondary'}`}
                  onClick={() => {
                    setVideoType('long');
                    if (duration < 20) setDuration(60);
                  }}
                  style={{ 
                    flex: 1, 
                    padding: '12px 10px',
                    background: videoType === 'long' ? 'linear-gradient(135deg, #06b6d4 0%, #0284c7 100%)' : 'rgba(255, 255, 255, 0.05)',
                    border: videoType === 'long' ? '1px solid #38bdf8' : '1px solid rgba(255, 255, 255, 0.12)',
                    color: '#ffffff',
                    fontWeight: '800',
                    borderRadius: '14px',
                    boxShadow: videoType === 'long' ? '0 4px 18px rgba(6, 182, 212, 0.45)' : 'none',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '6px',
                    fontSize: '0.9rem'
                  }}
                >🖥️ Long</button>
                <button 
                  className={`button ${videoType === 'ultra' ? 'primary' : 'secondary'}`}
                  onClick={() => {
                    setVideoType('ultra');
                    if (duration < 20) setDuration(60);
                  }}
                  style={{ 
                    flex: 1, 
                    padding: '12px 10px',
                    background: videoType === 'ultra' ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' : 'rgba(255, 255, 255, 0.05)',
                    border: videoType === 'ultra' ? '1px solid #fbbf24' : '1px solid rgba(255, 255, 255, 0.12)',
                    color: '#ffffff',
                    fontWeight: '800',
                    borderRadius: '14px',
                    boxShadow: videoType === 'ultra' ? '0 4px 18px rgba(245, 158, 11, 0.45)' : 'none',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '6px',
                    fontSize: '0.9rem'
                  }}
                >⚡ Ultra</button>
              </div>
            </div>
            <div className="form-group">
              <label>Target Duration</label>
              <CustomSelect 
                value={duration} 
                onChange={(val) => setDuration(Number(val))}
                options={videoType === 'short' ? [
                  { value: 10, label: '⏱️ 10 Seconds' },
                  { value: 20, label: '⏱️ 20 Seconds' },
                  { value: 30, label: '⏱️ 30 Seconds' },
                  { value: 45, label: '⏱️ 45 Seconds' },
                  { value: 55, label: '⏱️ 55 Seconds' }
                ] : [
                  { value: 20, label: '⏱️ 20 Seconds' },
                  { value: 30, label: '⏱️ 30 Seconds' },
                  { value: 60, label: '⏱️ 1 Minute' },
                  { value: 120, label: '⏱️ 2 Minutes' },
                  { value: 180, label: '⏱️ 3 Minutes' },
                  { value: 300, label: '⏱️ 5 Minutes' }
                ]}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label>Main Topic</label>
              <input 
                type="text" 
                value={topic} 
                onChange={e => setTopic(e.target.value)} 
                placeholder="e.g. History of AI, Space Exploration"
              />
            </div>

            <div className="form-group">
              <label>Category / Niche (30+ Categories)</label>
              <CustomSelect 
                value={category} 
                onChange={(val) => setCategory(val)}
                options={CATEGORIES}
              />
            </div>
          </div>

          {category === '✍️ Custom Category (Type Below)' && (
            <div className="form-group">
              <label>Custom Category / Niche Name</label>
              <input 
                type="text" 
                value={customCategory} 
                onChange={e => setCustomCategory(e.target.value)} 
                placeholder="Type your custom niche (e.g. Cyberpunk Anime, Ancient Rome)"
              />
            </div>
          )}

          <div className="form-group">
            <button 
              className="button" 
              onClick={handleAutoGenerate}
              disabled={isGeneratingScript}
              style={{ 
                width: '100%', 
                marginBottom: '1.5rem', 
                background: isLimitExhausted ? 'linear-gradient(135deg, #ef4444 0%, #f97316 100%)' : 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%)', 
                color: 'white',
                border: 'none',
                borderRadius: '14px',
                padding: '13px 20px',
                fontWeight: '800',
                fontSize: '0.98rem',
                boxShadow: isLimitExhausted ? '0 6px 22px rgba(239, 68, 68, 0.5)' : '0 6px 22px rgba(59, 130, 246, 0.45)',
                cursor: 'pointer'
              }}
            >
              {isGeneratingScript 
                ? 'Generating Script via Cloxel AI Engine...' 
                : (isLimitExhausted ? '🔒 Free 2 Limit Exhausted (Click to Upgrade)' : '✨ Auto-Generate Script via AI')}
            </button>
          </div>

          {(videoType === 'long' || videoType === 'ultra') ? (
            <div className="form-group">
              <label>{videoType === 'ultra' ? '⚡ Ultra Mode Script (Multi-Character / Cinematic Script)' : 'Full Video Script (AI generated or custom)'}</label>
              <textarea 
                rows={8}
                value={fullScript}
                onChange={e => setFullScript(e.target.value)}
                placeholder={videoType === 'ultra' ? 'Paste or write your Ultra Cinematic Multi-Character script here...' : 'Paste or write your full video script here. Our smart AI will automatically split it into matching scenes and generate appropriate background visuals.'}
              />
            </div>
          ) : (
            <div className="scenes-list">
              {scenes.map((scene, index) => (
                <div key={index} className="scene-card" style={{ borderLeft: '4px solid var(--primary)', paddingLeft: '1rem', marginBottom: '1.5rem' }}>
                  <h4 style={{ color: '#a855f7', marginBottom: '0.5rem' }}>Scene {index + 1} ({index * 10}s - {(index + 1) * 10}s)</h4>
                  <div className="form-group">
                    <label>Script Chunk</label>
                    <textarea 
                      rows={2}
                      value={scene.text}
                      onChange={e => handleSceneChange(index, 'text', e.target.value)}
                      placeholder="Enter script text for this part..."
                    />
                  </div>
                  <div className="form-group">
                    <label>Video Search Keyword</label>
                    <input 
                      type="text"
                      value={scene.keyword}
                      onChange={e => handleSceneChange(index, 'keyword', e.target.value)}
                      placeholder="e.g. galaxy stars"
                    />
                  </div>
                </div>
              ))}
            </div>
          )}

        </main>

        <aside className="panel">
          <h2>⚙️ Video Settings</h2>

          <div className="form-group" style={{ marginBottom: '1.2rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: '700', color: '#c084fc' }}>
              <span>✨ Engine Generation Mode</span>
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginTop: '6px' }}>
              <button
                type="button"
                onClick={() => setGenerationMode('ultra')}
                style={{
                  padding: '10px 12px',
                  borderRadius: '12px',
                  border: generationMode === 'ultra' ? '2px solid #c084fc' : '1px solid rgba(255,255,255,0.1)',
                  background: generationMode === 'ultra' ? 'rgba(192, 132, 252, 0.25)' : 'rgba(15, 23, 42, 0.6)',
                  color: generationMode === 'ultra' ? '#ffffff' : '#94a3b8',
                  fontSize: '0.82rem',
                  fontWeight: '700',
                  cursor: 'pointer',
                  textAlign: 'center',
                  boxShadow: generationMode === 'ultra' ? '0 0 15px rgba(192, 132, 252, 0.4)' : 'none',
                  transition: 'all 0.2s ease'
                }}
              >
                ✨ Ultra Photo Motion
              </button>
              <button
                type="button"
                onClick={() => setGenerationMode('standard')}
                style={{
                  padding: '10px 12px',
                  borderRadius: '12px',
                  border: generationMode === 'standard' ? '2px solid #c084fc' : '1px solid rgba(255,255,255,0.1)',
                  background: generationMode === 'standard' ? 'rgba(192, 132, 252, 0.25)' : 'rgba(15, 23, 42, 0.6)',
                  color: generationMode === 'standard' ? '#ffffff' : '#94a3b8',
                  fontSize: '0.82rem',
                  fontWeight: '700',
                  cursor: 'pointer',
                  textAlign: 'center',
                  transition: 'all 0.2s ease'
                }}
              >
                🎬 Standard Stock Video
              </button>
            </div>
          </div>

          <div className="form-group" style={{ marginBottom: '1.2rem' }}>
            <label style={{ fontWeight: '700', color: '#e2e8f0' }}>📐 Aspect Ratio</label>
            <CustomSelect 
              value={aspectRatio} 
              onChange={(val) => setAspectRatio(val)}
              options={[
                { value: '16:9', label: '📺 16:9 Landscape HD (1920×1080)' },
                { value: '9:16', label: '📱 9:16 Vertical HD (1080×1920)' },
                { value: '1:1', label: '🔳 1:1 Square HD (1080×1080)' }
              ]}
            />
          </div>

          <div className="form-group" style={{ marginBottom: '1.2rem' }}>
            <label style={{ fontWeight: '700', color: '#e2e8f0' }}>🎨 Cinematic Filter & Style</label>
            <CustomSelect 
              value={filterStyle} 
              onChange={(val) => setFilterStyle(val)}
              options={[
                { value: 'warm_epic', label: '🟡 Warm Epic (Maharana Pratap / Historic / Warrior)' },
                { value: 'vintage_parchment', label: '📜 Vintage Parchment (Sepia Canvas)' },
                { value: 'dramatic_cinematic', label: '🎬 Dramatic Cinematic (Teal-Orange Movie Grade)' },
                { value: 'none', label: '⚪ Standard / Original Colors' }
              ]}
            />
          </div>
          
          <div className="form-group">
            <label>AI Voice</label>
            <CustomSelect 
              value={voiceId} 
              onChange={(val) => setVoiceId(val)}
              options={[
                { value: 'hi-IN-MadhurNeural', label: '♂️ Male (Hindi)' },
                { value: 'hi-IN-SwaraNeural', label: '♀️ Female (Hindi)' },
                { value: 'en-US-GuyNeural', label: '♂️ Male (English)' },
                { value: 'en-US-JennyNeural', label: '♀️ Female (English)' }
              ]}
            />
          </div>

          <div className="form-group">
            <label>Font Family (Visual Preview)</label>
            <CustomSelect 
              value={fontName} 
              onChange={(val) => setFontName(val)}
              options={fontList.map(f => {
                const fontClean = f.replace(/\.[^/.]+$/, "");
                return {
                  value: f,
                  label: fontClean,
                  fontFamily: `'${fontClean}', Montserrat, Poppins, Arial, sans-serif`
                };
              })}
            />
          </div>
          
          <div className="form-group">
            <label>🎵 Background Music Track</label>
            <CustomSelect 
              value={bgMusic} 
              onChange={(val) => setBgMusic(val)}
              options={bgMusicList.map(m => ({ 
                value: m, 
                label: m === 'random' ? '🎲 Random Background Music' : (m === 'none' ? '🚫 No Background Music' : `🎵 ${m}`) 
              }))}
            />
          </div>

          <div className="form-group">
            <label>Font Size</label>
            <input 
              type="number" 
              value={fontSize} 
              onChange={e => setFontSize(e.target.value)} 
            />
          </div>

          <div className="form-group">
            <label style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Subtitle Highlight Color</span>
              <span style={{ 
                fontSize: '0.75rem', 
                padding: '2px 10px', 
                borderRadius: '8px', 
                background: fontColor, 
                color: ['#FFFFFF', 'yellow', 'cyan', '#00FF00', '#FFD700', '#34D399'].includes(fontColor) ? '#000000' : '#FFFFFF',
                fontWeight: '800',
                boxShadow: `0 0 12px ${fontColor}`
              }}>
                PREVIEW
              </span>
            </label>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(6, 1fr)', 
              gap: '8px', 
              background: 'rgba(15, 23, 42, 0.6)', 
              padding: '12px', 
              borderRadius: '16px', 
              border: '1px solid rgba(168, 85, 247, 0.35)',
              marginTop: '6px'
            }}>
              {[
                { value: 'yellow', hex: '#FFFF00', name: 'Yellow' },
                { value: '#00FF00', hex: '#00FF00', name: 'Neon Green' },
                { value: '#FF00FF', hex: '#FF00FF', name: 'Magenta' },
                { value: 'cyan', hex: '#00FFFF', name: 'Cyan' },
                { value: '#FF3333', hex: '#FF3333', name: 'Flame Red' },
                { value: '#FF9900', hex: '#FF9900', name: 'Electric Orange' },
                { value: '#A855F7', hex: '#A855F7', name: 'Violet' },
                { value: '#00BFFF', hex: '#00BFFF', name: 'Sky Blue' },
                { value: '#FFFFFF', hex: '#FFFFFF', name: 'White' },
                { value: '#FFD700', hex: '#FFD700', name: 'Gold' },
                { value: '#34D399', hex: '#34D399', name: 'Mint' },
                { value: '#EC4899', hex: '#EC4899', name: 'Hot Pink' }
              ].map((item) => {
                const isSelected = fontColor === item.value;
                return (
                  <button
                    key={item.value}
                    type="button"
                    onClick={() => setFontColor(item.value)}
                    title={item.name}
                    style={{
                      height: '34px',
                      borderRadius: '10px',
                      background: item.hex,
                      border: isSelected ? '3px solid #ffffff' : '1px solid rgba(255, 255, 255, 0.15)',
                      boxShadow: isSelected ? `0 0 16px ${item.hex}, inset 0 0 4px rgba(0,0,0,0.5)` : '0 2px 6px rgba(0,0,0,0.4)',
                      cursor: 'pointer',
                      transform: isSelected ? 'scale(1.12)' : 'scale(1)',
                      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    {isSelected && (
                      <span style={{ 
                        color: ['#FFFFFF', 'yellow', 'cyan', '#00FF00', '#FFD700', '#34D399'].includes(item.value) ? '#000000' : '#FFFFFF', 
                        fontWeight: '900', 
                        fontSize: '0.85rem' 
                      }}>
                        ✓
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          <button 
            type="button" 
            className="btn-primary" 
            onClick={handleGenerateVideo}
            disabled={isGeneratingVideo || jobStatus === 'processing' || jobStatus === 'initializing'}
            style={{ 
              marginTop: '2rem',
              background: (isGeneratingVideo || jobStatus === 'processing' || jobStatus === 'initializing')
                ? 'linear-gradient(135deg, #4b5563 0%, #374151 100%)'
                : (isLimitExhausted ? 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)' : 'linear-gradient(135deg, #a855f7 0%, #c084fc 50%, #06b6d4 100%)'),
              color: '#ffffff',
              border: 'none',
              borderRadius: '16px',
              padding: '14px 24px',
              fontSize: '1.05rem',
              fontWeight: '900',
              boxShadow: (isGeneratingVideo || jobStatus === 'processing' || jobStatus === 'initializing') ? 'none' : (isLimitExhausted ? '0 8px 30px rgba(239, 68, 68, 0.6)' : '0 8px 30px rgba(168, 85, 247, 0.55)'),
              textShadow: '0 2px 4px rgba(0,0,0,0.3)',
              cursor: (isGeneratingVideo || jobStatus === 'processing' || jobStatus === 'initializing') ? 'not-allowed' : 'pointer',
              opacity: (isGeneratingVideo || jobStatus === 'processing' || jobStatus === 'initializing') ? 0.75 : 1
            }}
          >
            {(isGeneratingVideo || jobStatus === 'processing' || jobStatus === 'initializing')
              ? '⏳ Starting Video Generation (Locked 🔒)...' 
              : (isLimitExhausted ? '🔒 Free 2 Video Limit Reached - Unlock Premium' : '🚀 Generate Video')}
          </button>

          {jobStatus && (
            <div style={{ marginTop: '1.5rem', textAlign: 'center', background: 'rgba(255, 255, 255, 0.04)', padding: '20px', borderRadius: '16px', border: '1px solid rgba(168, 85, 247, 0.3)', boxShadow: '0 10px 30px rgba(0,0,0,0.5)' }}>
              <div className={`status-badge status-${jobStatus}`} style={{ display: 'inline-block', padding: '6px 14px', borderRadius: '20px', fontSize: '0.85rem', fontWeight: 'bold', textTransform: 'uppercase', marginBottom: '12px' }}>
                Status: {jobStatus.toUpperCase()}
              </div>

              {jobStatus === 'processing' && (
                <div style={{ marginTop: '0.5rem' }}>
                  <lottie-player 
                    src="/loding.json" 
                    background="transparent" 
                    speed="1" 
                    style={{ width: '180px', height: '180px', margin: '0 auto', display: 'block' }} 
                    loop 
                    autoplay
                  ></lottie-player>
                  <h4 style={{ color: '#ffffff', fontSize: '1.15rem', marginTop: '10px', marginBottom: '6px', fontWeight: '800' }}>
                    🎬 Rendering Your AI Video...
                  </h4>
                  <p style={{ color: '#c084fc', fontSize: '0.85rem', fontWeight: 'bold', marginBottom: '6px' }}>
                    Combining Voice, Visual Clips, Subtitles & Background Music
                  </p>
                  <p style={{ color: '#94a3b8', fontSize: '0.8rem', margin: 0 }}>
                    💡 You can keep using the dashboard! Edit scripts, change settings, or view history while rendering proceeds.
                  </p>
                </div>
              )}
            </div>
          )}

          {cloudinaryUrl ? (
            <div className="video-result">
              <video src={cloudinaryUrl} controls autoPlay loop muted></video>
              <a href={cloudinaryUrl} target="_blank" rel="noreferrer" className="download-link">
                Open in Cloudinary
              </a>
            </div>
          ) : downloadUrl ? (
            <div className="video-result">
              <video src={downloadUrl} controls autoPlay loop muted></video>
              <a href={downloadUrl} target="_blank" rel="noreferrer" className="download-link">
                Download Direct Video
              </a>
            </div>
          ) : null}
        </aside>
      </div>

      {/* Slide-out Sidebar Drawer */}
      {isSidebarOpen && (
        <div className="sidebar-backdrop" onClick={() => setIsSidebarOpen(false)}>
          <div className="sidebar-drawer" onClick={e => e.stopPropagation()}>
            <div className="sidebar-header">
              <h3>Menu & Profile</h3>
              <button className="sidebar-close-btn" onClick={() => setIsSidebarOpen(false)}>×</button>
            </div>

            <div className="sidebar-profile" style={{ display: 'flex', flexDirection: 'column', gap: '10px', background: 'rgba(255,255,255,0.04)', padding: '14px', borderRadius: '16px', border: '1px solid rgba(168,85,247,0.3)', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ position: 'relative', cursor: 'pointer', flexShrink: 0 }} title="Click to change profile picture">
                  {subStatus?.profile_pic ? (
                    <img src={subStatus.profile_pic} alt="Profile" style={{ width: '50px', height: '50px', borderRadius: '50%', objectFit: 'cover', border: '2px solid #a855f7' }} />
                  ) : (
                    <div className="profile-avatar" style={{ width: '50px', height: '50px', fontSize: '1.4rem', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #3b0764 0%, #6b21a8 100%)', borderRadius: '50%', color: '#c084fc', border: '2px solid #a855f7' }}>
                      {subStatus?.name ? subStatus.name.charAt(0).toUpperCase() : '👤'}
                    </div>
                  )}
                  <label htmlFor="profile-pic-input" style={{ position: 'absolute', bottom: '-2px', right: '-2px', background: '#a855f7', color: 'white', borderRadius: '50%', width: '22px', height: '22px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.7rem', cursor: 'pointer' }}>
                    📷
                  </label>
                  <input id="profile-pic-input" type="file" accept="image/*" onChange={handleProfilePicUpload} style={{ display: 'none' }} />
                </div>

                <div style={{ textAlign: 'left', flex: 1, overflow: 'hidden' }}>
                  <h4 style={{ margin: '0 0 2px 0', fontSize: '1.05rem', color: '#ffffff', fontWeight: '800', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {subStatus?.name || 'Account Active'}
                  </h4>
                  <div style={{ fontSize: '0.78rem', color: subStatus?.has_active_subscription ? '#34d399' : '#c084fc', fontWeight: 'bold' }}>
                    💎 {subStatus?.has_active_subscription ? `${(subStatus.plan_type || 'combo').toUpperCase()} PLAN (ACTIVE)` : (subStatus?.has_active_ultra_subscription ? 'ULTRA CINEMATIC (ACTIVE)' : `Free Demo (${subStatus?.free_demo_count ?? 2}/2)`)}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: isAutoScheduleActive ? '#34d399' : '#94a3b8', fontWeight: 'bold', marginTop: '2px' }}>
                    {isAutoScheduleActive ? '🟢 Auto-Publishing: ACTIVE' : '🔴 Auto-Publishing: PAUSED'}
                  </div>
                </div>
              </div>

              {(subStatus.email || subStatus.phone || subStatus.country) && (
                <div style={{ borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '8px', display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '0.75rem', color: '#cbd5e1', textAlign: 'left' }}>
                  {subStatus.email && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      <span>📧</span> <span>{subStatus.email}</span>
                    </div>
                  )}
                  {subStatus.phone && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span>📞</span> <span>{subStatus.phone}</span>
                    </div>
                  )}
                  {subStatus.country && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span>📍</span> <span>{subStatus.country}</span>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* YOUTUBE INTEGRATION INSIDE SIDEBAR DRAWER (COMPACT MODE) */}
            <div style={{ marginBottom: '12px' }}>
              <YouTubeIntegration 
                userId={userId} 
                hasActiveSubscription={subStatus.has_active_subscription} 
                onUpgradeClick={() => openPricingModal()} 
                onStatusChange={(statusData) => {
                  setYtStatus(statusData);
                  if (statusData && (statusData.linked === false || statusData.unlinked_reset)) {
                    setAutoSchedule({ schedule_enabled: false });
                    setEnableCheckbox(false);
                    fetchAutoSchedule();
                  }
                }}
                triggerAlert={triggerAlert}
                compact={true}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '14px' }}>
              <button 
                className="btn-upgrade-sidebar" 
                style={{ 
                  background: isAutoScheduleActive ? 'linear-gradient(135deg, #059669 0%, #10b981 100%)' : 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)', 
                  boxShadow: isAutoScheduleActive ? '0 4px 15px rgba(16, 185, 129, 0.4)' : '0 4px 15px rgba(6, 182, 212, 0.3)', 
                  padding: '8px 10px', 
                  fontSize: '0.8rem', 
                  whiteSpace: 'nowrap',
                  border: isAutoScheduleActive ? '1px solid #34d399' : 'none'
                }}
                onClick={() => { setIsSidebarOpen(false); setShowAutoUploadModal(true); }}
              >
                {isAutoScheduleActive ? '⚡ Auto-Schedule (🟢 ACTIVE)' : '⚙️ Auto-Schedule'}
              </button>

              <button 
                className="btn-upgrade-sidebar" 
                style={{ padding: '8px 10px', fontSize: '0.8rem', whiteSpace: 'nowrap' }} 
                onClick={() => openPricingModal()}
              >
                💎 Upgrade
              </button>
            </div>

            <div className="sidebar-history-section">
              <h4>🕒 Your Video History ({history.length})</h4>
              {history.length === 0 ? (
                <p className="no-history-msg">No videos generated yet.</p>
              ) : (
                <div className="sidebar-history-list">
                  {history.map((vid, idx) => (
                    <div key={idx} className="sidebar-history-card">
                      <p className="history-card-topic">{vid.topic || 'Untitled Video'}</p>
                      <p className="history-card-date">
                        {vid.created_at ? new Date(vid.created_at).toLocaleString() : ''}
                      </p>
                      <div style={{ display: 'flex', gap: '8px', marginTop: '6px' }}>
                        <button 
                          className="history-watch-btn" 
                          style={{ flex: 1, padding: '6px 12px', fontSize: '0.8rem', border: 'none', borderRadius: '8px', cursor: 'pointer', background: 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)', color: 'white', fontWeight: 'bold' }}
                          onClick={() => setPlayingHistoryVideo({
                            topic: vid.topic || 'Untitled Video',
                            videoUrl: vid.cloudinary_url || `${API_BASE}/download/${vid.job_id}`,
                            downloadUrl: vid.cloudinary_url || `${API_BASE}/download/${vid.job_id}`
                          })}
                        >
                          ▶ Play Video In-App
                        </button>
                      </div>
                      {!vid.cloudinary_url && (
                        <span className="history-local-tag">Local file</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="sidebar-footer">
              <button className="btn-logout-sidebar" onClick={() => { setIsSidebarOpen(false); handleLogout(); }}>
                🚪 Logout
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Pricing & Membership Modal with Dynamic Highlighting */}
      {showPricingModal && (
        <div className="pricing-modal-overlay" style={{ zIndex: 5000 }} onClick={() => setShowPricingModal(false)}>
          <div className="pricing-modal-card" onClick={e => e.stopPropagation()}>
            <button className="modal-close-btn" onClick={() => setShowPricingModal(false)}>×</button>
            
            <div className="pricing-header">
              <span className="pricing-badge">💎 MEMBERSHIP PLANS</span>
              <h2>Choose Your Monthly Video Plan</h2>
              <p>Unlock 30 days of daily automated AI video creation and auto-uploads.</p>
            </div>

            <div className="pricing-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))' }}>
              {/* Plan 0: Ultra Cinematic */}
              <div 
                className={`pricing-card ${selectedPlan === 'ultra' ? 'featured' : ''}`}
                onClick={() => setSelectedPlan('ultra')}
                style={{ 
                  cursor: 'pointer', 
                  border: selectedPlan === 'ultra' ? '2px solid #ec4899' : (subStatus.has_active_ultra_subscription ? '2px solid #22c55e' : '1px solid rgba(255, 255, 255, 0.12)'),
                  boxShadow: selectedPlan === 'ultra' ? '0 0 25px rgba(236, 72, 153, 0.4)' : 'none',
                  opacity: (isPaymentProcessing && selectedPlan !== 'ultra') ? 0.6 : 1
                }}
              >
                {subStatus.has_active_ultra_subscription ? (
                  <div className="card-tag" style={{ background: '#22c55e', color: '#ffffff', fontWeight: 'bold' }}>✅ ACTIVE ULTRA PLAN</div>
                ) : (
                  <div className="card-tag" style={{ background: selectedPlan === 'ultra' ? 'linear-gradient(135deg, #ec4899 0%, #a855f7 100%)' : 'rgba(255,255,255,0.1)' }}>SPECIAL ULTRA</div>
                )}
                <h3>Ultra Cinematic</h3>
                <div className="plan-price">₹20 <span>/ month</span></div>
                <p className="plan-desc">Multi-Character & Documentary Auto-Uploads.</p>
                <ul className="plan-features">
                  <li>✅ Daily 1 Ultra Mode Video for 30 Days</li>
                  <li>✅ YouTube Auto-Upload Enabled</li>
                  <li>✅ Multi-Character Dialogue & Ink FX</li>
                </ul>
                <button 
                  className={`btn-buy-plan ${selectedPlan === 'ultra' ? 'featured-btn' : ''}`} 
                  disabled={isPaymentProcessing}
                  style={{ 
                    background: subStatus.has_active_ultra_subscription ? '#16a34a' : (selectedPlan === 'ultra' ? 'linear-gradient(135deg, #ec4899 0%, #a855f7 100%)' : 'rgba(255, 255, 255, 0.08)'),
                    color: (selectedPlan === 'ultra' || subStatus.has_active_ultra_subscription) ? '#ffffff' : '#94a3b8',
                    cursor: isPaymentProcessing ? 'not-allowed' : 'pointer'
                  }}
                  onClick={(e) => { e.stopPropagation(); setSelectedPlan('ultra'); handleBuyPlan('ultra'); }}
                >
                  {isPaymentProcessing && selectedPlan === 'ultra' ? '⏳ Connecting...' : (subStatus.has_active_ultra_subscription ? '✅ Ultra Active (1 Month Limit)' : 'Subscribe for ₹20')}
                </button>
              </div>

              {/* Plan 1: Short Starter */}
              <div 
                className={`pricing-card ${selectedPlan === 'short' ? 'featured' : ''}`}
                onClick={() => setSelectedPlan('short')}
                style={{ 
                  cursor: 'pointer',
                  border: selectedPlan === 'short' ? '2px solid #a855f7' : (subStatus.plan_type === 'short' ? '2px solid #22c55e' : '1px solid rgba(255, 255, 255, 0.12)'),
                  boxShadow: selectedPlan === 'short' ? '0 0 25px rgba(168, 85, 247, 0.4)' : 'none',
                  opacity: (isPaymentProcessing && selectedPlan !== 'short') ? 0.6 : 1
                }}
              >
                {subStatus.plan_type === 'short' ? (
                  <div className="card-tag" style={{ background: '#22c55e', color: '#ffffff' }}>✅ ACTIVE PLAN</div>
                ) : (
                  <div className="card-tag">30 DAYS</div>
                )}
                <h3>Short Starter</h3>
                <div className="plan-price">₹50 <span>/ month</span></div>
                <p className="plan-desc">Perfect for Shorts & Reels creators.</p>
                <ul className="plan-features">
                  <li>✅ Daily 1 Short Video (9:16) for 30 Days</li>
                  <li>✅ YouTube Auto-Upload Enabled</li>
                  <li>✅ Cloud Storage & History</li>
                </ul>
                <button 
                  className={`btn-buy-plan ${selectedPlan === 'short' ? 'featured-btn' : ''}`} 
                  disabled={isPaymentProcessing}
                  style={{ 
                    background: subStatus.plan_type === 'short' ? '#16a34a' : (selectedPlan === 'short' ? 'linear-gradient(135deg, #a855f7 0%, #6366f1 100%)' : 'rgba(255, 255, 255, 0.08)'),
                    color: (selectedPlan === 'short' || subStatus.plan_type === 'short') ? '#ffffff' : '#94a3b8',
                    cursor: isPaymentProcessing ? 'not-allowed' : 'pointer'
                  }}
                  onClick={(e) => { e.stopPropagation(); setSelectedPlan('short'); handleBuyPlan('short'); }}
                >
                  {isPaymentProcessing && selectedPlan === 'short' ? '⏳ Connecting...' : (subStatus.plan_type === 'short' ? '✅ Active (Stack +30 Days ₹50)' : 'Subscribe for ₹50')}
                </button>
              </div>

              {/* Plan 2: Long Master */}
              <div 
                className={`pricing-card ${selectedPlan === 'long' ? 'featured' : ''}`}
                onClick={() => setSelectedPlan('long')}
                style={{ 
                  cursor: 'pointer',
                  border: selectedPlan === 'long' ? '2px solid #a855f7' : (subStatus.plan_type === 'long' ? '2px solid #22c55e' : '1px solid rgba(255, 255, 255, 0.12)'),
                  boxShadow: selectedPlan === 'long' ? '0 0 25px rgba(168, 85, 247, 0.4)' : 'none',
                  opacity: (isPaymentProcessing && selectedPlan !== 'long') ? 0.6 : 1
                }}
              >
                {subStatus.plan_type === 'long' ? (
                  <div className="card-tag" style={{ background: '#22c55e', color: '#ffffff' }}>✅ ACTIVE PLAN</div>
                ) : (
                  <div className="card-tag gold">POPULAR</div>
                )}
                <h3>Long Master</h3>
                <div className="plan-price">₹100 <span>/ month</span></div>
                <p className="plan-desc">For full-length YouTube video channels.</p>
                <ul className="plan-features">
                  <li>✅ Daily 1 Long Video (16:9) for 30 Days</li>
                  <li>✅ YouTube Auto-Upload Enabled</li>
                  <li>✅ Cloud Storage & History</li>
                </ul>
                <button 
                  className={`btn-buy-plan ${selectedPlan === 'long' ? 'featured-btn' : ''}`} 
                  disabled={isPaymentProcessing}
                  style={{ 
                    background: subStatus.plan_type === 'long' ? '#16a34a' : (selectedPlan === 'long' ? 'linear-gradient(135deg, #a855f7 0%, #6366f1 100%)' : 'rgba(255, 255, 255, 0.08)'),
                    color: (selectedPlan === 'long' || subStatus.plan_type === 'long') ? '#ffffff' : '#94a3b8',
                    cursor: isPaymentProcessing ? 'not-allowed' : 'pointer'
                  }}
                  onClick={(e) => { e.stopPropagation(); setSelectedPlan('long'); handleBuyPlan('long'); }}
                >
                  {isPaymentProcessing && selectedPlan === 'long' ? '⏳ Connecting...' : (subStatus.plan_type === 'long' ? '✅ Active (Stack +30 Days ₹100)' : 'Subscribe for ₹100')}
                </button>
              </div>

              {/* Plan 3: Pro Combo */}
              <div 
                className={`pricing-card ${selectedPlan === 'combo' ? 'featured' : ''}`}
                onClick={() => setSelectedPlan('combo')}
                style={{ 
                  cursor: 'pointer',
                  border: selectedPlan === 'combo' ? '2px solid #a855f7' : (subStatus.plan_type === 'combo' ? '2px solid #22c55e' : '1px solid rgba(255, 255, 255, 0.12)'),
                  boxShadow: selectedPlan === 'combo' ? '0 0 25px rgba(168, 85, 247, 0.4)' : 'none',
                  opacity: (isPaymentProcessing && selectedPlan !== 'combo') ? 0.6 : 1
                }}
              >
                {subStatus.plan_type === 'combo' ? (
                  <div className="card-tag" style={{ background: '#22c55e', color: '#ffffff' }}>✅ ACTIVE PLAN</div>
                ) : (
                  <div className="card-tag purple">BEST VALUE</div>
                )}
                <h3>Pro Combo</h3>
                <div className="plan-price">₹119 <span>/ month</span></div>
                <p className="plan-desc">All-in-one power suite for max reach.</p>
                <ul className="plan-features">
                  <li>✅ Daily 1 Short + 1 Long Video for 30 Days</li>
                  <li>✅ YouTube Auto-Upload Enabled</li>
                  <li>✅ Priority AI Rendering</li>
                </ul>
                <button 
                  className={`btn-buy-plan ${selectedPlan === 'combo' ? 'featured-btn' : ''}`} 
                  disabled={isPaymentProcessing}
                  style={{ 
                    background: subStatus.plan_type === 'combo' ? '#16a34a' : (selectedPlan === 'combo' ? 'linear-gradient(135deg, #a855f7 0%, #6366f1 100%)' : 'rgba(255, 255, 255, 0.08)'),
                    color: (selectedPlan === 'combo' || subStatus.plan_type === 'combo') ? '#ffffff' : '#94a3b8',
                    cursor: isPaymentProcessing ? 'not-allowed' : 'pointer'
                  }}
                  onClick={(e) => { e.stopPropagation(); setSelectedPlan('combo'); handleBuyPlan('combo'); }}
                >
                  {isPaymentProcessing && selectedPlan === 'combo' ? '⏳ Connecting...' : (subStatus.plan_type === 'combo' ? '✅ Active (Stack +30 Days ₹119)' : 'Subscribe for ₹119')}
                </button>
              </div>
            </div>

            <div className="pricing-footer">
              🔒 Safe & Secure Payments via Razorpay. Cancel anytime.
            </div>
          </div>
        </div>
      )}

      {/* Payment Success Confirmation Modal with payment.json Lottie animation */}
      {showPaymentSuccessModal && (
        <div className="pricing-modal-overlay" onClick={() => setShowPaymentSuccessModal(false)}>
          <div className="pricing-modal-card" style={{ maxWidth: '420px', textAlign: 'center', padding: '40px 24px' }} onClick={e => e.stopPropagation()}>
            <lottie-player 
              src="/payment.json" 
              background="transparent" 
              speed="1" 
              style={{ width: '220px', height: '220px', margin: '0 auto' }} 
              autoplay
            ></lottie-player>

            <h2 style={{ color: '#22c55e', fontSize: '1.8rem', marginTop: '16px', marginBottom: '8px' }}>
              🎉 Payment Successful!
            </h2>
            <p style={{ color: '#cbd5e1', fontSize: '0.95rem', marginBottom: '24px' }}>
              Your 30-Day Membership has been activated. You can now generate videos and auto-upload to YouTube!
            </p>

            <button 
              className="btn-hero-cta" 
              style={{ width: '100%', padding: '14px', fontSize: '1rem' }} 
              onClick={() => setShowPaymentSuccessModal(false)}
            >
              Start Creating Videos →
            </button>
          </div>
        </div>
      )}
      {/* Big Clean Full-Screen Loading Animation Overlay */}
      {(isGeneratingScript || isPaymentProcessing) && (
        <div className="pricing-modal-overlay" style={{ zIndex: 4000, background: 'rgba(10, 7, 24, 0.85)', backdropFilter: 'blur(10px)' }}>
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
              {isGeneratingScript ? 'Generating AI Video Script...' : 'Preparing Checkout...'}
            </h3>
            <p style={{ color: '#c084fc', fontSize: '0.95rem', fontWeight: 'bold', marginBottom: '6px' }}>
              Processing request via Cloxel AI Cloud
            </p>
            <p style={{ color: '#cbd5e1', fontSize: '0.85rem', margin: 0 }}>
              Please wait a moment while we process your request.
            </p>
          </div>
        </div>
      )}
      {/* In-App Video Player Modal for Video History */}
      {playingHistoryVideo && (
        <div className="pricing-modal-overlay" onClick={() => setPlayingHistoryVideo(null)} style={{ zIndex: 3000 }}>
          <div className="pricing-modal-card" style={{ maxWidth: '640px', padding: '32px 24px', textAlign: 'center' }} onClick={e => e.stopPropagation()}>
            <button className="modal-close-btn" onClick={() => setPlayingHistoryVideo(null)}>×</button>
            
            <h3 style={{ color: '#ffffff', fontSize: '1.3rem', marginBottom: '16px', fontWeight: '800' }}>
              🎬 {playingHistoryVideo.topic}
            </h3>

            <div style={{ borderRadius: '16px', overflow: 'hidden', background: '#000', marginBottom: '20px', border: '1px solid rgba(168,85,247,0.4)', boxShadow: '0 10px 30px rgba(0,0,0,0.8)' }}>
              <video 
                src={playingHistoryVideo.videoUrl} 
                controls 
                autoPlay 
                style={{ width: '100%', maxHeight: '65vh', display: 'block' }}
              ></video>
            </div>

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <a 
                href={playingHistoryVideo.downloadUrl} 
                target="_blank" 
                rel="noreferrer" 
                className="btn-hero-cta" 
                style={{ padding: '10px 20px', fontSize: '0.9rem', textDecoration: 'none' }}
              >
                ⬇ Download Video
              </a>
              <button 
                className="button secondary" 
                style={{ width: 'auto', padding: '10px 20px' }} 
                onClick={() => setPlayingHistoryVideo(null)}
              >
                Close Player
              </button>
            </div>
          </div>
        </div>
      )}
      {/* Auto-Upload Settings Modal (Secret Page) */}
      {showAutoUploadModal && (
        <div className="pricing-modal-overlay" onClick={() => setShowAutoUploadModal(false)} style={{ zIndex: 3000 }}>
          <div className="pricing-modal-card" style={{ maxWidth: '680px', padding: '36px' }} onClick={e => e.stopPropagation()}>
            <button className="sidebar-close-btn" style={{ position: 'absolute', top: '20px', right: '20px', background: 'none', border: 'none', color: '#fff', fontSize: '1.8rem', cursor: 'pointer' }} onClick={() => setShowAutoUploadModal(false)}>×</button>

            <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100%', marginBottom: '24px' }}>
              <span className="pricing-badge" style={{ background: 'rgba(6, 182, 212, 0.2)', color: '#38bdf8' }}>🤖 AUTOMATED YOUTUBE ENGINE</span>
              <h2 style={{ color: '#ffffff', fontSize: '1.8rem', marginTop: '8px', fontWeight: '800', textAlign: 'center', display: 'block', width: '100%', margin: '8px auto 0 auto' }}>
                Auto-Upload & Schedule Mode
              </h2>
              <p style={{ color: '#94a3b8', fontSize: '0.85rem', textAlign: 'center', display: 'block', width: '100%', margin: '4px auto 0 auto' }}>
                Configure daily automatic video generation and YouTube channel publishing.
              </p>
            </div>

            {/* Current Active Plan Status Card */}
            <div style={{ background: 'rgba(255,255,255,0.04)', padding: '18px 20px', borderRadius: '16px', border: '1px solid rgba(6, 182, 212, 0.3)', marginBottom: '20px' }}>
              <h4 style={{ color: '#38bdf8', marginBottom: '10px', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                💎 Active Membership Plan Status
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '0.85rem', color: '#cbd5e1' }}>
                <div><strong>Current Plan:</strong> <span style={{ color: '#c084fc', textTransform: 'uppercase', fontWeight: 'bold' }}>{subStatus.has_active_subscription ? `${subStatus.plan_type} (${autoSchedule.purchase_count || 1}x Stacked)` : 'Free Demo'}</span></div>
                <div><strong>Daily Video Limit:</strong> <span style={{ color: '#22c55e', fontWeight: 'bold' }}>{subStatus.daily_limit_text || (subStatus.plan_type === 'combo' ? '2 Videos Daily (1 Short + 1 Long)' : '1 Video Daily')}</span></div>
                <div><strong>Today Auto Short Reels:</strong> <span style={{ color: '#38bdf8' }}>{subStatus.today_auto_short_count ?? 0} / {subStatus.plan_type === 'combo' || subStatus.plan_type === 'short' ? '1' : '0'} Auto-Uploaded</span></div>
                <div><strong>Today Auto Long Videos:</strong> <span style={{ color: '#38bdf8' }}>{subStatus.today_auto_long_count ?? 0} / {subStatus.plan_type === 'combo' || subStatus.plan_type === 'long' ? '1' : '0'} Auto-Uploaded</span></div>
                <div><strong>Auto-Publish Target:</strong> <span style={{ color: '#ffffff' }}>YouTube Automation Engine</span></div>
                <div><strong>Total History Count:</strong> <span style={{ color: '#c084fc' }}>{history.length} Videos Saved</span></div>
              </div>
            </div>

            {/* Secret Auto-Generate Page Configuration Form */}
            <div style={{ background: 'rgba(0,0,0,0.35)', padding: '24px', borderRadius: '16px', border: '1px solid rgba(6, 182, 212, 0.3)', textAlign: 'left', marginBottom: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                <span style={{ fontSize: '1.8rem' }}>🔐</span>
                <div>
                  <h3 style={{ color: '#ffffff', fontSize: '1.15rem', fontWeight: '800', margin: 0 }}>
                    Secret Auto-Generate Page Configuration
                  </h3>
                  <p style={{ color: '#94a3b8', fontSize: '0.8rem', margin: 0 }}>
                    Set exact video generation times & topics. All data syncs directly to your secure account.
                  </p>
                </div>
              </div>

              {/* Auto-Publishing Status Banner */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: isAutoScheduleActive ? 'rgba(34, 197, 94, 0.12)' : 'rgba(239, 68, 68, 0.12)', border: isAutoScheduleActive ? '1px solid rgba(52, 211, 153, 0.35)' : '1px solid rgba(239, 68, 68, 0.35)', borderRadius: '12px', padding: '10px 16px', marginBottom: '18px' }}>
                <span style={{ fontSize: '0.88rem', fontWeight: 'bold', color: '#ffffff' }}>Account Auto-Upload Status:</span>
                <span style={{ padding: '4px 14px', borderRadius: '20px', fontSize: '0.8rem', fontWeight: '800', background: isAutoScheduleActive ? 'linear-gradient(135deg, #059669 0%, #10b981 100%)' : 'rgba(239, 68, 68, 0.25)', color: '#ffffff', boxShadow: isAutoScheduleActive ? '0 0 12px rgba(52, 211, 153, 0.4)' : 'none' }}>
                  {isAutoScheduleActive ? '🟢 ENGINE ACTIVE & SAVED IN DB' : '🔴 ENGINE PAUSED'}
                </span>
              </div>

              {/* Plan Video Counter Bar */}
              <div style={{ background: 'rgba(6, 182, 212, 0.1)', border: '1px solid rgba(6, 182, 212, 0.3)', borderRadius: '12px', padding: '12px 16px', marginBottom: '18px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem' }}>
                <div><span style={{ color: '#94a3b8' }}>Elapsed Membership Days:</span> <strong style={{ color: '#ffffff' }}>{autoSchedule.total_videos_created} Days Passed</strong></div>
                <div><span style={{ color: '#94a3b8' }}>Total Stacked Plan Remaining:</span> <strong style={{ color: '#38bdf8' }}>{autoSchedule.remaining_plan_videos} / {autoSchedule.total_plan_allowance || (subStatus.plan_type === 'combo' ? 60 : 30)} Videos Left</strong></div>
              </div>

              {/* LIVE ENGINES STATUS DASHBOARD */}
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid rgba(148, 163, 184, 0.2)', borderRadius: '14px', padding: '16px', marginBottom: '20px' }}>
                <h4 style={{ color: '#f8fafc', fontSize: '0.92rem', fontWeight: '800', margin: '0 0 12px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  ⚡ Live Automation Engines Status Breakdown
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '10px' }}>
                  {/* 1. Shorts Engine */}
                  <div style={{ background: (isAutoScheduleActive && (subStatus.plan_type === 'short' || subStatus.plan_type === 'combo')) ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.08)', border: (isAutoScheduleActive && (subStatus.plan_type === 'short' || subStatus.plan_type === 'combo')) ? '1px solid rgba(34, 197, 94, 0.3)' : '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '10px', padding: '10px 12px' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 'bold', color: '#cbd5e1', marginBottom: '4px' }}>📱 9:16 Short Reels Engine</div>
                    <div style={{ fontSize: '0.78rem', fontWeight: '800', color: (isAutoScheduleActive && (subStatus.plan_type === 'short' || subStatus.plan_type === 'combo')) ? '#4ade80' : '#f87171' }}>
                      {(isAutoScheduleActive && (subStatus.plan_type === 'short' || subStatus.plan_type === 'combo')) ? `🟢 RUNNING (Daily @ ${autoSchedule.short_time || '10:00 AM'})` : '🔴 INACTIVE'}
                    </div>
                  </div>

                  {/* 2. Long Engine */}
                  <div style={{ background: (isAutoScheduleActive && (subStatus.plan_type === 'long' || subStatus.plan_type === 'combo')) ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.08)', border: (isAutoScheduleActive && (subStatus.plan_type === 'long' || subStatus.plan_type === 'combo')) ? '1px solid rgba(34, 197, 94, 0.3)' : '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '10px', padding: '10px 12px' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 'bold', color: '#cbd5e1', marginBottom: '4px' }}>📽️ 16:9 Long Video Engine</div>
                    <div style={{ fontSize: '0.78rem', fontWeight: '800', color: (isAutoScheduleActive && (subStatus.plan_type === 'long' || subStatus.plan_type === 'combo')) ? '#4ade80' : '#f87171' }}>
                      {(isAutoScheduleActive && (subStatus.plan_type === 'long' || subStatus.plan_type === 'combo')) ? `🟢 RUNNING (Daily @ ${autoSchedule.long_time || '06:00 PM'})` : '🔴 INACTIVE'}
                    </div>
                  </div>

                  {/* 3. Ultra Engine */}
                  <div style={{ background: (isAutoScheduleActive && autoSchedule.ultra_enabled) ? 'rgba(236, 72, 153, 0.15)' : 'rgba(239, 68, 68, 0.08)', border: (isAutoScheduleActive && autoSchedule.ultra_enabled) ? '1px solid rgba(236, 72, 153, 0.4)' : '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '10px', padding: '10px 12px' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 'bold', color: '#cbd5e1', marginBottom: '4px' }}>🎬 Ultra 3D Motion Engine</div>
                    <div style={{ fontSize: '0.78rem', fontWeight: '800', color: (isAutoScheduleActive && autoSchedule.ultra_enabled) ? '#f472b6' : '#f87171' }}>
                      {(isAutoScheduleActive && autoSchedule.ultra_enabled) ? `🟢 RUNNING (Daily @ ${autoSchedule.ultra_time || '09:00 PM'} - 1/Mo)` : (autoSchedule.ultra_enabled ? '🟡 ENABLED (Main Switch Off)' : '🔴 TOGGLED OFF')}
                    </div>
                  </div>
                </div>
              </div>

              {/* Auto Schedule Switch */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px', background: 'rgba(255,255,255,0.03)', padding: '12px 16px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.08)' }}>
                <input 
                  type="checkbox" 
                  id="auto-schedule-enable"
                  checked={enableCheckbox}
                  onChange={(e) => setEnableCheckbox(e.target.checked)}
                  style={{ width: '18px', height: '18px', accentColor: '#06b6d4', cursor: 'pointer' }}
                />
                <label htmlFor="auto-schedule-enable" style={{ color: '#ffffff', fontWeight: 'bold', fontSize: '0.9rem', cursor: 'pointer' }}>
                  Enable Daily Automated AI Video Generation & YouTube Upload
                </label>
              </div>

              {/* 1. SHORT REEL SCHEDULE PROFILE (If Short Starter or Pro Combo) */}
              {(subStatus.plan_type === 'short' || subStatus.plan_type === 'combo') && (
                <div style={{ background: 'rgba(168,85,247,0.08)', padding: '18px', borderRadius: '14px', border: '1px solid rgba(168,85,247,0.3)', marginBottom: '20px' }}>
                  <h4 style={{ color: '#c084fc', marginBottom: '14px', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    📱 9:16 Short Reels Automation Settings
                  </h4>

                  {/* Topic Choice */}
                  <div style={{ marginBottom: '14px' }}>
                    <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '6px' }}>
                      <input 
                        type="checkbox" 
                        id="short-auto-topic"
                        checked={autoSchedule.short_auto_topic !== false}
                        onChange={(e) => setAutoSchedule({ ...autoSchedule, short_auto_topic: e.target.checked })}
                        style={{ width: '16px', height: '16px', accentColor: '#a855f7' }}
                      />
                      <label htmlFor="short-auto-topic" style={{ color: '#ffffff', fontSize: '0.85rem', fontWeight: 'bold' }}>
                        🎲 Dynamic AI Auto-Topic (Everyday New Trending Topic)
                      </label>
                    </div>

                    {autoSchedule.short_auto_topic === false && (
                      <textarea 
                        rows="2"
                        value={autoSchedule.short_topic || ''}
                        onChange={(e) => setAutoSchedule({ ...autoSchedule, short_topic: e.target.value })}
                        placeholder="Enter custom Short topics separated by comma (e.g. Space Facts, Fitness Hacks)"
                        style={{ width: '100%', padding: '10px', background: '#1e1738', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '8px', color: '#ffffff', fontSize: '0.85rem' }}
                      />
                    )}
                  </div>

                  {/* Short Voice, Font, Category, Color, Duration, Time */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '0.82rem' }}>
                    <div>
                      <label style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Category / Niche (30+ Options):</label>
                      <select value={autoSchedule.short_category || '🎲 Random / All Categories'} onChange={(e) => setAutoSchedule({ ...autoSchedule, short_category: e.target.value })} style={{ width: '100%', padding: '8px', background: '#1e1738', border: '1px solid rgba(255,255,255,0.15)', color: '#fff', borderRadius: '8px' }}>
                        {CATEGORIES.map((cat, i) => (
                          <option key={i} value={cat}>{cat}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Voice:</label>
                      <select value={autoSchedule.short_voice || 'hi-IN-MadhurNeural'} onChange={(e) => setAutoSchedule({ ...autoSchedule, short_voice: e.target.value })} style={{ width: '100%', padding: '8px', background: '#1e1738', border: '1px solid rgba(255,255,255,0.15)', color: '#fff', borderRadius: '8px' }}>
                        <option value="hi-IN-MadhurNeural">Madhur (Male, Hindi)</option>
                        <option value="hi-IN-SwaraNeural">Swara (Female, Hindi)</option>
                        <option value="en-US-GuyNeural">Guy (Male, English)</option>
                        <option value="en-US-JennyNeural">Jenny (Female, English)</option>
                      </select>
                    </div>

                    <div>
                      <label style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Font Family:</label>
                      <select value={autoSchedule.short_font || 'Arial.ttf'} onChange={(e) => setAutoSchedule({ ...autoSchedule, short_font: e.target.value })} style={{ width: '100%', padding: '8px', background: '#1e1738', border: '1px solid rgba(255,255,255,0.15)', color: '#fff', borderRadius: '8px' }}>
                        {fontList.map((f, i) => (
                          <option key={i} value={f}>{f.replace(/\.[^/.]+$/, "")}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Reel Duration (10s - 55s Max):</label>
                      <input 
                        type="number" 
                        min="10" 
                        max="55" 
                        value={autoSchedule.short_duration || 30} 
                        onChange={(e) => setAutoSchedule({ ...autoSchedule, short_duration: Math.min(55, Math.max(10, Number(e.target.value))) })}
                        style={{ width: '100%', padding: '8px', background: '#1e1738', border: '1px solid rgba(255,255,255,0.15)', color: '#fff', borderRadius: '8px' }}
                      />
                    </div>

                    <div>
                      <label style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Daily Upload Time (24h):</label>
                      <input 
                        type="time" 
                        value={autoSchedule.short_time || '10:00'} 
                        onChange={(e) => setAutoSchedule({ ...autoSchedule, short_time: e.target.value })}
                        style={{ width: '100%', padding: '8px', background: '#1e1738', border: '1px solid rgba(255,255,255,0.15)', color: '#fff', borderRadius: '8px' }}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* 2. LONG VIDEO SCHEDULE PROFILE (If Long Master or Pro Combo) */}
              {(subStatus.plan_type === 'long' || subStatus.plan_type === 'combo') && (
                <div style={{ background: 'rgba(6,182,212,0.08)', padding: '18px', borderRadius: '14px', border: '1px solid rgba(6,182,212,0.3)', marginBottom: '20px' }}>
                  <h4 style={{ color: '#38bdf8', marginBottom: '14px', fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    🖥️ 16:9 Long Video Automation Settings
                  </h4>

                  {/* Topic Choice */}
                  <div style={{ marginBottom: '14px' }}>
                    <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '6px' }}>
                      <input 
                        type="checkbox" 
                        id="long-auto-topic"
                        checked={autoSchedule.long_auto_topic !== false}
                        onChange={(e) => setAutoSchedule({ ...autoSchedule, long_auto_topic: e.target.checked })}
                        style={{ width: '16px', height: '16px', accentColor: '#06b6d4' }}
                      />
                      <label htmlFor="long-auto-topic" style={{ color: '#ffffff', fontSize: '0.85rem', fontWeight: 'bold' }}>
                        🎲 Dynamic AI Auto-Topic (Everyday New Deep-Dive Topic)
                      </label>
                    </div>

                    {autoSchedule.long_auto_topic === false && (
                      <textarea 
                        rows="2"
                        value={autoSchedule.long_topic || ''}
                        onChange={(e) => setAutoSchedule({ ...autoSchedule, long_topic: e.target.value })}
                        placeholder="Enter custom Long Video topics separated by comma (e.g. Ancient Mysteries, AI Revolution)"
                        style={{ width: '100%', padding: '10px', background: '#1e1738', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '8px', color: '#ffffff', fontSize: '0.85rem' }}
                      />
                    )}
                  </div>

                  {/* Long Voice, Font, Category, Color, Duration, Time */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '0.82rem' }}>
                    <div>
                      <label style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Category / Niche (30+ Options):</label>
                      <select value={autoSchedule.long_category || '🎲 Random / All Categories'} onChange={(e) => setAutoSchedule({ ...autoSchedule, long_category: e.target.value })} style={{ width: '100%', padding: '8px', background: '#1e1738', border: '1px solid rgba(255,255,255,0.15)', color: '#fff', borderRadius: '8px' }}>
                        {CATEGORIES.map((cat, i) => (
                          <option key={i} value={cat}>{cat}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Voice:</label>
                      <select value={autoSchedule.long_voice || 'hi-IN-MadhurNeural'} onChange={(e) => setAutoSchedule({ ...autoSchedule, long_voice: e.target.value })} style={{ width: '100%', padding: '8px', background: '#1e1738', border: '1px solid rgba(255,255,255,0.15)', color: '#fff', borderRadius: '8px' }}>
                        <option value="hi-IN-MadhurNeural">Madhur (Male, Hindi)</option>
                        <option value="hi-IN-SwaraNeural">Swara (Female, Hindi)</option>
                        <option value="en-US-GuyNeural">Guy (Male, English)</option>
                        <option value="en-US-JennyNeural">Jenny (Female, English)</option>
                      </select>
                    </div>

                    <div>
                      <label style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Font Family:</label>
                      <select value={autoSchedule.long_font || 'Arial.ttf'} onChange={(e) => setAutoSchedule({ ...autoSchedule, long_font: e.target.value })} style={{ width: '100%', padding: '8px', background: '#1e1738', border: '1px solid rgba(255,255,255,0.15)', color: '#fff', borderRadius: '8px' }}>
                        {fontList.map((f, i) => (
                          <option key={i} value={f}>{f.replace(/\.[^/.]+$/, "")}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Video Duration (20s - 300s / 5m Max):</label>
                      <input 
                        type="number" 
                        min="20" 
                        max="300" 
                        value={autoSchedule.long_duration || 60} 
                        onChange={(e) => setAutoSchedule({ ...autoSchedule, long_duration: Math.min(300, Math.max(20, Number(e.target.value))) })}
                        style={{ width: '100%', padding: '8px', background: '#1e1738', border: '1px solid rgba(255,255,255,0.15)', color: '#fff', borderRadius: '8px' }}
                      />
                    </div>

                    <div>
                      <label style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Daily Upload Time (24h):</label>
                      <input 
                        type="time" 
                        value={autoSchedule.long_time || '18:00'} 
                        onChange={(e) => setAutoSchedule({ ...autoSchedule, long_time: e.target.value })}
                        style={{ width: '100%', padding: '8px', background: '#1e1738', border: '1px solid rgba(255,255,255,0.15)', color: '#fff', borderRadius: '8px' }}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* 3. ULTRA CINEMATIC 3D MOTION SCHEDULE PROFILE (If Ultra Active or Enabled) */}
              {(subStatus.has_active_ultra_subscription || subStatus.plan_type === 'ultra' || subStatus.plan_type === 'combo' || autoSchedule.ultra_enabled) && (
                <div style={{ background: 'rgba(236,72,153,0.08)', padding: '18px', borderRadius: '14px', border: '1px solid rgba(236,72,153,0.3)', marginBottom: '20px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                    <h4 style={{ color: '#f472b6', margin: 0, fontSize: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      🎬 Ultra Cinematic 3D Photo Motion Auto-Upload Workflow
                    </h4>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', background: 'rgba(236,72,153,0.2)', padding: '4px 10px', borderRadius: '20px', border: '1px solid #ec4899' }}>
                      <input 
                        type="checkbox" 
                        checked={autoSchedule.ultra_enabled || false}
                        onChange={(e) => setAutoSchedule({ ...autoSchedule, ultra_enabled: e.target.checked })}
                        style={{ width: '16px', height: '16px', accentColor: '#ec4899' }}
                      />
                      <span style={{ color: '#fff', fontSize: '0.8rem', fontWeight: 'bold' }}>
                        {autoSchedule.ultra_enabled ? '🟢 ENABLED' : '🔴 DISABLED'}
                      </span>
                    </label>
                  </div>

                  {autoSchedule.ultra_enabled && (
                    <>
                      <div style={{ marginBottom: '14px' }}>
                        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '6px' }}>
                          <input 
                            type="checkbox" 
                            id="ultra-auto-topic"
                            checked={autoSchedule.ultra_auto_topic !== false}
                            onChange={(e) => setAutoSchedule({ ...autoSchedule, ultra_auto_topic: e.target.checked })}
                            style={{ width: '16px', height: '16px', accentColor: '#ec4899' }}
                          />
                          <label htmlFor="ultra-auto-topic" style={{ color: '#ffffff', fontSize: '0.85rem', fontWeight: 'bold' }}>
                            🎲 Dynamic AI Auto-Topic (History, Ancient Warriors & Science Mysteries)
                          </label>
                        </div>

                        {autoSchedule.ultra_auto_topic === false && (
                          <textarea 
                            rows="2"
                            value={autoSchedule.ultra_topic || ''}
                            onChange={(e) => setAutoSchedule({ ...autoSchedule, ultra_topic: e.target.value })}
                            placeholder="Enter custom Ultra topics separated by comma (e.g. Maharana Pratap, Ancient Warriors)"
                            style={{ width: '100%', padding: '10px', background: '#1e1738', border: '1px solid rgba(255,255,255,0.15)', borderRadius: '8px', color: '#ffffff', fontSize: '0.85rem' }}
                          />
                        )}
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '0.82rem' }}>
                        <div>
                          <label style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Category / Niche:</label>
                          <select value={autoSchedule.ultra_category || '🎲 Random / All Categories'} onChange={(e) => setAutoSchedule({ ...autoSchedule, ultra_category: e.target.value })} style={{ width: '100%', padding: '8px', background: '#1e1738', border: '1px solid rgba(255,255,255,0.15)', color: '#fff', borderRadius: '8px' }}>
                            {CATEGORIES.map((cat, i) => (
                              <option key={i} value={cat}>{cat}</option>
                            ))}
                          </select>
                        </div>

                        <div>
                          <label style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Video Size / Aspect Ratio:</label>
                          <select value={autoSchedule.ultra_aspect_ratio || '16:9'} onChange={(e) => setAutoSchedule({ ...autoSchedule, ultra_aspect_ratio: e.target.value })} style={{ width: '100%', padding: '8px', background: '#1e1738', border: '1px solid rgba(255,255,255,0.15)', color: '#fff', borderRadius: '8px' }}>
                            <option value="16:9">📺 16:9 Landscape HD (1920×1080)</option>
                            <option value="9:16">📱 9:16 Vertical Shorts (1080×1920)</option>
                          </select>
                        </div>

                        <div>
                          <label style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Voice:</label>
                          <select value={autoSchedule.ultra_voice || 'hi-IN-MadhurNeural'} onChange={(e) => setAutoSchedule({ ...autoSchedule, ultra_voice: e.target.value })} style={{ width: '100%', padding: '8px', background: '#1e1738', border: '1px solid rgba(255,255,255,0.15)', color: '#fff', borderRadius: '8px' }}>
                            <option value="hi-IN-MadhurNeural">Madhur (Male, Hindi)</option>
                            <option value="hi-IN-SwaraNeural">Swara (Female, Hindi)</option>
                            <option value="en-US-GuyNeural">Guy (Male, English)</option>
                            <option value="en-US-JennyNeural">Jenny (Female, English)</option>
                          </select>
                        </div>

                        <div>
                          <label style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Daily Upload Time (24h):</label>
                          <input 
                            type="time" 
                            value={autoSchedule.ultra_time || '21:00'} 
                            onChange={(e) => setAutoSchedule({ ...autoSchedule, ultra_time: e.target.value })}
                            style={{ width: '100%', padding: '8px', background: '#1e1738', border: '1px solid rgba(255,255,255,0.15)', color: '#fff', borderRadius: '8px' }}
                          />
                        </div>

                        <div>
                          <label style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Ultra Duration (20s - 300s / 5m Max):</label>
                          <input 
                            type="number" 
                            min="20" 
                            max="300" 
                            value={autoSchedule.ultra_duration || 60} 
                            onChange={(e) => setAutoSchedule({ ...autoSchedule, ultra_duration: Math.min(300, Math.max(20, Number(e.target.value))) })}
                            style={{ width: '100%', padding: '8px', background: '#1e1738', border: '1px solid rgba(255,255,255,0.15)', color: '#fff', borderRadius: '8px' }}
                          />
                        </div>

                        {(() => {
                          const catLow = (autoSchedule.ultra_category || '').toLowerCase();
                          const isCartoon = ['cartoon', 'anime', 'animation', 'character', 'comic'].some(k => catLow.includes(k));
                          if (!isCartoon) {
                            return (
                              <>
                                <div>
                                  <label style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Font Family:</label>
                                  <select value={autoSchedule.ultra_font || 'Arial.ttf'} onChange={(e) => setAutoSchedule({ ...autoSchedule, ultra_font: e.target.value })} style={{ width: '100%', padding: '8px', background: '#1e1738', border: '1px solid rgba(255,255,255,0.15)', color: '#fff', borderRadius: '8px' }}>
                                    {(fontList && fontList.length > 0 ? fontList : ['Arial.ttf']).map((font, i) => (
                                      <option key={i} value={font}>{font.replace(/\.[^/.]+$/, "")}</option>
                                    ))}
                                  </select>
                                </div>

                                <div>
                                  <label style={{ color: '#cbd5e1', display: 'block', marginBottom: '4px' }}>Subtitle Highlight Color:</label>
                                  <select value={autoSchedule.ultra_color || 'yellow'} onChange={(e) => setAutoSchedule({ ...autoSchedule, ultra_color: e.target.value })} style={{ width: '100%', padding: '8px', background: '#1e1738', border: '1px solid rgba(255,255,255,0.15)', color: '#fff', borderRadius: '8px' }}>
                                    <option value="yellow">🟡 Vivid Yellow</option>
                                    <option value="#00FF00">🟢 Neon Green</option>
                                    <option value="cyan">🔵 Cyan / Sky Blue</option>
                                    <option value="#FFD700">🏆 Royal Gold</option>
                                    <option value="#FFFFFF">⚪ Pure White</option>
                                    <option value="#FF00FF">Magenta / Hot Pink</option>
                                    <option value="#FF3333">🔥 Flame Red</option>
                                  </select>
                                </div>
                              </>
                            );
                          }
                          return null;
                        })()}
                      </div>
                    </>
                  )}
                </div>
              )}

              {subStatus.has_active_subscription ? (
                isAutoScheduleActive ? (
                  <button 
                    className="btn-hero-cta" 
                    style={{ width: '100%', padding: '14px', fontSize: '1rem', background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)', boxShadow: '0 4px 20px rgba(239, 68, 68, 0.4)' }}
                    onClick={() => setShowStopScheduleWarningModal(true)}
                  >
                    🛑 Stop Auto-Publishing Engine →
                  </button>
                ) : (
                  <button 
                    className="btn-hero-cta" 
                    disabled={isSavingSchedule}
                    style={{ width: '100%', padding: '14px', fontSize: '1rem', background: isSavingSchedule ? 'rgba(255,255,255,0.15)' : 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)', boxShadow: isSavingSchedule ? 'none' : '0 4px 20px rgba(6, 182, 212, 0.4)', opacity: isSavingSchedule ? 0.6 : 1, cursor: isSavingSchedule ? 'not-allowed' : 'pointer' }}
                    onClick={() => handleSaveAutoSchedule(true)}
                  >
                    {isSavingSchedule ? '⏳ Saving Settings to DB...' : '⚡ Start Auto-Publishing Engine →'}
                  </button>
                )
              ) : (
                <button 
                  className="btn-hero-cta" 
                  style={{ width: '100%', padding: '14px', fontSize: '0.92rem', background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)', boxShadow: '0 4px 20px rgba(239, 68, 68, 0.4)', opacity: 0.95 }}
                  onClick={() => {
                    setShowAutoUploadModal(false);
                    setShowPricingModal(true);
                  }}
                >
                  🔒 Active Membership Required — Click to Upgrade Plan & Unlock Auto-Schedule 💎
                </button>
              )}
            </div>

            <div style={{ textAlign: 'center' }}>
              <button className="button secondary" style={{ width: 'auto', padding: '8px 24px' }} onClick={() => setShowAutoUploadModal(false)}>
                Close Settings
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Stop Auto-Publishing Confirmation Warning Modal */}
      {showStopScheduleWarningModal && (
        <div className="pricing-modal-overlay" style={{ zIndex: 4000 }} onClick={() => setShowStopScheduleWarningModal(false)}>
          <div 
            style={{ 
              maxWidth: '460px', 
              width: '90%',
              padding: '32px 28px', 
              textAlign: 'center',
              background: 'rgba(255, 255, 255, 0.04)', 
              borderRadius: '24px', 
              border: '1px solid rgba(239, 68, 68, 0.45)', 
              boxShadow: '0 20px 50px rgba(239, 68, 68, 0.25)', 
              backdropFilter: 'blur(20px)',
              WebkitBackdropFilter: 'blur(20px)'
            }} 
            onClick={e => e.stopPropagation()}
          >
            <div style={{ fontSize: '3rem', marginBottom: '12px' }}>⚠️</div>
            <h3 style={{ color: '#ef4444', fontSize: '1.4rem', fontWeight: '800', marginBottom: '12px' }}>
              Stop Auto-Publishing Warning
            </h3>
            <p style={{ color: '#cbd5e1', fontSize: '0.92rem', lineHeight: '1.5', marginBottom: '24px' }}>
              If you stop auto-publishing now, your automated daily video generation and YouTube channel publishing will be <strong>completely STOPPED</strong>.<br/><br/>
              When you re-enable it in the future, you will need to re-configure your daily upload schedule. Are you sure you want to stop?
            </p>
            <div style={{ display: 'flex', gap: '12px' }}>
              <button 
                className="button secondary" 
                style={{ flex: 1, padding: '12px' }}
                onClick={() => setShowStopScheduleWarningModal(false)}
              >
                Cancel / Keep Active
              </button>
              <button 
                className="button" 
                style={{ flex: 1, padding: '12px', background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)', color: '#fff', border: 'none', fontWeight: 'bold' }}
                onClick={() => handleSaveAutoSchedule(false)}
              >
                🛑 Yes, Stop Everything Now
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Custom Glassmorphism Transparent Warning & Alert Modal */}
      {customAlert && (
        <div 
          className="pricing-modal-overlay" 
          style={{ zIndex: 5000, background: 'rgba(10, 7, 24, 0.45)', backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)' }}
          onClick={() => setCustomAlert(null)}
        >
          <div 
            style={{ 
              maxWidth: '460px', 
              width: '90%',
              padding: '36px 28px', 
              textAlign: 'center', 
              background: 'rgba(255, 255, 255, 0.04)', 
              borderRadius: '24px', 
              border: customAlert.type === 'danger' ? '1px solid rgba(239, 68, 68, 0.45)' : (customAlert.type === 'success' ? '1px solid rgba(34, 197, 94, 0.45)' : '1px solid rgba(168, 85, 247, 0.45)'), 
              boxShadow: customAlert.type === 'danger' ? '0 20px 50px rgba(239, 68, 68, 0.25)' : '0 20px 50px rgba(168, 85, 247, 0.25)', 
              backdropFilter: 'blur(20px)',
              WebkitBackdropFilter: 'blur(20px)'
            }} 
            onClick={e => e.stopPropagation()}
          >
            <div style={{ fontSize: '3.2rem', marginBottom: '14px', filter: 'drop-shadow(0 4px 12px rgba(0,0,0,0.5))' }}>
              {customAlert.icon || '⚠️'}
            </div>
            
            <h3 style={{ color: customAlert.type === 'danger' ? '#ef4444' : (customAlert.type === 'success' ? '#22c55e' : '#ffffff'), fontSize: '1.4rem', fontWeight: '800', marginBottom: '12px' }}>
              {customAlert.title}
            </h3>
            
            <div style={{ color: '#e2e8f0', fontSize: '0.92rem', lineHeight: '1.55', marginBottom: '28px', whiteSpace: 'pre-line' }}>
              {customAlert.message}
            </div>

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              {customAlert.onConfirm ? (
                <>
                  <button 
                    className="button secondary" 
                    style={{ flex: 1, padding: '12px', borderRadius: '12px', background: 'rgba(255, 255, 255, 0.08)', color: '#cbd5e1', border: '1px solid rgba(255, 255, 255, 0.15)' }}
                    onClick={() => setCustomAlert(null)}
                  >
                    {customAlert.cancelText || 'Cancel'}
                  </button>
                  <button 
                    className="button" 
                    style={{ 
                      flex: 1, 
                      padding: '12px', 
                      borderRadius: '12px', 
                      background: customAlert.type === 'danger' ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)' : 'linear-gradient(135deg, #a855f7 0%, #06b6d4 100%)', 
                      color: '#ffffff', 
                      border: 'none', 
                      fontWeight: 'bold',
                      boxShadow: '0 4px 15px rgba(0,0,0,0.3)'
                    }}
                    onClick={() => {
                      const cb = customAlert.onConfirm;
                      setCustomAlert(null);
                      if (cb) cb();
                    }}
                  >
                    {customAlert.confirmText || 'Confirm'}
                  </button>
                </>
              ) : (
                <button 
                  className="button" 
                  style={{ 
                    width: '100%', 
                    padding: '13px', 
                    borderRadius: '12px', 
                    background: customAlert.type === 'danger' ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)' : (customAlert.type === 'success' ? 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)' : 'linear-gradient(135deg, #a855f7 0%, #06b6d4 100%)'), 
                    color: '#ffffff', 
                    border: 'none', 
                    fontWeight: 'bold',
                    fontSize: '0.95rem'
                  }}
                  onClick={() => setCustomAlert(null)}
                >
                  {customAlert.confirmText || 'Got It →'}
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
