import React, { useEffect, useState, Suspense, lazy } from 'react';
import { Container, Title, Text, Button, Group, Card, Stack, Loader, Alert } from '@mantine/core';
import { IconVideo, IconAlertCircle } from '@tabler/icons-react';
import { useAppStore } from '../store/useAppStore';
import { api } from '../api/client';

// Lazy load components
const Header = lazy(() => import('../components/Header'));
const VideoInput = lazy(() => import('../components/VideoInput'));
const Settings = lazy(() => import('../components/Settings'));
const ProgressBar = lazy(() => import('../components/ProgressBar'));
const Result = lazy(() => import('../components/Result'));

import { DubbingStage } from '../types';

const HomePage: React.FC = () => {
  const { isLoading, error, success, setLoading, setError, setSuccess } = useAppStore();

  // Input state
  const [videoUrl, setVideoUrl] = useState<string>('');
  const [videoFile, setVideoFile] = useState<File | null>(null);

  // Settings state
  const [ttsEngine, setTtsEngine] = useState('edgetts');
  const [voiceId, setVoiceId] = useState('vi-VN-HoaiMyNeural');
  const [translationMethod, setTranslationMethod] = useState('google');
  const [isMultiSpeaker, setIsMultiSpeaker] = useState(true);

  // Process state
  const [stage, setStage] = useState<DubbingStage>(DubbingStage.IDLE);
  const [progress, setProgress] = useState<number>(0);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [jobId, setJobId] = useState<string | null>(null);

  // Result state
  const [resultVideoUrl, setResultVideoUrl] = useState<string | null>(null);
  const [resultAudioUrl, setResultAudioUrl] = useState<string | null>(null);

  // Poll for status updates
  useEffect(() => {
    if (isProcessing && jobId) {
      const pollStatus = async () => {
        try {
          const statusResponse = await api.jobs.getJob(jobId);
          const { status, progress: jobProgress, message, output_path } = statusResponse.data;

          setProgress(jobProgress || 0);
          setStage(status as DubbingStage);

          if (status === 'completed') {
            setIsProcessing(false);
            setJobId(null);
            setSuccess('Xử lý video thành công!');
            setResultVideoUrl(output_path); // Giả sử API trả về đường dẫn trực tiếp
          } else if (status === 'failed') {
            setIsProcessing(false);
            setJobId(null);
            setError(message || 'Xử lý video thất bại');
          }
        } catch (err) {
          setIsProcessing(false);
          setJobId(null);
          setError('Lỗi khi kiểm tra trạng thái xử lý.');
          console.error(err);
        }
      };

      const interval = setInterval(pollStatus, 3000); // Poll every 3 seconds
      return () => clearInterval(interval);
    }
  }, [isProcessing, jobId, setError, setSuccess]);


  const handleVideoProcessing = async () => {
    if (!videoUrl && !videoFile) {
      setError('Vui lòng cung cấp link video hoặc tải tệp lên.');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setSuccess(null);
    setResultVideoUrl(null);
    setResultAudioUrl(null);
    setProgress(0);
    setStage(DubbingStage.IDLE);

    try {
      const formData = new FormData();
      if (videoFile) {
        formData.append('video_file', videoFile);
      } else {
        formData.append('video_url', videoUrl);
      }

      const options = {
        tts_engine: ttsEngine,
        voice_id: voiceId,
        translation_method: translationMethod,
        is_multi_speaker: isMultiSpeaker,
      };
      formData.append('options', JSON.stringify(options));

      const response = await api.video.process(formData);
      setJobId(response.data.job_id);
      setStage(DubbingStage.QUEUED);

    } catch (err: any) {
      setIsProcessing(false);
      setError(err.response?.data?.detail || 'Đã xảy ra lỗi khi bắt đầu xử lý');
      setStage(DubbingStage.IDLE);
    }
  };

  const handleReset = () => {
    setVideoUrl('');
    setVideoFile(null);
    setStage(DubbingStage.IDLE);
    setProgress(0);
    setResultVideoUrl(null);
    setResultAudioUrl(null);
    setError(null);
    setSuccess(null);
    setIsProcessing(false);
    setJobId(null);
  };

  return (
    <Container size="xl" py="xl">
      <Suspense fallback={<Loader />}>
        <Header />

        <Stack spacing="xl" mt="lg">
          <div style={{ textAlign: 'center' }}>
            <Title order={1} size="h1" mb="md">
              Vietnamese AI Dubbing
            </Title>
            <Text size="lg" color="dimmed" mb="xl">
              Công cụ lồng tiếng video AI tự động sang tiếng Việt
            </Text>
          </div>

          <Card shadow="sm" padding="lg" radius="md" withBorder>
            {resultVideoUrl ? (
              <Result
                videoUrl={resultVideoUrl}
                audioUrl={resultAudioUrl}
                onReset={handleReset}
              />
            ) : (
              <Stack spacing="lg">
                <VideoInput
                  videoUrl={videoUrl}
                  setVideoUrl={setVideoUrl}
                  setVideoFile={setVideoFile}
                  disabled={isProcessing}
                />

                <Settings
                  ttsEngine={ttsEngine}
                  setTtsEngine={setTtsEngine}
                  voiceId={voiceId}
                  setVoiceId={setVoiceId}
                  translationMethod={translationMethod}
                  setTranslationMethod={setTranslationMethod}
                  isMultiSpeaker={isMultiSpeaker}
                  setIsMultiSpeaker={setIsMultiSpeaker}
                  disabled={isProcessing}
                />

                {error && (
                  <Alert icon={<IconAlertCircle size={16} />} title="Lỗi!" color="red">
                    {error}
                  </Alert>
                )}
                {success && (
                   <Alert color="teal">{success}</Alert>
                )}

                {isProcessing && (
                  <ProgressBar stage={stage} progress={progress} />
                )}

                <Group position="center" mt="md">
                  <Button
                    onClick={handleVideoProcessing}
                    disabled={isProcessing || (!videoUrl && !videoFile)}
                    size="lg"
                    leftIcon={<IconVideo size={20} />}
                    loading={isProcessing}
                  >
                    {isProcessing ? 'Đang xử lý...' : 'Lồng tiếng ngay'}
                  </Button>
                </Group>
              </Stack>
            )}
          </Card>
        </Stack>
      </Suspense>
    </Container>
  );
};

export default HomePage;
