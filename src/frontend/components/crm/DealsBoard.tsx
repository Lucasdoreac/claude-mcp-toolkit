import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

interface Deal {
  id: string;
  title: string;
  value: number;
  company: string;
  stage: string;
}

export default function DealsBoard() {
  const deals: Deal[] = [
    {
      id: '1',
      title: 'Projeto Website',
      value: 25000,
      company: 'Empresa ABC',
      stage: 'Proposta'
    }
  ];

  const stages = ['Lead', 'Contato', 'Proposta', 'Negociação', 'Fechado'];

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Pipeline de Vendas</h2>
      <div className="flex space-x-4 overflow-x-auto pb-4">
        {stages.map((stage) => (
          <div key={stage} className="min-w-[300px]">
            <Card>
              <CardHeader>
                <CardTitle>{stage}</CardTitle>
              </CardHeader>
              <CardContent>
                {deals
                  .filter((deal) => deal.stage === stage)
                  .map((deal) => (
                    <div
                      key={deal.id}
                      className="p-4 mb-2 bg-gray-50 rounded-lg"
                    >
                      <h3 className="font-semibold">{deal.title}</h3>
                      <p className="text-sm text-gray-600">{deal.company}</p>
                      <p className="text-sm font-medium">
                        R$ {deal.value.toLocaleString()}
                      </p>
                    </div>
                  ))}
              </CardContent>
            </Card>
          </div>
        ))}
      </div>
    </div>
  );
}