"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import axios from 'axios';
import { TrendingUp, CheckCircle, AlertCircle, Clock } from 'lucide-react';

interface Summary {
    total_stories: number;
    stories_by_status: { [key: string]: number };
    total_epics: number;
    active_tasks: number;
    checklists_total: number;
    checklists_complete: number;
    last_updated: string;
}

export const BMADTrackingCard = () => {
    const [summary, setSummary] = useState<Summary | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get('/api/bmad/summary', { timeout: 10000 });
                if (response.data) {
                    setSummary(response.data);
                    setError(null);
                } else {
                    setError('No summary data available');
                }
            } catch (err: any) {
                console.error('BMAD summary fetch error:', err);
                if (err.code === 'ECONNABORTED') {
                    // Retry once on timeout with extended timeout
                    try {
                        const retryResp = await axios.get('/api/bmad/summary', { timeout: 20000 });
                        if (retryResp.data) {
                            setSummary(retryResp.data);
                            setError(null);
                        } else {
                            setError('No summary data available');
                        }
                    } catch (retryErr) {
                        console.error('BMAD summary retry error:', retryErr);
                        setError('Failed to fetch summary data (timeout)');
                    }
                } else {
                    setError('Failed to fetch summary data');
                }
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
        return () => clearInterval(interval);
    }, []);

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'Done': return <CheckCircle className="text-green-500" />;
            case 'In Progress': return <Clock className="text-blue-500" />;
            case 'Review': return <TrendingUp className="text-yellow-500" />;
            default: return <AlertCircle className="text-gray-500" />;
        }
    };
    
    if (loading) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>BMAD Summary</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
                    <p>Loading summary...</p>
                </CardContent>
            </Card>
        );
    }

    if (error) return <p className="text-red-500">{error}</p>;
    if (!summary) return <p>No summary data available.</p>;

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center">
                    <TrendingUp className="mr-2" />
                    BMAD Live Summary
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <h3 className="font-bold">Stories ({summary.total_stories})</h3>
                        <ul className="list-disc pl-5">
                            {Object.entries(summary.stories_by_status).map(([status, count]) => (
                                <li key={status} className="flex items-center">
                                    {getStatusIcon(status)}
                                    <span className="ml-2">{status}: {count}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                    <div>
                        <h3 className="font-bold">Epics</h3>
                        <p>{summary.total_epics} active</p>
                    </div>
                    <div>
                        <h3 className="font-bold">Tasks</h3>
                        <p>{summary.active_tasks} active</p>
                    </div>
                    <div>
                        <h3 className="font-bold">Checklists</h3>
                        <p>{summary.checklists_complete} / {summary.checklists_total} complete</p>
                    </div>
                </div>
                <div className="text-xs text-gray-500 mt-4">
                    Last updated: {new Date(summary.last_updated).toLocaleTimeString()}
                </div>
            </CardContent>
        </Card>
    );
}; 