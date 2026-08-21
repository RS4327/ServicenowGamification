import React from "react";
import {
  Home,
  UserRound,
  Users,
  Trophy,
  ShieldCheck,
  FileText,
  LineChart,
  Sparkles,
  BarChart3,
  Target,
  Award,
  BookOpen,
  Settings,
  LogOut,
  Bot,
  Circle,
} from "lucide-react";

const menuItems = [
  { label: "Manager Dashboard", path: "/manager", icon: Home },
  { label: "Agent Dashboard", path: "/agent", icon: UserRound },
  { label: "Assignment Groups", path: "/assignment-groups", icon: Users },
  { label: "Leaderboard", path: "/leaderboard", icon: Trophy },
  { label: "SLA Overview", path: "/sla", icon: ShieldCheck },
  { label: "Incident Overview", path: "/incidents", icon: FileText },
  { label: "Performance Charts", path: "/performance", icon: LineChart },
  { label: "AI Insights", path: "/ai-insights", icon: Sparkles },
  { label: "Reports", path: "/reports", icon: BarChart3 },
  { label: "Goals & Rewards", path: "/goals", icon: Target },
  { label: "Badges", path: "/badges", icon: Award },
  { label: "Knowledge Center", path: "/knowledge", icon: BookOpen },
  { label: "Settings", path: "/settings", icon: Settings },
];

export default function Sidebar({
  activePath = "/manager",
  onNavigate,
  onLogout,
}) {
  return (
    <aside className="sidebar">

      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">
          <Bot size={24} />
        </div>

        <div className="sidebar-logo-text">
          <strong>ServiceNow</strong>
          <span>Gamification Platform</span>
        </div>
      </div>

      <nav className="sidebar-navigation">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const active = activePath === item.path;

          return (
            <button
              key={item.path}
              className={`sidebar-item ${active ? "active" : ""}`}
              onClick={() => onNavigate?.(item.path)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-bottom">

        <div className="ai-status">
          <div className="ai-status-icon">
            <Bot size={19} />
          </div>

          <div>
            <strong>AI Model Status</strong>

            <div className="online-status">
              <Circle size={8} fill="currentColor" />
              Online
            </div>
          </div>
        </div>

        <button
          className="sidebar-item logout"
          onClick={onLogout}
        >
          <LogOut size={18} />
          <span>Logout</span>
        </button>

      </div>

    </aside>
  );
}