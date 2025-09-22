/**
 * Subtitle Translator Component
 */

import React from 'react';
import { Card, Text, Button, Stack, Alert } from '@mantine/core';
import { IconLanguage } from '@tabler/icons-react';

const SubtitleTranslator: React.FC = () => {
  return (
    <Stack spacing="lg">
      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Stack spacing="md">
          <div>
            <Text size="lg" weight={500} mb="xs">
              Dịch phụ đề
            </Text>
            <Text size="sm" color="dimmed">
              Dịch phụ đề sang tiếng Việt
            </Text>
          </div>

          <Alert color="orange">
            <Text size="sm">
              Tính năng đang được phát triển. Sẽ có sẵn trong phiên bản sắp tới.
            </Text>
          </Alert>

          <Button disabled>
            Dịch phụ đề
          </Button>
        </Stack>
      </Card>
    </Stack>
  );
};

export default SubtitleTranslator;