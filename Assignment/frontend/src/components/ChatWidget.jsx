import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Cpu } from 'lucide-react';

export default function ChatWidget({ backendUrl }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hello! I am Dipti's AI Representative. I am fully grounded in her resume and GitHub repositories. Ask me about her education, professional experiences, deep architectural decisions on her projects, or book a calendar meeting directly with me! How can I help you today?"
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [toolLogs, setToolLogs] = useState([]);
  const chatEndRef = useRef(null);

  const typingQueueRef = useRef("");
  const typingIntervalRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  useEffect(() => {
    return () => {
      if (typingIntervalRef.current) clearInterval(typingIntervalRef.current);
    };
  }, []);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);
    setToolLogs([]);

    // Clear any active typing interval from a previous response
    if (typingIntervalRef.current) {
      clearInterval(typingIntervalRef.current);
      typingIntervalRef.current = null;
    }
    typingQueueRef.current = "";

    try {
      const response = await fetch(`${backendUrl}/api/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          history: messages.slice(-10) // Send last 10 messages for memory context
        })
      });

      if (!response.ok) throw new Error('Failed to fetch response');
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      let isStreamingActive = true;
      let currentText = "";

      // Push an empty assistant message first that we will stream into
      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      // Start the smooth typewriter effect interval
      typingIntervalRef.current = setInterval(() => {
        if (typingQueueRef.current.length > 0) {
          // Dynamic batch size to catch up if text generation is extremely fast (bursts)
          const batchSize = typingQueueRef.current.length > 60 ? 4 : (typingQueueRef.current.length > 30 ? 2 : 1);
          const nextChars = typingQueueRef.current.substring(0, batchSize);
          typingQueueRef.current = typingQueueRef.current.substring(batchSize);
          currentText += nextChars;

          setMessages(prev => {
            const updated = [...prev];
            updated[updated.length - 1] = { role: 'assistant', content: currentText };
            return updated;
          });
        } else if (!isStreamingActive) {
          clearInterval(typingIntervalRef.current);
          typingIntervalRef.current = null;
        }
      }, 15); // Print a character roughly every 15ms

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        // Save the last element (which could be a partial line) back to buffer
        buffer = lines.pop();

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const dataJson = JSON.parse(line.substring(6));
              
              // Update logs if tools were called
              if (dataJson.tool_calls && dataJson.tool_calls.length > 0) {
                setToolLogs(dataJson.tool_calls.map(tc => `Tool Triggered: ${tc.name}(${JSON.stringify(tc.args)})`));
              }

              // Queue text chunks for the typewriter instead of writing immediately
              if (dataJson.text) {
                typingQueueRef.current += dataJson.text;
              }
            } catch (err) {
              console.warn("Failed to parse stream event chunk:", err, line);
            }
          }
        }
      }

      isStreamingActive = false;
    } catch (error) {
      console.error(error);
      if (typingIntervalRef.current) {
        clearInterval(typingIntervalRef.current);
        typingIntervalRef.current = null;
      }
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: "I apologize, but I encountered a communication error with my backend services. Please make sure the FastAPI server is running locally on port 8000." 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="glass-panel chat-container" style={{ display: 'flex', flexDirection: 'column', height: '550px', overflow: 'hidden' }}>
      {/* Header */}
      <div className="chat-header" style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-glass)', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div className="avatar-glow" style={{ width: '38px', height: '38px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--primary-indigo) 0%, var(--secondary-purple) 100%)', display: 'flex', alignItems: 'center', justifySelf: 'center', justifyContent: 'center' }}>
          <Bot size={20} color="#fff" />
        </div>
        <div>
          <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.05rem', fontWeight: 600 }}>Chat Representative</h3>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#10b981', display: 'inline-block' }}></span>
            Grounded RAG Agent
          </span>
        </div>
      </div>

      {/* Messages Window */}
      <div className="chat-messages" style={{ flex: 1, padding: '20px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {messages.map((msg, index) => {
          const isAI = msg.role === 'assistant';
          return (
            <div key={index} style={{ display: 'flex', gap: '12px', alignSelf: isAI ? 'flex-start' : 'flex-end', maxWidth: '85%', flexDirection: isAI ? 'row' : 'row-reverse' }}>
              <div style={{ 
                width: '32px', 
                height: '32px', 
                borderRadius: '50%', 
                background: isAI ? 'rgba(99, 102, 241, 0.15)' : 'rgba(255, 255, 255, 0.08)',
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                flexShrink: 0,
                border: isAI ? '1px solid var(--border-glass-glow)' : '1px solid var(--border-glass)'
              }}>
                {isAI ? <Bot size={16} color="var(--primary-indigo)" /> : <User size={16} color="#fff" />}
              </div>
              <div style={{
                background: isAI ? 'rgba(255, 255, 255, 0.03)' : 'linear-gradient(135deg, var(--primary-indigo) 0%, var(--secondary-purple) 100%)',
                padding: '12px 18px',
                borderRadius: '16px',
                border: isAI ? '1px solid var(--border-glass)' : 'none',
                fontSize: '0.92rem',
                lineHeight: 1.5,
                color: '#f8fafc',
                whiteSpace: 'pre-wrap'
              }}>
                {msg.content}
              </div>
            </div>
          );
        })}
        {isLoading && (
          <div style={{ display: 'flex', gap: '12px', alignSelf: 'flex-start' }}>
            <div style={{ 
              width: '32px', height: '32px', borderRadius: '50%', background: 'rgba(99, 102, 241, 0.15)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid var(--border-glass-glow)'
            }}>
              <Bot size={16} className="pulse-animation" color="var(--primary-indigo)" />
            </div>
            <div className="typing-bubble" style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '12px 18px', borderRadius: '16px', border: '1px solid var(--border-glass)' }}>
              <span className="dot"></span>
              <span className="dot" style={{ animationDelay: '0.2s' }}></span>
              <span className="dot" style={{ animationDelay: '0.4s' }}></span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Real-time Agent Execution logs */}
      {toolLogs.length > 0 && (
        <div style={{ background: 'rgba(6, 182, 212, 0.05)', padding: '8px 16px', borderTop: '1px solid rgba(6, 182, 212, 0.15)', borderBottom: '1px solid rgba(6, 182, 212, 0.15)', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.75rem', color: '#06b6d4' }}>
          <Cpu size={14} className="spin-animation" />
          <span>{toolLogs.join(' | ')}</span>
        </div>
      )}

      {/* Input bar */}
      <form onSubmit={handleSend} style={{ padding: '16px 20px', borderTop: '1px solid var(--border-glass)', display: 'flex', gap: '10px' }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about projects, education, skills, or booking slots..."
          style={{
            flex: 1,
            background: 'var(--bg-input-glass)',
            border: '1px solid var(--border-glass)',
            padding: '12px 16px',
            borderRadius: '12px',
            color: '#fff',
            outline: 'none',
            fontSize: '0.9rem',
            transition: 'border-color 0.2s'
          }}
          onFocus={(e) => e.target.style.borderColor = 'var(--primary-indigo)'}
          onBlur={(e) => e.target.style.borderColor = 'var(--border-glass)'}
        />
        <button type="submit" className="btn btn-primary" style={{ padding: '12px', borderRadius: '12px' }} aria-label="Send message">
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}
