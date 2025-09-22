/**
 * Video Synthesizer Component
 */

import React from 'react';
import { Card, Text, Button, Stack, Alert } from '@mantine/core';
import { IconSettings } from '@tabler/icons-react';

const VideoSynthesizer: React.FC = () => {
  return (
    <Stack spacing="lg">
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Stack spacing="md">
          <div>
            <Text size="lg" weight={500} mb="xs">
              Tổng hợp video
            </Text>
            <Text size="sm" color="dimmed">
              Tổng hợp video với audio và phụ đề mới
            </Text>
          </div>

          <Alert color="orange">
            <Text size="sm">
              Tính năng đang được phát triển. Sẽ có sẵn trong phiên bản sắp tới.
            </Text>
          </Alert>

          <Button disabled>
            Tổng hợp video
          </Button>
        </Stack>
      </Card>
    </Stack>
  );
};

export default VideoSynthesizer;