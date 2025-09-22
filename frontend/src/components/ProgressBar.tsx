/**
 * Progress Bar Component
 */

import React from 'react';
import { Progress, Text, Stack, Group, Badge } from '@mantine/core';
import { IconCheck, IconX, IconClock, IconLoader } from '@tabler/icons-react';
import { DubbingStage } from '../types';

interface ProgressBarProps {
  stage: DubbingStage;
  progress: number;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ stage, progress }) => {
  const getStageInfo = (stage: DubbingStage) => {
    switch (stage) {
      case DubbingStage.IDLE:
        return {
          label: 'Sẵn sàng',
          description: 'Chuẩn bị bắt đầu xử lý',
          icon: IconClock,
          color: 'gray'
        };
      case DubbingStage.DOWNLOADING:
        return {
          label: 'Đang tải video',
          description: 'Đang tải video từ nguồn',
          icon: IconLoader,
          color: 'blue'
        };
      case DubbingStage.TRANSCRIBING:
        return {
          label: 'Đang chuyển văn bản',
          description: 'Đang nhận diện giọng nói và chuyển thành văn bản',
          icon: IconLoader,
          color: 'blue'
        };
      case DubbingStage.TRANSLATING:
        return {
          label: 'Đang dịch',
          description: 'Đang dịch văn bản sang tiếng Việt',
          icon: IconLoader,
          color: 'blue'
        };
      case DubbingStage.GENERATING_AUDIO:
        return {
          label: 'Đang tạo audio',
          description: 'Đang tạo file audio với giọng tiếng Việt',
          icon: IconLoader,
          color: 'blue'
        };
      case DubbingStage.MERGING:
        return {
          label: 'Đang hợp nhất',
          description: 'Đang hợp nhất video gốc với audio mới',
          icon: IconLoader,
          color: 'blue'
        };
      case DubbingStage.DONE:
        return {
          label: 'Hoàn thành',
          description: 'Xử lý video thành công',
          icon: IconCheck,
          color: 'green'
        };
      default:
        return {
          label: 'Không xác định',
          description: 'Trạng thái không xác định',
          icon: IconX,
          color: 'red'
        };
    }
  };

  const stageInfo = getStageInfo(stage);
  const IconComponent = stageInfo.icon;

  return (
    <Stack spacing="md">
      <div>
        <Group position="apart" mb="xs">
          <Text size="sm" weight={500}>
            Tiến độ xử lý
          </Text>
          <Badge color={stageInfo.color} variant="light">
            {stageInfo.label}
          </Badge>
        </Group>

        <Progress
          value={progress}
          color={stageInfo.color}
          size="lg"
          radius="md"
          mb="xs"
        />

        <Group position="apart">
          <Text size="xs" color="dimmed">
            {progress.toFixed(1)}% hoàn thành
          </Text>
          <Text size="xs" color="dimmed">
            {stageInfo.description}
          </Text>
        </Group>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <IconComponent size={16} color={`var(--mantine-color-${stageInfo.color}-6)`} />
        <Text size="sm" color={stageInfo.color}>
          {stageInfo.label}
        </Text>
      </div>
    </Stack>
  );
};

export default ProgressBar;