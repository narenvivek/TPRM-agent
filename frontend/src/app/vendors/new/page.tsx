'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ArrowLeft, Save } from 'lucide-react';
import Link from 'next/link';

export default function NewVendorPage() {
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        website: '',
        description: '',
        criticality: 'Low',
        spend: 0,
        data_sensitivity: 'Public'
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: name === 'spend' ? parseFloat(value) || 0 : value
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://100.64.185.83:8000';
            const res = await fetch(`${apiUrl}/vendors`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (res.ok) {
                router.push('/');
            } else {
                console.error("Failed to create vendor");
            }
        } catch (error) {
            console.error("Error creating vendor", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#0f172a] text-slate-100 p-8">
            <header className="mb-8">
                <Link href="/" className="inline-flex items-center text-slate-400 hover:text-blue-400 transition-colors mb-4">
                    <ArrowLeft size={16} className="mr-2" />
                    Back to Dashboard
                </Link>
                <h1 className="text-3xl font-bold text-white">Onboard New Vendor</h1>
                <p className="text-slate-400 mt-2">Enter vendor details to initiate risk assessment.</p>
            </header>

            <div className="max-w-2xl mx-auto">
                <Card>
                    <CardHeader>
                        <CardTitle>Vendor Information</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-300">Vendor Name</label>
                                <Input
                                    name="name"
                                    placeholder="e.g. Acme Corp"
                                    value={formData.name}
                                    onChange={handleChange}
                                    required
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-300">Website</label>
                                <Input
                                    name="website"
                                    placeholder="https://example.com"
                                    value={formData.website}
                                    onChange={handleChange}
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-300">Description</label>
                                <textarea
                                    name="description"
                                    className="flex min-h-[80px] w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                                    placeholder="Brief description of services..."
                                    value={formData.description}
                                    onChange={handleChange}
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-slate-300">Criticality</label>
                                    <select
                                        name="criticality"
                                        className="flex h-10 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                                        value={formData.criticality}
                                        onChange={handleChange}
                                    >
                                        <option value="Low">Low</option>
                                        <option value="Medium">Medium</option>
                                        <option value="High">High</option>
                                        <option value="Critical">Critical</option>
                                    </select>
                                </div>

                                <div className="space-y-2">
                                    <label className="text-sm font-medium text-slate-300">Annual Spend ($)</label>
                                    <Input
                                        type="number"
                                        name="spend"
                                        value={formData.spend}
                                        onChange={handleChange}
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-300">Data Sensitivity</label>
                                <select
                                    name="data_sensitivity"
                                    className="flex h-10 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                                    value={formData.data_sensitivity}
                                    onChange={handleChange}
                                >
                                    <option value="Public">Public</option>
                                    <option value="Internal">Internal</option>
                                    <option value="Confidential">Confidential</option>
                                    <option value="Restricted">Restricted</option>
                                </select>
                            </div>

                            <div className="pt-4 flex justify-end">
                                <Button type="submit" disabled={loading} className="w-full md:w-auto">
                                    {loading ? 'Saving...' : (
                                        <>
                                            <Save size={16} className="mr-2" />
                                            Save Vendor
                                        </>
                                    )}
                                </Button>
                            </div>
                        </form>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
