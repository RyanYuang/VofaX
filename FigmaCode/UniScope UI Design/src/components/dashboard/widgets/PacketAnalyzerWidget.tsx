import { Widget } from '../../../App';
import { ScrollArea } from '../../ui/scroll-area';
import { ChevronRight, CheckCircle2 } from 'lucide-react';

interface PacketAnalyzerWidgetProps {
  widget: Widget;
  theme: 'dark' | 'light';
  isConnected: boolean;
}

const mockPackets = [
  { id: '1', name: 'Frame #1', value: 'AA BB 04 00', crc: true },
  { id: '2', name: 'Frame #2', value: 'CC DD 08 00', crc: true },
  { id: '3', name: 'Frame #3', value: '4F 4B 02 00', crc: true },
];

export default function PacketAnalyzerWidget({ widget, theme, isConnected }: PacketAnalyzerWidgetProps) {
  return (
    <ScrollArea className="h-full p-3">
      <div className="space-y-1">
        {mockPackets.map((packet) => (
          <div
            key={packet.id}
            className={`p-2 rounded flex items-center justify-between ${
              theme === 'dark' ? 'bg-[#1A1A1A] hover:bg-[#1f1f1f]' : 'bg-gray-50 hover:bg-gray-100'
            }`}
          >
            <div className="flex items-center gap-2">
              <ChevronRight className="w-4 h-4 text-gray-400" />
              <span className="text-sm">{packet.name}</span>
              <span 
                className="text-xs text-[#0A84FF]"
                style={{ fontFamily: 'JetBrains Mono, monospace' }}
              >
                {packet.value}
              </span>
            </div>
            {packet.crc && (
              <CheckCircle2 className="w-4 h-4 text-[#30D158]" />
            )}
          </div>
        ))}
      </div>
    </ScrollArea>
  );
}
