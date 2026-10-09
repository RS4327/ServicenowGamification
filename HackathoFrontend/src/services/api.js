/**

 * Data Access Layer

 *

 * Architecture: Dashboard → Data Access Layer → Primary (Database) → Fallback (Repository Snapshot)

 *

 * VITE_DATA_SOURCE=snapshot  → skip all API calls, return versioned snapshot (demo/offline)

 * VITE_DATA_SOURCE=database  → call live API; if unreachable fall back to snapshot

 */



import { DATA_SOURCE, BASE_URL, recordSourceUsed } from '../config/dataSource.js'

import * as snapshot from '../data/sampleData.js'



// ── API error (has a real HTTP status) vs network error (server unreachable) ──



class ApiError extends Error {

  constructor(message, status) {

    super(message)

    this.status = status

    this.isApiError = true

  }

}



// ── Core HTTP helper ──────────────────────────────────────────────────────────



async function apiFetch(path, options = {}) {

  if (!BASE_URL) throw new Error('VITE_API_BASE_URL not configured')

  const token = localStorage.getItem('gd-token')

  const res = await fetch(`${BASE_URL}${path}`, {

    ...options,

    headers: {

      'Content-Type': 'application/json',

      ...(token ? { Authorization: `Bearer ${token}` } : {}),

      ...(options.headers || {}),

    },

  })

  let json

  try { json = await res.json() } catch { json = {} }

  if (!res.ok) throw new ApiError(json.error || `HTTP ${res.status}`, res.status)

  if (!json.success) throw new ApiError(json.error || 'API error', res.status)

  return json.data

}



// ── Switching abstraction ─────────────────────────────────────────────────────

// snapshot mode       → returns snapshotData immediately, no network call

// database mode       → tries API; if server is unreachable falls back to snapshot

// database + strict   → tries API; if server responds with error THROWS (used for login

//                        so the UI can show "Invalid credentials" instead of silently

//                        falling back to a sample user)



async function withSource(apiCall, snapshotData, { strict = false } = {}) {

  if (DATA_SOURCE === 'snapshot') {

    recordSourceUsed('snapshot')

    return snapshotData

  }

  try {

    const result = await apiCall()

    recordSourceUsed('database')

    return result

  } catch (err) {

    // strict=true: re-throw real API errors (4xx/5xx) so the caller can show them

    // Only fall back when the server is genuinely unreachable (network/TypeError)

    if (strict && err.isApiError) throw err

    console.warn('[DataLayer] Falling back to snapshot:', err.message)

    recordSourceUsed('snapshot-fallback')

    return snapshotData

  }

}



// ── Data-shape helpers ────────────────────────────────────────────────────────

// The DB does not return color values for state/distribution charts;

// we add them client-side so the UI always has what it needs.



const STATE_COLORS = { Resolved: '#3b82f6', Closed: '#10b981', Open: '#f59e0b' }



function injectStateColors(data) {

  return data.map(item => ({ ...item, color: STATE_COLORS[item.name] || '#94a3b8' }))

}



// Oracle may return TREND_UP as 1/0 or 'true'/'false'; normalise to JS boolean.

function normaliseBool(val) {

  if (typeof val === 'boolean') return val

  if (typeof val === 'number')  return val !== 0

  if (typeof val === 'string')  return val.toLowerCase() === 'true' || val === '1'

  return false

}



function normaliseTopAgents(data) {

  return data.map(a => ({ ...a, trendUp: normaliseBool(a.trendUp) }))

}



// ── Authentication ────────────────────────────────────────────────────────────



export async function loginUser(username, password, role) {

  return withSource(

    () => apiFetch('/auth/login', {

      method: 'POST',

      body: JSON.stringify({ username, password, role }),

    }),

    {

      token: null,

      user: {

        name: role === 'manager' ? 'Manager' : 'Beth Anglin',

        role,

        avatar: role === 'manager' ? 'M' : 'BA',

      },

    },

    { strict: true }  // propagate 401/500 so LoginPage shows the real error

  )

}



// ── Manager Dashboard — Stats (6 KPI cards) ───────────────────────────────────

// DB view: LIVE_STREAK_OVERALL_LEVEL



export async function getManagerStats() {

  return withSource(

    () => apiFetch('/dashboard/manager/stats'),

    snapshot.managerStats

  )

}



// ── Manager Dashboard — Incidents Over Time ───────────────────────────────────

// DB view: MANGER_INCIDENTS_OVER_TIME_02



export async function getIncidentsOverTime(period = 'monthly') {

  return withSource(

    () => apiFetch(`/dashboard/manager/incidents-over-time?period=${period}`),

    snapshot.incidentsOverTime

  )

}



// ── Manager Dashboard — SLA + FCR Trend ──────────────────────────────────────

// DB view: MANAGER_FCR_SLA_TREND_OVERALL_05



export async function getSlaTrend(period = 'monthly') {

  return withSource(

    () => apiFetch(`/dashboard/manager/sla-trend?period=${period}`),

    snapshot.slaTrend

  )

}



// ── Manager Dashboard — Incidents by State (donut chart) ─────────────────────

// DB view: MANAGER_INCIDENT_BY_STATE_03

// Note: DB returns { name, value } only — colors are mapped client-side



export async function getIncidentsByState() {

  return withSource(

    async () => injectStateColors(await apiFetch('/dashboard/manager/incidents-by-state')),

    snapshot.incidentsByState

  )

}



// ── Manager Dashboard — Top Agents by FCR ────────────────────────────────────

// DB view: MANAGER_AGENTS_BY_FCR_TRENDS_05

// Note: DB TREND_UP column may be 0/1 — normalised to boolean



export async function getTopAgents(limit = 5) {

  return withSource(

    async () => normaliseTopAgents(

      await apiFetch(`/dashboard/manager/top-agents?limit=${limit}&metric=fcr`)

    ),

    snapshot.topAgentsByFCR

  )

}



// ── Manager Dashboard — MTTR by Priority ─────────────────────────────────────

// DB view: MANAGER_AVG_BY_PRIORITY_06



export async function getMttrByPriority() {

  return withSource(

    () => apiFetch('/dashboard/manager/mttr-by-priority'),

    snapshot.mttrByPriority

  )

}



// ── Manager Dashboard — SLA Compliance by Priority ───────────────────────────

// DB view: MANAGER_SLA_BY_PRIORITY_08



export async function getSlaByPriority() {

  return withSource(

    () => apiFetch('/dashboard/manager/sla-by-priority'),

    snapshot.slaByPriority

  )

}



// ── Alerts ────────────────────────────────────────────────────────────────────

// DB table: SERVICENOWGAMIFICATION.MANAGER_RECENT_ALERT_09

// Note: DB returns JSON_ARRAYAGG (array at top level inside data envelope)



export async function getRecentAlerts(limit = 3) {

  return withSource(

    () => apiFetch(`/alerts?limit=${limit}`),

    snapshot.recentAlerts

  )

}



// ── Gamification Summary ──────────────────────────────────────────────────────

// DB view: MANAGER_GAMIFICATION_SUMMARY_10



export async function getGamificationSummary() {

  return withSource(

    () => apiFetch('/gamification/summary'),

    snapshot.gamificationSummary

  )

}



// ── Top Badges ────────────────────────────────────────────────────────────────

// DB table: MANGER_TOP_BADGES_EARDNED_11

// Note: DB returns JSON_ARRAYAGG ordered by ID



export async function getTopBadges(limit = 3) {

  return withSource(

    () => apiFetch(`/badges/top?limit=${limit}`),

    snapshot.topBadges

  )

}



// ── Performance Distribution ──────────────────────────────────────────────────

// DB table: SERVICENOWGAMIFICATION.MANAGER_PERFORMANACE_DISTRIBUTION_12

// Note: DB returns JSON_ARRAYAGG ordered by category (High → Average → Low)



export async function getPerformanceDistribution() {

  return withSource(

    () => apiFetch('/performance/distribution'),

    snapshot.performanceDistribution

  )

}



// ── Agent Dashboard ───────────────────────────────────────────────────────────



export async function getAgentStats() {

  return withSource(() => apiFetch('/dashboard/agent/stats'), snapshot.agentStats)

}



export async function getAgentPerformanceTrend() {

  return withSource(() => apiFetch('/dashboard/agent/performance-trend'), snapshot.agentPerformanceTrend)

}



export async function getAgentIncidentsByState() {

  return withSource(

    async () => injectStateColors(await apiFetch('/dashboard/agent/incidents-by-state')),

    snapshot.agentIncidentsByState

  )

}



export async function getRecentIncidents(limit = 5) {

  return withSource(

    () => apiFetch(`/dashboard/agent/recent-incidents?limit=${limit}`),

    snapshot.recentIncidents

  )

}



export async function getAgentBadges() {

  return withSource(() => apiFetch('/dashboard/agent/badges'), snapshot.badgesEarned)

}



// ── Leaderboard ───────────────────────────────────────────────────────────────



export async function getLeaderboard(metric = 'points', period = 'month') {

  return withSource(

    () => apiFetch(`/leaderboard?metric=${metric}&period=${period}`),

    snapshot.leaderboardData

  )

}



// ── AI Insights ───────────────────────────────────────────────────────────────



export async function getInsights(role = 'manager') {

  return withSource(() => apiFetch(`/insights?role=${role}`), snapshot.aiInsights)

}



// ── Performance Charts ────────────────────────────────────────────────────────



export async function getPerformanceCharts(period = 'this_month') {

  return withSource(() => apiFetch(`/performance/charts?period=${period}`), snapshot.performanceChartData)

}



// ── Agents Management ─────────────────────────────────────────────────────────



export async function getAgents(search = '', status = '') {

  return withSource(

    () => apiFetch(`/agents?search=${encodeURIComponent(search)}&status=${encodeURIComponent(status)}`),

    snapshot.agentsList

  )

}



// ── Goals ─────────────────────────────────────────────────────────────────────



export async function getGoals() {

  return withSource(() => apiFetch('/goals'), snapshot.goalsList)

}



export async function updateGoal(id, data) {

  return withSource(

    () => apiFetch(`/goals/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

    data

  )

}



// ── Badges (agent full list) ──────────────────────────────────────────────────



export async function getBadges() {

  return withSource(() => apiFetch('/badges'), snapshot.allBadges)

}



// ── Settings ──────────────────────────────────────────────────────────────────



export async function updateProfile(data) {

  return withSource(

    () => apiFetch('/settings/profile', { method: 'PUT', body: JSON.stringify(data) }),

    data

  )

}



export async function updateNotifications(data) {

  return withSource(

    () => apiFetch('/settings/notifications', { method: 'PUT', body: JSON.stringify(data) }),

    data

  )

}

