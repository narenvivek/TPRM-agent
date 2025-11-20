'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ShieldCheck, AlertTriangle, Activity, Search, Plus } from 'lucide-react';
import { motion } from 'framer-motion';
import Link from 'next/link';

interface Vendor {
  id: string;
  name: string;
  risk_score: number;
  risk_level: string;
  criticality: string;
}

export default function Dashboard() {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch vendors from backend
    const fetchVendors = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://100.64.185.83:8000';
        const res = await fetch(`${apiUrl}/vendors`);
        const data = await res.json();
        setVendors(data);
      } catch (error) {
        console.error("Failed to fetch vendors", error);
      } finally {
        setLoading(false);
      }
    };
    fetchVendors();
  }, []);

  const highRiskVendors = vendors.filter(v => v.risk_level === 'High' || v.risk_level === 'Critical');

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-100 p-8">
      <header className="mb-12 flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-violet-400">
            TPRM Command Center
          </h1>
          <p className="text-slate-400 mt-2">Third-Party Risk Management & Intelligence</p>
        </div>
        <Link href="/vendors/new">
          <Button className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
            <Plus size={20} />
            Add Vendor
          </Button>
        </Link>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-400">Total Vendors</CardTitle>
            <ShieldCheck className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{vendors.length}</div>
            <p className="text-xs text-slate-500">Active partnerships</p>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-red-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-400">High Risk</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{highRiskVendors.length}</div>
            <p className="text-xs text-slate-500">Requires immediate attention</p>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-violet-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-400">Pending Analysis</CardTitle>
            <Activity className="h-4 w-4 text-violet-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-slate-500">Documents in queue</p>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-semibold">Vendor Risk Landscape</h2>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-500 h-4 w-4" />
            <input
              type="text"
              placeholder="Search vendors..."
              className="bg-slate-900 border border-slate-700 rounded-full py-2 pl-10 pr-4 text-sm focus:outline-none focus:border-blue-500 w-64"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {loading ? (
            <div className="text-center py-12 text-slate-500">Loading intelligence...</div>
          ) : (
            vendors.map((vendor, i) => (
              <motion.div
                key={vendor.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
              >
                <Link href={`/vendors/${vendor.id}`}>
                  <Card className="hover:bg-slate-800/50 transition-colors cursor-pointer group">
                    <CardContent className="p-6 flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className={`w-2 h-12 rounded-full ${vendor.risk_level === 'High' ? 'bg-red-500' :
                          vendor.risk_level === 'Medium' ? 'bg-yellow-500' : 'bg-green-500'
                          }`} />
                        <div>
                          <h3 className="font-semibold text-lg group-hover:text-blue-400 transition-colors">{vendor.name}</h3>
                          <p className="text-sm text-slate-400">{vendor.criticality} Criticality • Score: {vendor.risk_score}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${vendor.risk_level === 'High' ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
                          vendor.risk_level === 'Medium' ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20' :
                            'bg-green-500/10 text-green-400 border border-green-500/20'
                          }`}>
                          {vendor.risk_level || 'Unassessed'}
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              </motion.div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
