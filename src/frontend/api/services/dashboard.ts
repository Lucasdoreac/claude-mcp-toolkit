/**
 * Dashboard API service.
 */
import apiClient from '../client';

export interface DashboardMetrics {
  total_deals: number;
  active_deals: number;
  total_proposals: number;
  total_clients: number;
}

export interface RecentActivity {
  id: number;
  title: string;
  status: string;
  created_at: string;
}

export interface PipelineStats {
  new: number;
  contacted: number;
  proposal_sent: number;
  negotiation: number;
  closed: number;
}

export interface ProposalStats {
  sent: number;
  accepted: number;
  rejected: number;
  expired: number;
}

export interface DashboardData {
  metrics: DashboardMetrics;
  recent_activity: RecentActivity[];
  pipeline_stats: PipelineStats;
  proposal_stats: ProposalStats;
}

class DashboardService {
  async getDashboardData(): Promise<DashboardData> {
    return apiClient.get<DashboardData>('/api/dashboard');
  }

  async refreshDashboard(): Promise<DashboardData> {
    // Force refresh by adding timestamp to bypass cache
    return apiClient.get<DashboardData>('/api/dashboard', {
      _t: new Date().getTime()
    });
  }
}

export const dashboardService = new DashboardService();
export default dashboardService;