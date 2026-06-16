import React, { useState, useEffect } from 'react';
import { Phone, Mic, MicOff, Volume2, Info, ArrowUpRight } from 'lucide-react';
import VapiModule from '@vapi-ai/web';
const Vapi = VapiModule.default || VapiModule;

export default function VoiceCall() {
  const [vapi, setVapi] = useState(null);
  const [callActive, setCallActive] = useState(false);
  const [vapiStatus, setVapiStatus] = useState('offline');
  const [volume, setVolume] = useState([10, 10, 10, 10, 10]);

  const VAPI_PUBLIC_KEY = import.meta.env.VITE_VAPI_PUBLIC_KEY;
  const VAPI_ASSISTANT_ID = import.meta.env.VITE_VAPI_ASSISTANT_ID;
  const isVoiceConfigured = Boolean(VAPI_PUBLIC_KEY && VAPI_ASSISTANT_ID);

  useEffect(() => {
    if (!isVoiceConfigured) {
      setVapiStatus('Setup Required');
      return;
    }

    try {
      const vapiInstance = new Vapi(VAPI_PUBLIC_KEY);
      setVapi(vapiInstance);
      
      vapiInstance.on('speech-start', () => setVapiStatus('AI Speaking...'));
      vapiInstance.on('speech-end', () => setVapiStatus('Listening...'));
      vapiInstance.on('call-start', () => {
        setCallActive(true);
        setVapiStatus('Connected');
      });
      vapiInstance.on('call-end', () => {
        setCallActive(false);
        setVapiStatus('Offline');
      });
      vapiInstance.on('volume-level', (vol) => {
        // Map volume float (0.0 to 1.0) to 5 visual bars (10px to 45px)
        const val = Math.floor(vol * 35) + 10;
        setVolume([
          Math.max(10, val - 8),
          Math.max(10, val - 3),
          val,
          Math.max(10, val - 3),
          Math.max(10, val - 8)
        ]);
      });
    } catch (err) {
      console.error("Vapi failed to load:", err);
      setVapiStatus('Setup Error');
    }
  }, [VAPI_PUBLIC_KEY, isVoiceConfigured]);

  const handleCall = async () => {
    if (!isVoiceConfigured) {
      setVapiStatus('Missing Vapi Env Vars');
      return;
    }
    if (!vapi) return;
    
    if (callActive) {
      vapi.stop();
    } else {
      setVapiStatus('Connecting...');
      try {
        await vapi.start(VAPI_ASSISTANT_ID);
      } catch (err) {
        console.error(err);
        setVapiStatus('Call Failed');
      }
    }
  };

  return (
    <div className="glass-panel voice-call-card" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '14px', height: '420px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '1px solid var(--border-glass)', paddingBottom: '10px' }}>
        <Phone size={20} color="var(--secondary-purple)" />
        <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.1rem', fontWeight: 600 }}>Dipti's AI Voice Representative</h3>
      </div>

      {/* Main visual sphere panel */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: '24px' }}>
        <div 
          className={callActive ? "avatar-glow call-ringing" : "avatar-glow"}
          style={{
            position: 'relative',
            width: '80px',
            height: '80px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, var(--primary-indigo) 0%, var(--secondary-purple) 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: callActive ? '0 0 40px rgba(168,85,247,0.5)' : 'none',
            transition: 'all 0.5s',
            flexShrink: 0
          }}
        >
          {callActive ? <Mic size={32} color="#fff" /> : <Phone size={32} color="#fff" />}
          
          {/* Pulsing ring animations */}
          {callActive && (
            <>
              <div className="pulse-ring" style={{ animationDelay: '0s' }}></div>
              <div className="pulse-ring" style={{ animationDelay: '0.6s' }}></div>
            </>
          )}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1 }}>
          {/* Dynamic Status Text */}
          <div>
            <div style={{ textTransform: 'uppercase', letterSpacing: '1.5px', fontSize: '0.65rem', color: 'var(--text-muted)' }}>Status</div>
            <h4 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.05rem', color: callActive ? 'var(--accent-cyan)' : '#fff', fontWeight: 600, marginTop: '1px' }}>
              {vapiStatus.toUpperCase()}
            </h4>
          </div>

          {/* Audio Visualizer Waves */}
          {callActive ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '3px', height: '30px' }}>
              {volume.map((h, i) => (
                <div 
                  key={i} 
                  style={{ 
                    width: '3px', 
                    height: `${h * 0.6}px`, 
                    borderRadius: '1.5px', 
                    background: 'var(--accent-cyan)',
                    transition: 'height 0.1s ease',
                    boxShadow: '0 0 6px rgba(6,182,212,0.4)'
                  }}
                />
              ))}
            </div>
          ) : (
            <div style={{ height: '30px', display: 'flex', alignItems: 'center', fontSize: '0.78rem', color: 'var(--text-dimmed)' }}>
              Microphone offline
            </div>
          )}
        </div>
      </div>

      {/* Twilio Telephony Access Card - Highlighted & Glowing */}
      <div style={{ 
        background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(168, 85, 247, 0.12) 100%)', 
        border: '1px solid rgba(168, 85, 247, 0.35)', 
        padding: '12px 16px', 
        borderRadius: '12px', 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '6px',
        boxShadow: '0 4px 20px 0 rgba(168, 85, 247, 0.08)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Subtle background glow circle */}
        <div style={{
          position: 'absolute',
          top: '-20px',
          right: '-25px',
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          background: 'var(--secondary-purple)',
          filter: 'blur(25px)',
          opacity: 0.15,
          pointerEvents: 'none'
        }} />

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Direct Telephony Line (Twilio)
          </span>
          <ArrowUpRight size={14} color="var(--accent-cyan)" />
        </div>
        
        <div style={{ 
          fontSize: '1.4rem', 
          fontFamily: 'var(--font-heading)', 
          fontWeight: 800, 
          background: 'linear-gradient(to right, #38bdf8, #a78bfa)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          letterSpacing: '0.5px',
          margin: '1px 0'
        }}>
          +1 (984) 256-8289
        </div>
        
        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'flex', gap: '4px', alignItems: 'center' }}>
          <Info size={11} style={{ flexShrink: 0, color: 'var(--accent-cyan)' }} />
          <span>Call from your cell phone to speak with Dipti's AI voice agent live!</span>
        </div>
      </div>

      {/* Call controller button */}
      <button 
        onClick={handleCall}
        className={callActive ? "btn btn-secondary" : "btn btn-primary"}
        style={{ width: '100%', height: '42px', borderRadius: '10px', fontSize: '0.85rem' }}
        disabled={!isVoiceConfigured}
      >
        {callActive ? (
          <>
            <MicOff size={14} /> End Call Session
          </>
        ) : (
          <>
            <Volume2 size={14} /> Talk to Representative on Web
          </>
        )}
      </button>
    </div>
  );
}
