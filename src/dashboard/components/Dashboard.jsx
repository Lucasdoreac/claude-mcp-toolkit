import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TrendingUp, Users, FileText, DollarSign } from 'lucide-react';

const MetricCard = ({ title, value, change, icon: Icon }) => (
  <div className="bg-white overflow-hidden shadow rounded-lg">
    <div className="p-5">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <Icon className="h-6 w-6 text-gray-400" />
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
            <dd className="flex items-baseline">
              <div className="text-2xl font-semibold text-gray-900">{value}</div>
              {change && (
                <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                  change >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {change >= 0 ? '↑' : '↓'} {Math.abs(change)}%
                </div>
              )}
            </dd>
          </dl>
        </div>
      </div>
    </div>
  </div>
);

const SalesPipeline = ({ data }) => (
  <div className="bg-white shadow rounded-lg p-6">
    <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
      Pipeline de Vendas
    </h3>
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Line 
            type="monotone" 
            dataKey="value" 
            stroke="#4F46E5" 
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  </div>
);

const RecentProposals = ({ proposals }) => (
  <div className="bg-white shadow rounded-lg p-6">
    <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
      Propostas Recentes
    </h3>
    <div className="flow-root">
      <ul className="divide-y divide-gray-200">
        {proposals.map((proposal) => (
          <li key={proposal.id} className="py-4">
            <div className="flex items-center space-x-4">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {proposal.title}
                </p>
                <p className="text-sm text-gray-500">
                  {proposal.client}
                </p>
              </div>
              <div className="inline-flex items-center text-sm font-semibold text-gray-900">
                R$ {proposal.value.toLocaleString()}
              </div>
              <div className={`inline-flex px-2 text-xs font-semibold rounded-full ${
                proposal.status === 'sent' ? 'bg-yellow-100 text-yellow-800'
                : proposal.status === 'accepted' ? 'bg-green-100 text-green-800'
                : 'bg-gray-100 text-gray-800'
              }`}>
                {proposal.status}
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  </div>
);

const Dashboard = () => {
  const [metrics, setMetrics] = useState({
    totalLeads: 0,
    activeDeals: 0,
    proposalsSent: 0,
    revenue: 0
  });

  const [pipelineData, setPipelineData] = useState([]);
  const [proposals, setProposals] = useState([]);

  useEffect(() => {
    // TODO: Integrar com a API real
    // Dados de exemplo
    setMetrics({
      totalLeads: 124,
      activeDeals: 15,
      proposalsSent: 45,
      revenue: 157000
    });

    setPipelineData([
      { name: 'Jan', value: 25000 },
      { name: 'Fev', value: 35000 },
      { name: 'Mar', value: 45000 },
      { name: 'Abr', value: 52000 }
    ]);

    setProposals([
      {
        id: 1,
        title: 'Sistema de Gestão',
        client: 'Empresa ABC',
        value: 45000,
        status: 'sent'
      },
      {
        id: 2,
        title: 'Website E-commerce',
        client: 'Loja XYZ',
        value: 28000,
        status: 'accepted'
      },
      {
        id: 3,
        title: 'App Mobile',
        client: 'Startup 123',
        value: 65000,
        status: 'draft'
      }
    ]);
  }, []);

  return (
    <div className="space-y-6">
      {/* Métricas */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard 
          title="Total de Leads" 
          value={metrics.totalLeads}
          change={12}
          icon={Users}
        />
        <MetricCard 
          title="Deals Ativos" 
          value={metrics.activeDeals}
          change={-5}
          icon={TrendingUp}
        />
        <MetricCard 
          title="Propostas Enviadas" 
          value={metrics.proposalsSent}
          change={8}
          icon={FileText}
        />
        <MetricCard 
          title="Receita Total" 
          value={`R$ ${metrics.revenue.toLocaleString()}`}
          change={15}
          icon={DollarSign}
        />
      </div>

      {/* Pipeline e Propostas */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        <SalesPipeline data={pipelineData} />
        <RecentProposals proposals={proposals} />
      </div>
    </div>
  );
};

export default Dashboard;