import React from 'react';
import {
  LayoutDashboard,
  Cpu,
  TrendingUp,
  ShieldAlert,
  Database,
  History,
  Activity,
  BarChart2,
  ShieldCheck
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const menuItems = [
    { id: 'overview', label: 'Executive Overview', icon: LayoutDashboard },
    { id: 'risk-engine', label: 'NLP Risk Intelligence', icon: Cpu },
    { id: 'module-a', label: 'Module A — Index Rebalancer', icon: TrendingUp },
    { id: 'module-b', label: 'Module B — Wholesale Stress Test', icon: ShieldAlert },
    { id: 'market-intel', label: 'Market Analytics & Forecast', icon: BarChart2 },
    { id: 'events', label: 'Event Signal Explorer', icon: Database },
    { id: 'history', label: 'Audit Trail & History', icon: History },
  ];

  return (
    <aside className="glass-sidebar">
      {/* Branding */}
      <div style={{ padding: '20px 20px 18px', borderBottom: '1px solid var(--glass-border-subtle)' }}>

        <div style={{ display: 'flex', alignItems: 'center', gap: '11px' }}>
          <div style={{
            width: '38px',
            height: '38px',
            borderRadius: '11px',
            background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.22) 0%, rgba(200, 205, 215, 0.10) 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid rgba(255, 255, 255, 0.32)',
            boxShadow: '0 4px 14px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.35)'
          }}>
            <Activity size={20} color="#f5f5f7" />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '1.12rem', letterSpacing: '-0.03em', color: '#f5f5f7' }}>
              FinSight <span style={{ color: '#ffffff', fontWeight: 800 }}>AI</span>
            </div>
            <div style={{ fontSize: '0.66rem', color: '#b9bbc1', textTransform: 'uppercase', letterSpacing: '0.07em', fontWeight: 600 }}>
              Liquid Glass Desk
            </div>
          </div>
        </div>

        {/* Institutional Desk Status Badge in Silver Glass */}
        <div style={{
          marginTop: '16px',
          background: 'rgba(255, 255, 255, 0.06)',
          border: '1px solid var(--glass-border-subtle)',
          backdropFilter: 'blur(10px)',
          WebkitBackdropFilter: 'blur(10px)',
          borderRadius: '9px',
          padding: '7px 10px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.10)'
        }}>
          <ShieldCheck size={14} color="#e2e4e9" />
          <div style={{ fontSize: '0.68rem', color: '#d1d3d8', fontWeight: 600, letterSpacing: '0.02em' }}>
            Multi-Asset Risk Desk • visionOS
          </div>
        </div>
      </div>

      {/* Navigation List */}
      <nav style={{ padding: '16px 12px', flex: 1, overflowY: 'auto' }}>
        <div style={{ fontSize: '0.66rem', color: '#858890', textTransform: 'uppercase', letterSpacing: '0.08em', padding: '0 8px 10px', fontWeight: 600 }}>
          Workstation Modules
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
                gap: '11px',
                padding: '10px 13px',
                borderRadius: '10px',
                marginBottom: '4px',
                fontSize: '0.83rem',
                fontWeight: isActive ? 600 : 500,
                color: isActive ? '#ffffff' : '#9ca3af',
                background: isActive
                  ? 'linear-gradient(135deg, rgba(255, 255, 255, 0.24) 0%, rgba(255, 255, 255, 0.08) 100%)'
                  : 'transparent',
                border: isActive ? '1px solid rgba(255, 255, 255, 0.42)' : '1px solid transparent',
                boxShadow: isActive
                  ? '0 6px 20px rgba(0, 0, 0, 0.18), inset 0 1px 0 rgba(255, 255, 255, 0.55)'
                  : 'none',
                cursor: 'pointer',
                textAlign: 'left',
                backdropFilter: isActive ? 'blur(16px)' : 'none',
                WebkitBackdropFilter: isActive ? 'blur(16px)' : 'none',
                transition: 'all var(--transition-fast)'
              }}
              onMouseEnter={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.10)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.25)';
                  e.currentTarget.style.color = '#ffffff';
                  e.currentTarget.style.transform = 'translateX(2px)';
                }
              }}
              onMouseLeave={(e) => {
                if (!isActive) {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.borderColor = 'transparent';
                  e.currentTarget.style.color = '#9ca3af';
                  e.currentTarget.style.transform = 'translateX(0)';
                }
              }}
            >
              <Icon size={16} color={isActive ? '#ffffff' : '#8e8e93'} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Silver Status Footer */}
      <div style={{
        padding: '14px 18px',
        borderTop: '1px solid var(--glass-border-subtle)',
        background: 'rgba(255, 255, 255, 0.02)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '3px' }}>
          <span style={{ width: '7px', height: '7px', borderRadius: '50%', background: 'var(--accent-positive)', display: 'inline-block', boxShadow: '0 0 8px var(--accent-positive)' }}></span>
          <span style={{ fontSize: '0.74rem', fontWeight: 600, color: '#f5f5f7' }}>Production Engine Active</span>
        </div>
        <div style={{ fontSize: '0.70rem', color: '#b9bbc1', fontWeight: 600 }}>
          Lead Risk Engineer: Arpit Sharma
        </div>
        <div style={{ fontSize: '0.64rem', color: '#858890', marginTop: '1px' }}>
          TIET Quantitative Research • v1.1.0
        </div>
      </div>
    </aside>
  );
}
