import { useState } from 'react';
import { Download, FileJson, FileSpreadsheet, Search } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { ScrollArea } from './ui/scroll-area';

interface DataLoggerTabProps {
  theme: 'dark' | 'light';
  isConnected: boolean;
}

const mockLogData = [
  { time: '14:32:45.123', source: 'CH1', type: 'Sensor', data: 'AA BB 04 00', value: '1024' },
  { time: '14:32:45.456', source: 'CH2', type: 'Command', data: '53 54 41 54', value: 'STAT' },
  { time: '14:32:46.789', source: 'CH1', type: 'Sensor', data: 'CC DD 08 00', value: '2048' },
  { time: '14:32:47.012', source: 'CH3', type: 'Response', data: '4F 4B', value: 'OK' },
  { time: '14:32:48.345', source: 'CH1', type: 'Sensor', data: 'AA BB 02 00', value: '512' },
  { time: '14:32:49.678', source: 'CH2', type: 'Command', data: '52 45 41 44', value: 'READ' },
  { time: '14:32:50.901', source: 'CH4', type: 'Data', data: '00 01 02 03', value: '16909060' },
  { time: '14:32:51.234', source: 'CH1', type: 'Sensor', data: 'AA BB 03 00', value: '768' },
  { time: '14:32:52.567', source: 'CH3', type: 'Response', data: '45 52 52', value: 'ERR' },
  { time: '14:32:53.890', source: 'CH2', type: 'Command', data: '57 52 49 54', value: 'WRIT' },
];

export default function DataLoggerTab({ theme, isConnected }: DataLoggerTabProps) {
  const [filterText, setFilterText] = useState('');
  const [logData] = useState(mockLogData);

  const filteredData = logData.filter(row => 
    Object.values(row).some(val => 
      val.toLowerCase().includes(filterText.toLowerCase())
    )
  );

  return (
    <div className="h-full flex flex-col p-4 gap-4">
      <div className="flex items-center justify-between">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            value={filterText}
            onChange={(e) => setFilterText(e.target.value)}
            placeholder="Filter logs..."
            className={`pl-10 ${
              theme === 'dark' ? 'bg-[#252525] border-gray-700' : 'bg-white border-gray-300'
            }`}
          />
        </div>

        <div className="flex gap-2">
          <Button 
            variant="outline"
            size="sm"
            className={theme === 'dark' ? 'border-gray-700 hover:bg-gray-700' : 'border-gray-300'}
          >
            <FileSpreadsheet className="w-4 h-4 mr-2" />
            Export CSV
          </Button>
          <Button 
            variant="outline"
            size="sm"
            className={theme === 'dark' ? 'border-gray-700 hover:bg-gray-700' : 'border-gray-300'}
          >
            <FileJson className="w-4 h-4 mr-2" />
            Export JSON
          </Button>
        </div>
      </div>

      <div className={`flex-1 rounded-lg border overflow-hidden ${
        theme === 'dark' ? 'bg-[#0D0D0D] border-gray-800' : 'bg-gray-50 border-gray-200'
      }`}>
        <ScrollArea className="h-full">
          <Table>
            <TableHeader className={theme === 'dark' ? 'bg-[#252525]' : 'bg-gray-100'}>
              <TableRow className={theme === 'dark' ? 'border-gray-800 hover:bg-[#252525]' : 'border-gray-200'}>
                <TableHead className="w-[140px]" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                  Time
                </TableHead>
                <TableHead className="w-[100px]">Source</TableHead>
                <TableHead className="w-[120px]">Type</TableHead>
                <TableHead className="w-[200px]" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                  Data (HEX)
                </TableHead>
                <TableHead>Value</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredData.map((row, idx) => (
                <TableRow 
                  key={idx}
                  className={theme === 'dark' ? 'border-gray-800 hover:bg-[#1a1a1a]' : 'border-gray-200 hover:bg-gray-50'}
                >
                  <TableCell 
                    className="text-gray-400"
                    style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '12px' }}
                  >
                    {row.time}
                  </TableCell>
                  <TableCell>
                    <span className={`px-2 py-0.5 rounded text-xs ${
                      row.source === 'CH1' ? 'bg-[#0078D4] text-white' :
                      row.source === 'CH2' ? 'bg-[#FF8C00] text-white' :
                      row.source === 'CH3' ? 'bg-[#00C853] text-white' :
                      'bg-[#9C27B0] text-white'
                    }`}>
                      {row.source}
                    </span>
                  </TableCell>
                  <TableCell className="text-sm">{row.type}</TableCell>
                  <TableCell 
                    className="text-[#0078D4]"
                    style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '12px' }}
                  >
                    {row.data}
                  </TableCell>
                  <TableCell 
                    style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '12px' }}
                  >
                    {row.value}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </ScrollArea>
      </div>

      <div className={`p-3 rounded-lg border flex items-center justify-between ${
        theme === 'dark' ? 'bg-[#252525] border-gray-800' : 'bg-gray-50 border-gray-200'
      }`}>
        <span className="text-sm text-gray-400">
          Total: {filteredData.length} entries {filterText && `(filtered from ${logData.length})`}
        </span>
        <Button 
          variant="outline" 
          size="sm"
          className={theme === 'dark' ? 'border-gray-700 hover:bg-gray-700' : 'border-gray-300'}
        >
          <Download className="w-4 h-4 mr-2" />
          Download All
        </Button>
      </div>
    </div>
  );
}
