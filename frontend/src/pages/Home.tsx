import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { DatePicker, Typography, Divider, Space, Tag, Button, Row, Col } from "antd";
import {
  ReadOutlined,
  EyeOutlined,
  ApiOutlined,
  ThunderboltOutlined,
} from "@ant-design/icons";
import dayjs from "dayjs";
import axios from "axios";

const { Title, Text, Paragraph } = Typography;

export default function Home() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [selectedDate, setSelectedDate] = useState(dayjs());

  useEffect(() => {
    setLoading(true);
    const dateStr = selectedDate.format("YYYY-MM-DD");
    axios.get(`http://localhost:8000/api/reports/by-date/${dateStr}`)
      .then(res => setData(res.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [selectedDate]);

  return (
    <div style={{ background: "#fff", minHeight: "100vh" }}>
      {/* ===== 英雄区：恢宏大气 ===== */}
      <div style={{
        background: "linear-gradient(160deg, #0a0a1a 0%, #0f1b3d 30%, #1a237e 60%, #0d47a1 100%)",
        padding: "40px 0 36px",
        textAlign: "center",
        position: "relative",
        overflow: "hidden",
      }}>
        {/* 装饰圆 */}
        <div style={{
          position: "absolute", top: -120, right: -120,
          width: 300, height: 300, borderRadius: "50%",
          background: "rgba(25, 118, 210, 0.15)", filter: "blur(60px)",
        }} />
        <div style={{
          position: "absolute", bottom: -80, left: -80,
          width: 250, height: 250, borderRadius: "50%",
          background: "rgba(156, 39, 176, 0.12)", filter: "blur(50px)",
        }} />

        {/* LOGO + 名称 */}
        <div style={{ position: "relative", zIndex: 1 }}>
          <div style={{
            display: "inline-flex", alignItems: "center", justifyContent: "center",
            width: 56, height: 56, borderRadius: 16,
            background: "linear-gradient(135deg, #42a5f5, #7c4dff)",
            marginBottom: 16, boxShadow: "0 8px 32px rgba(66,165,245,0.4)",
          }}>
            <ApiOutlined style={{ fontSize: 36, color: "#fff" }} />
          </div>

          <Title level={1} style={{
            color: "#fff", margin: 0, fontSize: 40, fontWeight: 800,
            letterSpacing: 4, textShadow: "0 2px 16px rgba(0,0,0,0.3)",
          }}>
            每日五分钟了解前沿
          </Title>

          <Text style={{
            color: "rgba(255,255,255,0.65)", fontSize: 16, marginTop: 8,
            display: "block", letterSpacing: 2,
          }}>
            AI 技术趋势雷达 · 智能采集 · 深度分析 · 每日速递
          </Text>

          {/* 三个核心卖点 */}
          <Row gutter={32} justify="center" style={{ maxWidth: 600, margin: "20px auto 0" }}>
            <Col span={8}>
              <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 12 }}>🔍 智能采集</div>
              <div style={{ color: "rgba(255,255,255,0.8)", fontSize: 14, marginTop: 4 }}>arXiv · GitHub · RSS</div>
            </Col>
            <Col span={8}>
              <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 12 }}>🧠 AI 分析</div>
              <div style={{ color: "rgba(255,255,255,0.8)", fontSize: 14, marginTop: 4 }}>LLM 深度总结</div>
            </Col>
            <Col span={8}>
              <div style={{ color: "rgba(255,255,255,0.4)", fontSize: 12 }}>📊 每日更新</div>
              <div style={{ color: "rgba(255,255,255,0.8)", fontSize: 14, marginTop: 4 }}>定时自动生成</div>
            </Col>
          </Row>

          {/* 日期选择 */}
          <div style={{ marginTop: 20 }}>
            <DatePicker
              value={selectedDate}
              onChange={(v) => v && setSelectedDate(v)}
              size="large"
              style={{ width: 240, height: 44, borderRadius: 22 }}
              allowClear={false}
              format="YYYY-MM-DD"
            />
          </div>
        </div>
      </div>

      {/* ===== 文章内容区 ===== */}
      <div style={{ maxWidth: "100%", margin: "0 auto", padding: "0 40px 48px" }}>
        {!data ? (
          <div style={{ textAlign: "center", padding: "80px 0" }}>
            {loading ? (
              <Text type="secondary" style={{ fontSize: 16 }}>正在加载技术雷达...</Text>
            ) : (
              <>
                <ReadOutlined style={{ fontSize: 64, color: "#d9d9d9", marginBottom: 24 }} />
                <Title level={4} type="secondary" style={{ fontWeight: 400 }}>
                  {selectedDate.format("YYYY年MM月DD日")} 暂无技术雷达
                </Title>
                <Text type="secondary">系统会每天自动生成，或</Text>
                <br />
                <Link to="/tasks">
                  <Button type="primary" size="large" style={{ marginTop: 16, borderRadius: 20, padding: "0 32px" }}>
                    立即创建研究任务
                  </Button>
                </Link>
              </>
            )}
          </div>
        ) : (
          <ArticleContent data={data} />
        )}
      </div>
    </div>
  );
}

function ArticleContent({ data }: { data: any }) {
  const { report } = data;

  let sections: any[] = [];
  let title = report.title;
  try {
    const parsed = JSON.parse(report.content);
    title = parsed.title || title;
    if (parsed.sections && parsed.sections[0]?.items) {
      // 旧格式：sections[].items[] → 转成文章
      sections = parsed.sections.map((s: any) => ({
        heading: s.heading,
        content: (s.items || []).map((item: any) =>
          `【${item.title || "无标题"}】${item.summary || ""}${item.why_it_matters ? " 💡" + item.why_it_matters : ""}`
        ).join("\n\n"),
      }));
    } else {
      sections = parsed.sections || [];
    }
  } catch {}

  const dateStr = report.created_at?.slice(0, 10);

  return (
    <article style={{
      background: "#fff",
      borderRadius: 12,
      boxShadow: "0 4px 24px rgba(0,0,0,0.08)",
      padding: "48px 72px",
      maxWidth: 1300,
      margin: "0 auto",
    }}>
      {/* 文章标题 */}
      <div style={{ textAlign: "center", marginBottom: 28 }}>
        <Tag color="processing" style={{ fontSize: 14, padding: "5px 16px", borderRadius: 20, marginBottom: 16 }}>
          {dateStr}
        </Tag>
        <Title level={2} style={{ fontSize: 32, fontWeight: 700, margin: "8px 0 12px", color: "#1a1a2e" }}>
          {title}
        </Title>
        <Text style={{ color: "#999", fontSize: 14 }}>
          由 OpenResearch Agent 自动生成 ·
          <Link to={`/runs/${report.run_id}`} style={{ marginLeft: 4, color: "#1890ff" }}>查看执行轨迹 →</Link>
        </Text>
      </div>

      <Divider style={{ margin: "0 0 32px" }} />

      {/* 文章正文 */}
      <div style={{ fontSize: 16, lineHeight: 2, color: "#333" }}>
        {sections.length > 0 ? (
          sections.map((section, i) => (
            <div key={i} style={{ marginBottom: 32 }}>
              <div style={{
                fontSize: 22, fontWeight: 700, color: "#1a1a2e", marginBottom: 12,
                borderLeft: "4px solid #1890ff", paddingLeft: 14,
              }}>
                {section.heading}
              </div>
              <Paragraph style={{
                fontSize: 16, lineHeight: 2, textAlign: "justify",
                textIndent: "2em", margin: 0,
              }}>
                {section.content}
              </Paragraph>
            </div>
          ))
        ) : (
          <Paragraph style={{ fontSize: 16, lineHeight: 2, whiteSpace: "pre-wrap", textIndent: "2em" }}>
            {report.content}
          </Paragraph>
        )}
      </div>

      <Divider style={{ margin: "32px 0 24px" }} />

      {/* 底部 */}
      <div style={{ textAlign: "center" }}>
        <Space size="large">
          <Text type="secondary" style={{ fontSize: 13 }}>
            <EyeOutlined /> 报告 #{report.id}
          </Text>
          <Text type="secondary" style={{ fontSize: 13 }}>
            <ThunderboltOutlined /> Run #{report.run_id}
          </Text>
          <Link to="/reports" style={{ fontSize: 13 }}>
            查看更多历史报告 →
          </Link>
        </Space>
      </div>
    </article>
  );
}
