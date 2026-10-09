import React, { useState } from 'react'

import { useNavigate } from 'react-router-dom'

import { useAuth } from '../../context/AuthContext.jsx'

import { loginUser } from '../../services/api.js'



export default function LoginPage() {

  const [activeTab, setActiveTab] = useState('manager')

  const [username, setUsername] = useState('')

  const [password, setPassword] = useState('')

  const [remember, setRemember] = useState(false)

  const [hovering, setHovering] = useState(false)

  const [loading, setLoading] = useState(false)

  const [error, setError] = useState('')

  const { login } = useAuth()

  const navigate = useNavigate()



  const isManager = activeTab === 'manager'



  async function handleSubmit(e) {

    e.preventDefault()

    setError('')

    setLoading(true)

    try {

      const result = await loginUser(username || (isManager ? 'manager' : 'agent'), password || 'demo', activeTab)

      // result.token may be null in snapshot mode — that's fine

      login(result.user, result.token)

      navigate(isManager ? '/manager/dashboard' : '/agent/dashboard')

    } catch (err) {

      setError('Invalid credentials. Please try again.')

    } finally {

      setLoading(false)

    }

  }



  return (

    <div style={{

      minHeight: '100vh',

      display: 'flex',

      background: '#0f172a',

      position: 'relative',

      overflow: 'hidden',

    }}>

      {/* ── Left branded panel ── */}

      <div style={{

        width: '42%',

        background: 'linear-gradient(160deg, #1e3a5f 0%, #0f172a 60%, #0a1628 100%)',

        display: 'flex',

        flexDirection: 'column',

        alignItems: 'center',

        justifyContent: 'center',

        padding: '60px 48px',

        position: 'relative',

        borderRight: '1px solid rgba(255,255,255,0.06)',

      }}>

        {/* Decorative glow blobs */}

        <div style={{ position: 'absolute', width: '320px', height: '320px', borderRadius: '50%', background: 'rgba(59,130,246,0.12)', filter: 'blur(80px)', top: '10%', left: '-60px', pointerEvents: 'none' }} />

        <div style={{ position: 'absolute', width: '240px', height: '240px', borderRadius: '50%', background: 'rgba(99,102,241,0.1)', filter: 'blur(70px)', bottom: '15%', right: '-40px', pointerEvents: 'none' }} />



        {/* Trophy icon */}

        <div style={{

          width: '88px', height: '88px', borderRadius: '24px',

          background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',

          display: 'flex', alignItems: 'center', justifyContent: 'center',

          marginBottom: '32px',

          boxShadow: '0 0 40px rgba(59,130,246,0.4), 0 0 80px rgba(59,130,246,0.15)',

          animation: 'pulse-glow 3s ease infinite',

        }}>

          <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">

            <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/>

            <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/>

            <path d="M4 22h16"/>

            <path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/>

            <path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/>

            <path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/>

          </svg>

        </div>



        {/* Brand text */}

        <div style={{ textAlign: 'center', position: 'relative', zIndex: 1 }}>

          <p style={{ fontSize: '11px', fontWeight: 700, letterSpacing: '4px', color: '#64748b', textTransform: 'uppercase', marginBottom: '10px' }}>

            ServiceNow

          </p>

          <h1 style={{ fontSize: '30px', fontWeight: 800, color: '#f1f5f9', lineHeight: 1.2, marginBottom: '14px', letterSpacing: '-0.5px' }}>

            Gamification<br />Dashboard

          </h1>

          <div style={{ width: '40px', height: '3px', background: 'linear-gradient(90deg, #3b82f6, #6366f1)', borderRadius: '2px', margin: '0 auto 18px' }} />

          <p style={{ fontSize: '14px', color: '#64748b', fontWeight: 500, letterSpacing: '1px' }}>

            Motivate. Engage. Perform.

          </p>

        </div>



        {/* Feature pills */}

        <div style={{ marginTop: '56px', display: 'flex', flexDirection: 'column', gap: '12px', width: '100%', maxWidth: '260px', position: 'relative', zIndex: 1 }}>

          {[

            { icon: '📊', text: 'Real-time performance tracking' },

            { icon: '🏆', text: 'Gamified leaderboards' },

            { icon: '🤖', text: 'AI-powered insights' },

          ].map((f, i) => (

            <div key={i} style={{

              display: 'flex', alignItems: 'center', gap: '12px',

              background: 'rgba(255,255,255,0.04)',

              border: '1px solid rgba(255,255,255,0.07)',

              borderRadius: '12px', padding: '12px 16px',

            }}>

              <span style={{ fontSize: '18px' }}>{f.icon}</span>

              <span style={{ fontSize: '13px', color: '#94a3b8', fontWeight: 500 }}>{f.text}</span>

            </div>

          ))}

        </div>

      </div>



      {/* ── Right login panel ── */}

      <div style={{

        flex: 1,

        display: 'flex',

        alignItems: 'center',

        justifyContent: 'center',

        padding: '40px 48px',

        background: '#0f172a',

      }}>

        <div style={{ width: '100%', maxWidth: '400px', animation: 'fadeInUp 0.5s ease' }}>



          {/* Welcome heading */}

          <div style={{ marginBottom: '32px' }}>

            <h2 style={{ fontSize: '30px', fontWeight: 800, color: '#f1f5f9', marginBottom: '8px', letterSpacing: '-0.5px' }}>

              Welcome Back!

            </h2>

            <p style={{ fontSize: '14px', color: '#64748b' }}>Log in to your account</p>

          </div>



          {/* Role toggle */}

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '14px', marginBottom: '28px' }}>

            <span style={{ fontSize: '13px', fontWeight: 700, color: isManager ? '#f1f5f9' : '#475569', transition: 'color 0.2s' }}>

              👔 Manager

            </span>

            <div

              onClick={() => setActiveTab(isManager ? 'agent' : 'manager')}

              style={{

                width: '52px', height: '28px',

                background: isManager

                  ? 'linear-gradient(135deg, #3b82f6, #1d4ed8)'

                  : 'linear-gradient(135deg, #6366f1, #4f46e5)',

                borderRadius: '14px', position: 'relative',

                cursor: 'pointer', transition: 'background 0.3s',

                boxShadow: isManager ? '0 0 12px rgba(59,130,246,0.5)' : '0 0 12px rgba(99,102,241,0.5)',

                flexShrink: 0,

              }}

            >

              <div style={{

                position: 'absolute', top: '4px',

                left: isManager ? '4px' : '24px',

                width: '20px', height: '20px',

                background: '#fff', borderRadius: '50%',

                transition: 'left 0.3s cubic-bezier(0.4,0,0.2,1)',

                boxShadow: '0 1px 4px rgba(0,0,0,0.3)',

                display: 'flex', alignItems: 'center', justifyContent: 'center',

                fontSize: '10px',

              }}>

                {isManager ? '👔' : '⚡'}

              </div>

            </div>

            <span style={{ fontSize: '13px', fontWeight: 700, color: !isManager ? '#f1f5f9' : '#475569', transition: 'color 0.2s' }}>

              Agent ⚡

            </span>

          </div>



          {/* Form */}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>



            {/* Username */}

            <div>

              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#94a3b8', marginBottom: '8px' }}>

                Username

              </label>

              <div style={{ position: 'relative' }}>

                <span style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: '#475569', pointerEvents: 'none' }}>

                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">

                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>

                  </svg>

                </span>

                <input

                  type="text"

                  value={username}

                  onChange={e => setUsername(e.target.value)}

                  placeholder={isManager ? 'manager@servicenow.com' : 'agent@servicenow.com'}

                  style={{

                    width: '100%', padding: '13px 14px 13px 42px',

                    background: 'rgba(255,255,255,0.05)',

                    border: '1.5px solid rgba(255,255,255,0.1)',

                    borderRadius: '10px', fontSize: '14px', color: '#f1f5f9',

                    outline: 'none', transition: 'border-color 0.2s, box-shadow 0.2s',

                    boxSizing: 'border-box',

                  }}

                  onFocus={e => { e.target.style.borderColor = '#3b82f6'; e.target.style.boxShadow = '0 0 0 3px rgba(59,130,246,0.15)' }}

                  onBlur={e => { e.target.style.borderColor = 'rgba(255,255,255,0.1)'; e.target.style.boxShadow = 'none' }}

                />

              </div>

            </div>



            {/* Password */}

            <div>

              <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#94a3b8', marginBottom: '8px' }}>

                Password

              </label>

              <div style={{ position: 'relative' }}>

                <span style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: '#475569', pointerEvents: 'none' }}>

                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">

                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>

                  </svg>

                </span>

                <input

                  type="password"

                  value={password}

                  onChange={e => setPassword(e.target.value)}

                  placeholder="••••••••"

                  style={{

                    width: '100%', padding: '13px 14px 13px 42px',

                    background: 'rgba(255,255,255,0.05)',

                    border: '1.5px solid rgba(255,255,255,0.1)',

                    borderRadius: '10px', fontSize: '14px', color: '#f1f5f9',

                    outline: 'none', transition: 'border-color 0.2s, box-shadow 0.2s',

                    boxSizing: 'border-box',

                  }}

                  onFocus={e => { e.target.style.borderColor = '#3b82f6'; e.target.style.boxShadow = '0 0 0 3px rgba(59,130,246,0.15)' }}

                  onBlur={e => { e.target.style.borderColor = 'rgba(255,255,255,0.1)'; e.target.style.boxShadow = 'none' }}

                />

              </div>

            </div>



            {/* Remember me + Forgot password */}

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>

              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '13px', color: '#64748b' }}>

                <input

                  type="checkbox"

                  checked={remember}

                  onChange={e => setRemember(e.target.checked)}

                  style={{ width: '15px', height: '15px', accentColor: '#3b82f6', cursor: 'pointer' }}

                />

                Remember me

              </label>

              <a href="#" style={{ fontSize: '13px', color: '#3b82f6', fontWeight: 600, textDecoration: 'none' }}

                onMouseEnter={e => e.target.style.color = '#60a5fa'}

                onMouseLeave={e => e.target.style.color = '#3b82f6'}>

                Forgot Password?

              </a>

            </div>



            {/* Login button */}

            <button

              type="submit"

              style={{

                width: '100%', padding: '14px',

                background: isManager

                  ? 'linear-gradient(135deg, #3b82f6, #1d4ed8)'

                  : 'linear-gradient(135deg, #6366f1, #4f46e5)',

                color: '#fff', border: 'none', borderRadius: '10px',

                fontSize: '15px', fontWeight: 700, cursor: 'pointer',

                boxShadow: isManager

                  ? '0 6px 20px rgba(59,130,246,0.4)'

                  : '0 6px 20px rgba(99,102,241,0.4)',

                transition: 'all 0.2s',

                transform: hovering ? 'translateY(-2px)' : 'translateY(0)',

                letterSpacing: '0.3px',

              }}

              onMouseEnter={() => setHovering(true)}

              onMouseLeave={() => setHovering(false)}

            >

              {loading ? (

                <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>

                  <svg style={{ animation: 'spin 0.8s linear infinite' }} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">

                    <path d="M21 12a9 9 0 1 1-6.219-8.56"/>

                  </svg>

                  Signing in…

                </span>

              ) : (isManager ? 'Login as Manager' : 'Login as Agent')}

            </button>



            {error && (

              <div style={{

                marginTop: '12px', padding: '10px 14px',

                background: 'rgba(239,68,68,0.12)', border: '1px solid rgba(239,68,68,0.3)',

                borderRadius: '10px', fontSize: '13px', color: '#fca5a5',

                display: 'flex', alignItems: 'center', gap: '8px',

              }}>

                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>

                {error}

              </div>

            )}

          </form>



          {/* Live status */}

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginTop: '28px' }}>

            <div style={{ width: '7px', height: '7px', borderRadius: '50%', background: '#10b981', animation: 'live-pulse 2s ease infinite', boxShadow: '0 0 6px #10b981' }} />

            <span style={{ fontSize: '12px', color: '#475569' }}>Live system connected</span>

          </div>



          <p style={{ textAlign: 'center', marginTop: '16px', fontSize: '12px', color: '#334155' }}>

            © 2025 ServiceNow Gamification Dashboard

          </p>

        </div>

      </div>

    </div>

  )

}

