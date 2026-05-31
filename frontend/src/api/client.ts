// 前端所有调后端的请求都集中在这个文件里，改 API 地址只改一处。
// frontend/src/api/client.ts

import axios from "axios";

// 设置后端地址，所有请求自动拼接
const api = axios.create({
  baseURL: "http://localhost:8000/api",
});

// 创建研究任务
export async function createTask(topic: string, description?: string) {
  const res = await api.post("/tasks", { topic, description });
  return res.data;
}

// 获取任务列表
export async function listTasks() {
  const res = await api.get("/tasks");
  return res.data;
}

// 触发任务运行
export async function runTask(taskId: number) {
  const res = await api.post(`/tasks/${taskId}/run`);
  return res.data;
}

// 获取 run 详情（包含 steps + tool_calls + verification）
export async function getRunDetail(runId: number) {
  const res = await api.get(`/agent-runs/${runId}`);
  return res.data;
}

// 获取报告列表
export async function listReports() {
  const res = await api.get("/reports");
  return res.data;
}

// 获取单篇报告
export async function getReport(reportId: number) {
  const res = await api.get(`/reports/${reportId}`);
  return res.data;
}
