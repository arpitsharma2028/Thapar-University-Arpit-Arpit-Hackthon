import React from 'react';
import {
  LayoutDashboard,
  Cpu,
  TrendingUp,
  ShieldAlert,
  Database,
  History,
  Activity,
  Award,
  Sparkles
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const menuItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'risk-engine', label: 'Risk Intelligence', icon: Cpu },
    { id: 'module-a', label: 'Module A — Rebalancer', icon: TrendingUp },
    { id: 'module-b', label: 'Module B — Stress Testing', icon: ShieldAlert },
    { id: 'market-intel', label: 'Market Analytics & Forecast', icon: Sparkles },
    { id: 'events', label: 'Event Explorer', icon: Database },
    { id: 'history', label: 'Simulation History', icon: History },
  ];

  return (
    <aside style={{
      width: '260px',
      background: 'var(--bg-secondary)',
      borderRight: '1px solid var(--border-color)',
      display: 'flex',
      flexDirection: 'column',
      minHeight: '100vh',
      flexShrink: 0
    }}>
      {/* Platform Branding Header */}
      <div style={{ padding: '24px 20px', borderBottom: '1px solid var(--border-color)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '38px',
            height: '38px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #2563eb, #7c3aed)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(37, 99, 235, 0.4)'
          }}>
            <Activity size={22} color="#ffffff" />
          </div>
          <div>
            <div style={{ fontWeight: 800, fontSize: '1.15rem', letterSpacing: '-0.02em', color: '#f8fafc' }}>
              FinSight <span style={{ color: '#38bdf8' }}>AI</span>
            </div>
            <div style={{ fontSize: '0.68rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Risk Intelligence
            </div>
          </div>
        </div>

        {/* Hackathon Badge */}
        <div style={{
          marginTop: '16px',
          background: 'rgba(245, 158, 11, 0.1)',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          borderRadius: '8px',
          padding: '8px 10px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <Award size={16} color="#f59e0b" />
          <div style={{ fontSize: '0.72rem', color: '#fcd34d', fontWeight: 600 }}>
            S&P Global & CRISIL 2026
          </div>
        </div>
      </div>

      {/* Navigation List */}
      <nav style={{ padding: '16px 12px', flex: 1 }}>
        <div style={{ fontSize: '0.68rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.06em', padding: '0 8px 10px' }}>
          Platform Modules
        </div>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '11px 14px',
                borderRadius: '8px',
                marginBottom: '4px',
                fontSize: '0.84rem',
                fontWeight: isActive ? 600 : 500,
                color: isActive ? '#ffffff' : '#94a3b8',
                background: isActive ? 'linear-gradient(90deg, rgba(37, 99, 235, 0.25), rgba(37, 99, 235, 0.05))' : 'transparent',
                border: isActive ? '1px solid rgba(59, 130, 246, 0.4)' : '1px solid transparent',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s ease'
              }}
            >
              <Icon size={17} color={isActive ? '#38bdf8' : '#64748b'} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Status Footer with User Name and Campus */}
      <div style={{
        padding: '16px 20px',
        borderTop: '1px solid var(--border-color)',
        background: 'rgba(10, 14, 23, 0.6)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981', display: 'inline-block', boxShadow: '0 0 8px #10b981' }}></span>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#e2e8f0' }}>Backend Online</span>
        </div>
        <div style={{ fontSize: '0.72rem', color: '#38bdf8', fontWeight: 600 }}>
          Candidate: Arpit Sharma
        </div>
        <div style={{ fontSize: '0.65rem', color: '#64748b', marginTop: '2px' }}>
          Thapar Institute of Engg & Tech
        </div>
      </div>
    </aside>
  );
}
