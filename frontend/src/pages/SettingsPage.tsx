/**
 * Settings Page Component
 */

import React, { Suspense, lazy } from 'react';
import {
  Container,
  Title,
  Text,
  Card,
  Stack,
  Switch,
  Select,
  Button,
  Group,
  TextInput,
  NumberInput,
  Divider,
  Alert
} from '@mantine/core';
import { IconSettings, IconBell, IconShield, IconPalette, IconApi } from '@tabler/icons-react';
import { useAppStore } from '../store/useAppStore';

// Lazy load components
const Header = lazy(() => import('../components/Header'));

const SettingsPage: React.FC = () => {
  const { setSuccess, setError } = useAppStore();

  const handleSaveSettings = () => {
    try {
      // Save settings logic here
      setSuccess('Cài đặt đã được lưu thành công');
    } catch (error: any) {
      setError('Lỗi khi lưu cài đặt: ' + error.message);
    }
  };

  return (
    <Container size="lg" py="xl">
      <Suspense fallback={<div>Loading...</div>}>
        <Header />

        <Stack spacing="xl">
          <div style={{ textAlign: 'center' }}>
            <Title order={1} size="h1" mb="md">
              Cài đặt
            </Title>
            <Text size="lg" color="dimmed" mb="xl">
              Tùy chỉnh ứng dụng theo sở thích của bạn
            </Text>
          </div>

          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Stack spacing="lg">
              <div>
                <Group position="apart" mb="xs">
                  <Text size="lg" weight={500}>Giao diện</Text>
                  <IconPalette size={20} />
                </Group>
                <Divider mb="md" />
                <Switch
                  label="Chế độ tối"
                  description="Bật chế độ tối cho giao diện"
                  defaultChecked
                />
              </div>

              <Divider />

              <div>
                <Group position="apart" mb="xs">
                  <Text size="lg" weight={500}>Thông báo</Text>
                  <IconBell size={20} />
                </Group>
                <Divider mb="md" />
                <Switch
                  label="Thông báo hoàn thành"
                  description="Nhận thông báo khi job xử lý xong"
                  defaultChecked
                />
                <Switch
                  label="Thông báo lỗi"
                  description="Nhận thông báo khi có lỗi xảy ra"
                  defaultChecked
                />
              </div>

              <Divider />

              <div>
                <Group position="apart" mb="xs">
                  <Text size="lg" weight={500}>Xử lý Video</Text>
                  <IconSettings size={20} />
                </Group>
                <Divider mb="md" />
                <Select
                  label="Chất lượng mặc định"
                  description="Chất lượng video đầu ra mặc định"
                  data={[
                    { value: '720p', label: '720p (HD)' },
                    { value: '1080p', label: '1080p (Full HD)' },
                    { value: '4k', label: '4K (Ultra HD)' },
                  ]}
                  defaultValue="720p"
                />
                <NumberInput
                  label="Tốc độ xử lý"
                  description="Số luồng xử lý song song"
                  defaultValue={2}
                  min={1}
                  max={8}
                  mt="md"
                />
              </div>

              <Divider />

              <div>
                <Group position="apart" mb="xs">
                  <Text size="lg" weight={500}>API Keys</Text>
                  <IconApi size={20} />
                </Group>
                <Divider mb="md" />
                <Alert color="blue" mb="md">
                  Các API key sẽ được mã hóa và lưu trữ an toàn
                </Alert>
                <TextInput
                  label="OpenRouter API Key"
                  description="API key cho dịch vụ OpenRouter"
                  placeholder="sk-..."
                  type="password"
                />
                <TextInput
                  label="Google Translate API Key"
                  description="API key cho Google Translate"
                  placeholder="AIza..."
                  type="password"
                  mt="md"
                />
              </div>

              <Divider />

              <div>
                <Group position="apart" mb="xs">
                  <Text size="lg" weight={500}>Bảo mật</Text>
                  <IconShield size={20} />
                </Group>
                <Divider mb="md" />
                <Switch
                  label="Xác thực hai yếu tố"
                  description="Bật xác thực hai yếu tố để bảo mật tài khoản"
                />
                <Switch
                  label="Tự động đăng xuất"
                  description="Tự động đăng xuất sau 30 phút không hoạt động"
                  defaultChecked
                />
              </div>

              <Group position="right" mt="xl">
                <Button variant="outline">
                  Hủy
                </Button>
                <Button onClick={handleSaveSettings}>
                  Lưu cài đặt
                </Button>
              </Group>
            </Stack>
          </Card>
        </Stack>
      </Suspense>
    </Container>
  );
};

export default SettingsPage;