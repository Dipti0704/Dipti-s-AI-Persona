import React, { useState, useEffect } from 'react';
import { Calendar, Clock, User, Mail, CheckCircle2, AlertCircle, CalendarRange } from 'lucide-react';

export default function Scheduler({ backendUrl }) {
  const [selectedDate, setSelectedDate] = useState('');
  const [slots, setSlots] = useState([]);
  const [selectedTime, setSelectedTime] = useState('');
  
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  
  const [datesList, setDatesList] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [bookingResult, setBookingResult] = useState(null);
  const [error, setError] = useState('');

  // Generate next 5 workdays (skipping Saturday & Sunday)
  useEffect(() => {
    const list = [];
    let current = new Date();
    
    // Start generating from tomorrow
    while (list.length < 5) {
      current.setDate(current.getDate() + 1);
      const day = current.getDay();
      
      if (day !== 0 && day !== 6) { // Skip Sunday (0) and Saturday (6)
        const year = current.getFullYear();
        const month = String(current.getMonth() + 1).padStart(2, '0');
        const dateVal = String(current.getDate()).padStart(2, '0');
        
        const formattedDate = `${year}-${month}-${dateVal}`;
        const label = current.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
        list.push({ value: formattedDate, label });
      }
    }
    
    setDatesList(list);
    // Select first date by default
    if (list.length > 0) {
      setSelectedDate(list[0].value);
    }
  }, []);

  // Fetch slots whenever selectedDate changes
  useEffect(() => {
    if (!selectedDate) return;
    
    const fetchSlots = async () => {
      setIsLoading(true);
      setError('');
      setBookingResult(null);
      setSelectedTime('');
      
      try {
        const response = await fetch(`${backendUrl}/api/slots`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ date: selectedDate })
        });
        
        if (!response.ok) throw new Error("Could not retrieve available slots.");
        const data = await response.json();
        setSlots(data.slots || []);
      } catch (err) {
        console.error(err);
        setError("Error communicating with slot server. Is backend port 8000 online?");
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchSlots();
  }, [selectedDate, backendUrl]);

  const handleBooking = async (e) => {
    e.preventDefault();
    if (!selectedDate || !selectedTime || !name || !email) {
      setError('Please fill in all booking credentials.');
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${backendUrl}/api/book`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          date: selectedDate,
          time: selectedTime,
          name,
          email
        })
      });
      
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Booking failed.");
      }
      
      const data = await response.json();
      setBookingResult(data);
      
      // Clear inputs
      setName('');
      setEmail('');
      
      // Refresh slots
      const refreshResp = await fetch(`${backendUrl}/api/slots`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date: selectedDate })
      });
      const refreshData = await refreshResp.json();
      setSlots(refreshData.slots || []);
      
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to finalize booking.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="glass-panel scheduler-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px', minHeight: '550px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', borderBottom: '1px solid var(--border-glass)', paddingBottom: '16px' }}>
        <CalendarRange size={24} color="var(--primary-indigo)" />
        <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.2rem', fontWeight: 600 }}>Interview Scheduler</h3>
      </div>
      
      {bookingResult ? (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', flex: 1, textAlign: 'center', gap: '16px', animation: 'scaleUp 0.4s ease' }}>
          <CheckCircle2 size={64} color="#10b981" />
          <h4 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem', color: '#10b981', fontWeight: 600 }}>Booking Confirmed! 🚀</h4>
          <p style={{ fontSize: '0.92rem', color: 'var(--text-muted)', maxWidth: '320px', lineHeight: 1.5 }}>
            Dipti's AI representative has reserved your interview slot successfully.
          </p>
          <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-glass)', padding: '16px', borderRadius: '12px', width: '100%', maxWidth: '360px', display: 'flex', flexDirection: 'column', gap: '8px', textAlign: 'left' }}>
            <div style={{ fontSize: '0.85rem' }}><span style={{ color: 'var(--text-muted)' }}>Date:</span> <strong style={{ color: '#fff' }}>{bookingResult.date}</strong></div>
            <div style={{ fontSize: '0.85rem' }}><span style={{ color: 'var(--text-muted)' }}>Time:</span> <strong style={{ color: '#fff' }}>{bookingResult.time} (IST)</strong></div>
            <div style={{ fontSize: '0.85rem' }}><span style={{ color: 'var(--text-muted)' }}>Event Link:</span> <a href={bookingResult.meeting_link} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent-cyan)', textDecoration: 'none' }}>Launch Meeting 🔗</a></div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-dimmed)', marginTop: '4px' }}>A confirmation invite has been emailed.</div>
          </div>
          <button className="btn btn-secondary" onClick={() => setBookingResult(null)} style={{ marginTop: '10px' }}>Book Another Slot</button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '18px', flex: 1 }}>
          {/* Day selection */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 500 }}>1. Choose Date</label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '6px' }}>
              {datesList.map((dt) => (
                <button
                  key={dt.value}
                  onClick={() => setSelectedDate(dt.value)}
                  style={{
                    padding: '10px 4px',
                    borderRadius: '10px',
                    background: selectedDate === dt.value ? 'linear-gradient(135deg, var(--primary-indigo) 0%, var(--secondary-purple) 100%)' : 'rgba(255,255,255,0.03)',
                    border: selectedDate === dt.value ? 'none' : '1px solid var(--border-glass)',
                    color: '#fff',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    textAlign: 'center',
                    transition: 'all 0.2s'
                  }}
                >
                  {dt.label.split(',')[0]}
                  <div style={{ fontSize: '0.85rem', marginTop: '2px', opacity: 0.9 }}>{dt.label.split(' ')[2]}</div>
                </button>
              ))}
            </div>
          </div>
          
          {/* Available Slots */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 500 }}>2. Select Available Slot</label>
            {isLoading ? (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60px', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                <Clock size={16} className="spin-animation" style={{ marginRight: '8px' }} /> Checking availability...
              </div>
            ) : slots.length === 0 ? (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60px', border: '1px dashed var(--border-glass)', borderRadius: '10px', color: 'var(--text-dimmed)', fontSize: '0.85rem' }}>
                No slots available on this date.
              </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
                {slots.map((sl) => (
                  <button
                    key={sl}
                    onClick={() => setSelectedTime(sl)}
                    style={{
                      padding: '10px 8px',
                      borderRadius: '10px',
                      background: selectedTime === sl ? 'rgba(6, 182, 212, 0.15)' : 'rgba(255,255,255,0.02)',
                      border: selectedTime === sl ? '1px solid var(--accent-cyan)' : '1px solid var(--border-glass)',
                      color: selectedTime === sl ? 'var(--accent-cyan)' : '#fff',
                      fontSize: '0.85rem',
                      fontWeight: 500,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '6px',
                      transition: 'all 0.2s'
                    }}
                  >
                    <Clock size={12} />
                    {sl}
                  </button>
                ))}
              </div>
            )}
          </div>
          
          {/* Form Credentials */}
          {selectedTime && (
            <form onSubmit={handleBooking} style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: 'auto', animation: 'fadeIn 0.3s ease' }}>
              <div style={{ borderTop: '1px solid var(--border-glass)', paddingTop: '14px', marginBottom: '4px' }}>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Confirm Booking for <strong style={{ color: 'var(--accent-cyan)' }}>{selectedTime}</strong> on <strong>{selectedDate}</strong></span>
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <div style={{ flex: 1, position: 'relative' }}>
                  <User size={14} style={{ position: 'absolute', left: '12px', top: '12px', color: 'var(--text-dimmed)' }} />
                  <input
                    type="text"
                    placeholder="Your Name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    style={{
                      width: '100%',
                      background: 'var(--bg-input-glass)',
                      border: '1px solid var(--border-glass)',
                      padding: '10px 10px 10px 32px',
                      borderRadius: '10px',
                      color: '#fff',
                      fontSize: '0.82rem',
                      outline: 'none'
                    }}
                  />
                </div>
                <div style={{ flex: 1, position: 'relative' }}>
                  <Mail size={14} style={{ position: 'absolute', left: '12px', top: '12px', color: 'var(--text-dimmed)' }} />
                  <input
                    type="email"
                    placeholder="Your Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    style={{
                      width: '100%',
                      background: 'var(--bg-input-glass)',
                      border: '1px solid var(--border-glass)',
                      padding: '10px 10px 10px 32px',
                      borderRadius: '10px',
                      color: '#fff',
                      fontSize: '0.82rem',
                      outline: 'none'
                    }}
                  />
                </div>
              </div>
              
              {error && (
                <div style={{ color: '#ef4444', fontSize: '0.78rem', display: 'flex', alignItems: 'center', gap: '4px', background: 'rgba(239,68,68,0.05)', padding: '8px', borderRadius: '8px', border: '1px solid rgba(239,68,68,0.15)' }}>
                  <AlertCircle size={12} /> {error}
                </div>
              )}
              
              <button type="submit" className="btn btn-accent" style={{ width: '100%', padding: '10px' }}>Confirm Interview Appointment</button>
            </form>
          )}
        </div>
      )}
    </div>
  );
}
