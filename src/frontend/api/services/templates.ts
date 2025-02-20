/**
 * Templates API service.
 */
import apiClient from '../client';

export interface Template {
  id: number;
  name: string;
  description?: string;
  type: string;
  content: string;
  variables: Record<string, any>;
  version: number;
  is_active: boolean;
  is_default: boolean;
  created_by: number;
  created_at: string;
  updated_at?: string;
}

export interface TemplateCreate {
  name: string;
  description?: string;
  type: string;
  content: string;
  variables: Record<string, any>;
  is_default?: boolean;
}

export interface TemplateUpdate {
  name?: string;
  description?: string;
  content?: string;
  variables?: Record<string, any>;
  is_active?: boolean;
  is_default?: boolean;
}

export interface TemplateInstance {
  id: number;
  template_id: number;
  content: string;
  variables_used: Record<string, any>;
  created_by: number;
  created_at: string;
}

export interface TemplateInstanceCreate {
  template_id: number;
  variables: Record<string, any>;
}

class TemplateService {
  async getTemplates(type?: string, activeOnly = true): Promise<Template[]> {
    return apiClient.get<Template[]>('/api/templates', {
      type,
      active_only: activeOnly
    });
  }

  async getTemplate(id: number): Promise<Template> {
    return apiClient.get<Template>(`/api/templates/${id}`);
  }

  async createTemplate(data: TemplateCreate): Promise<Template> {
    return apiClient.post<Template>('/api/templates', data);
  }

  async updateTemplate(id: number, data: TemplateUpdate): Promise<Template> {
    return apiClient.put<Template>(`/api/templates/${id}`, data);
  }

  async deleteTemplate(id: number): Promise<void> {
    return apiClient.delete(`/api/templates/${id}`);
  }

  async getDefaultTemplate(type: string): Promise<Template> {
    return apiClient.get<Template>(`/api/templates/type/${type}/default`);
  }

  async createInstance(data: TemplateInstanceCreate): Promise<TemplateInstance> {
    return apiClient.post<TemplateInstance>('/api/templates/instance', data);
  }

  async renderTemplate(id: number, variables: Record<string, any>): Promise<string> {
    const response = await apiClient.post<{ content: string }>(
      `/api/templates/${id}/render`,
      variables
    );
    return response.content;
  }

  getVariableOptions(type: string, variableName: string): any[] {
    // This would be customized based on variable type
    switch (type) {
      case 'status':
        return ['draft', 'sent', 'accepted', 'rejected'];
      case 'priority':
        return ['low', 'medium', 'high'];
      case 'currency':
        return ['USD', 'EUR', 'GBP', 'BRL'];
      default:
        return [];
    }
  }

  validateVariable(type: string, value: any): boolean {
    switch (type) {
      case 'string':
        return typeof value === 'string';
      case 'number':
        return typeof value === 'number' && !isNaN(value);
      case 'boolean':
        return typeof value === 'boolean';
      case 'date':
        return /^\d{4}-\d{2}-\d{2}$/.test(value);
      default:
        return true;
    }
  }
}

export const templateService = new TemplateService();
export default templateService;