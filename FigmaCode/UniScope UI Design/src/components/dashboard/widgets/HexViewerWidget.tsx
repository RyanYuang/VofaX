import { useState, useEffect } from 'react';
import { Widget } from '../../../App';
import { ScrollArea } from '../../ui/scroll-area';

interface HexViewerWidgetProps {
  widget: Widget;
  theme: 'dark' | 'light';
  isConnected: boolean;
}

export default function HexViewerWidget({ widget, theme, isConnected }: HexViewerWidgetProps) {
  const [data, setData] = useState<number[]>([]);

  useEffect(() => {
    if (isConnected) {
      const newData = Array.from({ length: 256 }, () => Math.floor(Math.random() * 256));
      setData(newData);
    }
  }, [isConnected]);

  const bytesPerRow = widget.config.bytesPerRow || 16;
  const rows = [];
  for (let i = 0; i < data.length; i += bytesPerRow) {
    rows.push(data.slice(i, i + bytesPerRow));
  }

  return (
    <ScrollArea className="h-full p-3">
      <div
        className={`p-3 rounded ${
          theme === 'dark' ? 'bg-[#1A1A1A]' : 'bg-gray-50'
        }`}
        style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '12px' }}
      >
        {rows.map((row, rowIdx) => (
          <div key={rowIdx} className="flex gap-4 mb-1">
            <span className="text-gray-500 w-16">
              {(rowIdx * bytesPerRow).toString(16).toUpperCase().padStart(4, '0')}:
            </span>
            <span className="text-[#0A84FF]">
              {row.map(byte => byte.toString(16).toUpperCase().padStart(2, '0')).join(' ')}
            </span>
            <span className="text-gray-400">
              {row.map(byte => (byte >= 32 && byte <= 126 ? String.fromCharCode(byte) : '.')).join('')}
            </span>
          </div>
        ))}
      </div>
    </ScrollArea>
  );
}
