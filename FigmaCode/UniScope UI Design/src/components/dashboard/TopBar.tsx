import { Radar, Moon, Sun, Save, FolderOpen, Download, Grid3x3, Wifi, WifiOff } from 'lucide-react';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '../ui/dropdown-menu';
import { toast } from 'sonner@2.0.3';
import { Widget } from '../../App';

interface TopBarProps {
  theme: 'dark' | 'light';
  setTheme: (theme: 'dark' | 'light') => void;
  isConnected: boolean;
  selectedPort: string;
  onConnect: () => void;
  gridSnap: boolean;
  setGridSnap: (snap: boolean) => void;
  onLoadTemplate: (template: 'debug' | 'sensor' | 'protocol') => void;
  widgets: Widget[];
}

export default function TopBar({ 
  theme, 
  setTheme, 
  isConnected, 
  selectedPort,
  onConnect,
  gridSnap,
  setGridSnap,
  onLoadTemplate,
  widgets
}: TopBarProps) {
  
  const handleSaveLayout = () => {
    const layout = JSON.stringify(widgets, null, 2);
    const blob = new Blob([layout], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `uniscope-layout-${Date.now()}.json`;
    a.click();
    toast.success('Layout saved');
  };

  const handleExportData = () => {
    toast.success('Data exported');
  };

  return (
    <div className={`h-14 border-b flex items-center justify-between px-4 ${
      theme === 'dark' ? 'bg-[#252525] border-gray-800' : 'bg-gray-50 border-gray-200'
    }`}>
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-gradient-to-br from-[#0A84FF] to-[#0066CC]">
          <Radar className="w-5 h-5 text-white" />
        </div>
        <span className="tracking-tight" style={{ fontFamily: 'Inter, sans-serif' }}>
          UniScope
        </span>
        
        <Badge 
          variant={isConnected ? "default" : "secondary"}
          className={`ml-4 cursor-pointer ${
            isConnected 
              ? 'bg-[#30D158] hover:bg-[#30D158] text-white' 
              : theme === 'dark' 
                ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
          onClick={onConnect}
        >
          <div className={`w-2 h-2 rounded-full mr-2 ${isConnected ? 'bg-white animate-pulse' : 'bg-gray-400'}`}></div>
          {isConnected ? `${selectedPort} @ 115200` : 'Not Connected'}
        </Badge>
      </div>

      <div className="flex items-center gap-2">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button 
              variant="outline" 
              size="sm"
              className={theme === 'dark' ? 'border-gray-700 hover:bg-gray-700' : 'border-gray-300'}
            >
              <FolderOpen className="w-4 h-4 mr-2" />
              Templates
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className={theme === 'dark' ? 'bg-[#252525] border-gray-700' : 'bg-white'}>
            <DropdownMenuItem onClick={() => onLoadTemplate('debug')}>
              Debug Mode
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onLoadTemplate('sensor')}>
              Sensor Monitor
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onLoadTemplate('protocol')}>
              Protocol Test
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <Button 
          variant="outline" 
          size="sm"
          onClick={handleSaveLayout}
          className={theme === 'dark' ? 'border-gray-700 hover:bg-gray-700' : 'border-gray-300'}
        >
          <Save className="w-4 h-4 mr-2" />
          Save Layout
        </Button>

        <Button 
          variant="outline" 
          size="sm"
          onClick={handleExportData}
          className={theme === 'dark' ? 'border-gray-700 hover:bg-gray-700' : 'border-gray-300'}
        >
          <Download className="w-4 h-4 mr-2" />
          Export Data
        </Button>

        <div className="w-px h-6 bg-gray-600 mx-1"></div>

        <Button
          variant={gridSnap ? "default" : "outline"}
          size="sm"
          onClick={() => setGridSnap(!gridSnap)}
          className={gridSnap ? 'bg-[#0A84FF] hover:bg-[#0066CC]' : theme === 'dark' ? 'border-gray-700 hover:bg-gray-700' : 'border-gray-300'}
        >
          <Grid3x3 className="w-4 h-4 mr-2" />
          Grid Snap
        </Button>

        <div className="w-px h-6 bg-gray-600 mx-1"></div>

        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className={theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-gray-200'}
        >
          {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </Button>
      </div>
    </div>
  );
}
