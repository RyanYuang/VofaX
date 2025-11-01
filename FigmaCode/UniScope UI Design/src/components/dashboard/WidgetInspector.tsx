import { Copy, Trash2, Settings2 } from 'lucide-react';
import { Widget } from '../../App';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Switch } from '../ui/switch';
import { Slider } from '../ui/slider';
import { Separator } from '../ui/separator';

interface WidgetInspectorProps {
  theme: 'dark' | 'light';
  widget: Widget;
  onUpdate: (updates: Partial<Widget>) => void;
  onDelete: () => void;
  onDuplicate: () => void;
}

const channelOptions = ['IO', 'I0', 'I1', 'I2', 'I3', 'I4', 'I5', 'I6', 'I7', 'I8', 'I9', 'I10', 'I11', 'I12', 'I13', 'I14'];

export default function WidgetInspector({ theme, widget, onUpdate, onDelete, onDuplicate }: WidgetInspectorProps) {
  const updateConfig = (key: string, value: any) => {
    onUpdate({ config: { ...widget.config, [key]: value } });
  };

  const toggleChannel = (channel: string) => {
    const currentChannels = widget.dataBinding?.channels || [];
    const newChannels = currentChannels.includes(channel)
      ? currentChannels.filter(ch => ch !== channel)
      : [...currentChannels, channel];
    onUpdate({ dataBinding: { ...widget.dataBinding, channels: newChannels } });
  };

  return (
    <div className={`w-[320px] border-l flex flex-col ${
      theme === 'dark' ? 'bg-[#252525] border-gray-800' : 'bg-gray-50 border-gray-200'
    }`}>
      <div className={`p-4 border-b flex items-center justify-between ${theme === 'dark' ? 'border-gray-800' : 'border-gray-200'}`}>
        <div className="flex items-center gap-2">
          <Settings2 className="w-4 h-4 text-gray-400" />
          <span className="text-sm">Widget Inspector</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="space-y-2">
          <Label className="text-xs text-gray-400">WIDGET TITLE</Label>
          <Input
            value={widget.title}
            onChange={(e) => onUpdate({ title: e.target.value })}
            className={theme === 'dark' ? 'bg-[#1A1A1A] border-gray-700' : 'bg-white border-gray-300'}
          />
        </div>

        <Separator className={theme === 'dark' ? 'bg-gray-700' : 'bg-gray-300'} />

        <div className="space-y-2">
          <Label className="text-xs text-gray-400">DATA SOURCE BINDING</Label>
          <div className="space-y-2">
            <Label className="text-xs">Channels</Label>
            <div className="grid grid-cols-3 gap-2">
              {channelOptions.map((channel) => (
                <button
                  key={channel}
                  onClick={() => toggleChannel(channel)}
                  className={`px-2 py-1 rounded text-xs transition-all ${
                    widget.dataBinding?.channels?.includes(channel)
                      ? 'bg-[#0A84FF] text-white'
                      : theme === 'dark'
                        ? 'bg-[#1A1A1A] text-gray-400 hover:bg-[#2A2A2A]'
                        : 'bg-white text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {channel}
                </button>
              ))}
            </div>
          </div>
        </div>

        <Separator className={theme === 'dark' ? 'bg-gray-700' : 'bg-gray-300'} />

        <div className="space-y-3">
          <Label className="text-xs text-gray-400">WIDGET SETTINGS</Label>

          {widget.type === 'oscilloscope' && (
            <>
              <div className="space-y-2">
                <Label className="text-xs">Time Base: {widget.config.timeBase}ms/div</Label>
                <Slider
                  value={[widget.config.timeBase]}
                  onValueChange={([value]) => updateConfig('timeBase', value)}
                  min={10}
                  max={1000}
                  step={10}
                />
              </div>
              <div className="space-y-2">
                <Label className="text-xs">Y-Axis</Label>
                <Select 
                  value={widget.config.yAxis} 
                  onValueChange={(value) => updateConfig('yAxis', value)}
                >
                  <SelectTrigger className={theme === 'dark' ? 'bg-[#1A1A1A] border-gray-700' : 'bg-white border-gray-300'}>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="auto">Auto</SelectItem>
                    <SelectItem value="fixed">Fixed (±3V)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center justify-between">
                <Label className="text-xs">Show Grid</Label>
                <Switch
                  checked={widget.config.showGrid}
                  onCheckedChange={(checked) => updateConfig('showGrid', checked)}
                />
              </div>
            </>
          )}

          {widget.type === 'terminal' && (
            <>
              <div className="space-y-2">
                <Label className="text-xs">Display Mode</Label>
                <Select 
                  value={widget.config.displayMode} 
                  onValueChange={(value) => updateConfig('displayMode', value)}
                >
                  <SelectTrigger className={theme === 'dark' ? 'bg-[#1A1A1A] border-gray-700' : 'bg-white border-gray-300'}>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ascii">ASCII</SelectItem>
                    <SelectItem value="hex">HEX</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center justify-between">
                <Label className="text-xs">Auto-scroll</Label>
                <Switch
                  checked={widget.config.autoScroll}
                  onCheckedChange={(checked) => updateConfig('autoScroll', checked)}
                />
              </div>
            </>
          )}

          {widget.type === 'gauge' && (
            <>
              <div className="space-y-2">
                <Label className="text-xs">Min Value</Label>
                <Input
                  type="number"
                  value={widget.config.min}
                  onChange={(e) => updateConfig('min', parseFloat(e.target.value))}
                  className={theme === 'dark' ? 'bg-[#1A1A1A] border-gray-700' : 'bg-white border-gray-300'}
                />
              </div>
              <div className="space-y-2">
                <Label className="text-xs">Max Value</Label>
                <Input
                  type="number"
                  value={widget.config.max}
                  onChange={(e) => updateConfig('max', parseFloat(e.target.value))}
                  className={theme === 'dark' ? 'bg-[#1A1A1A] border-gray-700' : 'bg-white border-gray-300'}
                />
              </div>
              <div className="space-y-2">
                <Label className="text-xs">Unit</Label>
                <Input
                  value={widget.config.unit}
                  onChange={(e) => updateConfig('unit', e.target.value)}
                  placeholder="e.g., °C, kPa, %"
                  className={theme === 'dark' ? 'bg-[#1A1A1A] border-gray-700' : 'bg-white border-gray-300'}
                />
              </div>
            </>
          )}

          {widget.type === 'hex-viewer' && (
            <div className="space-y-2">
              <Label className="text-xs">Bytes per Row</Label>
              <Select 
                value={widget.config.bytesPerRow.toString()} 
                onValueChange={(value) => updateConfig('bytesPerRow', parseInt(value))}
              >
                <SelectTrigger className={theme === 'dark' ? 'bg-[#1A1A1A] border-gray-700' : 'bg-white border-gray-300'}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="8">8</SelectItem>
                  <SelectItem value="16">16</SelectItem>
                  <SelectItem value="32">32</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          {widget.type === 'chart' && (
            <div className="space-y-2">
              <Label className="text-xs">Chart Type</Label>
              <Select 
                value={widget.config.chartType} 
                onValueChange={(value) => updateConfig('chartType', value)}
              >
                <SelectTrigger className={theme === 'dark' ? 'bg-[#1A1A1A] border-gray-700' : 'bg-white border-gray-300'}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="line">Line Chart</SelectItem>
                  <SelectItem value="bar">Bar Chart</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          {widget.type === 'data-table' && (
            <div className="space-y-2">
              <Label className="text-xs">Max Rows</Label>
              <Input
                type="number"
                value={widget.config.maxRows}
                onChange={(e) => updateConfig('maxRows', parseInt(e.target.value))}
                className={theme === 'dark' ? 'bg-[#1A1A1A] border-gray-700' : 'bg-white border-gray-300'}
              />
            </div>
          )}
        </div>
      </div>

      <div className={`p-4 border-t space-y-2 ${theme === 'dark' ? 'border-gray-800' : 'border-gray-200'}`}>
        <Button
          variant="outline"
          className={`w-full ${theme === 'dark' ? 'border-gray-700 hover:bg-gray-700' : 'border-gray-300'}`}
          onClick={onDuplicate}
        >
          <Copy className="w-4 h-4 mr-2" />
          Duplicate Widget
        </Button>
        <Button
          variant="outline"
          className="w-full border-[#FF453A] text-[#FF453A] hover:bg-[#FF453A] hover:text-white"
          onClick={onDelete}
        >
          <Trash2 className="w-4 h-4 mr-2" />
          Delete Widget
        </Button>
      </div>
    </div>
  );
}
