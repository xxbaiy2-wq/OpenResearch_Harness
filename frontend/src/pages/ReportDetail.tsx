import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { Card, Tag, Typography, Space, Row, Col, Statistic, Descriptions } from "antd";
import { FileTextOutlined, CheckCircleOutlined, BookOutlined } from "@ant-design/icons";
import axios from "axios";

const { Title, Paragraph, Text } = Typography;

export default function ReportDetail() {
  const { reportId } = useParams();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    axios.get(`http://localhost:8000/api/reports/${reportId}`)
      .then(res => setData(res.data))
      .catch(() => setData(null));
  }, [reportId]);

  if (!data || !data.report) return <Card loading>加载中...</Card>;

  const { report, items, verification } = data;
  let sections: any[] = [];
  try {
    sections = JSON.parse(report.content).sections || [];
  } catch {}

  const sourceStats: Record<string, number> = {};
  items?.forEach((i: any) => { sourceStats[i.source_type] = (sourceStats[i.source_type] || 0) + 1; });

  return (
    <div>
      <Link to="/reports">← 返回报告列表</Link>

      <Card style={{ marginTop: 16, marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>{report.title}</Title>
        <Descriptions size="small" style={{ marginTop: 12 }} column={4}>
          <Descriptions.Item label="报告 ID">{report.id}</Descriptions.Item>
          <Descriptions.Item label="Run ID">
            <Link to={`/runs/${report.run_id}`}>{report.run_id}</Link>
          </Descriptions.Item>
          <Descriptions.Item label="状态"><Tag>{report.status}</Tag></Descriptions.Item>
          <Descriptions.Item label="生成时间">{report.created_at?.slice(0, 19)}</Descriptions.Item>
        </Descriptions>
      </Card>

      {/* 统计 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card><Statistic title="收录内容" value={items?.length || 0} suffix="条" prefix={<BookOutlined />} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="板块数量" value={sections.length} suffix="个" prefix={<FileTextOutlined />} /></Card>
        </Col>
        {verification && (
          <Col span={12}>
            <Card>
              <Statistic title="验证结果" value={verification.passed ? "通过" : "未通过"}
                valueRender={() => <Tag color={verification.passed ? "success" : "warning"}><CheckCircleOutlined /> 分数: {verification.score}</Tag>} />
            </Card>
          </Col>
        )}
      </Row>

      {/* 报告正文 */}
      {sections.map((section, i) => (
        <Card key={i} title={section.heading} style={{ marginBottom: 16 }}>
          {section.items?.map((item: any, j: number) => (
            <Card key={j} type="inner" style={{ marginBottom: j < section.items.length - 1 ? 12 : 0 }}>
              <Title level={5} style={{ margin: "0 0 8px" }}>
                {item.url ? <a href={item.url} target="_blank" rel="noopener noreferrer">{item.title}</a> : item.title}
                {item.source_type && <Tag style={{ marginLeft: 8 }}>{item.source_type}</Tag>}
              </Title>
              <Paragraph type="secondary" style={{ margin: "0 0 6px", fontSize: 13 }}>{item.summary}</Paragraph>
              <Paragraph style={{ margin: 0, fontSize: 13, color: "#1890ff" }}>💡 {item.why_it_matters}</Paragraph>
            </Card>
          ))}
        </Card>
      ))}

      {/* 来源列表 */}
      {items?.length > 0 && (
        <Card title={<span>🔗 来源列表 ({items.length})</span>}>
          {items.map((item: any, i: number) => (
            <Card key={i} type="inner" size="small" style={{ marginBottom: 8 }}>
              <Space direction="vertical" size={2} style={{ width: "100%" }}>
                <Space>
                  <Text strong>{i + 1}. {item.title || "无标题"}</Text>
                  <Tag>{item.source_type}</Tag>
                </Space>
                {item.url && <a href={item.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: 12 }}>{item.url}</a>}
              </Space>
            </Card>
          ))}
        </Card>
      )}
    </div>
  );
}
