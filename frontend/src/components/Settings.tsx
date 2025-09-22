import React, { useState, useEffect } from 'react';
import { Select, Switch, Stack, Text, Card, Group, Divider } from '@mantine/core';
import { api } from '../api/client';

// Định nghĩa kiểu dữ liệu cho các tùy chọn
interface Option {
  value: string;
  label: string;
}

interface SettingsData {
  text_to_speech: {
    engines: string[];
    voices: Record<string, string>;
  };
  translation: {
    methods: string[];
  };
  // Thêm các service khác nếu cần
}

interface SettingsProps {
  // Các props để quản lý state từ component cha
  ttsEngine: string;
  setTtsEngine: (engine: string) => void;
  voiceId: string;
  setVoiceId: (voice: string) => void;
  translationMethod: string;
  setTranslationMethod: (method: string) => void;
  isMultiSpeaker: boolean;
  setIsMultiSpeaker: (isMulti: boolean) => void;
  disabled?: boolean;
}

const Settings: React.FC<SettingsProps> = ({
  ttsEngine,
  setTtsEngine,
  voiceId,
  setVoiceId,
  translationMethod,
  setTranslationMethod,
  isMultiSpeaker,
  setIsMultiSpeaker,
  disabled = false,
}) => {
  const [settingsData, setSettingsData] = useState<SettingsData | null>(null);
  const [voiceOptions, setVoiceOptions] = useState<Option[]>([]);

  // Lấy các tùy chọn xử lý từ backend
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const response = await api.health.getProcessingOptions(); // Giả sử client có phương thức này
        setSettingsData(response.data);

        // Set giá trị mặc định khi có dữ liệu
        if (response.data) {
          const defaultTtsEngine = response.data.text_to_speech?.engines?.[0] || '';
          const defaultTranslationMethod = response.data.translation?.methods?.[0] || '';
          setTtsEngine(defaultTtsEngine);
          setTranslationMethod(defaultTranslationMethod);
        }
      } catch (error) {
        console.error("Failed to fetch processing options:", error);
      }
    };
    fetchOptions();
  }, [setTtsEngine, setTranslationMethod]);

  // Cập nhật danh sách giọng đọc khi TTS engine thay đổi
  useEffect(() => {
    if (settingsData && ttsEngine) {
      const voices = settingsData.text_to_speech.voices || {};
      const options = Object.entries(voices).map(([value, label]) => ({ value, label }));
      setVoiceOptions(options);
      // Set giọng đọc mặc định nếu giọng đọc hiện tại không có trong danh sách mới
      if (!voices[voiceId]) {
        setVoiceId(options[0]?.value || '');
      }
    }
  }, [settingsData, ttsEngine, voiceId, setVoiceId]);

  if (!settingsData) {
    return <Text>Đang tải cài đặt...</Text>;
  }

  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Stack spacing="lg">
        <Text size="lg" weight={500}>Cài đặt xử lý</Text>
        <Divider />

        {/* Cài đặt Text-to-Speech */}
        <Stack spacing="sm">
          <Select
            label="Engine đọc (TTS)"
            placeholder="Chọn engine"
            value={ttsEngine}
            onChange={(value) => setTtsEngine(value || '')}
            data={settingsData.text_to_speech.engines.map(e => ({ value: e, label: e.toUpperCase() }))}
            disabled={disabled}
          />
          <Select
            label="Giọng đọc chính"
            placeholder="Chọn giọng đọc"
            value={voiceId}
            onChange={(value) => setVoiceId(value || '')}
            data={voiceOptions}
            disabled={disabled || !ttsEngine}
          />
        </Stack>

        <Divider />

        {/* Cài đặt Dịch thuật */}
        <Stack spacing="sm">
          <Select
            label="Phương thức dịch"
            placeholder="Chọn phương thức"
            value={translationMethod}
            onChange={(value) => setTranslationMethod(value || '')}
            data={settingsData.translation.methods.map(m => ({ value: m, label: m.charAt(0).toUpperCase() + m.slice(1) }))}
            disabled={disabled}
          />
        </Stack>

        <Divider />

        {/* Cài đặt khác */}
        <Stack spacing="sm">
           <Switch
              label="Nhận dạng nhiều người nói"
              description="Tự động phát hiện và gán giọng đọc khác nhau"
              checked={isMultiSpeaker}
              onChange={(event) => setIsMultiSpeaker(event.currentTarget.checked)}
              disabled={disabled}
            />
        </Stack>

      </Stack>
    </Card>
  );
};

export default Settings;
