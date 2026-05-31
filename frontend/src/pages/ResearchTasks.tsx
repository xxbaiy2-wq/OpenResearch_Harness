import React, { useState, useEffect } from "react";
import { Card, Table, Button, Input, Tag, Space, message } from "antd";
import { PlusOutlined, PlayCircleOutlined } from "@ant-design/icons";
import { createTask, listTasks, runTask } from "../api/client";

interface Task {
  id: number;
  topic: string;
  status: string;
  created_at: string;
}

const statusMap: Record<string, { color: string; text: string }> = {
  pending: { color: "default", text: "等待中" },
  running: { color: "processing", text: "运行中" },
  success: { color: "success", text: "成功" },
  failed: { color: "error", text: "失败" },
  verified_failed: { color: "warning", text: "验证未过" },
};

export default function ResearchTasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState<Record<number, boolean>>({});

  useEffect(() => { loadTasks(); }, []);

  async function loadTasks() {
    const data = await listTasks();
    setTasks(data);
  }

  async function handleCreate() {
    if (!topic.trim()) return;
    setLoading(true);
    await createTask(topic);
    setTopic("");
    await loadTasks();
    message.success("任务创建成功");
    setLoading(false);
  }

  async function handleRun(taskId: number) {
    setRunning(prev => ({ ...prev, [taskId]: true }));
    const result = await runTask(taskId);
    message.success(`Run 完成！run_id = ${result.run_id}`);
    await loadTasks();
    setRunning(prev => ({ ...prev, [taskId]: false }));
  }

  const columns = [
    { title: "ID", dataIndex: "id", width: 60 },
    { title: "主题", dataIndex: "topic" },
    {
      title: "状态", dataIndex: "status", width: 100,
      render: (s: string) => {
        const info = statusMap[s] || { color: "default", text: s };
        return <Tag color={info.color}>{info.text}</Tag>;
      },
    },
    { title: "创建时间", dataIndex: "created_at", width: 180, render: (t: string) => t?.slice(0, 19) },
    {
      title: "操作", width: 100,
      render: (_: any, record: Task) => (
        <Button
          type="primary"
          icon={<PlayCircleOutlined />}
          size="small"
          loading={running[record.id]}
          onClick={() => handleRun(record.id)}
        >
          Run
        </Button>
      ),
    },
  ];

  return (
    <div>
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Input
            value={topic}
            onChange={e => setTopic(e.target.value)}
            placeholder="输入研究主题，如：LangGraph"
            style={{ width: 300 }}
            onPressEnter={handleCreate}
          />
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate} loading={loading}>
            创建任务
          </Button>
        </Space>
      </Card>

      <Card title={<Space><span>研究任务</span><Tag>{tasks.length}</Tag></Space>}>
        <Table
          dataSource={tasks}
          columns={columns}
          rowKey="id"
          pagination={{ pageSize: 10 }}
          size="middle"
        />
      </Card>
    </div>
  );
}
