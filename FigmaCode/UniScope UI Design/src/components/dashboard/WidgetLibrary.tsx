import { useState } from 'react';
import { ChevronLeft, ChevronRight, Search, Activity, Terminal, FileText, Gauge, Table2, Network, LineChart } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { ScrollArea } from '../ui/scroll-area';
import { Widget } from '../../App';

interface WidgetLibraryProps {
  theme: 'dark' | 'light';
  isCollapsed: boolean;
  setIsCollapsed: (collapsed: boolean) => void;
  onAddWidget: (type: Widget['type']) => void;
}

const widgetTypes = [
  { type: 'oscilloscope' as const, icon: Activity, label: 'Oscilloscope', description: 'Multi-channel waveform viewer' },
  { type: 'terminal' as const, icon: Terminal, label: 'Terminal', description: 'Serial data console' },
  { type: 'hex-viewer' as const, icon: FileText, label: 'Hex Viewer', description: 'Raw data in hexadecimal' },
  { type: 'gauge' as const, icon: Gauge, label: 'Gauge', description: 'Circular meter display' },
  { type: 'data-table' as const, icon: Table2, label: 'Data Table', description: 'Live updating table' },
  { type: 'packet-analyzer' as const, icon: Network, label: 'Packet Analyzer', description: 'Protocol decoder' },
  { type: 'chart' as const, icon: LineChart, label: 'Chart', description: 'Line/Bar chart' },
];

export default function WidgetLibrary({ theme, isCollapsed, setIsCollapsed, onAddWidget }: WidgetLibraryProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [draggedType, setDraggedType] = useState<Widget['type'] | null>(null);

  const filteredWidgets = widgetTypes.filter(w => 
    w.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
    w.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (isCollapsed) {
    return (
      <div className={`w-12 border-r flex flex-col items-center py-4 ${
        theme === 'dark' ? 'bg-[#252525] border-gray-800' : 'bg-gray-50 border-gray-200'
      }`}>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsCollapsed(false)}
          className={theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-gray-200'}
        >
          <ChevronRight className="w-4 h-4" />
        </Button>
      </div>
    );
  }

  return (
    <div className={`w-[280px] border-r flex flex-col ${
      theme === 'dark' ? 'bg-[#252525] border-gray-800' : 'bg-gray-50 border-gray-200'
    }`}>
      <div className="flex items-center justify-between p-4 pb-2">
        <span className="text-sm text-gray-400">Widget Library</span>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsCollapsed(true)}
          className={`h-7 w-7 ${theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-gray-200'}`}
        >
          <ChevronLeft className="w-4 h-4" />
        </Button>
      </div>

      <div className="px-4 pb-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search widgets..."
            className={`pl-10 ${
              theme === 'dark' ? 'bg-[#1A1A1A] border-gray-700' : 'bg-white border-gray-300'
            }`}
          />
        </div>
      </div>

      <ScrollArea className="flex-1 px-4">
        <div className="space-y-2 pb-4">
          {filteredWidgets.map((widget) => {
            const Icon = widget.icon;
            return (
              <div
                key={widget.type}
                draggable
                onDragStart={(e) => {
                  setDraggedType(widget.type);
                  e.dataTransfer.setData('widgetType', widget.type);
                  e.dataTransfer.effectAllowed = 'copy';
                }}
                onDragEnd={() => setDraggedType(null)}
                onClick={() => onAddWidget(widget.type)}
                className={`p-3 rounded-lg border cursor-grab active:cursor-grabbing transition-all ${
                  draggedType === widget.type
                    ? 'opacity-50 scale-95'
                    : theme === 'dark'
                      ? 'bg-[#1A1A1A] border-gray-700 hover:border-[#0A84FF] hover:bg-[#1f1f1f]'
                      : 'bg-white border-gray-300 hover:border-[#0A84FF] hover:bg-gray-50'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className={`p-2 rounded-lg ${
                    theme === 'dark' ? 'bg-[#0A84FF]/10' : 'bg-[#0A84FF]/10'
                  }`}>
                    <Icon className="w-5 h-5 text-[#0A84FF]" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm mb-0.5">{widget.label}</div>
                    <div className="text-xs text-gray-400">{widget.description}</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </ScrollArea>

      <div className={`p-4 border-t ${theme === 'dark' ? 'border-gray-800' : 'border-gray-200'}`}>
        <div className={`p-3 rounded-lg ${theme === 'dark' ? 'bg-[#1A1A1A]' : 'bg-gray-100'}`}>
          <p className="text-xs text-gray-400 mb-1">💡 Tip</p>
          <p className="text-xs text-gray-500">
            Drag widgets onto the canvas or click to add them
          </p>
        </div>
      </div>
    </div>
  );
}
