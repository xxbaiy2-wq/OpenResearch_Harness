import React, { useState } from "react";
import { Card, Input, Button, List, Tag, Typography, Empty, Space, Row, Col } from "antd";
import { SearchOutlined } from "@ant-design/icons";
import axios from "axios";

const { Text } = Typography;

export default function Search() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function handleSearch() {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await axios.get(`http://localhost:8000/api/reports/search?q=${query}`);
      setResults(res.data);
    } catch {
      setResults(null);
    }
    setLoading(false);
  }

  const sourceColor: Record<string, string> = { github: "default", arxiv: "orange", rss: "green" };

  return (
    <div>
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={8}>
          <Col flex="auto">
            <Input
              value={query}
              onChange={e => setQuery(e.target.value)}
              onPressEnter={handleSearch}
              placeholder="输入关键词，如：LangGraph、RAG、MCP"
              size="large"
            />
          </Col>
          <Col>
            <Button type="primary" icon={<SearchOutlined />} size="large" loading={loading} onClick={handleSearch}>
              搜索
            </Button>
          </Col>
        </Row>
      </Card>

      {results && (
        <Card title={`搜索结果：「${results.query}」共 ${results.count} 条`}>
          {results.items.length === 0 ? (
            <Empty description="没有找到相关内容" />
          ) : (
            <List
              dataSource={results.items}
              renderItem={(item: any) => (
                <List.Item>
                  <List.Item.Meta
                    title={
                      <Space>
                        {item.url ? (
                          <a href={item.url} target="_blank" rel="noopener noreferrer">{item.title}</a>
                        ) : <Text>{item.title}</Text>}
                        <Tag color={sourceColor[item.source_type]}>{item.source_type}</Tag>
                      </Space>
                    }
                    description={<Text type="secondary">{item.summary}</Text>}
                  />
                </List.Item>
              )}
            />
          )}
        </Card>
      )}
    </div>
  );
}
