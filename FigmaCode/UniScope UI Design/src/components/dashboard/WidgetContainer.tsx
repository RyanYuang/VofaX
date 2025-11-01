import { useRef, useState } from 'react';
import { useDrag } from 'react-dnd';
import { Resizable } from 're-resizable';
import { GripVertical, Copy, Trash2, MoreVertical } from 'lucide-react';
import { Widget } from '../../App';
import OscilloscopeWidget from './widgets/OscilloscopeWidget';
import TerminalWidget from './widgets/TerminalWidget';
import HexViewerWidget from './widgets/HexViewerWidget';
import GaugeWidget from './widgets/GaugeWidget';
import DataTableWidget from './widgets/DataTableWidget';
import PacketAnalyzerWidget from './widgets/PacketAnalyzerWidget';
import ChartWidget from './widgets/ChartWidget';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';

interface WidgetContainerProps {
  widget: Widget;
  theme: 'dark' | 'light';
  isSelected: boolean;
  onSelect: () => void;
  onUpdate: (updates: Partial<Widget>) => void;
  onDelete: () => void;
  onDuplicate: () => void;
  gridSnap: boolean;
  isConnected: boolean;
}

export default function WidgetContainer({
  widget,
  theme,
  isSelected,
  onSelect,
  onUpdate,
  onDelete,
  onDuplicate,
  gridSnap,
  isConnected
}: WidgetContainerProps) {
  const dragRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const [{ opacity }, drag] = useDrag(() => ({
    type: 'widget',
    item: () => {
      setIsDragging(true);
      return { id: widget.id, x: widget.x, y: widget.y };
    },
    end: (item, monitor) => {
      setIsDragging(false);
      const offset = monitor.getClientOffset();
      if (offset && dragRef.current) {
        const parent = dragRef.current.parentElement;
        if (parent) {
          const parentRect = parent.getBoundingClientRect();
          let newX = offset.x - parentRect.left;
          let newY = offset.y - parentRect.top;

          if (gridSnap) {
            newX = Math.round(newX / 20) * 20;
            newY = Math.round(newY / 20) * 20;
          }

          onUpdate({ x: newX, y: newY });
        }
      }
    },
    collect: (monitor) => ({
      opacity: monitor.isDragging() ? 0.5 : 1,
    }),
  }), [widget, gridSnap]);

  drag(dragRef);

  const renderWidget = () => {
    switch (widget.type) {
      case 'oscilloscope':
        return <OscilloscopeWidget widget={widget} theme={theme} isConnected={isConnected} />;
      case 'terminal':
        return <TerminalWidget widget={widget} theme={theme} isConnected={isConnected} />;
      case 'hex-viewer':
        return <HexViewerWidget widget={widget} theme={theme} isConnected={isConnected} />;
      case 'gauge':
        return <GaugeWidget widget={widget} theme={theme} isConnected={isConnected} />;
      case 'data-table':
        return <DataTableWidget widget={widget} theme={theme} isConnected={isConnected} />;
      case 'packet-analyzer':
        return <PacketAnalyzerWidget widget={widget} theme={theme} isConnected={isConnected} />;
      case 'chart':
        return <ChartWidget widget={widget} theme={theme} isConnected={isConnected} />;
      default:
        return null;
    }
  };

  return (
    <Resizable
      size={{ width: widget.width, height: widget.height }}
      onResizeStop={(e, direction, ref, d) => {
        let newWidth = widget.width + d.width;
        let newHeight = widget.height + d.height;

        if (gridSnap) {
          newWidth = Math.round(newWidth / 20) * 20;
          newHeight = Math.round(newHeight / 20) * 20;
        }

        onUpdate({
          width: newWidth,
          height: newHeight,
        });
      }}
      style={{
        position: 'absolute',
        left: widget.x,
        top: widget.y,
        opacity,
        zIndex: isSelected ? 10 : 1,
      }}
      minWidth={200}
      minHeight={150}
      enable={{
        top: false,
        right: true,
        bottom: true,
        left: false,
        topRight: false,
        bottomRight: true,
        bottomLeft: false,
        topLeft: false,
      }}
    >
      <div
        ref={dragRef}
        onClick={onSelect}
        className={`h-full rounded-lg overflow-hidden transition-all ${
          theme === 'dark' ? 'bg-[#252525]' : 'bg-white'
        } ${
          isSelected
            ? 'ring-2 ring-[#0A84FF] shadow-lg shadow-[#0A84FF]/20'
            : theme === 'dark'
              ? 'border border-gray-800 hover:border-gray-700'
              : 'border border-gray-200 hover:border-gray-300'
        }`}
      >
        <div
          className={`h-10 flex items-center justify-between px-3 border-b cursor-grab active:cursor-grabbing ${
            theme === 'dark' ? 'bg-[#2A2A2A] border-gray-800' : 'bg-gray-50 border-gray-200'
          }`}
        >
          <div className="flex items-center gap-2">
            <GripVertical className="w-4 h-4 text-gray-500" />
            <span className="text-sm">{widget.title}</span>
          </div>
          <div className="flex items-center gap-1">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className={`p-1 rounded hover:bg-gray-700 transition-colors`}>
                  <MoreVertical className="w-4 h-4 text-gray-400" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className={theme === 'dark' ? 'bg-[#252525] border-gray-700' : 'bg-white'}>
                <DropdownMenuItem onClick={onDuplicate}>
                  <Copy className="w-4 h-4 mr-2" />
                  Duplicate
                </DropdownMenuItem>
                <DropdownMenuItem onClick={onDelete} className="text-[#FF453A]">
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
        <div className="h-[calc(100%-40px)] overflow-hidden">
          {renderWidget()}
        </div>
      </div>
    </Resizable>
  );
}
