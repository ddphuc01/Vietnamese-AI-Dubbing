/**
 * Voice Separator Component
 */

import React from 'react';
import { Card, Text, Button, Stack, Alert } from '@mantine/core';
import { IconMicrophone } from '@tabler/icons-react';

const VoiceSeparator: React.FC = () => {
  return (
    <Stack spacing="lg">
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Stack spacing="md">
          <div>
            <Text size="lg" weight={500} mb="xs">
              Tách giọng nói
            </Text>
            <Text size="sm" color="dimmed">
              Tách giọng nói và âm nhạc từ video
            </Text>
          </div>

          <Alert color="orange">
            <Text size="sm">
              Tính năng đang được phát triển. Sẽ có sẵn trong phiên bản sắp tới.
            </Text>
          </Alert>

          <Button disabled>
            Tách giọng nói
          </Button>
        </Stack>
      </Card>
    </Stack>
  );
};

export default VoiceSeparator;