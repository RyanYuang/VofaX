import { useState } from 'react';
import { ChevronRight, ChevronDown, CheckCircle2, XCircle, Settings } from 'lucide-react';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';

interface ProtocolAnalyzerTabProps {
  theme: 'dark' | 'light';
  isConnected: boolean;
}

interface PacketNode {
  id: string;
  name: string;
  value?: string;
  crc?: 'valid' | 'invalid';
  children?: PacketNode[];
}

const mockPackets: PacketNode[] = [
  {
    id: '1',
    name: 'Frame #1',
    value: '14:32:45.123',
    crc: 'valid',
    children: [
      { id: '1.1', name: 'Header', value: 'AA BB' },
      { id: '1.2', name: 'Length', value: '04 00 (4 bytes)' },
      { id: '1.3', name: 'Payload', value: '00 01 02 03', children: [
        { id: '1.3.1', name: 'Field 1', value: '00 01 (1)' },
        { id: '1.3.2', name: 'Field 2', value: '02 03 (515)' },
      ]},
      { id: '1.4', name: 'CRC16', value: 'A3 2F', crc: 'valid' },
    ]
  },
  {
    id: '2',
    name: 'Frame #2',
    value: '14:32:46.456',
    crc: 'valid',
    children: [
      { id: '2.1', name: 'Header', value: 'AA BB' },
      { id: '2.2', name: 'Length', value: '08 00 (8 bytes)' },
      { id: '2.3', name: 'Payload', value: 'CC DD EE FF 11 22 33 44' },
      { id: '2.4', name: 'CRC16', value: 'B4 1A', crc: 'valid' },
    ]
  },
  {
    id: '3',
    name: 'Frame #3',
    value: '14:32:47.789',
    crc: 'invalid',
    children: [
      { id: '3.1', name: 'Header', value: 'AA BB' },
      { id: '3.2', name: 'Length', value: '02 00 (2 bytes)' },
      { id: '3.3', name: 'Payload', value: '4F 4B' },
      { id: '3.4', name: 'CRC16', value: 'FF FF', crc: 'invalid' },
    ]
  },
];

function TreeNode({ node, theme, level = 0 }: { node: PacketNode; theme: 'dark' | 'light'; level?: number }) {
  const [isExpanded, setIsExpanded] = useState(level === 0);

  const hasChildren = node.children && node.children.length > 0;

  return (
    <div>
      <div 
        className={`flex items-center gap-2 py-1.5 px-2 rounded cursor-pointer group ${
          theme === 'dark' ? 'hover:bg-[#2a2a2a]' : 'hover:bg-gray-100'
        }`}
        style={{ paddingLeft: `${level * 20 + 8}px` }}
        onClick={() => hasChildren && setIsExpanded(!isExpanded)}
      >
        {hasChildren ? (
          isExpanded ? (
            <ChevronDown className="w-4 h-4 text-gray-400" />
          ) : (
            <ChevronRight className="w-4 h-4 text-gray-400" />
          )
        ) : (
          <div className="w-4 h-4" />
        )}

        <span className="text-sm">{node.name}</span>
        
        {node.value && (
          <span 
            className="text-sm text-[#0078D4] ml-auto"
            style={{ fontFamily: 'JetBrains Mono, monospace' }}
          >
            {node.value}
          </span>
        )}

        {node.crc && (
          <div className="ml-2">
            {node.crc === 'valid' ? (
              <CheckCircle2 className="w-4 h-4 text-[#00C853]" />
            ) : (
              <XCircle className="w-4 h-4 text-[#FF5252]" />
            )}
          </div>
        )}
      </div>

      {hasChildren && isExpanded && (
        <div>
          {node.children!.map(child => (
            <TreeNode key={child.id} node={child} theme={theme} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function ProtocolAnalyzerTab({ theme, isConnected }: ProtocolAnalyzerTabProps) {
  return (
    <div className="h-full flex flex-col p-4 gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h3>Packet Tree View</h3>
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <CheckCircle2 className="w-4 h-4 text-[#00C853]" />
            <span>CRC Valid</span>
            <XCircle className="w-4 h-4 text-[#FF5252] ml-3" />
            <span>CRC Invalid</span>
          </div>
        </div>

        <Button 
          variant="outline"
          size="sm"
          className={theme === 'dark' ? 'border-gray-700 hover:bg-gray-700' : 'border-gray-300'}
        >
          <Settings className="w-4 h-4 mr-2" />
          Parser Config
        </Button>
      </div>

      <div className={`flex-1 rounded-lg border overflow-hidden ${
        theme === 'dark' ? 'bg-[#0D0D0D] border-gray-800' : 'bg-gray-50 border-gray-200'
      }`}>
        <ScrollArea className="h-full p-2">
          {mockPackets.map(packet => (
            <TreeNode key={packet.id} node={packet} theme={theme} />
          ))}
        </ScrollArea>
      </div>

      <div className={`p-4 rounded-lg border space-y-3 ${
        theme === 'dark' ? 'bg-[#252525] border-gray-800' : 'bg-gray-50 border-gray-200'
      }`}>
        <div>
          <div className="text-xs text-gray-400 mb-1">PROTOCOL SETTINGS</div>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Header:</span>
              <span style={{ fontFamily: 'JetBrains Mono, monospace' }}>AA BB</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">CRC Type:</span>
              <span>CRC-16/MODBUS</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Byte Order:</span>
              <span>Little Endian</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
