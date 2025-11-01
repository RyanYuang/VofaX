import { Circle } from 'lucide-react';

interface StatusBarProps {
  theme: 'dark' | 'light';
  rxBytes: number;
  txBytes: number;
  isConnected: boolean;
}

export default function StatusBar({ theme, rxBytes, txBytes, isConnected }: StatusBarProps) {
  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className={`h-8 border-t flex items-center justify-between px-4 text-xs ${
      theme === 'dark' ? 'bg-[#252525] border-gray-800' : 'bg-gray-50 border-gray-200'
    }`}>
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <span className="text-gray-400">RX:</span>
          <span style={{ fontFamily: 'JetBrains Mono, monospace' }}>{formatBytes(rxBytes)}</span>
        </div>
        <div className="w-px h-4 bg-gray-600"></div>
        <div className="flex items-center gap-2">
          <span className="text-gray-400">TX:</span>
          <span style={{ fontFamily: 'JetBrains Mono, monospace' }}>{formatBytes(txBytes)}</span>
        </div>
        <div className="w-px h-4 bg-gray-600"></div>
        <div className="flex items-center gap-2">
          <span className="text-gray-400">Baud:</span>
          <span style={{ fontFamily: 'JetBrains Mono, monospace' }}>115200</span>
        </div>
        <div className="w-px h-4 bg-gray-600"></div>
        <div className="flex items-center gap-2">
          <span className="text-gray-400">Encoding:</span>
          <span>UTF-8</span>
        </div>
      </div>

      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <span className="text-gray-400">FPS:</span>
          <span style={{ fontFamily: 'JetBrains Mono, monospace' }}>
            {isConnected ? '60' : '0'}
          </span>
        </div>
        <div className="w-px h-4 bg-gray-600"></div>
        <button className="flex items-center gap-2 hover:text-[#FF5252] transition-colors">
          <Circle className={`w-3 h-3 ${isConnected ? 'fill-[#FF5252] text-[#FF5252]' : 'text-gray-600'}`} />
          <span className="text-gray-400">Macro Recording</span>
        </button>
      </div>
    </div>
  );
}
