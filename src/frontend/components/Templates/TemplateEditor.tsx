/**
 * Template editor component.
 */
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { Loader2, Save, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useApi } from '@/hooks/useApi';
import { templateService, Template, TemplateCreate, TemplateUpdate } from '@/api/services/templates';

interface TemplateEditorProps {
  templateId?: number;
  onSave?: (template: Template) => void;
  onCancel?: () => void;
}

export function TemplateEditor({ templateId, onSave, onCancel }: TemplateEditorProps) {
  const router = useRouter();
  const [formData, setFormData] = useState<TemplateCreate | TemplateUpdate>({
    name: '',
    description: '',
    type: 'email',
    content: '',
    variables: {},
    is_default: false
  });

  // Load template if editing
  const {
    data: template,
    loading: loadingTemplate,
    error: loadError
  } = useApi(templateService.getTemplate, templateId ? null : undefined);

  useEffect(() => {
    if (template) {
      setFormData({
        name: template.name,
        description: template.description,
        type: template.type,
        content: template.content,
        variables: template.variables,
        is_default: template.is_default
      });
    }
  }, [template]);

  // Save template
  const {
    loading: saving,
    error: saveError,
    execute: saveTemplate
  } = useApi(async () => {
    if (templateId) {
      return templateService.updateTemplate(templateId, formData);
    } else {
      return templateService.createTemplate(formData as TemplateCreate);
    }
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const saved = await saveTemplate();
      if (onSave) {
        onSave(saved);
      } else {
        router.push('/templates');
      }
    } catch (error) {
      console.error('Error saving template:', error);
    }
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    } else {
      router.push('/templates');
    }
  };

  const handleVariablesChange = (value: string) => {
    try {
      const parsed = JSON.parse(value);
      setFormData({ ...formData, variables: parsed });
    } catch (e) {
      // Invalid JSON - keep the text for editing but don't update the variables
      console.warn('Invalid JSON:', e);
    }
  };

  if (loadingTemplate) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  if (loadError || saveError) {
    return (
      <Alert variant="destructive">
        <AlertDescription>
          {loadError?.message || saveError?.message}
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-4">
        <div>
          <Label htmlFor="name">Name</Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />
        </div>

        <div>
          <Label htmlFor="description">Description</Label>
          <Textarea
            id="description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
        </div>

        <div>
          <Label htmlFor="type">Type</Label>
          <select
            id="type"
            value={formData.type}
            onChange={(e) => setFormData({ ...formData, type: e.target.value })}
            className="w-full px-3 py-2 border rounded-md"
            required
          >
            <option value="email">Email</option>
            <option value="document">Document</option>
            <option value="proposal">Proposal</option>
          </select>
        </div>

        <div>
          <Label htmlFor="content">Content</Label>
          <Textarea
            id="content"
            value={formData.content}
            onChange={(e) => setFormData({ ...formData, content: e.target.value })}
            className="h-64 font-mono"
            required
          />
        </div>

        <div>
          <Label htmlFor="variables">Variables (JSON)</Label>
          <Textarea
            id="variables"
            value={JSON.stringify(formData.variables, null, 2)}
            onChange={(e) => handleVariablesChange(e.target.value)}
            className="h-48 font-mono"
            required
          />
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="is_default"
            checked={formData.is_default}
            onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
          />
          <Label htmlFor="is_default">Set as default template for this type</Label>
        </div>
      </div>

      <div className="flex justify-end gap-2">
        <Button
          type="button"
          variant="outline"
          onClick={handleCancel}
          disabled={saving}
        >
          <X className="w-4 h-4 mr-2" />
          Cancel
        </Button>

        <Button type="submit" disabled={saving}>
          {saving ? (
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <Save className="w-4 h-4 mr-2" />
          )}
          Save Template
        </Button>
      </div>
    </form>
  );
}

export default TemplateEditor;