import { useState } from 'react';
import { X, RefreshCw, Wifi } from 'lucide-react';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Label } from '../ui/label';
import { toast } from 'sonner@2.0.3';

interface ConnectionDialogProps {
  theme: 'dark' | 'light';
  onClose: () => void;
  onConnect: (port: string) => void;
}

export default function ConnectionDialog({ theme, onClose, onConnect }: ConnectionDialogProps) {
  const [selectedPort, setSelectedPort] = useState('');
  const [baudRate, setBaudRate] = useState('115200');
  const [ports, setPorts] = useState(['COM3', 'COM5', '/dev/ttyUSB0']);
  const [isScanning, setIsScanning] = useState(false);

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
      toast.error('No port selected');
      return;
    }
    onConnect(selectedPort);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className={`w-[480px] rounded-xl shadow-2xl ${
        theme === 'dark' ? 'bg-[#252525]' : 'bg-white'
      }`}>
        <div className={`p-4 border-b flex items-center justify-between ${
          theme === 'dark' ? 'border-gray-800' : 'border-gray-200'
        }`}>
          <h3>Serial Connection</h3>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className={theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-gray-200'}
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="p-6 space-y-4">
          <div className="space-y-2">
            <Label className="text-xs text-gray-400">PORT</Label>
            <div className="flex gap-2">
              <Select value={selectedPort} onValueChange={setSelectedPort}>
                <SelectTrigger className={theme === 'dark' ? 'bg-[#1A1A1A] border-gray-700' : 'bg-white border-gray-300'}>
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
                onClick={handleScan}
                disabled={isScanning}
                className={theme === 'dark' ? 'bg-[#1A1A1A] border-gray-700 hover:bg-gray-700' : 'bg-white border-gray-300'}
              >
                <RefreshCw className={`w-4 h-4 ${isScanning ? 'animate-spin' : ''}`} />
              </Button>
            </div>
          </div>

          <div className="space-y-2">
            <Label className="text-xs text-gray-400">BAUD RATE</Label>
            <Select value={baudRate} onValueChange={setBaudRate}>
              <SelectTrigger className={theme === 'dark' ? 'bg-[#1A1A1A] border-gray-700' : 'bg-white border-gray-300'}>
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
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div className="space-y-2">
              <Label className="text-xs text-gray-400">PARITY</Label>
              <Select defaultValue="None">
                <SelectTrigger className={theme === 'dark' ? 'bg-[#1A1A1A] border-gray-700' : 'bg-white border-gray-300'}>
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
              <Select defaultValue="8">
                <SelectTrigger className={theme === 'dark' ? 'bg-[#1A1A1A] border-gray-700' : 'bg-white border-gray-300'}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7">7</SelectItem>
                  <SelectItem value="8">8</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label className="text-xs text-gray-400">STOP BITS</Label>
              <Select defaultValue="1">
                <SelectTrigger className={theme === 'dark' ? 'bg-[#1A1A1A] border-gray-700' : 'bg-white border-gray-300'}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">1</SelectItem>
                  <SelectItem value="2">2</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        <div className={`p-4 border-t flex justify-end gap-2 ${
          theme === 'dark' ? 'border-gray-800' : 'border-gray-200'
        }`}>
          <Button
            variant="outline"
            onClick={onClose}
            className={theme === 'dark' ? 'border-gray-700 hover:bg-gray-700' : 'border-gray-300'}
          >
            Cancel
          </Button>
          <Button
            onClick={handleConnect}
            className="bg-[#30D158] hover:bg-[#28a745] text-white"
          >
            <Wifi className="w-4 h-4 mr-2" />
            Connect
          </Button>
        </div>
      </div>
    </div>
  );
}
