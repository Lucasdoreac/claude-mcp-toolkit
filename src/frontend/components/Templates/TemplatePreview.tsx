/**
 * Template preview component.
 */
import React, { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useApi } from '@/hooks/useApi';
import { templateService, Template } from '@/api/services/templates';

interface TemplatePreviewProps {
  template: Template;
  initialVariables?: Record<string, any>;
  onUse?: (content: string) => void;
}

export function TemplatePreview({ template, initialVariables, onUse }: TemplatePreviewProps) {
  const [variables, setVariables] = useState<Record<string, any>>(
    initialVariables || {}
  );
  const [preview, setPreview] = useState<string>('');

  const {
    loading: rendering,
    error,
    execute: renderTemplate
  } = useApi(() => templateService.renderTemplate(template.id, variables));

  useEffect(() => {
    // Initialize variables with default values from schema
    const defaults: Record<string, any> = {};
    Object.entries(template.variables).forEach(([key, schema]) => {
      switch (schema.type) {
        case 'string':
          defaults[key] = schema.default || '';
          break;
        case 'number':
          defaults[key] = schema.default || 0;
          break;
        case 'boolean':
          defaults[key] = schema.default || false;
          break;
        case 'date':
          defaults[key] = schema.default || new Date().toISOString().split('T')[0];
          break;
      }
    });
    setVariables({ ...defaults, ...initialVariables });
  }, [template.variables, initialVariables]);

  const handleVariableChange = (name: string, value: any) => {
    const schema = template.variables[name];
    let parsedValue = value;

    // Parse value based on type
    if (schema.type === 'number') {
      parsedValue = parseFloat(value) || 0;
    } else if (schema.type === 'boolean') {
      parsedValue = value === 'true';
    }

    setVariables({ ...variables, [name]: parsedValue });
  };

  const handlePreview = async () => {
    try {
      const content = await renderTemplate();
      setPreview(content);
    } catch (error) {
      console.error('Error rendering template:', error);
    }
  };

  const handleUse = () => {
    if (onUse && preview) {
      onUse(preview);
    }
  };

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>{error.message}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Variables</h3>
          {Object.entries(template.variables).map(([name, schema]) => (
            <div key={name}>
              <Label htmlFor={name}>{name}</Label>
              {schema.type === 'string' && !schema.options ? (
                <Input
                  id={name}
                  value={variables[name] || ''}
                  onChange={(e) => handleVariableChange(name, e.target.value)}
                />
              ) : schema.type === 'string' && schema.options ? (
                <select
                  id={name}
                  value={variables[name] || ''}
                  onChange={(e) => handleVariableChange(name, e.target.value)}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  {templateService.getVariableOptions(schema.options, name).map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              ) : schema.type === 'number' ? (
                <Input
                  id={name}
                  type="number"
                  value={variables[name] || 0}
                  onChange={(e) => handleVariableChange(name, e.target.value)}
                />
              ) : schema.type === 'boolean' ? (
                <select
                  id={name}
                  value={variables[name] ? 'true' : 'false'}
                  onChange={(e) => handleVariableChange(name, e.target.value)}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value="true">Yes</option>
                  <option value="false">No</option>
                </select>
              ) : schema.type === 'date' ? (
                <Input
                  id={name}
                  type="date"
                  value={variables[name] || ''}
                  onChange={(e) => handleVariableChange(name, e.target.value)}
                />
              ) : null}
            </div>
          ))}

          <Button
            onClick={handlePreview}
            disabled={rendering}
            className="w-full mt-4"
          >
            {rendering ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              'Preview'
            )}
          </Button>
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-medium">Preview</h3>
          <div
            className="p-4 border rounded-md min-h-[200px] prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{ __html: preview }}
          />
          {onUse && preview && (
            <Button onClick={handleUse} className="w-full">
              Use This Content
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

export default TemplatePreview;