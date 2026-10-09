// ── Manager Dashboard ─────────────────────────────────────────────────────────



export const managerStats = {

  totalIncidents: 59,

  slaCompliance: 6.78,

  fcr: 37.29,

  avgMTTR: 860.49,

  reopenRate: 14.41,

  customerRating: 4.32,

  incidentsTrend: 12.3,

  slaTrend: 5.2,

  fcrTrend: 8.7,

  mttrTrend: -3.1,

  reopenTrend: -1.8,

  ratingTrend: 4.6,

  period: 'Apr 21 – May 19, 2025',

}



export const incidentsOverTime = [

  { date: 'Apr 21', incidents: 42 },

  { date: 'Apr 28', incidents: 38 },

  { date: 'May 5',  incidents: 55 },

  { date: 'May 12', incidents: 70 },

  { date: 'May 19', incidents: 60 },

]



export const slaTrend = [

  { date: 'Apr 21', sla: 15.2, fcr: 30.1 },

  { date: 'Apr 28', sla: 12.8, fcr: 33.4 },

  { date: 'May 5',  sla: 14.1, fcr: 35.2 },

  { date: 'May 12', sla: 13.9, fcr: 32.8 },

  { date: 'May 19', sla: 11.5, fcr: 37.29 },

]



export const incidentsByState = [

  { name: 'Resolved', value: 38, color: '#3b82f6' },

  { name: 'Closed',   value: 29, color: '#10b981' },

  { name: 'Open',     value: 33, color: '#f59e0b' },

]



export const topAgentsByFCR = [

  { name: 'Fred Luddy',                   fcr: 92.45, incidents: 142, trend: 6.2,  trendUp: true },

  { name: 'Gulrez Fulsath',               fcr: 76.38, incidents: 118, trend: 4.1,  trendUp: true },

  { name: 'AIT Service Level Management', fcr: 65.73, incidents: 96,  trend: 2.8,  trendUp: true },

  { name: 'AVV_SeedDriver2',              fcr: 58.94, incidents: 87,  trend: 1.3,  trendUp: true },

  { name: 'Vamsi',                        fcr: 43.21, incidents: 65,  trend: 2.7,  trendUp: false },

]



export const mttrByPriority = [

  { priority: 'P1', hours: 220.45 },

  { priority: 'P2', hours: 480.32 },

  { priority: 'P3', hours: 850.67 },

  { priority: 'P4', hours: 1250.80 },

]



export const slaByPriority = [

  { priority: 'P1', compliance: 11.21 },

  { priority: 'P2', compliance: 8.67  },

  { priority: 'P3', compliance: 6.34  },

  { priority: 'P4', compliance: 3.92  },

]



export const recentAlerts = [

  { id: 1, title: 'High MTTR for Priority 1 incidents', desc: 'Average MTTR exceeded threshold',   time: '10 min ago', level: 'critical' },

  { id: 2, title: 'Low SLA Compliance',                 desc: 'SLA compliance below 7%',           time: '25 min ago', level: 'warning'  },

  { id: 3, title: 'High Reopen Rate',                   desc: 'Reopen rate above 14%',             time: '1 hour ago', level: 'info'     },

]



export const gamificationSummary = {

  totalAgents:       25,

  totalPoints:       125680,

  badgesAwarded:     156,

  activeChallenges:  8,

}



export const topBadges = [

  { id: 1, name: 'SLA Champion',      desc: 'Awarded to 8 agents',  color: '#f59e0b', icon: 'star'  },

  { id: 2, name: 'First Call Hero',   desc: 'Awarded to 10 agents', color: '#10b981', icon: 'check' },

  { id: 3, name: 'Resolution Master', desc: 'Awarded to 7 agents',  color: '#8b5cf6', icon: 'clock' },

]



export const performanceDistribution = [

  { name: 'High Performers',    value: 40, color: '#10b981' },

  { name: 'Average Performers', value: 40, color: '#3b82f6' },

  { name: 'Low Performers',     value: 20, color: '#f59e0b' },

]



export const topPerformer = {

  name:       'Kevin Brown',

  level:      5,

  points:     4850,

  monthTrend: 18.6,

}



// ── Agent Dashboard ───────────────────────────────────────────────────────────



export const agentStats = {

  myIncidents:   7,

  slaCompliance: 0,

  fcr:           57.14,

  mttr:          359.44,

}



export const agentPerformanceTrend = [

  { date: 'Apr 21', sla: 0, fcr: 50    },

  { date: 'Apr 28', sla: 0, fcr: 55    },

  { date: 'May 5',  sla: 0, fcr: 52    },

  { date: 'May 12', sla: 0, fcr: 57    },

  { date: 'May 19', sla: 0, fcr: 57.14 },

]



export const agentIncidentsByState = [

  { name: 'Resolved', value: 4, color: '#3b82f6' },

  { name: 'Closed',   value: 2, color: '#f59e0b' },

  { name: 'Open',     value: 1, color: '#ef4444' },

]



export const recentIncidents = [

  { id: 'INC0010001', shortDesc: 'Issue with email access',   state: 'Resolved', openedAt: '2025-05-20' },

  { id: 'INC0010002', shortDesc: 'VPN not connecting',        state: 'Open',     openedAt: '2025-05-18' },

  { id: 'INC0010003', shortDesc: 'Password reset',            state: 'Closed',   openedAt: '2025-05-16' },

  { id: 'INC0010004', shortDesc: 'Software installation',     state: 'Resolved', openedAt: '2025-05-17' },

  { id: 'INC0010005', shortDesc: 'System slow performance',   state: 'Open',     openedAt: '2025-05-16' },

]



export const badgesEarned = [

  { id: 1, name: 'Quick Resolve', description: 'Resolved 5 incidents under 1 hour',              color: '#3b82f6' },

  { id: 2, name: 'FCR Achiever',  description: 'Maintained FCR above 50% for a month',           color: '#10b981' },

  { id: 3, name: 'SLA Watcher',   description: 'Monitored and escalated 10 SLA-risk tickets',    color: '#f59e0b' },

]



export const allBadges = {

  earned: badgesEarned,

  locked: [

    { id: 4, name: 'Speed Demon',  description: 'Resolve 10 incidents in under 30 minutes each' },

    { id: 5, name: 'Perfect Week', description: 'Achieve 100% FCR and SLA for an entire week'   },

    { id: 6, name: 'Century Club', description: 'Resolve 100 incidents in a single month'        },

  ],

}



// ── Leaderboard ───────────────────────────────────────────────────────────────



export const leaderboardData = [

  { rank: 1,  name: 'Fred Luddy',          fcr: 80,    slaCompliance: 20,  mttr: 81.63,   points: 950 },

  { rank: 2,  name: 'Guillermo Fröhlich',  fcr: 100,   slaCompliance: 100, mttr: 24,      points: 910 },

  { rank: 3,  name: 'ATF_TestITUser2',     fcr: 100,   slaCompliance: 100, mttr: 24,      points: 880 },

  { rank: 4,  name: 'ITIL User',           fcr: 100,   slaCompliance: 0,   mttr: 48,      points: 870 },

  { rank: 5,  name: 'Beth Anglin',         fcr: 57.14, slaCompliance: 0,   mttr: 359.44,  points: 720 },

  { rank: 6,  name: 'Venkat',              fcr: 50,    slaCompliance: 0,   mttr: 27.83,   points: 680 },

  { rank: 7,  name: 'David Lee',           fcr: 33.33, slaCompliance: 0,   mttr: 1504.54, points: 560 },

  { rank: 8,  name: 'ITIL User',           fcr: 25,    slaCompliance: 8.33,mttr: 1237.99, points: 520 },

  { rank: 9,  name: 'Don Goodliffe',       fcr: 25,    slaCompliance: 0,   mttr: 1237.99, points: 500 },

  { rank: 10, name: 'Bud Richman',         fcr: 0,     slaCompliance: 0,   mttr: 1727.80, points: 300 },

]



// ── AI Insights ───────────────────────────────────────────────────────────────



export const aiInsights = [

  { id: 1, title: 'SLA Compliance is Low',    impact: 'High',   icon: 'warning', description: 'Current SLA compliance of 6.78% is critically below the 90% target.',       recommendation: ['Review all open incidents older than 4 hours','Redistribute workload from overloaded agents','Implement automated escalation rules'] },

  { id: 2, title: 'High MTTR Detected',       impact: 'High',   icon: 'clock',   description: 'Average MTTR of 860.49 hrs significantly exceeds the 24-hr benchmark.',      recommendation: ['Identify bottlenecks in resolution workflow','Provide training for high-MTTR agents','Enable knowledge base for common incidents'] },

  { id: 3, title: 'Reassignment Impact',      impact: 'Medium', icon: 'refresh', description: '34 incidents reassigned 3+ times, increasing MTTR by 340%.',                 recommendation: ['Improve incident categorization accuracy','Create specialist routing rules','Review agent skill profiles'] },

  { id: 4, title: 'Top Performer Identified', impact: 'Low',    icon: 'star',    description: 'Guillermo Fröhlich maintains 100% FCR and SLA — a best practice template.', recommendation: ['Document top performer resolution patterns','Pair with lower-performing agents','Recognise and reward consistently'] },

]



// ── Performance Charts ────────────────────────────────────────────────────────



export const performanceChartData = [

  { date: 'Apr 21', mttr: 400,    sla: 0, fcr: 50,    incidents: 1 },

  { date: 'Apr 28', mttr: 380,    sla: 0, fcr: 55,    incidents: 0 },

  { date: 'May 5',  mttr: 420,    sla: 0, fcr: 52,    incidents: 2 },

  { date: 'May 12', mttr: 360,    sla: 0, fcr: 57,    incidents: 1 },

  { date: 'May 19', mttr: 359.44, sla: 0, fcr: 57.14, incidents: 1 },

]



// ── Agents list (for AgentsPage) ──────────────────────────────────────────────



export const agentsList = [

  { id: 1, name: 'Fred Luddy',          role: 'Senior Agent',  fcr: 80,    slaCompliance: 20,  mttr: 81.63,   points: 950, status: 'Active' },

  { id: 2, name: 'Guillermo Fröhlich',  role: 'Lead Agent',    fcr: 100,   slaCompliance: 100, mttr: 24,      points: 910, status: 'Active' },

  { id: 3, name: 'ATF_TestITUser2',     role: 'Agent',         fcr: 100,   slaCompliance: 100, mttr: 24,      points: 880, status: 'Active' },

  { id: 4, name: 'ITIL User',           role: 'Agent',         fcr: 100,   slaCompliance: 0,   mttr: 48,      points: 870, status: 'Away'   },

  { id: 5, name: 'Beth Anglin',         role: 'Agent',         fcr: 57.14, slaCompliance: 0,   mttr: 359.44,  points: 720, status: 'Active' },

  { id: 6, name: 'Venkat',              role: 'Junior Agent',  fcr: 50,    slaCompliance: 0,   mttr: 27.83,   points: 680, status: 'Active' },

  { id: 7, name: 'David Lee',           role: 'Agent',         fcr: 33.33, slaCompliance: 0,   mttr: 1504.54, points: 560, status: 'Away'   },

  { id: 8, name: 'Don Goodliffe',       role: 'Junior Agent',  fcr: 25,    slaCompliance: 0,   mttr: 1237.99, points: 500, status: 'Active' },

  { id: 9, name: 'Bud Richman',         role: 'Agent',         fcr: 0,     slaCompliance: 0,   mttr: 1727.80, points: 300, status: 'Away'   },

]



// ── Goals list (for GoalsPage) ────────────────────────────────────────────────



export const goalsList = [

  { id: 1, title: 'FCR Goal',            description: 'Achieve First Contact Resolution rate of 80%',  current: 57.14,  target: 80,  unit: '%',   color: '#f59e0b' },

  { id: 2, title: 'SLA Compliance Goal', description: 'Maintain SLA compliance rate above 90%',        current: 0,      target: 90,  unit: '%',   color: '#10b981' },

  { id: 3, title: 'Incidents Resolved',  description: 'Resolve 10 incidents this month',               current: 4,      target: 10,  unit: '',    color: '#3b82f6' },

  { id: 4, title: 'MTTR Reduction',      description: 'Reduce MTTR below 200 hours',                   current: 359.44, target: 200, unit: 'hrs', color: '#8b5cf6', invert: true },

  { id: 5, title: 'Training Completion', description: 'Complete 3 mandatory training modules',          current: 1,      target: 3,   unit: '',    color: '#ec4899' },

  { id: 6, title: 'Badges Earned',       description: 'Earn 5 performance badges this quarter',         current: 3,      target: 5,   unit: '',    color: '#f97316' },

]

