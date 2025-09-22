/**
 * About Page Component
 */

import React, { Suspense, lazy } from 'react';
import {
  Container,
  Title,
  Text,
  Card,
  Stack,
  Group,
  Badge,
  List,
  ThemeIcon,
  Divider
} from '@mantine/core';
import {
  IconHeart,
  IconCode,
  IconRocket,
  IconShield,
  IconUsers,
  IconStar
} from '@tabler/icons-react';

// Lazy load components
const Header = lazy(() => import('../components/Header'));

const AboutPage: React.FC = () => {
  const features = [
    {
      icon: IconRocket,
      title: 'Xử lý nhanh chóng',
      description: 'Sử dụng AI tiên tiến để xử lý video một cách nhanh chóng và hiệu quả'
    },
    {
      icon: IconShield,
      title: 'Bảo mật cao',
      description: 'Dữ liệu của bạn được bảo vệ với các tiêu chuẩn bảo mật cao nhất'
    },
    {
      icon: IconUsers,
      title: 'Dễ sử dụng',
      description: 'Giao diện thân thiện, dễ dàng sử dụng cho mọi người'
    },
    {
      icon: IconCode,
      title: 'Mã nguồn mở',
      description: 'Dự án mã nguồn mở, cộng đồng có thể đóng góp và phát triển'
    }
  ];

  const technologies = [
    'React 19',
    'TypeScript',
    'FastAPI',
    'Python',
    'FunASR',
    'EdgeTTS',
    'SQLAlchemy',
    'Mantine UI'
  ];

  return (
    <Container size="lg" py="xl">
      <Suspense fallback={<div>Loading...</div>}>
        <Header />

        <Stack spacing="xl">
          <div style={{ textAlign: 'center' }}>
            <Title order={1} size="h1" mb="md">
              Về Vietnamese AI Dubbing
            </Title>
            <Text size="lg" color="dimmed" mb="xl">
              Công cụ lồng tiếng video AI tự động sang tiếng Việt
            </Text>
          </div>

          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Stack spacing="lg">
              <div>
                <Title order={2} size="h2" mb="md">
                  Giới thiệu
                </Title>
                <Text size="lg" mb="lg">
                  Vietnamese AI Dubbing là một công cụ mạnh mẽ sử dụng trí tuệ nhân tạo
                  để tự động lồng tiếng video sang tiếng Việt. Với công nghệ tiên tiến,
                  chúng tôi giúp bạn dễ dàng tạo ra những video có chất lượng cao với
                  giọng nói tự nhiên và biểu cảm.
                </Text>
                <Text size="lg" mb="lg">
                  Dự án này được phát triển với mục tiêu giúp cộng đồng Việt Nam có
                  thể tiếp cận và sử dụng công nghệ AI một cách dễ dàng và hiệu quả.
                </Text>
              </div>

              <Divider />

              <div>
                <Title order={2} size="h2" mb="md">
                  Tính năng nổi bật
                </Title>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
                  {features.map((feature, index) => (
                    <Card key={index} shadow="sm" padding="md" radius="md" withBorder>
                      <Group mb="sm">
                        <ThemeIcon size="xl" radius="md" color="orange">
                          <feature.icon size={20} />
                        </ThemeIcon>
                        <Text size="lg" weight={500}>
                          {feature.title}
                        </Text>
                      </Group>
                      <Text size="sm" color="dimmed">
                        {feature.description}
                      </Text>
                    </Card>
                  ))}
                </div>
              </div>

              <Divider />

              <div>
                <Title order={2} size="h2" mb="md">
                  Công nghệ sử dụng
                </Title>
                <Group spacing="sm" mb="md">
                  {technologies.map((tech, index) => (
                    <Badge key={index} size="lg" variant="light" color="orange">
                      {tech}
                    </Badge>
                  ))}
                </Group>
                <Text size="sm" color="dimmed">
                  Chúng tôi sử dụng các công nghệ tiên tiến nhất để đảm bảo hiệu suất
                  và chất lượng tốt nhất cho người dùng.
                </Text>
              </div>

              <Divider />

              <div>
                <Title order={2} size="h2" mb="md">
                  Lộ trình phát triển
                </Title>
                <List spacing="sm" size="sm" icon={
                  <ThemeIcon size="sm" radius="xl" color="orange">
                    <IconStar size={12} />
                  </ThemeIcon>
                }>
                  <List.Item>
                    <Text weight={500}>Phase 1:</Text> Thiết lập nền tảng và cấu trúc dự án
                  </List.Item>
                  <List.Item>
                    <Text weight={500}>Phase 2:</Text> Phát triển giao diện người dùng
                  </List.Item>
                  <List.Item>
                    <Text weight={500}>Phase 3:</Text> Tích hợp video download
                  </List.Item>
                  <List.Item>
                    <Text weight={500}>Phase 4:</Text> Voice separation và speech recognition
                  </List.Item>
                  <List.Item>
                    <Text weight={500}>Phase 5:</Text> Translation và text-to-speech
                  </List.Item>
                  <List.Item>
                    <Text weight={500}>Phase 6:</Text> Video synthesis và export
                  </List.Item>
                </List>
              </div>

              <Divider />

              <div>
                <Title order={2} size="h2" mb="md">
                  Đóng góp
                </Title>
                <Text size="lg" mb="lg">
                  Chúng tôi hoan nghênh mọi đóng góp từ cộng đồng! Nếu bạn muốn tham gia
                  phát triển dự án, vui lòng:
                </Text>
                <List spacing="sm" size="sm">
                  <List.Item>Fork dự án trên GitHub</List.Item>
                  <List.Item>Tạo một branch mới cho tính năng của bạn</List.Item>
                  <List.Item>Viết test cho code mới</List.Item>
                  <List.Item>Tạo Pull Request với mô tả chi tiết</List.Item>
                </List>
              </div>

              <Divider />

              <div>
                <Title order={2} size="h2" mb="md">
                  Liên hệ
                </Title>
                <Text size="lg" mb="lg">
                  Nếu bạn có câu hỏi hoặc cần hỗ trợ, hãy liên hệ với chúng tôi:
                </Text>
                <Group spacing="xl">
                  <div>
                    <Text weight={500}>Email:</Text>
                    <Text>contact@vietnamese-ai-dubbing.com</Text>
                  </div>
                  <div>
                    <Text weight={500}>GitHub:</Text>
                    <Text>github.com/vietnamese-ai-dubbing</Text>
                  </div>
                </Group>
              </div>
            </Stack>
          </Card>

          <Card shadow="sm" padding="lg" radius="md" withBorder style={{ backgroundColor: 'var(--mantine-color-orange-light)' }}>
            <div style={{ textAlign: 'center' }}>
              <Title order={3} size="h3" mb="md" color="orange">
                Được phát triển với ❤️ cho cộng đồng Việt Nam
              </Title>
              <Text size="sm" color="orange">
                Vietnamese AI Dubbing - Mang công nghệ AI đến với mọi người
              </Text>
            </div>
          </Card>
        </Stack>
      </Suspense>
    </Container>
  );
};

export default AboutPage;