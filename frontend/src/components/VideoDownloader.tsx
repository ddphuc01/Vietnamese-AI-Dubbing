/**
 * Video Downloader Component
 */

import React, { useState } from 'react';
import {
  Card,
  Text,
  Button,
  TextInput,
  Select,
  Stack,
  Group,
  Progress,
  Alert,
  Badge
} from '@mantine/core';
import { IconDownload, IconLink, IconSettings } from '@tabler/icons-react';

const VideoDownloader: React.FC = () => {
  const [url, setUrl] = useState('');
  const [quality, setQuality] = useState('720p');
  const [isDownloading, setIsDownloading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleDownload = async () => {
    if (!url) return;

    setIsDownloading(true);
    setProgress(0);

    // Simulate download progress
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsDownloading(false);
          return 100;
        }
        return prev + 10;
      });
    }, 500);
  };

  return (
    <Stack spacing="lg">
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Stack spacing="md">
          <div>
            <Text size="lg" weight={500} mb="xs">
              Tải video từ Internet
            </Text>
            <Text size="sm" color="dimmed">
              Tải video từ YouTube, Vimeo và các nền tảng khác
            </Text>
          </div>

          <TextInput
            placeholder="Nhập URL video..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            icon={<IconLink size={16} />}
          />

          <Select
            label="Chất lượng"
            value={quality}
            onChange={(value) => setQuality(value || '720p')}
            data={[
              { value: '144p', label: '144p' },
              { value: '240p', label: '240p' },
              { value: '360p', label: '360p' },
              { value: '480p', label: '480p' },
              { value: '720p', label: '720p (HD)' },
              { value: '1080p', label: '1080p (Full HD)' },
              { value: '4k', label: '4K' },
            ]}
          />

          {isDownloading && (
            <div>
              <Group position="apart" mb="xs">
                <Text size="sm">Đang tải...</Text>
                <Badge color="blue">{progress}%</Badge>
              </Group>
              <Progress value={progress} color="blue" />
            </div>
          )}

          <Button
            onClick={handleDownload}
            disabled={!url || isDownloading}
            leftIcon={<IconDownload size={16} />}
          >
            {isDownloading ? 'Đang tải...' : 'Tải video'}
          </Button>
        </Stack>
      </Card>

      <Alert color="blue" icon={<IconSettings size={16} />}>
        <Text size="sm">
          Hỗ trợ tải từ: YouTube, Vimeo, Dailymotion, Facebook, Instagram, TikTok
        </Text>
      </Alert>
    </Stack>
  );
};

export default VideoDownloader;