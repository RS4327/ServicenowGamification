import React from 'react'

import { Routes, Route, Navigate } from 'react-router-dom'

import { useAuth } from './context/AuthContext.jsx'

import LoginPage from './pages/Login/LoginPage.jsx'

import Layout from './components/Layout/Layout.jsx'

import ManagerDashboard from './pages/Dashboard/ManagerDashboard.jsx'

import AgentDashboard from './pages/Dashboard/AgentDashboard.jsx'

import LeaderboardPage from './pages/Leaderboard/LeaderboardPage.jsx'

import AIInsightsPage from './pages/AIInsights/AIInsightsPage.jsx'

import PerformanceChartsPage from './pages/PerformanceCharts/PerformanceChartsPage.jsx'

import AgentsPage from './pages/Agents/AgentsPage.jsx'

import ReportsPage from './pages/Reports/ReportsPage.jsx'

import SettingsPage from './pages/Settings/SettingsPage.jsx'

import MyPerformancePage from './pages/MyPerformance/MyPerformancePage.jsx'

import BadgesPage from './pages/Badges/BadgesPage.jsx'

import GoalsPage from './pages/Goals/GoalsPage.jsx'



function ProtectedRoute({ children, requiredRole }) {

  const { user } = useAuth()

  if (!user) return <Navigate to="/" replace />

  if (requiredRole && user.role !== requiredRole) return <Navigate to="/" replace />

  return children

}



export default function App() {

  return (

    <Routes>

      <Route path="/" element={<LoginPage />} />



      <Route

        path="/manager/*"

        element={

          <ProtectedRoute requiredRole="manager">

            <Layout role="manager" />

          </ProtectedRoute>

        }

      >

        <Route index element={<Navigate to="dashboard" replace />} />

        <Route path="dashboard" element={<ManagerDashboard />} />

        <Route path="agents" element={<AgentsPage />} />

        <Route path="leaderboard" element={<LeaderboardPage />} />

        <Route path="ai-insights" element={<AIInsightsPage />} />

        <Route path="performance-charts" element={<PerformanceChartsPage />} />

        <Route path="reports" element={<ReportsPage />} />

        <Route path="settings" element={<SettingsPage />} />

      </Route>



      <Route

        path="/agent/*"

        element={

          <ProtectedRoute requiredRole="agent">

            <Layout role="agent" />

          </ProtectedRoute>

        }

      >

        <Route index element={<Navigate to="dashboard" replace />} />

        <Route path="dashboard" element={<AgentDashboard />} />

        <Route path="my-performance" element={<MyPerformancePage />} />

        <Route path="leaderboard" element={<LeaderboardPage />} />

        <Route path="ai-insights" element={<AIInsightsPage />} />

        <Route path="performance-charts" element={<PerformanceChartsPage />} />

        <Route path="badges" element={<BadgesPage />} />

        <Route path="goals" element={<GoalsPage />} />

      </Route>



      <Route path="*" element={<Navigate to="/" replace />} />

    </Routes>

  )

}

