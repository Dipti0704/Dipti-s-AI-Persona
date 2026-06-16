import React, { useState } from 'react';
import { Bot, User, Code, Calendar, Mail, Phone, MapPin, ExternalLink, Globe } from 'lucide-react';
import ChatWidget from './components/ChatWidget';
import VoiceCall from './components/VoiceCall';
import Scheduler from './components/Scheduler';
import {
  candidateProfile,
  dashboardTabs,
} from './content/profile';

const tabIcons = {
  chat: Bot,
  voice: Phone,
  scheduler: Calendar,
};

// Official LinkedIn SVG Icon component due to brand icons removal in lucide-react 1.x
const LinkedInIcon = ({ size = 16, style }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="currentColor"
    width={size}
    height={size}
    style={style}
  >
    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.779-1.75-1.75s.784-1.75 1.75-1.75 1.75.779 1.75 1.75-.784 1.75-1.75 1.75zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
  </svg>
);

function CandidateSidebar() {
  return (
    <aside className="sidebar">
      <section className="glass-panel sidebar-card">
        <div className="section-title">
          <User size={18} color="var(--primary-indigo)" />
          <h3>Candidate Bio</h3>
        </div>

        <p>{candidateProfile.bio}</p>

        <div className="bio-facts">
          <div><strong>Education:</strong> {candidateProfile.education}</div>
          <div><strong>Internship:</strong> {candidateProfile.internship}</div>
        </div>
      </section>

      <section className="glass-panel sidebar-card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <div className="section-title">
          <Globe size={18} color="var(--accent-cyan)" />
          <h3>Personal Portfolio</h3>
        </div>
        
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
          Explore my detailed custom portfolio site containing all my active engineering projects, case studies, and live web apps.
        </p>

        <a 
          href={candidateProfile.portfolioUrl} 
          target="_blank" 
          rel="noopener noreferrer" 
          className="btn btn-primary"
          style={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            gap: '8px', 
            padding: '10px 16px',
            borderRadius: '10px',
            fontSize: '0.9rem',
            fontWeight: 600,
            textDecoration: 'none'
          }}
        >
          Visit dipti-things <ExternalLink size={14} />
        </a>
      </section>
    </aside>
  );
}

export default function App() {
  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
  const [activeTab, setActiveTab] = useState('chat');

  return (
    <div className="app-shell">
      <header className="glass-panel hero-header">
        <div className="identity-block">
          <div className="brand-avatar">
            <Bot size={34} color="#fff" />
          </div>
          <div>
            <h1>
              {candidateProfile.name}
              <span>{candidateProfile.title}</span>
            </h1>
            <p>
              <span>{candidateProfile.role}</span>
              <span className="dot-separator" />
              <span><MapPin size={14} /> {candidateProfile.location}</span>
            </p>
          </div>
        </div>

        <div className="header-actions">
          <a href={`mailto:${candidateProfile.email}`} className="btn btn-secondary">
            <Mail size={16} /> Email Dipti
          </a>
          <a href={candidateProfile.githubUrl} target="_blank" rel="noopener noreferrer" className="btn btn-secondary">
            <Code size={16} /> GitHub <ExternalLink size={12} />
          </a>
          <a href={candidateProfile.linkedinUrl} target="_blank" rel="noopener noreferrer" className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <LinkedInIcon size={16} style={{ color: '#0a66c2' }} /> LinkedIn <ExternalLink size={12} />
          </a>
        </div>
      </header>

      <main className="dashboard-layout">
        <div className="workspace">
          <nav className="tab-bar" aria-label="Dashboard sections">
            {dashboardTabs.map((tab) => {
              const Icon = tabIcons[tab.id];
              const isActive = activeTab === tab.id;

              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`btn tab-button ${isActive ? 'active' : ''}`}
                  type="button"
                >
                  <Icon size={16} /> {tab.label}
                </button>
              );
            })}
          </nav>

          {activeTab === 'chat' && <ChatWidget backendUrl={backendUrl} />}
          {activeTab === 'voice' && <VoiceCall />}
          {activeTab === 'scheduler' && <Scheduler backendUrl={backendUrl} />}
        </div>

        <CandidateSidebar />
      </main>

      <footer className="app-footer">
        System architecture: FastAPI backend | React + Vite UI | RAG vector pipeline | Vapi webhook integrations
      </footer>
    </div>
  );
}
