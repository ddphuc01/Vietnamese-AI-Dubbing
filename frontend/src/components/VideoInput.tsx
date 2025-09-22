/**
 * Video Input Component
 */

import React, { useRef, useState } from 'react';
import {
  Card,
  Text,
  Button,
  Group,
  Stack,
  TextInput,
  FileInput,
  Alert,
  Progress
} from '@mantine/core';
import {
  IconUpload,
  IconLink,
  IconVideo,
  IconX,
  IconCheck
} from '@tabler/icons-react';

interface VideoInputProps {
  videoUrl: string;
  setVideoUrl: (url: string) => void;
  setVideoFile: (file: File | null) => void;
  disabled?: boolean;
}

const VideoInput: React.FC<VideoInputProps> = ({
  videoUrl,
  setVideoUrl,
  setVideoFile,
  disabled = false
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (disabled) return;

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileUpload = async (file: File) => {
    if (disabled) return;

    // Validate file type
    const allowedTypes = ['video/mp4', 'video/webm', 'video/ogg', 'video/avi', 'video/mov'];
    if (!allowedTypes.includes(file.type)) {
      alert('Định dạng file không được hỗ trợ. Vui lòng chọn file video (MP4, WebM, OGG, AVI, MOV).');
      return;
    }

    // Validate file size (max 500MB)
    const maxSize = 500 * 1024 * 1024;
    if (file.size > maxSize) {
      alert('File quá lớn. Kích thước tối đa là 500MB.');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    // Simulate upload progress
    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsUploading(false);
          setVideoFile(file);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleUrlSubmit = () => {
    if (videoUrl.trim()) {
      setVideoFile(null);
      // Here you could validate the URL
    }
  };

  const clearInput = () => {
    setVideoUrl('');
    setVideoFile(null);
    setUploadProgress(0);
    setIsUploading(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Stack spacing="md">
        <div>
          <Text size="lg" weight={500} mb="xs">
            Nguồn video
          </Text>
          <Text size="sm" color="dimmed">
            Chọn video từ máy tính hoặc nhập URL
          </Text>
        </div>

        {/* URL Input */}
        <TextInput
          placeholder="Nhập URL video (YouTube, Vimeo, ...)"
          value={videoUrl}
          onChange={(e) => setVideoUrl(e.target.value)}
          disabled={disabled || isUploading}
          rightSection={
            videoUrl && !isUploading ? (
              <Group spacing="xs">
                <Button
                  size="xs"
                  variant="light"
                  onClick={handleUrlSubmit}
                  disabled={disabled}
                >
                  <IconCheck size={14} />
                </Button>
                <Button
                  size="xs"
                  variant="light"
                  color="red"
                  onClick={clearInput}
                >
                  <IconX size={14} />
                </Button>
              </Group>
            ) : null
          }
        />

        <Text size="sm" color="dimmed" style={{ textAlign: 'center' }}>
          hoặc
        </Text>

        {/* File Upload Area */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          style={{
            border: '2px dashed',
            borderColor: dragActive ? 'var(--mantine-color-orange-5)' : 'var(--mantine-color-gray-3)',
            borderRadius: 'var(--mantine-radius-md)',
            padding: '2rem',
            textAlign: 'center',
            backgroundColor: dragActive ? 'var(--mantine-color-orange-0)' : 'transparent',
            cursor: disabled ? 'not-allowed' : 'pointer',
            opacity: disabled ? 0.6 : 1,
          }}
          onClick={() => !disabled && !isUploading && fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="video/*"
            onChange={handleFileInputChange}
            style={{ display: 'none' }}
            disabled={disabled || isUploading}
          />

          {isUploading ? (
            <Stack spacing="sm" align="center">
              <IconUpload size={32} color="var(--mantine-color-orange-5)" />
              <Text size="sm" weight={500}>
                Đang tải lên...
              </Text>
              <Progress value={uploadProgress} w={200} />
              <Text size="xs" color="dimmed">
                {uploadProgress}%
              </Text>
            </Stack>
          ) : (
            <Stack spacing="sm" align="center">
              <IconVideo size={32} color="var(--mantine-color-gray-5)" />
              <Text size="sm" weight={500}>
                Kéo thả video vào đây
              </Text>
              <Text size="xs" color="dimmed">
                hoặc nhấp để chọn file
              </Text>
              <Button
                variant="light"
                size="sm"
                leftIcon={<IconUpload size={14} />}
                disabled={disabled}
              >
                Chọn video
              </Button>
            </Stack>
          )}
        </div>

        {/* Supported formats info */}
        <Alert color="blue" icon={<IconLink size={16} />}>
          <Text size="xs">
            Hỗ trợ: MP4, WebM, OGG, AVI, MOV. Kích thước tối đa: 500MB
          </Text>
        </Alert>
      </Stack>
    </Card>
  );
};

export default VideoInput;