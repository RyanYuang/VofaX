import { useState, useEffect } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import SplashScreen from './components/SplashScreen';
import TopBar from './components/dashboard/TopBar';
import WidgetLibrary from './components/dashboard/WidgetLibrary';
import Canvas from './components/dashboard/Canvas';
import WidgetInspector from './components/dashboard/WidgetInspector';
import ConnectionDialog from './components/dashboard/ConnectionDialog';
import { Toaster } from './components/ui/sonner';

export interface Widget {
  id: string;
  type: 'oscilloscope' | 'terminal' | 'hex-viewer' | 'gauge' | 'data-table' | 'packet-analyzer' | 'chart';
  x: number;
  y: number;
  width: number;
  height: number;
  title: string;
  config: any;
  dataBinding?: {
    channels?: string[];
    field?: string;
  };
}

export default function App() {
  const [showSplash, setShowSplash] = useState(true);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [isConnected, setIsConnected] = useState(false);
  const [selectedPort, setSelectedPort] = useState<string>('');
  const [showConnectionDialog, setShowConnectionDialog] = useState(false);
  const [widgets, setWidgets] = useState<Widget[]>([]);
  const [selectedWidgetId, setSelectedWidgetId] = useState<string | null>(null);
  const [isLibraryCollapsed, setIsLibraryCollapsed] = useState(false);
  const [gridSnap, setGridSnap] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowSplash(false);
    }, 2500);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    document.documentElement.className = theme;
  }, [theme]);

  useEffect(() => {
    // Clear selectedWidgetId if the widget no longer exists
    if (selectedWidgetId && !widgets.find(w => w.id === selectedWidgetId)) {
      setSelectedWidgetId(null);
    }
  }, [widgets, selectedWidgetId]);

  const addWidget = (type: Widget['type'], x: number = 100, y: number = 100) => {
    const defaultConfigs = {
      oscilloscope: { width: 500, height: 350, title: 'Oscilloscope', config: { timeBase: 50, yAxis: 'auto', showGrid: true } },
      terminal: { width: 500, height: 400, title: 'Terminal', config: { displayMode: 'ascii', autoScroll: true } },
      'hex-viewer': { width: 450, height: 350, title: 'Hex Viewer', config: { bytesPerRow: 16 } },
      gauge: { width: 280, height: 280, title: 'Gauge', config: { min: 0, max: 100, unit: '' } },
      'data-table': { width: 600, height: 350, title: 'Data Table', config: { maxRows: 100 } },
      'packet-analyzer': { width: 500, height: 400, title: 'Packet Analyzer', config: { protocol: 'custom' } },
      chart: { width: 500, height: 350, title: 'Chart', config: { chartType: 'line' } },
    };

    const config = defaultConfigs[type];
    const newWidget: Widget = {
      id: `widget-${Date.now()}-${Math.random()}`,
      type,
      x,
      y,
      width: config.width,
      height: config.height,
      title: config.title,
      config: config.config,
      dataBinding: { channels: ['I0'] },
    };

    setWidgets([...widgets, newWidget]);
    setSelectedWidgetId(newWidget.id);
  };

  const updateWidget = (id: string, updates: Partial<Widget>) => {
    setWidgets(widgets.map(w => w.id === id ? { ...w, ...updates } : w));
  };

  const deleteWidget = (id: string) => {
    setWidgets(widgets.filter(w => w.id !== id));
    if (selectedWidgetId === id) {
      setSelectedWidgetId(null);
    }
  };

  const duplicateWidget = (id: string) => {
    const widget = widgets.find(w => w.id === id);
    if (widget) {
      const newWidget = {
        ...widget,
        id: `widget-${Date.now()}-${Math.random()}`,
        x: widget.x + 20,
        y: widget.y + 20,
      };
      setWidgets([...widgets, newWidget]);
    }
  };

  const loadTemplate = (template: 'debug' | 'sensor' | 'protocol') => {
    const templates = {
      debug: [
        { type: 'oscilloscope' as const, x: 50, y: 50, width: 600, height: 350, title: 'Signal Monitor', config: { timeBase: 50, showGrid: true }, dataBinding: { channels: ['I0', 'I1', 'I2'] } },
        { type: 'terminal' as const, x: 670, y: 50, width: 500, height: 350, title: 'Debug Console', config: { displayMode: 'ascii', autoScroll: true }, dataBinding: { channels: ['IO'] } },
        { type: 'data-table' as const, x: 50, y: 420, width: 600, height: 300, title: 'Data Log', config: { maxRows: 100 }, dataBinding: { channels: ['IO'] } },
      ],
      sensor: [
        { type: 'gauge' as const, x: 50, y: 50, width: 280, height: 280, title: 'Temperature', config: { min: 0, max: 100, unit: '°C' }, dataBinding: { channels: ['I0'] } },
        { type: 'gauge' as const, x: 350, y: 50, width: 280, height: 280, title: 'Pressure', config: { min: 0, max: 1000, unit: 'kPa' }, dataBinding: { channels: ['I1'] } },
        { type: 'gauge' as const, x: 650, y: 50, width: 280, height: 280, title: 'Humidity', config: { min: 0, max: 100, unit: '%' }, dataBinding: { channels: ['I2'] } },
        { type: 'chart' as const, x: 50, y: 350, width: 880, height: 350, title: 'Sensor History', config: { chartType: 'line' }, dataBinding: { channels: ['I0', 'I1', 'I2'] } },
      ],
      protocol: [
        { type: 'packet-analyzer' as const, x: 50, y: 50, width: 500, height: 450, title: 'Protocol Parser', config: { protocol: 'custom' }, dataBinding: { channels: ['IO'] } },
        { type: 'hex-viewer' as const, x: 570, y: 50, width: 500, height: 450, title: 'Raw Data', config: { bytesPerRow: 16 }, dataBinding: { channels: ['IO'] } },
        { type: 'terminal' as const, x: 50, y: 520, width: 1020, height: 250, title: 'Debug Output', config: { displayMode: 'hex', autoScroll: true }, dataBinding: { channels: ['IO'] } },
      ],
    };

    const templateWidgets = templates[template].map((w, idx) => ({
      ...w,
      id: `widget-${Date.now()}-${idx}`,
    }));

    setWidgets(templateWidgets);
    setSelectedWidgetId(null);
  };

  if (showSplash) {
    return <SplashScreen />;
  }

  return (
    <DndProvider backend={HTML5Backend}>
      <div className={`h-screen flex flex-col ${theme === 'dark' ? 'bg-[#1A1A1A] text-white' : 'bg-white text-gray-900'}`}>
        <TopBar 
          theme={theme} 
          setTheme={setTheme}
          isConnected={isConnected}
          selectedPort={selectedPort}
          onConnect={() => setShowConnectionDialog(true)}
          gridSnap={gridSnap}
          setGridSnap={setGridSnap}
          onLoadTemplate={loadTemplate}
          widgets={widgets}
        />
        
        <div className="flex-1 flex overflow-hidden">
          <WidgetLibrary 
            theme={theme}
            isCollapsed={isLibraryCollapsed}
            setIsCollapsed={setIsLibraryCollapsed}
            onAddWidget={addWidget}
          />
          
          <Canvas 
            theme={theme}
            widgets={widgets}
            setWidgets={setWidgets}
            selectedWidgetId={selectedWidgetId}
            setSelectedWidgetId={setSelectedWidgetId}
            onAddWidget={addWidget}
            onDeleteWidget={deleteWidget}
            onDuplicateWidget={duplicateWidget}
            gridSnap={gridSnap}
            isConnected={isConnected}
          />

          {selectedWidgetId && widgets.find(w => w.id === selectedWidgetId) && (
            <WidgetInspector
              theme={theme}
              widget={widgets.find(w => w.id === selectedWidgetId)!}
              onUpdate={(updates) => updateWidget(selectedWidgetId, updates)}
              onDelete={() => deleteWidget(selectedWidgetId)}
              onDuplicate={() => duplicateWidget(selectedWidgetId)}
            />
          )}
        </div>

        {showConnectionDialog && (
          <ConnectionDialog
            theme={theme}
            onClose={() => setShowConnectionDialog(false)}
            onConnect={(port) => {
              setIsConnected(true);
              setSelectedPort(port);
              setShowConnectionDialog(false);
            }}
          />
        )}

        <Toaster theme={theme} />
      </div>
    </DndProvider>
  );
}
