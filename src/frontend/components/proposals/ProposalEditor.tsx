import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function ProposalEditor() {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Editor de Proposta</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                Cliente
              </label>
              <input
                type="text"
                className="w-full p-2 border rounded"
                placeholder="Nome do Cliente"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">
                Escopo do Projeto
              </label>
              <textarea
                className="w-full p-2 border rounded h-32"
                placeholder="Descreva o escopo do projeto"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Valor
              </label>
              <input
                type="number"
                className="w-full p-2 border rounded"
                placeholder="0,00"
              />
            </div>

            <div className="flex space-x-2">
              <Button>Salvar Rascunho</Button>
              <Button variant="outline">Visualizar PDF</Button>
              <Button variant="outline">Enviar Proposta</Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}