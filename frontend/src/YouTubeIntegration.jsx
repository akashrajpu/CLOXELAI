import React, { useState, useEffect } from 'react';

const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';

function YouTubeIntegration({ userId, hasActiveSubscription, onUpgradeClick, onStatusChange, triggerAlert, compact = false }) {
  const [status, setStatus] = useState(() => {
    try {
      if (userId) {
        const cached = localStorage.getItem(`yt_status_cache_${userId}`);
        if (cached) {
          const parsed = JSON.parse(cached);
          if (parsed && typeof parsed === 'object') return parsed;
        }
      }
    } catch(e) {}
    return null;
  });
  const [isLoading, setIsLoading] = useState(() => !status);
  const [isActionPending, setIsActionPending] = useState(false);
  const [error, setError] = useState(null);

  const fetchStatus = async () => {
    if (!userId) return;
    if (!status) setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/youtube/status/${userId}`);
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
        try { localStorage.setItem(`yt_status_cache_${userId}`, JSON.stringify(data)); } catch(e) {}
        if (onStatusChange) onStatusChange(data);
      }
    } catch (err) {
      setError("Failed to fetch YouTube status");
      if (!status) setStatus({ linked: false });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, [userId]);

  const handleLink = async () => {
    if (isActionPending) return;
    if (!hasActiveSubscription) {
      if (triggerAlert) {
        triggerAlert(
          "Active Membership Required",
          "Connecting a YouTube account is exclusive to active paid members. Please upgrade your plan first!",
          "🔒",
          "danger",
          onUpgradeClick,
          "Upgrade Plan →"
        );
      } else {
        alert("🔒 Active Paid Membership Required! Please upgrade your plan first.");
        if (onUpgradeClick) onUpgradeClick();
      }
      return;
    }

    setIsActionPending(true);
    try {
      const response = await fetch(`${API_BASE}/youtube/auth-url?internal_id=${userId}`);
      const data = await response.json();
      
      if (!response.ok) {
        setIsActionPending(false);
        if (triggerAlert) {
          triggerAlert("YouTube Error", data.detail || "Error connecting to YouTube API.", "⚠️", "danger");
        } else {
          alert(data.detail || "Error connecting to YouTube API.");
        }
        return;
      }
      
      if (data.auth_url) {
        window.location.href = data.auth_url;
      } else {
        setIsActionPending(false);
      }
    } catch (err) {
      setIsActionPending(false);
      alert("Failed to get authorization URL. Is the backend running?");
    }
  };

  const handleUnlink = async () => {
    if (isActionPending) return;
    if (!window.confirm("⚠️ Warning: Unlinking YouTube will STOP Auto-Publishing and ERASE all saved schedule settings. Are you sure you want to proceed?")) return;
    
    setIsActionPending(true);
    try {
      const response = await fetch(`${API_BASE}/youtube/unlink`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ internal_id: userId })
      });
      
      const data = await response.json();
      if (!response.ok) {
        if (triggerAlert) {
          triggerAlert("Unlink Error", data.detail || "Failed to unlink YouTube account.", "⚠️", "danger");
        } else {
          alert(data.detail || "Failed to unlink");
        }
      } else {
        if (triggerAlert) {
          triggerAlert(
            "🛑 YouTube Unlinked & Schedule Reset",
            "YouTube channel unlinked successfully! Auto-publishing has been STOPPED and all Short, Long, and Ultra schedule data has been WIPED OUT. Re-connect YouTube in the future to set up a new schedule.",
            "🛑",
            "info"
          );
        } else {
          alert("YouTube account unlinked! Auto-publishing stopped and all schedule data reset.");
        }
        fetchStatus();
        if (onStatusChange) onStatusChange({ linked: false, unlinked_reset: true });
      }
    } catch (err) {
      if (triggerAlert) {
        triggerAlert("Error", "Error unlinking account. Is the backend running?", "⚠️", "danger");
      } else {
        alert("Error unlinking account");
      }
    } finally {
      setIsActionPending(false);
    }
  };

  const handleTestUpload = async () => {
    setIsActionPending(true);
    try {
      const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://cloxelai.onrender.com';
      const response = await fetch(`${API_BASE}/test-youtube-upload`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ internal_id: userId })
      });
      const data = await response.json();
      if (response.ok && data.youtube_url) {
        if (triggerAlert) {
          triggerAlert("🎉 YouTube Demo Upload Successful!", `Video uploaded live to your channel!\n\nYouTube URL: ${data.youtube_url}`, "🎉", "success");
        } else {
          alert(`Demo Video uploaded to YouTube: ${data.youtube_url}`);
        }
      } else {
        if (triggerAlert) {
          triggerAlert("Upload Test Error", data.detail || "Failed to upload demo video.", "⚠️", "danger");
        } else {
          alert(data.detail || "Upload test failed.");
        }
      }
    } catch (err) {
      if (triggerAlert) {
        triggerAlert("Error", "Error triggering test upload to YouTube.", "⚠️", "danger");
      } else {
        alert("Error triggering test upload");
      }
    } finally {
      setIsActionPending(false);
    }
  };

  if (isLoading) return <div className="yt-card" style={{ padding: compact ? '10px' : '20px', fontSize: '0.85rem' }}>Checking YouTube connection...</div>;

  if (compact) {
    return (
      <div className="yt-card compact" style={{ padding: '12px 14px', borderRadius: '14px', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ fontSize: '0.88rem', fontWeight: 'bold', color: '#ffffff', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span>📺 YouTube Channel</span>
          </div>
          {status && status.linked && (
            <span style={{ background: 'rgba(34, 197, 94, 0.2)', color: '#22c55e', border: '1px solid rgba(34, 197, 94, 0.4)', padding: '2px 8px', borderRadius: '999px', fontSize: '0.72rem', fontWeight: 'bold' }}>
              ✅ Linked
            </span>
          )}
        </div>

        {status && status.linked ? (
          <>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '6px' }}>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Connected for Auto-Upload</span>
              <button 
                className={`btn-unlink ${!status.can_unlink || isActionPending ? 'disabled' : ''}`}
                onClick={handleUnlink}
                disabled={!status.can_unlink || isActionPending}
                style={{ padding: '4px 10px', fontSize: '0.75rem', opacity: isActionPending ? 0.6 : 1 }}
              >
                {isActionPending ? '⏳ Unlinking...' : 'Unlink'}
              </button>
            </div>
            <button
              type="button"
              onClick={handleTestUpload}
              disabled={isActionPending}
              style={{ width: '100%', marginTop: '8px', padding: '6px', fontSize: '0.75rem', fontWeight: 'bold', background: 'linear-gradient(135deg, #059669 0%, #10b981 100%)', color: '#ffffff', border: 'none', borderRadius: '8px', cursor: isActionPending ? 'not-allowed' : 'pointer', opacity: isActionPending ? 0.6 : 1 }}
            >
              {isActionPending ? '⏳ Uploading Demo to YouTube...' : '⚡ Instant Demo Upload Test (For Video)'}
            </button>
          </>
        ) : (
          <button 
            className="btn-yt-link" 
            onClick={handleLink}
            disabled={isActionPending}
            style={{ width: '100%', padding: '8px', fontSize: '0.85rem', fontWeight: 'bold', background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)', color: '#fff', border: 'none', borderRadius: '8px', cursor: isActionPending ? 'not-allowed' : 'pointer', marginTop: '8px', opacity: isActionPending ? 0.6 : 1 }}
          >
            {isActionPending ? '⏳ Connecting...' : '📺 Link YouTube Account'}
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="yt-card">
      <h3>YouTube Auto-Upload</h3>
      <p className="yt-desc">Connect your YouTube account to automatically upload generated videos directly to your channel.</p>
      
      {status && status.linked ? (
        <div className="yt-status linked">
          <div className="yt-badge">✅ YouTube Account Linked</div>
          
          <div className="yt-actions">
            <button 
              className={`btn-unlink ${!status.can_unlink ? 'disabled' : ''}`}
              onClick={handleUnlink}
              disabled={!status.can_unlink}
            >
              Unlink Account
            </button>
            
            {!status.can_unlink && (
              <div className="yt-lock-msg">
                🔒 Locked for security. You can unlink in {status.hours_left} hours.
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="yt-status unlinked">
          <button className="btn-yt-link" onClick={handleLink}>
            Link YouTube Account
          </button>
          <div className="yt-security-note">
            Your credentials are kept strictly on our secure servers.
          </div>
        </div>
      )}
    </div>
  );
}

export default YouTubeIntegration;
