import React, { useState } from "react";
import "./App.css";

const BLUE = "#07539b";
const DARK = "#003b73";

const menu = [
  ["⌂", "Dashboard"],
  ["♙", "Agents"],
  ["♜", "Leaderboard"],
  ["✦", "AI Insights"],
  ["◒", "Performance Charts"],
  ["▤", "Reports"],
  ["⚙", "Settings"],
  ["↪", "Logout"],
];

const agents = [
  ["Fred Luddly", "80.00", "20.00", "81.63", "950"],
  ["Guillermo Frolich", "100.00", "100.00", "24.00", "910"],
  ["ATF_TestUtilUser2", "100.00", "100.00", "24.00", "890"],
  ["ATF Service Level Management", "100.00", "0.00", "48.00", "870"],
  ["Beth Anglin", "57.14", "0.00", "359.44", "720"],
  ["Venkat", "50.00", "0.00", "96.72", "680"],
  ["David Loo", "33.33", "0.00", "1504.54", "560"],
  ["ITIL User", "25.00", "8.33", "549.15", "520"],
  ["Don Goodliffe", "25.00", "0.00", "1237.70", "500"],
  ["Bud Richman", "0.00", "0.00", "1727.80", "300"],
];

function App() {
  const [page, setPage] = useState("login");

  return (
    <div className="app">
      <header className="main-title">
        PHASE 7: DASHBOARD BLUEPRINT
      </header>

      <main className="blueprint">
        <section className="screen">
          <ScreenTitle>Step 45: Login Page</ScreenTitle>
          <LoginPage onLogin={() => setPage("manager")} />
        </section>

        <section className="screen">
          <ScreenTitle>Step 46: Manager Dashboard</ScreenTitle>
          <Dashboard
            active="Dashboard"
            role="Manager"
            name="Manager"
            manager
          />
        </section>

        <section className="screen">
          <ScreenTitle>Step 47: Agent Dashboard</ScreenTitle>
          <Dashboard
            active="Dashboard"
            role="Agent"
            name="Beth Anglin"
          />
        </section>

        <section className="screen">
          <ScreenTitle>Step 48: Leaderboard Page</ScreenTitle>
          <Leaderboard />
        </section>

        <section className="screen">
          <ScreenTitle>Step 49: AI Insights Page</ScreenTitle>
          <AIInsights />
        </section>

        <section className="screen">
          <ScreenTitle>Step 50: Performance Charts Page</ScreenTitle>
          <PerformanceCharts />
        </section>
      </main>
    </div>
  );
}

function ScreenTitle({ children }) {
  return <div className="screen-title">{children}</div>;
}

function LoginPage({ onLogin }) {
  return (
    <div className="login-page">
      <div className="login-left">
        <div className="trophy">🏆</div>
        <h2>ServiceNow</h2>
        <h2>Gamification Dashboard</h2>
        <p>Motivate. Engage. Perform.</p>
      </div>

      <div className="login-right">
        <h1>Welcome Back!</h1>
        <p>Log in to your account</p>

        <div className="input">
          <span>♙</span>
          <input placeholder="Username" />
        </div>

        <div className="input">
          <span>🔒</span>
          <input type="password" placeholder="Password" />
        </div>

        <label className="remember">
          <input type="checkbox" />
          Remember me
        </label>

        <button className="login-button" onClick={onLogin}>
          Login
        </button>

        <a href="#forgot">Forgot Password?</a>
      </div>
    </div>
  );
}

function Sidebar({ active }) {
  return (
    <aside className="sidebar">
      <div className="side-logo">
        Gamification
        <br />
        Dashboard
      </div>

      {menu.map(([icon, item]) => (
        <div
          key={item}
          className={`side-item ${active === item ? "selected" : ""}`}
        >
          <span>{icon}</span>
          {item}
        </div>
      ))}
    </aside>
  );
}

function Dashboard({ active, role, name, manager }) {
  return (
    <div className="dashboard">
      <Sidebar active={active} />

      <div className="content">
        <div className="topbar">
          <span>{role}</span>
          <span>
            ◉ &nbsp;{name} &nbsp;⌄
          </span>
        </div>

        <div className="metrics">
          {manager ? (
            <>
              <Metric title="Total Incidents" value="59" change="↑ 12.3%" green />
              <Metric title="SLA Compliance" value="6.78%" change="↑ 5.2%" green />
              <Metric title="FCR" value="37.29%" change="↑ 8.7%" green />
              <Metric title="Avg. MTTR (Hours)" value="860.49" change="↓ 3.1%" />
            </>
          ) : (
            <>
              <Metric title="My Incidents" value="7" />
              <Metric title="SLA Compliance" value="0%" />
              <Metric title="FCR" value="57.14%" />
              <Metric title="MTTR (Hours)" value="359.44" />
            </>
          )}
        </div>

        <div className="chart-grid">
          <ChartCard title={manager ? "Incidents Over Time" : "My Performance Trend"}>
            <LineChart manager={manager} />
          </ChartCard>

          <ChartCard title={manager ? "SLA Compliance Trend (%)" : "My Incidents by State"}>
            {manager ? <LineChart second /> : <Donut />}
          </ChartCard>

          <ChartCard title={manager ? "Incidents by State" : "My Recent Incidents"}>
            {manager ? <Donut /> : <IncidentTable />}
          </ChartCard>

          <ChartCard title={manager ? "Top 5 Agents by FCR (%)" : "Badges Earned"}>
            {manager ? <BarChart /> : <Badges />}
          </ChartCard>
        </div>
      </div>
    </div>
  );
}

function Metric({ title, value, change, green }) {
  return (
    <div className="metric">
      <div>{title}</div>
      <strong>{value}</strong>
      {change && (
        <small className={green ? "green" : "red"}>{change}</small>
      )}
    </div>
  );
}

function ChartCard({ title, children }) {
  return (
    <div className="chart-card">
      <h3>{title}</h3>
      {children}
    </div>
  );
}

function LineChart({ second = false }) {
  const points = second
    ? "10,25 30,38 50,25 70,42 90,30 110,37 130,31 150,48 170,41 190,55 210,40"
    : "10,65 30,66 50,70 70,50 90,42 110,36 130,15 150,30 170,22 190,40 210,50";

  return (
    <svg className="chart" viewBox="0 0 220 100">
      <line x1="10" y1="80" x2="215" y2="80" className="axis" />
      <line x1="10" y1="20" x2="10" y2="80" className="axis" />
      <polyline points={points} className="line" />
      {points.split(" ").map((p, i) => {
        const [x, y] = p.split(",");
        return <circle key={i} cx={x} cy={y} r="2.5" className="point" />;
      })}
      <text x="10" y="95">Apr 21</text>
      <text x="75" y="95">May 5</text>
      <text x="145" y="95">May 12</text>
      <text x="190" y="95">May 19</text>
    </svg>
  );
}

function Donut() {
  return (
    <div className="donut-wrapper">
      <div className="donut">
        <div className="donut-center">
          <b>59</b>
          <span>Total</span>
        </div>
      </div>

      <div className="legend">
        <span><i className="blue" />Resolved</span>
        <span><i className="green-bg" />Closed</span>
        <span><i className="orange" />Open</span>
      </div>
    </div>
  );
}

function BarChart() {
  const data = [
    ["Fred Luddly", 100],
    ["Guillermo Frolich", 80],
    ["ATF Service Level", 55],
    ["ATF_TestUtilUser2", 45],
    ["Venkat", 35],
  ];

  return (
    <div className="bars">
      {data.map(([name, value]) => (
        <div className="bar-row" key={name}>
          <span>{name}</span>
          <div>
            <i style={{ width: `${value}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

function IncidentTable() {
  return (
    <table className="mini-table">
      <thead>
        <tr>
          <th>Number</th>
          <th>Short Description</th>
          <th>State</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>INC0010008</td>
          <td>Issue with email access</td>
          <td>Resolved</td>
        </tr>
        <tr>
          <td>INC0010007</td>
          <td>VPN not connecting</td>
          <td>Open</td>
        </tr>
        <tr>
          <td>INC0010006</td>
          <td>Password reset</td>
          <td>Closed</td>
        </tr>
        <tr>
          <td>INC0010005</td>
          <td>Software installation</td>
          <td>Resolved</td>
        </tr>
      </tbody>
    </table>
  );
}

function Badges() {
  return (
    <div className="badges">
      <Badge icon="🏅" title="Quick Resolver" text="Resolved 5 incidents" />
      <Badge icon="🎯" title="FCR Achiever" text="Achieved 50% FCR" />
      <Badge icon="🏆" title="SLA Watcher" text="Focus on SLA" />
    </div>
  );
}

function Badge({ icon, title, text }) {
  return (
    <div className="badge">
      <span>{icon}</span>
      <div>
        <b>{title}</b>
        <small>{text}</small>
      </div>
    </div>
  );
}

function Leaderboard() {
  return (
    <div className="dashboard">
      <Sidebar active="Leaderboard" />

      <div className="content">
        <h2 className="page-heading">Leaderboard</h2>

        <div className="filters">
          <label>
            Metric
            <select>
              <option>FCR (%)</option>
            </select>
          </label>

          <label>
            Period
            <select>
              <option>This Month</option>
            </select>
          </label>

          <button>Apply</button>
        </div>

        <table className="leaderboard-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Agent</th>
              <th>FCR (%)</th>
              <th>SLA Compliance (%)</th>
              <th>MTTR (Hours)</th>
              <th>Points</th>
            </tr>
          </thead>

          <tbody>
            {agents.map((a, index) => (
              <tr key={a[0]}>
                <td>{index + 1}</td>
                <td>{a[0]}</td>
                <td>{a[1]}</td>
                <td>{a[2]}</td>
                <td>{a[3]}</td>
                <td>{a[4]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function AIInsights() {
  return (
    <div className="dashboard">
      <Sidebar active="AI Insights" />

      <div className="content">
        <h2 className="page-heading">AI Insights</h2>

        <Insight
          icon="⚠"
          title="SLA Compliance is Low"
          type="High Impact"
          color="red"
          text="Overall SLA Compliance is 6.78% which is below target. Focus on improving resolution speed."
        />

        <Insight
          icon="◷"
          title="High MTTR Detected"
          type="Medium Impact"
          color="orange"
          text="Average MTTR is 860.49 hours. Consider reviewing long pending incidents."
        />

        <Insight
          icon="♧"
          title="Reassignment Impact"
          type="Medium Impact"
          color="orange"
          text="34 incidents were reassigned. Reassignments increase resolution time."
        />

        <Insight
          icon="☆"
          title="Top Performer"
          type="Low Impact"
          color="green-text"
          text="Guillermo Frolich has 100% FCR and 100% SLA Compliance. Great job!"
        />

        <div className="recommendations">
          <h3>Recommendations</h3>
          <ul>
            <li>Provide training on faster resolution</li>
            <li>Improve first contact resolution</li>
            <li>Monitor and reduce reassignment rate</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

function Insight({ icon, title, type, color, text }) {
  return (
    <div className="insight">
      <div className={`insight-icon ${color}`}>{icon}</div>

      <div className="insight-body">
        <b>{title}</b>
        <p>{text}</p>
      </div>

      <span className={`impact ${color}`}>{type}</span>
    </div>
  );
}

function PerformanceCharts() {
  return (
    <div className="dashboard">
      <Sidebar active="Performance Charts" />

      <div className="content">
        <div className="chart-header">
          <h2 className="page-heading">Performance Charts</h2>
          <select>
            <option>This Month</option>
          </select>
        </div>

        <div className="performance-grid">
          <ChartCard title="MTTR (Hours) Trend">
            <LineChart />
          </ChartCard>

          <ChartCard title="SLA Compliance (%) Trend">
            <LineChart second />
          </ChartCard>

          <ChartCard title="FCR (%) Trend">
            <LineChart />
          </ChartCard>

          <ChartCard title="Incidents by State">
            <StackedBars />
          </ChartCard>
        </div>
      </div>
    </div>
  );
}

function StackedBars() {
  return (
    <div className="stacked">
      {[60, 55, 72, 70, 65, 50].map((height, i) => (
        <div className="stack" key={i}>
          <i style={{ height: `${height * 0.35}px` }} className="blue" />
          <i style={{ height: `${height * 0.25}px` }} className="green-bg" />
          <i style={{ height: `${height * 0.4}px` }} className="orange" />
        </div>
      ))}
    </div>
  );
}

export default App;