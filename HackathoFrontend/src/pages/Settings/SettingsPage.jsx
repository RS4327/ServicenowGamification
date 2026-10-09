import React, { useState } from 'react'

import { useAuth } from '../../context/AuthContext.jsx'

import { useTheme } from '../../context/ThemeContext.jsx'



export default function SettingsPage() {

  const { user } = useAuth()

  const { theme } = useTheme()

  const [displayName, setDisplayName] = useState(user?.name || '')

  const [email, setEmail] = useState('manager@company.com')

  const [notifEmail, setNotifEmail] = useState(true)

  const [notifSLA, setNotifSLA] = useState(true)

  const [notifLeaderboard, setNotifLeaderboard] = useState(false)

  const [saved, setSaved] = useState(false)



  function handleSave(e) {

    e.preventDefault()

    setSaved(true)

    setTimeout(() => setSaved(false), 3000)

  }



  const inputStyle = {

    width: '100%', padding: '11px 14px',

    border: `1.5px solid ${theme.inputBorder}`, borderRadius: '10px',

    fontSize: '14px', color: theme.textPrimary, background: theme.inputBg,

    outline: 'none', transition: 'border-color 0.2s',

  }



  const card = {

    background: theme.cardBg, borderRadius: '14px',

    border: `1px solid ${theme.cardBorder}`, boxShadow: theme.cardShadow,

    backdropFilter: 'blur(20px)',

  }



  return (

    <div>

      <div style={{ marginBottom: '24px' }}>

        <h2 style={{ fontSize: '22px', fontWeight: 700, color: theme.textPrimary, marginBottom: '4px' }}>

          Account <span style={{ color: theme.accent }}>Settings</span>

        </h2>

        <p style={{ color: theme.textSecondary, fontSize: '14px' }}>Manage your account preferences</p>

      </div>



      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '16px' }}>

        {/* Main Settings */}

        <div style={{ ...card, padding: '28px' }}>

          <h3 style={{ fontSize: '16px', fontWeight: 700, color: theme.textPrimary, marginBottom: '20px' }}>Profile Settings</h3>

          <form onSubmit={handleSave}>

            {/* Avatar */}

            <div style={{

              display: 'flex', alignItems: 'center', gap: '16px',

              marginBottom: '24px', paddingBottom: '24px',

              borderBottom: `1px solid ${theme.cardBorder}`,

            }}>

              <div style={{

                width: '64px', height: '64px',

                background: theme.accentGrad,

                borderRadius: '16px',

                display: 'flex', alignItems: 'center', justifyContent: 'center',

                color: '#fff', fontWeight: 700, fontSize: '20px',

                boxShadow: `0 0 20px ${theme.accent}40`,

              }}>

                {user?.avatar || 'U'}

              </div>

              <div>

                <div style={{ fontWeight: 600, color: theme.textPrimary, marginBottom: '4px', fontSize: '15px' }}>{user?.name}</div>

                <div style={{ fontSize: '12px', color: theme.accent, marginBottom: '10px', textTransform: 'capitalize', fontWeight: 600 }}>{user?.role}</div>

                <button type="button" style={{

                  fontSize: '12px', padding: '5px 14px',

                  border: `1.5px solid ${theme.cardBorder}`, borderRadius: '8px',

                  background: theme.inputBg, color: theme.textSecondary, cursor: 'pointer',

                }}>

                  Change Photo

                </button>

              </div>

            </div>



            <div style={{ marginBottom: '16px' }}>

              <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: theme.textMuted, marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>

                Display Name

              </label>

              <input

                type="text" value={displayName}

                onChange={e => setDisplayName(e.target.value)}

                style={inputStyle}

                onFocus={e => e.target.style.borderColor = theme.accent}

                onBlur={e => e.target.style.borderColor = theme.inputBorder}

              />

            </div>



            <div style={{ marginBottom: '28px' }}>

              <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: theme.textMuted, marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>

                Email Address

              </label>

              <input

                type="email" value={email}

                onChange={e => setEmail(e.target.value)}

                style={inputStyle}

                onFocus={e => e.target.style.borderColor = theme.accent}

                onBlur={e => e.target.style.borderColor = theme.inputBorder}

              />

            </div>



            <h3 style={{ fontSize: '15px', fontWeight: 700, color: theme.textPrimary, marginBottom: '14px' }}>Notification Preferences</h3>



            {[

              { label: 'Email Notifications', desc: 'Receive daily performance digest via email', state: notifEmail, setState: setNotifEmail },

              { label: 'SLA Alerts', desc: 'Get notified when SLA compliance drops below threshold', state: notifSLA, setState: setNotifSLA },

              { label: 'Leaderboard Updates', desc: 'Receive weekly leaderboard ranking notifications', state: notifLeaderboard, setState: setNotifLeaderboard },

            ].map(item => (

              <div key={item.label} style={{

                display: 'flex', alignItems: 'center', justifyContent: 'space-between',

                padding: '14px 0', borderBottom: `1px solid ${theme.cardBorder}`,

              }}>

                <div>

                  <div style={{ fontSize: '14px', fontWeight: 500, color: theme.textPrimary, marginBottom: '2px' }}>{item.label}</div>

                  <div style={{ fontSize: '12px', color: theme.textSecondary }}>{item.desc}</div>

                </div>

                <div

                  onClick={() => item.setState(!item.state)}

                  style={{

                    width: '44px', height: '24px',

                    background: item.state ? theme.accent : theme.inputBorder,

                    borderRadius: '12px', position: 'relative',

                    transition: 'background 0.2s', cursor: 'pointer', flexShrink: 0,

                    boxShadow: item.state ? `0 0 8px ${theme.accent}50` : 'none',

                  }}

                >

                  <div style={{

                    position: 'absolute', top: '3px',

                    left: item.state ? '23px' : '3px',

                    width: '18px', height: '18px',

                    background: '#fff', borderRadius: '50%',

                    transition: 'left 0.2s',

                    boxShadow: '0 1px 3px rgba(0,0,0,0.2)',

                  }} />

                </div>

              </div>

            ))}



            <div style={{ marginTop: '24px', display: 'flex', alignItems: 'center', gap: '12px' }}>

              <button

                type="submit"

                style={{

                  padding: '11px 28px', background: theme.accentGrad, color: '#fff',

                  borderRadius: '10px', fontSize: '14px', fontWeight: 600,

                  border: 'none', cursor: 'pointer',

                  boxShadow: `0 4px 16px ${theme.accent}40`,

                  transition: 'all 0.2s',

                }}

                onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-1px)'; e.currentTarget.style.boxShadow = `0 8px 20px ${theme.accent}50` }}

                onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = `0 4px 16px ${theme.accent}40` }}

              >

                Save Changes

              </button>

              {saved && (

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: theme.success, fontSize: '14px', fontWeight: 600 }}>

                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">

                    <polyline points="20 6 9 17 4 12"/>

                  </svg>

                  Saved successfully

                </div>

              )}

            </div>

          </form>

        </div>



        {/* Side cards */}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>

          <div style={{ ...card, padding: '20px' }}>

            <h3 style={{ fontSize: '14px', fontWeight: 700, color: theme.textPrimary, marginBottom: '14px' }}>Account Info</h3>

            {[

              { label: 'Role', value: user?.role || 'Manager' },

              { label: 'Member Since', value: 'Jan 2024' },

              { label: 'Last Login', value: 'Today' },

              { label: 'Account Status', value: 'Active' },

            ].map(item => (

              <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>

                <span style={{ fontSize: '13px', color: theme.textSecondary }}>{item.label}</span>

                <span style={{ fontSize: '13px', fontWeight: 600, color: theme.textPrimary, textTransform: 'capitalize' }}>{item.value}</span>

              </div>

            ))}

          </div>



          <div style={{ ...card, padding: '20px' }}>

            <h3 style={{ fontSize: '14px', fontWeight: 700, color: theme.textPrimary, marginBottom: '14px' }}>Security</h3>

            {['Change Password', 'Two-Factor Auth'].map(label => (

              <button key={label} style={{

                width: '100%', padding: '10px 14px',

                border: `1px solid ${theme.cardBorder}`, borderRadius: '10px',

                background: theme.inputBg, color: theme.textSecondary,

                fontSize: '13px', fontWeight: 500, cursor: 'pointer',

                marginBottom: '8px', textAlign: 'left', transition: 'all 0.2s',

              }}

              onMouseEnter={e => { e.currentTarget.style.borderColor = theme.accent; e.currentTarget.style.color = theme.accent }}

              onMouseLeave={e => { e.currentTarget.style.borderColor = theme.cardBorder; e.currentTarget.style.color = theme.textSecondary }}>

                {label}

              </button>

            ))}

          </div>

        </div>

      </div>

    </div>

  )

}

 