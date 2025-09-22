/**
 * Jobs Page Component - Display and manage video processing jobs
 */

import React, { useEffect, useState, Suspense, lazy } from 'react';
import {
  Container,
  Title,
  Text,
  Card,
  Table,
  Badge,
  Button,
  Group,
  Stack,
  Loader,
  ActionIcon,
  Menu,
  TextInput,
  Select,
  Pagination,
  Progress
} from '@mantine/core';
import {
  IconRefresh,
  IconTrash,
  IconDownload,
  IconEye,
  IconDots,
  IconSearch,
  IconFilter
} from '@tabler/icons-react';
import { useAppStore } from '../store/useAppStore';
import { api, Job, JobStats } from '../api/client';

// Lazy load components
const Header = lazy(() => import('../components/Header'));

const JobsPage: React.FC = () => {
  const { jobs, jobStats, setJobs, setJobStats, setLoading, setError } = useAppStore();
  const [loading, setLocalLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const loadJobs = async () => {
    try {
      setLocalLoading(true);
      const response = await api.jobs.list({
        limit: 100,
        offset: 0
      });
      setJobs(response.data);
    } catch (error: any) {
      setError('Không thể tải danh sách jobs: ' + error.message);
    } finally {
      setLocalLoading(false);
    }
  };

  const loadJobStats = async () => {
    try {
      const response = await api.jobs.stats();
      setJobStats(response.data);
    } catch (error: any) {
      console.error('Failed to load job stats:', error);
    }
  };

  useEffect(() => {
    loadJobs();
    loadJobStats();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'green';
      case 'processing':
        return 'blue';
      case 'pending':
        return 'yellow';
      case 'failed':
        return 'red';
      case 'cancelled':
        return 'gray';
      default:
        return 'gray';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Hoàn thành';
      case 'processing':
        return 'Đang xử lý';
      case 'pending':
        return 'Chờ xử lý';
      case 'failed':
        return 'Thất bại';
      case 'cancelled':
        return 'Đã hủy';
      default:
        return status;
    }
  };

  const filteredJobs = jobs.filter(job => {
    const matchesSearch = job.job_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.input_filename?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || job.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const paginatedJobs = filteredJobs.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handleDeleteJob = async (jobId: string) => {
    try {
      await api.jobs.delete(jobId);
      setJobs(jobs.filter(job => job.job_id !== jobId));
    } catch (error: any) {
      setError('Không thể xóa job: ' + error.message);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('vi-VN');
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <Container size="xl" py="xl">
      <Suspense fallback={<Loader />}>
        <Header />

        <Stack spacing="xl">
          <div style={{ textAlign: 'center' }}>
            <Title order={1} size="h1" mb="md">
              Quản lý Jobs
            </Title>
            <Text size="lg" color="dimmed" mb="xl">
              Theo dõi và quản lý các tác vụ xử lý video
            </Text>
          </div>

          {/* Stats Cards */}
          {jobStats && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
              <Card shadow="sm" padding="lg" radius="md" withBorder>
                <Text size="sm" color="dimmed">Tổng số jobs</Text>
                <Text size="xl" weight={700}>{jobStats.total_jobs}</Text>
              </Card>
              <Card shadow="sm" padding="lg" radius="md" withBorder>
                <Text size="sm" color="dimmed">Thành công</Text>
                <Text size="xl" weight={700} color="green">
                  {jobStats.status_counts.completed || 0}
                </Text>
              </Card>
              <Card shadow="sm" padding="lg" radius="md" withBorder>
                <Text size="sm" color="dimmed">Đang xử lý</Text>
                <Text size="xl" weight={700} color="blue">
                  {jobStats.status_counts.processing || 0}
                </Text>
              </Card>
              <Card shadow="sm" padding="lg" radius="md" withBorder>
                <Text size="sm" color="dimmed">Tỷ lệ thành công</Text>
                <Text size="xl" weight={700} color="orange">
                  {jobStats.success_rate.toFixed(1)}%
                </Text>
              </Card>
            </div>
          )}

          {/* Filters and Actions */}
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Group position="apart" mb="md">
              <Group>
                <TextInput
                  placeholder="Tìm kiếm job ID hoặc tên file..."
                  icon={<IconSearch size={16} />}
                  value={searchTerm}
                  onChange={(event) => setSearchTerm(event.currentTarget.value)}
                  style={{ width: 300 }}
                />
                <Select
                  placeholder="Lọc theo trạng thái"
                  icon={<IconFilter size={16} />}
                  value={statusFilter}
                  onChange={(value) => setStatusFilter(value || 'all')}
                  data={[
                    { value: 'all', label: 'Tất cả' },
                    { value: 'pending', label: 'Chờ xử lý' },
                    { value: 'processing', label: 'Đang xử lý' },
                    { value: 'completed', label: 'Hoàn thành' },
                    { value: 'failed', label: 'Thất bại' },
                    { value: 'cancelled', label: 'Đã hủy' },
                  ]}
                  style={{ width: 150 }}
                />
              </Group>
              <Button
                leftIcon={<IconRefresh size={16} />}
                onClick={loadJobs}
                loading={loading}
              >
                Làm mới
              </Button>
            </Group>

            {/* Jobs Table */}
            {loading ? (
              <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
                <Loader />
              </div>
            ) : (
              <Table striped highlightOnHover>
                <thead>
                  <tr>
                    <th>Job ID</th>
                    <th>Trạng thái</th>
                    <th>Tiến độ</th>
                    <th>File đầu vào</th>
                    <th>Thời gian tạo</th>
                    <th>Thời gian xử lý</th>
                    <th>Thao tác</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedJobs.map((job) => (
                    <tr key={job.id}>
                      <td>
                        <Text size="sm" weight={500}>
                          {job.job_id.substring(0, 8)}...
                        </Text>
                      </td>
                      <td>
                        <Badge color={getStatusColor(job.status)} variant="light">
                          {getStatusLabel(job.status)}
                        </Badge>
                      </td>
                      <td>
                        <div style={{ width: 100 }}>
                          <Progress value={job.progress} color={getStatusColor(job.status)} size="sm" />
                          <Text size="xs" color="dimmed" mt={2}>
                            {job.progress.toFixed(1)}%
                          </Text>
                        </div>
                      </td>
                      <td>
                        <Text size="sm" style={{ maxWidth: 200 }} truncate>
                          {job.input_filename || 'N/A'}
                        </Text>
                      </td>
                      <td>
                        <Text size="sm">
                          {formatDate(job.created_at)}
                        </Text>
                      </td>
                      <td>
                        <Text size="sm">
                          {job.processing_time ? formatDuration(job.processing_time) : 'N/A'}
                        </Text>
                      </td>
                      <td>
                        <Menu shadow="md" width={120}>
                          <Menu.Target>
                            <ActionIcon>
                              <IconDots size={16} />
                            </ActionIcon>
                          </Menu.Target>
                          <Menu.Dropdown>
                            <Menu.Item icon={<IconEye size={14} />}>
                              Xem chi tiết
                            </Menu.Item>
                            {job.status === 'completed' && (
                              <Menu.Item icon={<IconDownload size={14} />}>
                                Tải xuống
                              </Menu.Item>
                            )}
                            <Menu.Item
                              icon={<IconTrash size={14} />}
                              color="red"
                              onClick={() => handleDeleteJob(job.job_id)}
                            >
                              Xóa
                            </Menu.Item>
                          </Menu.Dropdown>
                        </Menu>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            )}

            {/* Pagination */}
            {filteredJobs.length > itemsPerPage && (
              <div style={{ display: 'flex', justifyContent: 'center', marginTop: '1rem' }}>
                <Pagination
                  total={Math.ceil(filteredJobs.length / itemsPerPage)}
                  value={currentPage}
                  onChange={setCurrentPage}
                  size="sm"
                />
              </div>
            )}

            {filteredJobs.length === 0 && !loading && (
              <div style={{ textAlign: 'center', padding: '2rem' }}>
                <Text color="dimmed">Không tìm thấy job nào</Text>
              </div>
            )}
          </Card>
        </Stack>
      </Suspense>
    </Container>
  );
};

export default JobsPage;