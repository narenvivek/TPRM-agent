'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, ShieldAlert, CheckCircle, FileText, Loader2, Download, Upload, FileCheck } from 'lucide-react';
import Link from 'next/link';

interface Vendor {
    id: string;
    name: string;
    website: string;
    description: string;
    criticality: string;
    risk_score: number;
    risk_level: string;
}

interface Document {
    id: string;
    vendor_id: string;
    filename: string;
    file_type: string;
    document_type: string;
    file_size: number;
    file_url: string;
    upload_date: string;
    analysis_status: string;
    risk_score?: number;
    risk_level?: string;
    findings?: string[];
    recommendations?: string[];
}

export default function VendorDetailsPage() {
    const params = useParams();
    const id = params.id as string;
    const [vendor, setVendor] = useState<Vendor | null>(null);
    const [documents, setDocuments] = useState<Document[]>([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [analyzingId, setAnalyzingId] = useState<string | null>(null);
    const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);

    const fetchVendor = async () => {
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const res = await fetch(`${apiUrl}/vendors`);
            const data = await res.json();
            const found = data.find((v: any) => v.id === id);
            setVendor(found || null);
        } catch (error) {
            console.error("Failed to fetch vendor", error);
        }
    };

    const fetchDocuments = async () => {
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const res = await fetch(`${apiUrl}/vendors/${id}/documents`);
            const data = await res.json();
            setDocuments(data);
        } catch (error) {
            console.error("Failed to fetch documents", error);
        }
    };

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            await Promise.all([fetchVendor(), fetchDocuments()]);
            setLoading(false);
        };
        loadData();
    }, [id]);

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setSelectedFiles(e.target.files);
        }
    };

    const handleFileUpload = async () => {
        if (!selectedFiles || selectedFiles.length === 0) {
            alert("Please select at least one file");
            return;
        }

        setUploading(true);
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const formData = new FormData();

            // Append all selected files
            for (let i = 0; i < selectedFiles.length; i++) {
                formData.append('files', selectedFiles[i]);
            }
            formData.append('document_type', 'General');

            const res = await fetch(`${apiUrl}/vendors/${id}/documents/upload`, {
                method: 'POST',
                body: formData
            });

            if (!res.ok) {
                const error = await res.json();
                throw new Error(error.detail || 'Upload failed');
            }

            const result = await res.json();
            const uploadCount = result.documents?.length || selectedFiles.length;

            // Refresh documents list
            await fetchDocuments();
            setSelectedFiles(null);

            // Reset file input
            const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
            if (fileInput) fileInput.value = '';

            alert(`Successfully uploaded ${uploadCount} document(s)!`);
        } catch (error) {
            console.error("Upload failed", error);
            alert(`Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
        } finally {
            setUploading(false);
        }
    };

    const handleAnalyzeDocument = async (documentId: string) => {
        setAnalyzingId(documentId);
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const res = await fetch(`${apiUrl}/documents/${documentId}/analyze`, {
                method: 'POST'
            });

            if (!res.ok) {
                const error = await res.json();
                throw new Error(error.detail || 'Analysis failed');
            }

            // Refresh documents to show updated analysis
            await fetchDocuments();
            alert("Document analyzed successfully!");
        } catch (error) {
            console.error("Analysis failed", error);
            alert(`Analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
        } finally {
            setAnalyzingId(null);
        }
    };

    if (loading) return <div className="p-8 text-slate-400">Loading vendor details...</div>;
    if (!vendor) return <div className="p-8 text-slate-400">Vendor not found.</div>;

    return (
        <div className="min-h-screen bg-[#0f172a] text-slate-100 p-8">
            <header className="mb-8">
                <Link href="/" className="inline-flex items-center text-slate-400 hover:text-blue-400 transition-colors mb-4">
                    <ArrowLeft size={16} className="mr-2" />
                    Back to Dashboard
                </Link>
                <div className="flex justify-between items-start">
                    <div>
                        <h1 className="text-3xl font-bold text-white">{vendor.name}</h1>
                        <a href={vendor.website} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline mt-1 block">
                            {vendor.website}
                        </a>
                    </div>
                    <div className="text-right">
                        <div className="text-slate-400 text-sm">Criticality: {vendor.criticality}</div>
                    </div>
                </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="md:col-span-2 space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Vendor Overview</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <h4 className="text-sm font-medium text-slate-400">Description</h4>
                                <p className="mt-1">{vendor.description || 'No description provided.'}</p>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Documents ({documents.length})</CardTitle>
                        </CardHeader>
                        <CardContent>
                            {documents.length === 0 ? (
                                <div className="text-center py-8 text-slate-500">
                                    <FileText className="h-12 w-12 mx-auto mb-4 opacity-20" />
                                    <p>No documents uploaded yet.</p>
                                    <p className="text-sm">Upload compliance documents to begin risk analysis.</p>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    {documents.map((doc) => (
                                        <div key={doc.id} className="border border-slate-700 rounded-lg p-4 hover:bg-slate-800/50 transition-colors">
                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-2">
                                                        <FileText className="h-5 w-5 text-blue-400" />
                                                        <h4 className="font-medium">{doc.filename}</h4>
                                                    </div>
                                                    <div className="flex items-center gap-4 mt-2 text-xs text-slate-400">
                                                        <span>{doc.document_type}</span>
                                                        <span>{(doc.file_size / 1024).toFixed(1)} KB</span>
                                                        <span>{doc.upload_date}</span>
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                                                        doc.analysis_status === 'Completed'
                                                            ? 'bg-green-500/10 text-green-400 border border-green-500/20'
                                                            : 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'
                                                    }`}>
                                                        {doc.analysis_status}
                                                    </span>
                                                    <a
                                                        href={doc.file_url}
                                                        target="_blank"
                                                        rel="noreferrer"
                                                        className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
                                                    >
                                                        <Download className="h-4 w-4 text-slate-400" />
                                                    </a>
                                                </div>
                                            </div>

                                            {doc.analysis_status !== 'Completed' && (
                                                <div className="mt-4">
                                                    <Button
                                                        onClick={() => handleAnalyzeDocument(doc.id)}
                                                        disabled={analyzingId === doc.id}
                                                        size="sm"
                                                        className="w-full"
                                                    >
                                                        {analyzingId === doc.id ? (
                                                            <>
                                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                                Analyzing...
                                                            </>
                                                        ) : (
                                                            <>
                                                                <ShieldAlert className="mr-2 h-4 w-4" />
                                                                Analyze with AI
                                                            </>
                                                        )}
                                                    </Button>
                                                </div>
                                            )}

                                            {doc.analysis_status === 'Completed' && doc.findings && (
                                                <div className="mt-4 p-4 rounded-lg bg-slate-800/50 border border-slate-700">
                                                    <div className="flex items-center justify-between mb-3">
                                                        <h5 className="font-semibold text-sm">Analysis Results</h5>
                                                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                                                            doc.risk_level === 'High'
                                                                ? 'bg-red-500/20 text-red-400'
                                                                : doc.risk_level === 'Medium'
                                                                ? 'bg-yellow-500/20 text-yellow-400'
                                                                : 'bg-green-500/20 text-green-400'
                                                        }`}>
                                                            {doc.risk_level} Risk ({doc.risk_score}/100)
                                                        </span>
                                                    </div>
                                                    <div className="space-y-3 text-sm">
                                                        <div>
                                                            <h6 className="text-xs font-medium text-slate-400 mb-1">Key Findings</h6>
                                                            <ul className="space-y-1">
                                                                {doc.findings.slice(0, 3).map((finding, i) => (
                                                                    <li key={i} className="flex items-start gap-2">
                                                                        <ShieldAlert className="h-3 w-3 text-yellow-500 mt-0.5 shrink-0" />
                                                                        <span className="text-xs">{finding}</span>
                                                                    </li>
                                                                ))}
                                                            </ul>
                                                            {doc.findings.length > 3 && (
                                                                <p className="text-xs text-slate-400 mt-1">
                                                                    +{doc.findings.length - 3} more findings
                                                                </p>
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>

                <div className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Upload Documents</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="text-sm text-slate-400">
                                Upload vendor compliance documents (PDF, DOCX, TXT) for AI-powered risk analysis.
                            </div>
                            <div className="space-y-2">
                                <input
                                    type="file"
                                    accept=".pdf,.docx,.txt"
                                    onChange={handleFileSelect}
                                    multiple
                                    className="w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-500 file:cursor-pointer"
                                />
                                {selectedFiles && selectedFiles.length > 0 && (
                                    <div className="text-xs text-slate-400">
                                        Selected: {selectedFiles.length} file(s)
                                    </div>
                                )}
                            </div>
                            <Button
                                onClick={handleFileUpload}
                                disabled={!selectedFiles || selectedFiles.length === 0 || uploading}
                                className="w-full"
                            >
                                {uploading ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Uploading...
                                    </>
                                ) : (
                                    <>
                                        <Upload className="mr-2 h-4 w-4" />
                                        Upload Documents
                                    </>
                                )}
                            </Button>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
