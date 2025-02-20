import React, { useState } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { AlertCircle, CheckCircle, Clock, Ban } from 'lucide-react';

const PipelineStage = ({ title, deals, icon: Icon }) => (
  <div className="flex-1 min-w-[250px] bg-gray-50 rounded-lg p-4 mx-2">
    <div className="flex items-center mb-4">
      <Icon className="h-5 w-5 text-gray-500 mr-2" />
      <h3 className="text-lg font-medium text-gray-900">{title}</h3>
      <span className="ml-2 text-sm text-gray-500">({deals.length})</span>
    </div>
    
    <div className="space-y-3">
      {deals.map((deal, index) => (
        <Draggable key={deal.id} draggableId={deal.id} index={index}>
          {(provided) => (
            <div
              ref={provided.innerRef}
              {...provided.draggableProps}
              {...provided.dragHandleProps}
              className="bg-white p-4 rounded shadow-sm hover:shadow"
            >
              <div className="flex justify-between items-start mb-2">
                <h4 className="text-sm font-medium text-gray-900">{deal.title}</h4>
                <span className={`text-sm font-medium ${
                  deal.priority === 'high' ? 'text-red-600'
                  : deal.priority === 'medium' ? 'text-yellow-600'
                  : 'text-green-600'
                }`}>
                  R$ {deal.value.toLocaleString()}
                </span>
              </div>
              
              <div className="text-sm text-gray-500 mb-2">{deal.client}</div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Clock className="h-4 w-4 text-gray-400 mr-1" />
                  <span className="text-xs text-gray-500">
                    {deal.daysInStage} dias
                  </span>
                </div>
                
                <div className="flex items-center">
                  {deal.nextAction && (
                    <span className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">
                      {deal.nextAction}
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}
        </Draggable>
      ))}
    </div>
  </div>
);

const SalesPipeline = () => {
  const [stages] = useState([
    {
      id: 'new',
      title: 'Novos Leads',
      icon: AlertCircle,
      deals: [
        {
          id: 'deal1',
          title: 'Website E-commerce',
          client: 'Loja XYZ',
          value: 28000,
          priority: 'high',
          daysInStage: 2,
          nextAction: 'Agendar Reunião'
        },
        {
          id: 'deal2',
          title: 'Sistema ERP',
          client: 'Empresa ABC',
          value: 45000,
          priority: 'medium',
          daysInStage: 1,
          nextAction: 'Enviar Proposta'
        }
      ]
    },
    {
      id: 'proposal',
      title: 'Proposta Enviada',
      icon: Clock,
      deals: [
        {
          id: 'deal3',
          title: 'App Mobile',
          client: 'Startup 123',
          value: 65000,
          priority: 'high',
          daysInStage: 3,
          nextAction: 'Follow-up'
        }
      ]
    },
    {
      id: 'negotiation',
      title: 'Em Negociação',
      icon: CheckCircle,
      deals: [
        {
          id: 'deal4',
          title: 'Consultoria TI',
          client: 'Corp XYZ',
          value: 120000,
          priority: 'high',
          daysInStage: 5,
          nextAction: 'Reunião Final'
        }
      ]
    },
    {
      id: 'closed',
      title: 'Fechados',
      icon: CheckCircle,
      deals: [
        {
          id: 'deal5',
          title: 'Dashboard Analytics',
          client: 'Tech Inc',
          value: 85000,
          priority: 'medium',
          daysInStage: 0,
          nextAction: null
        }
      ]
    },
    {
      id: 'lost',
      title: 'Perdidos',
      icon: Ban,
      deals: []
    }
  ]);

  const handleDragEnd = (result) => {
    // TODO: Implementar lógica de drag and drop
    console.log('Drag ended:', result);
  };

  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-medium text-gray-900">Pipeline de Vendas</h2>
          <div className="flex items-center space-x-4">
            <select className="text-sm border-gray-300 rounded-md">
              <option>Todos os Deals</option>
              <option>Alta Prioridade</option>
              <option>Média Prioridade</option>
              <option>Baixa Prioridade</option>
            </select>
            <button className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm">
              Novo Deal
            </button>
          </div>
        </div>

        <div className="flex overflow-x-auto pb-4">
          {stages.map((stage) => (
            <Droppable key={stage.id} droppableId={stage.id}>
              {(provided) => (
                <div ref={provided.innerRef} {...provided.droppableProps}>
                  <PipelineStage
                    title={stage.title}
                    deals={stage.deals}
                    icon={stage.icon}
                  />
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          ))}
        </div>

        <div className="mt-6 border-t pt-4">
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">
                R$ 343.000
              </div>
              <div className="text-sm text-gray-500">Total Pipeline</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                R$ 85.000
              </div>
              <div className="text-sm text-gray-500">Deals Fechados</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">45%</div>
              <div className="text-sm text-gray-500">Taxa de Conversão</div>
            </div>
          </div>
        </div>
      </div>
    </DragDropContext>
  );
};

export default SalesPipeline;