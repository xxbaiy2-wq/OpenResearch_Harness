import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Card, InputNumber, Empty, Row, Col, Statistic, List, Typography, Space } from "antd";
import { BarChartOutlined, FileTextOutlined, BookOutlined } from "@ant-design/icons";
import axios from "axios";

const { Title, Text } = Typography;

export default function Weekly() {
  const today = new Date();
  const [year, setYear] = useState(today.getFullYear());
  const [week, setWeek] = useState(getWeek(today));
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    axios.get(`http://localhost:8000/api/reports/weekly/${year}/${week}`)
      .then(res => setData(res.data))
      .catch(() => setData(null));
  }, [year, week]);

  return (
    <div>
      <Card style={{ marginBottom: 16 }}>
        <Space size="large">
          <Space>
            <Text>年份：</Text>
            <InputNumber value={year} onChange={v => setYear(Number(v))} min={2024} max={2030} />
          </Space>
          <Space>
            <Text>第</Text>
            <InputNumber value={week} onChange={v => setWeek(Number(v))} min={1} max={53} />
            <Text>周</Text>
          </Space>
        </Space>
      </Card>

      {!data ? (
        <Card><Empty description={`${year}年第${week}周暂无数据`} /></Card>
      ) : (
        <>
          <Card title={<span><BarChartOutlined /> 概览</span>} style={{ marginBottom: 16 }}>
            <Row gutter={24}>
              <Col span={8}><Statistic title="日报数量" value={data.report_count} suffix="篇" prefix={<FileTextOutlined />} /></Col>
              <Col span={8}><Statistic title="收集内容" value={data.item_count} suffix="条" prefix={<BookOutlined />} /></Col>
              <Col span={8}>
                <Statistic title="来源分布" valueRender={() =>
                  <Space>{Object.entries(data.source_stats).map(([k, v]: [string, any]) => <span key={k}>{k}: {v}</span>)}</Space>
                } />
              </Col>
            </Row>
          </Card>

          <Card title="每日报告">
            <List
              dataSource={data.daily_reports}
              renderItem={(r: any) => (
                <List.Item>
                  <Space>
                    <Text type="secondary">{r.created_at}</Text>
                    <Link to={`/reports/${r.id}`}>{r.title}</Link>
                  </Space>
                </List.Item>
              )}
            />
          </Card>
        </>
      )}
    </div>
  );
}

function getWeek(d: Date) {
  const onejan = new Date(d.getFullYear(), 0, 1);
  return Math.ceil(((d.getTime() - onejan.getTime()) / 86400000 + onejan.getDay() + 1) / 7);
}
