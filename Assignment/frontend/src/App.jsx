import React, { useState } from 'react';
import { Bot, User, Code, Calendar, Mail, Phone, MapPin, ExternalLink } from 'lucide-react';
import ChatWidget from './components/ChatWidget';
import VoiceCall from './components/VoiceCall';
import Scheduler from './components/Scheduler';
import {
  candidateProfile,
  dashboardTabs,
  portfolioProjects,
} from './content/profile';

const tabIcons = {
  chat: Bot,
  voice: Phone,
  scheduler: Calendar,
};

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
          <div><strong>Cell Secretary:</strong> {candidateProfile.responsibility}</div>
        </div>
      </section>

      <section className="glass-panel sidebar-card">
        <div className="section-title">
          <Code size={18} color="var(--accent-cyan)" />
          <h3>GitHub Portfolios</h3>
        </div>

        <div className="project-list">
          {portfolioProjects.map((project) => (
            <article key={project.name} className="project-card">
              <div className="project-title-row">
                <h4>{project.name}</h4>
                <span>{project.tag}</span>
              </div>
              <p>{project.desc}</p>
              <div>Stack: {project.stack}</div>
            </article>
          ))}
        </div>
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
            <Code size={16} /> GitHub Profile <ExternalLink size={12} />
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
