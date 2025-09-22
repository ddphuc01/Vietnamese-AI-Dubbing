/**
 * Video Preview Component
 */

import React, { useRef, useEffect } from 'react';
import { Card, Text, Group, Button, Stack } from '@mantine/core';
import { IconPlayerPlay, IconPlayerPause, IconVolume, IconVolumeOff } from '@tabler/icons-react';

interface VideoPreviewProps {
  previewUrl: string;
  onPlay?: () => void;
  onPause?: () => void;
  onVolumeChange?: (muted: boolean) => void;
}

const VideoPreview: React.FC<VideoPreviewProps> = ({
  previewUrl,
  onPlay,
  onPause,
  onVolumeChange
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = React.useState(false);
  const [isMuted, setIsMuted] = React.useState(false);
  const [duration, setDuration] = React.useState(0);
  const [currentTime, setCurrentTime] = React.useState(0);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleLoadedMetadata = () => {
      setDuration(video.duration);
    };

    const handleTimeUpdate = () => {
      setCurrentTime(video.currentTime);
    };

    const handlePlay = () => {
      setIsPlaying(true);
      onPlay?.();
    };

    const handlePause = () => {
      setIsPlaying(false);
      onPause?.();
    };

    video.addEventListener('loadedmetadata', handleLoadedMetadata);
    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('play', handlePlay);
    video.addEventListener('pause', handlePause);

    return () => {
      video.removeEventListener('loadedmetadata', handleLoadedMetadata);
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('play', handlePlay);
      video.removeEventListener('pause', handlePause);
    };
  }, [onPlay, onPause]);

  const togglePlay = () => {
    const video = videoRef.current;
    if (!video) return;

    if (isPlaying) {
      video.pause();
    } else {
      video.play();
    }
  };

  const toggleMute = () => {
    const video = videoRef.current;
    if (!video) return;

    const newMuted = !isMuted;
    setIsMuted(newMuted);
    video.muted = newMuted;
    onVolumeChange?.(newMuted);
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    const video = videoRef.current;
    if (!video) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const progressWidth = rect.width;
    const newTime = (clickX / progressWidth) * duration;

    video.currentTime = newTime;
  };

  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Stack spacing="md">
        <div>
          <Text size="lg" weight={500} mb="xs">
            Xem trước video
          </Text>
          <Text size="sm" color="dimmed">
            Xem trước video trước khi xử lý
          </Text>
        </div>

        <div style={{ position: 'relative' }}>
          <video
            ref={videoRef}
            src={previewUrl}
            style={{
              width: '100%',
              borderRadius: '8px',
              background: '#000'
            }}
            controls={false}
            preload="metadata"
          />

          {/* Custom Controls */}
          <div
            style={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              background: 'linear-gradient(transparent, rgba(0,0,0,0.7))',
              padding: '1rem',
              borderRadius: '0 0 8px 8px'
            }}
          >
            <Group position="apart" mb="xs">
              <Group spacing="sm">
                <Button
                  size="sm"
                  variant="white"
                  onClick={togglePlay}
                  style={{ minWidth: 'auto', padding: '0.5rem' }}
                >
                  {isPlaying ? (
                    <IconPlayerPause size={16} />
                  ) : (
                    <IconPlayerPlay size={16} />
                  )}
                </Button>

                <Button
                  size="sm"
                  variant="white"
                  onClick={toggleMute}
                  style={{ minWidth: 'auto', padding: '0.5rem' }}
                >
                  {isMuted ? (
                    <IconVolumeOff size={16} />
                  ) : (
                    <IconVolume size={16} />
                  )}
                </Button>
              </Group>

              <Text size="xs" color="white">
                {formatTime(currentTime)} / {formatTime(duration)}
              </Text>
            </Group>

            {/* Progress Bar */}
            <div
              style={{
                height: '4px',
                background: 'rgba(255,255,255,0.3)',
                borderRadius: '2px',
                cursor: 'pointer',
                position: 'relative'
              }}
              onClick={handleSeek}
            >
              <div
                style={{
                  height: '100%',
                  background: 'white',
                  borderRadius: '2px',
                  width: `${(currentTime / duration) * 100}%`,
                  transition: 'width 0.1s ease'
                }}
              />
            </div>
          </div>
        </div>

        <Group position="apart">
          <Text size="sm" color="dimmed">
            Độ dài: {formatTime(duration)}
          </Text>
          <Button variant="light" size="sm">
            Thay đổi video
          </Button>
        </Group>
      </Stack>
    </Card>
  );
};

export default VideoPreview;