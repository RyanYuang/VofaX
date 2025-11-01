import { useState, useEffect } from 'react';
import { Widget } from '../../../App';
import { ScrollArea } from '../../ui/scroll-area';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../ui/table';

interface DataTableWidgetProps {
  widget: Widget;
  theme: 'dark' | 'light';
  isConnected: boolean;
}

interface DataRow {
  time: string;
  channel: string;
  value: string;
}

export default function DataTableWidget({ widget, theme, isConnected }: DataTableWidgetProps) {
  const [rows, setRows] = useState<DataRow[]>([]);

  useEffect(() => {
    if (isConnected) {
      const interval = setInterval(() => {
        const channels = widget.dataBinding?.channels || ['I0'];
        const newRow: DataRow = {
          time: new Date().toLocaleTimeString(),
          channel: channels[Math.floor(Math.random() * channels.length)],
          value: (Math.random() * 100).toFixed(2),
        };
        setRows(prev => [newRow, ...prev].slice(0, widget.config.maxRows || 100));
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [isConnected, widget.dataBinding?.channels, widget.config.maxRows]);

  return (
    <ScrollArea className="h-full">
      <Table>
        <TableHeader className={theme === 'dark' ? 'bg-[#2A2A2A]' : 'bg-gray-100'}>
          <TableRow className={theme === 'dark' ? 'border-gray-800' : 'border-gray-200'}>
            <TableHead style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '11px' }}>
              Time
            </TableHead>
            <TableHead>Channel</TableHead>
            <TableHead>Value</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row, idx) => (
            <TableRow 
              key={idx}
              className={theme === 'dark' ? 'border-gray-800 hover:bg-[#1f1f1f]' : 'border-gray-200 hover:bg-gray-50'}
            >
              <TableCell 
                className="text-gray-400"
                style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '11px' }}
              >
                {row.time}
              </TableCell>
              <TableCell>
                <span className="px-2 py-0.5 rounded text-xs bg-[#0A84FF] text-white">
                  {row.channel}
                </span>
              </TableCell>
              <TableCell style={{ fontFamily: 'JetBrains Mono, monospace' }}>
                {row.value}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </ScrollArea>
  );
}
