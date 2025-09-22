/**
 * Tab Selector Component
 */

import React from 'react';
import { Tabs, Tab } from '@mantine/core';
import {
  IconVideo,
  IconDownload,
  IconMicrophone,
  IconLanguage,
  IconSettings
} from '@tabler/icons-react';

interface TabSelectorProps {
  activeTab: 'dubbing' | 'downloader' | 'separator' | 'recognition' | 'translation' | 'synthesizer';
  setActiveTab: (tab: 'dubbing' | 'downloader' | 'separator' | 'recognition' | 'translation' | 'synthesizer') => void;
}

const TabSelector: React.FC<TabSelectorProps> = ({ activeTab, setActiveTab }) => {
  const tabs = [
    {
      value: 'dubbing',
      label: 'Lồng tiếng',
      icon: IconVideo,
      description: 'Xử lý video và lồng tiếng AI'
    },
    {
      value: 'downloader',
      label: 'Tải video',
      icon: IconDownload,
      description: 'Tải video từ các nền tảng'
    },
    {
      value: 'separator',
      label: 'Tách giọng',
      icon: IconMicrophone,
      description: 'Tách giọng nói và âm nhạc'
    },
    {
      value: 'recognition',
      label: 'Nhận diện',
      icon: IconMicrophone,
      description: 'Nhận diện giọng nói và chuyển văn bản'
    },
    {
      value: 'translation',
      label: 'Dịch',
      icon: IconLanguage,
      description: 'Dịch phụ đề sang tiếng Việt'
    },
    {
      value: 'synthesizer',
      label: 'Tổng hợp',
      icon: IconSettings,
      description: 'Tổng hợp video với giọng mới'
    }
  ];

  return (
    <Tabs value={activeTab} onChange={(value) => setActiveTab(value as any)}>
      <Tabs.List grow>
        {tabs.map((tab) => (
          <Tab
            key={tab.value}
            value={tab.value}
            icon={<tab.icon size={16} />}
          >
            <div className="text-center">
              <div className="font-medium">{tab.label}</div>
              <div className="text-xs text-gray-500 hidden sm:block">
                {tab.description}
              </div>
            </div>
          </Tab>
        ))}
      </Tabs.List>
    </Tabs>
  );
};

export default TabSelector;