/**
 * Header Component
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Header as MantineHeader,
  Container,
  Group,
  Button,
  Text,
  Menu,
  ActionIcon,
  useMantineColorScheme,
  Switch,
  Avatar,
  UnstyledButton
} from '@mantine/core';
import {
  IconHome,
  IconVideo,
  IconList,
  IconSettings,
  IconInfoCircle,
  IconSun,
  IconMoon,
  IconLogout,
  IconUser
} from '@tabler/icons-react';

const Header: React.FC = () => {
  const location = useLocation();
  const { colorScheme, toggleColorScheme } = useMantineColorScheme();

  const navigation = [
    { name: 'Trang chủ', href: '/home', icon: IconHome },
    { name: 'Xử lý Video', href: '/video-processing', icon: IconVideo },
    { name: 'Jobs', href: '/jobs', icon: IconList },
    { name: 'Cài đặt', href: '/settings', icon: IconSettings },
    { name: 'Giới thiệu', href: '/about', icon: IconInfoCircle },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <MantineHeader height={70} px="md">
      <Container size="xl" h="100%">
        <Group position="apart" h="100%">
          {/* Logo */}
          <Group spacing="xs">
            <Avatar size="md" color="orange" radius="md">
              <IconVideo size={20} />
            </Avatar>
            <div>
              <Text size="lg" weight={700} color="orange">
                Vietnamese AI Dubbing
              </Text>
            </div>
          </Group>

          {/* Navigation */}
          <Group spacing="sm" className="hidden md:flex">
            {navigation.map((item) => (
              <Button
                key={item.name}
                component={Link}
                to={item.href}
                variant={isActive(item.href) ? 'filled' : 'subtle'}
                leftIcon={<item.icon size={16} />}
                size="sm"
              >
                {item.name}
              </Button>
            ))}
          </Group>

          {/* Right side */}
          <Group spacing="sm">
            {/* Theme toggle */}
            <ActionIcon
              variant="outline"
              color="orange"
              onClick={() => toggleColorScheme()}
              title="Toggle color scheme"
            >
              {colorScheme === 'dark' ? <IconSun size={16} /> : <IconMoon size={16} />}
            </ActionIcon>

            {/* User menu */}
            <Menu shadow="md" width={200}>
              <Menu.Target>
                <UnstyledButton>
                  <Group spacing="xs">
                    <Avatar size="sm" color="orange" radius="xl">
                      <IconUser size={14} />
                    </Avatar>
                    <Text size="sm" weight={500}>
                      User
                    </Text>
                  </Group>
                </UnstyledButton>
              </Menu.Target>
              <Menu.Dropdown>
                <Menu.Item icon={<IconUser size={14} />}>
                  Hồ sơ
                </Menu.Item>
                <Menu.Item icon={<IconSettings size={14} />}>
                  Cài đặt
                </Menu.Item>
                <Menu.Divider />
                <Menu.Item icon={<IconLogout size={14} />} color="red">
                  Đăng xuất
                </Menu.Item>
              </Menu.Dropdown>
            </Menu>

            {/* Mobile menu button */}
            <Menu shadow="md" width={200} className="md:hidden">
              <Menu.Target>
                <ActionIcon variant="outline" size="lg">
                  <IconSettings size={16} />
                </ActionIcon>
              </Menu.Target>
              <Menu.Dropdown>
                {navigation.map((item) => (
                  <Menu.Item
                    key={item.name}
                    component={Link}
                    to={item.href}
                    icon={<item.icon size={14} />}
                  >
                    {item.name}
                  </Menu.Item>
                ))}
              </Menu.Dropdown>
            </Menu>
          </Group>
        </Group>
      </Container>
    </MantineHeader>
  );
};

export default Header;