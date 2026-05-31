import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Card, Tag, Timeline, Table, Typography, Row, Col, Statistic, Space, Empty, Collapse } from "antd";
import { ClockCircleOutlined, CheckCircleOutlined, CloseCircleOutlined } from "@ant-design/icons";
import { getRunDetail } from "../api/client";

const { Title, Text } = Typography;

export default function AgentRunDetail() {
  const { runId } = useParams();
  const [detail, setDetail] = useState<any>(null);

  useEffect(() => {
    if (runId) getRunDetail(Number(runId)).then(setDetail);
  }, [runId]);

  if (!detail) return <Card loading>加载中...</Card>;

  const { run, steps, tool_calls, verification } = detail;

  const statusColor: Record<string, string> = {
    success: "success", failed: "error", running: "processing",
  };

  return (
    <div>
      <Link to="/">← 返回</Link>
      <Title level={3} style={{ marginTop: 8 }}>Agent Run #{run.id}</Title>

      {/* 概况 */}
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={24}>
          <Col span={6}>
            <Statistic title="状态" value={run.status}
              valueRender={() => <Tag color={statusColor[run.status] || "default"}>{run.status}</Tag>} />
          </Col>
          <Col span={6}>
            <Statistic title="总耗时" value={run.total_latency_ms} suffix="ms" prefix={<ClockCircleOutlined />} />
          </Col>
          <Col span={6}>
            <Statistic title="Steps" value={steps.length} suffix="个" />
          </Col>
          <Col span={6}>
            <Statistic title="Tool Calls" value={tool_calls.length} suffix="次" />
          </Col>
        </Row>
        {run.error_message && <Text type="danger" style={{ display: "block", marginTop: 12 }}>错误：{run.error_message}</Text>}
      </Card>

      {/* Step Timeline */}
      <Card title="⏱️ Step Timeline" style={{ marginBottom: 16 }}>
        <Timeline
          items={steps.map((s: any) => ({
            color: s.status === "success" ? "green" : "red",
            children: (
              <div>
                <Space>
                  <strong>{s.step_name}</strong>
                  <Tag color={s.status === "success" ? "success" : "error"}>{s.status}</Tag>
                  <Text type="secondary">{s.latency_ms} ms</Text>
                </Space>
                {s.error_message && <Text type="danger" style={{ display: "block" }}>{s.error_message}</Text>}
                <Collapse ghost size="small" items={[{
                  key: "detail",
                  label: "查看输入输出",
                  children: <pre style={{ background: "#f5f5f5", padding: 8, borderRadius: 4, fontSize: 12, maxHeight: 200, overflow: "auto" }}>
                    {JSON.stringify({ input: s.input_json, output: s.output_json }, null, 2)}
                  </pre>
                }]} />
              </div>
            ),
          }))}
        />
      </Card>

      {/* Tool Calls */}
      <Card title={`🔧 Tool Calls (${tool_calls.length})`} style={{ marginBottom: 16 }}>
        {tool_calls.length === 0 ? (
          <Empty description="暂无工具调用记录" />
        ) : (
          <Table
            dataSource={tool_calls}
            size="small"
            pagination={false}
            rowKey="id"
            columns={[
              { title: "Tool", dataIndex: "tool_name", render: (t: string) => <Text strong>{t}</Text> },
              { title: "Status", dataIndex: "status", width: 80, render: (s: string) => <Tag color={s === "success" ? "success" : "error"}>{s}</Tag> },
              { title: "Latency", dataIndex: "latency_ms", width: 80, render: (v: number) => `${v} ms` },
              { title: "Retries", dataIndex: "retry_count", width: 70 },
            ]}
          />
        )}
      </Card>

      {/* Verification */}
      {verification && (
        <Card title="✅ Verification">
          <Space size="large">
            <Statistic title="通过" value={verification.passed ? "是" : "否"}
              valueRender={() => <Tag color={verification.passed ? "success" : "error"}>{verification.passed ? "通过" : "未通过"}</Tag>} />
            <Statistic title="分数" value={verification.score} suffix="/ 100" />
          </Space>
          {verification.problems?.length > 0 && (
            <ul style={{ marginTop: 12 }}>
              {verification.problems.map((p: any, i: number) => (
                <li key={i}><Text type="danger">{p.message}</Text></li>
              ))}
            </ul>
          )}
        </Card>
      )}
    </div>
  );
}
