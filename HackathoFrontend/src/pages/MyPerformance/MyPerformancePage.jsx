import React from 'react'

import {

  LineChart, Line, BarChart, Bar, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,

  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,

} from 'recharts'

import { agentStats, agentPerformanceTrend, performanceChartData } from '../../data/sampleData.js'

import { useTheme } from '../../context/ThemeContext.jsx'



const radarData = [

  { metric: 'FCR', value: 57 },

  { metric: 'SLA', value: 0 },

  { metric: 'Speed', value: 35 },

  { metric: 'Quality', value: 70 },

  { metric: 'Volume', value: 45 },

]



function MetricCard({ label, value, unit, color, desc, theme }) {

  return (

    <div style={{

      background: theme.cardBg, borderRadius: '14px',

      border: `1px solid ${theme.cardBorder}`,

      borderLeft: `4px solid ${color}`,

      boxShadow: theme.cardShadow, backdropFilter: 'blur(20px)',

      padding: '20px', flex: 1, minWidth: 0,

    }}>

      <div style={{ fontSize: '12px', color: theme.textMuted, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '10px' }}>{label}</div>

      <div style={{ fontSize: '28px', fontWeight: 800, color: theme.textPrimary, marginBottom: '4px' }}>

        {value}{unit && <span style={{ fontSize: '15px', color: theme.textSecondary, marginLeft: '4px' }}>{unit}</span>}

      </div>

      {desc && <div style={{ fontSize: '12px', color: theme.textMuted }}>{desc}</div>}

    </div>

  )

}



export default function MyPerformancePage() {

  const { theme } = useTheme()



  const card = {

    background: theme.cardBg, borderRadius: '14px',

    border: `1px solid ${theme.cardBorder}`, boxShadow: theme.cardShadow,

    backdropFilter: 'blur(20px)', padding: '20px',

  }



  const tooltipStyle = {

    background: theme.sidebarBg, border: `1px solid ${theme.cardBorder}`,

    borderRadius: '10px', color: theme.textPrimary,

  }



  return (

    <div>

      <div style={{ marginBottom: '24px' }}>

        <h2 style={{ fontSize: '22px', fontWeight: 700, color: theme.textPrimary, marginBottom: '4px' }}>

          My <span style={{ color: theme.accent }}>Performance</span>

        </h2>

        <p style={{ color: theme.textSecondary, fontSize: '14px' }}>Detailed breakdown of your performance metrics</p>

      </div>



      {/* Stat Cards */}

      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', flexWrap: 'wrap' }}>

        <MetricCard label="My Incidents" value={agentStats.myIncidents} color={theme.accent} desc="Total assigned this period" theme={theme} />

        <MetricCard label="SLA Compliance" value={agentStats.slaCompliance} unit="%" color={theme.success} desc="Target: 90%" theme={theme} />

        <MetricCard label="First Contact Resolution" value={agentStats.fcr} unit="%" color={theme.warning} desc="Target: 80%" theme={theme} />

        <MetricCard label="Avg MTTR" value={agentStats.mttr} unit="hrs" color={theme.accentSecondary} desc="Mean time to resolve" theme={theme} />

      </div>



      {/* Trend + Radar */}

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '16px', marginBottom: '20px' }}>

        <div style={card}>

          <h3 style={{ fontSize: '15px', fontWeight: 600, color: theme.textPrimary, marginBottom: '4px' }}>Performance Trend</h3>

          <p style={{ fontSize: '12px', color: theme.textMuted, marginBottom: '16px' }}>SLA and FCR over the past 8 weeks</p>

          <ResponsiveContainer width="100%" height={220}>

            <LineChart data={agentPerformanceTrend} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>

              <CartesianGrid strokeDasharray="3 3" stroke={theme.chartGrid} />

              <XAxis dataKey="date" tick={{ fontSize: 11, fill: theme.textMuted }} />

              <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: theme.textMuted }} />

              <Tooltip contentStyle={tooltipStyle} />

              <Legend wrapperStyle={{ fontSize: '12px', color: theme.textSecondary }} />

              <Line type="monotone" dataKey="sla" stroke={theme.success} strokeWidth={2.5} dot={{ r: 3 }} name="SLA %" />

              <Line type="monotone" dataKey="fcr" stroke={theme.warning} strokeWidth={2.5} dot={{ r: 3 }} name="FCR %" />

            </LineChart>

          </ResponsiveContainer>

        </div>



        <div style={card}>

          <h3 style={{ fontSize: '15px', fontWeight: 600, color: theme.textPrimary, marginBottom: '4px' }}>Skill Radar</h3>

          <p style={{ fontSize: '12px', color: theme.textMuted, marginBottom: '8px' }}>Multi-dimensional performance view</p>

          <ResponsiveContainer width="100%" height={220}>

            <RadarChart data={radarData} cx="50%" cy="50%" outerRadius={75}>

              <PolarGrid stroke={theme.chartGrid} />

              <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11, fill: theme.textSecondary }} />

              <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />

              <Radar name="Performance" dataKey="value" stroke={theme.accent} fill={theme.accent} fillOpacity={0.2} />

              <Tooltip contentStyle={tooltipStyle} />

            </RadarChart>

          </ResponsiveContainer>

        </div>

      </div>



      {/* MTTR Trend */}

      <div style={{ ...card, marginBottom: '20px' }}>

        <h3 style={{ fontSize: '15px', fontWeight: 600, color: theme.textPrimary, marginBottom: '4px' }}>MTTR Trend (Hours)</h3>

        <p style={{ fontSize: '12px', color: theme.textMuted, marginBottom: '16px' }}>Weekly resolution time tracking</p>

        <ResponsiveContainer width="100%" height={200}>

          <BarChart data={performanceChartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>

            <CartesianGrid strokeDasharray="3 3" stroke={theme.chartGrid} />

            <XAxis dataKey="date" tick={{ fontSize: 11, fill: theme.textMuted }} />

            <YAxis tick={{ fontSize: 11, fill: theme.textMuted }} />

            <Tooltip contentStyle={tooltipStyle} />

            <Bar dataKey="mttr" fill={theme.accentSecondary} radius={[4, 4, 0, 0]} name="MTTR (hrs)" />

          </BarChart>

        </ResponsiveContainer>

      </div>



      {/* Weekly Breakdown Table */}

      <div style={card}>

        <h3 style={{ fontSize: '15px', fontWeight: 600, color: theme.textPrimary, marginBottom: '16px' }}>Weekly Breakdown</h3>

        <table style={{ width: '100%', borderCollapse: 'collapse' }}>

          <thead>

            <tr style={{ background: theme.tableRowAlt, borderBottom: `1px solid ${theme.cardBorder}` }}>

              {['Period', 'FCR (%)', 'SLA (%)', 'MTTR (hrs)'].map(h => (

                <th key={h} style={{ padding: '10px 14px', textAlign: 'left', fontSize: '11px', fontWeight: 700, color: theme.textMuted, textTransform: 'uppercase', letterSpacing: '0.8px' }}>{h}</th>

              ))}

            </tr>

          </thead>

          <tbody>

            {performanceChartData.map((row, i) => (

              <tr

                key={i}

                style={{ borderBottom: i < performanceChartData.length - 1 ? `1px solid ${theme.cardBorder}` : 'none', transition: 'background 0.15s' }}

                onMouseEnter={e => e.currentTarget.style.background = theme.tableRowHover}

                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}

              >

                <td style={{ padding: '11px 14px', fontWeight: 600, fontSize: '13px', color: theme.textPrimary }}>{row.date}</td>

                <td style={{ padding: '11px 14px', fontSize: '13px', color: theme.warning, fontWeight: 600 }}>{row.fcr}%</td>

                <td style={{ padding: '11px 14px', fontSize: '13px', color: theme.success, fontWeight: 600 }}>{row.sla}%</td>

                <td style={{ padding: '11px 14px', fontSize: '13px', color: theme.accentSecondary, fontWeight: 600 }}>{row.mttr}</td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>

    </div>

  )

}

