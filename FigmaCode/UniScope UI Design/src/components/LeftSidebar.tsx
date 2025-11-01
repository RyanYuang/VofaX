import { useState } from 'react';
import { ChevronLeft, ChevronRight, RefreshCw, Wifi, WifiOff } from 'lucide-react';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Label } from './ui/label';
import { Separator } from './ui/separator';
import { Input } from './ui/input';
import { toast } from 'sonner@2.0.3';

interface LeftSidebarProps {
  theme: 'dark' | 'light';
  isCollapsed: boolean;
  setIsCollapsed: (collapsed: boolean) => void;
  isConnected: boolean;
  setIsConnected: (connected: boolean) => void;
  selectedPort: string;
  setSelectedPort: (port: string) => void;
}

export default function LeftSidebar({ 
  theme, 
  isCollapsed, 
  setIsCollapsed, 
  isConnected, 
  setIsConnected,
  selectedPort,
  setSelectedPort 
}: LeftSidebarProps) {
  const [isScanning, setIsScanning] = useState(false);
  const [baudRate, setBaudRate] = useState('115200');
  const [parity, setParity] = useState('None');
  const [dataBits, setDataBits] = useState('8');
  const [stopBits, setStopBits] = useState('1');
  const [flowControl, setFlowControl] = useState('None');
  const [ports, setPorts] = useState(['COM3', 'COM5', '/dev/ttyUSB0']);

  const handleScan = () => {
    setIsScanning(true);
    setTimeout(() => {
      setPorts(['COM3', 'COM5', 'COM8', '/dev/ttyUSB0', '/dev/ttyACM0']);
      setIsScanning(false);
      toast.success('Scan complete', { description: '5 ports found' });
    }, 1000);
  };

  const handleConnect = () => {
    if (!selectedPort) {
      toast.error('No port selected', { description: 'Please select a serial port first' });
      return;
    }
    
    if (isConnected) {
      setIsConnected(false);
      toast.info('Disconnected', { description: `Closed connection to ${selectedPort}` });
    } else {
      setIsConnected(true);
      toast.success('Connected', { description: `Connected to ${selectedPort} at ${baudRate} baud` });
    }
  };

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
        <span className="text-sm text-gray-400">Serial Configuration</span>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsCollapsed(true)}
          className={`h-7 w-7 ${theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-gray-200'}`}
        >
          <ChevronLeft className="w-4 h-4" />
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="space-y-2">
          <Label className="text-xs text-gray-400">SERIAL PORTS</Label>
          <div className="flex gap-2">
            <Select value={selectedPort} onValueChange={setSelectedPort}>
              <SelectTrigger className={theme === 'dark' ? 'bg-[#1E1E1E] border-gray-700' : 'bg-white border-gray-300'}>
                <SelectValue placeholder="Select port..." />
              </SelectTrigger>
              <SelectContent>
                {ports.map(port => (
                  <SelectItem key={port} value={port}>{port}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button
              variant="outline"
              size="icon"
              onClick={handleScan}
              disabled={isScanning}
              className={theme === 'dark' ? 'bg-[#1E1E1E] border-gray-700 hover:bg-gray-700' : 'bg-white border-gray-300'}
            >
              <RefreshCw className={`w-4 h-4 ${isScanning ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>

        <div className="space-y-2">
          <Label className="text-xs text-gray-400">BAUD RATE</Label>
          <Select value={baudRate} onValueChange={setBaudRate}>
            <SelectTrigger className={theme === 'dark' ? 'bg-[#1E1E1E] border-gray-700' : 'bg-white border-gray-300'}>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="9600">9600</SelectItem>
              <SelectItem value="19200">19200</SelectItem>
              <SelectItem value="38400">38400</SelectItem>
              <SelectItem value="57600">57600</SelectItem>
              <SelectItem value="115200">115200</SelectItem>
              <SelectItem value="230400">230400</SelectItem>
              <SelectItem value="460800">460800</SelectItem>
              <SelectItem value="921600">921600</SelectItem>
              <SelectItem value="2000000">2000000</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <Label className="text-xs text-gray-400">PARITY</Label>
            <Select value={parity} onValueChange={setParity}>
              <SelectTrigger className={theme === 'dark' ? 'bg-[#1E1E1E] border-gray-700' : 'bg-white border-gray-300'}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="None">None</SelectItem>
                <SelectItem value="Even">Even</SelectItem>
                <SelectItem value="Odd">Odd</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-gray-400">DATA BITS</Label>
            <Select value={dataBits} onValueChange={setDataBits}>
              <SelectTrigger className={theme === 'dark' ? 'bg-[#1E1E1E] border-gray-700' : 'bg-white border-gray-300'}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="5">5</SelectItem>
                <SelectItem value="6">6</SelectItem>
                <SelectItem value="7">7</SelectItem>
                <SelectItem value="8">8</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <Label className="text-xs text-gray-400">STOP BITS</Label>
            <Select value={stopBits} onValueChange={setStopBits}>
              <SelectTrigger className={theme === 'dark' ? 'bg-[#1E1E1E] border-gray-700' : 'bg-white border-gray-300'}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1">1</SelectItem>
                <SelectItem value="1.5">1.5</SelectItem>
                <SelectItem value="2">2</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-gray-400">FLOW</Label>
            <Select value={flowControl} onValueChange={setFlowControl}>
              <SelectTrigger className={theme === 'dark' ? 'bg-[#1E1E1E] border-gray-700' : 'bg-white border-gray-300'}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="None">None</SelectItem>
                <SelectItem value="RTS/CTS">RTS/CTS</SelectItem>
                <SelectItem value="XON/XOFF">XON/XOFF</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <Button 
          className={`w-full ${
            isConnected 
              ? 'bg-[#FF5252] hover:bg-[#ff3838]' 
              : 'bg-[#00C853] hover:bg-[#00a844]'
          } text-white`}
          onClick={handleConnect}
        >
          {isConnected ? (
            <>
              <WifiOff className="w-4 h-4 mr-2" />
              Disconnect
            </>
          ) : (
            <>
              <Wifi className="w-4 h-4 mr-2" />
              Connect
            </>
          )}
        </Button>

        <Separator className={theme === 'dark' ? 'bg-gray-700' : 'bg-gray-300'} />

        <div className="space-y-2">
          <Label className="text-xs text-gray-400">QUICK SEND</Label>
          <Input 
            placeholder="HEX: AA BB CC" 
            className={theme === 'dark' ? 'bg-[#1E1E1E] border-gray-700 font-mono' : 'bg-white border-gray-300 font-mono'}
            style={{ fontFamily: 'JetBrains Mono, monospace' }}
          />
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              size="sm"
              className={`flex-1 ${theme === 'dark' ? 'bg-[#1E1E1E] border-gray-700 hover:bg-gray-700' : 'bg-white border-gray-300'}`}
            >
              HEX
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              className={`flex-1 ${theme === 'dark' ? 'bg-[#1E1E1E] border-gray-700 hover:bg-gray-700' : 'bg-white border-gray-300'}`}
            >
              ASCII
            </Button>
          </div>
          <Button 
            variant="outline"
            className={`w-full ${theme === 'dark' ? 'bg-[#0078D4] border-[#0078D4] hover:bg-[#005a9e] text-white' : 'bg-[#0078D4] border-[#0078D4] hover:bg-[#005a9e] text-white'}`}
          >
            Send
          </Button>
        </div>
      </div>
    </div>
  );
}
