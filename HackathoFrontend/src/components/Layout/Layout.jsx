import React, { useState } from 'react'

import { Outlet } from 'react-router-dom'

import Sidebar from './Sidebar.jsx'

import Topbar from './Topbar.jsx'

import { useTheme } from '../../context/ThemeContext.jsx'



const EXPANDED = 240

const COLLAPSED = 64



export default function Layout({ role }) {

  const { theme } = useTheme()

  const [collapsed, setCollapsed] = useState(false)

  const sidebarWidth = collapsed ? COLLAPSED : EXPANDED



  return (

    <div style={{ display: 'flex', minHeight: '100vh', background: theme.pageBg }}>

      <Sidebar role={role} collapsed={collapsed} onToggle={() => setCollapsed(v => !v)} />

      <div style={{ flex: 1, marginLeft: sidebarWidth, transition: 'margin-left 0.3s cubic-bezier(0.4,0,0.2,1)' }}>

        <Topbar sidebarWidth={sidebarWidth} />

        <main style={{ marginTop: '64px', padding: '28px', minHeight: 'calc(100vh - 64px)' }}>

          <Outlet />

        </main>

      </div>

    </div>

  )

}

