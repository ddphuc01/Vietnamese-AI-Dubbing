/**
 * Result Component - Display processing results
 */

import React from 'react';
import {
  Card,
  Text,
  Button,
  Group,
  Stack,
  Badge,
  Divider,
  Alert,
  ActionIcon,
  Menu
} from '@mantine/core';
import {
  IconDownload,
  IconShare,
  IconCopy,
  IconDots,
  IconCheck,
  IconX,
  IconPlayerPlay
} from '@tabler/icons-react';

interface ResultProps {
  videoUrl: string | null;
  audioUrl: string | null;
  onReset: () => void;
  jobId?: string;
  processingTime?: number;
  fileSize?: string;
}

const Result: React.FC<ResultProps> = ({
  videoUrl,
  audioUrl,
  onReset,
  jobId,
  processingTime,
  fileSize
}) => {
  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleDownload = (url: string, filename: string) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleCopyUrl = async (url: string) => {
    try {
      await navigator.clipboard.writeText(url);
      // You could show a notification here
    } catch (error) {
      console.error('Failed to copy URL:', error);
    }
  };

  const handleShare = async () => {
    if (navigator.share && videoUrl) {
      try {
        await navigator.share({
          title: 'Vietnamese AI Dubbing Result',
          text: 'Video đã được lồng tiếng bằng AI',
          url: videoUrl,
        });
      } catch (error) {
        console.error('Error sharing:', error);
      }
    }
  };

  return (
    <Stack spacing="lg">
      <Alert color="green" icon={<IconCheck size={16} />} title="Xử lý thành công!">
        Video của bạn đã được lồng tiếng thành công. Bạn có thể tải xuống hoặc chia sẻ kết quả.
      </Alert>

      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Stack spacing="md">
          <div>
            <Group position="apart" mb="xs">
              <Text size="lg" weight={500}>
                Kết quả xử lý
              </Text>
              <Badge color="green" variant="light">
                Hoàn thành
              </Badge>
            </Group>
            <Text size="sm" color="dimmed">
              Video đã được xử lý thành công với giọng tiếng Việt
            </Text>
          </div>

          <Divider />

          {/* Video Result */}
          {videoUrl && (
            <div>
              <Text size="md" weight={500} mb="sm">
                Video hoàn chỉnh
              </Text>
              <div style={{ position: 'relative', paddingBottom: '56.25%', height: 0, overflow: 'hidden', borderRadius: '8px' }}>
                <video
                  src={videoUrl}
                  controls
                  style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    borderRadius: '8px'
                  }}
                />
              </div>
            </div>
          )}

          {/* Audio Result */}
          {audioUrl && (
            <div>
              <Text size="md" weight={500} mb="sm">
                Audio lồng tiếng
              </Text>
              <audio
                src={audioUrl}
                controls
                style={{
                  width: '100%',
                  borderRadius: '8px'
                }}
              />
            </div>
          )}

          <Divider />

          {/* Job Information */}
          <div>
            <Text size="md" weight={500} mb="sm">
              Thông tin xử lý
            </Text>
            <Group spacing="xl">
              {jobId && (
                <div>
                  <Text size="sm" color="dimmed">Job ID</Text>
                  <Text size="sm" weight={500}>{jobId.substring(0, 8)}...</Text>
                </div>
              )}
              {processingTime && (
                <div>
                  <Text size="sm" color="dimmed">Thời gian xử lý</Text>
                  <Text size="sm" weight={500}>{formatTime(processingTime)}</Text>
                </div>
              )}
              {fileSize && (
                <div>
                  <Text size="sm" color="dimmed">Kích thước file</Text>
                  <Text size="sm" weight={500}>{fileSize}</Text>
                </div>
              )}
            </Group>
          </div>

          <Divider />

          {/* Action Buttons */}
          <Group position="apart">
            <Group spacing="sm">
              {videoUrl && (
                <Button
                  leftIcon={<IconDownload size={16} />}
                  onClick={() => handleDownload(videoUrl, 'video_dubbed.mp4')}
                >
                  Tải video
                </Button>
              )}

              {audioUrl && (
                <Button
                  variant="light"
                  leftIcon={<IconDownload size={16} />}
                  onClick={() => handleDownload(audioUrl, 'audio_dubbed.mp3')}
                >
                  Tải audio
                </Button>
              )}

              {videoUrl && (
                <Button
                  variant="light"
                  leftIcon={<IconShare size={16} />}
                  onClick={handleShare}
                >
                  Chia sẻ
                </Button>
              )}
            </Group>

            <Menu shadow="md" width={150}>
              <Menu.Target>
                <ActionIcon>
                  <IconDots size={16} />
                </ActionIcon>
              </Menu.Target>
              <Menu.Dropdown>
                {videoUrl && (
                  <Menu.Item
                    icon={<IconCopy size={14} />}
                    onClick={() => handleCopyUrl(videoUrl)}
                  >
                    Sao chép URL video
                  </Menu.Item>
                )}
                {audioUrl && (
                  <Menu.Item
                    icon={<IconCopy size={14} />}
                    onClick={() => handleCopyUrl(audioUrl)}
                  >
                    Sao chép URL audio
                  </Menu.Item>
                )}
                <Menu.Item
                  icon={<IconX size={14} />}
                  color="red"
                  onClick={onReset}
                >
                  Xử lý video mới
                </Menu.Item>
              </Menu.Dropdown>
            </Menu>
          </Group>
        </Stack>
      </Card>

      {/* Additional Information */}
      <Card shadow="sm" padding="md" radius="md" withBorder style={{ backgroundColor: 'var(--mantine-color-blue-light)' }}>
        <Group position="apart">
          <div>
            <Text size="sm" weight={500} color="blue">
              Mẹo sử dụng
            </Text>
            <Text size="xs" color="blue">
              Bạn có thể tải xuống cả video và audio riêng biệt để sử dụng linh hoạt
            </Text>
          </div>
          <Button
            size="sm"
            variant="light"
            color="blue"
            onClick={onReset}
          >
            Xử lý video khác
          </Button>
        </Group>
      </Card>
    </Stack>
  );
};

export default Result;