import { useRef } from 'react';
import { useDrop } from 'react-dnd';
import { Plus } from 'lucide-react';
import { Widget } from '../../App';
import WidgetContainer from './WidgetContainer';
import { Button } from '../ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';

interface CanvasProps {
  theme: 'dark' | 'light';
  widgets: Widget[];
  setWidgets: (widgets: Widget[]) => void;
  selectedWidgetId: string | null;
  setSelectedWidgetId: (id: string | null) => void;
  onAddWidget: (type: Widget['type'], x?: number, y?: number) => void;
  onDeleteWidget: (id: string) => void;
  onDuplicateWidget: (id: string) => void;
  gridSnap: boolean;
  isConnected: boolean;
}

export default function Canvas({
  theme,
  widgets,
  setWidgets,
  selectedWidgetId,
  setSelectedWidgetId,
  onAddWidget,
  onDeleteWidget,
  onDuplicateWidget,
  gridSnap,
  isConnected
}: CanvasProps) {
  const canvasRef = useRef<HTMLDivElement>(null);

  const [{ isOver }, drop] = useDrop(() => ({
    accept: 'widget',
    drop: (item: any, monitor) => {
      const offset = monitor.getClientOffset();
      if (offset && canvasRef.current) {
        const canvasRect = canvasRef.current.getBoundingClientRect();
        const x = offset.x - canvasRect.left;
        const y = offset.y - canvasRect.top;
        
        if (item.widgetType) {
          // New widget from library
          onAddWidget(item.widgetType, x, y);
        }
      }
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
    }),
  }), [onAddWidget]);

  const handleCanvasClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      setSelectedWidgetId(null);
    }
  };

  return (
    <div
      ref={(node) => {
        canvasRef.current = node;
        drop(node);
      }}
      onClick={handleCanvasClick}
      className={`flex-1 relative overflow-auto ${
        theme === 'dark' ? 'bg-[#1A1A1A]' : 'bg-gray-50'
      }`}
      style={{
        backgroundImage: gridSnap
          ? theme === 'dark'
            ? 'radial-gradient(circle, #2A2A2A 1px, transparent 1px)'
            : 'radial-gradient(circle, #D1D5DB 1px, transparent 1px)'
          : 'none',
        backgroundSize: '20px 20px',
      }}
    >
      {widgets.length === 0 ? (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className={`mb-6 inline-flex p-6 rounded-2xl ${
              theme === 'dark' ? 'bg-[#252525]' : 'bg-white'
            }`}>
              <div className="relative">
                <div className="absolute inset-0 bg-[#0A84FF] blur-2xl opacity-20 animate-pulse"></div>
                <Plus className="w-16 h-16 text-[#0A84FF] relative" />
              </div>
            </div>
            <h3 className="text-xl mb-2">Drag a widget to start</h3>
            <p className="text-gray-400 mb-6">
              Or click the button below to add your first widget
            </p>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button className="bg-[#0A84FF] hover:bg-[#0066CC] text-white">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Widget
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className={theme === 'dark' ? 'bg-[#252525] border-gray-700' : 'bg-white'}>
                <DropdownMenuItem onClick={() => onAddWidget('oscilloscope')}>Oscilloscope</DropdownMenuItem>
                <DropdownMenuItem onClick={() => onAddWidget('terminal')}>Terminal</DropdownMenuItem>
                <DropdownMenuItem onClick={() => onAddWidget('hex-viewer')}>Hex Viewer</DropdownMenuItem>
                <DropdownMenuItem onClick={() => onAddWidget('gauge')}>Gauge</DropdownMenuItem>
                <DropdownMenuItem onClick={() => onAddWidget('data-table')}>Data Table</DropdownMenuItem>
                <DropdownMenuItem onClick={() => onAddWidget('packet-analyzer')}>Packet Analyzer</DropdownMenuItem>
                <DropdownMenuItem onClick={() => onAddWidget('chart')}>Chart</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      ) : (
        <>
          {widgets.map((widget) => (
            <WidgetContainer
              key={widget.id}
              widget={widget}
              theme={theme}
              isSelected={selectedWidgetId === widget.id}
              onSelect={() => setSelectedWidgetId(widget.id)}
              onUpdate={(updates) => {
                setWidgets(widgets.map(w => w.id === widget.id ? { ...w, ...updates } : w));
              }}
              onDelete={() => onDeleteWidget(widget.id)}
              onDuplicate={() => onDuplicateWidget(widget.id)}
              gridSnap={gridSnap}
              isConnected={isConnected}
            />
          ))}
        </>
      )}

      {isOver && (
        <div className="absolute inset-0 border-4 border-dashed border-[#0A84FF] bg-[#0A84FF]/5 pointer-events-none rounded-lg" />
      )}
    </div>
  );
}
