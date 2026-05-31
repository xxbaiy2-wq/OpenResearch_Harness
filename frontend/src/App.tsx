import React, { useState } from "react";
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from "react-router-dom";
import { Layout, Menu, Typography } from "antd";
import {
  RadarChartOutlined,
  DatabaseOutlined,
  FileTextOutlined,
  SearchOutlined,
  BarChartOutlined,
  CodeOutlined,
} from "@ant-design/icons";
import Home from "./pages/Home";
import ResearchTasks from "./pages/ResearchTasks";
import AgentRunDetail from "./pages/AgentRunDetail";
import ReportDetail from "./pages/ReportDetail";
import Reports from "./pages/Reports";
import Search from "./pages/Search";
import Weekly from "./pages/Weekly";

const { Header, Content, Sider } = Layout;
const { Title } = Typography;

const menuItems = [
  { key: "/", icon: <RadarChartOutlined />, label: "每日雷达" },
  { key: "/search", icon: <SearchOutlined />, label: "技术搜索" },
  { key: "/weekly", icon: <BarChartOutlined />, label: "周报趋势" },
  { key: "/reports", icon: <FileTextOutlined />, label: "历史报告" },
  { key: "/tasks", icon: <CodeOutlined />, label: "任务管理" },
];

function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Header style={{
        background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
        padding: "0 24px",
        display: "flex",
        alignItems: "center",
        boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
      }}>
        <div style={{ display: "flex", alignItems: "center", cursor: "pointer" }} onClick={() => navigate("/")}>
          <RadarChartOutlined style={{ fontSize: 28, color: "#1890ff", marginRight: 12 }} />
          <Title level={4} style={{ color: "#fff", margin: 0, letterSpacing: 1 }}>
            OpenResearch 技术雷达
          </Title>
        </div>
        <div style={{ flex: 1 }} />
        <span style={{ color: "rgba(255,255,255,0.6)", fontSize: 13 }}>
          每日 5 分钟 · 掌握前沿技术动态
        </span>
      </Header>

      <Layout>
        <Sider
          collapsible
          collapsed={collapsed}
          onCollapse={setCollapsed}
          theme="light"
          style={{ borderRight: "1px solid #f0f0f0" }}
          width={180}
        >
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={({ key }) => navigate(key)}
            style={{ border: "none", paddingTop: 8 }}
          />
        </Sider>

        <Content style={{ padding: 24, background: "#f0f2f5", overflow: "auto" }}>
          <div style={{ maxWidth: "100%", margin: "0 auto" }}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/tasks" element={<ResearchTasks />} />
              <Route path="/runs/:runId" element={<AgentRunDetail />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/reports/:reportId" element={<ReportDetail />} />
              <Route path="/search" element={<Search />} />
              <Route path="/weekly" element={<Weekly />} />
            </Routes>
          </div>
        </Content>
      </Layout>
    </Layout>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  );
}

export default App;
