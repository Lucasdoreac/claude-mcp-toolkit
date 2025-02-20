import React from 'react';
import { useRouter } from 'next/router';
import { Home, Users, FileText, BarChart2, Settings } from 'lucide-react';

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();

  const menuItems = [
    { icon: Home, label: 'Dashboard', path: '/' },
    { icon: Users, label: 'CRM', path: '/crm' },
    { icon: FileText, label: 'Propostas', path: '/proposals' },
    { icon: BarChart2, label: 'Analytics', path: '/analytics' },
    { icon: Settings, label: 'Configurações', path: '/settings' }
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-white shadow-lg">
        <div className="p-4">
          <h1 className="text-2xl font-bold">MCP Toolkit</h1>
        </div>
        
        <nav className="mt-8">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = router.pathname === item.path;
            
            return (
              <a
                key={item.path}
                href={item.path}
                className={`flex items-center space-x-2 px-4 py-3 hover:bg-gray-100 ${isActive ? 'bg-gray-100' : ''}`}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </a>
            );
          })}
        </nav>
      </div>

      {/* Main Content */}
      <div className="ml-64 p-8">
        {children}
      </div>
    </div>
  );
}