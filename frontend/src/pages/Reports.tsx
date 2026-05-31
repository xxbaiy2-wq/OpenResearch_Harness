import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Card, Table, Tag, Empty } from "antd";
import { FileTextOutlined } from "@ant-design/icons";
import { listReports } from "../api/client";

export default function Reports() {
  const [reports, setReports] = useState<any[]>([]);

  useEffect(() => { listReports().then(setReports); }, []);

  const columns = [
    { title: "ID", dataIndex: "id", width: 60 },
    { title: "标题", dataIndex: "title" },
    {
      title: "状态", dataIndex: "status", width: 100,
      render: (s: string) => <Tag color={s === "published" ? "success" : "default"}>{s}</Tag>,
    },
    { title: "生成时间", dataIndex: "created_at", width: 180, render: (t: string) => t?.slice(0, 19) },
    {
      title: "操作", width: 80,
      render: (_: any, r: any) => <Link to={`/reports/${r.id}`}>查看</Link>,
    },
  ];

  return (
    <Card title={<span><FileTextOutlined /> 历史报告</span>}>
      {reports.length === 0 ? (
        <Empty description="暂无报告" />
      ) : (
        <Table dataSource={reports} columns={columns} rowKey="id" pagination={{ pageSize: 10 }} size="middle" />
      )}
    </Card>
  );
}
