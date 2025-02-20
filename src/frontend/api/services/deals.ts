/**
 * Deals API service.
 */
import apiClient from '../client';

export interface Deal {
  id: number;
  title: string;
  description: string;
  value: number;
  status: string;
  priority: string;
  client_id: number;
  owner_id: number;
  created_at: string;
  updated_at: string;
}

export interface DealCreate {
  title: string;
  description?: string;
  value: number;
  status: string;
  priority: string;
  client_id: number;
}

export interface DealUpdate {
  title?: string;
  description?: string;
  value?: number;
  status?: string;
  priority?: string;
}

export interface DealFilters {
  status?: string;
  priority?: string;
  client_id?: number;
}

class DealService {
  async getDeals(filters?: DealFilters): Promise<Deal[]> {
    return apiClient.get<Deal[]>('/api/deals', filters);
  }

  async getDeal(id: number): Promise<Deal> {
    return apiClient.get<Deal>(`/api/deals/${id}`);
  }

  async createDeal(data: DealCreate): Promise<Deal> {
    return apiClient.post<Deal>('/api/deals', data);
  }

  async updateDeal(id: number, data: DealUpdate): Promise<Deal> {
    return apiClient.put<Deal>(`/api/deals/${id}`, data);
  }

  async deleteDeal(id: number): Promise<void> {
    return apiClient.delete(`/api/deals/${id}`);
  }

  async updateDealStatus(id: number, status: string): Promise<Deal> {
    return apiClient.post<Deal>(`/api/deals/${id}/status`, { status });
  }
}

export const dealService = new DealService();
export default dealService;