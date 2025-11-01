import { Radar, Moon, Sun, Minus, Square, X } from 'lucide-react';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

interface TopBarProps {
  theme: 'dark' | 'light';
  setTheme: (theme: 'dark' | 'light') => void;
  isConnected: boolean;
  selectedPort: string;
}

export default function TopBar({ theme, setTheme, isConnected, selectedPort }: TopBarProps) {
  return (
    <div className={`h-14 border-b flex items-center justify-between px-4 ${
      theme === 'dark' ? 'bg-[#252525] border-gray-800' : 'bg-gray-50 border-gray-200'
    }`}>
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg bg-gradient-to-br from-[#0078D4] to-[#005a9e]`}>
          <Radar className="w-5 h-5 text-white" />
        </div>
        <span className="tracking-tight" style={{ fontFamily: 'Inter, sans-serif' }}>
          UniScope
        </span>
        
        <Badge 
          variant={isConnected ? "default" : "secondary"}
          className={`ml-4 ${
            isConnected 
              ? 'bg-[#00C853] hover:bg-[#00C853] text-white' 
              : theme === 'dark' 
                ? 'bg-gray-700 text-gray-300' 
                : 'bg-gray-200 text-gray-700'
          }`}
        >
          <div className={`w-2 h-2 rounded-full mr-2 ${isConnected ? 'bg-white animate-pulse' : 'bg-gray-400'}`}></div>
          {isConnected ? `Connected${selectedPort ? ` • ${selectedPort}` : ''}` : 'Disconnected'}
        </Badge>
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className={theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-gray-200'}
        >
          {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </Button>

        <div className="w-px h-6 bg-gray-600 mx-1"></div>

        <Button 
          variant="ghost" 
          size="icon"
          className={theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-gray-200'}
        >
          <Minus className="w-4 h-4" />
        </Button>
        <Button 
          variant="ghost" 
          size="icon"
          className={theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-gray-200'}
        >
          <Square className="w-3.5 h-3.5" />
        </Button>
        <Button 
          variant="ghost" 
          size="icon"
          className={`${theme === 'dark' ? 'hover:bg-[#FF5252]' : 'hover:bg-red-100'} hover:text-white`}
        >
          <X className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}
