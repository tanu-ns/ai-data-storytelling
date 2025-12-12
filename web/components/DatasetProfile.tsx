"use client";

import { useState } from "react";
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";

export default function DatasetProfile({ data }: { data: any }) {
    const [tab, setTab] = useState("profile");

    if (!data || !data.meta_info) return <div className="text-gray-500">Processing data... or no data available.</div>;

    const { meta_info } = data;
    const { summary, correlation, schema, distributions } = meta_info;

    // Render a single distribution chart based on col name
    const renderChart = (col: string) => {
        if (!distributions || !distributions[col]) return <p className="text-xs text-gray-400">No chart data</p>;
        const dist = distributions[col];

        let chartData = [];
        if (dist.type === "numeric") {
            chartData = dist.bins.map((b: any) => ({ name: b.range, count: b.count }));
        } else {
            chartData = dist.counts.map((c: any) => ({ name: c.name, count: c.value }));
        }

        return (
            <div className="h-40 w-full mt-2">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="name" hide />
                        <Tooltip />
                        <Bar dataKey="count" fill="#8884d8" radius={[4, 4, 0, 0]} />
                    </BarChart>
                </ResponsiveContainer>
                <p className="text-center text-xs text-gray-500 mt-1">{dist.type === "numeric" ? "Distribution" : "Top Values"}</p>
            </div>
        );
    };

    return (
        <div className="mt-8 bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
            <div className="flex space-x-4 border-b border-gray-700 pb-2 mb-4">
                <button
                    onClick={() => setTab("profile")}
                    className={`px-4 py-2 font-semibold ${tab === "profile" ? "text-blue-500 border-b-2 border-blue-500" : "text-gray-400"
                        }`}
                >
                    Data Profile
                </button>
                <button
                    onClick={() => setTab("correlation")}
                    className={`px-4 py-2 font-semibold ${tab === "correlation" ? "text-blue-500 border-b-2 border-blue-500" : "text-gray-400"
                        }`}
                >
                    Correlations
                </button>
            </div>

            {tab === "profile" && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {Object.keys(schema).map((col) => (
                        <div key={col} className="border dark:border-gray-700 p-4 rounded bg-gray-50 dark:bg-gray-900">
                            <div className="flex justify-between items-start mb-2">
                                <div>
                                    <h4 className="font-bold text-lg truncate" title={col}>{col}</h4>
                                    <span className="text-xs px-2 py-0.5 rounded bg-gray-200 dark:bg-gray-700">{schema[col]}</span>
                                </div>
                                <div className="text-right text-xs">
                                    <p>Missing: {summary[col]?.missing_count || 0}</p>
                                    <p>Unique: {summary[col]?.unique || "-"}</p>
                                </div>
                            </div>

                            {/* Stats Grid */}
                            <div className="grid grid-cols-2 gap-2 text-sm mb-2">
                                {summary[col]?.mean != null && (
                                    <>
                                        <div>Mean: {Number(summary[col].mean).toFixed(2)}</div>
                                        <div>Max: {summary[col].max}</div>
                                    </>
                                )}
                            </div>

                            {/* Chart */}
                            {renderChart(col)}
                        </div>
                    ))}
                </div>
            )}

            {tab === "correlation" && (
                <div className="overflow-x-auto">
                    {(!correlation || Object.keys(correlation).length === 0) ? (
                        <p>No numeric correlations available.</p>
                    ) : (
                        <table className="min-w-full text-sm text-left">
                            <thead className="text-xs uppercase bg-gray-100 dark:bg-gray-700">
                                <tr>
                                    <th className="px-4 py-2"></th>
                                    {Object.keys(correlation).map(c => <th key={c} className="px-4 py-2">{c}</th>)}
                                </tr>
                            </thead>
                            <tbody>
                                {Object.keys(correlation).map(row => (
                                    <tr key={row} className="border-b dark:border-gray-700">
                                        <td className="px-4 py-2 font-bold">{row}</td>
                                        {Object.keys(correlation).map(col => (
                                            <td key={col} className="px-4 py-2 bg-opacity-10" style={{
                                                backgroundColor: correlation[row][col] ? `rgba(59, 130, 246, ${Math.abs(correlation[row][col])})` : 'transparent'
                                            }}>
                                                {correlation[row][col]?.toFixed(2)}
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            )}
        </div>
    );
}
